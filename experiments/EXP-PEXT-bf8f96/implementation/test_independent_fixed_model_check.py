"""Independent fixed-model replay and corruption tests on source fixtures."""

import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from candidate_binding import CandidateBinder
from candidate_stage import join_path
from fixed_field_multiplication import build as build_fixed
from fixed_model_geometry import build_from_source
from independent_fixed_model_check import verify


class IndependentFixedModelCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-independent-fixed-")
        binary = Path(cls.scratch.name) / "join"
        subprocess.run(["rustc", "--edition=2021", str(Path(__file__).with_name(
            "join_certificate.rs")), "-o", str(binary)], check=True,
            capture_output=True)
        cls.joined = json.loads(subprocess.check_output(
            [binary, "f27-char3", "0", "4"]))
        cls.records = []
        for row in cls.joined["rows"]:
            record = build_from_source(cls.joined["field"], row["model"],
                                       row["target"], row["matrix"],
                                       row["conjugates"])
            cls.records.append(json.loads(json.dumps(record)))

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_every_source_fixture_product_and_unit_replayed(self):
        checked = [verify(record, self.joined["field"], row["conjugates"])
                   for record, row in zip(self.records, self.joined["rows"])]
        self.assertEqual([row["products_checked"] for row in checked],
                         [4, 64, 64, 64])
        self.assertTrue(all(row["valid"] and row["source_generator_checked"]
                            for row in checked))

    def test_published_n5_fixed_algebra_replayed(self):
        binder = CandidateBinder("q3-n5", plan_path=join_path("q3-n5"))
        binding = binder.bind(0, 0)
        field = binder.field
        forms = [binding["quotient_form"]]
        for _ in range(field.n-1):
            forms.append([field.power(value, field.p) for value in forms[-1]])
        checked = verify(json.loads(json.dumps(build_fixed(field, forms))),
                         binding["field"], forms)
        self.assertEqual((checked["dimension"], checked["products_checked"]),
                         (2, 4))

    def test_tampered_fixed_multiplication_coefficient_rejected(self):
        record = copy.deepcopy(self.records[1])
        table = record["fixed_model"]["multiplication"]
        term = next(term for row in table for product in row for term in product)
        numerator = term["factor"]["numerator"]
        numerator[0] = 1 if numerator[0] != 1 else 2
        with self.assertRaisesRegex(ValueError, "fixed multiplication"):
            verify(record, self.joined["field"], self.joined["rows"][1]["conjugates"])

    def test_tampered_fixed_basis_factor_rejected(self):
        record = copy.deepcopy(self.records[1])
        vector = record["fixed_model"]["basis"]["vectors"][0]
        numerator = vector["coefficients"][0]["factor"]["numerator"]
        numerator[0] = (numerator[0] + 1) % 27
        with self.assertRaisesRegex(ValueError, "fixed basis vector"):
            verify(record, self.joined["field"], self.joined["rows"][1]["conjugates"])

    def test_tampered_source_form_rejected(self):
        record = copy.deepcopy(self.records[0])
        source_map = record["source"]["source"]["source_map"]
        source_map["moved_form"][0] = (source_map["moved_form"][0] + 1) % 27
        with self.assertRaisesRegex(ValueError, "source form mismatch"):
            verify(record, self.joined["field"], self.joined["rows"][0]["conjugates"])

    def test_tampered_source_map_readback_rejected(self):
        row = self.joined["rows"][0]
        for key, component, expected_error in (
                ("determinant", None, "source determinant mismatch"),
                ("x_map", "numerator_constant", "stored x map mismatch"),
                ("y_map", "numerator_y", "stored y map mismatch")):
            with self.subTest(key=key):
                record = copy.deepcopy(self.records[0])
                source_map = record["source"]["source"]["source_map"]
                if component is None:
                    source_map[key] = 2
                else:
                    source_map[key][component][0] = (source_map[key][component][0] + 1) % 27
                with self.assertRaisesRegex(ValueError, expected_error):
                    verify(record, self.joined["field"], row["conjugates"])

    def test_tampered_ambient_table_rejected(self):
        record = copy.deepcopy(self.records[0])
        algebra = record["fixed_model"]["basis"]["algebra"]
        algebra["multiplication"][0][0]["factor"]["numerator"][0] = 2
        with self.assertRaisesRegex(ValueError, "ambient multiplication"):
            verify(record, self.joined["field"], self.joined["rows"][0]["conjugates"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
