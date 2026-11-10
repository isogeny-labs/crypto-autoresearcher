#!/usr/bin/env python3
"""Tests for tools/pcc/pcc.py: the canary corpus end to end through the CLI,
plus the producer/verifier round trip (keygen, claim new, verify, verdict,
ledger verify with a base, standing, lint-prose) in a scratch repository.

    python3 tools/pcc/test_pcc.py
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pcc  # noqa: E402

PCC = [sys.executable, str(HERE / "pcc.py")]


def run(args: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    e = dict(os.environ, PCC_REPO=str(cwd))
    if env:
        e.update(env)
    return subprocess.run(PCC + args, cwd=cwd, capture_output=True, text=True, env=e)


class Ed25519Tests(unittest.TestCase):
    def test_rfc8032_vector(self):
        # RFC 8032 section 7.1, test 1 (empty message).
        secret = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
        self.assertEqual(pcc.ed25519_public(secret).hex(),
                         "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a")
        sig = pcc.ed25519_sign(secret, b"")
        self.assertEqual(sig.hex(), "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
                                    "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b")
        self.assertTrue(pcc.ed25519_verify(pcc.ed25519_public(secret), b"", sig))
        self.assertFalse(pcc.ed25519_verify(pcc.ed25519_public(secret), b"x", sig))

    def test_cross_check_with_cryptography_when_available(self):
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        except ImportError:
            self.skipTest("cryptography not installed")
        secret = os.urandom(32)
        msg = b"pcc cross-check"
        theirs = Ed25519PrivateKey.from_private_bytes(secret)
        self.assertEqual(theirs.sign(msg), pcc.ed25519_sign(secret, msg))


class CanaryTests(unittest.TestCase):
    def test_every_sabotage_class_is_rejected(self):
        out = io.StringIO()
        rc = pcc.run_canary(out)
        self.assertEqual(rc, 0, out.getvalue())
        self.assertNotIn("WRONG", out.getvalue())


class RoundTripTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.repo = Path(self.td.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.email", "t@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.name", "t"], check=True)
        (self.repo / "pcc").mkdir()
        self.key = self.repo / "ci.key"
        r = run(["keygen", "--out", str(self.key), "--key-id", "ci-main"], self.repo)
        self.assertEqual(r.returncode, 0, r.stderr)
        pub = json.loads(r.stdout)
        (self.repo / pcc.KEYRING_PATH).write_text(json.dumps(
            {"schema": pcc.KEYRING_SCHEMA, "keys": [pub], "trusted_verifiers": []}))
        self.assertEqual(run(["ledger", "init"], self.repo).returncode, 0)
        self.commit("genesis")

    def tearDown(self):
        self.td.cleanup()

    def commit(self, msg: str) -> None:
        subprocess.run(["git", "-C", str(self.repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-q", "-m", msg], check=True)

    def make_solve(self) -> str:
        curve = pcc.Curve(pcc._SECP_P, 0, 7, pcc._SECP_N)
        k = 123456789
        Q = curve.mul(k, pcc._SECP_G)
        cert = {"schema": pcc.SOLVE_CERT_SCHEMA, "curve": {"p": pcc._SECP_P, "a": 0, "b": 7, "n": pcc._SECP_N},
                "P": list(pcc._SECP_G), "Q": list(Q), "k": k}
        (self.repo / "cert.json").write_text(json.dumps(cert))
        r = run(["claim", "new", "--kind", "solve", "--statement", "k is the discrete log of Q",
                 "--claim-type", "data", "--proof", "certificate:cert.json"], self.repo)
        self.assertEqual(r.returncode, 0, r.stderr)
        return Path(r.stdout.strip()).stem

    def test_claim_verify_verdict_standing(self):
        cid = self.make_solve()
        r = run(["verify", cid, "--json"], self.repo)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(json.loads(r.stdout)["verdict"], "pass")
        # Unsigned: the standing is unverified however the verify went.
        self.assertEqual(run(["standing", cid], self.repo).returncode, 2)
        r = run(["verdict", cid, "--sign-key", str(self.key), "--key-id", "ci-main"], self.repo)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = run(["standing", cid, "--json"], self.repo)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout)["standing"], "verified")
        # Editing the claim after the verdict drops it back to unverified.
        path = self.repo / pcc.CLAIMS_DIR / f"{cid}.json"
        c = json.loads(path.read_text())
        c["statement"] = "a stronger statement"
        path.write_text(json.dumps(c))
        self.assertEqual(run(["standing", cid], self.repo).returncode, 2)

    def test_verdict_refuses_a_key_outside_the_keyring(self):
        cid = self.make_solve()
        stranger = self.repo / "stranger.key"
        run(["keygen", "--out", str(stranger), "--key-id", "stranger"], self.repo)
        r = run(["verdict", cid, "--sign-key", str(stranger), "--key-id", "ci-main"], self.repo)
        self.assertEqual(r.returncode, 3)
        self.assertIn("not the keyring key", r.stderr)

    def test_attestation_path_shorthand_and_immutable_legacy_record(self):
        artifact = self.repo / "artifact.txt"
        artifact.write_text("producer observation, no independent signature\n")
        made = run(["claim", "new", "--kind", "statement", "--statement", "scoped observation",
                    "--claim-type", "data", "--proof", "attestation:artifact.txt"], self.repo)
        self.assertEqual(made.returncode, 0, made.stderr)
        path = self.repo / made.stdout.strip()
        claim = json.loads(path.read_text())
        self.assertEqual(claim["proofs"][0]["subject"],
                         {"path": "artifact.txt", "sha256": pcc.sha256_file(artifact)})
        checked = run(["verify", claim["id"], "--json"], self.repo)
        self.assertEqual(checked.returncode, 2, checked.stdout + checked.stderr)
        self.assertEqual(json.loads(checked.stdout)["verdict"], "not_covered")
        legacy = json.loads(path.read_text())
        legacy["proofs"][0].update(legacy["proofs"][0].pop("subject"))
        verdict = pcc.verify_claim(legacy, self.repo, pcc.load_keyring(self.repo / pcc.KEYRING_PATH))
        self.assertEqual(verdict["verdict"], "not_covered", verdict)
        self.assertEqual(json.loads(path.read_text()), claim)
        artifact.write_text("edited artifact\n")
        bad = pcc.verify_claim(legacy, self.repo, pcc.load_keyring(self.repo / pcc.KEYRING_PATH))
        self.assertEqual(bad["verdict"], "fail", bad)

    def test_ledger_prefix_against_base(self):
        cid = self.make_solve()
        self.commit("claim")
        subprocess.run(["git", "-C", str(self.repo), "checkout", "-q", "-b", "work"], check=True)
        run(["verdict", cid, "--sign-key", str(self.key), "--key-id", "ci-main"], self.repo)
        r = run(["ledger", "verify", "--base", "main"], self.repo)
        self.assertEqual(r.returncode, 0, r.stdout)
        # Rewrite history: drop the claim entry from the middle.
        led = self.repo / pcc.LEDGER_PATH
        lines = led.read_text().splitlines()
        led.write_text("\n".join([lines[0]] + lines[2:]) + "\n")
        r = run(["ledger", "verify", "--base", "main"], self.repo)
        self.assertEqual(r.returncode, 1)
        self.assertIn("seq", r.stdout)
        # Truncate below the base: chain is fine, prefix is not.
        led.write_text(lines[0] + "\n")
        r = run(["ledger", "verify", "--base", "main"], self.repo)
        self.assertEqual(r.returncode, 1)
        self.assertIn("history removed", r.stdout)

    def test_lint_prose_uses_ledger_standings(self):
        cid = self.make_solve()
        bad = f"This proves the log [pcc:{cid}].\n"
        r = subprocess.run(PCC + ["lint-prose", "--stdin"], input=bad, cwd=self.repo, capture_output=True,
                           text=True, env=dict(os.environ, PCC_REPO=str(self.repo)))
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("unverified", r.stdout)
        run(["verdict", cid, "--sign-key", str(self.key), "--key-id", "ci-main"], self.repo)
        r = subprocess.run(PCC + ["lint-prose", "--stdin"], input=bad, cwd=self.repo, capture_output=True,
                           text=True, env=dict(os.environ, PCC_REPO=str(self.repo)))
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_bypass_is_a_ledger_entry(self):
        r = run(["ledger", "append-bypass", "--reason", "smoke", "--command", "scripts/run_x.sh"], self.repo)
        self.assertEqual(r.returncode, 0, r.stderr)
        entries = pcc.read_ledger(self.repo / pcc.LEDGER_PATH)
        self.assertEqual(entries[-1]["type"], "bypass")
        self.assertEqual(entries[-1]["body"]["reason"], "smoke")
        self.assertEqual(run(["ledger", "verify"], self.repo).returncode, 0)

    def test_broken_ledger_refuses_appends(self):
        led = self.repo / pcc.LEDGER_PATH
        led.write_text(led.read_text().replace('"type":"genesis"', '"type":"note"'))
        r = run(["ledger", "append-bypass", "--reason", "x", "--command", "y"], self.repo)
        self.assertEqual(r.returncode, 3)
        self.assertIn("broken ledger", r.stderr)


class ClaimTypeTests(unittest.TestCase):
    setUp = RoundTripTests.setUp
    tearDown = RoundTripTests.tearDown
    commit = RoundTripTests.commit
    make_solve = RoundTripTests.make_solve
    """claim_type, ledger verify, standing-by-type, sample-for-validation."""

    def write_claim(self, cid: str, created: str, claim_type: str | None, kind: str = "statement") -> None:
        c = {"schema": pcc.CLAIM_SCHEMA, "id": cid, "kind": kind, "statement": "s", "scope": "", "proofs": [],
             "producer": {"commit": "a" * 40, "session": "", "model": ""}, "created_at": created}
        if claim_type:
            c["claim_type"] = claim_type
        (self.repo / pcc.CLAIMS_DIR).mkdir(parents=True, exist_ok=True)
        (self.repo / pcc.CLAIMS_DIR / f"{cid}.json").write_text(json.dumps(c))

    def test_legacy_claim_without_type_is_data(self):
        self.write_claim("PCC-20261105-aaaaaa", "2026-11-05T00:00:00Z", None)
        r = run(["ledger", "verify"], self.repo)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(json.loads(run(["standing-by-type", "--json"], self.repo).stdout)["data"],
                         {"unverified": 1})

    def test_new_claim_without_type_fails_ledger_verify(self):
        self.write_claim("PCC-20261112-bbbbbb", "2026-11-12T00:00:00Z", None)
        r = run(["ledger", "verify"], self.repo)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("claim_type is missing", r.stdout)

    def test_backdated_created_at_does_not_exempt(self):
        self.write_claim("PCC-20261112-cccccc", "2026-01-01T00:00:00Z", None)
        self.assertEqual(run(["ledger", "verify"], self.repo).returncode, 1)

    def test_invalid_type_fails_and_valid_new_passes(self):
        self.write_claim("PCC-20261112-dddddd", "2026-11-12T00:00:00Z", "opinion")
        self.assertEqual(run(["ledger", "verify"], self.repo).returncode, 1)
        self.write_claim("PCC-20261112-dddddd", "2026-11-12T00:00:00Z", "literature")
        self.assertEqual(run(["ledger", "verify"], self.repo).returncode, 0)

    def test_validate_claim_rejects_new_untyped(self):
        reasons: list[str] = []
        c = {"schema": pcc.CLAIM_SCHEMA, "id": "PCC-20261112-eeeeee", "kind": "statement", "statement": "s",
             "proofs": [], "producer": {"commit": "a" * 40}, "created_at": "2026-11-12T00:00:00Z"}
        self.assertFalse(pcc.validate_claim(c, reasons))
        self.assertTrue(any("claim_type" in r for r in reasons))
        self.assertTrue(pcc.validate_claim(dict(c, claim_type="interpretive"), []))

    def test_claim_new_records_type(self):
        cid = self.make_solve()
        c = json.loads((self.repo / pcc.CLAIMS_DIR / f"{cid}.json").read_text())
        self.assertEqual(c["claim_type"], "data")

    def populate(self):
        for i in range(30):
            self.write_claim(f"PCC-20261112-{i:06x}", "2026-11-12T00:00:00Z",
                             ("data", "literature", "interpretive")[i % 3])

    def test_standing_by_type_counts(self):
        self.populate()
        r = run(["standing-by-type"], self.repo)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("data: 10 claim(s): unverified=10", r.stdout)
        self.assertIn("interpretive: 10 claim(s): unverified=10", r.stdout)

    def test_sample_is_seeded_stratified_and_oversamples_interpretive(self):
        self.populate()
        out = self.repo / "sample.json"
        args = ["sample-for-validation", "--rate-data", "1", "--rate-interpretive", "3", "--seed", "7",
                "--base", "0.2", "--out", str(out)]
        self.assertEqual(run(args, self.repo).returncode, 0)
        first = out.read_text()
        run(args, self.repo)
        self.assertEqual(out.read_text(), first)  # deterministic given the seed
        s = json.loads(first)
        self.assertAlmostEqual(s["strata"]["interpretive"]["probability"], 0.6)
        self.assertAlmostEqual(s["strata"]["data"]["probability"], 0.2)
        for t in pcc.CLAIM_TYPES:
            self.assertGreaterEqual(s["strata"][t]["sampled"], 1)
        self.assertEqual(len(s["claims"]), sum(v["sampled"] for v in s["strata"].values()))
        # Across seeds the interpretive stratum is drawn more often than data.
        tot = {"data": 0, "interpretive": 0}
        for seed in range(40):
            st = pcc.sample_for_validation(self.repo, pcc.load_keyring(self.repo / pcc.KEYRING_PATH),
                                           1, 3, seed, base=0.2)["strata"]
            for t in tot:
                tot[t] += st[t]["sampled"]
        self.assertGreater(tot["interpretive"], 2 * tot["data"])

    def test_sample_refuses_under_3x(self):
        self.populate()
        r = run(["sample-for-validation", "--rate-data", "1", "--rate-interpretive", "2", "--seed", "1",
                 "--out", str(self.repo / "x.json")], self.repo)
        self.assertEqual(r.returncode, 3)
        self.assertIn("3x", r.stderr)


class LeanScanTests(unittest.TestCase):
    def test_comment_and_string_lookalikes_are_not_holes(self):
        src = "theorem t : 1 = 1 := rfl\n-- sorry here is a comment\n/- block sorry -/\ndef s := \"sorry\"\n"
        text = pcc.strip_lean_comments_and_strings(src)
        self.assertIsNone(pcc.LEAN_HOLE_RES["sorry"].search(text))
        self.assertIsNotNone(pcc.LEAN_HOLE_RES["sorry"].search(pcc.strip_lean_comments_and_strings(
            "theorem t : 1 = 1 := by sorry\n")))

    def test_declaration_binding_ignores_whitespace_but_not_content(self):
        a = pcc.lean_find_declaration.__wrapped__ if hasattr(pcc.lean_find_declaration, "__wrapped__") else None
        self.assertIsNone(a)
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "A.lean"
            p.write_text("theorem foo (n : Nat) :\n    n + 0 = n := by simp\n")
            _, s1 = pcc.lean_find_declaration([p], "foo")
            p.write_text("theorem foo (n : Nat) : n + 0 = n := by simp\n")
            _, s2 = pcc.lean_find_declaration([p], "foo")
            self.assertEqual(s1, s2)
            p.write_text("theorem foo (n : Nat) : n + 1 = n := by simp\n")
            _, s3 = pcc.lean_find_declaration([p], "foo")
            self.assertNotEqual(s1, s3)


if __name__ == "__main__":
    unittest.main(verbosity=1)
