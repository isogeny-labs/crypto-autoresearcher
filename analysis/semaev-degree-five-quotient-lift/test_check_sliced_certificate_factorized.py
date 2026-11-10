#!/usr/bin/env python3
"""Independent small exact tests of the mapped-row quotient checker."""

import hashlib
import itertools
import json
from math import comb
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

from check_sliced_certificate_factorized import (MappedCertificate,
                                                  PreadCertificate,
                                                  full_system,
                                                  check_map_factorized)
from check_quotient_closure_factorized import check_closure_factorized
from check_trace_slice_certificate import check_map, read_certificate, trace_slice
from slice_trace_certificate import project


class FactorizedCertificateTests(unittest.TestCase):
    def test_bounded_low_row_cache_preserves_closure_and_skips_re_reads(self):
        class CountedRows:
            def __init__(self, values):
                self.values = values
                self.reads = 0

            def __len__(self):
                return len(self.values)

            def __getitem__(self, index):
                self.reads += 1
                return self.values[index]

        masks = (0, 1, 2, 3)
        plain = CountedRows((3, 2, 0, 0))
        cached = CountedRows((3, 2, 0, 0))
        self.assertEqual(check_closure_factorized(2, 2, masks, plain),
                         check_closure_factorized(2, 2, masks, cached,
                                                  row_bytes=8,
                                                  max_low_cache_bytes=432))
        self.assertLess(cached.reads, plain.reads)
        refused = CountedRows((3, 2, 0, 0))
        check_closure_factorized(2, 2, masks, refused, row_bytes=8,
                                 max_low_cache_bytes=431)
        self.assertEqual(refused.reads, plain.reads)

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
                    for reader in (MappedCertificate, PreadCertificate):
                        with self.subTest(reader=reader.__name__):
                            with reader(path) as certificate:
                                if expected_error is None:
                                    result = check_map_factorized(certificate, polys)
                                    self.assertEqual(result['codimension_lower_bound'], 2)
                                else:
                                    with self.assertRaisesRegex(ValueError, expected_error):
                                        check_map_factorized(certificate, polys)
            self.write_map(path, [3, 2, 0, 0])
            with path.open('ab') as stream:
                stream.write(b'!')
            for reader in (MappedCertificate, PreadCertificate):
                with self.assertRaisesRegex(ValueError, 'length'):
                    reader(path)

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
            with PreadCertificate(output) as certificate:
                streamed = check_map_factorized(certificate, polys)
            self.assertEqual(result['status'], 'valid_affine_slice_nonmembership')
            self.assertEqual(result['codimension_lower_bound'], 3)
            self.assertEqual(streamed['low_kernel_dimension'],
                             result['low_kernel_dimension'])
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
            self.assertEqual(json.loads(accepted.stdout)['checker_method'],
                             'pread_rows_factorized_closure')
            mapped = subprocess.run(command + ['--row-access', 'mapped'],
                                    capture_output=True, text=True)
            self.assertEqual(mapped.returncode, 0, mapped.stderr)
            self.assertEqual(json.loads(mapped.stdout)['checker_method'],
                             'mapped_rows_factorized_closure')
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
            with PreadCertificate(output) as certificate:
                streamed = check_map_factorized(certificate, polys)
            cert_n, degree, codim, masks, rows = read_certificate(output)
            original = check_map(cert_n, degree, codim, masks, rows, polys)
            self.assertEqual((n, degree, codim), (5, 5, 3))
            self.assertEqual(result['low_kernel_dimension'], 28)
            self.assertEqual(result['low_kernel_dimension'],
                             original['low_kernel_dimension'])
            self.assertEqual(streamed['low_kernel_dimension'],
                             original['low_kernel_dimension'])

    def test_cli_full_original_retained_degree_five(self):
        root = Path(__file__).resolve().parent
        source = root / 'validation/cascade-20261029-v2/0/degree5.bin'
        record = {'n': 6, 'modulus_hex': '43', 'a2': 0, 'a6_hex': '3',
                  'z_hex': '2', 'V_basis_hex': ['1', '2', '4'], 'k': 3}
        digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            plan = Path(tmp) / 'plan.json'
            plan.write_text(json.dumps({'record': record}, sort_keys=True))
            command = [sys.executable,
                       str(root / 'check_sliced_certificate_factorized.py'),
                       str(source), '--plan', str(plan),
                       '--expect-plan-sha256', digest(plan),
                       '--expect-descent-source-sha256',
                       digest(root.parent / 'semaev-m2-last-fall-degree/verify/cert_check.py'),
                       '--expect-closure-source-sha256',
                       digest(root / 'check_quotient_closure_factorized.py'),
                       '--full-original', '--expect-certificate-sha256',
                       digest(source)]
            accepted = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            result = json.loads(accepted.stdout)
            self.assertEqual(result['status'], 'valid_full_nonmembership')
            self.assertEqual((result['variables'], result['degree'],
                              result['codimension_lower_bound']), (6, 5, 3))
            rejected = subprocess.run(command + ['--affine-combination-mask',
                                                  '0x24'],
                                      capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('only valid for a slice', rejected.stderr)

    def test_frozen_n47_full_system_has_original_dimensions(self):
        root = Path(__file__).resolve().parent
        plan = json.loads((root / 'n47-rand00-d5-local-plan-002.json').read_text())
        n, polys = full_system(plan['record'],
                               root.parent /
                               'semaev-m2-last-fall-degree/verify/cert_check.py')
        self.assertEqual((n, len(polys)), (48, 47))
        self.assertLessEqual(max(bin(m).count('1') for p in polys for m in p), 2)

    def test_sparse_large_certificate_opens_under_address_cap(self):
        # Sparse rows keep this fixture small on disk while its logical row
        # payload exceeds the child's address-space limit.
        n, degree, codim = 30, 5, 20_000
        columns = sum(comb(n, d) for d in range(degree + 1))
        row_bytes = 8 * ((codim + 63) // 64)
        file_bytes = 32 + 8 * columns + row_bytes * columns
        self.assertGreater(file_bytes, 256 << 20)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'sparse.bin'
            with path.open('wb') as stream:
                stream.write(struct.pack('<4q', n, degree, columns, codim))
                for d in range(degree + 1):
                    for indices in itertools.combinations(range(n), d):
                        stream.write(struct.pack('<Q', sum(1 << i for i in indices)))
                stream.truncate(file_bytes)
            child = '''
import resource, sys
from check_sliced_certificate_factorized import MappedCertificate, PreadCertificate
resource.setrlimit(resource.RLIMIT_AS, (256 << 20, 256 << 20))
with PreadCertificate(sys.argv[1]) as cert:
    assert (cert.n, cert.degree, cert.codim) == (30, 5, 20000)
    assert cert.rows[0] == cert.rows[len(cert.rows) - 1] == 0
try:
    MappedCertificate(sys.argv[1])
except OSError:
    pass
else:
    raise AssertionError('whole-file mapping bypassed the address cap')
'''
            result = subprocess.run([sys.executable, '-c', child, str(path)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
