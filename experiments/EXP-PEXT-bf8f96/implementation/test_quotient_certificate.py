"""Fixed producer/checker interoperability and adversarial software tests."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from check_quotient_certificate import Field, load, square_relations, verify


FIXTURES = {
    "f3-char3": (3, 1, [0, 1], [1, 0, 1], 6, 2),
    "f5-odd": (5, 1, [0, 1], [0, 1, 1], 9, 1),
    "f5-split": (5, 1, [0, 1], [0, 1, 0], 4, 4),
    "f9-embedded": (3, 2, [1, 0, 1], [1, 0, 1], 12, 4),
    "f125-embedded": (5, 3, [1, 1, 0, 1], [0, 1, 1], 108, 4),
}


def expected(name):
    p, n, modulus, curve, _, _ = FIXTURES[name]
    return {"field": {"prime": p, "degree": n, "modulus": modulus}, "curve": curve}


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-cert-software-")
        cls.binary = str(Path(cls.scratch.name)/"certificate")
        subprocess.run(["rustc", "--edition", "2021", str(Path(__file__).with_name("quotient_certificate.rs")), "-o", cls.binary], check=True)
        cls.records = {name: json.loads(subprocess.check_output([cls.binary, name])) for name in FIXTURES}

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_five_fixed_certificates(self):
        for name, record in self.records.items():
            with self.subTest(fixture=name):
                result = verify(record, expected(name))
                self.assertEqual((result["points"], result["cosets"]), FIXTURES[name][-2:])

    def test_coverage_witness_chart_and_relation_mutations(self):
        def missing_point(d): d["points"].pop()
        def bad_half(d):
            row = next(r for r in d["cosets"][0]["members"] if r["point"] is not None)
            row["half"] = None
        def missing_chart(d): d["quotients"][1]["images"].pop()
        def wrong_chart(d):
            row = next(r for r in d["quotients"][1]["images"] if "affine" in r["image"])
            row["image"]["affine"][1] = (row["image"]["affine"][1]+1) % 9
        def conjugate(d): d["quotients"][0]["conjugates"][1][0] = (d["quotients"][0]["conjugates"][1][0]+1) % 9
        def omitted_relation(d): d["quotients"][0]["relations"].pop()
        def duplicate_relation(d): d["quotients"][0]["relations"].append(d["quotients"][0]["relations"][0])
        def wrong_scalar(d): d["quotients"][0]["relations"][0][1] = False
        def boolean_rank(d): d["quotients"][0]["geometric_rank"] = True
        def duplicate_coset(d): d["cosets"][1] = d["cosets"][0]
        def extra_image_key(d): d["quotients"][1]["images"][0]["image"]["extra"] = 0
        for mutation in [missing_point, bad_half, missing_chart, wrong_chart, conjugate, omitted_relation,
                         duplicate_relation, wrong_scalar, boolean_rank, duplicate_coset, extra_image_key]:
            with self.subTest(mutation=mutation.__name__):
                record = copy.deepcopy(self.records["f9-embedded"])
                mutation(record)
                with self.assertRaises(ValueError): verify(record, expected("f9-embedded"))

    def test_field_and_expected_input_rejection(self):
        record = copy.deepcopy(self.records["f9-embedded"])
        record["field"]["logarithm_to_polynomial_index"][2] = 1
        with self.assertRaises(ValueError): verify(record, expected("f9-embedded"))
        field = copy.deepcopy(self.records["f9-embedded"]["field"])
        field["modulus"] = [0, 0, 1]
        with self.assertRaises(ValueError): Field(field)
        with self.assertRaises(ValueError): verify(self.records["f9-embedded"], expected("f9-embedded"), field_limit=8)
        with self.assertRaises(ValueError): verify(self.records["f5-split"], expected("f5-odd"))
        record = copy.deepcopy(self.records["f5-odd"])
        record["curve"][0] = False
        with self.assertRaises(ValueError): verify(record, expected("f5-odd"))

    def test_constant_relations_and_projective_rejection(self):
        f = Field(self.records["f5-odd"]["field"])
        form = [1, 1, 0, 1, 0]
        twist = [f.mul(2, c) for c in form]
        self.assertEqual(square_relations(f, [form, form]), [[0, True], [3, True]])
        self.assertEqual(square_relations(f, [form, twist]), [[0, True], [3, False]])
        with self.assertRaises(ValueError): square_relations(f, [[0, 0, 0, 0, 1]])
        with self.assertRaises(ValueError): square_relations(f, [[1, 1, 1, 0, 0]])
        with self.assertRaises(ValueError): square_relations(f, [form]*8)

    def test_cli_expected_input_binding(self):
        certificate = Path(self.scratch.name)/"cli-certificate.json"
        intended = Path(self.scratch.name)/"cli-expected.json"
        certificate.write_text(json.dumps(self.records["f9-embedded"]))
        intended.write_text(json.dumps(expected("f9-embedded")))
        command = [sys.executable, str(Path(__file__).with_name("check_quotient_certificate.py")),
                   str(certificate), "--expected-input", str(intended)]
        accepted = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertTrue(json.loads(accepted.stdout)["valid"])
        intended.write_text(json.dumps(expected("f5-odd")))
        rejected = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(rejected.returncode, 2)
        self.assertIn("external expected-input mismatch", rejected.stderr)

    def test_strict_json_loading(self):
        p = Path(self.scratch.name)/"malformed.json"
        for text in ['{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}']:
            p.write_text(text)
            with self.assertRaises(ValueError): load(p)
        with p.open("wb") as f: f.truncate(16*1024*1024+1)
        with self.assertRaises(ValueError): load(p)


if __name__ == "__main__":
    unittest.main(verbosity=2)
