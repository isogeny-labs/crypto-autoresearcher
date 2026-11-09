"""Certificate cardinality controls using archived decomposition_t0_r0 values.

Source: GOAL-GFPN-380702 review TASK-20260923-404bf9, run_complete.
The archived JSON has SHA-256 5aa9d97027c48ff3e05b5f462e9b070b199d99b21399ed87648025bff48d99f4.
"""

import copy
import unittest

import verify_independent


CERT = {
    "p": 11, "cmod": 2, "arm": "S4", "m": 4,
    "curve": {"a2": [2, 0, 0, 0, 0], "a4": [0, 10, 0, 0, 0],
              "a6": [0, 0, 0, 0, 0]},
    "G": [[3, 9, 9, 8, 1], [9, 4, 7, 7, 1]],
    "R": [[0, 0, 1, 10, 6], [5, 1, 7, 4, 7]],
    "k": 9744, "subgroup_order": 80376,
    "points": [
        [[7, 0, 0, 0, 0], [2, 5, 7, 8, 9]],
        [[7, 0, 0, 0, 0], [2, 5, 7, 8, 9]],
        [[6, 0, 0, 0, 0], [4, 7, 9, 0, 5]],
        [[6, 0, 0, 0, 0], [4, 7, 9, 0, 5]],
    ],
    "signs": [1, 1, -1, -1],
}


class CertificateCardinalityTests(unittest.TestCase):
    def test_archived_valid_relation(self):
        self.assertEqual(verify_independent.verify(copy.deepcopy(CERT)), (True, 4, []))

    def test_extra_point_cannot_be_ignored_by_zip(self):
        cert = copy.deepcopy(CERT)
        cert["points"].append(copy.deepcopy(cert["points"][0]))
        ok, count, reasons = verify_independent.verify(cert)
        self.assertFalse(ok)
        self.assertEqual(count, 0)
        self.assertIn("expected 4 points, got 5", reasons)

    def test_extra_sign_cannot_be_ignored_by_zip(self):
        cert = copy.deepcopy(CERT)
        cert["signs"].append(1)
        ok, count, reasons = verify_independent.verify(cert)
        self.assertFalse(ok)
        self.assertEqual(count, 0)
        self.assertIn("expected 4 signs, got 5", reasons)


if __name__ == "__main__":
    unittest.main()
