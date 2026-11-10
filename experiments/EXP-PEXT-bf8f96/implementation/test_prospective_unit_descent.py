"""Fixed F27 full-row prospective component summary and mutation checks."""

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from check_prospective_unit_descent import verify
from generic_interval_descent import certify_from_checked_review
from independent_candidate_unit import IndependentCandidateChecker
from prospective_unit_descent import summarize


class ProspectiveUnitDescentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-prospective-unit-")
        binary = Path(cls.scratch.name) / "candidate_unit"
        subprocess.run(["rustc", "--edition=2021",
                        str(Path(__file__).with_name("candidate_unit.rs")),
                        "-o", str(binary)], check=True, capture_output=True)
        cls.form = [1, 0, 1, 1, 0]
        cls.raw = subprocess.check_output(
            [str(binary), "3", "3", ",".join(map(str, cls.form)),
             "27", "819", "3276", "1000", "1000", "819"])
        cls.unit = json.loads(cls.raw)
        cls.binding = {"schema": "pext.candidate-binding/v1",
                       "experiment": "EXP-PEXT-bf8f96", "cohort": "f27-software-fixture",
                       "class_index": 0, "T_index": 0,
                       "model": {"fixture": True}, "target": None,
                       "field": cls.unit["field"], "quotient_form": cls.form,
                       "input_sha256": "a"*64, "manifest_sha256": "b"*64,
                       "join_plan_sha256": "c"*64,
                       "structure_offset": 0, "structure_end_exclusive": 819,
                       "structures_per_T": 819}
        checker = IndependentCandidateChecker(cls.unit["field"])
        ordinals = [row[0] for row in cls.unit["rows"]]
        generic_ordinals = [cls.unit["generic_intervals"][0][0]]
        independent = checker.verify(cls.unit, cls.form,
                                     geometry_ordinals=ordinals,
                                     generic_ordinals=generic_ordinals)
        generic = certify_from_checked_review(
            cls.unit, cls.binding, checker, independent,
            hashlib.sha256(cls.raw).hexdigest())
        cls.review = {"raw_sha256": hashlib.sha256(cls.raw).hexdigest(),
                      "geometry_ordinals": ordinals,
                      "generic_ordinals": generic_ordinals,
                      "independent": independent, "generic_descent": generic}

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_complete_fixture_summary_and_independent_replay(self):
        record = summarize(self.raw, self.binding, self.review)
        checked = verify(record, self.raw, self.binding, self.review)
        self.assertTrue(checked["valid"])
        self.assertEqual((record["exceptional_count"], record["generic_count"],
                          record["covered_count"]), (279, 540, 819))
        self.assertEqual((record["connected_exceptional_count"],
                          record["disconnected_exceptional_count"],
                          record["prospective_connected_genus_minimum"]), (279, 0, 1))
        self.assertEqual(record["descent_status"], "unresolved")
        self.assertEqual(sum(row["count"] for row in record["exceptional_rank_pairs"]), 279)

    def test_mutated_summary_review_and_square_class_rejected(self):
        record = summarize(self.raw, self.binding, self.review)
        changed = copy.deepcopy(record)
        changed["connected_exceptional_count"] -= 1
        with self.assertRaisesRegex(ValueError, "summary differs"):
            verify(changed, self.raw, self.binding, self.review)
        partial = copy.deepcopy(self.review)
        partial["independent"]["arithmetic_checked"] -= 1
        with self.assertRaisesRegex(ValueError, "complete independent review"):
            summarize(self.raw, self.binding, partial)
        with self.assertRaisesRegex(ValueError, "full independent review"):
            verify(record, self.raw, self.binding, partial)
        tampered_unit = copy.deepcopy(self.unit)
        tampered_unit["exceptional_squareclasses"][0] = [2, True]
        raw = json.dumps(tampered_unit).encode()
        with self.assertRaisesRegex(ValueError, "raw|arithmetic|certificate"):
            verify(record, raw, self.binding, self.review)
        bad_generic = copy.deepcopy(self.review)
        bad_generic["generic_descent"]["generic_intervals_sha256"] = "0"*64
        with self.assertRaisesRegex(ValueError, "generic descent certificate differs"):
            verify(record, self.raw, self.binding, bad_generic)


if __name__ == "__main__":
    unittest.main(verbosity=2)
