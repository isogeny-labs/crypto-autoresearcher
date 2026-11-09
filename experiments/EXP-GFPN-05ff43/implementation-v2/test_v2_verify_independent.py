"""V2 cardinality controls using a compact archived instrument certificate.

Source: RUN-GFPN-0037fb/certificates/decomposition_torsion_S3_norm_tctl_planted_r0.json.
The archived JSON has SHA-256 86647e724ac1ebdb4a24081cc139557bbbb1a9f7d8860f99aed6594b12c4efc1.
"""

import copy
import unittest

import v2_verify_independent


CERT = {
    "p": 4111, "n": 5, "modulus": [4109, 0, 0, 0, 0, 1], "arm": "torsion_S3_norm",
    "m": 3, "known_scalar": True, "relation_mod_T": False,
    "curve": {"a2": [2, 0, 0, 0, 0], "a4": [0, 63, 0, 0, 0],
              "a6": [0, 0, 0, 0, 0]},
    "subgroup_order": 587093656674520813, "k": 1,
    "G": [[1163, 4074, 2375, 2637, 1892], [1187, 883, 1878, 2502, 1843]],
    "R": [[1163, 4074, 2375, 2637, 1892], [1187, 883, 1878, 2502, 1843]],
    "factor_base": {"kind": "x_plus_b_over_x_in_Fp"},
    "points": [
        [[2565, 2464, 3138, 2946, 3543], [3443, 3761, 255, 656, 1015]],
        [[1609, 3475, 4043, 450, 3063], [1525, 851, 4021, 2772, 1273]],
        [[2351, 3544, 2226, 3424, 1885], [3029, 198, 593, 1806, 3518]],
    ],
    "signs": [1, 1, 1],
}


class V2CertificateCardinalityTests(unittest.TestCase):
    def test_archived_valid_relation(self):
        self.assertEqual(v2_verify_independent.verify(copy.deepcopy(CERT)), (True, 3, []))

    def test_extra_point_cannot_be_ignored_by_zip(self):
        cert = copy.deepcopy(CERT)
        cert["points"].append(copy.deepcopy(cert["points"][0]))
        ok, count, reasons = v2_verify_independent.verify(cert)
        self.assertFalse(ok)
        self.assertEqual(count, 0)
        self.assertIn("expected 3 points and signs, got 4 / 3", reasons)

    def test_noncanonical_coordinate_rejected(self):
        for change in ("out_of_range", "extra_coefficient"):
            with self.subTest(change=change):
                cert = copy.deepcopy(CERT)
                if change == "out_of_range":
                    cert["points"][0][0][0] += cert["p"]
                else:
                    cert["points"][0][0].append(0)
                ok, count, reasons = v2_verify_independent.verify(cert)
                self.assertFalse(ok)
                self.assertEqual(count, 0)
                self.assertTrue(any("canonical n-tuple" in reason for reason in reasons))

    def test_noncanonical_curve_and_modulus_rejected(self):
        for key in ("curve", "modulus"):
            with self.subTest(key=key):
                cert = copy.deepcopy(CERT)
                if key == "curve":
                    cert["curve"]["a4"][1] += cert["p"]
                else:
                    cert["modulus"][0] += cert["p"]
                ok, count, _ = v2_verify_independent.verify(cert)
                self.assertFalse(ok)
                self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
