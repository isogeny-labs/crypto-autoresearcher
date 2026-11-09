"""Fixed encoding controls only: no certificate search or closure solver."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import encode_certificate as enc


def request():
    return {'schema': enc.SCHEMA, 'degree_cap': 2, 'quotient_dimension': 1,
            'input': {'schema': enc.INPUT_SCHEMA, 'n': 3, 'modulus': 0b1011,
                      'basis': [1], 'a2': 0, 'a6': 1, 'z': 1,
                      'require_rational_target': False}}


def evaluate(equation, bits):
    out = 0
    for monomial in equation['terms']:
        term = 1
        for variable in monomial:
            term &= bits[variable]
        out ^= term
    return out


class EncodingControls(unittest.TestCase):
    def test_genuine_sat_evaluation_assignment_and_exact_sizes(self):
        # X=0,Y=1 in V={0,1}: S3(0,1,1)=1+a6=0.
        result = enc.encode(request())
        payload = result['encoding']
        self.assertEqual(payload['monomial_masks'], [0, 1, 2, 3])
        self.assertEqual(payload['variable_count'], 10)
        self.assertEqual(len(payload['equations']), 11)
        self.assertEqual(result['preflight']['M'], 4)
        self.assertEqual(result['preflight']['L'], 3)
        # q=1: C evaluates each monomial at (0,1); T=(0,1); R=e_empty.
        bits = [1, 0, 1, 0, 0, 1, 1, 0, 0, 0]
        self.assertTrue(all(evaluate(eq, bits) == 0 for eq in payload['equations']))
        self.assertFalse(result['solver_executed'])
        self.assertFalse(result['dataset_admission'])
        self.assertIsNone(result['lfd_lower_bound'])
        self.assertEqual(result['encoding_sha256'], enc.digest(payload))
        self.assertEqual(result, enc.encode(request()))

    def test_rank_two_sat_quotient_non_diagonal_layout(self):
        r = request()
        r['quotient_dimension'] = 2
        payload = enc.encode(r)['encoding']
        self.assertEqual(payload['variable_count'], 24)
        self.assertEqual(len(payload['equations']), 24)
        # Function basis (1,x) on solutions (0,1),(1,0), so y=1+x.
        bits = ([1, 0, 0, 1, 1, 1, 0, 0] +
                [0, 0, 1, 1, 1, 0, 1, 0] +
                [1, 0, 0, 1, 0, 0, 0, 0])
        self.assertTrue(all(evaluate(eq, bits) == 0 for eq in payload['equations']))
        self.assertEqual(payload['layout']['T']['offset'], 8)
        self.assertEqual(payload['layout']['R']['offset'], 16)

    def test_invalid_partial_action_and_right_inverse_detected(self):
        equations = enc.encode(request())['encoding']['equations']
        bits = [1, 0, 1, 0, 0, 0, 1, 0, 0, 0]  # Incorrect T_y=0.
        self.assertTrue(any(evaluate(eq, bits) for eq in equations if eq['kind'] == 'closure'))
        bits = [1, 0, 1, 0, 0, 1, 0, 0, 0, 0]  # Missing right inverse.
        self.assertTrue(any(evaluate(eq, bits) for eq in equations if eq['kind'] == 'right_inverse'))

    def test_preflight_refuses_before_inspection_or_combinatorial_allocation(self):
        large = request()
        large['input'].update(n=64, basis=[1 << i for i in range(64)])
        large['degree_cap'] = 64
        with patch.object(enc, 'inspect', side_effect=AssertionError('inspection ran')), patch.object(enc.itertools, 'combinations', side_effect=AssertionError('allocation ran')):
            with self.assertRaisesRegex(ValueError, 'preflight variables cap'):
                enc.encode(large)
        for name in ('variables', 'equations', 'terms'):
            caps = enc.DEFAULT_CAPS.copy()
            caps[name] = 1
            with patch.object(enc, 'inspect', side_effect=AssertionError('inspection ran')):
                with self.assertRaisesRegex(ValueError, 'preflight ' + name + ' cap'):
                    enc.encode(request(), caps)

    def test_schema_domain_and_cap_rejections(self):
        for key, value in [('degree_cap', 1), ('degree_cap', 3), ('degree_cap', True), ('quotient_dimension', 0), ('quotient_dimension', 5), ('quotient_dimension', True)]:
            r = request()
            r[key] = value
            with self.assertRaises(ValueError):
                enc.encode(r)
        r = request()
        r['extra'] = 0
        with self.assertRaises(ValueError):
            enc.encode(r)
        caps = enc.DEFAULT_CAPS.copy()
        caps['variables'] += 1
        with self.assertRaisesRegex(ValueError, 'only lower'):
            enc.encode(request(), caps)

    def test_duplicate_bounded_read_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'request.json'
            p.write_text('{"schema":1,"schema":2}')
            with self.assertRaisesRegex(ValueError, 'duplicate JSON'):
                enc.read_request(p)
            p.write_bytes(b' ' * (enc.MAX_INPUT_BYTES + 1))
            with self.assertRaisesRegex(ValueError, '64 KiB'):
                enc.read_request(p)
            p.write_text(json.dumps(request()))
            self.assertEqual(enc.read_request(p)[0], request())
            output = Path(td) / 'output.json'
            enc.write_output(output, {'preserve': 1})
            before = output.read_bytes()
            with self.assertRaises(FileExistsError):
                enc.write_output(output, {'overwrite': 1})
            self.assertEqual(before, output.read_bytes())

    def test_canonical_xor_and_no_unrequested_global_relations(self):
        self.assertEqual(enc.canonical_terms([[2, 2], [2], [], [], [3, 1]]), [[1, 3]])
        equations = enc.encode(request())['encoding']['equations']
        self.assertEqual({eq['kind'] for eq in equations}, {'unit', 'generator', 'closure', 'right_inverse'})
        self.assertEqual(sum(eq['kind'] == 'closure' for eq in equations), 6)
        for eq in equations:
            self.assertTrue(all(len(term) <= 2 for term in eq['terms']))
            self.assertEqual(eq['terms'], enc.canonical_terms(eq['terms']))

if __name__ == '__main__':
    unittest.main()
