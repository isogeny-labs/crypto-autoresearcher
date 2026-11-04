"""Coefficient-aware relation ledger against independent polynomial squares."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from check_compact_class_inputs import BasisField
from check_quotient_certificate import polynomial_mul, square_relations
from generic_disjoint import classify, exceptional_geometry
from squareclass_relations import coefficient_bit, ledger


class SquareclassRelationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-constant-relations-")
        binary = Path(cls.scratch.name) / "join"
        subprocess.run(["rustc", "--edition=2021", str(Path(__file__).with_name(
            "join_certificate.rs")), "-o", str(binary)], check=True, capture_output=True)
        cls.joined = json.loads(subprocess.check_output([binary, "f27-char3"]))
        cls.field = BasisField(cls.joined["field"])

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_generic_and_exceptional_agree_with_independent_square_test(self):
        selected = {}
        for row in self.joined["rows"]:
            kind = classify(self.field, row["conjugates"])["classification"]
            selected.setdefault(kind, row["conjugates"])
            if len(selected) == 2:
                break
        self.assertEqual(set(selected), {"generic-disjoint", "exceptional"})
        for kind, forms in selected.items():
            result = ledger(self.field, forms)
            self.assertEqual(result["classification"], kind)
            old = square_relations(self.field, forms)
            new = [[row["mask"], row["arithmetic_relation"]]
                   for row in result["relations"] if row["geometric_relation"]]
            self.assertEqual(new, old)
            if kind == "exceptional":
                self.assertEqual(result["geometric_rank"], exceptional_geometry(
                    self.field, forms)["geometric_squareclass_rank"])
            else:
                self.assertEqual(result["geometric_rank"], 3)

    def test_nonsquare_coefficients_retained_in_repeated_support(self):
        field = self.field
        self.assertEqual(coefficient_bit(field, 1), 0)
        self.assertEqual(coefficient_bit(field, 2), 1)
        for coefficient in (1, 2):
            forms = [[coefficient, 0, 0, 0, coefficient]]*3
            result = ledger(field, forms)
            self.assertEqual(result["geometric_rank"], 1)
            self.assertEqual(result["arithmetic_rank"], 1)
            self.assertEqual(result["coefficient_nonsquare"],
                             [coefficient == 2]*3)
            self.assertEqual(sum(row["geometric_relation"] for row in
                                 result["relations"]), 4)
            self.assertEqual([[row["mask"], row["arithmetic_relation"]]
                              for row in result["relations"] if row["geometric_relation"]],
                             square_relations(field, forms))
        with self.assertRaisesRegex(ValueError, "nonzero coefficient"):
            coefficient_bit(field, 0)

    def test_synthetic_rank_two_relation_changes_with_constant_twist(self):
        field = self.field
        first = [1, 3, 1]
        second = [field.power(value, 3) for value in first]
        third = [field.power(value, 9) for value in first]
        forms = [polynomial_mul(field, first, second),
                 polynomial_mul(field, second, third),
                 polynomial_mul(field, third, first)]
        self.assertEqual((ledger(field, forms)["geometric_rank"],
                          ledger(field, forms)["arithmetic_rank"]), (2, 2))
        twisted = [[field.mul(2, value) for value in form] for form in forms]
        result = ledger(field, twisted)
        self.assertEqual((result["geometric_rank"], result["arithmetic_rank"]), (2, 3))
        self.assertTrue(result["constant_nonsquare_relation"])
        self.assertEqual(result["relations"][7]["projective_support"], [[1], False])
        self.assertFalse(result["relations"][7]["arithmetic_relation"])
        self.assertEqual([[row["mask"], row["arithmetic_relation"]]
                          for row in result["relations"] if row["geometric_relation"]],
                         square_relations(field, twisted))


if __name__ == "__main__":
    unittest.main(verbosity=2)
