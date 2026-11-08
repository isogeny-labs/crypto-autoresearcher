#!/usr/bin/env python3
"""Tests for tools/ledger_vocabulary.py and the validator's vocabulary rules."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import ledger_vocabulary as vocab  # noqa: E402
import validate_ledger as vl  # noqa: E402

# New-error lines the validator reported on the repository before the
# vocabulary rules were added (recorded by running it at the start). The rules
# must add nothing to this set.
PRE_EXISTING_NEW_ERRORS = {
    "experiments/EXP-BINSTD-591d28/runs/RUN-BINSTD-f7ca97/manifest.yaml: "
    "expected top-level key 'run'",
}

BEFORE = "2026-11-07"
AFTER = vocab.VOCABULARY_CUTOFF


class CanonicalSetTests(unittest.TestCase):
    def test_hypothesis_status_is_the_agents_state_list_plus_rejected_scoped(self):
        self.assertEqual(
            vocab.canonical("hypothesis_status"),
            frozenset(vocab.HYPOTHESIS_STATES) | {"rejected_scoped"})
        for value in ("approved", "analyzed", "running", "replicated",
                      "rejected", "inconclusive"):
            self.assertIn(value, vocab.canonical("hypothesis_status"))
        for retired in ("active", "paused"):
            self.assertNotIn(retired, vocab.canonical("hypothesis_status"))

    def test_schema_enums_match_fallbacks(self):
        schemas = REPO / "schemas"
        hyp = json.loads((schemas / "hypothesis.schema.json").read_text())
        ev = json.loads((schemas / "evidence.schema.json").read_text())
        self.assertEqual(
            set(hyp["properties"]["hypothesis"]["properties"]["status"]["enum"]),
            vocab.HYPOTHESIS_STATUSES_FALLBACK)
        props = ev["properties"]["evidence"]["properties"]
        self.assertEqual(set(props["direction"]["enum"]),
                         vocab.EVIDENCE_DIRECTIONS_FALLBACK)
        self.assertEqual(set(props["strength"]["enum"]),
                         vocab.EVIDENCE_STRENGTHS_FALLBACK)

    def test_experiment_statuses(self):
        expected = {"draft", "review_required", "approved", "running",
                    "completed", "failed_infrastructure", "invalid",
                    "analyzed", "archived", "amended", "cancelled"}
        self.assertEqual(vocab.canonical("experiment_status"), expected)

    def test_tiers_and_proof_statuses(self):
        self.assertTrue({"toy", "theory", "medium", "crypto"}
                        <= vocab.canonical("claim_tier"))
        self.assertEqual(vocab.canonical("proof_status"),
                         {"empirical_only", "derivation", "certificate",
                          "not_applicable"})
        self.assertEqual(vl.PROOF_STATUSES, set(vocab.canonical("proof_status")))

    def test_every_legacy_target_is_canonical(self):
        for kind, mapping in vocab.LEGACY.items():
            for source, target in mapping.items():
                self.assertIn(target, vocab.canonical(kind), (kind, source))
                self.assertNotIn(source, vocab.canonical(kind), (kind, source))


class NormalizeTests(unittest.TestCase):
    def test_canonical_maps_to_itself(self):
        for kind in vocab.kinds():
            for value in vocab.canonical(kind):
                self.assertEqual(vocab.normalize(kind, value), value)

    def test_rejected_and_rejected_scoped_are_both_canonical(self):
        self.assertEqual(vocab.normalize("hypothesis_status", "rejected"), "rejected")
        self.assertEqual(vocab.normalize("hypothesis_status", "rejected_scoped"),
                         "rejected_scoped")

    def test_legacy_variants(self):
        self.assertEqual(vocab.normalize("claim_tier", "toy_measurement"), "toy")
        self.assertEqual(vocab.normalize("claim_tier", "theoretical"), "theory")
        self.assertEqual(vocab.normalize("evidence_direction", "refutes"), "contradicts")
        self.assertEqual(vocab.normalize("evidence_direction", "Supports"), "supports")
        self.assertEqual(vocab.normalize("experiment_status", "executed"), "completed")
        self.assertEqual(vocab.normalize("proof_status", "derivation_repaired"),
                         "derivation")

    def test_ambiguous_values_do_not_normalize(self):
        self.assertIsNone(vocab.normalize("claim_tier", "measured-single-host"))
        self.assertIsNone(vocab.normalize("evidence_direction", "mixed"))
        self.assertIsNone(vocab.normalize("evidence_strength", "moderate"))
        self.assertIsNone(vocab.normalize("hypothesis_status", None))
        self.assertIsNone(vocab.normalize("hypothesis_status", 3))

    def test_record_date_precedence(self):
        body = {"id": "EV-X-20260101-001", "created": "2026-11-09",
                "recorded_at": "2026-01-01T00:00:00Z"}
        self.assertEqual(vocab.record_date(body, vl._id_date), "2026-11-09")
        self.assertEqual(vocab.record_date({"id": "DEC-20261108-abc"}, vl._id_date),
                         "2026-11-08")
        self.assertIsNone(vocab.record_date({"id": "H-X-abcdef"}, vl._id_date))


class _RecordCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ctx = vl.Ctx(set())

    def tearDown(self):
        self.tmp.cleanup()

    def _record(self, rec_type: str, body: dict) -> str:
        path = os.path.join(self.tmp.name, f"{body['id']}.yaml")
        with open(path, "w", encoding="utf-8") as fh:
            yaml.safe_dump({rec_type: body}, fh)
        return path

    def _check(self, rec_type: str, body: dict) -> None:
        path = self._record(rec_type, body)
        doc = yaml.safe_load(Path(path).read_text())
        vl.check_vocabulary(path, doc[rec_type], rec_type, self.ctx)


class CheckVocabularyTests(_RecordCase):
    def test_old_record_is_an_advisory_not_an_error(self):
        self._check("hypothesis", {"id": "H-VOC-001", "status": "paused",
                                   "created": BEFORE})
        self._check("hypothesis", {"id": "H-VOC-002", "status": "paused",
                                   "created": BEFORE})
        self._check("evidence", {"id": "EV-VOC-001", "direction": "mixed",
                                 "strength": "moderate", "claim_tier": "toy",
                                 "created": BEFORE})
        self.assertEqual(self.ctx.errors, [])
        vl.report_vocabulary_advisories(self.ctx)
        lines = [a for a in self.ctx.advisories if "vocabulary" in a]
        self.assertEqual(len(lines), 3)  # one per (type, field), not per record
        status = [a for a in lines if "hypothesis.status" in a]
        self.assertEqual(len(status), 1)
        self.assertIn("paused=2", status[0])

    def test_new_record_is_an_error(self):
        self._check("hypothesis", {"id": "H-VOC-003", "status": "paused",
                                   "created": AFTER})
        self.assertEqual(len(self.ctx.errors), 1)
        self.assertIn("status 'paused' is not in the hypothesis status vocabulary",
                      self.ctx.errors[0])
        self.assertIn("use one of", self.ctx.errors[0])

    def test_new_record_error_names_the_normalization(self):
        self._check("evidence", {"id": "EV-VOC-002", "direction": "neutral",
                                 "strength": "preliminary",
                                 "claim_tier": "toy_measurement",
                                 "updated": AFTER})
        self.assertEqual(len(self.ctx.errors), 1)
        self.assertIn("claim_tier 'toy_measurement'", self.ctx.errors[0])
        self.assertIn("use 'toy'", self.ctx.errors[0])

    def test_new_experiment_status(self):
        self._check("experiment", {"id": "EXP-VOC-001", "status": "executed",
                                   "approved_at": AFTER})
        self.assertEqual(len(self.ctx.errors), 1)
        self.assertIn("use 'completed'", self.ctx.errors[0])
        self.ctx.errors.clear()
        self._check("experiment", {"id": "EXP-VOC-002", "status": "approved",
                                   "approved_at": AFTER})
        self.assertEqual(self.ctx.errors, [])

    def test_canonical_new_record_is_clean(self):
        self._check("evidence", {"id": "EV-VOC-003", "direction": "weakens",
                                 "strength": "replicated", "claim_tier": "medium",
                                 "proof_status": "empirical_only",
                                 "created": AFTER})
        self.assertEqual(self.ctx.errors, [])

    def test_undated_record_is_treated_as_legacy(self):
        self._check("hypothesis", {"id": "H-VOC-004", "status": "paused"})
        self.assertEqual(self.ctx.errors, [])


class PositiveControlTests(_RecordCase):
    MSG = ("supporting evidence at tier medium names no positive control; "
           "the instrument is uncalibrated")

    def _ev(self, **extra):
        body = {"id": "EV-PC-001", "direction": "supports",
                "strength": "preliminary", "claim_tier": "medium",
                "created": AFTER}
        body.update(extra)
        return body

    def test_uncalibrated_support_fails(self):
        self._check("evidence", self._ev())
        self.assertEqual(len(self.ctx.errors), 1)
        self.assertTrue(self.ctx.errors[0].endswith(self.MSG), self.ctx.errors)

    def test_each_control_field_satisfies(self):
        for extra in ({"controls": {"positive": "planted-solution arm"}},
                      {"positive_control": ["EXP-PC-001 planted arm"]},
                      {"instrument_calibration": {"ref": "RUN-PC-001"}}):
            self.ctx.errors.clear()
            self._check("evidence", self._ev(**extra))
            self.assertEqual(self.ctx.errors, [], extra)

    def test_empty_control_does_not_satisfy(self):
        self._check("evidence", self._ev(controls={"positive": []}))
        self.assertEqual(len(self.ctx.errors), 1)

    def test_toy_tier_old_record_and_other_directions_are_exempt(self):
        self._check("evidence", self._ev(claim_tier="toy"))
        self._check("evidence", self._ev(direction="weakens"))
        self._check("evidence", self._ev(created=BEFORE))
        self.assertEqual(self.ctx.errors, [])

    def test_crypto_tier(self):
        self._check("evidence", self._ev(claim_tier="crypto"))
        self.assertEqual(len(self.ctx.errors), 1)
        self.assertIn("at tier crypto", self.ctx.errors[0])


class HistogramTests(unittest.TestCase):
    def test_record_body_shapes(self):
        self.assertIsNone(vocab.record_body("a bare string", "hypothesis"))
        self.assertIsNone(vocab.record_body(None, "hypothesis"))
        self.assertEqual(vocab.record_body({"hypothesis": {"status": "x"}},
                                           "hypothesis"), {"status": "x"})
        self.assertEqual(vocab.record_body({"status": "x"}, "hypothesis"),
                         {"status": "x"})

    def test_histogram_on_a_temp_repo(self):
        with tempfile.TemporaryDirectory() as root:
            hyp = Path(root, "ledger", "hypotheses")
            hyp.mkdir(parents=True)
            (hyp / "H-A-001.yaml").write_text("hypothesis:\n  status: approved\n")
            (hyp / "H-A-002.yaml").write_text("status: analyzed\n")
            (hyp / "H-A-003.yaml").write_text("just a string\n")
            (hyp / "H-A-004.yaml").write_text("hypothesis: [unclosed\n")
            result = vocab.histogram(root)
            counts = result["counts"][("hypothesis", "status")]
            self.assertEqual(counts, {"approved": 1, "analyzed": 1})
            self.assertEqual(result["files"]["hypothesis"]["skipped"], 2)

    def test_cli_vocabulary_flag_exits_zero(self):
        result = subprocess.run(
            [sys.executable, str(REPO / "tools" / "validate_ledger.py"),
             "--vocabulary"], cwd=REPO, text=True, capture_output=True,
            check=False, timeout=600)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("hypothesis.status", result.stdout)
        self.assertIn("evidence.claim_tier", result.stdout)


class RepositoryIntegrationTests(unittest.TestCase):
    def test_no_new_error_beyond_the_pre_existing_set(self):
        result = subprocess.run(
            [sys.executable, str(REPO / "tools" / "validate_ledger.py")],
            cwd=REPO, text=True, capture_output=True, check=False, timeout=1200)
        self.assertIn(result.returncode, (0, 1), result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        new = {line.strip()[2:] for line in result.stderr.splitlines()
               if line.strip().startswith("- ")}
        self.assertFalse(
            {e for e in new if "vocabulary" in e or "positive control" in e},
            new)
        self.assertLessEqual(new, PRE_EXISTING_NEW_ERRORS, new - PRE_EXISTING_NEW_ERRORS)


if __name__ == "__main__":
    unittest.main()
