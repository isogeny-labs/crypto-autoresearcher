"""Zero-science candidate tests through the real supervisor completion gate."""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import experiment_execution as supervisor
spec = importlib.util.spec_from_file_location('pfdr_manifest_candidate', HERE / 'run_manifest_v3.py')
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GeneratedManifestAdmission(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='pfdr envelope test ')
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        self.plan = json.loads((HERE.parent / 'trial-plan.json').read_text())
        self.plan['hypothesis_id'] = driver.HYPOTHESIS_ID
        self.source_path = str((HERE / 'run_manifest_v3.py').relative_to(ROOT))
        self.plan['source_sha256'][self.source_path] = digest(HERE / 'run_manifest_v3.py')
        self.plan['trials'] = [t for t in self.plan['trials'] if t['id'] != 'pilot']
        self.plan_path = self.directory / 'prospective plan.json'

    def prepare(self, trial):
        self.plan_path.write_text(json.dumps(self.plan))
        self.args = argparse.Namespace(plan=str(self.plan_path), run_dir=str(self.directory),
                                       run_id=trial['run_id'], trial_id=trial['id'])
        launch = {'run_id': trial['run_id'], 'trial_id': trial['id'],
                  'plan_sha256': digest(self.plan_path), 'authority': {'commit': '1' * 40}}
        (self.directory / 'launch.json').write_text(json.dumps(launch))
        return launch

    def test_generated_envelopes_for_all_four_stages(self):
        def census(args):
            (Path(args.out) / (args.block + '-jobs.jsonl')).write_text('')

        def analyze(args):
            Path(args.out).write_text(json.dumps({'reading': 'TEST_ONLY', 'alive_lines': [],
                'calibration': {}, 'valid_lines': [], 'controls': {}}))

        for trial in self.plan['trials']:
            with self.subTest(stage=trial['id']):
                launch = self.prepare(trial)
                argv = ['python3', self.source_path, 'trial', '--run-dir', self.args.run_dir,
                        '--run-id', self.args.run_id, '--trial-id', self.args.trial_id,
                        '--plan', self.args.plan]
                (self.directory / 'command.txt').write_text(json.dumps(argv))
                (self.directory / 'environment.json').write_text(json.dumps({
                    'commit': '1' * 40, 'source_sha256': self.plan['source_sha256']}))
                for name in ('stdout.log', 'stderr.log', 'check.stdout.log', 'check.stderr.log'):
                    (self.directory / name).touch()
                started = datetime.now(timezone.utc).isoformat()
                with patch.object(driver, 'cmd_build'), patch.object(driver, 'cmd_census', census), \
                     patch.object(driver, 'cmd_analyze', analyze), \
                     patch.object(driver, '_git_commit', return_value=('2' * 40, False)), \
                     patch.object(sys, 'argv', argv[1:]):
                    self.assertEqual(driver.cmd_trial(self.args), 0)
                finished = datetime.now(timezone.utc).isoformat()
                supervisor.complete_manifest(self.directory, self.plan, str(self.plan_path),
                    digest(self.plan_path), trial, launch['authority'], argv, ['checker'], started, finished)
                manifest = yaml.safe_load((self.directory / 'manifest.yaml').read_text())['run']
                self.assertEqual(manifest['code']['commit'], '1' * 40)
                self.assertEqual(manifest['code']['observed_head_at_completion'], '2' * 40)
                self.assertEqual(manifest['inputs']['plan_sha256'], digest(self.plan_path))
                for key in ('seed', 'curve_id', 'parameters'):
                    self.assertNotIn(key, manifest['inputs'])
                self.assertEqual(supervisor.manifest_schema_errors(self.directory / 'manifest.yaml'), [])

    def test_scientific_functions_and_constants_are_unchanged(self):
        def scientific_ast(path):
            nodes = ast.parse(path.read_text()).body
            return [ast.dump(node, include_attributes=False) for node in nodes
                    if isinstance(node, (ast.FunctionDef, ast.Assign, ast.AnnAssign))
                    and getattr(node, 'name', None) != 'cmd_trial']
        self.assertEqual(scientific_ast(HERE / 'run.py'),
                         scientific_ast(HERE / 'run_manifest_v3.py'))

    def test_bad_bindings_refused_before_build(self):
        for field in ('hypothesis_id', 'experiment_id', 'source_sha256'):
            with self.subTest(field=field):
                original = self.plan.pop(field)
                self.prepare(self.plan['trials'][0])
                with patch.object(driver, 'cmd_build') as build:
                    with self.assertRaises(ValueError):
                        driver.cmd_trial(self.args)
                    build.assert_not_called()
                self.plan[field] = original

    def test_unsupported_trial_inputs_refused_before_build(self):
        trial = self.plan['trials'][0]
        for key in ('seed', 'curve_id', 'parameters'):
            with self.subTest(field=key):
                trial[key] = None
                self.prepare(trial)
                with patch.object(driver, 'cmd_build') as build:
                    with self.assertRaises(ValueError):
                        driver.cmd_trial(self.args)
                    build.assert_not_called()
                del trial[key]


if __name__ == '__main__':
    unittest.main()
