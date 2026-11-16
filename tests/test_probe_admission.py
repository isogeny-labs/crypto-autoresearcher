"""check_probe_admission: review I1 (probe) and I12 (nearest) for new ECC ideas."""

from __future__ import annotations

import copy
import os
import sys
import tempfile
import unittest
from unittest import mock

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

import check_probe_admission as cpa                  # noqa: E402
import validate_ledger                               # noqa: E402

NEW_ID = "IDEA-20261112-abc123"
GOOD = {
    "id": NEW_ID,
    "question_id": "RQ-ECDLP-001",
    "probe": {
        "command": "python3 probes/p.py --bits 24",
        "evaluator": "probes/p.py",
        "metric": "relations_per_second",
        "threshold": 1.5,
        "direction": "higher_is_better",
        "cpu_minutes": 5,
        "instance": "24-bit prime field curve, factor base 2^8",
    },
    "nearest": {
        "id": "IDEA-20261001-aaaaaa",
        "difference": "Uses a Frobenius-stable factor base instead of a "
                      "random one, changing the relation yield.",
    },
}


class ProbeAdmission(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = tmp.name
        os.makedirs(os.path.join(self.root, "probes"))
        open(os.path.join(self.root, "probes", "p.py"), "w").close()
        p = mock.patch.object(validate_ledger, "REPO", self.root)
        p.start()
        self.addCleanup(p.stop)
        p = mock.patch.object(validate_ledger, "_lead_exists",
                              lambda r: r == "LEAD-ICB-real-lead")
        p.start()
        self.addCleanup(p.stop)

    def run_check(self, body, today="2026-11-20", rec_id=None):
        ctx = validate_ledger.Ctx(legacy_paths=set())
        rid = rec_id or body["id"]
        ctx.register("IDEA-20261001-aaaaaa",
                     os.path.join(self.root, "a.yaml"), {}, "idea")
        ctx.register(rid, os.path.join(self.root, "x.yaml"), body, "idea")
        cpa.check_probe_admission(ctx, today=today)
        return ctx

    def test_complete_record_passes(self):
        ctx = self.run_check(copy.deepcopy(GOOD))
        self.assertEqual((ctx.errors, ctx.advisories), ([], []))

    def test_lead_id_accepted(self):
        b = copy.deepcopy(GOOD)
        b["nearest"]["id"] = "LEAD-ICB-real-lead"
        ctx = self.run_check(b)
        self.assertEqual((ctx.errors, ctx.advisories), ([], []))

    def test_missing_blocks(self):
        for key in ("probe", "nearest"):
            b = copy.deepcopy(GOOD)
            del b[key]
            ctx = self.run_check(b)
            self.assertEqual(len(ctx.advisories), 1, key)
            self.assertIn(f"{key}: block is missing", ctx.advisories[0])

    def test_each_probe_field_required(self):
        for key in GOOD["probe"]:
            b = copy.deepcopy(GOOD)
            del b["probe"][key]
            ctx = self.run_check(b)
            self.assertEqual(len(ctx.advisories), 1, key)
            self.assertIn(f"probe.{key}", ctx.advisories[0])

    def test_probe_malformed(self):
        for key, bad in (("threshold", "high"), ("threshold", True),
                         ("direction", "bigger"), ("cpu_minutes", 11),
                         ("cpu_minutes", 0), ("evaluator", "probes/nope.py"),
                         ("command", "  ")):
            b = copy.deepcopy(GOOD)
            b["probe"][key] = bad
            ctx = self.run_check(b)
            self.assertEqual(len(ctx.advisories), 1, (key, bad))

    def test_nearest_problems(self):
        for key, bad in (("id", "IDEA-20260101-zzzzzz"),
                         ("id", "LEAD-ICB-missing"), ("id", NEW_ID),
                         ("difference", "too short")):
            b = copy.deepcopy(GOOD)
            b["nearest"][key] = bad
            ctx = self.run_check(b)
            self.assertEqual(len(ctx.advisories), 1, (key, bad))
            self.assertIn("nearest.", ctx.advisories[0])

    def test_non_ecc_area_exempt(self):
        b = {"id": NEW_ID, "question_id": "RQ-CLGRP-001"}
        ctx = self.run_check(b)
        self.assertEqual((ctx.errors, ctx.advisories), ([], []))

    def test_pre_date_exempt(self):
        rid = "IDEA-20261110-abc123"
        ctx = self.run_check({"id": rid, "question_id": "RQ-ECDLP-001"})
        self.assertEqual((ctx.errors, ctx.advisories), ([], []))

    def test_advisory_before_error_after(self):
        b = {"id": NEW_ID, "question_id": "RQ-ECDLP-001"}
        before = self.run_check(b, today="20261130")
        self.assertEqual(before.errors, [])
        self.assertTrue(before.advisories)
        after = self.run_check(b, today="2026-12-01")
        self.assertEqual(after.advisories, [])
        self.assertEqual(len(after.errors), 2)

    def test_area_field_used(self):
        ctx = self.run_check({"id": NEW_ID, "area": "ECDLP"})
        self.assertEqual(len(ctx.advisories), 2)

    def test_cli(self):
        import yaml
        path = os.path.join(self.root, NEW_ID + ".yaml")
        with open(path, "w") as fh:
            yaml.safe_dump({"idea": GOOD}, fh)
        with mock.patch("builtins.print"):
            self.assertEqual(cpa.main([path]), 0)
            bad = {k: v for k, v in GOOD.items() if k != "probe"}
            with open(path, "w") as fh:
                yaml.safe_dump(bad, fh)
            # advisory today (before 2026-12-01 unless clock is later)
            with mock.patch.object(cpa, "_date",
                                   lambda v=None: cpa._dt.date(2026, 12, 2)):
                self.assertEqual(cpa.main([path]), 1)


if __name__ == "__main__":
    unittest.main()
