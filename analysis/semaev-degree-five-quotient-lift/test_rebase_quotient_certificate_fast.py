#!/usr/bin/env python3
"""Controls for the native missing-coordinate quotient rebase."""
import hashlib
import importlib.util
import itertools
from math import comb
from pathlib import Path
import random
import shutil
import struct
import subprocess
import tempfile
import unittest

DIRECTORY = Path(__file__).parent
GENERIC = DIRECTORY / "rebase_quotient_certificate.py"
NATIVE = DIRECTORY / "rebase_quotient_certificate_fast.cpp"
SPEC = importlib.util.spec_from_file_location("generic_rebase", GENERIC)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fixture(path, n, degree, codim, seed):
    masks = sorted((sum(1 << j for j in choice)
                    for d in range(degree + 1)
                    for choice in itertools.combinations(range(n), d)),
                   key=lambda mask: (-bin(mask).count("1"), mask))
    assert len(masks) == sum(comb(n, d) for d in range(degree + 1))
    rng = random.Random(seed)
    rows = [rng.getrandbits(codim) for _ in range(len(masks) - codim)]
    rows += [1 << j for j in range(codim - 1, -1, -1)]
    # An invertible three-coordinate change removes three literal unit rows.
    tail = (0b011, 0b101, 0b111)
    shifted = []
    for value in rows:
        result = value & ((1 << (codim - 3)) - 1)
        for j, image in enumerate(tail):
            if value >> (codim - 3 + j) & 1:
                result ^= image << (codim - 3)
        shifted.append(result)
    width = 8 * ((codim + 63) // 64)
    with path.open("wb") as stream:
        stream.write(struct.pack("<4q", n, degree, len(masks), codim))
        stream.write(struct.pack("<" + str(len(masks)) + "Q", *masks))
        for row in shifted:
            stream.write(row.to_bytes(width, "little"))
    return shifted


class FastRebaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("g++"):
            raise unittest.SkipTest("g++ unavailable")
        cls.build = tempfile.TemporaryDirectory()
        cls.binary = Path(cls.build.name) / "rebase_fast"
        result = subprocess.run(["g++", "-O3", "-std=c++17", "-Wall", "-Wextra",
                                 "-Werror", str(NATIVE), "-lcrypto", "-o", str(cls.binary)],
                                capture_output=True, text=True)
        if result.returncode:
            raise AssertionError(result.stderr)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "build"):
            cls.build.cleanup()

    def test_exhaustive_kernel_and_multiword_agreement(self):
        for n, degree, codim, seed in ((4, 2, 6, 17), (8, 4, 73, 987)):
            with self.subTest(codim=codim), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                source, generic, fast = (root / name for name in
                                         ("source.bin", "generic.bin", "fast.bin"))
                rows = fixture(source, n, degree, codim, seed)
                digest = hashlib.sha256(source.read_bytes()).hexdigest()
                MODULE.rebase(source, generic, digest)
                result = subprocess.run([str(self.binary), str(source), str(fast), digest],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(generic.read_bytes(), fast.read_bytes())
                if len(rows) <= 11:
                    offset = 32 + 8 * len(rows)
                    transformed = struct.unpack_from("<" + str(len(rows)) + "Q",
                                                     fast.read_bytes(), offset)
                    for subset in range(1 << len(rows)):
                        original = converted = 0
                        for j in range(len(rows)):
                            if subset >> j & 1:
                                original ^= rows[j]
                                converted ^= transformed[j]
                        self.assertEqual(original == 0, converted == 0)

    def test_bad_hash_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, target = root / "source.bin", root / "target.bin"
            fixture(source, 4, 2, 6, 17)
            result = subprocess.run([str(self.binary), str(source), str(target), "0" * 64],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
