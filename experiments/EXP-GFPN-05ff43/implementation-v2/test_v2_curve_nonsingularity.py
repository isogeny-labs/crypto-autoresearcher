"""The V2 verifier must reject singular curves before group arithmetic."""

import copy
import unittest

import v2_verify_independent as verifier
from test_v2_verify_independent import CERT


class V2CurveNonsingularityTests(unittest.TestCase):
    def test_archived_curve_is_nonsingular(self):
        cert = copy.deepcopy(CERT)
        field = verifier.FqP(cert["p"], cert["modulus"])
        curve = verifier.CurveP(field, *(
            cert["curve"][key] for key in ("a2", "a4", "a6")
        ))
        self.assertTrue(curve.is_nonsingular())
        self.assertTrue(verifier.verify(cert)[0])

    def test_cuspidal_certificate_rejected(self):
        # Before this gate, the singular y²=x³ record passed every check.
        zero = [0] * 3
        one = [1, 0, 0]
        cert = {"p": 4111, "n": 3, "modulus": [4109, 0, 0, 1],
                "curve": {"a2": zero, "a4": zero, "a6": zero},
                "G": [one, one], "R": [one, one], "k": 1,
                "subgroup_order": 4111, "m": 1, "arm": "S1",
                "factor_base": {"kind": "x_in_Fp"},
                "points": [[one, one]], "signs": [1],
                "known_scalar": True, "relation_mod_T": False}
        ok, count, reasons = verifier.verify(cert)
        self.assertFalse(ok)
        self.assertEqual(count, 0)
        self.assertTrue(any("singular curve" in reason for reason in reasons))


if __name__ == "__main__":
    unittest.main()
