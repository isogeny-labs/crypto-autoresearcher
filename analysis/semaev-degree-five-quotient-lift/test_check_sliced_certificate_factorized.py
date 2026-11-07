#!/usr/bin/env python3
"""Independent small exact tests of the mapped-row quotient checker."""

import hashlib
import itertools
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

from check_sliced_certificate_factorized import MappedCertificate, check_map_factorized
from check_quotient_closure_factorized import check_closure_factorized
from check_trace_slice_certificate import check_map, read_certificate, trace_slice
from slice_trace_certificate import project


class FactorizedCertificateTests(unittest.TestCase):
    def test_small_quotient_floor_has_boolean_evaluation(self):
        # Proposition 1.10's q<d case in the smallest nontrivial ring.
        masks = (0, 1, 2, 3)
        evaluations = [tuple(int(m & point == m) for m in masks)
                       for point in range(4)]
        accepted = 0
        for rows in itertools.product(range(4), repeat=4):
            if rows[0] == 0 or len(set(rows) - {0}) < 2:
                continue
            try:
                check_closure_factorized(2, 3, masks, rows)
            except ValueError:
                continue
            functionals = [tuple(bin(a & row).count('1') % 2 for row in rows)
                           for a in range(4)]
            self.assertTrue(any(e in functionals for e in evaluations))
            accepted += 1
        self.assertEqual(accepted, 36)

    @staticmethod
    def write_map(path, rows):
        with path.open('wb') as stream:
            stream.write(struct.pack('<4q', 2, 2, 4, 2))
            stream.write(struct.pack('<4Q', 0, 1, 2, 3))
            stream.write(struct.pack('<4Q', *rows))

    def test_complete_checks_and_tampering(self):
        cases = (
            ([3, 2, 0, 0], [], None),
            ([3, 2, 0, 0], [{0}], 'C1'),
            ([0, 1, 2, 0], [], 'C3'),
            ([1, 1, 0, 0], [], 'C0'),
            ([3, 1, 2, 1], [], 'C2'),
            ([3, 2, 0, 4], [], 'C0'),
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'map.bin'
            for rows, polys, expected_error in cases:
                with self.subTest(rows=rows, polys=polys):
                    self.write_map(path, rows)
                    with MappedCertificate(path) as certificate:
                        if expected_error is None:
                            result = check_map_factorized(certificate, polys)
                            self.assertEqual(result['codimension_lower_bound'], 2)
                        else:
                            with self.assertRaisesRegex(ValueError, expected_error):
                                check_map_factorized(certificate, polys)
            self.write_map(path, [3, 2, 0, 0])
            with path.open('ab') as stream:
                stream.write(b'!')
            with self.assertRaisesRegex(ValueError, 'length'):
                MappedCertificate(path)

    def test_retained_n6_slice_agrees_with_pinned_checker(self):
        root = Path(__file__).resolve().parent
        source = root / 'validation/cascade-20261029-v2/0/degree4.bin'
        source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        self.assertEqual(source_hash,
                         'cfe306125fef4482fb86b15966c7be5ec6e26ed5ca09d5addafd2c5f9e079c4a')
        record = {'n': 6, 'modulus_hex': '43', 'a2': 0, 'a6_hex': '3',
                  'z_hex': '2', 'V_basis_hex': ['1', '2', '4']}
        n, polys, _ = trace_slice(record, 3, 0x24)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'slice.bin'
            project(source, output, 3, source_hash)
            with MappedCertificate(output) as certificate:
                result = check_map_factorized(certificate, polys)
            self.assertEqual(result['status'], 'valid_affine_slice_nonmembership')
            self.assertEqual(result['codimension_lower_bound'], 3)
            cert_n, degree, codim, masks, rows = read_certificate(output)
            original = check_map(cert_n, degree, codim, masks, rows, polys)
            self.assertEqual(result['low_kernel_dimension'],
                             original['low_kernel_dimension'])
            self.assertEqual(n, cert_n)

    def test_cli_binds_named_inputs_and_certificate_hash(self):
        root = Path(__file__).resolve().parent
        source = root / 'validation/cascade-20261029-v2/0/degree4.bin'
        record = {'n': 6, 'modulus_hex': '43', 'a2': 0, 'a6_hex': '3',
                  'z_hex': '2', 'V_basis_hex': ['1', '2', '4']}
        digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            output = tmp / 'slice.bin'
            plan = tmp / 'plan.json'
            plan.write_text(json.dumps({'record': record}, sort_keys=True))
            project(source, output, 3, digest(source))
            command = [sys.executable, str(root / 'check_sliced_certificate_factorized.py'),
                       str(output), '--plan', str(plan),
                       '--expect-plan-sha256', digest(plan),
                       '--expect-descent-source-sha256',
                       digest(root.parent / 'semaev-m2-last-fall-degree/verify/cert_check.py'),
                       '--expect-slice-source-sha256',
                       digest(root / 'check_trace_slice_certificate.py'),
                       '--expect-closure-source-sha256',
                       digest(root / 'check_quotient_closure_factorized.py'),
                       '--variable', '3', '--affine-combination-mask', '0x24',
                       '--expect-certificate-sha256', digest(output)]
            accepted = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            self.assertEqual(json.loads(accepted.stdout)['codimension_lower_bound'], 3)
            command[-1] = '0' * 64
            rejected = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('certificate digest mismatch', rejected.stderr)
            command[-1] = digest(output)
            closure_hash_index = command.index('--expect-closure-source-sha256') + 1
            command[closure_hash_index] = '0' * 64
            rejected = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('closure source digest mismatch', rejected.stderr)

    def test_retained_degree_five_map_agrees_with_pinned_checker(self):
        root = Path(__file__).resolve().parent
        source = root / 'validation/cascade-20261029-v2/0/degree5.bin'
        source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        self.assertEqual(source_hash,
                         '7cf2d46d96fe00dfddd1277935c7f0b6577c7ab9cbdc774151c81f56fee82d73')
        record = {'n': 6, 'modulus_hex': '43', 'a2': 0, 'a6_hex': '3',
                  'z_hex': '2', 'V_basis_hex': ['1', '2', '4']}
        n, polys, _ = trace_slice(record, 3, 0x24)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'slice.bin'
            project(source, output, 3, source_hash)
            with MappedCertificate(output) as certificate:
                result = check_map_factorized(certificate, polys)
            cert_n, degree, codim, masks, rows = read_certificate(output)
            original = check_map(cert_n, degree, codim, masks, rows, polys)
            self.assertEqual((n, degree, codim), (5, 5, 3))
            self.assertEqual(result['low_kernel_dimension'], 28)
            self.assertEqual(result['low_kernel_dimension'],
                             original['low_kernel_dimension'])


if __name__ == '__main__':
    unittest.main()
