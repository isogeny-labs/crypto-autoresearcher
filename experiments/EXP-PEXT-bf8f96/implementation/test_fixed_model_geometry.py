"""Component geometry checks on exact source and constant-twist fixtures."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from check_quotient_certificate import polynomial_mul
from fixed_field_multiplication import build as build_fixed
from fixed_model_geometry import assess, build_from_source
from target_transport import verified_field


class FixedModelGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-fixed-geometry-")
        binary = Path(cls.scratch.name) / "join"
        subprocess.run(["rustc", "--edition=2021", str(Path(__file__).with_name(
            "join_certificate.rs")), "-o", str(binary)], check=True, capture_output=True)
        cls.joined = json.loads(subprocess.check_output([binary, "f27-char3", "0", "4"]))
        cls.field = verified_field(json.dumps(cls.joined["field"], sort_keys=True,
                                              separators=(",", ":")))

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_source_rows_bind_rank_and_component_genus(self):
        observed = []
        for row in self.joined["rows"]:
            result = build_from_source(self.joined["field"], row["model"],
                                       row["target"], row["matrix"], row["conjugates"])
            self.assertEqual(result["source"]["source"]["source_map"]["moved_form"],
                             row["transformed_form"])
            self.assertTrue(result["geometrically_connected"])
            observed.append((result["geometric_component_degree"],
                             result["connected_curve_genus"]))
        self.assertEqual(observed, [(2, 1), (8, 13), (8, 13), (8, 13)])

    def test_constant_twist_has_two_geometric_components(self):
        f = self.field
        a = [1, 3, 1]
        b = [f.power(value, 3) for value in a]
        c = [f.power(value, 9) for value in a]
        forms = [polynomial_mul(f, a, b), polynomial_mul(f, b, c),
                 polynomial_mul(f, c, a)]
        twisted = [[f.mul(2, value) for value in form] for form in forms]
        result = assess(self.joined["field"], twisted, build_fixed(f, twisted))
        self.assertEqual((result["independent_relation_replay"]["geometric_rank"],
                          result["independent_relation_replay"]["arithmetic_rank"]), (2, 3))
        self.assertEqual((result["geometric_component_count"],
                          result["geometric_component_degree"]), (2, 4))
        self.assertFalse(result["geometrically_connected"])
        self.assertIsNone(result["connected_curve_genus"])

    def test_rank_mismatch_is_rejected(self):
        row = self.joined["rows"][0]
        fixed = build_fixed(self.field, row["conjugates"])
        fixed["dimension"] += 1
        with self.assertRaisesRegex(ValueError, "independent relation replay"):
            assess(self.joined["field"], row["conjugates"], fixed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
