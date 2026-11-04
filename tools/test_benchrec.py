#!/usr/bin/env python3
"""Tests for tools/benchrec.py: run in a throwaway git repository."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().with_name("benchrec.py")


def sh(*args, cwd, check=True, env=None):
    p = subprocess.run(list(args), cwd=cwd, capture_output=True, text=True, env=env)
    if check and p.returncode != 0:
        raise AssertionError(f"{' '.join(map(str, args))}\n{p.stdout}\n{p.stderr}")
    return p


class BenchrecTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        sh("git", "init", "-q", "-b", "main", cwd=self.root)
        sh("git", "config", "user.email", "t@example.invalid", cwd=self.root)
        sh("git", "config", "user.name", "t", cwd=self.root)
        (self.root / "README.md").write_text("x\n")
        (self.root / ".gitignore").write_text(".benchrec/\n")
        sh("git", "add", "-A", cwd=self.root)
        sh("git", "commit", "-qm", "init", cwd=self.root)
        self.env = dict(os.environ, BENCHREC_ISOLATION="L0")

    def tearDown(self):
        self.tmp.cleanup()

    def br(self, *args, check=True):
        return sh(sys.executable, str(TOOL), *args, cwd=self.root, check=check, env=self.env)

    def commit_all(self, msg="c"):
        sh("git", "add", "-A", cwd=self.root)
        sh("git", "commit", "-qm", msg, cwd=self.root)

    def make_record(self, slug="rho-step", value=100.0, reference=None, status="measured"):
        rec = self.br("init", "--slug", slug, "--problem", "kernel:rho_step").stdout.strip()
        self.assertTrue((self.root / rec).is_file())
        self.assertEqual(self.br("open", check=False).returncode, 1)
        out = self.root / "out"
        out.mkdir(exist_ok=True)
        data = out / f"{slug}-{value}.json"
        data.write_text(json.dumps({"value": value}))
        r = self.br("run", rec, "--", sys.executable, "-c", "print('ran')")
        self.assertIn("ran", r.stdout)
        self.br("add-raw", rec, str(data))
        args = ["metric", rec, "--name", "ir_per_op", "--value", str(value), "--unit", "ir_per_op", "--n", "3"]
        if reference is not None:
            args += ["--reference", str(reference), "--reference-kind", "matched_rho"]
        self.br(*args)
        self.br("metric", rec, "--name", "cost", "--value", str(value / 10), "--unit", "S")
        pdf = self.root / "report.pdf"
        pdf.write_bytes(b"%PDF-1.4\n")
        close = ["close", rec, "--status", status, "--summary", "a run"]
        if status == "measured":
            close += ["--report", str(pdf)]
        self.br(*close)
        return rec

    def test_full_lifecycle_and_progress(self):
        rec1 = self.make_record(value=100.0, reference=50.0)
        rec2 = self.make_record(slug="rho-step-2", value=80.0, reference=50.0)
        prog = json.loads((self.root / "benchmarks/progress/progress.json").read_text())
        self.assertEqual(prog["schema"], "bench.progress/v1")
        s = next(x for x in prog["series"] if x["metric"] == "ir_per_op")
        self.assertEqual(len(s["points"]), 2)
        self.assertAlmostEqual(s["points"][1]["derived"]["improvement_vs_first_percent"], 20.0)
        self.assertAlmostEqual(s["points"][1]["derived"]["value_over_reference"], 1.6)
        for f in ("PROGRESS.md", "progress.svg", "progress.pdf"):
            self.assertTrue((self.root / "benchmarks/progress" / f).stat().st_size > 100)
        self.assertTrue((self.root / "benchmarks/progress/progress.pdf").read_bytes().startswith(b"%PDF"))
        self.assertEqual(self.br("open", check=False).returncode, 0)
        self.assertEqual(self.br("gate").returncode, 0)
        self.assertEqual(self.br("report", "--check").returncode, 0)
        # Records are immutable once closed.
        r = self.br("metric", rec1, "--name", "x", "--value", "1", "--unit", "S", check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn(rec2, (self.root / rec2).as_posix())

    def test_unknown_unit_and_bad_close_rejected(self):
        rec = self.br("init", "--slug", "unit-test", "--problem", "p:q").stdout.strip()
        r = self.br("metric", rec, "--name", "m", "--value", "1", "--unit", "furlongs", check=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("unknown unit", r.stderr)
        r = self.br("close", rec, "--status", "measured", check=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("no command recorded", r.stderr)
        self.assertEqual(json.loads((self.root / rec).read_text())["status"], "open")

    def test_gate_fails_on_open_record(self):
        self.br("init", "--slug", "left-open", "--problem", "p:q")
        r = self.br("gate", check=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("not closed", r.stdout)

    def test_check_base_requires_record_for_new_entry(self):
        self.make_record()
        self.commit_all("record")
        sh("git", "checkout", "-qb", "feature", cwd=self.root)
        d = self.root / "benchmarks/20261104-new-thing"
        d.mkdir(parents=True)
        (d / "README.md").write_text("entry\n")
        self.commit_all("entry without record")
        r = self.br("check", "--base", "main", check=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("benchmarks/20261104-new-thing: benchmark entry added without", r.stdout)
        rec = self.br("init", "--slug", "new-thing", "--problem", "p:q", "--entry", "benchmarks/20261104-new-thing").stdout.strip()
        self.br("run", rec, "--", "true")
        self.br("add-raw", rec, str(d / "README.md"))
        self.br("metric", rec, "--name", "m", "--value", "2", "--unit", "wall_s")
        pdf = self.root / "r.pdf"
        pdf.write_bytes(b"%PDF-1.4\n")
        self.br("close", rec, "--status", "measured", "--report", str(pdf), "--summary", "ok")
        self.commit_all("record")
        self.assertEqual(self.br("check", "--base", "main").returncode, 0)

    def test_closed_record_edit_rejected_against_base(self):
        rec = self.make_record()
        self.commit_all("record")
        sh("git", "checkout", "-qb", "feature", cwd=self.root)
        p = self.root / rec
        d = json.loads(p.read_text())
        d["summary"] = "rewritten"
        p.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n")
        self.br("report")
        self.commit_all("tamper")
        r = self.br("check", "--base", "main", check=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("closed record is immutable", r.stdout)

    def test_stale_progress_detected(self):
        self.make_record()
        (self.root / "benchmarks/progress/PROGRESS.md").write_text("edited by hand\n")
        r = self.br("check", check=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("progress report is stale", r.stdout)

    def test_raw_missing_locally_and_not_uploaded_fails(self):
        rec = self.make_record()
        os.remove(self.root / "out" / "rho-step-100.0.json")
        r = self.br("check", check=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("neither in Git", r.stdout)

    def test_config_override(self):
        (self.root / ".benchrec.json").write_text(json.dumps({
            "records_dir": "docs/benchmarks/records", "progress_dir": "docs/benchmarks/progress",
            "entry_dirs": ["docs/benchmarks"], "entry_re": "^[a-z0-9-]+-\\d{8}$"}))
        rec = self.br("init", "--slug", "cfg", "--problem", "p:q").stdout.strip()
        self.assertTrue(rec.startswith("docs/benchmarks/records/"))


if __name__ == "__main__":
    unittest.main()
