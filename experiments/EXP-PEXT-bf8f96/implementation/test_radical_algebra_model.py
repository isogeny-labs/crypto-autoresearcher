"""F27 source, monomial algebra, Frobenius and constant-twist controls."""

import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from check_compact_class_inputs import BasisField
from check_quotient_certificate import polynomial_mul
from radical_algebra_model import build, build_from_source


class RadicalAlgebraModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-radical-algebra-")
        binary = Path(cls.scratch.name) / "join"
        subprocess.run(["rustc", "--edition=2021", str(Path(__file__).with_name(
            "join_certificate.rs")), "-o", str(binary)], check=True, capture_output=True)
        cls.joined = json.loads(subprocess.check_output([binary, "f27-char3", "0", "4"]))
        cls.field = BasisField(cls.joined["field"])
        cls.rows = cls.joined["rows"]

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_actual_source_forms_give_exact_dimensions_and_action(self):
        ranks = []
        for row in self.rows:
            result = build_from_source(self.joined["field"], row["model"],
                                       row["target"], row["matrix"], row["conjugates"])
            algebra = result["algebra"]
            ranks.append(algebra["arithmetic_rank"])
            self.assertEqual(len(algebra["basis_masks"]), 1 << algebra["arithmetic_rank"])
            self.assertEqual(len(algebra["multiplication"]), len(algebra["basis_masks"]))
            self.assertEqual(len(algebra["frobenius_action"]), len(algebra["basis_masks"]))
            self.assertEqual(algebra["multiplication"][0][0]["target"], 0)
            self.assertEqual(result["source"]["source_map"]["moved_form"],
                             row["transformed_form"])
            self.assertEqual(result["status"],
                             "source_and_explicit_Kx_algebra_checked; fixed_invariants_pending")
        self.assertEqual(ranks, [1, 3, 3, 3])

    def test_constant_twist_changes_arithmetic_dimension(self):
        field = self.field
        first = [1, 3, 1]
        second = [field.power(value, 3) for value in first]
        third = [field.power(value, 9) for value in first]
        forms = [polynomial_mul(field, first, second),
                 polynomial_mul(field, second, third),
                 polynomial_mul(field, third, first)]
        original = build(field, forms)
        twisted = build(field, [[field.mul(2, value) for value in form]
                                for form in forms])
        self.assertEqual((original["geometric_rank"], original["arithmetic_rank"]), (2, 2))
        self.assertEqual((twisted["geometric_rank"], twisted["arithmetic_rank"]), (2, 3))
        self.assertEqual((len(original["basis_masks"]), len(twisted["basis_masks"])), (4, 8))
        self.assertTrue(twisted["constant_nonsquare_relation"])

    def test_nonconjugate_form_refused(self):
        forms = copy.deepcopy(self.rows[1]["conjugates"])
        forms[1][0] = (forms[1][0] + 1) % 27
        with self.assertRaises(ValueError):
            build(self.field, forms)
        row = self.rows[0]
        forms = copy.deepcopy(row["conjugates"])
        forms[0][0] = (forms[0][0] + 1) % 27
        with self.assertRaisesRegex(ValueError, "conjugate 0 differs"):
            build_from_source(self.joined["field"], row["model"], row["target"],
                              row["matrix"], forms)


if __name__ == "__main__":
    unittest.main(verbosity=2)
