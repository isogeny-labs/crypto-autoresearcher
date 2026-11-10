"""Full-cohort C3 sealed-read A/A artifact contract."""

import copy
from pathlib import Path
import tempfile
import unittest

from c3_order_control import ARTIFACT, compare_artifact, write_artifact
from geometric_campaign import EXPECTED


class C3OrderControlTests(unittest.TestCase):
    def test_write_once_equal_rows_and_changed_minimum_refusal(self):
        curves = [{"cohort": name, "class_index": 0,
                   "xline_geometric_minimum": index + 1,
                   "all_maps_geometric_minimum": index + 1,
                   "T_count": 1,
                   "units": [{"candidate_order_aa":
                              "reverse-cocycle-build-representatives-buckets-and-roots/v1"}]}
                  for index, name in enumerate(EXPECTED)]
        campaign = {"schema": "pext.geometric-campaign/v1",
                    "cohorts": {name: {"classes": 1, "T_blocks": 1}
                                for name in EXPECTED}}
        runs = {"n3core": "RUN-one", "n3ext": "RUN-two", "n5": "RUN-three"}
        with tempfile.TemporaryDirectory(prefix="pext-c3-aa-") as scratch:
            root = Path(scratch)
            result = write_artifact(root, curves, campaign,
                                    copy.deepcopy(curves), copy.deepcopy(campaign),
                                    "a" * 64, runs)
            self.assertEqual(result["classes_by_cohort"],
                             {name: 1 for name in EXPECTED})
            self.assertTrue(compare_artifact(root, curves, campaign,
                                             copy.deepcopy(curves), copy.deepcopy(campaign),
                                             "a" * 64, runs)["valid"])
            with self.assertRaises(FileExistsError):
                write_artifact(root, curves, campaign, curves, campaign,
                               "a" * 64, runs)
            altered = copy.deepcopy(curves)
            altered[-1]["all_maps_geometric_minimum"] = 0
            with self.assertRaisesRegex(ValueError, "reductions differ"):
                compare_artifact(root, curves, campaign, altered, campaign,
                                 "a" * 64, runs)
            missing_candidate_aa = copy.deepcopy(curves)
            missing_candidate_aa[0]["units"][0].pop("candidate_order_aa")
            with self.assertRaisesRegex(ValueError, "candidate-order A/A missing"):
                compare_artifact(root, missing_candidate_aa, campaign,
                                 missing_candidate_aa, campaign, "a" * 64, runs)
            artifact = root / ARTIFACT
            artifact.unlink()
            artifact.symlink_to(root / "missing")
            with self.assertRaisesRegex(ValueError, "artifact differs"):
                compare_artifact(root, curves, campaign, curves, campaign,
                                 "a" * 64, runs)


if __name__ == "__main__":
    unittest.main(verbosity=2)
