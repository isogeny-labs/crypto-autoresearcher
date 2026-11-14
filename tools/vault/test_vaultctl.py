"""Git integration regressions for locked, mixed and fresh worktree bootstrap."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import vaultctl


class VaultWorktreeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        self.root.mkdir()
        self.env = dict(os.environ, KEY='vault-regression-secret', HOME=self.temp.name)
        self.env.pop('CAVAULT_SCRIPT', None)
        self.git('init', '-q')
        self.git('config', 'user.email', 'vault-test@example.invalid')
        self.git('config', 'user.name', 'Vault regression')
        (self.root / 'tools/vault').mkdir(parents=True)
        shutil.copyfile(Path(vaultctl.__file__), self.root / 'tools/vault/vaultctl.py')
        (self.root / '.gitattributes').write_text(
            '* filter=vault -text\n**/.gitattributes -filter -text\n'
            '/.gitattributes -filter -text\n/tools/vault/** -filter -text\n'
            '/.codex/environments/** -filter -text\n'
        )
        (self.root / 'nested').mkdir()
        (self.root / 'nested/.gitattributes').write_text('*.bin -diff\n')
        (self.root / 'a.py').write_text('print(42)\n')
        (self.root / 'nested/b.bin').write_bytes(b'\x00\xffpayload\n')
        (self.root / 'empty').write_bytes(b'')
        (self.root / 'executable').write_text('#!/bin/sh\nexit 0\n')
        (self.root / 'executable').chmod(0o755)
        (self.root / 'link').symlink_to('a.py')
        self.run_vault('setup')
        self.git('add', '.')
        self.git('commit', '-qm', 'encrypted fixture')

    def git(self, *args, cwd=None, input=None, check=True):
        return subprocess.run(['git', *args], cwd=cwd or self.root, env=self.env,
                              input=input, capture_output=True, check=check)

    def run_vault(self, *args, cwd=None, env=None, check=True):
        return subprocess.run([sys.executable, str(self.root / 'tools/vault/vaultctl.py'), *args],
                              cwd=cwd or self.root, env=env or self.env,
                              capture_output=True, check=check)

    def lock(self, *names):
        for name in names:
            data = self.git('show', ':' + name).stdout
            self.assertTrue(data.startswith(vaultctl.MAGIC))
            (self.root / name).write_bytes(data)

    def test_fresh_worktree_bootstrap_and_clean_index(self):
        # Emulate a checkout made before local filters have been installed.
        self.git('config', '--remove-section', 'filter.vault')
        target = Path(self.temp.name) / 'worktree'
        r = self.git('worktree', 'add', '--detach', str(target), 'HEAD')
        self.assertNotIn(b'not a valid attribute', r.stderr)
        self.assertTrue((target / 'a.py').read_bytes().startswith(vaultctl.MAGIC))
        before = self.git('write-tree', cwd=target).stdout
        self.run_vault('unlock', cwd=target)
        shutil.rmtree(self.root / 'tools')  # A removed source worktree cannot break the filter.
        self.assertEqual((target / 'a.py').read_text(), 'print(42)\n')
        self.assertEqual((target / 'nested/b.bin').read_bytes(), b'\x00\xffpayload\n')
        self.assertEqual((target / 'empty').read_bytes(), b'')
        self.assertTrue((target / 'executable').stat().st_mode & 0o111)
        self.assertTrue((target / 'link').is_symlink())
        self.assertEqual(self.git('write-tree', cwd=target).stdout, before)
        r = self.git('status', '--porcelain', cwd=target)
        self.assertEqual(r.stdout, b'')
        self.assertEqual(r.stderr, b'')
        self.assertEqual(self.git('config', 'filter.vault.required').stdout.strip(), b'true')

    def test_mixed_tree_preserves_unstaged_and_staged_edits_even_with_force(self):
        (self.root / 'a.py').write_text('staged version\n')
        self.git('add', 'a.py')
        (self.root / 'a.py').write_text('unstaged version\n')
        before = self.git('write-tree').stdout
        self.lock('nested/b.bin', 'empty')
        self.run_vault('unlock', '--force')
        self.assertEqual((self.root / 'a.py').read_text(), 'unstaged version\n')
        self.assertEqual((self.root / 'nested/b.bin').read_bytes(), b'\x00\xffpayload\n')
        self.assertEqual(self.git('write-tree').stdout, before)
        self.run_vault('unlock')
        self.assertEqual(self.git('write-tree').stdout, before)
        self.assertEqual((self.root / 'a.py').read_text(), 'unstaged version\n')

    def test_empty_ciphertext_is_authenticated(self):
        self.lock('empty')
        p = self.root / 'empty'
        corrupt = p.read_bytes()[:-1] + bytes([p.read_bytes()[-1] ^ 1])
        p.write_bytes(corrupt)
        result = self.run_vault('unlock', check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(p.read_bytes(), corrupt)
        self.assertEqual(list(self.root.glob('.vault-unlock-*')), [])

    def test_missing_key_fails_closed(self):
        self.lock('a.py')
        before = (self.root / 'a.py').read_bytes()
        env = dict(self.env)
        env.pop('KEY')
        result = self.run_vault('unlock', env=env, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.root / 'a.py').read_bytes(), before)
        self.assertEqual(self.git('config', 'filter.vault.required').stdout.strip(), b'true')

    def test_codex_setup_persists_selection_outside_worktree(self):
        import tomllib
        self.git('config', 'extensions.worktreeConfig', 'true')
        self.git('config', '--worktree', 'codex.localEnvironmentConfigPath', '__none__')
        self.run_vault('setup', '--codex')
        shared = self.git('config', '--local', 'codex.localEnvironmentConfigPath').stdout.strip()
        selected = self.git('config', 'codex.localEnvironmentConfigPath').stdout.strip()
        self.assertEqual(shared, selected)
        config = Path(os.fsdecode(selected))
        self.assertTrue(config.is_relative_to(self.root / '.git'))
        data = tomllib.loads(config.read_text())
        self.assertEqual(data['setup']['script'], 'python3 tools/vault/vaultctl.py unlock')

    def test_bootstrap_path_boundaries(self):
        for path in ['.gitattributes', 'nested/.gitattributes',
                     '.codex/environments/environment.toml']:
            self.assertTrue(vaultctl._is_plaintext_path(path), path)
        for path in ['.gitattributes.backup', 'nested/.gitattributes.backup', '.codex/config.toml', 'source.py']:
            self.assertFalse(vaultctl._is_plaintext_path(path), path)

    def test_lfs_materialization_is_preserved(self):
        pointer = b'version https://git-lfs.github.com/spec/v1\noid sha256:' + b'0' * 64 + b'\nsize 7\n'
        oid = self.git('hash-object', '-w', '--stdin', input=pointer).stdout.strip().decode()
        self.git('update-index', '--add', '--cacheinfo', '100644,' + oid + ',lfs')
        (self.root / 'lfs').write_bytes(b'payload')
        before = self.git('write-tree').stdout
        self.lock('empty')
        self.run_vault('unlock')
        self.assertEqual((self.root / 'lfs').read_bytes(), b'payload')
        self.assertEqual(self.git('write-tree').stdout, before)

    def test_wrong_key_preserves_ciphertext(self):
        self.lock('a.py')
        before = (self.root / 'a.py').read_bytes()
        result = self.run_vault('unlock', env=dict(self.env, KEY='wrong-secret'), check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.root / 'a.py').read_bytes(), before)

    def test_legacy_encrypted_attribute_is_recovered(self):
        p = self.root / 'nested/.gitattributes'
        original = p.read_bytes()
        encrypted = subprocess.run(
            [sys.executable, str(self.root / 'tools/vault/vaultctl.py'), 'clean'],
            input=original, env=self.env, capture_output=True, check=True).stdout
        p.write_bytes(encrypted)
        self.run_vault('unlock')
        self.assertEqual(p.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
