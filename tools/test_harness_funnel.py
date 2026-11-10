"""Tests for tools/harness_funnel.py using small fixture ledgers."""
from __future__ import annotations

import contextlib
import datetime as dt
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_funnel as hf  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
AS_OF = dt.date(2026, 11, 8)


def put(root: Path, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def spec(root: Path, exp: str, body: str, nested: bool = True) -> None:
    if nested:
        body = "experiment:\n" + "".join("  " + ln + "\n" for ln in body.strip().split("\n"))
    put(root, f"experiments/{exp}/specification.yaml", body)


def make_ledger(root: Path) -> None:
    put(root, "ledger/proposals/IDEA-1.yaml", "idea: {id: IDEA-1}\n")
    put(root, "ledger/ideas/IDEA-2.yaml", "id: IDEA-2\n")
    put(root, "ledger/hypotheses/H-1.yaml", "hypothesis: {id: H-1, status: specified, goal_id: GOAL-B}\n")
    put(root, "ledger/hypotheses/H-2.yaml", "hypothesis: {id: H-2, status: approved}\n")
    put(root, "ledger/hypotheses/bad.yaml", "just a string\n")
    put(root, "ledger/goals/GOAL-A.yaml", "research_goal: {id: GOAL-A, status: active}\n")
    put(root, "ledger/goals/GOAL-B/goal.yaml", "research_goal: {id: GOAL-B, status: draft}\n")
    put(root, "ledger/decisions/DEC-20261001-001.yaml",
        "coordinator_decision: {id: DEC-20261001-001, decision: approve, decided_at: '2026-10-01', target_ids: [EXP-TARGET]}\n")
    put(root, "ledger/decisions/DEC-20261002-001.yaml", "coordinator_decision: {id: DEC-20261002-001, decision: revise}\n")
    put(root, "ledger/decisions/broken.yaml", "{{{{\n")
    put(root, "ledger/evidence/EV-1.yaml",
        "evidence: {id: EV-1, claim_tier: toy, direction: supports, experiment_ids: [EXP-RUN-EV], "
        "certificate: {kind: x, verified: true}}\n")
    put(root, "ledger/EV-LEGACY.yaml", "evidence: {id: EV-L, claim_tier: theory, direction: neutral}\n")
    spec(root, "EXP-OLD", "id: EXP-OLD\nstatus: approved\ngoal_id: GOAL-A\napproved_at: '2026-09-01'\napproved_by: coordinator")
    spec(root, "EXP-NEW", "id: EXP-NEW\nstatus: approved\nhypothesis_id: H-1\napproved_at: 2026-11-05")
    spec(root, "EXP-VIA-DEC", "id: EXP-VIA-DEC\nstatus: approved\ngoal_id: GOAL-A\napproval_decision: DEC-20261001-001")
    spec(root, "EXP-TARGET", "id: EXP-TARGET\nstatus: approved\ngoal_id: GOAL-A")
    spec(root, "EXP-NODATE", "id: EXP-NODATE\nstatus: approved")
    spec(root, "EXP-RAN", "id: EXP-RAN\nstatus: approved\ngoal_id: GOAL-A\napproved_at: '2026-09-01'")
    spec(root, "EXP-RUN-EV", "id: EXP-RUN-EV\nstatus: approved\ngoal_id: GOAL-A\napproved_at: '2026-09-01'")
    spec(root, "EXP-DRAFT", "id: EXP-DRAFT\nstatus: draft")
    spec(root, "EXP-FLAT", "id: EXP-FLAT\nstatus: draft", nested=False)
    put(root, "experiments/EXP-BAD/specification.yaml", "- not\n- a mapping\n")
    put(root, "experiments/EXP-RAN/runs/RUN-1/manifest.yaml", "run: {status: completed_valid}\n")
    put(root, "experiments/EXP-RAN/runs/RUN-2/manifest.json", json.dumps({"status": "failed"}))
    put(root, "experiments/EXP-RAN/runs/.gitkeep", "")
    (root / "experiments/EXP-EMPTY/runs").mkdir(parents=True)


class FunnelTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        make_ledger(self.root)
        self.s = hf.summarize(hf.Funnel(self.root, "fs"), AS_OF)

    def tearDown(self):
        self.tmp.cleanup()

    def test_stage_counts(self):
        s = self.s
        self.assertEqual(s["proposals"], {"proposals": 1, "ideas": 1, "total": 2})
        self.assertEqual(s["hypotheses"]["total"], 2)
        self.assertEqual(s["hypotheses"]["by_status"], {"approved": 1, "specified": 1})
        self.assertEqual(s["specifications"]["total"], 9)
        self.assertEqual(s["specifications"]["by_status"]["approved"], 7)
        self.assertEqual(s["decisions"]["by_decision"], {"approve": 1, "revise": 1})
        self.assertEqual(s["goals"]["total"], 2)
        self.assertEqual(s["unreadable_records"], {"hypotheses": 1, "decisions": 1, "specifications": 1})

    def test_runs_ignore_dotfiles_and_empty_dirs(self):
        self.assertEqual(s := self.s["runs"]["total"], 2)
        self.assertEqual(self.s["runs"]["experiments_with_runs"], 1)
        self.assertEqual(self.s["runs"]["by_manifest_status"], {"completed_valid": 1, "failed": 1})

    def test_evidence(self):
        ev = self.s["evidence"]
        self.assertEqual(ev["total"], 2)
        self.assertEqual(ev["by_claim_tier"], {"theory": 1, "toy": 1})
        self.assertEqual(ev["certificate_verified"], 1)

    def test_approved_unrun(self):
        u = self.s["approved_unrun"]
        # approved: OLD, NEW, VIA-DEC, TARGET, NODATE, RAN (run), RUN-EV (evidence)
        self.assertEqual(self.s["approved"]["total"], 7)
        self.assertEqual(u["total"], 5)
        self.assertEqual(self.s["approved"]["with_run"], 1)
        self.assertEqual(self.s["approved"]["with_evidence"], 1)

    def test_aging_and_sources(self):
        u = self.s["approved_unrun"]
        # OLD 68d, NEW 3d, VIA-DEC 38d, TARGET 38d (approve decision target), NODATE unknown
        self.assertEqual(u["aging_days"], {"0-7d": 1, "8-14d": 0, "15-30d": 0, "31-60d": 2,
                                           "61-90d": 1, "91d+": 0, "unknown": 1})
        self.assertEqual(u["approval_date_source"],
                         {"approve_decision_target": 1, "approval_decision": 1, "approved_at": 2, "unknown": 1})

    def test_per_goal_via_hypothesis(self):
        pg = self.s["per_goal"]
        self.assertEqual(pg["GOAL-A"], {"approved": 5, "approved_unrun": 3})
        self.assertEqual(pg["GOAL-B"], {"approved": 1, "approved_unrun": 1})
        self.assertEqual(pg[hf.NO_GOAL], {"approved": 1, "approved_unrun": 1})

    def test_ratios(self):
        r = self.s["ratios"]
        self.assertEqual(r["decisions_per_evidence"], 1.0)
        self.assertAlmostEqual(r["evidence_per_approved_contract"], round(2 / 7, 3))

    def test_deterministic(self):
        again = hf.summarize(hf.Funnel(self.root, "fs"), AS_OF)
        self.assertEqual(json.dumps(self.s), json.dumps(again))

    def test_cli_json_and_check(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = hf.main(["--root", str(self.root), "--json", "--as-of", "2026-11-08", "--runs-source", "fs"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(buf.getvalue())["approved_unrun"]["total"], 5)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = hf.main(["--root", str(self.root), "--check", "--runs-source", "fs"])
        self.assertEqual(rc, 0)
        self.assertIn("approved_unrun 5", buf.getvalue())

    def test_age_bucket_edges(self):
        self.assertEqual([hf.age_bucket(n) for n in (0, 7, 8, 14, 15, 30, 31, 60, 61, 90, 91, None)],
                         ["0-7d", "0-7d", "8-14d", "8-14d", "15-30d", "15-30d", "31-60d", "31-60d",
                          "61-90d", "61-90d", "91d+", "unknown"])


class RealRepoTests(unittest.TestCase):
    """Drift guard: headline counts stay within 5% of the 2026-11-08 review."""

    EXPECTED = {
        ("proposals", "total"): 2825,
        ("hypotheses", "total"): 2263,
        ("specifications", "total"): 2847,
        ("approved", "total"): 1661,
        ("approved_unrun", "total"): 1187,
        ("runs", "total"): 3843,
        ("evidence", "total"): 826,
        ("decisions", "total"): 3642,
    }

    def test_headline_counts(self):
        if not (REPO / "ledger" / "decisions").is_dir():
            self.skipTest("ledger not present in this checkout")
        s = hf.summarize(hf.Funnel(REPO, "auto"), AS_OF)
        for (stage, key), want in self.EXPECTED.items():
            got = s[stage][key]
            self.assertLessEqual(abs(got - want) / want, 0.05,
                                 f"{stage}.{key}: {got} is more than 5% from the reviewed {want}")


if __name__ == "__main__":
    unittest.main()
