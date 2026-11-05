"""Geometric reducer arithmetic on two fixed F27 software units."""

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from geometric_reducer import (curve_summary, expected_pattern,
                               genus_from_rank_and_support, load_type2_artifacts,
                               type2_unit_summary, type2_witness_ordinals,
                               unit_summary)


class GeometricReducerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-geometric-reducer-")
        source = Path(__file__).parent / "candidate_unit.rs"
        binary = Path(cls.scratch.name) / "candidate_unit"
        subprocess.run(["rustc", "--edition=2021", str(source), "-o", str(binary)],
                       check=True, capture_output=True)
        cls.units = []
        for form in ([1, 0, 1, 1, 0], [1, 1, 1, 0, 1]):
            args = [str(binary), "3", "3", ",".join(map(str, form)),
                    "27", "819", "3276", "1000", "1000", "819"]
            cls.units.append(json.loads(subprocess.check_output(args)))

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def summarize(self, index, unit=None):
        return unit_summary(self.units[index] if unit is None else unit, n=3,
                            target_count=2, t_index=index, expected_structures=819)

    def test_pattern_contract_and_rh(self):
        self.assertEqual([expected_pattern(count, index) for count, index in
                          ((1, 0), (2, 0), (2, 1), (4, 0), (4, 1))],
                         [[1, 3], [1, 1, 2], [4], [1, 1, 1, 1], [2, 2]])
        self.assertEqual(genus_from_rank_and_support(3, 12), 17)
        with self.assertRaisesRegex(ValueError, "nonintegral"):
            genus_from_rank_and_support(1, 5)

    def test_f27_spectrum_and_curve_matched_minima(self):
        first, second = self.summarize(0), self.summarize(1)
        self.assertEqual(sum(first["m_r_histogram"].values()), 819)
        self.assertEqual(sum(second["m_r_histogram"].values()), 819)
        self.assertEqual(first["m_r_histogram"].get("3,12"), first["generic"])
        self.assertEqual(first["factor_pattern"], [1, 1, 2])
        self.assertEqual(second["factor_pattern"], [4])
        self.assertEqual(first["spectrum"], [1, 9, 11, 13, 17])
        self.assertEqual(second["spectrum"], [1, 17])
        self.assertIsNone(first["geometric_spectrum_violation_count"])
        self.assertEqual(second["geometric_spectrum_violation_count"], 0)
        self.assertEqual((first["exceptional"], second["exceptional"]), (279, 1))
        first["T_index"], second["T_index"] = 0, 1
        curve = curve_summary("f27-software-fixture", 0, [0, 0], [first, second])
        self.assertEqual((curve["xline_geometric_minimum"],
                          curve["all_maps_geometric_minimum"]), (1, 1))
        self.assertFalse(curve["strict_geometric_minimum_drop"])

    def test_mutations_and_missing_t_refused(self):
        bad = copy.deepcopy(self.units[1])
        bad["rows"][0][4] += 1
        with self.assertRaisesRegex(ValueError, "Riemann-Hurwitz"):
            self.summarize(1, bad)
        bad = copy.deepcopy(self.units[0])
        bad["generic_intervals"][0][1] += 1
        with self.assertRaisesRegex(ValueError, "generic complement"):
            self.summarize(0, bad)
        bad = copy.deepcopy(self.units[1])
        bad["factor_pattern"] = [2, 2]
        self.assertEqual(self.summarize(1, bad)["branch_type_mismatch_count"], 1)
        first = self.summarize(0)
        first["T_index"] = 0
        with self.assertRaisesRegex(ValueError, "incomplete canonical T"):
            curve_summary("f27-software-fixture", 0, [0, 0], [first, first])

    def test_type2_exact_curve_t_join_and_digest_refusal(self):
        unit = self.units[0]
        row = unit["rows"][0]
        slot = {"name": "u000000", "class_index": 0, "T_index": 0}
        review = {"raw_sha256": "a"*64,
                  "type2_counts": {"exceptional_checked": len(unit["rows"]),
                                   "type2_signature_count": 1,
                                   "hyperelliptic_predicate_true_count": 1,
                                   "hyperelliptic_predicate_false_count": 0}}
        signature = {"unit_name": slot["name"], "class_index": 0, "T_index": 0,
                     "raw_sha256": review["raw_sha256"], "ordinal": row[0],
                     "matrix": row[1], "hyperelliptic_predicate": True,
                     "alpha_choices_checked": 1}
        self.assertEqual(type2_unit_summary(unit, review, slot, [signature]),
                         review["type2_counts"])
        second_row = unit["rows"][1]
        second = dict(signature, ordinal=second_row[0], matrix=second_row[1],
                      hyperelliptic_predicate=False)
        review_two = copy.deepcopy(review)
        review_two["type2_counts"].update(type2_signature_count=2,
                                           hyperelliptic_predicate_false_count=1)
        counts, witnesses = type2_witness_ordinals(
            unit, review_two, slot, [signature, second])
        self.assertEqual(counts["type2_signature_count"], 2)
        self.assertEqual(witnesses, [row[0]])
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            type2_witness_ordinals(unit, review_two, slot, [signature, signature])
        bad = dict(signature, matrix=[0, 0, 0, 0])
        with self.assertRaisesRegex(ValueError, "sealed exceptional"):
            type2_unit_summary(unit, review, slot, [bad])
        summarized = dict(self.summarize(0), T_index=0, **review["type2_counts"])
        curve = curve_summary("fixture", 0, [0], [summarized])
        self.assertEqual(curve["hyperelliptic_predicate_true_count"], 1)
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            rows = (json.dumps(signature, sort_keys=True) + "\n").encode()
            reviews = b"fixture-review\n"
            summary = {"schema": "pext.type2-batch-check/v1", "valid": True,
                       "cohort": "fixture", "join_plan_sha256": "b"*64,
                       "binary_sha256": "c"*64,
                       "candidate_reviews_sha256": hashlib.sha256(reviews).hexdigest(),
                       "type2_rows_sha256": hashlib.sha256(rows).hexdigest(),
                       "unit_count": 1, "exceptional_checked": len(unit["rows"]),
                       "signature_count": 1, "hyperelliptic_predicate_true_count": 1,
                       "hyperelliptic_predicate_false_count": 0,
                       "status": "full_independent_exceptional_scan"}
            summary_bytes = json.dumps(summary).encode()
            (root / "type2-rows.jsonl").write_bytes(rows)
            (root / "type2-check.json").write_bytes(summary_bytes)
            check = {"type2_check_sha256": hashlib.sha256(summary_bytes).hexdigest()}
            loaded, partition = load_type2_artifacts(
                root, "fixture", "b"*64, "c"*64, check, reviews, [slot], 3)
            self.assertEqual((loaded["signature_count"], len(partition[slot["name"]])), (1, 1))
            (root / "type2-rows.jsonl").write_bytes(rows + b"\n")
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                load_type2_artifacts(root, "fixture", "b"*64, "c"*64,
                                     check, reviews, [slot], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
