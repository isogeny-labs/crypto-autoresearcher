"""Fixed finite-group partition controls; no curve census or genus measurements."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from check_structure_certificate import Field, cocycle, inverse, multiply, normalize, transform, verify

FORMS = [[1, 1, 0, 1, 0], [2, 2, 0, 2, 0]]


def expected(n):
    return {"field": {"prime": 3, "degree": n, "modulus": [0, 1] if n == 1 else [1, 2, 0, 1]}, "forms": FORMS}


class StructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-structure-tests-")
        binary = str(Path(cls.scratch.name)/"fixtures")
        subprocess.run(["rustc", "--edition", "2021", str(Path(__file__).with_name("structure_certificate.rs")), "-o", binary], check=True)
        cls.records = {n: json.loads(subprocess.check_output([binary, name])) for n, name in [(1, "f3-identity"), (3, "f27-structures")]}

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_complete_certificates(self):
        for n, count in [(1, 1), (3, 819)]:
            self.assertEqual(verify(self.records[n], expected(n))["structures"], count)

    def test_exhaustive_group_partition(self):
        """Brute normalized PGL2(F27) is exactly disjoint union H*N."""
        record = self.records[3]
        f = Field(record["field"])
        def group(elements):
            for b in elements:
                for c in elements:
                    for d in elements:
                        if d != f.mul(b, c):
                            yield [1, b, c, d]
            for c in elements:
                if c:
                    for d in elements:
                        yield [0, 1, c, d]
        whole = {tuple(m) for m in group(range(27))}
        subgroup = list(group(range(3)))
        self.assertEqual(len(whole), 19656)
        self.assertEqual(len(subgroup), 24)
        covered = set()
        for row in record["structures"]:
            orbit = {tuple(normalize(f, multiply(f, h, row["matrix"]))) for h in subgroup}
            self.assertEqual(len(orbit), 24)
            self.assertFalse(covered & orbit)
            covered |= orbit
        self.assertEqual(covered, whole)

    def test_wrong_orientation_and_scalar_controls(self):
        f = Field(self.records[3]["field"])
        for index in [0, 1, 12, 13, 50, 116, 117, 400, 818]:
            row = self.records[3]["structures"][index]
            m = row["matrix"]
            # Pullback identity G_N(N(X,Z))=det(N)^4 F(X,Z).
            adj = [m[3], f.sub(0, m[1]), f.sub(0, m[2]), m[0]]
            det = f.sub(f.mul(m[0], m[3]), f.mul(m[1], m[2]))
            for form, transformed in zip(FORMS, row["transformed_forms"]):
                self.assertEqual(transform(f, transformed, adj), [f.mul(v, f.power(det, 4)) for v in form])
        r = copy.deepcopy(self.records[3])
        def reversed_orientation(m):
            return normalize(f, multiply(f, m, inverse(f, [f.power(v, f.p) for v in m])))
        row = next(row for row in r["structures"] if reversed_orientation(row["matrix"]) != row["cocycle"])
        row["cocycle"] = reversed_orientation(row["matrix"])
        with self.assertRaises(ValueError): verify(r, expected(3))
        r = copy.deepcopy(self.records[3])
        # Multiplying an entire form by nonsquare2 is not a harmless monic normalization.
        r["structures"][0]["transformed_forms"][0] = [f.mul(2, x) for x in r["structures"][0]["transformed_forms"][0]]
        with self.assertRaises(ValueError): verify(r, expected(3))

    def test_cli_binding(self):
        certificate = Path(self.scratch.name)/"certificate.json"
        inputs = Path(self.scratch.name)/"expected.json"
        certificate.write_text(json.dumps(self.records[1]))
        inputs.write_text(json.dumps(expected(1)))
        command = [sys.executable, str(Path(__file__).with_name("check_structure_certificate.py")),
                   str(certificate), "--expected-input", str(inputs)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["structures"], 1)
        inputs.write_text(json.dumps(expected(3)))
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("expected field mismatch", result.stderr)

    def test_mutations_and_limits(self):
        def missing(r): r["structures"].pop()
        def duplicate(r): r["structures"][1] = r["structures"][0]
        def singular(r): r["structures"][0]["matrix"] = [1, 1, 1, 1]
        def bool_count(r): r["count"] = True
        def bool_form(r): r["forms"][0][0] = True
        def wrong_form(r): r["structures"][0]["transformed_forms"][0][0] = 2
        def extra_key(r): r["structures"][0]["extra"] = 0
        for mutation in [missing, duplicate, singular, bool_count, bool_form, wrong_form, extra_key]:
            with self.subTest(mutation=mutation.__name__):
                record = copy.deepcopy(self.records[3]); mutation(record)
                with self.assertRaises(ValueError): verify(record, expected(3))
        with self.assertRaises(ValueError): verify(self.records[3], expected(3), structure_limit=818)
        with self.assertRaises(ValueError): verify(self.records[3], expected(1))


if __name__ == "__main__":
    unittest.main(verbosity=2)
