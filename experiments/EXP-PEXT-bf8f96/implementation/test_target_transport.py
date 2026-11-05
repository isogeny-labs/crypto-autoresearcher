"""Exact software controls for all-T quotient coordinate transport."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from check_compact_class_inputs import BasisField
from check_curve_class_certificate import family_models, orbit
from check_quotient_certificate import Curve
from check_structure_certificate import cocycle, inverse, multiply, normalize
from target_transport import AlgebraCurve, synthesize, verify


class TransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix='pext-transport-software-')
        source = Path(__file__).with_name('quotient_certificate.rs')
        joined = Path(__file__).with_name('join_certificate.rs')
        cls.producer = Path(cls.scratch.name)/'quotient'
        cls.join_producer = Path(cls.scratch.name)/'join'
        subprocess.run(['rustc', '--edition=2021', str(source), '-o', str(cls.producer)], check=True)
        subprocess.run(['rustc', '--edition=2021', str(joined), '-o', str(cls.join_producer)], check=True)
        cls.records = {name: json.loads(subprocess.check_output([cls.producer, name]))
                       for name in ['f3-char3', 'f5-odd', 'f9-embedded', 'f125-embedded']}
        cls.join_record = json.loads(subprocess.check_output([cls.join_producer, 'f27-char3']))

    @classmethod
    def tearDownClass(cls): cls.scratch.cleanup()

    def test_all_small_field_classes_and_all_T_Q(self):
        for name in ['f3-char3', 'f5-odd']:
            field = self.records[name]['field']; f = BasisField(field)
            remaining = set(family_models(f)); model_count = case_count = 0
            while remaining:
                model = min(remaining, key=lambda m: (0 if f.p == 3 and m[0] else 1, *(f.log[v] for v in m)))
                remaining -= orbit(f, model); model_count += 1
                curve = Curve(f, list(model)); algebra = AlgebraCurve(f, list(model))
                for p in curve.points:
                    for q in curve.points:
                        self.assertEqual(algebra.add(p, q), curve.add(p, q))
                for t in curve.points:
                    source = list(t) if t is not None else None
                    for q in curve.points:
                        half = list(q) if q is not None else None
                        cert = synthesize(field, list(model), source, half)
                        self.assertTrue(verify(cert, {k: cert[k] for k in ('field', 'curve', 'source_target', 'half')})['valid'])
                        case_count += 1
            self.assertEqual(model_count, 8 if f.p == 3 else 12)
            self.assertGreater(case_count, model_count)
            print(json.dumps({'fixture': name, 'classes': model_count, 'all_T_Q': case_count}, sort_keys=True))

    def test_extensions_and_twists(self):
        base = self.records['f9-embedded']; field = base['field']; f = BasisField(field)
        results = {}
        for model in [[1, 0, 1], [1, 0, 2], [0, 1, 1]]:  # char3 A, twist, B
            curve = Curve(f, model); count = 0
            for t in curve.points:
                for q in curve.points:
                    cert = synthesize(field, model, list(t) if t is not None else None,
                                      list(q) if q is not None else None)
                    self.assertTrue(verify(cert, {k: cert[k] for k in ('field', 'curve', 'source_target', 'half')})['valid'])
                    count += 1
            results[str(model)] = count
        record = self.join_record; field = record['field']; model = record['classes'][0]['model']
        curve = Curve(BasisField(field), model)
        selected = sorted(curve.points, key=curve.key)
        for t in [None, selected[len(selected)//2], selected[-1]]:
            for q in [None, selected[1], selected[len(selected)//2], selected[-1]]:
                cert = synthesize(field, model, list(t) if t is not None else None,
                                  list(q) if q is not None else None)
                self.assertTrue(verify(cert, {k: cert[k] for k in ('field', 'curve', 'source_target', 'half')})['valid'])
        big = self.records['f125-embedded']; field = big['field']; model = big['curve']
        selected = big['points']
        for t in [None, selected[len(selected)//2], selected[-1]]:
            for q in [None, selected[1], selected[-1]]:
                cert = synthesize(field, model, t, q)
                self.assertTrue(verify(cert, {k: cert[k] for k in ('field', 'curve', 'source_target', 'half')})['valid'])
        print(json.dumps({'f9_all_T_Q_by_model': results, 'f27_selected': 12, 'f125_selected': 9}, sort_keys=True))

    def test_matrix_ordinate_composition(self):
        record = self.records['f3-char3']; field = record['field']; f = BasisField(field)
        points = record['points']; curve = Curve(f, record['curve'])
        for t in points:
            for q1 in points:
                first = synthesize(field, record['curve'], t, q1)
                t1 = first['target']
                for q2 in points:
                    second = synthesize(field, record['curve'], t1, q2)
                    combined = curve.add(curve.read_point(q1), curve.read_point(q2))
                    direct = synthesize(field, record['curve'], t, list(combined) if combined is not None else None)
                    raw = multiply(f, second['matrix'], first['matrix'])
                    scale = next(v for v in raw if v)
                    self.assertEqual(normalize(f, raw), direct['matrix'])
                    self.assertEqual(f.div(f.mul(first['kappa'], second['kappa']), f.mul(scale, scale)), direct['kappa'])
        print(json.dumps({'composition_triples': len(points)**3}))

    def test_projective_cocycle_reindexing(self):
        record = self.join_record; field = record['field']; f = BasisField(field)
        model = record['classes'][0]['model']; curve = Curve(f, model)
        q = next(p for p in curve.points if p is not None)
        cert = synthesize(field, model, None, list(q)); a = cert['matrix']
        sigma_a = [f.power(v, f.p) for v in a]
        for row in [record['rows'][0], record['rows'][len(record['rows'])//2], record['rows'][-1]]:
            n = row['matrix']
            left = cocycle(f, normalize(f, multiply(f, n, inverse(f, a))))
            right = normalize(f, multiply(f, multiply(f, a, cocycle(f, n)), inverse(f, sigma_a)))
            self.assertEqual(left, right)

    def test_mutation_and_cli(self):
        record = self.records['f5-odd']; points = record['points']
        cert = synthesize(record['field'], record['curve'], None, points[1])
        expected = {k: cert[k] for k in ('field', 'curve', 'source_target', 'half')}
        mutations = [
            lambda x: x['matrix'].__setitem__(0, (x['matrix'][0]+1) % 5),
            lambda x: x.__setitem__('kappa', 0),
            lambda x: x.__setitem__('kappa', (-x['kappa']) % 5),
            lambda x: x['source_form'].__setitem__(0, (x['source_form'][0]+1) % 5),
            lambda x: x['target_form'].__setitem__(0, (x['target_form'][0]+1) % 5),
            lambda x: x.__setitem__('target', None),
            lambda x: x.__setitem__('matrix', [0, 0, 0, 0]),
            lambda x: x.__setitem__('matrix', [2*v % 5 for v in x['matrix']]),
            lambda x: x.__setitem__('half', None),
            lambda x: x.__setitem__('source_target', points[1]),
            lambda x: x.__setitem__('extra', 1),
        ]
        for mutate in mutations:
            broken = copy.deepcopy(cert); mutate(broken)
            with self.subTest(mutation=mutate):
                with self.assertRaises((ValueError, TypeError)): verify(broken, expected)
        wrong = copy.deepcopy(expected); wrong['half'] = None
        with self.assertRaises(ValueError): verify(cert, wrong)
        path = Path(self.scratch.name)/'cert.json'; inp = Path(self.scratch.name)/'input.json'
        path.write_text(json.dumps(cert)); inp.write_text(json.dumps(expected))
        command = [sys.executable, str(Path(__file__).with_name('target_transport.py')), str(path), '--expected-input', str(inp)]
        accepted = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertTrue(json.loads(accepted.stdout)['valid'])
        inp.write_text(json.dumps(wrong))
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)


if __name__ == '__main__': unittest.main(verbosity=2)
