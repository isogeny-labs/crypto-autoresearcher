"""python3 -m unittest tools.test_check_harness_change_gate"""
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from tools import check_harness_change_gate as gate

TODAY = dt.date(2026, 11, 10)
BUDGET_PATCH = "-WAKE_BUDGET = 9_000\n+WAKE_BUDGET = 10_000\n"


def _root(*dates, empty=()):
    root = Path(tempfile.mkdtemp())
    for d in dates:
        (root / "evals/baselines" / d).mkdir(parents=True)
        (root / "evals/baselines" / d / "summary.json").write_text(json.dumps({"tasks": []}))
    for d in empty:
        (root / "evals/baselines" / d).mkdir(parents=True)
    return root


class GateTests(unittest.TestCase):
    def test_unrelated_diff_does_not_trigger(self):
        ok, _ = gate.evaluate([("M", "docs/other.md")], "", _root(), TODAY)
        self.assertTrue(ok)

    def test_budget_file_edit_without_constant_change_does_not_trigger(self):
        ok, _ = gate.evaluate([("M", gate.BUDGET_FILE)], "+# comment\n", _root(), TODAY)
        self.assertTrue(ok)

    def test_budget_constant_without_baseline_fails_with_command(self):
        ok, lines = gate.evaluate([("M", gate.BUDGET_FILE)], BUDGET_PATCH, _root(), TODAY)
        self.assertFalse(ok)
        text = "\n".join(lines)
        self.assertIn("--backend anthropic --trials 10 --out evals/baselines/2026-11-10", text)

    def test_skill_tuning_triggers(self):
        ok, _ = gate.evaluate([("M", "coordination/skill-tuning/x/round-1.yaml")], "", _root(), TODAY)
        self.assertFalse(ok)

    def test_new_loop_doc_triggers_but_edit_does_not(self):
        self.assertFalse(gate.evaluate([("A", "docs/new-loop.md")], "", _root(), TODAY)[0])
        self.assertTrue(gate.evaluate([("M", "docs/self-improvement-loop.md")], "", _root(), TODAY)[0])

    def test_fresh_baseline_passes(self):
        ok, lines = gate.evaluate([("A", "docs/x-loop.md")], "", _root("2026-10-20"), TODAY)
        self.assertTrue(ok)
        self.assertIn("2026-10-20", "\n".join(lines))

    def test_stale_baseline_fails_and_says_why(self):
        ok, lines = gate.evaluate([("A", "docs/x-loop.md")], "", _root("2026-09-01"), TODAY)
        self.assertFalse(ok)
        self.assertIn("70 days old", "\n".join(lines))

    def test_boundary_30_days_passes_31_fails(self):
        self.assertTrue(gate.evaluate([("A", "docs/x-loop.md")], "", _root("2026-10-11"), TODAY)[0])
        self.assertFalse(gate.evaluate([("A", "docs/x-loop.md")], "", _root("2026-10-10"), TODAY)[0])

    def test_dir_without_summary_and_future_dir_do_not_count(self):
        root = _root("2026-12-01", empty=("2026-11-09",))
        ok, lines = gate.evaluate([("A", "docs/x-loop.md")], "", root, TODAY)
        self.assertFalse(ok)
        text = "\n".join(lines)
        self.assertIn("no summary.json", text)
        self.assertIn("future", text)


if __name__ == "__main__":
    unittest.main()
