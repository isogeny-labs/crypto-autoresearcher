#!/usr/bin/env python3
"""Admission and checker-output controls for the sliced D4 stage runner."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import hashlib

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_n51_poly00_sliced_d4 import (admission, command, validate_output,
                                      verify_prior_publication)


class SlicedD4RunnerTests(unittest.TestCase):
    def test_pending_authorization_refuses_before_output(self):
        with self.assertRaisesRegex(RuntimeError, 'authorization'):
            admission({}, {'authorization_status': 'pending',
                           'authorization_note': None,
                           'external_jobs_reconciliation': None}, 'published', 'project')

    def test_projection_command_has_exact_limits_and_no_placeholders(self):
        plan = json.loads((Path(__file__).resolve().parent /
                           'n51-poly00-sliced-d4-plan-001.json').read_text())
        argv = command(plan, 'project')
        self.assertEqual(argv[:5], ['/usr/bin/prlimit', '--as=4294967296', '--',
                                    '/usr/bin/timeout', '900'])
        self.assertIn(plan['input_map'], argv)
        self.assertIn(plan['projected_output'], argv)
        self.assertFalse(any(word.startswith('<') for word in argv))

    def test_independent_checker_status_is_required(self):
        plan = {'rebased_output': '/unused/rebased.bin'}
        accepted = {'status': 'valid_affine_slice_nonmembership', 'variables': 51,
                    'degree': 4, 'codimension_lower_bound': 45615,
                    'certificate_sha256': 'a' * 64}
        with patch('run_n51_poly00_sliced_d4.sha', return_value='a' * 64):
            self.assertEqual(validate_output(plan, 'check', json.dumps(accepted)), accepted)
            rejected = dict(accepted, status='invalid')
            with self.assertRaisesRegex(ValueError, 'did not accept'):
                validate_output(plan, 'check', json.dumps(rejected))

    def test_next_stage_requires_published_unchanged_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / 'run'
            output.mkdir()
            published = root / 'repo' / 'stage.json'
            published.parent.mkdir()
            project_file = output / 'projected.bin'
            project_file.write_bytes(b'projected')
            admission_file = output / 'project.admission.json'
            started_file = output / 'project.started.json'
            stdout_file = output / 'project.stdout.txt'
            stderr_file = output / 'project.stderr.txt'
            for path in (admission_file, started_file, stdout_file, stderr_file):
                path.write_bytes(path.name.encode())
            digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
            receipt = {'status': 'accepted_stage',
                       'admission_sha256': digest(admission_file),
                       'started_sha256': digest(started_file),
                       'stdout_sha256': digest(stdout_file),
                       'output_sha256': digest(project_file),
                       'finished': {'stderr_sha256': digest(stderr_file)}}
            receipt_path = output / 'project.receipt.json'
            receipt_path.write_text(json.dumps(receipt))
            published.write_bytes(receipt_path.read_bytes())
            plan = {'output_root': str(output), 'projected_output': str(project_file),
                    'rebased_output': str(output / 'rebased.bin'),
                    'checker_receipt': str(output / 'checker.json'),
                    'profile_output': str(output / 'profile.json'),
                    'stage_publications': {'project': 'stage.json'}}
            with patch('run_n51_poly00_sliced_d4.REPO', published.parent), \
                 patch('run_n51_poly00_sliced_d4.committed'):
                self.assertEqual(verify_prior_publication(plan, 'rebase'), receipt)
                stdout_file.write_bytes(b'tampered')
                with self.assertRaisesRegex(RuntimeError, 'transcript changed'):
                    verify_prior_publication(plan, 'rebase')


if __name__ == '__main__':
    unittest.main()
