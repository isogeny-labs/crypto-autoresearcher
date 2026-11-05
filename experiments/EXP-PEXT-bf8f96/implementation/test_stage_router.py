"""Prospective router rejects changed six-run contracts and unbound sources."""

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from input_manifest import ROOT
from stage_router import SELF, STAGES, dispatch, validate_shape

sys.path.insert(0, str(ROOT / "tools"))
import experiment_execution


def plan():
    watchdogs = (7200, 3600, 21600, 28800, 21600, 3600)
    return {"experiment_id": "EXP-PEXT-bf8f96",
            "source_sha256": {SELF: hashlib.sha256((ROOT / SELF).read_bytes()).hexdigest()},
            "trials": [{"id": stage, "stage": stage, "run_id": f"RUN-fixture-{stage}",
                        "watchdog_seconds": seconds, "memory_mb": 4096}
                       for stage, seconds in zip(STAGES, watchdogs)]}


class StageRouterTests(unittest.TestCase):
    def test_exact_six_stage_shape_and_run_binding(self):
        value = plan()
        self.assertEqual(validate_shape(value, "n3core", "RUN-fixture-n3core")["id"],
                         "n3core")
        changed = plan(); changed["trials"][2]["watchdog_seconds"] += 1
        with self.assertRaisesRegex(ValueError, "finite watchdog"):
            validate_shape(changed, "n3core", "RUN-fixture-n3core")
        changed = plan(); changed["trials"][2]["id"] = "n3ext"
        with self.assertRaisesRegex(ValueError, "six-stage order"):
            validate_shape(changed, "n3core", "RUN-fixture-n3core")
        with self.assertRaisesRegex(ValueError, "run ID"):
            validate_shape(value, "n3core", "RUN-wrong")

    def test_authorized_plan_route_and_missing_source_refusal(self):
        value = plan()
        with tempfile.TemporaryDirectory() as scratch:
            with patch.object(experiment_execution, "load_plan", return_value=value), \
                 patch.object(experiment_execution, "sha256", side_effect=lambda path:
                              hashlib.sha256(Path(path).read_bytes()).hexdigest()), \
                 patch("stage_router.run_candidate", return_value={"stage": "n3core"}) as run:
                result = dispatch("run", "candidate-plan.json", scratch,
                                  "n3core", "RUN-fixture-n3core")
                self.assertEqual(result["result"], {"stage": "n3core"})
                run.assert_called_once()
                value["source_sha256"][SELF] = "0" * 64
                with self.assertRaisesRegex(ValueError, "source absent"):
                    dispatch("run", "candidate-plan.json", scratch,
                             "n3core", "RUN-fixture-n3core")
                self.assertEqual(run.call_count, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
