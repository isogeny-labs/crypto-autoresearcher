#!/usr/bin/env python3
"""Synthetic complete-run and adversarial custody checks for the x1 replay."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from verify_n47_x1_count_run import verify


REPOSITORY = Path(__file__).resolve().parents[2]
PLAN = REPOSITORY / 'analysis/semaev-degree-five-quotient-lift/n47-rand00-x1-count-plan-001.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


class CountReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.plan = json.loads(PLAN.read_text())
        self.plan['output_root'] = str(self.root)
        self.plan['original_input_system_path'] = str(self.root / 'input.sys')
        (self.root / 'input.sys').write_bytes(b'synthetic original system')
        self.plan['input_sys_sha256'] = digest(b'synthetic original system')
        binary = str(self.root / 'count_x1')
        (self.root / 'count_x1').write_bytes(b'synthetic binary')
        self.plan['build_argv'][-1] = binary
        self.plan['build_launch_argv'][-1] = binary
        for control in self.plan['controls']:
            control['argv'][0] = binary
            control['launch_argv'][5] = binary
        self.plan['target_argv'][0] = binary
        self.plan['target_launch_argv'][5] = binary
        self.plan_path = self.root / 'plan.json'
        self.plan_path.write_text(json.dumps(self.plan))
        self.receipt = {
            'schema': 'semaev.n47-rand00-x1-count-run/v1',
            'plan_sha256': digest(self.plan_path.read_bytes()),
            'source_sha256': self.plan['source_sha256'],
            'binary_sha256': digest(b'synthetic binary'),
            'attempts': 1, 'retries': 0,
            'build': self.stage('build', self.plan['build_launch_argv'], b''),
            'controls': [],
        }
        for control in self.plan['controls']:
            stage = self.stage(control['id'], control['launch_argv'],
                               ('%d\n' % control['expected_exact_count']).encode())
            stage['id'] = control['id']
            self.receipt['controls'].append(stage)
        self.receipt['target'] = self.stage('target', self.plan['target_launch_argv'], b'0\n')
        self.receipt_path = self.root / 'receipt.json'
        self.write_receipt()

    def stage(self, name, argv, stdout):
        (self.root / (name + '.out')).write_bytes(stdout)
        (self.root / (name + '.err')).write_bytes(b'')
        return {'argv': argv, 'exit_code': 0,
                'stdout_path': name + '.out', 'stdout_sha256': digest(stdout),
                'stderr_path': name + '.err', 'stderr_sha256': digest(b'')}

    def write_receipt(self):
        self.receipt_path.write_text(json.dumps(self.receipt))

    def check(self):
        return verify(self.plan_path, self.receipt_path, REPOSITORY, self.root)

    def test_complete_receipt_is_accepted(self):
        self.assertEqual(self.check()['status'], 'accepted_zero_count')

    def test_changed_target_count_is_rejected_even_with_new_hash(self):
        (self.root / 'target.out').write_bytes(b'1\n')
        self.receipt['target']['stdout_sha256'] = digest(b'1\n')
        self.write_receipt()
        with self.assertRaisesRegex(ValueError, 'stage stdout mismatch'):
            self.check()

    def test_changed_command_is_rejected(self):
        self.receipt['target']['argv'][-1] = '0'
        self.write_receipt()
        with self.assertRaisesRegex(ValueError, 'stage argv mismatch'):
            self.check()

    def test_missing_control_is_rejected(self):
        self.receipt['controls'].pop()
        self.write_receipt()
        with self.assertRaisesRegex(ValueError, 'control count mismatch'):
            self.check()


if __name__ == '__main__':
    unittest.main()
