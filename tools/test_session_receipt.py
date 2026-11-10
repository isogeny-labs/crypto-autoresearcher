#!/usr/bin/env python3
"""Tests for tools/session_receipt.py."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import session_receipt as sr  # noqa: E402


def _args(**over) -> argparse.Namespace:
    base = dict(skill="design-experiment", role="coordinator", mode=None, outcome="approved",
                created="EXP-FROB-123456,H-FROB-000001,TASK-20261007-aaaaaa,weird",
                files_read=12, started=None, runtime=None, model=None, policy=None,
                usage_json=None, usage_source=None, goal="GOAL-FROB-000001", notes=None,
                supersedes=None, bounced=None, allow_null_usage=None, transcript=None)
    base.update(over)
    return argparse.Namespace(**base)


class ReceiptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.now = datetime(2026, 10, 7, 9, 30, tzinfo=timezone.utc)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_receipt_groups_created_ids_and_never_estimates_usage(self) -> None:
        rec = sr.receipt(_args(), repo_root=self.root, now=self.now, env={})
        self.assertEqual(rec["schema"], sr.SCHEMA)
        self.assertTrue(rec["id"].startswith("SR-20261007-"))
        self.assertEqual(rec["records_created"],
                         {"EXP": ["EXP-FROB-123456"], "H": ["H-FROB-000001"],
                          "TASK": ["TASK-20261007-aaaaaa"], "other": ["weird"]})
        self.assertEqual(rec["records_created_count"], 4)
        self.assertIsNone(rec["usage"])
        self.assertIsNone(rec["usage_source"])
        self.assertIsNone(rec["runtime"])
        self.assertIsNone(rec["model"])
        self.assertIsNone(rec["provider"])
        self.assertIsNone(rec["backend"])
        self.assertIsNone(rec["started_at"])
        self.assertEqual(rec["ended_at"], "2026-10-07T09:30:00+00:00")

    def test_runtime_detection_uses_only_runtime_markers(self) -> None:
        self.assertEqual(sr.detect_runtime({"CURSOR_AGENT": "1", "CURSOR_WORKLOAD_CGROUP": "x"}), "cursor_cloud")
        self.assertEqual(sr.detect_runtime({"CLAUDECODE": "1"}), "claude_code")
        self.assertEqual(sr.detect_runtime({"AUTORESEARCH_RUNTIME": "api_direct"}), "api_direct")
        self.assertIsNone(sr.detect_runtime({"HOME": "/x"}))
        self.assertEqual(sr.detect_model({"AUTORESEARCH_RESOLVED_MODEL": "m-1"}), "m-1")
        self.assertIsNone(sr.detect_model({}))

    def test_usage_json_must_be_an_object(self) -> None:
        with self.assertRaises(ValueError):
            sr.receipt(_args(usage_json="[1,2]"), repo_root=self.root, now=self.now, env={})
        rec = sr.receipt(_args(usage_json='{"input_tokens": 10}', usage_source="test"),
                         repo_root=self.root, now=self.now, env={})
        self.assertEqual(rec["usage"], {"input_tokens": 10})
        self.assertEqual(rec["usage_source"], "test")

    def test_started_falls_back_to_environment(self) -> None:
        rec = sr.receipt(_args(), repo_root=self.root, now=self.now,
                         env={"SESSION_RECEIPT_STARTED": "2026-10-07T09:00:00+00:00"})
        self.assertEqual(rec["started_at"], "2026-10-07T09:00:00+00:00")

    def test_write_is_write_once_and_summary_aggregates(self) -> None:
        rec = sr.receipt(_args(), repo_root=self.root, now=self.now, env={})
        path = sr.write(rec, self.root)
        self.assertEqual(path.parent.name, "20261007")
        with self.assertRaises(FileExistsError):
            sr.write(rec, self.root)
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertEqual(loaded["skill"], "design-experiment")
        rec2 = sr.receipt(_args(skill="run", outcome="nothing_executable", created=""),
                          repo_root=self.root, now=self.now, env={})
        sr.write(rec2, self.root)
        s = sr.summary(sr.load_all(self.root))
        self.assertEqual(s["receipts"], 2)
        self.assertEqual(s["usage_known"], 0)
        self.assertEqual(s["runtime_known"], 0)
        self.assertEqual(s["provenance_complete"], 0)
        self.assertEqual(s["by_skill"]["run"], {"nothing_executable": 1})
        self.assertEqual(s["records_created_by_skill"]["design-experiment"], 4)
        text = sr.render_summary(s)
        self.assertIn("session receipts: 2", text)
        self.assertIn("design-experiment: 1 (approved 1); records created 4", text)
        self.assertIn("none yet", sr.render_summary(sr.summary([])))

    def test_bounce_count_is_recorded_and_summed(self) -> None:
        rec = sr.receipt(_args(skill="propose-ideas", outcome="proposed", bounced=3),
                         repo_root=self.root, now=self.now, env={})
        self.assertEqual(rec["bounced"], 3)
        sr.write(rec, self.root)
        rec2 = sr.receipt(_args(skill="propose-ideas", outcome="proposed", bounced=2),
                          repo_root=self.root, now=self.now, env={})
        sr.write(rec2, self.root)
        s = sr.summary(sr.load_all(self.root))
        self.assertEqual(s["bounced_by_skill"], {"propose-ideas": 5})
        self.assertIn("bounced 5", sr.render_summary(s))
        # A receipt that did not count bounces records null, never zero.
        self.assertIsNone(sr.receipt(_args(), repo_root=self.root, now=self.now, env={})["bounced"])

    def test_receipt_refuses_ecc_design_record_flood(self) -> None:
        (self.root / "orchestration").mkdir()
        (self.root / "ledger/questions").mkdir(parents=True)
        (self.root / "ledger/proposals").mkdir()
        (self.root / "orchestration/research-priority.yaml").write_text(
            yaml.safe_dump({"ecc_areas": ["ECDLP"], "process_budget": {
                "effective_on": "2026-11-01",
                "max_new_ecc_ideas_per_session": 3,
                "max_new_ecc_experiments_per_session": 1,
                "max_new_ecc_ideas_per_utc_day": 12,
                "max_new_ecc_experiments_per_utc_day": 6}}), encoding="utf-8")
        (self.root / "ledger/questions/q.yaml").write_text(yaml.safe_dump({
            "research_question": {"id": "RQ-ECDLP-abc123"}}), encoding="utf-8")
        ids = [f"IDEA-20261101-abc12{i}" for i in range(4)]
        for index, idea_id in enumerate(ids):
            (self.root / f"ledger/proposals/{index}.yaml").write_text(yaml.safe_dump({
                "idea": {"id": idea_id, "question_id": "RQ-ECDLP-abc123"}}),
                encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "process budget exceeded"):
            sr.receipt(_args(skill="propose-ideas", outcome="proposed",
                             created=",".join(ids)), repo_root=self.root,
                       now=datetime(2026, 11, 1, 12, tzinfo=timezone.utc), env={})

    def test_cli_requires_skill_and_outcome(self) -> None:
        with self.assertRaises(SystemExit):
            sr.main(["--repo-root", str(self.root)])
        self.assertEqual(sr.main(["--repo-root", str(self.root), "--skill", "run",
                                  "--outcome", "ran"]), 0)
        self.assertEqual(len(sr.load_all(self.root)), 1)
        self.assertEqual(sr.main(["--repo-root", str(self.root), "summary"]), 0)


if __name__ == "__main__":
    unittest.main()


def _line(mid, u, model="claude-opus-5-5", stop="end_turn"):
    return {"type": "assistant", "requestId": "req_" + mid,
            "message": {"id": mid, "model": model, "stop_reason": stop,
                        "content": [{"type": "text"}], "usage": u}}


def _u(inp, w1, rd, out):
    return {"input_tokens": inp, "cache_creation_input_tokens": w1,
            "cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": w1},
            "cache_read_input_tokens": rd, "output_tokens": out, "speed": "standard"}


class TranscriptUsageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        self.home = Path(self.tmp.name) / "home"
        self.proj = self.home / ".claude" / "projects" / "-x-repo"
        self.proj.mkdir(parents=True)
        self.env = {"HOME": str(self.home), "CLAUDECODE": "1"}
        self.now = datetime(2026, 11, 10, 9, 0, tzinfo=timezone.utc)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _transcript(self, text=None):
        path = self.proj / "sess1.jsonl"
        if text is None:
            rows = [_line("m1", _u(2, 10_000, 40_000, 200), stop="tool_use"),
                    _line("m1", _u(2, 10_000, 40_000, 200), stop="tool_use"),  # duplicate block line
                    _line("m2", _u(2, 1_000, 50_000, 300))]
            text = "".join(json.dumps(r) + "\n" for r in rows)
        path.write_text(text, encoding="utf-8")
        return path

    def _receipt(self, **over):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            rec = sr.receipt(_args(**over), repo_root=self.root, now=self.now, env=self.env)
        return rec, err.getvalue()

    def test_usage_filled_from_newest_transcript(self) -> None:
        self._transcript()
        rec, _ = self._receipt()
        self.assertEqual(rec["usage_source"], "claude_code_transcript")
        self.assertEqual(rec["requests"], 2)  # deduplicated by message id
        self.assertEqual(rec["usage"]["output_tokens"], 500)
        self.assertEqual(rec["usage"]["cache_creation_input_tokens"], 11_000)
        self.assertEqual(rec["usage"]["cache_read_input_tokens"], 90_000)
        self.assertAlmostEqual(rec["cost_usd"], 11_000 * 8e-6 + 90_000 * 0.2e-6 + 500 * 20e-6 + 4 * 4e-6, places=6)
        self.assertAlmostEqual(rec["cache_hit_ratio"], round(90_000 / 101_004, 4))
        self.assertIsNone(rec["usage_override_reason"])
        print(json.dumps({k: rec[k] for k in ("runtime", "usage", "usage_source", "cost_usd",
                                              "cache_hit_ratio", "requests")}))

    def test_unreadable_transcript_refuses(self) -> None:
        self._transcript("not json at all\n{broken\n")
        with self.assertRaises(sr.UsageRefused) as ctx:
            self._receipt()
        self.assertIn("no receipt without usage", str(ctx.exception))
        self.assertEqual(sr.main(["--repo-root", str(self.root), "--skill", "run", "--outcome", "ran",
                                  "--runtime", "claude_code", "--transcript", str(self.proj / "sess1.jsonl")]), 2)
        self.assertFalse((self.root / sr.RECEIPTS_DIR).exists())

    def test_absent_transcript_writes_null_with_warning(self) -> None:
        rec, err = self._receipt()
        self.assertIsNone(rec["usage"])
        self.assertEqual(rec["usage_source"], "unavailable")
        self.assertIn("warning", err)

    def test_override_requires_reason_and_is_stored(self) -> None:
        self._transcript("garbage\n")
        rec, _ = self._receipt(allow_null_usage="transcript truncated by container restart")
        self.assertIsNone(rec["usage"])
        self.assertEqual(rec["usage_source"], "unavailable")
        self.assertEqual(rec["usage_override_reason"], "transcript truncated by container restart")
        with self.assertRaises(ValueError):
            self._receipt(allow_null_usage="  ")

    def test_usage_json_wins_over_transcript(self) -> None:
        self._transcript()
        rec, _ = self._receipt(usage_json='{"input_tokens": 7}', usage_source="manual")
        self.assertEqual(rec["usage"], {"input_tokens": 7})
        self.assertEqual(rec["usage_source"], "manual")

    def test_summary_cost_columns_and_runtime_coverage(self) -> None:
        self._transcript()
        a, _ = self._receipt()
        b, _ = self._receipt(created="EXP-FROB-123456", outcome="review_required")
        c = sr.receipt(_args(runtime="cursor"), repo_root=self.root, now=self.now, env={})
        s = sr.summary([a, b, c])
        self.assertEqual(s["cost_known"], 2)
        self.assertAlmostEqual(s["cost_usd_total"], 2 * a["cost_usd"], places=5)
        self.assertEqual(s["supported_proxy_receipts"], 1)
        self.assertAlmostEqual(s["cost_per_supported"], 2 * a["cost_usd"], places=5)
        self.assertIsNone(s["cost_per_evidence_record"])  # no EV-* created
        self.assertEqual(s["usage_by_runtime"]["claude_code"], {"receipts": 2, "usage_known": 2})
        self.assertEqual(s["usage_by_runtime"]["cursor"], {"receipts": 1, "usage_known": 0})
        text = sr.render_summary(s)
        self.assertIn("per supported outcome", text)
        self.assertIn("usage coverage by runtime: claude_code 2/2, cursor 0/1", text)
