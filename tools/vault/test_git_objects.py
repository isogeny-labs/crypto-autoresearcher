"""Committed-object soundness and large bidirectional batch regressions."""
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from tools.vault import vaultctl
from tools.vault.git_objects import read_blob, read_blobs


class GitObjectsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        self.key = mock.patch.dict(os.environ, KEY='public-git-object-regression-key')
        self.key.start()
        self.addCleanup(self.key.stop)
        self.cipher = mock.patch.object(vaultctl, '_CIPHER', None)
        self.cipher.start()
        self.addCleanup(self.cipher.stop)

    def store(self, data):
        return subprocess.check_output(['git', '-C', str(self.root), 'hash-object', '-w', '--stdin'],
                                       input=data).decode().strip()

    def test_plain_encrypted_empty_and_binary_objects(self):
        data = [b'legacy text\n', b'\x00\xff\x01', b'']
        ids = [self.store(item) for item in data]
        ids += [self.store(vaultctl.encrypt(item)) for item in data]
        self.assertEqual(list(read_blobs(self.root, ids)), data + data)
        for oid, expected in zip(ids, data + data):
            self.assertEqual(read_blob(self.root, oid), expected)

    def test_committed_path_does_not_use_modified_worktree(self):
        payload = b'{"committed":true}\n'
        oid = self.store(vaultctl.encrypt(payload))
        subprocess.run(['git', '-C', str(self.root), 'update-index', '--add', '--cacheinfo',
                        '100644,' + oid + ',data.json'], check=True)
        (self.root / 'data.json').write_bytes(b'changed worktree\n')
        self.assertEqual(read_blob(self.root, ':data.json'), payload)

    def test_batch_larger_than_pipe_capacity_finishes_and_preserves_order(self):
        data = [b'a' * 2048, b'b' * 4096]
        ids = [self.store(vaultctl.encrypt(item)) for item in data]
        count = 2100
        digests = [hashlib.sha256(item).digest() for item in data]
        for i, item in enumerate(read_blobs(self.root, [ids[i % 2] for i in range(count)])):
            self.assertEqual(hashlib.sha256(item).digest(), digests[i % 2])
        self.assertEqual(i + 1, count)

    def test_corrupt_ciphertext_is_never_returned_as_plaintext(self):
        encrypted = vaultctl.encrypt(b'sealed')
        bad = encrypted[:-1] + bytes([encrypted[-1] ^ 1])
        oid = self.store(bad)
        with self.assertRaises(vaultctl.VaultError):
            read_blob(self.root, oid)
        with self.assertRaises(vaultctl.VaultError):
            list(read_blobs(self.root, [oid]))

    def test_absent_and_non_blob_requests_are_rejected(self):
        missing = '0' * 40
        self.assertIsNone(read_blob(self.root, missing, missing_ok=True))
        with self.assertRaises(subprocess.CalledProcessError):
            read_blob(self.root, missing)
        with self.assertRaises(ValueError):
            list(read_blobs(self.root, [missing]))
        with self.assertRaises(ValueError):
            list(read_blobs(self.root, ['HEAD:data.json\ninjected']))


if __name__ == '__main__':
    unittest.main()
