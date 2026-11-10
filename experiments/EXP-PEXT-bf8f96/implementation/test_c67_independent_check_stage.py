"""Fixed placeholder checks for the future sealed C6/C7 replay stage."""

import ast
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import c67_independent_check_stage as stage
import c67_run_custody as custody
from test_c67_run_custody import fixture_admission, fixture_results

sys.path.insert(0, str(custody.ROOT / "tools"))
import experiment_execution


class BinderFixture:
    def __init__(self, cohort, plan_path):
        self.plan_sha256 = next(row["join_plan_sha256"] for row in
                                fixture_admission()["records"] if row["cohort"] == cohort)
        self.plan = {"field": {"fixed": "software-fixture"}}


class C67IndependentStageTests(unittest.TestCase):
    def test_required_source_set_covers_local_static_import_closure(self):
        directory = stage.ROOT / stage.PREFIX / "implementation"
        pending = ["c67_independent_check_stage", "c67_run_custody",
                   "c67_control_schedule", "c6_coordinate_control",
                   "c7_seed_replay", "c7_matched_random"]
        found = set()
        while pending:
            module = pending.pop()
            if module in found:
                continue
            source = directory / (module + ".py")
            self.assertTrue(source.is_file())
            found.add(module)
            for node in ast.walk(ast.parse(source.read_text())):
                if isinstance(node, ast.Import):
                    names = [alias.name.split(".")[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module.split(".")[0]]
                else:
                    continue
                pending.extend(name for name in names
                               if (directory / (name + ".py")).is_file()
                               and name not in found)
        self.assertEqual(set(stage.SOURCES),
                         {stage.PREFIX + "implementation/" + name + ".py"
                          for name in found})

    def _sealed_fixture(self, root):
        admission = fixture_admission()
        fixture_results(root, admission)
        custody_summary = custody.compare_results(root, admission)
        (root / custody.READBACK).write_bytes(custody.canonical(custody_summary))
        c6 = json.loads((root / admission["records"][0]["path"]).read_bytes())["payload"]
        return admission, c6

    def test_replays_every_sealed_batch_and_preserves_scope(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            admission, c6 = self._sealed_fixture(root)
            with patch.object(stage, "CandidateBinder", side_effect=BinderFixture), \
                 patch.object(stage, "check_all_slots", return_value=c6) as c6_check, \
                 patch.object(stage, "replay_c7", return_value={"valid": True,
                                                                  "selected": 16,
                                                                  "attempted": 16}) as c7_check:
                result = stage.recompute(root, admission)
            self.assertEqual(result["status"], "checked_all_controls")
            self.assertEqual(len(result["records"]), 3)
            self.assertEqual(c6_check.call_count, 1)
            self.assertEqual(c7_check.call_count, 2)
            self.assertEqual(result["coverage_complete"], True)

    def test_changed_c6_and_failed_c7_replay_refused(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            admission, c6 = self._sealed_fixture(root)
            with patch.object(stage, "CandidateBinder", side_effect=BinderFixture), \
                 patch.object(stage, "check_all_slots", return_value={**c6, "slot_count": 15}):
                with self.assertRaisesRegex(ValueError, "C6 retained control differs"):
                    stage.recompute(root, admission)
            with patch.object(stage, "CandidateBinder", side_effect=BinderFixture), \
                 patch.object(stage, "check_all_slots", return_value=c6), \
                 patch.object(stage, "replay_c7", side_effect=ValueError("seed mismatch")):
                with self.assertRaisesRegex(ValueError, "seed mismatch"):
                    stage.recompute(root, admission)
            (root / custody.READBACK).unlink()
            with self.assertRaisesRegex(ValueError, "missing or symlinked"):
                stage.recompute(root, admission)

    def test_future_plan_requires_exact_replay_source_closure(self):
        hashes = {relative: custody.digest(custody._regular(stage.ROOT / relative))
                  for relative in stage.SOURCES}
        self.assertEqual(stage.checked_sources(hashes), hashes)
        changed = dict(hashes)
        changed[stage.SOURCES[0]] = "0" * 64
        with self.assertRaisesRegex(ValueError, "source hash mismatch"):
            stage.checked_sources(changed)
        with self.assertRaisesRegex(ValueError, "source closure absent"):
            stage.checked_sources({})

    def test_approved_plan_artifact_gate_and_write_once_summary(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            admission = fixture_admission()
            plan = {"trials": [{"id": "n3ext", "artifacts": [stage.CHECK]}],
                    "source_sha256": {relative: custody.digest(custody._regular(stage.ROOT / relative))
                                      for relative in stage.SOURCES}}
            result = {"schema": "fixed-check-fixture", "coverage_complete": True}
            with patch.object(custody, "_preflight", return_value=(root, admission)), \
                 patch.object(experiment_execution, "load_plan", return_value=plan), \
                 patch.object(stage, "recompute", return_value=result):
                self.assertEqual(stage.check("fixture-plan", root, "n3ext")["schema"],
                                 "fixed-check-fixture")
                self.assertEqual(stage.check("fixture-plan", root, "n3ext")["schema"],
                                 "fixed-check-fixture")
                (root / stage.CHECK).write_text("changed")
                with self.assertRaisesRegex(ValueError, "differs from retained"):
                    stage.check("fixture-plan", root, "n3ext")
                plan["trials"][0]["artifacts"] = []
                with self.assertRaisesRegex(ValueError, "absent from approved"):
                    stage.check("fixture-plan", root, "n3ext")


if __name__ == "__main__":
    unittest.main(verbosity=2)
