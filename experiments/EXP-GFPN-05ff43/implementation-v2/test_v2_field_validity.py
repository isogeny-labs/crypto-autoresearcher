"""Independent field preflight controls for V2 decomposition certificates."""

import copy
import unittest

import v2_verify_independent as verifier
from test_v2_verify_independent import CERT


class FieldValidityTests(unittest.TestCase):
    def test_archived_field_parameters(self):
        # The 168 tracked V2 certificates use exactly these three fields.
        self.assertTrue(verifier._field_is_valid(4111, (4109, 0, 0, 1)))
        self.assertTrue(verifier._field_is_valid(4111, (4109, 0, 0, 0, 0, 1)))
        self.assertTrue(verifier._field_is_valid(16777291, (16777289, 0, 0, 1)))

    def test_reducible_polynomial_and_composite_modulus(self):
        self.assertFalse(verifier._field_is_valid(5, (4, 0, 1)))  # x² - 1
        self.assertTrue(verifier._field_is_valid(5, (2, 0, 1)))   # x² + 2
        self.assertFalse(verifier._field_is_valid(9, (1, 0, 1)))

    def test_full_certificate_rejects_reducible_field(self):
        cert = copy.deepcopy(CERT)
        cert["modulus"] = [0, 0, 0, 0, 0, 1]  # x⁵
        ok, count, reasons = verifier.verify(cert)
        self.assertFalse(ok)
        self.assertEqual(count, 0)
        self.assertTrue(any("modulus is reducible" in reason for reason in reasons))

    def test_full_certificate_rejects_composite_p(self):
        cert = copy.deepcopy(CERT)
        cert["p"] = 4110
        ok, count, reasons = verifier.verify(cert)
        self.assertFalse(ok)
        self.assertEqual(count, 0)
        self.assertTrue(any("p is not an admitted prime" in reason for reason in reasons))


if __name__ == "__main__":
    unittest.main()
