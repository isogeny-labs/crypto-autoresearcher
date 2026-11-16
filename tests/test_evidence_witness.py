"""Tests for tools/check_evidence_witness.py (review 2026-11-10, I6b).

    python3 tests/test_evidence_witness.py
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

import check_evidence_witness as cew  # noqa: E402
import validate_ledger                # noqa: E402

BEFORE, ADVISORY, ENFORCED = "2026-11-20", "2026-11-20", "2026-12-11"


def run_check(body: dict, today: str, root: str | None = None):
    ctx = validate_ledger.Ctx(legacy_paths=set())
    rid = body["id"]
    ctx.register(rid, os.path.join(REPO, "ledger", "evidence", rid + ".yaml"), body, "evidence")
    cew.check_evidence_witness(ctx, today, root)
    return ctx


def record(**kw) -> dict:
    base = {"id": "EV-T-001", "type": "empirical", "run_ids": ["RUN-T-001"], "recorded_at": "2026-11-12"}
    base.update(kw)
    return base


GOOD = {
    "sampled_replay": {"kind": "sampled_replay", "checker_path": "checker.py", "shares_code_with_driver": False,
                       "fraction": 0.1, "miss_probability": 0.01},
    "independent_reexecution": {"kind": "independent_reexecution", "second_implementation_path": "second.py",
                                "metric_agreement": True},
    "certificate": {"kind": "certificate", "verifier": "cairn", "certificate_path": "cert.json"},
}


class WitnessTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        for n in ("checker.py", "second.py", "cert.json"):
            open(os.path.join(self.td.name, n), "w").close()

    def tearDown(self):
        self.td.cleanup()

    def test_positive_each_kind(self):
        for kind, w in GOOD.items():
            ctx = run_check(record(witness=w), ENFORCED, self.td.name)
            self.assertEqual((ctx.errors, ctx.advisories), ([], []), kind)

    def test_missing_witness_is_advisory_then_error(self):
        ctx = run_check(record(), ADVISORY)
        self.assertEqual(ctx.errors, [])
        self.assertEqual(len(ctx.advisories), 1)
        self.assertIn("no `witness:` block", ctx.advisories[0])
        ctx = run_check(record(), ENFORCED)
        self.assertEqual(len(ctx.errors), 1)
        self.assertEqual(ctx.advisories, [])
        self.assertEqual(len(run_check(record(), "2026-12-10").errors), 0)

    def test_bad_kind(self):
        ctx = run_check(record(witness={"kind": "trust_me"}), ENFORCED)
        self.assertIn("witness.kind", ctx.errors[0])

    def test_sampled_replay_negatives(self):
        bad = [
            ({"shares_code_with_driver": True}, "shares_code_with_driver"),
            ({"shares_code_with_driver": None}, "shares_code_with_driver"),
            ({"fraction": 0}, "fraction"),
            ({"fraction": 1.5}, "fraction"),
            ({"fraction": True}, "fraction"),
            ({"miss_probability": 2}, "miss_probability"),
            ({"miss_probability": None}, "miss_probability"),
            ({"checker_path": ""}, "checker_path"),
            ({"checker_path": "absent.py"}, "checker_path"),
        ]
        for change, needle in bad:
            w = dict(GOOD["sampled_replay"], **change)
            ctx = run_check(record(witness=w), ENFORCED, self.td.name)
            self.assertTrue(any(needle in e for e in ctx.errors), (change, ctx.errors))
        w = dict(GOOD["sampled_replay"], fraction=1)
        self.assertEqual(run_check(record(witness=w), ENFORCED, self.td.name).errors, [])

    def test_reexecution_negatives(self):
        for change, needle in [({"metric_agreement": False}, "metric_agreement"),
                               ({"metric_agreement": {"agreed": False}}, "metric_agreement"),
                               ({"second_implementation_path": None}, "second_implementation_path")]:
            w = dict(GOOD["independent_reexecution"], **change)
            ctx = run_check(record(witness=w), ENFORCED, self.td.name)
            self.assertTrue(any(needle in e for e in ctx.errors), change)
        w = dict(GOOD["independent_reexecution"], metric_agreement={"agreed": True, "tolerance": 1e-9})
        self.assertEqual(run_check(record(witness=w), ENFORCED, self.td.name).errors, [])

    def test_certificate_negatives(self):
        for change, needle in [({"verifier": ""}, "verifier"), ({"certificate_path": "nope.json"}, "certificate_path")]:
            w = dict(GOOD["certificate"], **change)
            ctx = run_check(record(witness=w), ENFORCED, self.td.name)
            self.assertTrue(any(needle in e for e in ctx.errors), change)

    def test_pre_date_exempt(self):
        self.assertEqual(run_check(record(recorded_at="2026-11-10"), ENFORCED).errors, [])
        self.assertEqual(run_check(record(id="EV-T-20261105-aa", recorded_at=None), ENFORCED).errors, [])
        # A dateless record cannot be placed after the rule.
        self.assertEqual(run_check(record(recorded_at=None), ENFORCED).errors, [])
        # The date in the id counts when recorded_at is absent.
        self.assertEqual(len(run_check(record(id="EV-T-20261115-aa", recorded_at=None), ENFORCED).errors), 1)

    def test_non_measurement_claims_exempt(self):
        self.assertEqual(run_check(record(type="theoretical"), ENFORCED).errors, [])
        self.assertEqual(run_check(record(run_ids=[]), ENFORCED).errors, [])
        self.assertEqual(run_check(record(type="literature", run_ids=[]), ENFORCED).errors, [])

    def test_claims_entry_with_metrics_is_measurement(self):
        r = record(type="theoretical", run_ids=[], claims=[{"id": "C1", "metrics": {"gae": 12}}])
        self.assertEqual(len(run_check(r, ENFORCED).errors), 1)

    def test_other_record_kinds_ignored(self):
        ctx = validate_ledger.Ctx(legacy_paths=set())
        ctx.register("H-T-001", "x", record(id="H-T-001"), "hypothesis")
        cew.check_evidence_witness(ctx, ENFORCED)
        self.assertEqual(ctx.errors, [])

    def test_cli(self):
        path = os.path.join(self.td.name, "EV-T-001.yaml")
        with open(path, "w") as fh:
            yaml.safe_dump({"evidence": record(witness=GOOD["certificate"])}, fh)
        script = os.path.join(REPO, "tools", "check_evidence_witness.py")
        r = subprocess.run([sys.executable, script, path, "--today", ENFORCED, "--root", self.td.name],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        with open(path, "w") as fh:
            yaml.safe_dump({"evidence": record()}, fh)
        r = subprocess.run([sys.executable, script, path, "--today", ENFORCED], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1, r.stdout)
        r = subprocess.run([sys.executable, script, path, "--today", "2026-11-20"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("advisory:", r.stdout)


if __name__ == "__main__":
    unittest.main()
