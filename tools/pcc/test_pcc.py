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
                 "--proof", "certificate:cert.json"], self.repo)
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
                    "--proof", "attestation:artifact.txt"], self.repo)
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
