"""Exact radical action and witness consistency on F27 software fixtures."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from check_compact_class_inputs import BasisField
from check_quotient_certificate import polynomial_mul
from radical_frobenius import (candidate_lift, monic_polynomial_square_root,
                               relation_square_root, square_root)


class RadicalFrobeniusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-radical-frobenius-")
        binary = Path(cls.scratch.name) / "join"
        subprocess.run(["rustc", "--edition=2021", str(Path(__file__).with_name(
            "join_certificate.rs")), "-o", str(binary)], check=True, capture_output=True)
        joined = json.loads(subprocess.check_output([binary, "f27-char3"]))
        cls.field = BasisField(joined["field"])
        cls.rows = joined["rows"]

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_fixed_join_rows_have_checked_order_three_action(self):
        for row in self.rows[:6]:
            result = candidate_lift(self.field, row["conjugates"])
            self.assertEqual(result["status"],
                             "order_n_radical_lift_checked; source_map_and_model_pending")
            self.assertTrue(result["order_n_check"])
            self.assertEqual(sum(result["generator_signs"]) % 2, 0)

    def test_canonical_root_signs_are_corrected(self):
        field = self.field
        base = [1, 0, 0, 0, 1]
        forms = [[field.mul(field.power(3, 3**index), value) for value in base]
                 for index in range(3)]
        result = candidate_lift(field, forms)
        self.assertEqual((result["geometric_rank"], result["arithmetic_rank"]), (1, 1))
        self.assertEqual(result["generator_signs"], [1, 0, 1])
        self.assertEqual(result["relation_equations"], 4)
        self.assertEqual(len(result["basis_witnesses"]), 2)

    def test_nonsquare_constant_is_not_misread_as_relation_witness(self):
        field = self.field
        first = [1, 3, 1]
        second = [field.power(value, 3) for value in first]
        third = [field.power(value, 9) for value in first]
        monic = [polynomial_mul(field, first, second),
                 polynomial_mul(field, second, third),
                 polynomial_mul(field, third, first)]
        twisted = [[field.mul(2, value) for value in form] for form in monic]
        result = candidate_lift(field, twisted)
        self.assertEqual((result["geometric_rank"], result["arithmetic_rank"]), (2, 3))
        self.assertTrue(result["constant_nonsquare_relation"])
        with self.assertRaisesRegex(ValueError, "nonsquare"):
            relation_square_root(field, twisted, 7)

    def test_invalid_square_witness_rejected(self):
        field = self.field
        self.assertIsNone(square_root(field, 2))
        self.assertEqual(monic_polynomial_square_root(field, [1, 2, 1]), [1, 1])
        with self.assertRaisesRegex(ValueError, "not an exact square"):
            monic_polynomial_square_root(field, [1, 0, 1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
