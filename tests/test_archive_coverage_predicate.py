"""Readiness, admission and preapproval share ONE archive-coverage predicate.

Regression for problems/ready-plans-lack-supervisor-archive-coverage.md
(17 of 18 selector-`ready` plans refused by authorize()) and
problems/experiment-preapproval-readiness-cycle.md: a plan whose executor
task omits a supervisor file must be refused by authorize(), reported
`needs_archive_coverage` by the selector and `approvable: false` by the
probe, all with the same gap strings from
experiment_execution.archive_coverage_gaps. Runs under plain unittest.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import types
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:  # the shared fixture module is written for pytest; only its builder is used
    import pytest  # noqa: F401
except ImportError:
    stub = types.ModuleType("pytest")
    stub.mark = types.SimpleNamespace(parametrize=lambda *a, **k: (lambda f: f))
    stub.raises = None
    sys.modules["pytest"] = stub

from tests.test_experiment_preapproval import fixture  # noqa: E402
from tools import experiment_execution as execution  # noqa: E402
from tools import experiment_preapproval as probe  # noqa: E402
from tools import newest_experiments as selector  # noqa: E402


def _write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


class SharedArchiveCoveragePredicate(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="archive-coverage-")).resolve()
        self.addCleanup(shutil.rmtree, self.root, True)
        self.packet, self.files = fixture(self.root)
        self.exp = self.packet["experiment_id"]
        trial = self.files["trial"]
        self.launch = f"experiments/{self.exp}/runs/{trial['run_id']}/launch.json"

    def _drop(self, suffix: str) -> None:
        queue = json.loads(self.files["queue"].read_text())
        paths = queue["tasks"][0]["artifact_paths"]
        paths.remove(next(p for p in paths if p.endswith(suffix)))
        _write(self.files["queue"], queue)

    def _materialize(self) -> None:
        for key in ("specification", "trial_plan", "queue", "handoff"):
            target = self.root / self.packet[key]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(Path(self.packet["preview"][key]).read_bytes())

    def _authorize(self):
        """authorize() with every gate BEFORE archive coverage satisfied by stubs.

        The dispatcher output carries the queued executor task unchanged, so
        artifact_paths reach the coverage loop exactly as written.
        """
        plan_path = self.root / self.packet["trial_plan"]
        task = dict(json.loads(self.files["queue"].read_text())["tasks"][0])
        task.update({"state": "running", "claim": {
            "status": "live", "owner": "fixture-owner", "epoch": 1,
            "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()}})
        dispatch = {"schema": "crypto.autoresearch.dispatch_plan.v1", "gates": {"all": True},
                    "plan_sha256": "0" * 64, "dispatches": [task]}

        def fake_run(argv, **kwargs):
            _write(Path(argv[argv.index("--output") + 1]), dispatch)
            return types.SimpleNamespace(returncode=0, stdout="", stderr="")

        with mock.patch.object(execution, "committed_queue"), \
                mock.patch.object(execution, "committed"), \
                mock.patch.object(execution, "load_plan"), \
                mock.patch.object(execution, "git", return_value="f" * 40), \
                mock.patch.object(execution.subprocess, "run", side_effect=fake_run):
            return execution.authorize(self.root, plan_path, self.files["plan"], "fixture-owner", 1)

    def test_missing_supervisor_file_is_refused_identically_by_all_three(self):
        self._drop("launch.json")
        result = probe.assess(self.root, self.packet)
        self.assertFalse(result["approvable"])
        self.assertEqual(result["archive_coverage_gaps"], [self.launch])
        self.assertTrue(any("executor archive coverage missing" in b for b in result["blockers"]))

        self._materialize()
        progress = selector.execution_progress(self.root / "experiments" / self.exp, self.root)
        self.assertEqual(progress["execution_state"], "needs_archive_coverage")
        self.assertNotEqual(progress["execution_state"], "ready")
        self.assertEqual(progress["archive_coverage_gaps"], [self.launch])
        rows = selector.newest_runnable(self.root, off_main={})
        self.assertEqual([(r["id"], r["execution_state"]) for r in rows],
                         [(self.exp, "needs_archive_coverage")])

        with self.assertRaises(execution.ExecutionError) as refused:
            self._authorize()
        self.assertEqual(str(refused.exception), f"handoff archive coverage missing: {self.launch}")

    def test_missing_trial_artifacts_report_every_gap_in_plan_order(self):
        self._drop("launch.json")
        self._drop("calls.tar.gz")
        expected = [self.launch, self.launch.replace("launch.json", "calls.tar.gz")]
        self.assertEqual(probe.assess(self.root, self.packet)["archive_coverage_gaps"], expected)
        self._materialize()
        progress = selector.execution_progress(self.root / "experiments" / self.exp, self.root)
        self.assertEqual(progress["archive_coverage_gaps"], expected)
        plan = json.loads((self.root / self.packet["trial_plan"]).read_text())
        task = json.loads(self.files["queue"].read_text())["tasks"][0]
        self.assertEqual(execution.archive_coverage_gaps(self.root, plan, task), expected)
        with self.assertRaises(execution.ExecutionError) as refused:
            self._authorize()
        self.assertEqual(str(refused.exception), f"handoff archive coverage missing: {expected[0]}")

    def test_complete_plan_is_approvable_ready_and_admitted(self):
        result = probe.assess(self.root, self.packet)
        self.assertTrue(result["approvable"], result["blockers"])
        self.assertEqual(result["archive_coverage_gaps"], [])
        self._materialize()
        progress = selector.execution_progress(self.root / "experiments" / self.exp, self.root)
        self.assertEqual(progress["execution_state"], "ready")
        receipt = self._authorize()
        self.assertEqual(set(receipt), {"owner", "epoch", "expires_at", "dispatch_plan_sha256", "commit"})
        self.assertEqual((receipt["owner"], receipt["epoch"]), ("fixture-owner", 1))

    def test_required_paths_are_generated_files_then_trial_artifacts(self):
        plan = self.files["plan"]
        trial = self.files["trial"]
        base = f"experiments/{self.exp}/runs/{trial['run_id']}"
        self.assertEqual(execution.required_archive_paths(self.root, plan),
                         [f"{base}/{n}" for n in (*execution.GENERATED, *trial["artifacts"])])
        self.assertEqual(execution.archive_coverage_gaps(self.root, plan, None),
                         execution.required_archive_paths(self.root, plan))


if __name__ == "__main__":
    unittest.main()
