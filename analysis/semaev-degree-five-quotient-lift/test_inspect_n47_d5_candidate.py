#!/usr/bin/env python3
"""Boundary controls for the native D5 checker header admission screen."""

from math import comb
from pathlib import Path
import struct
import tempfile
import unittest

from inspect_n47_d5_candidate import inspect


class HeaderScreenTest(unittest.TestCase):
    def test_frozen_size_endpoint_and_next_word(self):
        columns = sum(comb(48, i) for i in range(6))
        cap = 45_161_173_824
        plan = {'record': {'k': 24}, 'maximum_certificate_bytes': cap}
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'candidate.bin'
            with path.open('wb') as stream:
                stream.write(struct.pack('<4q', 48, 5, columns, 187_584))
                stream.truncate(cap)  # Sparse fixture: only header and length are screened.
            result = inspect(path, plan)
            self.assertEqual(result['certificate_bytes'], cap)
            self.assertEqual(result['row_bytes'], 23_448)
            self.assertEqual(result['native_paired_live_rows_payload_upper_bytes'],
                             8_796_986_160)
            self.assertEqual(result['native_paired_explicit_bytes_x86_64'],
                             53_967_351_600)
            with path.open('r+b') as stream:
                stream.write(struct.pack('<4q', 48, 5, columns, 187_585))
                stream.truncate(32 + columns * (8 + 23_456))
            with self.assertRaisesRegex(ValueError, 'frozen producer size cap'):
                inspect(path, plan)


if __name__ == '__main__':
    unittest.main()
