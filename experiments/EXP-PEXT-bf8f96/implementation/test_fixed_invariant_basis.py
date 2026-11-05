"""Exact fixed-vector bases, including characteristic-dividing-degree trace."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from candidate_binding import CandidateBinder
from candidate_stage import join_path
from check_compact_class_inputs import BasisField
from check_quotient_certificate import polynomial_mul
from fixed_invariant_basis import build


class FixedInvariantBasisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-fixed-basis-")
        binary = Path(cls.scratch.name) / "join"
        subprocess.run(["rustc", "--edition=2021", str(Path(__file__).with_name(
            "join_certificate.rs")), "-o", str(binary)], check=True, capture_output=True)
        cls.joined = json.loads(subprocess.check_output([binary, "f27-char3", "0", "4"]))
        cls.field = BasisField(cls.joined["field"])

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_f27_source_orbits_and_characteristic_three_trace(self):
        dimensions = []
        for row in self.joined["rows"]:
            result = build(self.field, row["conjugates"])
            dimensions.append(result["basis_dimension"])
            self.assertEqual(result["basis_dimension"],
                             len(result["algebra"]["basis_masks"]))
            self.assertEqual(result["moore_rank"], 3)
            self.assertEqual(sum(len(orbit) for orbit in result["orbits"]),
                             result["basis_dimension"])
            for vector in result["vectors"]:
                if len(vector["coefficients"]) == 1:
                    self.assertEqual(vector["seed_basis_index"], 2)
        self.assertEqual(dimensions, [2, 8, 8, 8])

    def test_nonsquare_constant_twist_keeps_exact_basis_dimension(self):
        f = self.field
        a = [1, 3, 1]
        b = [f.power(value, 3) for value in a]
        c = [f.power(value, 9) for value in a]
        forms = [polynomial_mul(f, a, b), polynomial_mul(f, b, c),
                 polynomial_mul(f, c, a)]
        original = build(f, forms)
        twisted = build(f, [[f.mul(2, value) for value in form] for form in forms])
        self.assertEqual((original["basis_dimension"], twisted["basis_dimension"]), (4, 8))
        self.assertTrue(twisted["algebra"]["constant_nonsquare_relation"])

    def test_published_n5_class_has_checked_fixed_basis(self):
        binder = CandidateBinder("q3-n5", plan_path=join_path("q3-n5"))
        binding = binder.bind(0, 0)
        f = binder.field
        forms = [binding["quotient_form"]]
        for _ in range(f.n-1):
            forms.append([f.power(value, f.p) for value in forms[-1]])
        result = build(f, forms)
        self.assertEqual(result["degree"], 5)
        self.assertEqual(result["basis_dimension"], 2)
        self.assertEqual(result["status"],
                         "fixed_kx_basis_checked; base_multiplication_pending")


if __name__ == "__main__":
    unittest.main(verbosity=2)
