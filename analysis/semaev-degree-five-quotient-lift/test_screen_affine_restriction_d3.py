#!/usr/bin/env python3
"""Focused correctness controls for the bounded affine-restriction D3 screen."""

import struct
import unittest

from screen_affine_restriction_d3 import (MAGIC, read_generators, restrict,
                                          screen_w3)


class RestrictionD3Tests(unittest.TestCase):
    def test_restriction_substitution_and_cancellation(self):
        # x0*x1 + x0 + x1 becomes 1 for x0=1, and x1 for x0=0.
        poly = {(1 << 0) | (1 << 1), 1 << 0, 1 << 1}
        self.assertEqual(restrict([poly], 2, {0: 1}), (1, [{0}]))
        self.assertEqual(restrict([poly], 2, {0: 0}), (1, [{1}]))

    def test_w3_positive_and_negative_controls(self):
        self.assertTrue(screen_w3(2, [{1}, {0, 1}], 20)['one_in_w3'])
        self.assertFalse(screen_w3(2, [{1, 2}], 20)['one_in_w3'])
        self.assertTrue(screen_w3(2, [{3, 0}, {3}], 20)['one_in_w3'])

    def test_binary_parser_rejects_duplicate_and_trailing_terms(self):
        header = MAGIC + struct.pack('<QQQ', 2, 1, 2)
        with self.assertRaisesRegex(ValueError, 'invalid quadratic generator'):
            read_generators(header + struct.pack('<QQ', 1, 1))
        valid = MAGIC + struct.pack('<QQQQ', 2, 1, 1, 1)
        self.assertEqual(read_generators(valid), (2, [{1}]))
        with self.assertRaisesRegex(ValueError, 'trailing generator bytes'):
            read_generators(valid + b'\0')


if __name__ == '__main__':
    unittest.main()
