"""Type2 length-six signature and separate trace-zero witness controls."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from check_compact_class_inputs import BasisField
from type2_predicate import inspect


class Type2PredicateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-type2-")
        binary = Path(cls.scratch.name) / "candidate_unit"
        subprocess.run(["rustc", "--edition=2021", str(Path(__file__).with_name(
            "candidate_unit.rs")), "-o", str(binary)], check=True, capture_output=True)
        forms = {"positive": [20, 0, 22, 0, 1],
                 "negative": [13, 6, 0, 8, 1],
                 "other22": [6, 0, 7, 0, 1],
                 "irreducible4": [1, 1, 1, 0, 1]}
        cls.units = {}
        for name, form in forms.items():
            args = [str(binary), "3", "3", ",".join(map(str, form)),
                    "27", "819", "3276", "1000", "1000", "819"]
            cls.units[name] = json.loads(subprocess.check_output(args))
        cls.field = BasisField(cls.units["positive"]["field"])

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_type2_positive_and_negative_trace_zero_predicate(self):
        positive = inspect(self.field, self.units["positive"], [1, 0, 0, 1])
        negative = inspect(self.field, self.units["negative"], [1, 0, 0, 1])
        self.assertTrue(positive["signature"])
        self.assertTrue(positive["hyperelliptic_predicate"])
        self.assertEqual(positive["trace_zero_matrix"], [1, 0, 0, 2])
        self.assertTrue(negative["signature"])
        self.assertFalse(negative["hyperelliptic_predicate"])
        self.assertIsNone(negative["trace_zero_matrix"])
        self.assertEqual(negative["base_matrix_pair_space_per_choice"], 9)
        self.assertGreaterEqual(negative["alpha_choices_checked"], 1)

    def test_base_field_projective_transport_and_other_patterns(self):
        moved = inspect(self.field, self.units["positive"], [1, 1, 0, 1])
        self.assertTrue(moved["signature"])
        self.assertTrue(moved["hyperelliptic_predicate"])
        other = inspect(self.field, self.units["other22"], [1, 0, 0, 1])
        self.assertFalse(other["signature"])
        self.assertIsNone(other["hyperelliptic_predicate"])
        irreducible = inspect(self.field, self.units["irreducible4"], [1, 0, 0, 1])
        self.assertFalse(irreducible["signature"])
        self.assertEqual(irreducible["status"], "checked_non_type2_factor_pattern")

    def test_bad_branch_certificate_and_matrix_refused(self):
        bad = dict(self.units["positive"])
        bad["roots"] = list(bad["roots"])
        bad["roots"][0] = [0, 0]
        with self.assertRaisesRegex(ValueError, "root off quartic|incomplete factor root orbit"):
            inspect(self.field, bad, [1, 0, 0, 1])
        with self.assertRaises(ValueError):
            inspect(self.field, self.units["positive"], [1, 0, 0, 0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
