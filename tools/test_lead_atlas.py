#!/usr/bin/env python3
"""Tests for the ECDLP lead atlas (knowledge/leads/ecdlp/, tools/lead_atlas.py).

Counts are floors: the atlas grows, and an exact count would fail on every
branch that adds a lead.
"""
from __future__ import annotations

import copy
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lead_atlas as la  # noqa: E402
import build_frontier_map as bfm  # noqa: E402
import validate_ledger as vl  # noqa: E402

FLOOR_PER_FAMILY = 3


class AtlasTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = la.load_leads()

    def test_committed_rows_pass_the_check(self) -> None:
        errors, _warnings = la.check_leads(self.rows)
        self.assertEqual(errors, [])

    def test_every_family_is_populated(self) -> None:
        for fam in la.FAMILIES:
            with self.subTest(fam):
                self.assertGreaterEqual(
                    sum(r.get("family") == fam for r in self.rows),
                    FLOOR_PER_FAMILY)

    def test_closure_without_obstruction_fails(self) -> None:
        row = copy.deepcopy(next(r for r in self.rows
                                 if r["disposition"] in la.CLOSED))
        row.pop("obstruction")
        errors, _ = la.check_leads([row])
        self.assertTrue(any("requires an obstruction" in e for e in errors))

    def test_open_lead_without_next_step_fails(self) -> None:
        row = copy.deepcopy(next(r for r in self.rows
                                 if r["disposition"] in la.OPEN))
        row.pop("next_action", None)
        errors, _ = la.check_leads([row])
        self.assertTrue(any("next_action.step" in e for e in errors))

    def test_inherited_revisit_requires_complete_obstruction(self) -> None:
        row = copy.deepcopy(next(r for r in self.rows
                                 if r["disposition"] in la.OPEN))
        row["next_action"] = {"from_revisit_when": True}
        row.pop("obstruction", None)
        errors, _ = la.check_leads([row])
        self.assertTrue(any("requires an obstruction block" in e
                            for e in errors))

    def test_inherited_revisit_and_explicit_step_are_exclusive(self) -> None:
        row = copy.deepcopy(next(r for r in self.rows
                                 if (r.get("next_action") or {}).get(
                                     "from_revisit_when")))
        row["next_action"]["step"] = "ambiguous action"
        errors, _ = la.check_leads([row])
        self.assertTrue(any("cannot combine step" in e for e in errors))

    def test_unknown_ledger_ref_fails(self) -> None:
        row = copy.deepcopy(self.rows[0])
        row["ledger_refs"] = ["H-NOPE-000000"]
        errors, _ = la.check_leads([row])
        self.assertTrue(any("H-NOPE-000000" in e for e in errors))

    def test_coverage_has_no_dangling_lead(self) -> None:
        self.assertEqual(la.coverage_report(self.rows)["dangling"], [])

    def test_match_finds_the_frobenius_factor_base_lead(self) -> None:
        """The GGMP re-derivation (DEC-20260916-3c0cf5) must hit a lead."""
        hits = la.match("Frobenius-invariant factor base for Koblitz subfield "
                        "curve index calculus")
        self.assertTrue(hits)
        self.assertTrue(any(h[1].startswith("LEAD-ICB-") for h in hits[:3]),
                        hits[:3])

    def test_brief_never_raises(self) -> None:
        self.assertIn("lead atlas", la.brief())

    def test_render_lists_every_lead(self) -> None:
        text = la.render(self.rows)
        for r in self.rows:
            self.assertIn(r["id"], text)

    def test_only_scoped_obstructions_leave_pursuit_queue(self) -> None:
        pursued = {r["id"] for r in la.pursuit_rows(self.rows)}
        for row in self.rows:
            with self.subTest(row=row["id"]):
                self.assertEqual(row["id"] in pursued,
                                 row["disposition"] != "closed_obstructed")

    def test_closed_non_obstruction_uses_revisit_trigger(self) -> None:
        row = next(r for r in self.rows if r["disposition"] in
                   ("closed_known", "closed_dominated", "exhausted_at_scale"))
        self.assertTrue(la.is_pursued(row))
        self.assertIn(str(row["obstruction"]["revisit_when"]),
                      la.pursuit_action(row))

    def test_render_excludes_only_obstructed_from_pursuit_section(self) -> None:
        text = la.render(self.rows)
        section = text.split("## Pursuit queue", 1)[1].split("\n## ", 1)[0]
        for row in self.rows:
            with self.subTest(row=row["id"]):
                self.assertEqual(f"| `{row['id']}` " in section,
                                 row["disposition"] != "closed_obstructed")

    def test_reopened_family_rows_render_the_inherited_action(self) -> None:
        row = next(r for r in self.rows
                   if (r.get("next_action") or {}).get("from_revisit_when"))
        text = la.render(self.rows)
        family = text.split(f"## {row['family']}", 1)[1].split(
            "\n## ", 1)[0]
        rendered = next(line for line in family.splitlines()
                        if line.startswith(f"| `{row['id']}` "))
        self.assertIn(la._one(row["obstruction"]["revisit_when"]), rendered)

    def test_pursuit_action_is_not_markdown_escaped(self) -> None:
        row = copy.deepcopy(next(r for r in self.rows
                                 if r["disposition"] in la.OPEN))
        row["next_action"] = {"step": "chain | tree"}
        self.assertEqual(la.pursuit_action(row), "chain | tree")

    def test_conditional_jksst_result_does_not_close_uncovered_lifts(self) -> None:
        by_id = {row["id"]: row for row in self.rows}
        for lead_id in (
                "LEAD-TRF-global-lift-small-height",
                "LEAD-ICP-char0-lifting-xedni-smoothness"):
            with self.subTest(lead=lead_id):
                row = by_id[lead_id]
                self.assertEqual(row["disposition"], "open_next_step")
                self.assertTrue(row["next_action"]["from_revisit_when"])
                self.assertTrue(la.is_pursued(row))

        kr = next(row for row in bfm.load_rows()
                  if row["id"] == "KR-IC-cd159a")
        self.assertIn("conditional", kr["title"].lower())
        self.assertIn("not an unconditional", kr["claim"].lower())

        cm = by_id["LEAD-TRF-cm-canonical-lift-heights"]
        self.assertEqual(cm["disposition"], "closed_obstructed")
        statement = cm["obstruction"]["statement"]
        self.assertIn("fixed arity", statement)
        self.assertIn("target-dependent arbitrary set-section", statement)


class TierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = la.load_leads()
        self.base = copy.deepcopy(self.rows[0])
        for k in ("tier", "tier_evidence", "status", "best_measured"):
            self.base.pop(k, None)

    def test_default_is_zero_and_untiered(self) -> None:
        self.assertEqual(la.tier_of(self.base), (0, True))
        self.base["tier"] = 0
        self.assertEqual(la.tier_of(self.base), (0, False))

    def test_parse_tier(self) -> None:
        self.base["tier"] = 2
        self.assertEqual(la.tier_of(self.base), (2, False))

    def test_invalid_tier_and_missing_evidence_fail(self) -> None:
        bad = copy.deepcopy(self.base)
        bad["tier"] = 7
        errors, _ = la.check_leads([bad])
        self.assertTrue(any("tier must be" in e for e in errors))
        bad["tier"] = 2
        errors, _ = la.check_leads([bad])
        self.assertTrue(any("requires tier_evidence" in e for e in errors))
        bad["tier_evidence"] = {2: "some/path"}
        errors, _ = la.check_leads([bad])
        self.assertFalse(any("tier" in e for e in errors))

    def test_tiers_table(self) -> None:
        a, b = copy.deepcopy(self.base), copy.deepcopy(self.base)
        a["tier"], a["tier_evidence"] = 3, {3: "x"}
        tt = la.tier_table([a, b])
        self.assertEqual(tt["total"], {0: 1, 1: 0, 2: 0, 3: 1})
        self.assertEqual(tt["untiered"], 1)
        self.assertEqual([h["id"] for h in tt["tier2_plus"]], [a["id"]])
        self.assertAlmostEqual(tt["tier2_ratio"], 0.5)

    def test_progress_claim_below_tier_two_is_advised(self) -> None:
        row = copy.deepcopy(self.base)
        row["status"] = "measured"
        self.assertEqual(len(la.tier_advice([row])), 1)
        row["tier"], row["tier_evidence"] = 2, {2: "x"}
        self.assertEqual(la.tier_advice([row]), [])
        row2 = copy.deepcopy(self.base)
        row2["best_measured"] = "gain CONFIRMED at n = 19"
        self.assertEqual(len(la.tier_advice([row2])), 1)
        self.assertEqual(la.tier_advice([self.base]), [])

    def test_advice_does_not_fail_the_check(self) -> None:
        row = copy.deepcopy(self.base)
        row["status"] = "confirmed"
        errors, _ = la.check_leads([row])
        self.assertFalse(any("progress" in e for e in errors))

    def test_match_and_brief_carry_tier(self) -> None:
        hits = la.match("Frobenius-invariant factor base for Koblitz "
                        "subfield curve index calculus")
        self.assertTrue(all(len(h) == 5 for h in hits))
        self.assertTrue(any(h[4].startswith("T") for h in hits))
        self.assertIn("Evidence tiers", la.brief())

    def test_backfilled_tier_two_leads_cite_validation(self) -> None:
        for r in self.rows:
            if la.tier_of(r)[0] >= 2:
                self.assertIn("VALIDATION.json",
                              str(r["tier_evidence"].get(la.tier_of(r)[0])))


class PriorArtLeadTests(unittest.TestCase):
    def _errors(self, rec_id: str, block: dict) -> list[str]:
        ctx = vl.Ctx(set())
        body = {"id": rec_id, "novelty_status": "unverified",
                "prior_art": block}
        vl.check_prior_art("x.yaml", body, ctx)
        return ctx.errors

    def _block(self, **extra) -> dict:
        return {"frontier_map": "knowledge/frontiers/ecdlp",
                "rows_checked": [sorted(vl._frontier_row_ids())[0]],
                "none_found_after": ["q"], **extra}

    def test_lead_required_after_cutover(self) -> None:
        errs = self._errors(f"IDEA-{vl.LEAD_CUTOVER}-abc123", self._block())
        self.assertTrue(any("prior_art.lead is required" in e for e in errs))

    def test_lead_optional_before_cutover(self) -> None:
        errs = self._errors("IDEA-20261010-abc123", self._block())
        self.assertFalse(any("prior_art.lead" in e for e in errs))

    def test_known_lead_and_new_lead_pass(self) -> None:
        lead = la.load_leads()[0]["id"]
        rid = f"IDEA-{vl.LEAD_CUTOVER}-abc123"
        self.assertFalse(any("prior_art.lead" in e for e in
                             self._errors(rid, self._block(lead=lead))))
        self.assertFalse(any("prior_art.lead" in e for e in self._errors(
            rid, self._block(lead="new", new_lead_reason="no lead covers it"))))
        self.assertTrue(any("new_lead_reason" in e for e in
                            self._errors(rid, self._block(lead="new"))))
        self.assertTrue(any("is not a lead" in e for e in self._errors(
            rid, self._block(lead="LEAD-ICB-does-not-exist"))))

    def test_post_cutover_known_lead_requires_disposition_specific_delta(self) -> None:
        closed = next(r for r in la.load_leads() if r["disposition"] in la.CLOSED)
        opened = next(r for r in la.load_leads() if r["disposition"] in la.OPEN)
        rid = f"IDEA-{vl.LEAD_DELTA_CUTOVER}-abc123"
        self.assertTrue(any("lead_delta is required" in e for e in
                            self._errors(rid, self._block(lead=closed["id"]))))
        self.assertFalse(self._errors(rid, self._block(
            lead=closed["id"], lead_delta={"kind": "answers_obstruction",
                                            "statement": "changes assumption A"})))
        self.assertFalse(self._errors(rid, self._block(
            lead=opened["id"], lead_delta={"kind": "advances_next_action",
                                            "statement": "runs its queued test"})))
        self.assertTrue(any("advances_next_action" in e for e in self._errors(
            rid, self._block(lead=opened["id"], lead_delta={
                "kind": "answers_obstruction", "statement": "wrong kind"}))))


class RecordAreaTests(unittest.TestCase):
    """ecdlp_records() must see records the id prefix or line regex miss."""

    def _area(self, fn, text: str, suffix: str = ".yaml") -> str | None:
        with tempfile.NamedTemporaryFile("w", suffix=suffix,
                                         delete=False) as fh:
            fh.write(text)
        try:
            return fn(fh.name)
        finally:
            os.unlink(fh.name)

    def test_one_line_json_idea(self) -> None:
        text = ('{"idea":{"id":"IDEA-20261030-a62c58",'
                '"question_id":"RQ-PFDR-ae2fba","status":"proposed"}}')
        self.assertEqual(self._area(la._idea_area, text), "PFDR")

    def test_yaml_idea_still_uses_the_line_form(self) -> None:
        text = "idea:\n  id: IDEA-x\n  question_id: RQ-ECDLP-002\n"
        self.assertEqual(self._area(la._idea_area, text), "ECDLP")

    def test_hypothesis_area_from_its_question(self) -> None:
        text = ("hypothesis:\n  id: H-SEMAEV-94dab2\n"
                "  question_id: RQ-ECDLP-002\n")
        self.assertEqual(self._area(la._record_area, text), "ECDLP")

    def test_prefix_outside_areas_is_classified_by_question(self) -> None:
        recs = la.ecdlp_records()
        for rid in ("H-SEMAEV-94dab2", "H-PFIVE-6510c2",
                    "IDEA-20261030-a62c58"):
            with self.subTest(rid):
                self.assertIn(rid, recs)


if __name__ == "__main__":
    unittest.main()
