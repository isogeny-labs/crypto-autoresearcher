"""Write-once and exact readback for incomplete C5 analyze artifacts."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from c5_preview_stage import (COHORTS, METADATA, ROSTERS, SUMMARY,
                              compare_preview, plans_from_campaign,
                              write_preview)
from candidate_stage import join_path


class C5PreviewStageTests(unittest.TestCase):
    def fixture(self):
        plans, curves = {}, []
        for cohort in COHORTS:
            published = json.loads(join_path(cohort).read_bytes())
            model = published["classes"][0]["model"]
            plans[cohort] = {"schema": "pext.join-plan/v1", "cohort": cohort,
                             "field": published["field"], "structures_per_T": 9,
                             "classes": [{"model": model, "targets": [None]}]}
            unit = {"T_index": 0, "unit_name": "u000000", "structures": 9,
                    "candidate_unit_sha256": "a"*64,
                    "type2_hyperelliptic_ordinals": [],
                    "branch_type_mismatch_count": 0,
                    "geometric_spectrum_violation_count": 0}
            if published["field"]["degree"] == 3:
                unit.update(type2_check_sha256="b"*64,
                            hyperelliptic_predicate_true_count=0)
            curves.append({"cohort": cohort, "class_index": 0,
                           "model": model, "T_count": 1, "units": [unit]})
        return plans, curves

    def test_write_once_and_exact_readback(self):
        plans, curves = self.fixture()
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            result = write_preview(root, curves, plans, "c"*64,
                                   {"n3core": "RUN-fixture"})
            self.assertEqual(result["unit_count"], 4)
            self.assertEqual(result["selected_preview_count"], 4)
            self.assertEqual(len((root / METADATA).read_bytes().splitlines()), 4)
            self.assertEqual(len((root / ROSTERS).read_bytes().splitlines()), 4)
            self.assertTrue(compare_preview(root, curves, plans, "c"*64,
                                            {"n3core": "RUN-fixture"})["valid"])
            with self.assertRaises(FileExistsError):
                write_preview(root, curves, plans, "c"*64, {})
            (root / ROSTERS).write_text("{}\n")
            with self.assertRaisesRegex(ValueError, ROSTERS):
                compare_preview(root, curves, plans, "c"*64,
                                {"n3core": "RUN-fixture"})
            (root / ROSTERS).unlink()
            (root / ROSTERS).symlink_to(root / SUMMARY)
            with self.assertRaisesRegex(ValueError, ROSTERS):
                compare_preview(root, curves, plans, "c"*64,
                                {"n3core": "RUN-fixture"})

    def test_published_plan_binding(self):
        campaign = {"schema": "pext.geometric-campaign/v1",
                    "status": "complete_checked_geometric_counts; controls_and_descent_pending",
                    "cohorts": {
            cohort: {"join_plan_sha256": hashlib.sha256(
                join_path(cohort).read_bytes()).hexdigest()} for cohort in COHORTS}}
        plans = plans_from_campaign(campaign)
        self.assertEqual(set(plans), set(COHORTS))
        campaign["cohorts"]["q5-n3"]["join_plan_sha256"] = "0"*64
        with self.assertRaisesRegex(ValueError, "differs from checked campaign"):
            plans_from_campaign(campaign)


if __name__ == "__main__":
    unittest.main(verbosity=2)
