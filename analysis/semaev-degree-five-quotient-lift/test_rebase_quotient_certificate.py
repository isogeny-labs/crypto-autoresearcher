#!/usr/bin/env python3
"""Focused controls for rebasing a valid but non-unit quotient map."""
import hashlib
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

SOURCE = Path(__file__).with_name("rebase_quotient_certificate.py")
SPEC = importlib.util.spec_from_file_location("rebase_quotient_certificate", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def make_certificate(path):
    # The first three rows span F_2^3 but none is a unit vector.
    masks = [3, 5, 6, 1, 2, 4, 0]
    rows = [0b011, 0b101, 0b111, 0b000, 0b110, 0b000, 0b011]
    with path.open("wb") as stream:
        stream.write(struct.pack("<4q", 3, 2, 7, 3))
        stream.write(struct.pack("<7Q", *masks))
        for row in rows:
            stream.write(struct.pack("<Q", row))
    return rows


class RebaseTest(unittest.TestCase):
    def test_nonunit_map_rebases_without_changing_kernel(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.bin"
            target = Path(tmp) / "rebased.bin"
            original = make_certificate(source)
            sha = hashlib.sha256(source.read_bytes()).hexdigest()
            self.assertEqual(len({r for r in original if r and r & (r - 1) == 0}), 0)
            result = MODULE.rebase(source, target, sha)
            self.assertEqual(result["unit_representatives"], 3)
            data = target.read_bytes()
            rebased = list(struct.unpack_from("<7Q", data, 32 + 7 * 8))
            self.assertEqual(len({r for r in rebased if r and r & (r - 1) == 0}), 3)
            for subset in range(1 << 7):
                left = 0
                right = 0
                for i in range(7):
                    if subset >> i & 1:
                        left ^= original[i]
                        right ^= rebased[i]
                self.assertEqual(left == 0, right == 0)

    def test_wrong_source_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.bin"
            target = Path(tmp) / "rebased.bin"
            make_certificate(source)
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                MODULE.rebase(source, target, "0" * 64)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
