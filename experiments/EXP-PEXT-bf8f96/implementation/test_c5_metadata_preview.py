"""Complete curve/T binding and refusal checks for prospective C5 metadata."""

import copy
import json
from pathlib import Path
import unittest

from c5_metadata_preview import assemble
from c5_selection import select


class C5MetadataPreviewTests(unittest.TestCase):
    def setUp(self):
        published = Path(__file__).parent.parent / "inputs/join-plans-20261103/q5-n3.json"
        field = json.loads(published.read_text())["field"]
        self.plan = {"schema": "pext.join-plan/v1", "cohort": "fixture",
                     "field": field, "structures_per_T": 9,
                     "classes": [{"model": [0, 0, 1] if i == 2 else [0, 1, 1],
                                  "targets": [None, [i]]} for i in range(7)]}
        self.curves = []
        for i, entry in enumerate(self.plan["classes"]):
            units = []
            for t in range(2):
                ordinal = i*2+t
                witness = [3] if (i, t) == (4, 1) else []
                units.append({"T_index": t, "unit_name": f"u{ordinal:06d}",
                              "structures": 9,
                              "candidate_unit_sha256": f"{ordinal+1:064x}",
                              "type2_check_sha256": "a"*64,
                              "type2_hyperelliptic_ordinals": witness,
                              "hyperelliptic_predicate_true_count": len(witness),
                              "branch_type_mismatch_count": int((i, t) == (5, 0)),
                              "geometric_spectrum_violation_count": 0})
            self.curves.append({"cohort": "fixture", "class_index": i,
                                "model": entry["model"], "T_count": 2,
                                "units": units})

    def test_complete_preview_and_forced_review(self):
        preview = assemble(self.plan, self.curves)
        self.assertEqual(preview["unit_count"], 14)
        self.assertEqual(preview["rows"][2*4+1]["type2_hyperelliptic_ordinals"], [3])
        self.assertTrue(preview["rows"][2*5]["unit_counterexample"])
        self.assertEqual({r["descent_status"] for r in preview["rows"]}, {"unresolved"})
        with self.assertRaisesRegex(ValueError, "unresolved descent"):
            select(self.plan, preview["rows"])
        selected = select(self.plan, preview["rows"], preview=True)
        self.assertEqual(selected["status"], "incomplete_metadata_preview")
        by_slot = {(r["class_index"], r["T_index"]): r
                   for r in selected["selected_units"]}
        self.assertIn("type2_witness", by_slot[4, 1]["reasons"])
        self.assertIn("counterexample", by_slot[5, 0]["reasons"])
        self.assertIn("special_j", by_slot[2, 0]["reasons"])

    def test_missing_identity_or_type2_custody_refused(self):
        with self.assertRaisesRegex(ValueError, "complete join plan"):
            assemble(self.plan, self.curves[:-1])
        altered = copy.deepcopy(self.curves)
        altered[0]["units"][0]["unit_name"] = "u999999"
        with self.assertRaisesRegex(ValueError, "canonical slot"):
            assemble(self.plan, altered)
        altered = copy.deepcopy(self.curves)
        altered[4]["units"][1]["hyperelliptic_predicate_true_count"] = 0
        with self.assertRaisesRegex(ValueError, "witness count"):
            assemble(self.plan, altered)
        altered = copy.deepcopy(self.curves)
        altered[0]["units"][0]["candidate_unit_sha256"] = "0"
        with self.assertRaisesRegex(ValueError, "candidate unit SHA-256"):
            assemble(self.plan, altered)
        altered = copy.deepcopy(self.curves)
        altered[0]["units"][0]["type2_check_sha256"] = "b"*64
        with self.assertRaisesRegex(ValueError, "batch hash differs"):
            assemble(self.plan, altered)


if __name__ == "__main__":
    unittest.main(verbosity=2)
