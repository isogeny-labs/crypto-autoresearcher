#!/usr/bin/env python3
"""Receipt and control-stop checks for the unlaunched retained W3 panel."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SOURCE = Path(__file__).with_name('run_retained_m2_w3_panel.py')
SPEC = importlib.util.spec_from_file_location('w3_panel_runner', SOURCE)
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class PanelRunnerChecks(unittest.TestCase):
    def attempt(self, bad_control, bad_digest=False):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source_plan = directory / 'source-plan.json'
            source_plan.write_text('{}\n')
            source_sha = RUNNER.sha(source_plan)
            fake = directory / 'fake-verifier.py'
            fake.write_text(
                'import argparse,json\n'
                'p=argparse.ArgumentParser()\n'
                'p.add_argument("--plan")\n'
                'p.add_argument("--item-id")\n'
                'a=p.parse_args()\n'
                'r=(8129 if ' + repr(bad_control) + ' else 8130) '
                'if a.item_id=="control" else 6175\n'
                'q=20876-r\n'
                'expected=12746 if a.item_id=="control" else 14701\n'
                'print(json.dumps(dict(item_id=a.item_id,plan_sha256=' +
                repr(source_sha) + ',equation_masks_sha256='
                '("b"*64 if a.item_id=="new" and ' + repr(bad_digest) +
                ' else "a"*64),'
                'expected_seed_codimension=expected,named_input='
                '("fresh-n50-poly-03" if a.item_id=="control" else '
                '"fresh-n50-rand-00"),columns=20876,rank=r,'
                'quotient_dimension=q,contains_one=False,'
                'quotient_matches_seed=(q==expected))))\n')
            plan_path = directory / 'plan.json'
            protocol_path = directory / 'protocol.json'
            ops_path = directory / 'ops.json'
            for path in (plan_path, protocol_path, ops_path):
                path.write_text('{}\n')
            lock = directory / 'lock'
            lock.touch()
            root = directory / 'output'
            plan = {'execution_order': ['control', 'new'],
                    'controls': ['control'],
                    'verifier_sha256': RUNNER.sha(fake),
                    'source_plan_sha256': source_sha,
                    'limits': {'total_wall_seconds': 600,
                               'per_item_wall_seconds': 60,
                               'per_item_cpu_seconds': 60,
                               'per_item_address_space_bytes': 4294967296}}
            ops = {'locks': [str(lock)], 'monthly_cap_usd': '1400'}
            by_id = {'control': {'record': {'name': 'fresh-n50-poly-03', 'k': 25},
                                 'seed_codimension': 12746},
                     'new': {'record': {'name': 'fresh-n50-rand-00', 'k': 25},
                             'seed_codimension': 14701}}
            admission = {'checked_utc': '2026-11-11T00:00:00+00:00'}
            fixed = (plan, ops, source_plan, fake, by_id,
                     {'control': 'a' * 64, 'new': 'a' * 64}, root,
                     RUNNER.dt.datetime.now(RUNNER.dt.timezone.utc) +
                     RUNNER.dt.timedelta(minutes=15), admission)
            with mock.patch.object(RUNNER, 'check_admission', return_value=fixed), \
                    mock.patch.object(RUNNER, 'budget_readback', return_value={}), \
                    mock.patch.object(RUNNER, 'available_memory', return_value=8 << 30):
                code = RUNNER.run(plan_path, protocol_path, ops_path, True)
            result = json.loads((root / 'result.json').read_text())
            return code, result, root.joinpath('item-00.finished.json').read_bytes()

    def test_success_keeps_both_exact_rows(self):
        code, result, first_receipt = self.attempt(False)
        self.assertEqual(code, 0)
        self.assertTrue(result['controls_ok'])
        self.assertEqual([row['status'] for row in result['rows']],
                         ['exact_seed_verified', 'exact_seed_verified'])
        self.assertIn(b'"started_sha256"', first_receipt)

    def test_bad_control_preserves_failure_and_stops_new_item(self):
        code, result, _ = self.attempt(True)
        self.assertEqual(code, 1)
        self.assertFalse(result['controls_ok'])
        self.assertEqual([row['status'] for row in result['rows']],
                         ['seed_dimension_mismatch', 'unrun'])

    def test_changed_equation_digest_is_not_accepted(self):
        code, result, _ = self.attempt(False, bad_digest=True)
        self.assertEqual(code, 1)
        self.assertTrue(result['controls_ok'])
        self.assertEqual([row['status'] for row in result['rows']],
                         ['exact_seed_verified', 'mismatch'])


if __name__ == '__main__':
    unittest.main()
