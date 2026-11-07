import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools.hydrate_bench_validations import hydrate


class HydrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "records").mkdir()
        (self.root / ".benchrec.json").write_text('{"records_dir":"records"}')
        self.record = self.root / "records/one.json"
        self.record.write_text('{"validation":"run/analysis.json"}')
        self.logical = self.root / "run/analysis.json"
        self.archive = self.root / "run/analysis.json.gz"
        self.receipt = self.root / "run/derived-encodings/analysis.json"
        self.receipt.parent.mkdir(parents=True)
        self.payload = b'{"verified":true}\n'
        self.encoded = gzip.compress(self.payload, mtime=0)
        self.archive.write_bytes(self.encoded)
        self.value = dict(original_path="analysis.json", archive_path="analysis.json.gz",
                          encoding="gzip6mtime0", original_bytes=len(self.payload),
                          archive_bytes=len(self.encoded),
                          original_sha256=hashlib.sha256(self.payload).hexdigest(),
                          archive_sha256=hashlib.sha256(self.encoded).hexdigest())
        self.save()

    def save(self):
        self.receipt.write_text(json.dumps(self.value))

    def refuses(self, error=ValueError):
        with self.assertRaises(error):
            hydrate(self.root)
        self.assertFalse(self.logical.exists())
        self.assertEqual(list(self.logical.parent.glob(".validation-*")), [])

    def test_restore_and_idempotence_leave_records_unchanged(self):
        before = self.record.read_bytes(), self.receipt.read_bytes(), self.archive.read_bytes()
        self.assertEqual(hydrate(self.root)[0]["status"], "restored_verified")
        self.assertEqual(self.logical.read_bytes(), self.payload)
        self.assertEqual(hydrate(self.root)[0]["status"], "present_verified")
        self.assertEqual(before, (self.record.read_bytes(), self.receipt.read_bytes(), self.archive.read_bytes()))

    def test_scoped_pull_only_missing_archive(self):
        self.archive.unlink()
        calls = []
        def pull(paths):
            calls.append(paths)
            self.archive.write_bytes(self.encoded)
        hydrate(self.root, pull=pull)
        self.assertEqual(calls, [[str(self.archive)]])

    def test_bad_archive_digest(self):
        self.archive.write_bytes(b"wrong")
        self.refuses()

    def test_bad_decoded_digest(self):
        self.value["original_sha256"] = "0" * 64
        self.save()
        self.refuses()

    def test_decoded_size_limits(self):
        for size in (len(self.payload) - 1, len(self.payload) + 1):
            with self.subTest(size=size):
                self.value["original_bytes"] = size
                self.save()
                self.refuses()

    def test_gzip_crc_failure(self):
        encoded = self.encoded[:-8] + bytes([self.encoded[-8] ^ 1]) + self.encoded[-7:]
        self.archive.write_bytes(encoded)
        self.value["archive_sha256"] = hashlib.sha256(encoded).hexdigest()
        self.save()
        self.refuses(OSError)

    def test_existing_corrupt_logical_is_not_overwritten(self):
        self.logical.write_bytes(b"wrong")
        with self.assertRaises(ValueError):
            hydrate(self.root)
        self.assertEqual(self.logical.read_bytes(), b"wrong")

    def test_archive_traversal(self):
        self.value["archive_path"] = "../elsewhere.gz"
        self.save()
        self.refuses()

    def test_logical_traversal(self):
        self.record.write_text('{"validation":"../outside.json"}')
        self.refuses()

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as outside:
            self.archive.unlink()
            self.archive.symlink_to(Path(outside) / "outside.gz")
            self.refuses()

    def test_bool_is_not_a_byte_count(self):
        self.value["original_bytes"] = True
        self.save()
        self.refuses()

    def test_no_receipt_is_left_to_benchrec(self):
        self.receipt.unlink()
        self.assertEqual(hydrate(self.root), [])
        self.assertFalse(self.logical.exists())


if __name__ == "__main__":
    unittest.main()
