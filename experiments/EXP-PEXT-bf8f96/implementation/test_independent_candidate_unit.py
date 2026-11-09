"""Exact fixed F27 independent candidate-set replay and mutation rejection."""

import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from independent_candidate_unit import IndependentCandidateChecker


class IndependentCandidateUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-independent-candidate-")
        base = Path(__file__).parent
        binary = Path(cls.scratch.name) / "candidate_unit"
        subprocess.run(["rustc", "--edition=2021", str(base / "candidate_unit.rs"),
                        "-o", str(binary)], check=True, capture_output=True)
        cls.forms = [[1, 0, 1, 1, 0], [1, 1, 1, 0, 1]]
        cls.units = [json.loads(subprocess.check_output(
            [binary, "3", "3", ",".join(map(str, form)),
             "27", "819", "3276", "1000", "1000", "819"])) for form in cls.forms]
        cls.checker = IndependentCandidateChecker(cls.units[0]["field"])

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_both_actual_f27_software_forms(self):
        reports = [self.checker.verify(unit, form,
                   geometry_ordinals=[row[0] for row in unit["rows"]],
                   generic_ordinals=[unit["generic_intervals"][0][0]])
                   for unit, form in zip(self.units, self.forms)]
        self.assertEqual([row["exceptional"] for row in reports], [279, 1])
        self.assertEqual([row["generic_intervals"] for row in reports], [109, 1])
        self.assertEqual([row["geometry_checked"] for row in reports], [279, 1])
        self.assertEqual([row["generic_checked"] for row in reports], [1, 1])

    def test_mutations_are_refused(self):
        unit = self.units[0]
        sample = [unit["rows"][0][0]]
        removed = copy.deepcopy(unit)
        removed["rows"].pop()
        with self.assertRaisesRegex(ValueError, "exact exceptional ordinal set"):
            self.checker.verify(removed, self.forms[0])
        wrong_matrix = copy.deepcopy(unit)
        wrong_matrix["rows"][0][1][0] ^= 1
        with self.assertRaisesRegex(ValueError, "sampled matrix ordinal mismatch"):
            self.checker.verify(wrong_matrix, self.forms[0], geometry_ordinals=sample)
        wrong_interval = copy.deepcopy(unit)
        wrong_interval["generic_intervals"][0][1] += 1
        with self.assertRaisesRegex(ValueError, "generic complement intervals"):
            self.checker.verify(wrong_interval, self.forms[0])
        wrong_genus = copy.deepcopy(unit)
        wrong_genus["rows"][0][4] += 1
        with self.assertRaisesRegex(ValueError, "sampled candidate geometry mismatch"):
            self.checker.verify(wrong_genus, self.forms[0], geometry_ordinals=sample)
        missing_aa = copy.deepcopy(unit)
        missing_aa.pop("candidate_order_aa")
        with self.assertRaisesRegex(ValueError, "candidate identity"):
            self.checker.verify(missing_aa, self.forms[0])
        with self.assertRaisesRegex(ValueError, "external form binding"):
            self.checker.verify(unit, self.forms[1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
