"""Refusal checks for the exact four-cohort geometric campaign join."""

import copy
import unittest

from geometric_campaign import EXPECTED, aggregate_cohorts


class CampaignAggregationTests(unittest.TestCase):
    def fixture(self):
        curves, metrics = [], {}
        for name in EXPECTED:
            targets = 1 if name == "q7-n3" else 2
            curve = {"cohort": name, "class_index": 0, "T_count": targets,
                     "units": [{"T_index": t, "geometric_minimum":
                                1 if name == "q5-n3" and t == 1 else 2}
                               for t in range(targets)],
                     "xline_geometric_minimum": 2,
                     "all_maps_geometric_minimum": 1 if name == "q5-n3" else 2,
                     "strict_geometric_minimum_drop": name == "q5-n3",
                     "branch_type_mismatch_count": 0,
                     "geometric_spectrum_violation_count": 0}
            row = {"classes": 1, "T_blocks": targets, "structures": 20,
                   "exceptional": 4, "generic": 16,
                   "curves_with_strict_geometric_minimum_drop": int(
                       curve["strict_geometric_minimum_drop"]),
                   "branch_type_mismatch_count": 0,
                   "geometric_spectrum_violation_count": 0}
            if EXPECTED[name][1] == 3:
                curve.update(type2_signature_count=1,
                             hyperelliptic_predicate_true_count=1,
                             hyperelliptic_predicate_false_count=0)
                row.update(type2_signature_count=1,
                           hyperelliptic_predicate_true_count=1,
                           hyperelliptic_predicate_false_count=0)
            curves.append(curve); metrics[name] = row
        return curves, metrics

    def test_exact_scope_and_curve_reconciliation(self):
        curves, metrics = self.fixture()
        result = aggregate_cohorts(curves, metrics)
        self.assertEqual(result["totals"]["classes"], 4)
        self.assertEqual(result["p3_geometric_drop_by_cohort"]["q5-n3"], 1)
        self.assertEqual(result["control_c1"]["odd_order_curves_by_cohort"]["q7-n3"], 1)
        self.assertEqual(set(result["type2_by_cubic_cohort"]),
                         {"q5-n3", "q7-n3", "q11-n3"})
        with self.assertRaisesRegex(ValueError, "coverage incomplete"):
            aggregate_cohorts(curves, {key: value for key, value in metrics.items()
                                       if key != "q3-n5"})
        corrupted = copy.deepcopy(curves)
        corrupted[0]["strict_geometric_minimum_drop"] = False
        with self.assertRaisesRegex(ValueError, "actual curve rows"):
            aggregate_cohorts(corrupted, metrics)
        corrupted = copy.deepcopy(curves)
        corrupted[1]["hyperelliptic_predicate_true_count"] = 0
        with self.assertRaisesRegex(ValueError, "Type2 cohort total"):
            aggregate_cohorts(corrupted, metrics)
        corrupted = copy.deepcopy(curves)
        corrupted[1]["all_maps_geometric_minimum"] = 1
        with self.assertRaisesRegex(ValueError, "C1 odd-order"):
            aggregate_cohorts(corrupted, metrics)
        corrupted = copy.deepcopy(curves)
        corrupted[1]["units"].append({"T_index": 1, "geometric_minimum": 1})
        with self.assertRaisesRegex(ValueError, "C1 curve lacks complete"):
            aggregate_cohorts(corrupted, metrics)


if __name__ == "__main__":
    unittest.main(verbosity=2)
