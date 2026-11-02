#!/usr/bin/env python3
"""Small exact checks for trace-sliced certificate production and verification."""
import hashlib
import json
from math import comb
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_trace_slice_certificate import (check_map, read_certificate,
                                           substitute, trace_slice)
from slice_trace_certificate import project


class TraceSliceCertificateTests(unittest.TestCase):
    def test_project_and_independent_check_with_nondirect_unit_rows(self):
        # Two evaluations on y=x0+x1+1=0. The projected map has rank two,
        # although its monomial rows include no unit vector for coordinate 0.
        masks = [m for m in range(8) if bin(m).count('1') <= 2]
        points = [1, 5]
        rows = [sum((1 << j) for j, p in enumerate(points) if m & p == m)
                for m in masks]
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'source.bin'
            output = Path(tmp) / 'slice.bin'
            with source.open('wb') as stream:
                stream.write(struct.pack('<4q', 3, 2, len(masks), 2))
                stream.write(struct.pack('<' + str(len(masks)) + 'Q', *masks))
                for row in rows:
                    stream.write(struct.pack('<Q', row))
            source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, 'digest mismatch'):
                project(source, output, 0, '0' * 64)
            self.assertFalse(output.exists())
            projected = project(source, output, 0, source_hash)
            self.assertEqual(projected['columns'], sum(comb(2, d) for d in range(3)))
            n, degree, codim, small_masks, small_rows = read_certificate(output)
            self.assertNotIn(1, small_rows)
            self.assertEqual(check_map(n, degree, codim, small_masks, small_rows,
                                       [substitute({0, 1, 2}, 0, [0, 2])])['status'],
                             'valid_trace_slice_nonmembership')
            with self.assertRaises(FileExistsError):
                project(source, output, 0, source_hash)

    def test_checker_rejects_bad_generator_and_bad_closure(self):
        masks = (0, 1, 2, 3)
        rows = (3, 1, 2, 1)
        with self.assertRaisesRegex(ValueError, 'C1'):
            check_map(2, 2, 2, masks, rows, [{0}])
        with self.assertRaisesRegex(ValueError, 'C2'):
            check_map(2, 2, 2, masks, rows, [set()])

    def test_named_odd_instance_has_independent_trace_identity(self):
        records = json.loads((Path(__file__).resolve().parents[1] /
                              'semaev-m2-last-fall-degree/results/instances.json').read_text())
        record = next(r for r in records if r['n'] == 19 and r['basis'] == 'poly')
        n, sliced, affine = trace_slice(record, len(record['V_basis_hex']))
        self.assertEqual(n, 2 * len(record['V_basis_hex']) - 1)
        self.assertEqual(len(sliced), 19)
        self.assertIn(1, affine)  # a_0 appears because Tr(1)=1 for odd n.

    def test_frontier_candidate_selection_uses_actual_trace(self):
        root = Path(__file__).resolve().parent
        n50 = json.loads((root / 'n50-poly03-d5-local-no-checkpoint-plan-002.json').read_text())
        sys.path.insert(0, str(root.parent / 'semaev-m2-last-fall-degree/verify'))
        from cert_check import mk_field
        record = n50['record']
        _, _, trace = mk_field(record['n'], int(record['modulus_hex'], 16))
        self.assertTrue(all(trace(int(v, 16)) == 0 for v in record['V_basis_hex']))
        with self.assertRaisesRegex(ValueError, 'zero trace'):
            trace_slice(record, 25)
        n51 = json.loads((root / 'n51-poly01-d5-stream-request-001.json').read_text())
        n, polys, affine = trace_slice(n51['record'], 26)
        self.assertEqual((n, len(polys)), (51, 51))
        self.assertIn(1, affine)


if __name__ == '__main__':
    unittest.main()
