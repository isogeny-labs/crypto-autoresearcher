"""Published curve/T/ordinal binding for one exceptional fixed model."""

import unittest
from copy import deepcopy

from candidate_binding import CandidateBinder
from candidate_stage import join_path
from source_fixed_unit import assess
from source_map_binding import certify_bound
from independent_source_map_check import verify as verify_source_map


class SourceFixedUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binder = CandidateBinder("q5-n3", plan_path=join_path("q5-n3"))

    def test_published_zero_target_identity_exceptional_row(self):
        result = assess(self.binder, 0, 0, [0, [1, 0, 0, 1], 1, 4, 1])
        self.assertEqual(result["join_plan_sha256"], self.binder.plan_sha256)
        self.assertTrue(result["independent_check"]["valid"])
        self.assertTrue(result["independent_source_map_check"]["valid"])
        self.assertEqual(result["connected_curve_genus"], 1)
        self.assertEqual(result["source_fixed_model"]["source"]["source"]["source_map"]
                         ["moved_form"], [1, 0, 0, 1, 0])

    def test_wrong_ordinal_matrix_and_genus_refused(self):
        with self.assertRaisesRegex(ValueError, "matrix differs"):
            assess(self.binder, 0, 0, [0, [0, 1, 1, 0], 1, 4, 1])
        with self.assertRaisesRegex(ValueError, "independent component geometry"):
            assess(self.binder, 0, 0, [0, [1, 0, 0, 1], 1, 4, 2])

    def test_stored_coordinate_mutations_and_published_identity_refused(self):
        for t_index in (0, 1):
            binding = self.binder.bind(0, t_index)
            record = certify_bound(self.binder, 0, t_index, 0, [1, 0, 0, 1])
            self.assertTrue(verify_source_map(record, binding["field"], binding["model"],
                                              binding["target"], [1, 0, 0, 1])["valid"])
            for key in ("x_map", "y_map"):
                changed = deepcopy(record)
                changed[key]["numerator_constant"] = [0]
                changed[key]["numerator_y"] = [0]
                with self.assertRaisesRegex(ValueError, "stored .* map mismatch"):
                    verify_source_map(changed, binding["field"], binding["model"],
                                      binding["target"], [1, 0, 0, 1])
            changed = deepcopy(record)
            changed["target"] = None if t_index else self.binder.bind(0, 1)["target"]
            with self.assertRaisesRegex(ValueError, "external identity mismatch"):
                verify_source_map(changed, binding["field"], binding["model"],
                                  binding["target"], [1, 0, 0, 1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
