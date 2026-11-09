"""No scientific execution: exercise all five frozen-plan manifest branches.

Scientific commands are mocked. These checks establish envelope admission and
source bindings, not validity of pilot counts, census data, or analysis.
"""
import argparse
import ast
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PLAN_PATH = str((HERE.parent / "trial-plan.json").relative_to(ROOT))
PREDECESSOR = ROOT / "experiments/EXP-PFDR-7c7c95/implementation"
sys.path.insert(0, str(ROOT / "tools"))
import experiment_execution as supervisor
import experiment_protocol as protocol_tools

module_spec = importlib.util.spec_from_file_location("pfdr_fa915a_driver", HERE / "run.py")
driver = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(driver)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ProspectiveManifestAdmission(unittest.TestCase):
    def setUp(self):
        previous = Path.cwd()
        os.chdir(ROOT)
        self.addCleanup(os.chdir, previous)
        self.temp = tempfile.TemporaryDirectory(prefix="pfdr five stage envelope ")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        # Positive tests use the contract as written, without adding missing
        # bindings or removing contradictory fields in the fixture.
        self.plan = json.loads((ROOT / PLAN_PATH).read_text())

    def test_exact_plan_and_protocol_source_bindings(self):
        self.assertEqual(self.plan["experiment_id"], driver.EXP)
        self.assertEqual(self.plan["hypothesis_id"], driver.HYPOTHESIS_ID)
        self.assertEqual(self.plan["historical_attempts"], 3)
        self.assertEqual(self.plan["cumulative_maximum_runs"], 8)
        self.assertEqual(self.plan["maximum_runs"], 5)
        self.assertEqual(self.plan["maximum_retries"], 0)
        self.assertEqual([t["id"] for t in self.plan["trials"]],
                         ["pilot", "census-main", "analyze-main", "census-rep", "analyze-final"])
        # authorize() rehashes source_sha256 at every launch. Input metadata
        # alone would not enforce these immutable external dependencies.
        for path, expected in self.plan["input_sha256"].items():
            self.assertEqual(self.plan["source_sha256"].get(path), expected, path)
        for path, expected in self.plan["source_sha256"].items():
            with self.subTest(source=path):
                self.assertEqual(digest(ROOT / path), expected)
        specification_path = ROOT / self.plan["specification"]
        self.assertEqual(digest(specification_path), self.plan["specification_sha256"])
        specification = yaml.safe_load(specification_path.read_text())["experiment"]
        protocols = specification["execution_plan"]["protocol_hashes"]
        self.assertTrue(protocols)
        for path, expected in protocols.items():
            with self.subTest(protocol=path):
                protocol = json.loads((ROOT / path).read_text())
                # This specification field uses the canonical protocol digest
                # excluding freeze metadata, not the serialized file digest.
                self.assertEqual(protocol_tools.protocol_hash(protocol), expected)
                if protocol["freeze"]["status"] == "frozen":
                    self.assertEqual(protocol["freeze"]["protocol_sha256"], expected)
                self.assertTrue(protocol["arms"])
                for arm in protocol["arms"]:
                    self.assertEqual(arm["instrument"]["flags"]["run_py_sha256"],
                                     digest(HERE / "run.py"))
                    self.assertEqual(arm["instrument"]["flags"]["paircount_c_sha256"],
                                     digest(HERE / "paircount.c"))

    def test_generated_envelopes_for_all_five_stages(self):
        def pilot(args):
            out = Path(args.out)
            (out / "design.json").write_text(json.dumps({
                "cells": [{"status": "ok", "n_curves": 10}], "plants": []}))
            (out / "pilot-jobs.jsonl").write_text('{"fixture_only": true}\n')

        def census(args):
            (Path(args.out) / (args.block + "-jobs.jsonl")).write_text(
                '{"status": "ok", "fixture_only": true}\n')

        def analyze(args):
            Path(args.out).write_text(json.dumps({"reading": "TEST_ONLY", "alive_lines": [],
                "calibration": {}, "valid_lines": [], "controls": {}}))
            Path(args.out).with_name("flags.json").write_text('{"fixture_only": true}')

        seen = []
        for trial in self.plan["trials"]:
            with self.subTest(stage=trial["id"]):
                directory = self.directory / trial["id"]
                directory.mkdir()
                argv = [arg.replace("{run_dir}", str(directory)) for arg in trial["argv"]]
                check_argv = [arg.replace("{run_dir}", str(directory)) for arg in trial["check_argv"]]
                args = argparse.Namespace(plan=PLAN_PATH, run_dir=str(directory),
                                          run_id=trial["run_id"], trial_id=trial["id"])
                authority = {"commit": "1" * 40}
                (directory / "launch.json").write_text(json.dumps({
                    "run_id": trial["run_id"], "trial_id": trial["id"],
                    "plan_sha256": digest(ROOT / PLAN_PATH), "authority": authority}))
                (directory / "command.txt").write_text(json.dumps(argv))
                (directory / "environment.json").write_text(json.dumps({
                    "commit": authority["commit"], "source_sha256": self.plan["source_sha256"],
                    "specification_sha256": self.plan["specification_sha256"]}))
                for name in ("stdout.log", "stderr.log", "check.stdout.log", "check.stderr.log"):
                    (directory / name).touch()
                started = datetime.now(timezone.utc).isoformat()
                with patch.object(driver, "cmd_build") as build, \
                     patch.object(driver, "cmd_pilot", side_effect=pilot) as pilot_mock, \
                     patch.object(driver, "cmd_census", side_effect=census), \
                     patch.object(driver, "cmd_analyze", side_effect=analyze), \
                     patch.object(driver, "_git_commit", return_value=("2" * 40, False)), \
                     patch.object(sys, "argv", argv[1:]):
                    self.assertEqual(driver.cmd_trial(args), 0)
                    build.assert_called_once()
                    self.assertEqual(pilot_mock.call_count, int(trial["id"] == "pilot"))
                finished = datetime.now(timezone.utc).isoformat()
                for artifact in trial["artifacts"]:
                    self.assertTrue((directory / artifact).is_file(), artifact)
                supervisor.complete_manifest(directory, self.plan, PLAN_PATH,
                    digest(ROOT / PLAN_PATH), trial, authority, argv, check_argv, started, finished)
                manifest = yaml.safe_load((directory / "manifest.yaml").read_text())["run"]
                self.assertEqual(manifest["code"]["commit"], "1" * 40)
                self.assertEqual(manifest["code"]["observed_head_at_completion"], "2" * 40)
                self.assertEqual(manifest["inputs"]["plan_sha256"], digest(ROOT / PLAN_PATH))
                for key in ("seed", "curve_id", "parameters"):
                    self.assertNotIn(key, manifest["inputs"])
                self.assertEqual(supervisor.manifest_schema_errors(directory / "manifest.yaml"), [])
                seen.append(trial["id"])
        self.assertEqual(seen, ["pilot", "census-main", "analyze-main", "census-rep", "analyze-final"])

    def test_pilot_bad_bindings_refused_before_build(self):
        mutations = [("hypothesis_id", None), ("experiment_id", "EXP-PFDR-ffffff"),
                     ("source_sha256", {}), ("seed", None), ("curve_id", None),
                     ("parameters", {"unexpected": 1})]
        for field, value in mutations:
            with self.subTest(field=field):
                plan = copy.deepcopy(self.plan)
                trial = next(t for t in plan["trials"] if t["id"] == "pilot")
                (trial if field in ("seed", "curve_id", "parameters") else plan)[field] = value
                plan_path = self.directory / "negative plan.json"
                plan_path.write_text(json.dumps(plan))
                (self.directory / "launch.json").write_text(json.dumps({
                    "run_id": trial["run_id"], "trial_id": trial["id"],
                    "plan_sha256": digest(plan_path), "authority": {"commit": "1" * 40}}))
                args = argparse.Namespace(plan=str(plan_path), run_dir=str(self.directory),
                                          run_id=trial["run_id"], trial_id=trial["id"])
                with patch.object(driver, "cmd_build") as build:
                    with self.assertRaises(ValueError):
                        driver.cmd_trial(args)
                    build.assert_not_called()

    def test_scientific_kernel_and_seed_namespace_are_unchanged(self):
        def scientific_ast(path):
            nodes = ast.parse(path.read_text()).body
            return [ast.dump(node, include_attributes=False) for node in nodes
                    if isinstance(node, (ast.FunctionDef, ast.Assign, ast.AnnAssign))
                    and getattr(node, "name", None) != "cmd_trial"
                    and not (isinstance(node, ast.Assign)
                             and any(isinstance(t, ast.Name) and t.id == "EXP" for t in node.targets))]
        self.assertEqual(scientific_ast(PREDECESSOR / "run.py"), scientific_ast(HERE / "run.py"))
        self.assertEqual(driver.SEED_NAMESPACE, "EXP-PFDR-ada71b")
        for path in ("check.py", "paircount.c", "vendor/curve.py"):
            self.assertEqual(digest(PREDECESSOR / path), digest(HERE / path))


if __name__ == "__main__":
    unittest.main()
