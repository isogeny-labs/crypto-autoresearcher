"""Write-once and exact readback checks for the geometric analysis component."""

import json
from pathlib import Path
import tempfile
import unittest

from geometric_analysis_stage import (ROWS, SUMMARY, compare_artifacts,
                                      write_component)


class GeometricAnalysisArtifactTests(unittest.TestCase):
    def test_write_once_and_tampered_curve_refused(self):
        curves = [{"cohort": "q5-n3", "class_index": 0,
                   "strict_geometric_minimum_drop": True}]
        campaign = {"schema": "pext.geometric-campaign/v1",
                    "status": "complete_checked_geometric_counts; controls_and_descent_pending"}
        source_runs = {"n3core": "RUN-fixture"}
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            summary = write_component(root, curves, campaign, "a"*64, source_runs)
            self.assertEqual(summary["status"],
                             "checked_geometric_counts; controls_and_descent_pending")
            self.assertTrue(compare_artifacts(root, curves, campaign, "a"*64,
                                              source_runs)["valid"])
            with self.assertRaises(FileExistsError):
                write_component(root, curves, campaign, "a"*64, source_runs)
            (root / ROWS).write_text(json.dumps({"cohort": "q5-n3"}) + "\n")
            with self.assertRaisesRegex(ValueError, "geometric-curves.jsonl"):
                compare_artifacts(root, curves, campaign, "a"*64, source_runs)
            (root / ROWS).unlink()
            (root / ROWS).symlink_to(root / SUMMARY)
            with self.assertRaisesRegex(ValueError, "geometric-curves.jsonl"):
                compare_artifacts(root, curves, campaign, "a"*64, source_runs)


if __name__ == "__main__":
    unittest.main(verbosity=2)
