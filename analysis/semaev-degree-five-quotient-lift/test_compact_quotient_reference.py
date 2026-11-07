#!/usr/bin/env python3
"""Exact retained-certificate tests for the compact quotient criterion."""

from pathlib import Path
import sys
import unittest

from check_trace_slice_certificate import read_certificate
from compact_quotient_reference import ProvisionalMap, check_compact


class CompactQuotientReferenceTests(unittest.TestCase):
    def test_retained_n6_d5_map_factors_through_compact_certificate(self):
        root = Path(__file__).resolve().parent / 'validation/cascade-20261029-v2/0'
        n, d, q, masks4, rows4 = read_certificate(root / 'degree4.bin')
        n5, d5, q5, masks5, rows5 = read_certificate(root / 'degree5.bin')
        self.assertEqual((n, d, q, n5, d5, q5), (6, 4, 3, 6, 5, 3))
        provisional = ProvisionalMap(n, d, masks4, rows4, q)
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent /
                               'semaev-m2-last-fall-degree/verify'))
        from cert_check import descend
        variables, generators = descend(6, 0x43, 0, 0x3, 0x2,
                                        [0x1, 0x2, 0x4])
        self.assertEqual(variables, n)
        full = dict(zip(masks5, rows5))
        h = ([full[m] for m in provisional.standard] +
             [full[provisional.reps[j]] for j in range(q)])
        result = check_compact(provisional, h, generators)
        self.assertEqual(result['rank'], q5)
        self.assertNotEqual(result['constant_image'], 0)
        for mask, expected in full.items():
            vector = provisional.phi(mask)
            actual = 0
            while vector:
                bit = (vector & -vector).bit_length() - 1
                actual ^= h[bit]
                vector &= vector - 1
            self.assertEqual(actual, expected, mask)

    def test_compact_tampering_is_rejected(self):
        root = Path(__file__).resolve().parent / 'validation/cascade-20261029-v2/0'
        n, d, q, masks4, rows4 = read_certificate(root / 'degree4.bin')
        _, _, _, masks5, rows5 = read_certificate(root / 'degree5.bin')
        provisional = ProvisionalMap(n, d, masks4, rows4, q)
        full = dict(zip(masks5, rows5))
        h = ([full[m] for m in provisional.standard] +
             [full[provisional.reps[j]] for j in range(q)])
        tampered = h.copy()
        tampered[-1] = 0
        with self.assertRaisesRegex(ValueError, 'constant killed'):
            check_compact(provisional, tampered, [])

    def test_recursive_high_rewrite_on_two_point_quotient(self):
        # This seed is evaluation on (0,0,0) and (1,1,1), in a rebased
        # coordinate system. All degree-two monomials must rewrite through
        # the later representative z.
        provisional = ProvisionalMap(3, 1, (1, 2, 4, 0), (1, 1, 1, 2), 2)
        self.assertEqual(provisional.standard, [])
        self.assertEqual(provisional.phi(3), provisional.phi(5))
        self.assertEqual(provisional.phi(5), provisional.phi(6))
        self.assertEqual(check_compact(provisional, [1, 2], [])['rank'], 2)
        with self.assertRaisesRegex(ValueError, 'generator not killed'):
            check_compact(provisional, [1, 2], [{0}])


if __name__ == '__main__':
    unittest.main()
