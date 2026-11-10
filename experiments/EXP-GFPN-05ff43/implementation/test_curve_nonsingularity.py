"""A singular cubic must not produce a decomposition certificate verdict."""

import copy
import unittest

import verify_independent as verifier
from test_verify_independent import CERT


class CurveNonsingularityTests(unittest.TestCase):
    def test_archived_curve_is_nonsingular(self):
        cert = copy.deepcopy(CERT)
        field = verifier.FqP(cert["p"], cert["cmod"])
        curve = verifier.CurveP(field, *(
            cert["curve"][key] for key in ("a2", "a4", "a6")
        ))
        self.assertTrue(curve.is_nonsingular())
        self.assertTrue(verifier.verify(cert)[0])

    def test_cuspidal_certificate_rejected(self):
        # Before this gate, the formula accepted this record: the point
        # (1,1) has order p under the arithmetic on singular y²=x³.
        zero = [0] * 5
        one = [1, 0, 0, 0, 0]
        cert = {"p": 11, "cmod": 2,
                "curve": {"a2": zero, "a4": zero, "a6": zero},
                "G": [one, one], "R": [one, one], "k": 1,
                "subgroup_order": 11, "m": 1, "arm": "S1",
                "points": [[one, one]], "signs": [1]}
        self.assertEqual(verifier.verify(cert), (False, 0, ["singular curve"]))


if __name__ == "__main__":
    unittest.main()
