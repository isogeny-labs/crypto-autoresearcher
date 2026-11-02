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
from check_affine_relation import verify as verify_affine_relation
from check_affine_w3 import analyze as analyze_affine_w3
from slice_trace_certificate import project


class TraceSliceCertificateTests(unittest.TestCase):
    def test_named_w3_affine_spaces_have_rank_one(self):
        for name, n, rank, low_rank in (
                ('n50-poly03-d5-local-no-checkpoint-plan-002.json', 50, 8130, 196),
                ('n51-poly01-d5-stream-request-001.json', 52, 10970, 254)):
            with self.subTest(name=name):
                result = analyze_affine_w3(name)
                self.assertEqual((result['variables'], result['w3_rank'],
                                  result['low_degree_rank'], result['affine_rank']),
                                 (n, rank, low_rank, 1))
                if n == 50:
                    pairs = (0, 3, 5, 6, 9, 10, 12, 14, 15, 17, 18, 20, 23)
                    expected = sorted([1 << j for j in pairs] +
                                      [1 << (25 + j) for j in pairs])
                else:
                    expected = [1, 1 << 26]
                self.assertEqual(result['affine_supports'], [expected])

    @staticmethod
    def quadratic_rank(polys):
        quadratic = sorted({m for poly in polys for m in poly
                            if bin(m).count('1') == 2})
        positions = {m: i for i, m in enumerate(quadratic)}
        pivots = {}
        for poly in polys:
            row = sum(1 << positions[m] for m in poly if m in positions)
            while row:
                bit = row.bit_length() - 1
                if bit in pivots:
                    row ^= pivots[bit]
                else:
                    pivots[bit] = row
                    break
        return len(pivots)

    def test_named_n50_affine_certificate_and_tamper_rejection(self):
        certificate = (Path(__file__).resolve().parent /
                       'n50-poly03-affine-relation-001.json')
        checked = verify_affine_relation(certificate)
        self.assertEqual((checked['status'], checked['quadratic_rank']),
                         ('valid_affine_relation', 48))
        tampered = json.loads(certificate.read_text())
        tampered['pair_indices'] = tampered['pair_indices'][:-1]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'tampered.json'
            path.write_text(json.dumps(tampered))
            with self.assertRaisesRegex(ValueError, 'differs from claimed'):
                verify_affine_relation(path)

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
                             'valid_affine_slice_nonmembership')
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

    def test_retained_named_certificate_projects_and_checks(self):
        root = Path(__file__).resolve().parent
        fixture = root / 'validation/panel-worker-v2-20261029/odd-a2-0'
        source = fixture / 'result/certificate.bin'
        source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        self.assertEqual(source_hash,
                         'd8552a13d300bcbec10966b52092d3754975716fd50062bab3b347b85dfbc6a9')
        self.assertIn('VALID: 1 is not in W_4(F)',
                      (fixture / 'result/check.stdout.txt').read_text())
        record = json.loads((fixture / 'instance.json').read_text())[0]
        n, polys, _ = trace_slice(record, 3)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'sliced.bin'
            projected = project(source, output, 3, source_hash)
            self.assertEqual(projected['certificate_sha256'],
                             'dc7c6c6f6f9594f1b33963a431d63c310d3780ea7337fc8902cd84dcb5920838')
            cert_n, degree, codim, masks, rows = read_certificate(output)
            self.assertEqual((cert_n, degree, codim), (n, 4, 1))
            result = check_map(n, degree, codim, masks, rows, polys)
            self.assertEqual(result['status'], 'valid_affine_slice_nonmembership')

    def test_retained_nontrace_affine_certificate_projects_and_checks(self):
        root = Path(__file__).resolve().parent
        fixture = root / 'validation/cascade-20261029-v2/0'
        source = fixture / 'degree4.bin'
        source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        self.assertEqual(source_hash,
                         'cfe306125fef4482fb86b15966c7be5ec6e26ed5ca09d5addafd2c5f9e079c4a')
        self.assertIn('VALID: 1 is not in W_4(F)',
                      (fixture / 'check4.stdout.txt').read_text())
        record = {'n': 6, 'modulus_hex': '43', 'a2': 0, 'a6_hex': '3',
                  'z_hex': '2', 'V_basis_hex': ['1', '2', '4']}
        n, polys, affine = trace_slice(record, 3, 0x24)
        self.assertEqual((n, affine), (5, [1]))
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'sliced.bin'
            projected = project(source, output, 3, source_hash)
            self.assertEqual(projected['certificate_sha256'],
                             '59cd20d3de0fde08b5d34490a9895a0f7c3d14830b8136e78e926260f28741e0')
            cert_n, degree, codim, masks, rows = read_certificate(output)
            self.assertEqual((cert_n, degree, codim), (5, 4, 3))
            result = check_map(n, degree, codim, masks, rows, polys)
            self.assertEqual(result['status'], 'valid_affine_slice_nonmembership')

    def test_frontier_candidate_selection_uses_actual_trace(self):
        root = Path(__file__).resolve().parent
        n50 = json.loads((root / 'n50-poly03-d5-local-no-checkpoint-plan-002.json').read_text())
        sys.path.insert(0, str(root.parent / 'semaev-m2-last-fall-degree/verify'))
        from cert_check import descend, mk_field
        record = n50['record']
        _, _, trace = mk_field(record['n'], int(record['modulus_hex'], 16))
        self.assertTrue(all(trace(int(v, 16)) == 0 for v in record['V_basis_hex']))
        _, original = descend(record['n'], int(record['modulus_hex'], 16),
                              record['a2'], int(record['a6_hex'], 16),
                              int(record['z_hex'], 16),
                              [int(v, 16) for v in record['V_basis_hex']])
        self.assertEqual(self.quadratic_rank(original), 48)
        with self.assertRaisesRegex(ValueError, 'zero trace'):
            trace_slice(record, 25)
        relation_mask = 0x13c4f635ad45c
        n, polys, affine = trace_slice(record, 25, relation_mask)
        self.assertEqual((n, len(polys)), (49, 50))
        pairs = (0, 3, 5, 6, 9, 10, 12, 14, 15, 17, 18, 20, 23)
        expected = {1 << j for j in pairs} | {1 << (25 + j) for j in pairs if j}
        self.assertEqual(set(affine), expected)
        with self.assertRaisesRegex(ValueError, 'not affine'):
            trace_slice(record, 25, 1)
        n51 = json.loads((root / 'n51-poly01-d5-stream-request-001.json').read_text())
        n, polys, affine = trace_slice(n51['record'], 26)
        self.assertEqual((n, len(polys)), (51, 51))
        self.assertIn(1, affine)
        record = n51['record']
        _, original = descend(record['n'], int(record['modulus_hex'], 16),
                              record['a2'], int(record['a6_hex'], 16),
                              int(record['z_hex'], 16),
                              [int(v, 16) for v in record['V_basis_hex']])
        # The trace relation spans the entire quadratic-kernel dimension one.
        self.assertEqual(self.quadratic_rank(original), 50)


if __name__ == '__main__':
    unittest.main()
