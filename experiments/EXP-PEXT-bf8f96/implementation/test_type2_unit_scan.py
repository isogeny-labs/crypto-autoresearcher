"""Full independent exceptional-row Type2 scan on fixed F27 units."""

import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from check_compact_class_inputs import BasisField
from independent_candidate_unit import IndependentCandidateChecker
from type2_unit_scan import scan


class Type2UnitScanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-type2-scan-")
        binary = Path(cls.scratch.name) / "candidate_unit"
        subprocess.run(["rustc", "--edition=2021", str(Path(__file__).with_name(
            "candidate_unit.rs")), "-o", str(binary)], check=True, capture_output=True)
        cls.units = []
        for form in ([20, 0, 22, 0, 1], [13, 6, 0, 8, 1], [6, 0, 7, 0, 1]):
            args = [str(binary), "3", "3", ",".join(map(str, form)),
                    "27", "819", "3276", "1000", "1000", "819"]
            cls.units.append(json.loads(subprocess.check_output(args)))
        cls.field = BasisField(cls.units[0]["field"])
        cls.checker = IndependentCandidateChecker(cls.units[0]["field"])

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def review(self, unit):
        ordinals = [row[0] for row in unit["rows"]]
        independent = self.checker.verify(unit, unit["form"], geometry_ordinals=ordinals)
        return {"independent": independent, "geometry_ordinals": ordinals}

    def test_full_checked_unit_cross_tabs(self):
        expected = [(6, 2), (8, 0), (6, 2)]
        for unit, (signatures, positives) in zip(self.units, expected):
            result = scan(self.field, unit, self.review(unit))
            self.assertEqual(result["type2_signature_count"], signatures)
            self.assertEqual(result["hyperelliptic_predicate_true_count"], positives)
            self.assertEqual(result["hyperelliptic_predicate_false_count"], signatures-positives)
            self.assertEqual(result["exceptional_checked"], unit["exceptional"])
            self.assertEqual(result["generic_excluded_by_orbit_overlap"], unit["generic"])
            self.assertEqual(len({row["ordinal"] for row in result["signature_rows"]}), signatures)

    def test_partial_review_refused(self):
        unit = self.units[0]
        review = self.review(unit)
        broken = copy.deepcopy(review)
        broken["geometry_ordinals"].pop()
        with self.assertRaisesRegex(ValueError, "full independently checked"):
            scan(self.field, unit, broken)
        broken = copy.deepcopy(review)
        broken["independent"]["geometry_checked"] -= 1
        with self.assertRaisesRegex(ValueError, "full independently checked"):
            scan(self.field, unit, broken)


if __name__ == "__main__":
    unittest.main(verbosity=2)
