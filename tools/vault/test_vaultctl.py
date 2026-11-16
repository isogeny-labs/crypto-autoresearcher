"""Git integration regressions for locked, mixed and fresh worktree bootstrap."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

if __package__:
    from . import vaultctl
else:
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

    def test_nested_envelope_cannot_change_staged_object_during_unlock(self):
        from unittest import mock
        with mock.patch.dict(os.environ, KEY=self.env['KEY']), \
                mock.patch.object(vaultctl, '_CIPHER', None):
            inner = vaultctl.encrypt(b'nested public fixture\n')
            outer = vaultctl.MAGIC + vaultctl._cipher().encrypt(
                inner, [vaultctl.SALT + b'|' + vaultctl.INFO])
        oid = self.git('hash-object', '-w', '--stdin', input=outer).stdout.strip().decode()
        self.git('update-index', '--add', '--cacheinfo', '100644,'+oid+',nested-envelope')
        (self.root/'nested-envelope').write_bytes(outer)
        before = self.git('write-tree').stdout
        self.run_vault('unlock')
        self.assertEqual((self.root/'nested-envelope').read_bytes(), inner)
        self.assertEqual(self.git('write-tree').stdout, before)

    def test_modified_ciphertext_is_unlocked_without_staging_it(self):
        before = self.git('write-tree').stdout
        changed = b'changed sealed local bytes\n'
        encrypted = subprocess.run(
            [sys.executable, str(self.root / 'tools/vault/vaultctl.py'), 'clean'],
            input=changed, env=self.env, capture_output=True, check=True).stdout
        (self.root / 'nested/b.bin').write_bytes(encrypted)
        self.lock('empty')
        self.run_vault('unlock')
        self.assertEqual((self.root / 'nested/b.bin').read_bytes(), changed)
        self.assertEqual(self.git('write-tree').stdout, before)
        self.assertIn(b'nested/b.bin', self.git('diff', '--name-only').stdout)

    def test_edit_after_unlock_with_restored_timestamp_stays_unstaged(self):
        from argparse import Namespace
        from unittest import mock
        self.lock('nested/b.bin', 'empty')
        before = self.git('write-tree').stdout
        target = self.root / 'nested/b.bin'
        original_run = subprocess.run
        edited = b'\x01\xffpayload\n'
        def intervene(*args, **kwargs):
            result = original_run(*args, **kwargs)
            command = args[0] if args else ()
            if len(command) > 1 and command[:2] == ['git', 'check-attr']:
                info = target.stat()
                target.write_bytes(edited)
                os.utime(target, ns=(info.st_atime_ns, info.st_mtime_ns))
            return result
        previous = Path.cwd()
        try:
            os.chdir(self.root)
            with mock.patch.dict(os.environ, KEY=self.env['KEY']), \
                    mock.patch.object(vaultctl, '_CIPHER', None), \
                    mock.patch.object(subprocess, 'run', side_effect=intervene):
                vaultctl.cmd_unlock(Namespace(
                    script=str(self.root / 'tools/vault/vaultctl.py'), quiet=True))
        finally:
            os.chdir(previous)
        self.assertEqual(target.read_bytes(), edited)
        self.assertEqual(self.git('write-tree').stdout, before)

    def test_unlock_preserves_unmerged_index_entries(self):
        oid = self.git('rev-parse', ':a.py').stdout.strip()
        conflict = b'0 ' + b'0' * 40 + b'\ta.py\n'
        for stage in (b'1', b'2', b'3'):
            conflict += b'100644 ' + oid + b' ' + stage + b'\ta.py\n'
        self.git('update-index', '--index-info', input=conflict)
        before = self.git('ls-files', '--stage').stdout
        self.lock('empty')
        self.run_vault('unlock')
        self.assertEqual(self.git('ls-files', '--stage').stdout, before)
        self.assertEqual((self.root / 'a.py').read_text(), 'print(42)\n')

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

    def test_old_backend_reports_dependency_error_without_bypassing_authentication(self):
        from unittest import mock
        backend = mock.Mock()
        backend.encrypt.side_effect = ValueError('empty data unsupported')
        with mock.patch.object(vaultctl, '_CIPHER', None), \
             mock.patch.object(vaultctl, '_derive_key', return_value=bytes(64)), \
             mock.patch('cryptography.hazmat.primitives.ciphers.aead.AESSIV', return_value=backend):
            with self.assertRaisesRegex(vaultctl.VaultError, 'OpenSSL >=3.5'):
                vaultctl.decrypt(vaultctl.MAGIC + bytes(16))
        backend.decrypt.assert_not_called()

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
