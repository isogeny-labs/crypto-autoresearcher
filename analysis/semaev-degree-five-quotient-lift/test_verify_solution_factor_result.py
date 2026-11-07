#!/usr/bin/env python3
"""Independent replay controls with a small complete quotient map."""
from pathlib import Path
import struct
import tempfile
import unittest

from verify_solution_factor_result import replay_map


class ReviewTest(unittest.TestCase):
    def test_positive_negative_and_mutated_witness(self):
        points = [1, 2, 4, 8]
        masks = list(range(16))
        images = [sum(1 << i for i, s in enumerate(points) if m & s == m)
                  for m in masks]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'map.bin'
            def write():
                path.write_bytes(struct.pack('<4q', 4, 4, 16, 4) +
                                 struct.pack('<16Q', *masks) +
                                 b''.join(struct.pack('<Q', image) for image in images))
            write()
            self.assertEqual(replay_map(path, points, {'factorization': True}, 4, 4, 16, 4),
                             'factorization_verified')
            images[0] ^= 1
            write()
            negative = {'factorization': False, 'witness_point_hex': '1',
                        'kernel_witness_terms_hex': ['0', '2', '4', '8']}
            self.assertEqual(replay_map(path, points, negative, 4, 4, 16, 4),
                             'seed_nonvanishing_witness')
            negative['kernel_witness_terms_hex'].pop()
            with self.assertRaisesRegex(ValueError, 'fails independent replay'):
                replay_map(path, points, negative, 4, 4, 16, 4)


if __name__ == '__main__':
    unittest.main()
