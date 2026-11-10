"""Fixed F27 theorem application and adversarial certificate mutations."""

import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from check_generic_interval_descent import verify
from geometric_reducer import unit_summary
from generic_interval_descent import certify, certify_from_checked_review
from independent_candidate_unit import IndependentCandidateChecker


class GenericIntervalDescentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-generic-descent-")
        binary = Path(cls.scratch.name) / "candidate_unit"
        subprocess.run(["rustc", "--edition=2021",
                        str(Path(__file__).with_name("candidate_unit.rs")),
                        "-o", str(binary)], check=True, capture_output=True)
        cls.form = [1, 0, 1, 1, 0]
        cls.raw = subprocess.check_output(
            [str(binary), "3", "3", ",".join(map(str, cls.form)),
             "27", "819", "3276", "1000", "1000", "819"])
        cls.unit = json.loads(cls.raw)
        cls.checker = IndependentCandidateChecker(cls.unit["field"])
        # Deliberately fixture-only: q3-n3 is not a published census cohort.
        cls.binding = {"schema": "pext.candidate-binding/v1",
                       "experiment": "EXP-PEXT-bf8f96", "cohort": "f27-software-fixture",
                       "class_index": 0, "T_index": 0,
                       "model": {"fixture": True}, "target": None,
                       "field": cls.unit["field"], "quotient_form": cls.form,
                       "input_sha256": "a"*64, "manifest_sha256": "b"*64,
                       "join_plan_sha256": "c"*64,
                       "structure_offset": 0, "structure_end_exclusive": 819,
                       "structures_per_T": 819}

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_exact_full_complement_and_coefficient_orbit(self):
        record = certify(self.unit, self.binding, self.checker, self.raw)
        checked = verify(record, self.raw, self.binding)
        self.assertTrue(checked["valid"])
        self.assertEqual((record["independent_exceptional_count"],
                          record["generic_count"], record["generic_interval_count"]),
                         (279, 540, 109))
        self.assertEqual((record["geometric_rank"], record["arithmetic_rank"],
                          record["genus"]), (3, 3, 17))
        self.assertEqual(record["scope"], "generic_complement_only")
        self.assertEqual(record["premises"]["radical_action_order"], 3)
        self.assertIn("collision_completeness_review", record["status"])
        reviewed = self.checker.verify(self.unit, self.form)
        from_review = certify_from_checked_review(
            self.unit, self.binding, self.checker, reviewed,
            record["candidate_raw_sha256"])
        self.assertEqual(from_review, record)

    def test_mutated_coverage_coefficients_and_provenance_refused(self):
        record = certify(self.unit, self.binding, self.checker, self.raw)
        for key, changed_value in (("genus", 1), ("arithmetic_rank", 2),
                                   ("descends_to_base_field", False),
                                   ("candidate_raw_sha256", "0"*64),
                                   ("join_plan_sha256", "0"*64),
                                   ("T_index", 1)):
            changed = copy.deepcopy(record)
            changed[key] = changed_value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "certificate differs"):
                verify(changed, self.raw, self.binding)
        missing = copy.deepcopy(self.unit)
        missing["rows"].pop()
        with self.assertRaisesRegex(ValueError, "exact exceptional ordinal set"):
            verify(record, json.dumps(missing).encode(), self.binding)
        interval = copy.deepcopy(self.unit)
        interval["generic_intervals"][0][1] += 1
        with self.assertRaisesRegex(ValueError, "generic complement intervals"):
            verify(record, json.dumps(interval).encode(), self.binding)
        changed_binding = copy.deepcopy(self.binding)
        changed_binding["quotient_form"][0] = 2
        with self.assertRaisesRegex(ValueError, "external candidate binding"):
            verify(record, self.raw, changed_binding)
        changed_binding = copy.deepcopy(self.binding)
        changed_binding["join_plan_sha256"] = "0"*64
        with self.assertRaisesRegex(ValueError, "certificate differs"):
            verify(record, self.raw, changed_binding)
        incomplete = copy.deepcopy(self.binding)
        incomplete.pop("manifest_sha256")
        with self.assertRaisesRegex(ValueError, "external candidate binding incomplete"):
            verify(record, self.raw, incomplete)
        with self.assertRaisesRegex(ValueError, "incomplete external candidate binding"):
            certify_from_checked_review(
                self.unit, incomplete, self.checker,
                self.checker.verify(self.unit, self.form),
                record["candidate_raw_sha256"])
        # Byte mutations are refused even if they decode to the same JSON value.
        with self.assertRaisesRegex(ValueError, "certificate differs"):
            verify(record, self.raw + b" ", self.binding)

    def test_reducer_refuses_tampered_certificate_before_curve_row(self):
        record = certify(self.unit, self.binding, self.checker, self.raw)
        review = {"raw_sha256": record["candidate_raw_sha256"],
                  "independent": self.checker.verify(self.unit, self.form),
                  "generic_descent": record}
        summary = unit_summary(
            self.unit, n=3, target_count=1, t_index=0, expected_structures=819,
            generic_binding=self.binding, generic_review=review,
            raw_sha256=record["candidate_raw_sha256"])
        self.assertEqual(summary["generic_descent"]["generic_count"], 540)
        tampered = copy.deepcopy(review)
        tampered["generic_descent"]["generic_intervals_sha256"] = "0"*64
        with self.assertRaisesRegex(ValueError, "generic descent certificate differs"):
            unit_summary(self.unit, n=3, target_count=1, t_index=0,
                         expected_structures=819, generic_binding=self.binding,
                         generic_review=tampered,
                         raw_sha256=record["candidate_raw_sha256"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
