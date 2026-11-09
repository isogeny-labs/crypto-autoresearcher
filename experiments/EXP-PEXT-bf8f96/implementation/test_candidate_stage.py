"""Six-stage candidate archive and budget shape controls; no trial launch."""

from copy import deepcopy
import json
import unittest

from candidate_stage import (COHORTS, COMPONENT_SOURCES, STAGE_ORDER,
                             WATCHDOGS, expected_artifacts, join_path,
                             validate_shape)


def fixture_plan(stage):
    trials = []
    for name in STAGE_ORDER:
        row = {"id": name, "stage": name, "watchdog_seconds": WATCHDOGS[name]}
        if name == stage:
            row["artifacts"] = expected_artifacts(stage) + ["manifest.yaml", "raw-result.json"]
            row["memory_mb"] = 4096
            row["candidate_driver_wall_seconds"] = 1000
            row["candidate_checker_reserve_seconds"] = 1000
            row["candidate_config"] = {}
            for cohort in COHORTS[stage]:
                published = json.loads(join_path(cohort).read_bytes())
                field = published["field"]
                structures = published["structures_per_T"]
                row["candidate_config"][cohort] = {
                    "caps": {"field_elements": field["prime"]**field["degree"],
                             "structures": structures, "image_entries": 4*structures,
                             "rational_candidates": 5_000_000,
                             "nonrational_maps": 5_000_000,
                             "total_candidates": structures},
                    "memory_bytes": 2*1024**3, "cpu_seconds": 300,
                    "unit_wall_seconds": 300}
        trials.append(row)
    return {"experiment_id": "EXP-PEXT-bf8f96", "trials": trials,
            "source_sha256": {name: "0"*64 for name in COMPONENT_SOURCES}}


class CandidateStageShapeTests(unittest.TestCase):
    def test_exact_archive_names_and_six_stage_shape(self):
        self.assertEqual(sum(WATCHDOGS.values()), 86400)
        self.assertEqual({stage: len(expected_artifacts(stage)) for stage in COHORTS},
                         {"n3core": 258, "n3ext": 679, "n5": 133})
        for stage in COHORTS:
            names = expected_artifacts(stage)
            for cohort in COHORTS[stage]:
                self.assertIn(f"cohorts/{cohort}/worker-exit.json", names)
                self.assertIn(f"cohorts/{cohort}/worker.stderr.log", names)
            self.assertEqual(len(names), len(set(names)))
            self.assertFalse(any("q13" in name for name in names))
            self.assertEqual(validate_shape(fixture_plan(stage), stage)["id"], stage)

    def test_missing_artifact_source_and_budget_refused(self):
        stage = "n3core"
        original = fixture_plan(stage)
        trial = original["trials"][2]
        altered = deepcopy(original)
        altered["trials"][2]["artifacts"].remove("cohorts/q7-n3/units-index.json")
        with self.assertRaisesRegex(ValueError, "artifacts absent"):
            validate_shape(altered, stage)
        altered = deepcopy(original)
        altered["source_sha256"].pop(next(iter(COMPONENT_SOURCES)))
        with self.assertRaisesRegex(ValueError, "source closure absent"):
            validate_shape(altered, stage)
        altered = deepcopy(original)
        altered["trials"][2]["candidate_checker_reserve_seconds"] = WATCHDOGS[stage]
        with self.assertRaisesRegex(ValueError, "budget missing or exceeds"):
            validate_shape(altered, stage)
        altered = deepcopy(original)
        altered["trials"][2]["candidate_config"]["q7-n3"]["caps"]["structures"] += 1
        with self.assertRaisesRegex(ValueError, "caps differ"):
            validate_shape(altered, stage)
        altered = deepcopy(original)
        altered["trials"][4]["watchdog_seconds"] += 1
        with self.assertRaisesRegex(ValueError, "six-stage budget"):
            validate_shape(altered, stage)


if __name__ == "__main__":
    unittest.main(verbosity=2)
