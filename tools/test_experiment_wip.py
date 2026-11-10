"""Tests for tools/experiment_wip.py using small fixture ledgers."""
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
import experiment_wip as ew  # noqa: E402
import harness_funnel as hf  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
AS_OF = dt.date(2026, 11, 8)
GOOD_FM = ("first_measurement:\n  command: python3 tools/x.py\n  max_seconds: 600\n  null_object: shuffled labels\n")


def policy(**over):
    p = {"schema": ew.SCHEMA, "mode": "advisory", "cutoff": "2026-11-08", "approved_unrun_cap_per_goal": 3,
         "approved_unrun_expiry_days": 14, "first_measurement_max_seconds": 3600, "notes": "n"}
    p.update(over)
    return p


def write_spec(root: Path, exp: str, status="approved", goal="GOAL-A", approved_at="2026-11-09", extra="",
               comment=""):
    lines = [f"experiment:  {comment}".rstrip(), f"  id: {exp}", f"  status: {status}  # keep me",
             f"  goal_id: {goal}", f"  approved_at: '{approved_at}'"]
    body = "\n".join(lines) + "\n" + "".join("  " + ln + "\n" for ln in extra.strip().split("\n") if ln)
    p = root / "experiments" / exp / "specification.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return p


class PolicyTests(unittest.TestCase):
    def test_real_policy_loads(self):
        p = ew.load_policy(REPO / "coordination" / "experiment_wip_policy.json")
        self.assertEqual(p["mode"], "advisory")
        self.assertEqual(p["cutoff"], "2026-11-08")

    def test_rejects_bad_policies(self):
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / "p.json"
            bad = [policy(schema="x"), policy(mode="loud"), policy(cutoff="11/08/2026"), policy(cutoff="2026-13-45"),
                   policy(approved_unrun_cap_per_goal=0), policy(approved_unrun_expiry_days=True),
                   policy(first_measurement_max_seconds="60"), policy(notes=3)]
            for b in bad:
                f.write_text(json.dumps(b))
                with self.assertRaises(ew.PolicyError, msg=str(b)):
                    ew.load_policy(f)
            f.write_text("{not json")
            with self.assertRaises(ew.PolicyError):
                ew.load_policy(f)
            with self.assertRaises(ew.PolicyError):
                ew.load_policy(Path(t) / "missing.json")


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def funnel(self):
        return hf.Funnel(self.root, "fs")

    def test_cap_counts_only_post_cutoff_contracts_past_the_cap(self):
        write_spec(self.root, "EXP-PRE", approved_at="2026-10-01", extra=GOOD_FM)
        for i, day in enumerate(("2026-11-08", "2026-11-09", "2026-11-10", "2026-11-11")):
            write_spec(self.root, f"EXP-P{i}", approved_at=day, extra=GOOD_FM)
        problems = ew.check(self.funnel(), policy())
        # EXP-PRE is open contract 1, P0 is 2, P1 is 3, P2 is 4 (over cap 3), P3 is 5 (over)
        self.assertEqual([(p["id"], p["problem"].split(",")[0]) for p in problems],
                         [("EXP-P2", "open contract 4 of goal when approved"),
                          ("EXP-P3", "open contract 5 of goal when approved")])

    def test_runs_free_the_cap(self):
        for i in range(4):
            write_spec(self.root, f"EXP-P{i}", approved_at="2026-11-09", extra=GOOD_FM)
        (self.root / "experiments/EXP-P0/runs/RUN-1").mkdir(parents=True)
        (self.root / "experiments/EXP-P0/runs/RUN-1/manifest.yaml").write_text("status: ok\n")
        self.assertEqual(ew.check(self.funnel(), policy()), [])

    def test_other_goals_do_not_share_a_cap(self):
        for i in range(3):
            write_spec(self.root, f"EXP-A{i}", goal="GOAL-A", approved_at="2026-11-09", extra=GOOD_FM)
            write_spec(self.root, f"EXP-B{i}", goal="GOAL-B", approved_at="2026-11-09", extra=GOOD_FM)
        self.assertEqual(ew.check(self.funnel(), policy()), [])

    def test_first_measurement_required_after_cutoff_only(self):
        write_spec(self.root, "EXP-OLD", approved_at="2026-10-01")
        write_spec(self.root, "EXP-NEW", approved_at="2026-11-08")
        write_spec(self.root, "EXP-DRAFT", status="draft", approved_at="2026-11-09")
        problems = ew.check(self.funnel(), policy())
        self.assertEqual([(p["id"], p["problem"]) for p in problems],
                         [("EXP-NEW", "missing first_measurement block")])

    def test_first_measurement_field_rules(self):
        mx = 3600
        self.assertEqual(ew.first_measurement_problems(
            {"first_measurement": {"command": ["a", "b"], "max_seconds": 3600, "null_object": "x"}}, mx), [])
        self.assertEqual(len(ew.first_measurement_problems({"first_measurement": {}}, mx)), 3)
        too_long = ew.first_measurement_problems(
            {"first_measurement": {"command": "c", "max_seconds": 7200, "null_object": "x"}}, mx)
        self.assertEqual(len(too_long), 1)
        self.assertIn("exceeds policy", too_long[0])
        self.assertEqual(len(ew.first_measurement_problems(
            {"first_measurement": {"command": "c", "max_seconds": True, "null_object": ""}}, mx)), 2)

    def test_exit_codes_by_mode(self):
        write_spec(self.root, "EXP-NEW", approved_at="2026-11-09")
        pol = self.root / "pol.json"
        pol.write_text(json.dumps(policy()))
        base = ["--root", str(self.root), "--policy", str(pol), "--check", "--runs-source", "fs"]
        for mode, want in (("advisory", 0), ("off", 0), ("enforce", 1)):
            with contextlib.redirect_stdout(io.StringIO()) as out:
                rc = ew.main(base + ["--mode", mode])
            self.assertEqual(rc, want, mode)
        self.assertIn("EXP-NEW", out.getvalue())
        pol.write_text(json.dumps(policy(mode="enforce")))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(ew.main(base), 1)
            self.assertEqual(ew.main(base + ["--mode", "advisory"]), 0)

    def test_bad_policy_exits_2(self):
        pol = self.root / "pol.json"
        pol.write_text("{}")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(ew.main(["--root", str(self.root), "--policy", str(pol), "--check"]), 2)


class ExpireTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.old = write_spec(self.root, "EXP-OLD", approved_at="2026-10-01", extra="execution_state: authorized")
        self.fresh = write_spec(self.root, "EXP-FRESH", approved_at="2026-11-05")
        self.nodate = self.root / "experiments/EXP-ND/specification.yaml"
        self.nodate.parent.mkdir(parents=True)
        self.nodate.write_text("experiment:\n  id: EXP-ND\n  status: approved\n")
        self.before = {p: p.read_text() for p in (self.old, self.fresh, self.nodate)}

    def tearDown(self):
        self.tmp.cleanup()

    def run_expire(self, apply):
        return ew.expire(hf.Funnel(self.root, "fs"), policy(), AS_OF, apply)

    def test_dry_run_writes_nothing(self):
        rows = self.run_expire(False)
        self.assertEqual([r["id"] for r in rows], ["EXP-OLD"])
        self.assertEqual(rows[0]["age_days"], 38)
        self.assertIn("status: approved -> draft", rows[0]["changes"])
        self.assertIn("execution_state: authorized -> draft", rows[0]["changes"])
        self.assertFalse(rows[0]["applied"])
        self.assertEqual({p: p.read_text() for p in self.before}, self.before)

    def test_apply_edits_only_overdue_and_keeps_comments(self):
        rows = self.run_expire(True)
        self.assertTrue(rows[0]["applied"])
        text = self.old.read_text()
        self.assertIn("status: draft", text)
        self.assertIn("status: draft  # keep me", text)
        body = hf.unwrap(hf.yaml.safe_load(text), "experiment")
        self.assertEqual(body["status"], "draft")
        self.assertEqual(body["execution_state"], "draft")
        self.assertEqual(body["expired_from_approved"], {"at": "2026-11-08", "age_days": 38, "policy": ew.SCHEMA})
        self.assertEqual(body["goal_id"], "GOAL-A")
        self.assertEqual(self.fresh.read_text(), self.before[self.fresh])
        self.assertEqual(self.nodate.read_text(), self.before[self.nodate])

    def test_apply_twice_is_idempotent(self):
        self.run_expire(True)
        once = self.old.read_text()
        self.assertEqual(self.run_expire(True), [])
        self.assertEqual(self.old.read_text(), once)

    def test_cli_default_never_writes(self):
        pol = self.root / "pol.json"
        pol.write_text(json.dumps(policy()))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = ew.main(["--root", str(self.root), "--policy", str(pol), "--expire", "--as-of", "2026-11-08",
                          "--runs-source", "fs"])
        self.assertEqual(rc, 0)
        self.assertIn("dry run, nothing written", out.getvalue())
        self.assertEqual({p: p.read_text() for p in self.before}, self.before)

    def test_unexpected_layout_is_reported_not_written(self):
        odd = self.root / "experiments/EXP-ODD/specification.yaml"
        odd.parent.mkdir(parents=True)
        odd.write_text("experiment: {id: EXP-ODD, status: approved, approved_at: '2026-09-01'}\n")
        rows = {r["id"]: r for r in self.run_expire(True)}
        self.assertIn("error", rows["EXP-ODD"])
        self.assertIn("status: approved", odd.read_text())


class ReportTests(unittest.TestCase):
    def test_report_lists_goal_over_cap_and_overdue(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            for i in range(5):
                write_spec(root, f"EXP-{i}", approved_at="2026-10-01")
            lines = "\n".join(ew.report_lines(hf.Funnel(root, "fs"), policy(), AS_OF))
            self.assertIn("GOAL-A", lines)
            self.assertIn("overdue approved-unrun contracts (older than 14 days): 5", lines)
            self.assertIn("38 days", lines)


if __name__ == "__main__":
    unittest.main()
