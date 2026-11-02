"""Full normalized-family software fixtures and general-model controls."""
import copy
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from check_curve_class_certificate import Field, family_models, nonsingular, normalize_model, orbit, transform_model, verify
from check_quotient_certificate import polynomial_mul


def expected(q, n):
    return {"prime": q, "degree": n, "modulus": [0, 1] if n == 1 else [1, 0, 1]}


def expanded_cubic(f, model, u, r):
    out = [0]*4
    a2, a4, a6 = model
    for i, coefficient in enumerate([a6, a4, a2, 1]):
        term = [coefficient]
        for _ in range(i):
            term = polynomial_mul(f, term, [r, f.mul(u, u)])
        for j, value in enumerate(term):
            out[j] = f.add(out[j], value)
    return out


class CurveClassTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-class-tests-")
        binary = str(Path(cls.scratch.name)/"classes")
        subprocess.run(["rustc", "--edition", "2021", str(Path(__file__).with_name("curve_class_certificate.rs")), "-o", binary], check=True)
        cls.records = {(q, n): json.loads(subprocess.check_output([binary, name])) for q, n, name in [(3, 1, "f3-classes"), (5, 1, "f5-classes"), (3, 2, "f9-classes")]}

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_complete_class_certificates(self):
        for (q, n), record in self.records.items():
            result = verify(record, expected(q, n))
            self.assertTrue(result["valid"])
        self.assertEqual(self.records[3, 1]["class_count"], 8)
        self.assertEqual(self.records[5, 1]["class_count"], 12)
        # Four characteristic-three j=0 classes, not a generic pair of twists.
        self.assertEqual(sum(row["representative"][0] == 0 for row in self.records[3, 1]["classes"]), 4)

    def test_general_model_normalization_and_full_action(self):
        for q, n in [(3, 1), (5, 1), (3, 2)]:
            record = self.records[q, n]
            f = Field(record["field"])
            index = {tuple(w["model"]): i for i, row in enumerate(record["classes"]) for w in row["members"]}
            # Every nonsingular long model normalizes into the certified universe.
            general = [m for m in itertools.product(range(f.size), repeat=3) if nonsingular(f, m)]
            for model in general:
                normalized, r = normalize_model(f, model)
                self.assertIn(normalized, index)
                self.assertEqual(expanded_cubic(f, model, 1, r), [normalized[2], normalized[1], normalized[0], 1])
            # Independent full affine-action partition at F3/F5, including all shifts.
            if n == 1:
                remaining = set(general)
                for row in record["classes"]:
                    rep = tuple(row["representative"])
                    full = {transform_model(f, rep, u, r) for u in range(1, f.size) for r in range(f.size)}
                    self.assertTrue(full <= remaining)
                    remaining -= full
                self.assertFalse(remaining)

    def test_witness_polynomial_identity_and_twists(self):
        for record in self.records.values():
            f = Field(record["field"])
            for row in record["classes"]:
                for w in row["members"]:
                    target = w["model"]
                    self.assertEqual(expanded_cubic(f, row["representative"], w["u"], w["r"]),
                                     [f.mul(f.power(w["u"], 6), c) for c in [target[2], target[1], target[0], 1]])
        record = self.records[5, 1]
        index = {tuple(w["model"]): i for i, row in enumerate(record["classes"]) for w in row["members"]}
        self.assertNotEqual(index[0, 1, 1], index[0, 4, 3])  # nonsquare2 quadratic twist

    def test_mutations_and_limits(self):
        def missing_class(r): r["classes"].pop(); r["class_count"] -= 1
        def duplicate_class(r): r["classes"][1] = r["classes"][0]
        def missing_member(r): next(c for c in r["classes"] if len(c["members"]) > 1)["members"].pop()
        def duplicate_member(r):
            c = next(c for c in r["classes"] if len(c["members"]) > 1); c["members"][1] = c["members"][0]
        def zero_scale(r): r["classes"][0]["members"][0]["u"] = 0
        def bad_shift(r):
            c = next(c for c in r["classes"] if c["representative"][0]); c["members"][0]["r"] = 1
        def singular_rep(r): r["classes"][0]["representative"] = [0, 0, 0]
        def bool_model(r): r["classes"][0]["representative"][0] = True
        def bad_domain(r): r["candidate_models"] -= 1
        def extra_key(r): r["classes"][0]["extra"] = 0
        for mutation in [missing_class, duplicate_class, missing_member, duplicate_member, zero_scale, bad_shift, singular_rep, bool_model, bad_domain, extra_key]:
            with self.subTest(mutation=mutation.__name__):
                r = copy.deepcopy(self.records[3, 2]); mutation(r)
                with self.assertRaises(ValueError): verify(r, expected(3, 2))
        with self.assertRaises(ValueError): verify(self.records[3, 2], expected(3, 2), model_limit=152)
        with self.assertRaises(ValueError): verify(self.records[3, 2], expected(3, 1))

    def test_cli_binding(self):
        certificate = Path(self.scratch.name)/"certificate.json"
        inputs = Path(self.scratch.name)/"field.json"
        certificate.write_text(json.dumps(self.records[3, 1])); inputs.write_text(json.dumps(expected(3, 1)))
        command = [sys.executable, str(Path(__file__).with_name("check_curve_class_certificate.py")), str(certificate), "--expected-field", str(inputs)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["classes"], 8)
        inputs.write_text(json.dumps(expected(5, 1)))
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("external field mismatch", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
