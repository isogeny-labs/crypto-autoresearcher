#!/usr/bin/env python3
"""Tests for kb_usage_report.py; stdlib only."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_module():
    spec = importlib.util.spec_from_file_location("kb_usage_report", HERE / "kb_usage_report.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


kb = load_module()

LOG = """# Session log — 2026-11-05

## 2026-11-05T10:00:00Z — first

### What was done

- Sources checked (KB):
  - `source:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` — `crypto:docs/x.md` — changed the plan.
  - query "Semaev degree" — no result.

### Decisions made (and why)

- none

## 2026-11-05T11:00:00Z — second

### What was done

- no KB receipt here.
"""

OTHER = """# Session log — 2026-11-04

## 2026-11-04T10:00:00Z — old

### What was done

- KB unavailable: server not loaded; used the lead atlas.
"""


class UsageReportTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        logs = self.root / "docs" / "session-logs"
        logs.mkdir(parents=True)
        (logs / "2026-11-05.md").write_text(LOG)
        (logs / "TEMPLATE.md").write_text("## YYYY-MM-DD — template\n- Sources checked (KB)\n")
        (logs / "2026-11-04.md").write_text(OTHER)

    def tearDown(self):
        self.tmp.cleanup()

    def test_counts_receipts_and_ids(self):
        row = kb.audit_root(self.root, None)
        self.assertEqual(row["logs"], 2)
        self.assertEqual(row["entries"], 3)
        self.assertEqual(row["receipts"], 2)  # one source receipt, one unavailable
        self.assertAlmostEqual(row["coverage"], 2 / 3)
        self.assertEqual(row["unique_source_ids"], 1)
        self.assertEqual(row["queries"], ["Semaev degree"])
        self.assertEqual(row["unavailable"], 1)

    def test_since_filters_old_entries(self):
        row = kb.audit_root(self.root, "2026-11-05")
        self.assertEqual(row["entries"], 2)
        self.assertEqual(row["receipts"], 1)
        self.assertEqual(row["coverage"], 0.5)

    def test_report_totals_and_json(self):
        data = kb.report([self.root], None)
        self.assertEqual(data["schema"], "kb-usage/v1")
        self.assertEqual(data["totals"]["entries"], 3)
        self.assertEqual(data["totals"]["receipts"], 2)
        self.assertEqual(data["totals"]["unique_source_ids"], 1)
        self.assertEqual(json.loads(json.dumps(data))["totals"]["coverage"], 2 / 3)

    def test_ref_reads_committed_logs(self):
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.root)], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "-C", str(self.root), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-q", "-m", "logs"], check=True)

        # Dirty the working tree: a measurement of committed history must not
        # see this edit, while the default read must.
        dirty = "## 2026-11-05T10:00:00Z — uncommitted\n\n- no receipt here\n"
        (self.root / "docs" / "session-logs" / "2026-11-05.md").write_text(dirty)

        work = kb.audit_root(self.root, None)
        committed = kb.audit_root(self.root, None, "HEAD")
        self.assertEqual((work["entries"], work["receipts"]), (2, 1))
        self.assertEqual((committed["entries"], committed["receipts"]), (3, 2))
        self.assertEqual(committed["unique_source_ids"], 1)

        missing = kb.main(["--root", str(self.root), "--ref", "no-such-ref"])
        self.assertEqual(missing, 2)

    def test_fail_under(self):
        with tempfile.TemporaryDirectory() as out:
            target = Path(out) / "out.json"
            code = kb.main(["--root", str(self.root), "--json", "--out", str(target), "--fail-under", "0.9"])
            self.assertEqual(code, 1)
            self.assertTrue(target.is_file())
            self.assertEqual(json.loads(target.read_text())["schema"], "kb-usage/v1")


if __name__ == "__main__":
    unittest.main()
