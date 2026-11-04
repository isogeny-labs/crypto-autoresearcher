import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest

from certificate import check, digest
from fixture_builder import build

ROOT = Path(__file__).resolve().parents[2]


def system(p, n, *rows):
    return {"prime": p, "variables": n,
            "generators": [[[m, c] for m, c in sorted(row.items())] for row in rows]}


class CertificateTests(unittest.TestCase):
    def check(self, doc):
        return check(doc, digest(doc["system"]))

    def test_prime_two_sided_unsat(self):
        # Over F5, x+y=0 and xy-1=0 have no Boolean solution.
        s = system(5, 2, {1: 1, 2: 1}, {0: 4, 3: 1})
        low, high = (self.check(build(s, d)) for d in (1, 2))
        self.assertEqual((low['lfd_lower_bound'], high['lfd_upper_bound']), (2, 2))
        self.assertEqual(high['solutions'], 0)
        self.assertEqual(high['kernel_premises'], 0)

    def test_binary_mutant_closure(self):
        s = system(2, 2, {1: 1, 3: 1}, {0: 1, 3: 1})
        result = self.check(build(s, 2))
        self.assertEqual((result['rank'], result['solutions']), (3, 1))
        # No literal input is low-degree. Their combination is low-degree
        # and has a product absent from their original two-dimensional span.
        bad = {"schema": "boolean.closed-space-certificate/v1", "system": s,
               "degree": 2, "steps": [{"op": "input", "index": 0},
                                          {"op": "input", "index": 1}], "basis": [0, 1]}
        with self.assertRaisesRegex(ValueError, 'not closed'):
            self.check(bad)

    def test_superspace_is_not_exact_without_primal_provenance(self):
        # For xy+1, evaluation at (1,1) has a closed 3D kernel but W2 is 1D.
        s = system(2, 2, {0: 1, 3: 1})
        good = build(s, 2)
        self.assertEqual(self.check(good)['rank'], 1)
        good['steps'].append({'op': 'kernel', 'terms': [[0, 1], [1, 1]]})
        good['basis'].append(len(good['steps']) - 1)
        with self.assertRaisesRegex(ValueError, 'kernel premises'):
            self.check(good)

    def test_changed_input_hash(self):
        s = system(2, 1, {1: 1})
        doc = build(s, 1)
        expected = digest(s)
        doc['system']['generators'][0] = [[0, 1]]
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            check(doc, expected)

    def test_malformed_rules(self):
        base = build(system(2, 2, {1: 1}), 1)
        bad_steps = [
            {'op': 'add', 'left': 999, 'right': 0, 'coefficient': 1},
            {'op': 'mul', 'ref': 0, 'variable': 0},  # actual product drops, but strict budget fails
            {'op': 'mul', 'ref': 0, 'variable': True},
            {'op': 'input', 'index': -1},
        ]
        for step in bad_steps:
            with self.subTest(step=step):
                doc = copy.deepcopy(base)
                doc['steps'].append(step)
                with self.assertRaises(ValueError):
                    self.check(doc)

    def test_composite_coefficient_modulus_rejected(self):
        with self.assertRaisesRegex(ValueError, 'prime'):
            build(system(4, 1, {1: 1}), 1)

    def test_satisfiable_lower_bound_uses_codimension(self):
        s = system(5, 2, {1: 1, 2: 4})
        result = self.check(build(s, 1))
        self.assertFalse(result['contains_one'])
        self.assertEqual(result['solutions'], 2)
        self.assertIsNone(result['lfd_lower_bound'])

    def test_handwritten_sat_positive_witness(self):
        # Handwritten certificate, independent of the fixture producer.
        # The sole solution of xy-1=0 on the Boolean cube is (1,1).
        # y-xy = -y*(xy-1) + x*(y^2-y) lies in the ordinary ideal,
        # but is outside the one-dimensional W2 span of xy-1.
        s = system(5, 2, {0: 4, 3: 1})
        doc = {"schema": "boolean.closed-space-certificate/v1", "system": s,
               "degree": 2, "steps": [{"op": "input", "index": 0}], "basis": [0]}
        result = self.check(doc)
        self.assertEqual(result['solutions'], 1)
        self.assertEqual(result['lfd_lower_bound'], 3)
        self.assertEqual(result['missing_consequence'], [[2, 1], [3, 4]])

    def test_historical_semaev_closed_filtration(self):
        path = ROOT / 'docs/reports/2026-10-26-semaev-closure-review/audit.py'
        spec = importlib.util.spec_from_file_location('historical_audit', path)
        audit = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(audit)
        raw = subprocess.check_output(['git', 'show', 'HEAD:' + audit.ARCHIVE], cwd=ROOT)
        draw = next(x for x in json.loads(raw)['draws'] if
                    (x['n'], x['nprime'], x['draw']) == (4, 4, 1))
        equations = audit.derive_equations(draw['basis'], draw['xR'])
        self.assertEqual(equations, draw['equations'])
        self.assertEqual(hashlib.sha256(json.dumps(equations, separators=(',', ':')).encode()).hexdigest(),
                         audit.EQUATIONS_SHA256)
        s = system(2, 8, *({m: 1 for m in row} for row in equations))
        results = [self.check(build(s, d)) for d in (1, 2, 3)]
        self.assertEqual([r['rank'] for r in results], [1, 11, 79])
        self.assertEqual([r['kernel_premises'] for r in results], [0, 0, 0])
        # These are exact quotient closures, not the historical literal ranks 1,11,53.

class NormalizationTests(unittest.TestCase):
    def test_explicit_field_equation_repairs(self):
        from normalization import normalize, check_repair
        for p in (2, 5, 65537):
            raw = {(4, 2): 1, (1, 3): p-1, (0, 0): 1}
            nf, q = normalize(raw, p, 2)
            self.assertTrue(check_repair(raw, nf, q, p, 2, 6))
            with self.assertRaises(ValueError):
                check_repair(raw, nf, q, p, 2, 5)
            nf[(0, 0)] = (nf.get((0, 0), 0) + 1) % p
            nf = {e: c for e, c in nf.items() if c}
            with self.assertRaisesRegex(ValueError, 'identity failed'):
                check_repair(raw, nf, q, p, 2, 6)


if __name__ == '__main__':
    unittest.main()
