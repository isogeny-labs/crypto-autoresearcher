"""Prospective C5 roster coverage and forced-witness selection."""

import copy
import json
from pathlib import Path
import unittest

from c5_selection import select


class C5SelectionTests(unittest.TestCase):
    def setUp(self):
        published = Path(__file__).parent.parent / "inputs/join-plans-20261103/q5-n3.json"
        field = json.loads(published.read_text())["field"]
        self.plan = {"schema": "pext.join-plan/v1", "cohort": "fixture",
                     "field": field, "structures_per_T": 9,
                     "classes": [{"model": [0, 0, 1] if i == 2 else [0, 1, 1],
                                  "targets": [None, [i]]} for i in range(7)]}
        self.metadata = [{"cohort": "fixture", "class_index": i, "T_index": t,
                          "torsion_count": 2, "descent_status": "certified_admissible",
                          "special_j": i == 2, "unit_counterexample": False,
                          "curve_counterexample": False, "counterexample_ordinals": [],
                          "type2_hyperelliptic_ordinals": [],
                          "candidate_unit_sha256": "a"*64}
                         for i in range(7) for t in range(2)]

    def test_canonical_strata_and_forced_rows(self):
        self.metadata[2*5]["counterexample_ordinals"] = [1, 8]
        self.metadata[2*4+1]["type2_hyperelliptic_ordinals"] = [3]
        self.metadata[2*6]["curve_counterexample"] = True
        self.metadata[2*6+1]["curve_counterexample"] = True
        roster = select(self.plan, self.metadata)
        self.assertEqual(roster["unit_count"], 14)
        self.assertEqual(roster["stratum_count"], 2)
        picked = {(r["class_index"], r["T_index"]): r
                  for r in roster["selected_units"]}
        self.assertEqual(set(picked), {(i, t) for i in (0, 2, 3, 4, 5, 6)
                                       for t in (0, 1)} - {(4, 0), (5, 1)})
        self.assertIn("middle_in_stratum", picked[3, 0]["reasons"])
        self.assertIn("special_j", picked[2, 1]["reasons"])
        self.assertEqual(picked[5, 0]["counterexample_ordinals"], [1, 8])
        self.assertEqual(picked[4, 1]["type2_hyperelliptic_ordinals"], [3])
        self.assertIn("counterexample", picked[6, 1]["reasons"])

    def test_incomplete_or_misaligned_metadata_refused(self):
        with self.assertRaisesRegex(ValueError, "cover every"):
            select(self.plan, self.metadata[:-1])
        swapped = copy.deepcopy(self.metadata)
        swapped[0], swapped[1] = swapped[1], swapped[0]
        with self.assertRaisesRegex(ValueError, "identity"):
            select(self.plan, swapped)
        inconsistent = copy.deepcopy(self.metadata)
        inconsistent[2*2+1]["special_j"] = False
        with self.assertRaisesRegex(ValueError, "special-j"):
            select(self.plan, inconsistent)
        hidden = copy.deepcopy(self.metadata)
        hidden[2*2]["special_j"] = False
        hidden[2*2+1]["special_j"] = False
        with self.assertRaisesRegex(ValueError, "published curve model"):
            select(self.plan, hidden)
        inconsistent = copy.deepcopy(self.metadata)
        inconsistent[2*2+1]["curve_counterexample"] = True
        with self.assertRaisesRegex(ValueError, "curve counterexample"):
            select(self.plan, inconsistent)
        duplicate = copy.deepcopy(self.metadata)
        duplicate[0]["counterexample_ordinals"] = [1, 1]
        with self.assertRaisesRegex(ValueError, "sorted unique"):
            select(self.plan, duplicate)


if __name__ == "__main__":
    unittest.main(verbosity=2)
