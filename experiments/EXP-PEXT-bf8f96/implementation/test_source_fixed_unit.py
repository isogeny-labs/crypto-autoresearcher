"""Published curve/T/ordinal binding for one exceptional fixed model."""

import unittest

from candidate_binding import CandidateBinder
from candidate_stage import join_path
from source_fixed_unit import assess


class SourceFixedUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binder = CandidateBinder("q5-n3", plan_path=join_path("q5-n3"))

    def test_published_zero_target_identity_exceptional_row(self):
        result = assess(self.binder, 0, 0, [0, [1, 0, 0, 1], 1, 4, 1])
        self.assertEqual(result["join_plan_sha256"], self.binder.plan_sha256)
        self.assertTrue(result["independent_check"]["valid"])
        self.assertEqual(result["connected_curve_genus"], 1)
        self.assertEqual(result["source_fixed_model"]["source"]["source"]["source_map"]
                         ["moved_form"], [1, 0, 0, 1, 0])

    def test_wrong_ordinal_matrix_and_genus_refused(self):
        with self.assertRaisesRegex(ValueError, "matrix differs"):
            assess(self.binder, 0, 0, [0, [0, 1, 1, 0], 1, 4, 1])
        with self.assertRaisesRegex(ValueError, "independent component geometry"):
            assess(self.binder, 0, 0, [0, [1, 0, 0, 1], 1, 4, 2])


if __name__ == "__main__":
    unittest.main(verbosity=2)
