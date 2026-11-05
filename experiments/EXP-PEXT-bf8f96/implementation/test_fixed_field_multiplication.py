"""Exact base-field multiplication on F27 and published n5 fixtures."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from candidate_binding import CandidateBinder
from candidate_stage import join_path
from check_compact_class_inputs import BasisField
from check_quotient_certificate import polynomial_mul
from fixed_field_multiplication import build, build_from_source


class FixedFieldMultiplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-fixed-multiplication-")
        binary = Path(cls.scratch.name) / "join"
        subprocess.run(["rustc", "--edition=2021", str(Path(__file__).with_name(
            "join_certificate.rs")), "-o", str(binary)], check=True, capture_output=True)
        cls.joined = json.loads(subprocess.check_output([binary, "f27-char3", "0", "4"]))
        cls.field = BasisField(cls.joined["field"])

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def assert_base_factors(self, result, prime):
        for row in result["multiplication"]:
            for product in row:
                for term in product:
                    for key in ("numerator", "denominator"):
                        self.assertTrue(all(0 <= value < prime for value in
                                            term["factor"][key]))
        for term in result["unit"]:
            for key in ("numerator", "denominator"):
                self.assertTrue(all(0 <= value < prime for value in
                                    term["factor"][key]))

    def test_f27_source_rows_have_exact_base_multiplication(self):
        dimensions = []
        for row in self.joined["rows"]:
            result = build(self.field, row["conjugates"])
            dimensions.append(result["dimension"])
            self.assertEqual(len(result["multiplication"]), result["dimension"])
            self.assertEqual(result["basis"]["basis_dimension"], result["dimension"])
            self.assertEqual(result["status"],
                             "fixed_field_multiplication_checked; independent_descent_review_pending")
            self.assert_base_factors(result, 3)
        self.assertEqual(dimensions, [2, 8, 8, 8])

    def test_named_source_binds_fixed_multiplication(self):
        row = self.joined["rows"][0]
        result = build_from_source(self.joined["field"], row["model"],
                                   row["target"], row["matrix"], row["conjugates"])
        self.assertEqual(result["source"]["source"]["source_map"]["moved_form"],
                         row["transformed_form"])
        self.assertEqual(result["fixed"]["dimension"], 2)
        self.assert_base_factors(result["fixed"], 3)

    def test_constant_twist_changes_base_algebra_dimension(self):
        f = self.field
        a = [1, 3, 1]
        b = [f.power(value, 3) for value in a]
        c = [f.power(value, 9) for value in a]
        forms = [polynomial_mul(f, a, b), polynomial_mul(f, b, c),
                 polynomial_mul(f, c, a)]
        original = build(f, forms)
        twisted = build(f, [[f.mul(2, value) for value in form] for form in forms])
        self.assertEqual((original["dimension"], twisted["dimension"]), (4, 8))
        self.assert_base_factors(twisted, 3)

    def test_published_n5_class_has_base_multiplication(self):
        binder = CandidateBinder("q3-n5", plan_path=join_path("q3-n5"))
        f = binder.field
        forms = [binder.bind(0, 0)["quotient_form"]]
        for _ in range(f.n-1):
            forms.append([f.power(value, f.p) for value in forms[-1]])
        result = build(f, forms)
        self.assertEqual((result["degree"], result["dimension"]), (5, 2))
        self.assert_base_factors(result, 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
