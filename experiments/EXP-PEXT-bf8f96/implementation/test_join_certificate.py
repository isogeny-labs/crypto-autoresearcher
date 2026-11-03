"""Fixed join coverage, scalar replay, and adversarial shard tests."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from check_join_certificate import verify_shards
from check_quotient_certificate import Curve
from check_compact_class_inputs import BasisField


class JoinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix='pext-join-software-')
        cls.binary = str(Path(cls.scratch.name)/'join')
        subprocess.run(['rustc', '--edition=2021', '-O', str(Path(__file__).with_name('join_certificate.rs')), '-o', cls.binary], check=True)
        cls.records = {name: json.loads(subprocess.check_output([cls.binary, name])) for name in ['f3-classes', 'f5-classes', 'f27-char3']}

    @classmethod
    def tearDownClass(cls): cls.scratch.cleanup()

    def test_complete_fixed_joins(self):
        for name, record in self.records.items():
            with self.subTest(fixture=name):
                result = verify_shards([record], name)
                self.assertEqual(result['rows'], record['total'])
                print(json.dumps(result, sort_keys=True))

    def test_native_shards_and_union(self):
        name = 'f27-char3'; record = self.records[name]; total = record['total']
        boundaries = sorted(set([0, 1, 818, 819, total-1, total]))
        shards = [json.loads(subprocess.check_output([self.binary, name, str(a), str(b)])) for a, b in zip(boundaries, boundaries[1:])]
        self.assertEqual([r for shard in shards for r in shard['rows']], record['rows'])
        self.assertTrue(verify_shards(list(reversed(shards)), name)['valid'])
        for invalid in [shards[:-1], shards+[shards[0]], [shards[0], *shards[2:]]]:
            with self.assertRaises(ValueError): verify_shards(invalid, name)
        altered = copy.deepcopy(shards); altered[1]['field']['prime'] = 5
        with self.assertRaises(ValueError): verify_shards(altered, name)
        empty = json.loads(subprocess.check_output([self.binary, name, str(total), str(total)]))
        self.assertEqual(empty['rows'], [])
        self.assertTrue(verify_shards([record, empty], name)['valid'])
        for args in [('1', '0'), ('0', str(total+1)), ('bad', '1'), ('0',)]:
            self.assertEqual(subprocess.run([self.binary, name, *args], capture_output=True).returncode, 2)

    def test_corrupted_identities_scalars_and_coverage(self):
        mutations = [
            lambda d: d['rows'].pop(),
            lambda d: d['classes'][0]['targets'].pop(),
            lambda d: d['classes'].pop(),
            lambda d: d['rows'][0].__setitem__('ordinal', True),
            lambda d: d['rows'][0].__setitem__('class_index', 1),
            lambda d: d['rows'][0].__setitem__('coset_index', 1),
            lambda d: d['rows'][0].__setitem__('structure_index', 1),
            lambda d: d['rows'][0]['model'].__setitem__(0, False),
            lambda d: d['rows'][0].__setitem__('target', [0, 0]),
            lambda d: d['rows'][0].__setitem__('matrix', [0, 0, 0, 0]),
            lambda d: d['rows'][0]['original_form'].__setitem__(0, 0),
            lambda d: d['rows'][0]['transformed_form'].__setitem__(3, 0),
            lambda d: d['rows'][0]['conjugates'][0].__setitem__(3, 0),
            lambda d: d.__setitem__('total', d['total']+1),
            lambda d: d.__setitem__('order', 'different'),
        ]
        for mutation in mutations:
            record = copy.deepcopy(self.records['f3-classes']); mutation(record)
            with self.subTest(mutation=mutation):
                with self.assertRaises(ValueError): verify_shards([record], 'f3-classes')
        record = copy.deepcopy(self.records['f27-char3'])
        record['rows'][1]['matrix'] = record['rows'][0]['matrix']
        record['rows'][1]['cocycle'] = record['rows'][0]['cocycle']
        with self.assertRaises(ValueError): verify_shards([record], 'f27-char3')
        with self.assertRaises(ValueError): verify_shards([self.records['f3-classes']], 'f5-classes')

    def test_translation_involution_on_all_control_points(self):
        # Group-level equivalence only; this does not certify the Mobius/scalar map.
        for record in self.records.values():
            f = BasisField(record['field'])
            for entry in record['classes']:
                curve = Curve(f, entry['model'])
                def neg(p): return None if p is None else (p[0], f.sub(0, p[1]))
                for t in map(curve.read_point, entry['targets']):
                    for q in curve.points:
                        target = curve.add(t, curve.add(q, q))
                        for p in curve.points:
                            self.assertEqual(curve.add(curve.add(t, neg(p)), q), curve.add(target, neg(curve.add(p, q))))

    def test_cli_replay(self):
        path = Path(self.scratch.name)/'join.json'; path.write_text(json.dumps(self.records['f3-classes']))
        command = [sys.executable, str(Path(__file__).with_name('check_join_certificate.py')), str(path), '--fixture', 'f3-classes']
        good = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertTrue(json.loads(good.stdout)['valid'])
        self.assertEqual(subprocess.run(command[:-1]+['f5-classes'], capture_output=True).returncode, 2)


if __name__ == '__main__': unittest.main(verbosity=2)
