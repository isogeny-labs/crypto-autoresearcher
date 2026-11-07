#!/usr/bin/env python3
"""Small positive and adversarial controls for the solution factor gate."""
import hashlib
from pathlib import Path
import struct
import tempfile
import unittest

from check_original_solution_factorization import check_factorization, check_generators


class FactorizationTest(unittest.TestCase):
    def test_complete_map_and_corrupted_constant(self):
        # The four one-hot points are separated by singleton monomials.
        # Their evaluation map has one unit row per quotient coordinate.
        points = [1, 2, 4, 8]
        masks = list(range(16))
        rows = [sum(1 << i for i, point in enumerate(points)
                    if mask & point == mask) for mask in masks]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'map.bin'
            def write():
                path.write_bytes(struct.pack('<4q', 4, 4, 16, 4) +
                                 struct.pack('<16Q', *masks) +
                                 b''.join(struct.pack('<Q', row) for row in rows))
                return hashlib.sha256(path.read_bytes()).hexdigest()
            digest = write()
            result = check_factorization(path, digest, points, 4)
            self.assertEqual(result['checked_pairs'], 4)
            self.assertTrue(result['factorization'])
            rows[0] ^= 1
            digest = write()
            negative = check_factorization(path, digest, points, 4)
            self.assertFalse(negative['factorization'])
            self.assertEqual(int(negative['witness_point_hex'], 16), points[0])
            terms = [int(x, 16) for x in negative['kernel_witness_terms_hex']]
            self.assertEqual(sum((m & points[0]) == m for m in terms) & 1, 1)

    def test_independent_generator_rejects_nonroot(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'generators.bin'
            path.write_bytes(b'SLCGEN01' + struct.pack('<QQ', 4, 1) +
                             struct.pack('<Q', 1) + struct.pack('<Q', 3))
            self.assertEqual(check_generators(path, [1, 2], 4, 1), 1)
            with self.assertRaisesRegex(ValueError, 'fails'):
                check_generators(path, [3], 4, 1)


if __name__ == '__main__':
    unittest.main()
