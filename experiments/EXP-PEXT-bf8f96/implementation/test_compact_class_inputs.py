"""Compact coverage, independent arithmetic and malformed-input controls."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from check_compact_class_inputs import BasisField, Field, verify
from check_curve_class_certificate import transform_model
from legacy_class_bijection import check_rows, require_historical_field


class CompactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-compact-tests-")
        cls.binary = str(Path(cls.scratch.name)/"compact")
        subprocess.run(["rustc", "--edition", "2021", "-O", str(Path(__file__).with_name("compact_class_inputs.rs")), "-o", cls.binary], check=True)
        cls.records = {name: json.loads(subprocess.check_output([cls.binary, name])) for name in ["f3-control", "f5-control", "f9-control"]}

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_all_arithmetic_pairs(self):
        # Field-only preparation, no target curve inputs or scientific metrics.
        for name in ["f9-control", "q5-n3", "q3-n5"]:
            identity = json.loads(subprocess.check_output([self.binary, name, "--field-only"]))
            direct, fast = Field(identity), BasisField(identity)
            for a in range(direct.size):
                for b in range(direct.size):
                    self.assertEqual(fast.add(a, b), direct.add(a, b))
                    self.assertEqual(fast.sub(a, b), direct.sub(a, b))
                    self.assertEqual(fast.mul(a, b), direct.mul(a, b))
                if a:
                    self.assertEqual(fast.mul(a, fast.div(1, a)), 1)

    def test_complete_control_coverage(self):
        for name, record in self.records.items():
            result, _, captures = verify(record, name, capture_models=record["representatives"])
            self.assertTrue(result["valid"])
            self.assertEqual(len(captures), record["class_count"])
        self.assertEqual(self.records["f3-control"]["class_count"], 8)
        self.assertEqual(self.records["f5-control"]["class_count"], 12)

    def test_explicit_bijection_witnesses(self):
        record = self.records["f5-control"]
        f = BasisField(record["field"])
        reps = record["representatives"]
        originals = [list(transform_model(f, rep, 2, 1)) for rep in reps]
        rows = [{"historical_ordinal": i, "historical_model": model,
                 "class_index": i, "u": 2, "r": 1} for i, model in enumerate(originals)]
        check_rows(f, reps, originals, rows)
        for variant in ["shift", "duplicate", "model", "missing", "boolean"]:
            modified = copy.deepcopy(rows)
            if variant == "shift": modified[0]["r"] = 2
            if variant == "duplicate": modified[1]["class_index"] = 0
            if variant == "model": modified[0]["historical_model"] = originals[1]
            if variant == "missing": modified.pop()
            if variant == "boolean": modified[0]["class_index"] = False
            with self.assertRaises(ValueError): check_rows(f, reps, originals, modified)
        identity = json.loads(subprocess.check_output([self.binary, "q3-n5", "--field-only"]))
        require_historical_field(identity)
        identity["modulus"][1] = 1
        with self.assertRaises(ValueError): require_historical_field(identity)

    def test_mutations_and_limits(self):
        def missing(r): r["representatives"].pop(); r["class_count"] -= 1
        def duplicate(r): r["representatives"][1] = r["representatives"][0]
        def singular(r): r["representatives"][0] = [0, 0, 0]
        def wrong_family(r): r["representatives"][0] = [1, 1, 1]
        def boolean(r): r["representatives"][0][0] = True
        def count(r): r["normalized_models"] -= 1
        def domain(r): r["candidate_models"] -= 1
        def reorder(r): r["representatives"].reverse()
        def extra(r): r["extra"] = 1
        for mutation in [missing, duplicate, singular, wrong_family, boolean, count, domain, reorder, extra]:
            with self.subTest(mutation=mutation.__name__):
                record = copy.deepcopy(self.records["f9-control"]); mutation(record)
                with self.assertRaises(ValueError): verify(record, "f9-control")
        with self.assertRaises(ValueError): verify(self.records["f9-control"], "f9-control", model_limit=152)
        with self.assertRaises(ValueError): verify(self.records["f9-control"], "f3-control")
        with self.assertRaises(ValueError): verify(self.records["f9-control"], "f9-control", capture_models=[(0, 0, 0)])
        with self.assertRaises(ValueError): BasisField(self.records["f9-control"]["field"], size_limit=8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
