"""Independent character genus and constant-twist component fixtures."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from check_quotient_certificate import Field, polynomial_mul
from candidate_binding import CandidateBinder
from candidate_stage import join_path
from independent_component_geometry import assess


class IndependentComponentGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-independent-geometry-")
        binary = Path(cls.scratch.name) / "join"
        subprocess.run(["rustc", "--edition=2021", str(Path(__file__).with_name(
            "join_certificate.rs")), "-o", str(binary)], check=True, capture_output=True)
        cls.joined = json.loads(subprocess.check_output([binary, "f27-char3", "0", "4"]))
        cls.field = Field(cls.joined["field"])

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_actual_f27_source_rows(self):
        observed = []
        for row in self.joined["rows"]:
            result = assess(self.joined["field"], row["conjugates"])
            observed.append((result["geometric_component_degree"],
                             result["geometric_component_genus"],
                             result["branch_points"]))
            self.assertEqual(result["geometric_component_count"], 1)
        self.assertEqual(observed, [(2, 1, 4), (8, 13, 10),
                                    (8, 13, 10), (8, 13, 10)])

    def test_constant_twist_suppresses_connected_genus(self):
        f = self.field
        a = [1, 3, 1]
        b = [f.power(value, 3) for value in a]
        c = [f.power(value, 9) for value in a]
        forms = [polynomial_mul(f, a, b), polynomial_mul(f, b, c),
                 polynomial_mul(f, c, a)]
        twisted = [[f.mul(2, value) for value in form] for form in forms]
        result = assess(self.joined["field"], twisted)
        self.assertEqual((result["geometric_rank"], result["arithmetic_rank"]), (2, 3))
        self.assertEqual(result["geometric_component_count"], 2)
        self.assertIsNone(result["connected_curve_genus"])

    def test_published_quintic_extension_class(self):
        binder = CandidateBinder("q3-n5", plan_path=join_path("q3-n5"))
        field = binder.field
        forms = [binder.bind(0, 0)["quotient_form"]]
        for _ in range(field.n - 1):
            forms.append([field.power(value, field.p) for value in forms[-1]])
        result = assess(binder.plan["field"], forms)
        self.assertEqual((result["geometric_component_count"],
                          result["geometric_component_degree"],
                          result["connected_curve_genus"]), (1, 2, 1))

    def test_nonconjugate_form_is_rejected(self):
        forms = [list(row) for row in self.joined["rows"][1]["conjugates"]]
        forms[1][0] = self.field.add(forms[1][0], 1)
        with self.assertRaisesRegex(ValueError, "nonconjugate"):
            assess(self.joined["field"], forms)


if __name__ == "__main__":
    unittest.main(verbosity=2)
