"""Provenance regression checks; no scientific trials or kernel builds."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('pfdr_recovery', HERE / 'run_recovery_20261109.py')
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)


class ProvenanceRecovery(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.plan = self.root / 'plan.json'
        self.plan.write_text(json.dumps({'task_id': 'test', 'trials': [
            {'id': 'selftest', 'run_id': 'test-run', 'stage': 'selftest', 'artifacts': ['manifest.yaml', 'raw-result.json']}]}))
        self.args = argparse.Namespace(plan=str(self.plan), run_dir=str(self.root),
                                       run_id='test-run', trial_id='selftest')
        self.launch = {'run_id': 'test-run', 'trial_id': 'selftest',
                       'plan_sha256': hashlib.sha256(self.plan.read_bytes()).hexdigest(),
                       'authority': {'commit': '1' * 40}}
        self.write_launch()

    def write_launch(self):
        (self.root / 'launch.json').write_text(json.dumps(self.launch))

    def test_archive_commit_does_not_replace_launch_identity(self):
        with patch.object(driver, 'cmd_build'), patch.object(driver, 'cmd_selftest'), \
             patch.object(driver, '_git_commit', return_value=('2' * 40, False)):
            self.assertEqual(driver.cmd_trial(self.args), 0)
        code = yaml.safe_load((self.root / 'manifest.yaml').read_text())['run']['code']
        self.assertEqual(code['commit'], '1' * 40)
        self.assertEqual(code['observed_head_at_completion'], '2' * 40)

    def test_mismatched_launch_fails_before_build(self):
        for field in ('run_id', 'trial_id', 'plan_sha256'):
            with self.subTest(field=field):
                original = self.launch[field]
                self.launch[field] = 'wrong'
                self.write_launch()
                with patch.object(driver, 'cmd_build') as build:
                    with self.assertRaises(ValueError):
                        driver.cmd_trial(self.args)
                    build.assert_not_called()
                self.launch[field] = original

    def test_missing_or_invalid_authority_fails_closed(self):
        for authority in (None, {}, {'commit': 'short'}, {'commit': 1}):
            with self.subTest(authority=authority):
                self.launch['authority'] = authority
                self.write_launch()
                with self.assertRaises(ValueError):
                    driver._launch_commit(self.args)

    def test_missing_launch_does_not_fall_back_to_head(self):
        (self.root / 'launch.json').unlink()
        with self.assertRaises(FileNotFoundError):
            driver._launch_commit(self.args)


if __name__ == '__main__':
    unittest.main()
