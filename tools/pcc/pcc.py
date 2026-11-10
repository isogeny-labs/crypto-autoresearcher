#!/usr/bin/env python3
"""pcc: proof-carrying claims.

Contract: docs/SABOTAGE_RESISTANCE.md. Every producer is assumed to be
sabotaging the work, so a claim is only what its proofs establish, verified
by code the producer did not write, and recorded in an append-only,
hash-chained ledger whose verdicts are signed by a key the producer does not
hold.

This file is kept byte-identical across the lab's repositories by the
shared-code lock (tools/check_lab_parity.py). It has no dependency beyond the
Python 3.11 standard library; Ed25519 is the RFC 8032 reference
implementation, so a verdict verifies the same way on every host.

    pcc keygen --out KEYFILE --key-id ID            # prints the public key
    pcc claim new --kind solve --statement S --proof certificate:PATH ...
    pcc verify CLAIM [--json]                        # pcc.verdict/v1 on stdout
    pcc verify-all [--json]
    pcc verdict --sign-key KEYFILE --key-id ID CLAIM # verify, sign, append
    pcc sign --sign-key KEYFILE --key-id ID ARTIFACT # ARTIFACT.sig.json
    pcc ledger verify [--base GITREF]
    pcc ledger append-bypass --reason R --command C
    pcc standing CLAIM-ID
    pcc standing-by-type [--json]                    # standings per claim_type
    pcc sample-for-validation --rate-data R --rate-interpretive R --seed N --out FILE
    pcc lint-prose FILE... | --stdin
    pcc canary                                       # the sabotage corpus

Exit status: 0 pass, 1 fail, 2 not covered (nothing failed, something could
not be checked), 3 usage or infrastructure error.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

CLAIM_SCHEMA = "pcc.claim/v1"
VERDICT_SCHEMA = "pcc.verdict/v1"
LEDGER_SCHEMA = "pcc.ledger-entry/v1"
KEYRING_SCHEMA = "pcc.keyring/v1"
SIGNATURE_SCHEMA = "pcc.signature/v1"
SOLVE_CERT_SCHEMA = "pcc.solve-certificate/v1"
ZK_SOLVE_CERT_SCHEMA = "pcc.zk-solve-certificate/v1"

CLAIM_KINDS = {"theorem", "solve", "measurement", "speedup", "execution", "absence", "statement"}
PROOF_KINDS = {"lean", "certificate", "zk-certificate", "replay", "recompute", "execution", "attestation"}
# Minimum proof kinds per claim kind (docs/SABOTAGE_RESISTANCE.md, section 4).
# A list means "any of these"; every list must be satisfied.
MINIMUM_PROOFS: dict[str, list[list[str]]] = {
    "theorem": [["lean"]],
    "solve": [["certificate", "zk-certificate"]],
    "measurement": [["recompute"], ["replay"]],
    "speedup": [["recompute"], ["replay"]],
    "execution": [["execution"]],
    "absence": [["execution", "lean"]],
    "statement": [],
}
# Claim types (review 2026-11-10, I11): validation effort is stratified by what
# kind of statement a claim is. Claims created before CLAIM_TYPE_REQUIRED_FROM
# may omit the field and count as `data`; newer claims must carry it.
CLAIM_TYPES = ("data", "literature", "interpretive")
CLAIM_TYPE_REQUIRED_FROM = "2026-11-11"
STANDARD_AXIOMS = ("propext", "Classical.choice", "Quot.sound")
STRONG_CLAIM_RE = re.compile(
    r"\b(prove[sd]?|verified|verifies|beats?|breakthrough|speed-?ups?|faster|secure|weak curves?|"
    r"improve[sd]?|improvement|solved|solves|broken|breaks)\b", re.IGNORECASE)
CITATION_RE = re.compile(r"\[pcc:(PCC-[0-9]{8}-[0-9a-f]{6}|unverified)\]")
CLAIM_ID_RE = re.compile(r"^PCC-[0-9]{8}-[0-9a-f]{6}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")

PCC_DIR = "pcc"
CLAIMS_DIR = "pcc/claims"
LEDGER_PATH = "pcc/ledger.jsonl"
KEYRING_PATH = "pcc/keyring.json"


# ----------------------------------------------------------------------------
# Canonical bytes, digests, time
# ----------------------------------------------------------------------------

def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_obj(obj: Any) -> str:
    return sha256_bytes(canonical(obj))


def utcnow() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git(repo: Path, *args: str) -> str | None:
    try:
        return subprocess.check_output(["git", "-C", str(repo), *args], text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def head_commit(repo: Path) -> str:
    return git(repo, "rev-parse", "HEAD") or "0" * 40


def repo_root(start: Path | None = None) -> Path:
    env = os.environ.get("PCC_REPO")
    if env:
        return Path(env).resolve()
    here = (start or Path(__file__)).resolve()
    top = git(here if here.is_dir() else here.parent, "rev-parse", "--show-toplevel")
    return Path(top).resolve() if top else here.parents[2]


class PccError(Exception):
    """Usage or infrastructure error (exit 3)."""


# ----------------------------------------------------------------------------
# Ed25519 (RFC 8032, reference implementation; no third-party dependency)
# ----------------------------------------------------------------------------

_P = 2 ** 255 - 19
_D = -121665 * pow(121666, _P - 2, _P) % _P
_Q = 2 ** 252 + 27742317777372353535851937790883648493
_SQRT_M1 = pow(2, (_P - 1) // 4, _P)


def _sha512_modq(s: bytes) -> int:
    return int.from_bytes(hashlib.sha512(s).digest(), "little") % _Q


def _ed_add(P, Q):
    A = (P[1] - P[0]) * (Q[1] - Q[0]) % _P
    B = (P[1] + P[0]) * (Q[1] + Q[0]) % _P
    C = 2 * P[3] * Q[3] * _D % _P
    D = 2 * P[2] * Q[2] % _P
    E, F, G, H = B - A, D - C, D + C, B + A
    return (E * F % _P, G * H % _P, F * G % _P, E * H % _P)


def _ed_mul(s: int, P):
    Q = (0, 1, 1, 0)
    while s > 0:
        if s & 1:
            Q = _ed_add(Q, P)
        P = _ed_add(P, P)
        s >>= 1
    return Q


def _ed_equal(P, Q) -> bool:
    return (P[0] * Q[2] - Q[0] * P[2]) % _P == 0 and (P[1] * Q[2] - Q[1] * P[2]) % _P == 0


def _recover_x(y: int, sign: int):
    if y >= _P:
        return None
    x2 = (y * y - 1) * pow(_D * y * y + 1, _P - 2, _P)
    if x2 == 0:
        return None if sign else 0
    x = pow(x2, (_P + 3) // 8, _P)
    if (x * x - x2) % _P != 0:
        x = x * _SQRT_M1 % _P
    if (x * x - x2) % _P != 0:
        return None
    if (x & 1) != sign:
        x = _P - x
    return x


_GY = 4 * pow(5, _P - 2, _P) % _P
_GX = _recover_x(_GY, 0)
_G = (_GX, _GY, 1, _GX * _GY % _P)


def _ed_compress(P) -> bytes:
    zinv = pow(P[2], _P - 2, _P)
    x, y = P[0] * zinv % _P, P[1] * zinv % _P
    return int.to_bytes(y | ((x & 1) << 255), 32, "little")


def _ed_decompress(s: bytes):
    if len(s) != 32:
        return None
    y = int.from_bytes(s, "little")
    sign = y >> 255
    y &= (1 << 255) - 1
    x = _recover_x(y, sign)
    return None if x is None else (x, y, 1, x * y % _P)


def _secret_expand(secret: bytes):
    if len(secret) != 32:
        raise PccError("an Ed25519 secret key is 32 bytes")
    h = hashlib.sha512(secret).digest()
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= 1 << 254
    return a, h[32:]


def ed25519_public(secret: bytes) -> bytes:
    a, _ = _secret_expand(secret)
    return _ed_compress(_ed_mul(a, _G))


def ed25519_sign(secret: bytes, msg: bytes) -> bytes:
    a, prefix = _secret_expand(secret)
    A = _ed_compress(_ed_mul(a, _G))
    r = _sha512_modq(prefix + msg)
    Rs = _ed_compress(_ed_mul(r, _G))
    h = _sha512_modq(Rs + A + msg)
    s = (r + h * a) % _Q
    return Rs + int.to_bytes(s, 32, "little")


def ed25519_verify(public: bytes, msg: bytes, signature: bytes) -> bool:
    if len(public) != 32 or len(signature) != 64:
        return False
    A = _ed_decompress(public)
    R = _ed_decompress(signature[:32])
    if A is None or R is None:
        return False
    s = int.from_bytes(signature[32:], "little")
    if s >= _Q:
        return False
    h = _sha512_modq(signature[:32] + public + msg)
    return _ed_equal(_ed_mul(s, _G), _ed_add(R, _ed_mul(h, A)))


# ----------------------------------------------------------------------------
# Keyring and signatures
# ----------------------------------------------------------------------------

def empty_keyring() -> dict[str, Any]:
    return {"schema": KEYRING_SCHEMA, "keys": [], "trusted_verifiers": []}


def load_keyring(path: Path | None) -> dict[str, Any]:
    if path is None or not path.is_file():
        return empty_keyring()
    kr = load_json(path)
    if not isinstance(kr, dict) or kr.get("schema") != KEYRING_SCHEMA:
        raise PccError(f"{path}: not a {KEYRING_SCHEMA} keyring")
    kr.setdefault("keys", [])
    kr.setdefault("trusted_verifiers", [])
    return kr


def keyring_public(kr: dict[str, Any], key_id: str) -> bytes | None:
    for k in kr.get("keys", []):
        if k.get("id") == key_id and k.get("algo") == "ed25519" and k.get("revoked") is not True:
            try:
                return bytes.fromhex(k["public_key"])
            except (KeyError, ValueError):
                return None
    return None


def signature_message(subject_kind: str, subject_sha256: str, key_id: str) -> bytes:
    return b"pcc.signature/v1\n" + canonical({"key_id": key_id, "subject_kind": subject_kind,
                                               "subject_sha256": subject_sha256})


def make_signature(secret: bytes, key_id: str, subject_kind: str, subject_sha256: str) -> dict[str, Any]:
    sig = ed25519_sign(secret, signature_message(subject_kind, subject_sha256, key_id))
    return {"schema": SIGNATURE_SCHEMA, "key_id": key_id, "subject_kind": subject_kind,
            "subject_sha256": subject_sha256, "signature": sig.hex(), "signed_at": utcnow()}


def check_signature(sig: Any, kr: dict[str, Any], subject_kind: str, subject_sha256: str,
                    reasons: list[str], what: str) -> bool:
    if not isinstance(sig, dict) or sig.get("schema") != SIGNATURE_SCHEMA:
        reasons.append(f"{what}: no {SIGNATURE_SCHEMA} signature")
        return False
    if sig.get("subject_kind") != subject_kind or sig.get("subject_sha256") != subject_sha256:
        reasons.append(f"{what}: signature is over a different subject")
        return False
    pub = keyring_public(kr, str(sig.get("key_id")))
    if pub is None:
        reasons.append(f"{what}: key {sig.get('key_id')!r} is not in the keyring")
        return False
    try:
        raw = bytes.fromhex(str(sig.get("signature")))
    except ValueError:
        reasons.append(f"{what}: signature is not hex")
        return False
    if not ed25519_verify(pub, signature_message(subject_kind, subject_sha256, str(sig["key_id"])), raw):
        reasons.append(f"{what}: signature does not verify under key {sig['key_id']}")
        return False
    return True


def read_secret(path: Path) -> bytes:
    text = path.read_text(encoding="utf-8").strip()
    try:
        secret = bytes.fromhex(text)
    except ValueError as e:
        raise PccError(f"{path}: secret key must be 64 hex characters") from e
    if len(secret) != 32:
        raise PccError(f"{path}: secret key must be 32 bytes")
    return secret


# ----------------------------------------------------------------------------
# Prime-field elliptic curves (verifier arithmetic; shares no code with any producer)
# ----------------------------------------------------------------------------

def is_probable_prime(n: int, rounds: int = 40) -> bool:
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for s in small:
        if n % s == 0:
            return n == s
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    bases = list(small) if n < 3_317_044_064_679_887_385_961_981 else list(small) + [
        secrets.randbelow(n - 3) + 2 for _ in range(rounds)]
    for a in bases:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


class Curve:
    """y^2 = x^3 + a x + b over GF(p), affine, None is the point at infinity."""

    def __init__(self, p: int, a: int, b: int, n: int):
        if not all(isinstance(v, int) and not isinstance(v, bool) for v in (p, a, b, n)):
            raise ValueError("curve parameters must be integers")
        if p < 5 or n < 2:
            raise ValueError("curve parameters out of range")
        if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
            raise ValueError("singular curve")
        self.p, self.a, self.b, self.n = p, a % p, b % p, n

    def on_curve(self, P) -> bool:
        if P is None:
            return True
        x, y = P
        if not (0 <= x < self.p and 0 <= y < self.p):
            return False
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0

    def add(self, P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        p = self.p
        if P[0] == Q[0]:
            if (P[1] + Q[1]) % p == 0:
                return None
            lam = (3 * P[0] * P[0] + self.a) * pow(2 * P[1], p - 2, p) % p
        else:
            lam = (Q[1] - P[1]) * pow(Q[0] - P[0], p - 2, p) % p
        x = (lam * lam - P[0] - Q[0]) % p
        return (x, (lam * (P[0] - x) - P[1]) % p)

    def mul(self, k: int, P):
        if k < 0:
            raise ValueError("negative scalar")
        R = None
        while k:
            if k & 1:
                R = self.add(R, P)
            P = self.add(P, P)
            k >>= 1
        return R

    def neg(self, P):
        return None if P is None else (P[0], (-P[1]) % self.p)


def _point(v: Any):
    if v is None:
        return None
    if (isinstance(v, (list, tuple)) and len(v) == 2
            and all(isinstance(c, int) and not isinstance(c, bool) for c in v)):
        return (int(v[0]), int(v[1]))
    raise ValueError(f"not a point: {v!r}")


def _curve_from(cert: dict[str, Any], reasons: list[str]) -> Curve | None:
    c = cert.get("curve")
    if not isinstance(c, dict):
        reasons.append("certificate: no curve")
        return None
    try:
        curve = Curve(c["p"], c["a"], c["b"], c["n"])
    except (KeyError, ValueError, TypeError) as e:
        reasons.append(f"certificate: bad curve ({e})")
        return None
    if not is_probable_prime(curve.p):
        reasons.append("certificate: p is not prime")
        return None
    if not is_probable_prime(curve.n):
        reasons.append("certificate: group order n is not prime")
        return None
    return curve


def _instance(cert: dict[str, Any], reasons: list[str]):
    curve = _curve_from(cert, reasons)
    if curve is None:
        return None
    try:
        P, Q = _point(cert.get("P")), _point(cert.get("Q"))
    except ValueError as e:
        reasons.append(f"certificate: {e}")
        return None
    if P is None or Q is None:
        reasons.append("certificate: P and Q must be affine points")
        return None
    if not curve.on_curve(P):
        reasons.append("certificate: P is not on the curve")
    if not curve.on_curve(Q):
        reasons.append("certificate: Q is not on the curve")
    if reasons:
        return None
    if curve.mul(curve.n, P) is not None:
        reasons.append("certificate: [n]P is not the point at infinity")
        return None
    return curve, P, Q


def verify_solve_certificate(cert: Any, reasons: list[str]) -> bool:
    if not isinstance(cert, dict) or cert.get("schema") != SOLVE_CERT_SCHEMA:
        reasons.append(f"certificate: schema is not {SOLVE_CERT_SCHEMA}")
        return False
    inst = _instance(cert, reasons)
    if inst is None:
        return False
    curve, P, Q = inst
    k = cert.get("k")
    if not isinstance(k, int) or isinstance(k, bool) or not (1 <= k < curve.n):
        reasons.append("certificate: k is not an integer in [1, n)")
        return False
    if curve.mul(k, P) != Q:
        reasons.append("certificate: [k]P != Q")
        return False
    return True


def schnorr_challenge(curve: Curve, P, Q, R) -> int:
    msg = b"pcc.zk-solve/v1\n" + canonical({"p": curve.p, "a": curve.a, "b": curve.b, "n": curve.n,
                                             "P": list(P), "Q": list(Q), "R": list(R)})
    return int.from_bytes(hashlib.sha256(msg).digest(), "big") % curve.n


def schnorr_prove(curve: Curve, P, Q, k: int, r: int | None = None):
    """Producer side, kept here only so the canary can build fixtures and so
    the verifier's challenge derivation is the specification."""
    r = secrets.randbelow(curve.n - 1) + 1 if r is None else r
    R = curve.mul(r, P)
    e = schnorr_challenge(curve, P, Q, R)
    return {"R": list(R), "s": (r + e * k) % curve.n}


def verify_zk_solve_certificate(cert: Any, reasons: list[str]) -> bool:
    if not isinstance(cert, dict) or cert.get("schema") != ZK_SOLVE_CERT_SCHEMA:
        reasons.append(f"certificate: schema is not {ZK_SOLVE_CERT_SCHEMA}")
        return False
    inst = _instance(cert, reasons)
    if inst is None:
        return False
    curve, P, Q = inst
    proof = cert.get("proof")
    if not isinstance(proof, dict):
        reasons.append("zk certificate: no proof")
        return False
    try:
        R = _point(proof.get("R"))
    except ValueError as e:
        reasons.append(f"zk certificate: {e}")
        return False
    s = proof.get("s")
    if R is None or not curve.on_curve(R):
        reasons.append("zk certificate: R is not on the curve")
        return False
    if not isinstance(s, int) or isinstance(s, bool) or not (0 <= s < curve.n):
        reasons.append("zk certificate: s is not an integer in [0, n)")
        return False
    e = schnorr_challenge(curve, P, Q, R)
    if curve.mul(s, P) != curve.add(R, curve.mul(e, Q)):
        reasons.append("zk certificate: [s]P != R + [e]Q")
        return False
    return True


# ----------------------------------------------------------------------------
# Lean: statement binding and hole scan (kernel build through the proof gate)
# ----------------------------------------------------------------------------

def strip_lean_comments_and_strings(src: str) -> str:
    """Remove -- comments, /- -/ block comments (nested) and string literals,
    keeping newlines so line numbers survive."""
    out: list[str] = []
    i, n, depth = 0, len(src), 0
    while i < n:
        if depth:
            if src.startswith("/-", i):
                depth += 1
                i += 2
            elif src.startswith("-/", i):
                depth -= 1
                i += 2
            else:
                out.append("\n" if src[i] == "\n" else " ")
                i += 1
            continue
        if src.startswith("/-", i):
            depth = 1
            i += 2
        elif src.startswith("--", i):
            while i < n and src[i] != "\n":
                i += 1
        elif src[i] == '"':
            i += 1
            while i < n and src[i] != '"':
                if src[i] == "\\":
                    i += 1
                if i < n and src[i] == "\n":
                    out.append("\n")
                i += 1
            i += 1
        else:
            out.append(src[i])
            i += 1
    return "".join(out)


LEAN_HOLE_RES = {
    "sorry": re.compile(r"(?<![\w.'])sorry(?![\w'])"),
    "admit": re.compile(r"(?<![\w.'])admit(?![\w'])"),
    "axiom": re.compile(r"^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*axiom\s", re.M),
    "native_decide": re.compile(r"(?<![\w.'])native_decide(?![\w'])"),
    "skipKernelTC": re.compile(r"skipKernelTC"),
    "ofReduceBool": re.compile(r"(?<![\w'])(?:Lean\.)?ofReduceBool(?![\w'])"),
    "trustCompiler": re.compile(r"(?<![\w'])(?:Lean\.)?trustCompiler(?![\w'])"),
    "unsafe": re.compile(r"^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+)*unsafe\s", re.M),
    "implemented_by": re.compile(r"implemented_by|@\[extern"),
}
LEAN_EXIT_RE = re.compile(r"^\s*#exit\b", re.M)


def lean_sources(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return sorted(p for p in target.rglob("*.lean") if ".lake" not in p.parts and "lakefile" not in p.name)


def lean_find_declaration(sources: list[Path], name: str) -> tuple[Path, str] | None:
    """The normalized statement text of `theorem|lemma <name> ... :=` (the
    name may be qualified; the last component is matched)."""
    short = re.escape(name.split(".")[-1])
    pat = re.compile(r"(?<![\w.'])(theorem|lemma)\s+(?:[\w'.]*\.)?" + short + r"(?![\w'])(.*?)(?<![:])(:=|\bby\b|\|)",
                     re.S)
    for src in sources:
        text = strip_lean_comments_and_strings(src.read_text(encoding="utf-8", errors="replace"))
        for m in pat.finditer(text):
            stmt = m.group(1) + " " + name.split(".")[-1] + " " + m.group(2)
            return src, re.sub(r"\s+", " ", stmt).strip()
    return None


def verify_lean(proof: dict[str, Any], repo: Path, reasons: list[str], notes: list[str]) -> str:
    target = _rel(repo, proof.get("project") or proof.get("path"), reasons, "lean project")
    if target is None:
        return "fail"
    name = proof.get("theorem")
    want = proof.get("decl_sha256")
    if not isinstance(name, str) or not name or not isinstance(want, str) or not HEX64_RE.match(want):
        reasons.append("lean: theorem and decl_sha256 are required")
        return "fail"
    sources = lean_sources(target)
    if not sources:
        reasons.append("lean: no .lean sources")
        return "fail"
    found = lean_find_declaration(sources, name)
    if found is None:
        reasons.append(f"lean: theorem {name} not found")
        return "fail"
    src, stmt = found
    got = sha256_bytes(stmt.encode("utf-8"))
    if got != want:
        reasons.append(f"lean: statement of {name} hashes to {got[:12]}…, pinned {want[:12]}… (statement changed)")
        return "fail"
    if re.search(r"(:|→|->)\s*True$", stmt):
        reasons.append(f"lean: {name} concludes True (vacuous)")
        return "fail"
    status = "pass"
    for s in sources:
        raw = s.read_text(encoding="utf-8", errors="replace")
        text = strip_lean_comments_and_strings(raw)
        for hole, rx in LEAN_HOLE_RES.items():
            if rx.search(text):
                reasons.append(f"lean: {s.relative_to(repo) if s.is_relative_to(repo) else s} uses {hole}")
                status = "fail"
        if LEAN_EXIT_RE.search(text):
            reasons.append(f"lean: #exit in {s.name} hides what follows")
            status = "fail"
    if status == "fail":
        return status
    gate = repo / "tools" / "lean" / "proof-gate.sh"
    if shutil.which("lake") is None or shutil.which("lean") is None:
        notes.append("lean: kernel build not run (lake/lean not on PATH); statement binding and hole scan only")
        return "not_covered"
    if not gate.is_file() or not target.is_relative_to(repo):
        notes.append("lean: kernel build not run (no tools/lean/proof-gate.sh for this target)")
        return "not_covered"
    rel = target.relative_to(repo).as_posix()
    try:
        r = subprocess.run([str(gate), rel], cwd=repo, capture_output=True, text=True, timeout=3600)
    except (OSError, subprocess.TimeoutExpired) as e:
        notes.append(f"lean: proof gate did not run ({e})")
        return "not_covered"
    if r.returncode == 0:
        notes.append(f"lean: proof gate PASS for {rel} ({src.name})")
        return "pass"
    if r.returncode == 1:
        reasons.append(f"lean: proof gate failed for {rel}: {r.stdout.strip().splitlines()[:1]}")
        return "fail"
    notes.append(f"lean: proof gate infrastructure error {r.returncode}")
    return "not_covered"


# ----------------------------------------------------------------------------
# Replay certificates, validator reports, execution receipts, attestations
# ----------------------------------------------------------------------------

def _rel(repo: Path, name: Any, reasons: list[str], what: str) -> Path | None:
    if not isinstance(name, str) or not name:
        reasons.append(f"{what}: no path")
        return None
    p = (repo / name).resolve()
    if not p.is_relative_to(repo):
        reasons.append(f"{what}: {name} escapes the repository")
        return None
    if not p.exists():
        reasons.append(f"{what}: {name} does not exist")
        return None
    return p


def _pinned(repo: Path, spec: Any, reasons: list[str], what: str) -> tuple[Path, Any] | None:
    if not isinstance(spec, dict):
        reasons.append(f"{what}: needs {{path, sha256}}")
        return None
    p = _rel(repo, spec.get("path"), reasons, what)
    if p is None:
        return None
    want = spec.get("sha256")
    if not isinstance(want, str) or not HEX64_RE.match(want):
        reasons.append(f"{what}: sha256 pin missing")
        return None
    if sha256_file(p) != want:
        reasons.append(f"{what}: {spec['path']} does not hash to its pin")
        return None
    try:
        return p, load_json(p)
    except ValueError as e:
        reasons.append(f"{what}: not JSON ({e})")
        return None


def _num(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and x == x and x not in (float("inf"), -float("inf"))


def _signed(repo: Path, proof: dict[str, Any], kr: dict[str, Any], subject_kind: str, subject_sha256: str,
            reasons: list[str], notes: list[str] | None = None) -> bool:
    """True when a keyring key signed the subject. A missing signature is not a
    failure but leaves independence unestablished (the caller reports
    not_covered); a signature that is present and wrong fails."""
    sig_spec = proof.get("signature")
    sig = None
    if sig_spec is None:
        if notes is not None:
            notes.append(f"{subject_kind}: unsigned; independence needs a keyring signature")
        return False
    if isinstance(sig_spec, dict) and "path" in sig_spec:
        p = _rel(repo, sig_spec["path"], reasons, "signature")
        if p is None:
            return False
        try:
            sig = load_json(p)
        except ValueError:
            reasons.append("signature: not JSON")
            return False
    elif isinstance(sig_spec, dict):
        sig = sig_spec
    return check_signature(sig, kr, subject_kind, subject_sha256, reasons, subject_kind)


def verify_replay(proof: dict[str, Any], repo: Path, kr: dict[str, Any], reasons: list[str],
                  notes: list[str]) -> str:
    got = _pinned(repo, proof, reasons, "replay certificate")
    if got is None:
        return "fail"
    path, cert = got
    if not isinstance(cert, dict):
        reasons.append("replay certificate: not an object")
        return "fail"
    if str(cert.get("status", "")).lower() not in {"verified", "pass", "passed", "ok"}:
        reasons.append(f"replay certificate: status {cert.get('status')!r} is not a verified replay")
    if cert.get("scalars_verified") is not True:
        reasons.append("replay certificate: scalars_verified is not true")
    runs = cert.get("runs")
    if not isinstance(runs, list) or not runs:
        reasons.append("replay certificate: no runs")
    # `independent: true` is a producer-written boolean and is not read.
    # Independence is the signature of a keyring key over the certificate.
    signed = _signed(repo, proof, kr, "replay-certificate", sha256_file(path), reasons, notes)
    if reasons:
        return "fail"
    return "pass" if signed else "not_covered"


def _raw_data_path(repo: Path, base: Path, name: Any, reasons: list[str]) -> Path | None:
    """A raw_data entry, relative to the evidence directory first and to the
    repository root second; either way it must stay inside the repository."""
    what = f"validator report raw_data {name}"
    if not isinstance(name, str) or not name:
        reasons.append(f"{what}: no path")
        return None
    for root in (base, repo):
        cand = (root / name).resolve()
        if not cand.is_relative_to(repo):
            reasons.append(f"{what}: escapes the repository")
            return None
        if cand.exists():
            return cand
    reasons.append(f"{what}: does not exist under {base.relative_to(repo).as_posix() or '.'} or the repository root")
    return None


def verify_recompute(proof: dict[str, Any], repo: Path, kr: dict[str, Any], reasons: list[str],
                     notes: list[str]) -> str:
    got = _pinned(repo, proof, reasons, "validator report")
    if got is None:
        return "fail"
    path, rep = got
    if not isinstance(rep, dict):
        reasons.append("validator report: not an object")
        return "fail"
    if str(rep.get("status", "")).lower() not in {"pass", "passed"}:
        reasons.append(f"validator report: status {rep.get('status')!r} is not pass")
    raw = rep.get("raw_data")
    # raw_data paths are relative to the evidence directory the validation gate
    # names (docs/VALIDATION_GATE.md), by default the report's own directory.
    base = path.parent
    ev = proof.get("evidence_dir")
    if ev is not None:
        base = _rel(repo, ev, reasons, "recompute evidence_dir") or base
    unpinned = 0
    if not isinstance(raw, list) or not raw:
        reasons.append("validator report: raw_data is empty")
    else:
        for item in raw:
            name = item.get("path") if isinstance(item, dict) else item
            p = _raw_data_path(repo, base, name, reasons)
            if p is None:
                continue
            pin = item.get("sha256") if isinstance(item, dict) else None
            if not isinstance(pin, str):
                unpinned += 1
            elif pin != sha256_file(p):
                reasons.append(f"validator report raw_data {name}: sha256 mismatch")
    if unpinned:
        notes.append(f"validator report: {unpinned} raw_data file(s) carry no sha256 pin; their binding is not established")
    heads = rep.get("headline")
    if not isinstance(heads, list) or not heads:
        reasons.append("validator report: no headline numbers recomputed")
    else:
        for h in heads:
            if not (isinstance(h, dict) and _num(h.get("claimed")) and _num(h.get("recomputed"))):
                reasons.append(f"validator report: headline {h!r} lacks numeric claimed/recomputed")
                continue
            tol = h.get("rel_tol", 1e-9)
            scale = max(abs(h["claimed"]), abs(h["recomputed"]), 1e-300)
            if abs(h["claimed"] - h["recomputed"]) > tol * scale:
                reasons.append(f"validator report: {h.get('name', '?')} claimed {h['claimed']} "
                               f"but recomputed {h['recomputed']}")
    signed = _signed(repo, proof, kr, "validator-report", sha256_file(path), reasons, notes)
    if reasons:
        return "fail"
    return "pass" if signed and not unpinned else "not_covered"


def verify_execution(proof: dict[str, Any], repo: Path, kr: dict[str, Any], reasons: list[str],
                     notes: list[str]) -> str:
    receipt = _pinned(repo, proof.get("receipt"), reasons, "execution receipt")
    verifier = proof.get("verifier")
    image_id = proof.get("image_id")
    binds = proof.get("journal_binds")
    if receipt is None:
        return "fail"
    if not isinstance(verifier, dict) or not isinstance(verifier.get("sha256"), str):
        reasons.append("execution: verifier {path, sha256} is required")
        return "fail"
    if not isinstance(image_id, str) or not image_id:
        reasons.append("execution: image_id is required")
        return "fail"
    if not isinstance(binds, dict) or not isinstance(binds.get("sha256"), str):
        reasons.append("execution: journal_binds {path, sha256} (the raw result) is required")
        return "fail"
    raw = _rel(repo, binds.get("path"), reasons, "execution raw result")
    if raw is None:
        return "fail"
    if sha256_file(raw) != binds["sha256"]:
        reasons.append("execution: raw result does not hash to journal_binds.sha256")
        return "fail"
    vpath = _rel(repo, verifier.get("path"), reasons, "execution verifier")
    if vpath is None:
        return "fail"
    vsha = sha256_file(vpath)
    if vsha != verifier["sha256"]:
        reasons.append("execution: verifier binary does not hash to its pin")
        return "fail"
    trusted = {t.get("sha256") for t in kr.get("trusted_verifiers", []) if isinstance(t, dict)}
    if vsha not in trusted:
        notes.append("execution: verifier digest is not in keyring.trusted_verifiers; not run")
        return "not_covered"
    rpath, _ = receipt
    try:
        r = subprocess.run([str(vpath), "verify", "--receipt", str(rpath), "--image-id", image_id],
                           cwd=repo, capture_output=True, text=True, timeout=int(proof.get("timeout", 1800)))
    except (OSError, subprocess.TimeoutExpired) as e:
        reasons.append(f"execution: verifier did not run ({e})")
        return "fail"
    try:
        out = json.loads(r.stdout.strip() or "null")
    except ValueError:
        out = None
    if r.returncode != 0 or not isinstance(out, dict):
        reasons.append(f"execution: verifier exit {r.returncode}, output not a JSON object")
        return "fail"
    if out.get("verified") is not True:
        reasons.append("execution: verifier did not report verified")
    if out.get("dev_mode") is not False:
        reasons.append("execution: receipt is a dev-mode receipt or dev_mode is unstated")
    if out.get("image_id") != image_id:
        reasons.append("execution: verifier reports a different image id")
    if out.get("receipt_sha256") != sha256_file(rpath):
        reasons.append("execution: verifier reports a different receipt digest")
    journal = out.get("journal")
    if not isinstance(journal, dict) or journal.get("raw_result_sha256") != binds["sha256"]:
        reasons.append("execution: journal does not commit to the raw result digest")
    return "fail" if reasons else "pass"


def _pinned_file(repo: Path, spec: Any, reasons: list[str], what: str) -> Path | None:
    """Like _pinned for a file of any type: the path and its digest only."""
    if not isinstance(spec, dict):
        reasons.append(f"{what}: needs {{path, sha256}}")
        return None
    p = _rel(repo, spec.get("path"), reasons, what)
    if p is None:
        return None
    want = spec.get("sha256")
    if not isinstance(want, str) or not HEX64_RE.match(want):
        reasons.append(f"{what}: sha256 pin missing")
        return None
    if sha256_file(p) != want:
        reasons.append(f"{what}: {spec['path']} does not hash to its pin")
        return None
    return p


def verify_attestation(proof: dict[str, Any], repo: Path, kr: dict[str, Any], reasons: list[str],
                       notes: list[str]) -> str:
    # Older CLI KIND:PATH records used the common flat pin shape. Preserve
    # those immutable records while applying the same pin/signature checks.
    # An explicitly supplied subject never falls back to a different pin.
    subject = proof.get("subject") if "subject" in proof else {
        "path": proof.get("path"), "sha256": proof.get("sha256")}
    spath = _pinned_file(repo, subject, reasons, "attestation subject")
    if spath is None:
        return "fail"
    kind = proof.get("subject_kind", "artifact")
    signed = _signed(repo, proof, kr, str(kind), sha256_file(spath), reasons, notes)
    if reasons:
        return "fail"
    return "pass" if signed else "not_covered"


# ----------------------------------------------------------------------------
# Claims and verdicts
# ----------------------------------------------------------------------------

def new_claim_id(now: str | None = None) -> str:
    day = (now or utcnow())[:10].replace("-", "")
    return f"PCC-{day}-{secrets.token_hex(3)}"


def claim_digest(claim: dict[str, Any]) -> str:
    """Digest of the claim without any field a verdict adds."""
    body = {k: v for k, v in claim.items() if k not in ("standing",)}
    return sha256_obj(body)


def claim_date(claim: dict[str, Any]) -> str:
    """Latest of created_at and the id's date, as YYYY-MM-DD, so that
    backdating one field does not exempt a claim from the claim_type rule."""
    created = str(claim.get("created_at", ""))[:10]
    m = re.match(r"^PCC-([0-9]{4})([0-9]{2})([0-9]{2})-", str(claim.get("id", "")))
    from_id = f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""
    return max(created, from_id)


def claim_type_of(claim: dict[str, Any], later_date: str = "") -> str | None:
    """The claim's type: its claim_type, else `data` for a legacy claim (every
    date known for it is before CLAIM_TYPE_REQUIRED_FROM), else None."""
    ct = claim.get("claim_type")
    if ct is not None:
        return ct if ct in CLAIM_TYPES else None
    date = max(claim_date(claim), later_date)
    return "data" if date and date < CLAIM_TYPE_REQUIRED_FROM else None


def claim_type_problem(claim: dict[str, Any], later_date: str = "") -> str | None:
    if "claim_type" in claim and claim["claim_type"] not in CLAIM_TYPES:
        return f"claim_type must be one of {list(CLAIM_TYPES)}, not {claim['claim_type']!r}"
    if claim_type_of(claim, later_date) is None:
        return (f"claim_type is missing; claims created on or after {CLAIM_TYPE_REQUIRED_FROM} "
                f"must set it to one of {list(CLAIM_TYPES)}")
    return None


def validate_claim(claim: Any, reasons: list[str]) -> bool:
    if not isinstance(claim, dict) or claim.get("schema") != CLAIM_SCHEMA:
        reasons.append(f"claim: schema is not {CLAIM_SCHEMA}")
        return False
    ok = True
    if not CLAIM_ID_RE.match(str(claim.get("id", ""))):
        reasons.append("claim: id must match PCC-YYYYMMDD-xxxxxx")
        ok = False
    if claim.get("kind") not in CLAIM_KINDS:
        reasons.append(f"claim: kind must be one of {sorted(CLAIM_KINDS)}")
        ok = False
    if not isinstance(claim.get("statement"), str) or not claim["statement"].strip():
        reasons.append("claim: statement is empty")
        ok = False
    proofs = claim.get("proofs")
    if not isinstance(proofs, list):
        reasons.append("claim: proofs must be a list")
        return False
    for i, pr in enumerate(proofs):
        if not isinstance(pr, dict) or pr.get("kind") not in PROOF_KINDS:
            reasons.append(f"claim: proofs[{i}] kind must be one of {sorted(PROOF_KINDS)}")
            ok = False
    problem = claim_type_problem(claim)
    if problem:
        reasons.append(f"claim: {problem}")
        ok = False
    prod = claim.get("producer")
    if not isinstance(prod, dict) or not re.match(r"^[0-9a-f]{40}$", str(prod.get("commit", ""))):
        reasons.append("claim: producer.commit must be a 40-hex commit")
        ok = False
    return ok


def verify_claim(claim: dict[str, Any], repo: Path, kr: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    results: list[dict[str, Any]] = []
    if not validate_claim(claim, reasons):
        return {"schema": VERDICT_SCHEMA, "claim_id": claim.get("id") if isinstance(claim, dict) else None,
                "claim_sha256": claim_digest(claim) if isinstance(claim, dict) else None,
                "verdict": "fail", "reasons": reasons, "proofs": results, "commit": head_commit(repo),
                "verified_at": utcnow(), "verifier_host": socket.gethostname()}
    passed_kinds: set[str] = set()
    for pr in claim["proofs"]:
        kind = pr["kind"]
        pr_reasons: list[str] = []
        notes: list[str] = []
        try:
            if kind == "lean":
                v = verify_lean(pr, repo, pr_reasons, notes)
            elif kind == "certificate":
                got = _pinned(repo, pr, pr_reasons, "solve certificate")
                v = "pass" if got and verify_solve_certificate(got[1], pr_reasons) else "fail"
            elif kind == "zk-certificate":
                got = _pinned(repo, pr, pr_reasons, "zk solve certificate")
                v = "pass" if got and verify_zk_solve_certificate(got[1], pr_reasons) else "fail"
            elif kind == "replay":
                v = verify_replay(pr, repo, kr, pr_reasons, notes)
            elif kind == "recompute":
                v = verify_recompute(pr, repo, kr, pr_reasons, notes)
            elif kind == "execution":
                v = verify_execution(pr, repo, kr, pr_reasons, notes)
            else:
                v = verify_attestation(pr, repo, kr, pr_reasons, notes)
        except Exception as e:  # a crashing verifier is a failed proof, never a pass
            v = "fail"
            pr_reasons.append(f"{kind}: verifier error {type(e).__name__}: {e}")
        if v == "pass":
            passed_kinds.add(kind)
        results.append({"kind": kind, "verdict": v, "reasons": pr_reasons, "notes": notes})
    missing: list[str] = []
    for group in MINIMUM_PROOFS.get(claim["kind"], []):
        if not any(k in passed_kinds for k in group):
            missing.append(" or ".join(group))
    verdicts = {r["verdict"] for r in results}
    if "fail" in verdicts:
        verdict = "fail"
    elif missing:
        verdict = "not_covered" if any(r["verdict"] == "not_covered" for r in results) else "fail"
        if verdict == "fail":
            reasons.append(f"claim kind {claim['kind']} needs a passing proof of kind: {'; '.join(missing)}")
        else:
            reasons.append(f"claim kind {claim['kind']} is not covered: {'; '.join(missing)}")
    elif claim["kind"] == "statement":
        verdict = "not_covered"
        reasons.append("a statement claim has no proof kind and can never be verified")
    else:
        verdict = "pass"
    return {"schema": VERDICT_SCHEMA, "claim_id": claim["id"], "claim_sha256": claim_digest(claim),
            "verdict": verdict, "reasons": reasons, "proofs": results, "commit": head_commit(repo),
            "verified_at": utcnow(), "verifier_host": socket.gethostname()}


# ----------------------------------------------------------------------------
# Ledger: append-only, hash-chained
# ----------------------------------------------------------------------------

def entry_hash(entry: dict[str, Any]) -> str:
    body = {k: v for k, v in entry.items() if k != "hash"}
    return sha256_obj(body)


def read_ledger_text(text: str) -> list[dict[str, Any]]:
    entries = []
    for i, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            e = json.loads(line)
        except ValueError as exc:
            raise PccError(f"ledger line {i}: not JSON ({exc})") from exc
        entries.append(e)
    return entries


def read_ledger(path: Path) -> list[dict[str, Any]]:
    return read_ledger_text(path.read_text(encoding="utf-8")) if path.is_file() else []


def check_chain(entries: list[dict[str, Any]], errors: list[str]) -> None:
    prev = "0" * 64
    for i, e in enumerate(entries):
        if not isinstance(e, dict) or e.get("schema") != LEDGER_SCHEMA:
            errors.append(f"ledger[{i}]: schema is not {LEDGER_SCHEMA}")
            return
        if e.get("seq") != i:
            errors.append(f"ledger[{i}]: seq is {e.get('seq')} (an entry was removed, inserted or reordered)")
            return
        if e.get("prev") != prev:
            errors.append(f"ledger[{i}]: prev does not match the previous entry's hash")
            return
        if e.get("hash") != entry_hash(e):
            errors.append(f"ledger[{i}]: hash does not match its content (entry edited)")
            return
        if e.get("type") not in {"genesis", "claim", "verdict", "bypass", "note"}:
            errors.append(f"ledger[{i}]: unknown type {e.get('type')!r}")
            return
        prev = e["hash"]


def check_prefix(base: list[dict[str, Any]], head: list[dict[str, Any]], errors: list[str]) -> None:
    if len(head) < len(base):
        errors.append(f"ledger: head has {len(head)} entries, base has {len(base)} (history removed)")
        return
    for i, (b, h) in enumerate(zip(base, head)):
        if b.get("hash") != h.get("hash"):
            errors.append(f"ledger[{i}]: differs from the base branch (history rewritten)")
            return


def append_entry(path: Path, entry_type: str, body: dict[str, Any], sig: dict[str, Any] | None = None) -> dict[str, Any]:
    entries = read_ledger(path)
    errors: list[str] = []
    check_chain(entries, errors)
    if errors:
        raise PccError("refusing to append to a broken ledger: " + errors[0])
    prev = entries[-1]["hash"] if entries else "0" * 64
    e: dict[str, Any] = {"schema": LEDGER_SCHEMA, "seq": len(entries), "prev": prev, "type": entry_type,
                         "at": utcnow(), "body": body}
    if sig is not None:
        e["sig"] = sig
    e["hash"] = entry_hash(e)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(e, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
    return e


def verdict_subject(verdict: dict[str, Any]) -> str:
    return sha256_obj({"claim_id": verdict["claim_id"], "claim_sha256": verdict["claim_sha256"],
                       "commit": verdict["commit"], "verdict": verdict["verdict"]})


def standing(claim: dict[str, Any], entries: list[dict[str, Any]], kr: dict[str, Any]) -> dict[str, Any]:
    """verified | scoped | failed | not_covered | unverified, from signed verdicts only."""
    digest = claim_digest(claim)
    result = {"claim_id": claim.get("id"), "claim_sha256": digest, "standing": "unverified", "verdicts": []}
    for e in entries:
        if e.get("type") != "verdict" or not isinstance(e.get("body"), dict):
            continue
        v = e["body"]
        if v.get("claim_id") != claim.get("id"):
            continue
        row = {"seq": e.get("seq"), "verdict": v.get("verdict"), "commit": v.get("commit"),
               "key_id": (e.get("sig") or {}).get("key_id"), "signed": False, "current": v.get("claim_sha256") == digest}
        reasons: list[str] = []
        try:
            row["signed"] = check_signature(e.get("sig"), kr, "verdict", verdict_subject(v), reasons, "verdict")
        except KeyError:
            reasons.append("verdict: malformed")
        row["reasons"] = reasons
        result["verdicts"].append(row)
    current = [r for r in result["verdicts"] if r["signed"] and r["current"]]
    if current:
        last = current[-1]
        result["standing"] = {"pass": "verified", "fail": "failed", "not_covered": "not_covered",
                              "scoped": "scoped"}.get(str(last["verdict"]), "unverified")
    return result


# ----------------------------------------------------------------------------
# Prose linter
# ----------------------------------------------------------------------------

def lint_prose(text: str, standings: dict[str, str]) -> list[str]:
    """Each paragraph with a strong-claim word needs a [pcc:ID] whose standing
    is verified, or an explicit [pcc:unverified] tag."""
    findings: list[str] = []
    paragraphs = re.split(r"\n\s*\n", text)
    line_no = 1
    for para in paragraphs:
        stripped = para.strip()
        if stripped and not stripped.startswith(("```", "    ", "|", "<", "#", ">")) and STRONG_CLAIM_RE.search(para):
            cites = CITATION_RE.findall(para)
            if not cites:
                word = STRONG_CLAIM_RE.search(para).group(0)
                findings.append(f"line {line_no}: '{word}' with no [pcc:ID] citation and no [pcc:unverified] tag")
            for c in cites:
                if c == "unverified":
                    continue
                st = standings.get(c)
                if st is None:
                    findings.append(f"line {line_no}: [pcc:{c}] names no known claim")
                elif st != "verified":
                    findings.append(f"line {line_no}: [pcc:{c}] has standing {st}, not verified")
        line_no += para.count("\n") + 2
    return findings


# ----------------------------------------------------------------------------
# Canary corpus: every sabotage class must be rejected, the clean fixture accepted
# ----------------------------------------------------------------------------

# secp256k1, so the arithmetic in the verifier is exercised at cryptographic size.
_SECP_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
_SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
_SECP_G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
           0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
# A small curve whose order is prime, for a cheap n-torsion check: y^2 = x^3 + 2x + 3 over GF(97).
_SMALL = {"p": 97, "a": 2, "b": 3, "n": 5}

LEAN_FIXTURE = """-- A toy theorem; the canary only needs a declaration to bind.
theorem two_mul_eq (n : Nat) : 2 * n = n + n := by
  omega
-- "sorry" inside a comment and a string must not be flagged:
def note : String := "no sorry here"
"""

MOCK_VERIFIER = """#!/usr/bin/env python3
import hashlib, json, sys
args = sys.argv[1:]
receipt = args[args.index("--receipt") + 1]
image = args[args.index("--image-id") + 1]
r = json.load(open(receipt))
out = {"verified": r.get("ok") is True, "dev_mode": bool(r.get("dev_mode", False)),
       "image_id": r.get("image_id"), "receipt_sha256": hashlib.sha256(open(receipt, "rb").read()).hexdigest(),
       "journal": {"raw_result_sha256": r.get("journal_raw")}}
print(json.dumps(out))
"""


class Fixture:
    """A repository-shaped directory with one passing claim per proof kind."""

    def __init__(self, root: Path):
        self.root = root
        self.secret = secrets.token_bytes(32)
        self.public = ed25519_public(self.secret)
        self.stranger = secrets.token_bytes(32)
        (root / PCC_DIR).mkdir(parents=True)
        (root / CLAIMS_DIR).mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        self.commit = "a" * 40
        self.claims: dict[str, dict[str, Any]] = {}
        self._build()

    # helpers ---------------------------------------------------------------
    def write(self, rel: str, obj: Any) -> Path:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(obj, (bytes, bytearray)):
            p.write_bytes(obj)
        elif isinstance(obj, str):
            p.write_text(obj, encoding="utf-8")
        else:
            p.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return p

    def pin(self, rel: str) -> dict[str, str]:
        return {"path": rel, "sha256": sha256_file(self.root / rel)}

    def sign(self, rel: str, kind: str, secret: bytes | None = None) -> dict[str, Any]:
        return make_signature(secret or self.secret, "fixture-ci", kind, sha256_file(self.root / rel))

    def claim(self, name: str, kind: str, proofs: list[dict[str, Any]], statement: str = "fixture") -> dict[str, Any]:
        c = {"schema": CLAIM_SCHEMA, "id": f"PCC-20260101-{sha256_bytes(name.encode())[:6]}", "kind": kind,
             "statement": statement, "scope": "canary fixture", "proofs": proofs,
             "claim_type": "data",
             "producer": {"commit": self.commit, "session": "fixture", "model": "none"}, "created_at": "2026-01-01T00:00:00Z"}
        self.write(f"{CLAIMS_DIR}/{c['id']}.json", c)
        self.claims[name] = c
        return c

    def keyring(self, trust_verifier: bool = True) -> dict[str, Any]:
        kr = {"schema": KEYRING_SCHEMA,
              "keys": [{"id": "fixture-ci", "algo": "ed25519", "public_key": self.public.hex(), "role": "verifier"}],
              "trusted_verifiers": []}
        if trust_verifier:
            kr["trusted_verifiers"].append({"name": "mock", "kind": "execution",
                                            "sha256": sha256_file(self.root / "verifier/mock_verify.py")})
        self.write(KEYRING_PATH, kr)
        return kr

    # the fixtures ------------------------------------------------------------
    def _build(self) -> None:
        curve = Curve(_SECP_P, 0, 7, _SECP_N)
        k = 0x1F3A5C7E9B2D4F6081A3C5E7092B4D6F8A1C3E5071B3D5F7092C4E6081A3C5E7
        P = _SECP_G
        Q = curve.mul(k, P)
        self.cert = {"schema": SOLVE_CERT_SCHEMA, "curve": {"p": _SECP_P, "a": 0, "b": 7, "n": _SECP_N},
                     "P": list(P), "Q": list(Q), "k": k}
        self.write("solve/cert.json", self.cert)
        self.claim("solve", "solve", [{"kind": "certificate", **self.pin("solve/cert.json")}])

        zk = {"schema": ZK_SOLVE_CERT_SCHEMA, "curve": self.cert["curve"], "P": list(P), "Q": list(Q),
              "proof": schnorr_prove(curve, P, Q, k, r=0x5EED)}
        self.zk = zk
        self.write("solve/zk.json", zk)
        self.claim("zk", "solve", [{"kind": "zk-certificate", **self.pin("solve/zk.json")}])

        self.write("lean/Toy.lean", LEAN_FIXTURE)
        found = lean_find_declaration([self.root / "lean/Toy.lean"], "two_mul_eq")
        assert found is not None
        self.decl_sha = sha256_bytes(found[1].encode())
        self.claim("lean", "theorem", [{"kind": "lean", "project": "lean", "theorem": "two_mul_eq",
                                        "decl_sha256": self.decl_sha}])

        self.write("runs/raw.jsonl", '{"gae": 10}\n{"gae": 12}\n')
        self.replay = {"status": "verified", "scalars_verified": True, "runs": [{"id": "r1"}, {"id": "r2"}]}
        self.write("runs/replay-certificate.json", self.replay)
        self.write("runs/replay-certificate.sig.json", self.sign("runs/replay-certificate.json", "replay-certificate"))
        self.report = {"status": "pass", "raw_data": [self.pin("runs/raw.jsonl")],
                       "headline": [{"name": "mean_gae", "claimed": 11.0, "recomputed": 11.0}]}
        self.write("runs/validator-report.json", self.report)
        self.write("runs/validator-report.sig.json", self.sign("runs/validator-report.json", "validator-report"))
        self.claim("measurement", "measurement", [
            {"kind": "replay", **self.pin("runs/replay-certificate.json"),
             "signature": {"path": "runs/replay-certificate.sig.json"}},
            {"kind": "recompute", **self.pin("runs/validator-report.json"),
             "signature": {"path": "runs/validator-report.sig.json"}}])

        vpath = self.write("verifier/mock_verify.py", MOCK_VERIFIER)
        vpath.chmod(0o755)
        self.write("exec/raw-result.bin", b"raw result bytes\n")
        self.receipt = {"ok": True, "dev_mode": False, "image_id": "img-0001",
                        "journal_raw": sha256_file(self.root / "exec/raw-result.bin")}
        self.write("exec/receipt.json", self.receipt)
        self.claim("execution", "execution", [{"kind": "execution", "receipt": self.pin("exec/receipt.json"),
                                               "verifier": self.pin("verifier/mock_verify.py"), "image_id": "img-0001",
                                               "journal_binds": self.pin("exec/raw-result.bin")}])

        self.write("att/artifact.txt", "bytes someone vouched for\n")
        self.write("att/artifact.sig.json", self.sign("att/artifact.txt", "artifact"))
        self.claim("attestation", "statement", [{"kind": "attestation", "subject": self.pin("att/artifact.txt"),
                                                 "subject_kind": "artifact", "signature": {"path": "att/artifact.sig.json"}}])
        self.keyring(trust_verifier=True)


def _run_canaries(fx: Fixture) -> list[tuple[str, str, str, list[str]]]:
    """Returns rows (name, expected, got, reasons). expected is 'pass' or 'fail'."""
    rows: list[tuple[str, str, str, list[str]]] = []
    kr = load_keyring(fx.root / KEYRING_PATH)

    def check(name: str, expected: str, claim_name: str, mutate=None, keyring=None):
        with tempfile.TemporaryDirectory() as td:
            copy = Path(td) / "repo"
            shutil.copytree(fx.root, copy, symlinks=True)
            subprocess.run(["git", "init", "-q", str(copy)], check=True)
            claim = json.loads(json.dumps(fx.claims[claim_name]))
            if mutate:
                claim = mutate(copy, claim) or claim
            v = verify_claim(claim, copy, keyring if keyring is not None else kr)
            got = v["verdict"]
            reasons = list(v["reasons"]) + [r for p in v["proofs"] for r in p["reasons"]]
            rows.append((name, expected, got, reasons))

    def rewrite(copy: Path, rel: str, fn):
        p = copy / rel
        obj = load_json(p)
        fn(obj)
        p.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    def repin(claim: dict[str, Any], idx: int, copy: Path, key: str | None = None):
        rel = (claim["proofs"][idx][key] if key else claim["proofs"][idx])["path"]
        target = claim["proofs"][idx][key] if key else claim["proofs"][idx]
        target["sha256"] = sha256_file(copy / rel)

    # clean fixtures
    for n in ("solve", "zk", "measurement", "execution"):
        check(f"clean:{n}", "pass", n)
    check("clean:lean", "pass_or_not_covered", "lean")
    check("clean:attestation(statement claim never verifies)", "not_covered", "attestation")

    # certificate
    def wrong_k(copy, c):
        rewrite(copy, "solve/cert.json", lambda o: o.__setitem__("k", o["k"] + 1))
        repin(c, 0, copy)
    check("certificate:wrong k", "fail", "solve", wrong_k)

    def q_off(copy, c):
        rewrite(copy, "solve/cert.json", lambda o: o["Q"].__setitem__(1, (o["Q"][1] + 1) % _SECP_P))
        repin(c, 0, copy)
    check("certificate:Q off the curve", "fail", "solve", q_off)

    def composite_n(copy, c):
        rewrite(copy, "solve/cert.json", lambda o: o["curve"].__setitem__("n", _SECP_N * 3))
        repin(c, 0, copy)
    check("certificate:composite n", "fail", "solve", composite_n)

    def wrong_order(copy, c):
        # a prime that is not the group order: [n]P != O
        rewrite(copy, "solve/cert.json", lambda o: o["curve"].__setitem__("n", _SECP_P))
        repin(c, 0, copy)
    check("certificate:[n]P != O", "fail", "solve", wrong_order)

    def unpinned(copy, c):
        rewrite(copy, "solve/cert.json", lambda o: o.__setitem__("k", o["k"] + 1))  # no repin
    check("claim:pinned digest mismatch", "fail", "solve", unpinned)

    def escape(copy, c):
        c["proofs"][0]["path"] = "../outside.json"
    check("claim:proof path outside the repository", "fail", "solve", escape)

    def missing_kind(copy, c):
        c["kind"] = "theorem"
    check("claim:minimum proof kind absent", "fail", "solve", missing_kind)

    # zk certificate
    def tamper_s(copy, c):
        rewrite(copy, "solve/zk.json", lambda o: o["proof"].__setitem__("s", (o["proof"]["s"] + 1) % _SECP_N))
        repin(c, 0, copy)
    check("zk-certificate:tampered s", "fail", "zk", tamper_s)

    def transplant(copy, c):
        curve = Curve(_SECP_P, 0, 7, _SECP_N)
        other = curve.mul(12345, _SECP_G)
        rewrite(copy, "solve/zk.json", lambda o: o.__setitem__("Q", list(other)))
        repin(c, 0, copy)
    check("zk-certificate:proof transplanted to another Q", "fail", "zk", transplant)

    # lean
    def lean_edit(copy, text_fn):
        p = copy / "lean/Toy.lean"
        p.write_text(text_fn(p.read_text()), encoding="utf-8")

    check("lean:sorry", "fail", "lean", lambda copy, c: lean_edit(copy, lambda t: t.replace("  omega", "  sorry")))
    check("lean:native_decide", "fail", "lean", lambda copy, c: lean_edit(copy, lambda t: t.replace("  omega", "  native_decide")))
    check("lean:user axiom", "fail", "lean", lambda copy, c: lean_edit(copy, lambda t: t + "axiom magic : False\n"))
    check("lean:skipKernelTC", "fail", "lean", lambda copy, c: lean_edit(copy, lambda t: "set_option debug.skipKernelTC true\n" + t))
    check("lean:#exit before the theorem", "fail", "lean", lambda copy, c: lean_edit(copy, lambda t: "#exit\n" + t))
    check("lean:statement edited after pinning", "fail", "lean",
          lambda copy, c: lean_edit(copy, lambda t: t.replace("2 * n = n + n", "2 * n = n + n + 0")))
    check("lean:conclusion True", "fail", "lean",
          lambda copy, c: (lean_edit(copy, lambda t: t.replace("2 * n = n + n", "True")),
                           c.__setitem__("proofs", [dict(c["proofs"][0], decl_sha256=sha256_bytes(
                               lean_find_declaration([copy / "lean/Toy.lean"], "two_mul_eq")[1].encode()))])))
    check("lean:theorem renamed away", "fail", "lean", lambda copy, c: c["proofs"][0].__setitem__("theorem", "no_such"))

    # replay / recompute
    def no_sig(copy, c):
        del c["proofs"][0]["signature"]
    check("replay:no signature (unsigned is uncovered, never verified)", "not_covered", "measurement", no_sig)

    def stranger_sig(copy, c):
        (copy / "runs/replay-certificate.sig.json").write_text(json.dumps(
            make_signature(fx.stranger, "fixture-ci", "replay-certificate",
                           sha256_file(copy / "runs/replay-certificate.json"))))
    check("replay:signature by an untrusted key", "fail", "measurement", stranger_sig)

    def sig_other_subject(copy, c):
        (copy / "runs/replay-certificate.sig.json").write_text(json.dumps(
            make_signature(fx.secret, "fixture-ci", "replay-certificate", "0" * 64)))
    check("replay:signature over a different subject", "fail", "measurement", sig_other_subject)

    def empty_runs(copy, c):
        rewrite(copy, "runs/replay-certificate.json", lambda o: o.__setitem__("runs", []))
        repin(c, 0, copy)
        (copy / "runs/replay-certificate.sig.json").write_text(json.dumps(
            make_signature(fx.secret, "fixture-ci", "replay-certificate", sha256_file(copy / "runs/replay-certificate.json"))))
    check("replay:empty runs (even when signed)", "fail", "measurement", empty_runs)

    def independent_true_only(copy, c):
        rewrite(copy, "runs/replay-certificate.json", lambda o: o.__setitem__("independent", True))
        repin(c, 0, copy)
        del c["proofs"][0]["signature"]
    check("replay:independent:true written by the producer, unsigned", "not_covered", "measurement", independent_true_only)

    def unpinned_raw(copy, c):
        rewrite(copy, "runs/validator-report.json", lambda o: o.__setitem__("raw_data", ["raw.jsonl"]))
        repin(c, 1, copy)
        (copy / "runs/validator-report.sig.json").write_text(json.dumps(
            make_signature(fx.secret, "fixture-ci", "validator-report", sha256_file(copy / "runs/validator-report.json"))))
    check("recompute:raw data without a sha256 pin", "not_covered", "measurement", unpinned_raw)

    def raw_outside(copy, c):
        rewrite(copy, "runs/validator-report.json", lambda o: o.__setitem__("raw_data", [{"path": "../../etc/passwd", "sha256": "0" * 64}]))
        repin(c, 1, copy)
        (copy / "runs/validator-report.sig.json").write_text(json.dumps(
            make_signature(fx.secret, "fixture-ci", "validator-report", sha256_file(copy / "runs/validator-report.json"))))
    check("recompute:raw data path outside the repository", "fail", "measurement", raw_outside)

    def headline(copy, c):
        rewrite(copy, "runs/validator-report.json", lambda o: o["headline"][0].__setitem__("recomputed", 11.5))
        repin(c, 1, copy)
        (copy / "runs/validator-report.sig.json").write_text(json.dumps(
            make_signature(fx.secret, "fixture-ci", "validator-report", sha256_file(copy / "runs/validator-report.json"))))
    check("recompute:headline claimed != recomputed", "fail", "measurement", headline)

    def raw_tampered(copy, c):
        (copy / "runs/raw.jsonl").write_text('{"gae": 10}\n{"gae": 99}\n')
    check("recompute:raw data digest mismatch", "fail", "measurement", raw_tampered)

    # execution
    def dev_mode(copy, c):
        rewrite(copy, "exec/receipt.json", lambda o: o.__setitem__("dev_mode", True))
        repin(c, 0, copy, "receipt")
    check("execution:dev-mode receipt", "fail", "execution", dev_mode)

    def wrong_image(copy, c):
        c["proofs"][0]["image_id"] = "img-0002"
    check("execution:wrong image id", "fail", "execution", wrong_image)

    def journal_unbound(copy, c):
        (copy / "exec/raw-result.bin").write_bytes(b"different raw bytes\n")
        c["proofs"][0]["journal_binds"]["sha256"] = sha256_file(copy / "exec/raw-result.bin")
    check("execution:journal does not commit to the raw result", "fail", "execution", journal_unbound)

    def verifier_swapped(copy, c):
        (copy / "verifier/mock_verify.py").write_text(MOCK_VERIFIER.replace('r.get("ok") is True', "True"))
    check("execution:verifier binary digest mismatch", "fail", "execution", verifier_swapped)

    def verifier_untrusted(copy, c):
        pass
    kr_untrusted = json.loads(json.dumps(kr))
    kr_untrusted["trusted_verifiers"] = []
    check("execution:verifier not in keyring", "not_covered", "execution", verifier_untrusted, keyring=kr_untrusted)

    def receipt_not_ok(copy, c):
        rewrite(copy, "exec/receipt.json", lambda o: o.__setitem__("ok", False))
        repin(c, 0, copy, "receipt")
    check("execution:verifier reports not verified", "fail", "execution", receipt_not_ok)

    # attestation
    def att_wrong_key(copy, c):
        (copy / "att/artifact.sig.json").write_text(json.dumps(
            make_signature(fx.stranger, "fixture-ci", "artifact", sha256_file(copy / "att/artifact.txt"))))
    check("attestation:wrong key", "fail", "attestation", att_wrong_key)

    def att_other_subject(copy, c):
        (copy / "att/artifact.txt").write_text("edited after signing\n")
        c["proofs"][0]["subject"]["sha256"] = sha256_file(copy / "att/artifact.txt")
    check("attestation:subject edited after signing", "fail", "attestation", att_other_subject)

    def legacy_attestation(copy, c):
        proof = c["proofs"][0]
        proof.update(proof.pop("subject"))
    check("attestation:legacy flat pin remains scoped", "not_covered", "attestation", legacy_attestation)

    def legacy_bad_pin(copy, c):
        legacy_attestation(copy, c)
        c["proofs"][0]["sha256"] = "0" * 64
    check("attestation:legacy corrupt pin", "fail", "attestation", legacy_bad_pin)

    def subject_no_fallback(copy, c):
        proof = c["proofs"][0]
        proof.update(proof["subject"])
        proof["subject"]["sha256"] = "0" * 64
    check("attestation:canonical corrupt pin cannot fall back", "fail", "attestation", subject_no_fallback)

    return rows


def _ledger_canaries(fx: Fixture) -> list[tuple[str, str, str, list[str]]]:
    rows: list[tuple[str, str, str, list[str]]] = []
    kr = load_keyring(fx.root / KEYRING_PATH)
    with tempfile.TemporaryDirectory() as td:
        led = Path(td) / "ledger.jsonl"
        append_entry(led, "genesis", {"repo": "fixture"})
        claim = fx.claims["solve"]
        append_entry(led, "claim", {"claim_id": claim["id"], "claim_sha256": claim_digest(claim)})
        verdict = verify_claim(claim, fx.root, kr)
        sig = make_signature(fx.secret, "fixture-ci", "verdict", verdict_subject(verdict))
        append_entry(led, "verdict", verdict, sig)
        base = read_ledger(led)
        append_entry(led, "note", {"text": "later entry"})
        head = read_ledger(led)

        def row(name, expected, entries, base_entries=None, claim_obj=None, keyring=kr):
            errors: list[str] = []
            check_chain(entries, errors)
            if base_entries is not None and not errors:
                check_prefix(base_entries, entries, errors)
            st = standing(claim_obj or claim, entries, keyring)["standing"] if not errors else "chain-broken"
            got = "fail" if errors else ("pass" if st == "verified" else st)
            rows.append((name, expected, got, errors))

        row("ledger:clean chain, signed verdict", "pass", head, base)
        edited = json.loads(json.dumps(head))
        edited[1]["body"]["claim_id"] = "PCC-20260101-ffffff"
        row("ledger:entry edited", "fail", edited, base)
        deleted = [head[0]] + head[2:]
        row("ledger:entry deleted", "fail", deleted, base)
        rewritten = json.loads(json.dumps(head))
        rewritten[3]["body"]["text"] = "rewritten"
        rewritten[3]["hash"] = entry_hash(rewritten[3])
        row("ledger:history rewritten (base not a prefix)", "fail", rewritten[:4], head)
        truncated = head[:2]
        row("ledger:history removed below base", "fail", truncated, base)
        unsigned = json.loads(json.dumps(head))
        del unsigned[2]["sig"]
        unsigned[2]["hash"] = entry_hash(unsigned[2])
        for i in range(3, len(unsigned)):
            unsigned[i]["prev"] = unsigned[i - 1]["hash"]
            unsigned[i]["hash"] = entry_hash(unsigned[i])
        row("ledger:verdict without a trusted signature", "unverified", unsigned)
        stale_claim = json.loads(json.dumps(claim))
        stale_claim["statement"] = "the claim was edited after the verdict"
        row("ledger:stale verdict after the claim changed", "unverified", head, None, stale_claim)
        stranger_kr = json.loads(json.dumps(kr))
        stranger_kr["keys"][0]["public_key"] = ed25519_public(fx.stranger).hex()
        row("ledger:verdict key not in keyring", "unverified", head, None, None, stranger_kr)
        failed_verdict = dict(verdict, verdict="fail")
        led2 = Path(td) / "l2.jsonl"
        append_entry(led2, "genesis", {})
        append_entry(led2, "verdict", failed_verdict,
                     make_signature(fx.secret, "fixture-ci", "verdict", verdict_subject(failed_verdict)))
        row("ledger:signed failing verdict", "failed", read_ledger(led2))
        # A new claim that omits claim_type, or backdates only one field, is rejected.
        errs: list[str] = []
        fresh = {k: v for k, v in claim.items() if k != "claim_type"}
        fresh["created_at"] = CLAIM_TYPE_REQUIRED_FROM + "T00:00:00Z"
        rows.append(("ledger:new claim without claim_type", "fail",
                     "fail" if claim_type_problem(fresh) else "pass", errs))
        backdated = dict(fresh, created_at="2026-01-01T00:00:00Z", id="PCC-20261112-abcdef")
        rows.append(("ledger:claim_type exemption by backdated created_at", "fail",
                     "fail" if claim_type_problem(backdated) else "pass", errs))
        legacy = {k: v for k, v in claim.items() if k != "claim_type"}
        rows.append(("ledger:legacy claim without claim_type counts as data", "pass",
                     "fail" if claim_type_problem(legacy) else "pass", errs))
    return rows


def _prose_canaries() -> list[tuple[str, str, str, list[str]]]:
    rows = []
    st = {"PCC-20260101-aaaaaa": "verified", "PCC-20260101-bbbbbb": "unverified"}

    def row(name, expected, text):
        f = lint_prose(text, st)
        rows.append((name, expected, "fail" if f else "pass", f))

    row("prose:strong claim with no citation", "fail", "This change beats rho at n=83.")
    row("prose:citation to an unverified claim", "fail", "This proves the bound [pcc:PCC-20260101-bbbbbb].")
    row("prose:citation to an unknown claim", "fail", "Verified speedup [pcc:PCC-20260101-cccccc].")
    row("prose:verified citation", "pass", "The speedup is 1.3x [pcc:PCC-20260101-aaaaaa].")
    row("prose:explicit unverified tag", "pass", "We think it beats rho [pcc:unverified].")
    row("prose:code block is not prose", "pass", "```\nprint('verified')\n```")
    row("prose:no strong word", "pass", "The run finished in 12 minutes.")
    return rows


def run_canary(out) -> int:
    with tempfile.TemporaryDirectory() as td:
        fx = Fixture(Path(td) / "fixture")
        rows = _run_canaries(fx) + _ledger_canaries(fx) + _prose_canaries()
    bad = 0
    for name, expected, got, reasons in rows:
        ok = (got == expected) or (expected == "pass_or_not_covered" and got in ("pass", "not_covered"))
        bad += not ok
        print(f"{'ok   ' if ok else 'WRONG'} expected {expected:<13} got {got:<13} {name}", file=out)
        if not ok:
            for r in reasons[:4]:
                print(f"        {r}", file=out)
    print(f"canary: {len(rows) - bad}/{len(rows)} classes behave as required", file=out)
    return 0 if bad == 0 else 1


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def _load_claim(repo: Path, ref: str) -> tuple[Path, dict[str, Any]]:
    p = Path(ref)
    if not p.is_file():
        p = repo / CLAIMS_DIR / f"{ref}.json"
    if not p.is_file():
        raise PccError(f"no claim at {ref}")
    return p, load_json(p)


def _standings(repo: Path, kr: dict[str, Any]) -> dict[str, str]:
    entries = read_ledger(repo / LEDGER_PATH)
    out: dict[str, str] = {}
    for p in sorted((repo / CLAIMS_DIR).glob("*.json")) if (repo / CLAIMS_DIR).is_dir() else []:
        try:
            c = load_json(p)
        except ValueError:
            continue
        if isinstance(c, dict) and isinstance(c.get("id"), str):
            out[c["id"]] = standing(c, entries, kr)["standing"]
    return out


def _claim_entry_dates(entries: list[dict[str, Any]]) -> dict[str, str]:
    out: dict[str, str] = {}
    for e in entries:
        if e.get("type") == "claim" and isinstance(e.get("body"), dict):
            out.setdefault(str(e["body"].get("claim_id")), str(e.get("at", ""))[:10])
    return out


def check_claim_types(repo: Path, entries: list[dict[str, Any]], errors: list[str]) -> None:
    """Every claim file must carry a valid claim_type unless it is a legacy
    claim; the ledger entry's own date also counts against the exemption."""
    dates = _claim_entry_dates(entries)
    for p in sorted((repo / CLAIMS_DIR).glob("*.json")) if (repo / CLAIMS_DIR).is_dir() else []:
        try:
            c = load_json(p)
        except ValueError:
            continue
        if not isinstance(c, dict) or c.get("schema") != CLAIM_SCHEMA:
            continue
        problem = claim_type_problem(c, dates.get(str(c.get("id")), ""))
        if problem:
            errors.append(f"claim {c.get('id')}: {problem}")


def _all_claims(repo: Path) -> list[dict[str, Any]]:
    out = []
    for p in sorted((repo / CLAIMS_DIR).glob("*.json")) if (repo / CLAIMS_DIR).is_dir() else []:
        try:
            c = load_json(p)
        except ValueError:
            continue
        if isinstance(c, dict) and isinstance(c.get("id"), str):
            out.append(c)
    return out


def standing_by_type(repo: Path, kr: dict[str, Any]) -> dict[str, dict[str, int]]:
    entries = read_ledger(repo / LEDGER_PATH)
    dates = _claim_entry_dates(entries)
    table: dict[str, dict[str, int]] = {t: {} for t in CLAIM_TYPES}
    for c in _all_claims(repo):
        t = claim_type_of(c, dates.get(c["id"], "")) or "untyped"
        st = standing(c, entries, kr)["standing"]
        table.setdefault(t, {})
        table[t][st] = table[t].get(st, 0) + 1
    return table


def sample_for_validation(repo: Path, kr: dict[str, Any], rate_data: float, rate_interpretive: float,
                          seed: int, rate_literature: float | None = None, base: float = 0.1) -> dict[str, Any]:
    """Stratified, seeded draw of claims for independent validation. A claim of
    a type with weight w is drawn when u < min(1, base*w), u = H(seed, id) in
    [0,1); each non-empty stratum yields at least its lowest-u claim."""
    if rate_interpretive < 3 * rate_data:
        raise PccError("--rate-interpretive must be at least 3x --rate-data (interpretive claims are sampled at "
                       "three times the data rate or more)")
    weights = {"data": rate_data, "literature": rate_data if rate_literature is None else rate_literature,
               "interpretive": rate_interpretive}
    if min(weights.values()) <= 0 or base <= 0:
        raise PccError("rates and --base must be positive")
    entries = read_ledger(repo / LEDGER_PATH)
    dates = _claim_entry_dates(entries)
    strata: dict[str, list[tuple[float, dict[str, Any]]]] = {t: [] for t in CLAIM_TYPES}
    untyped = []
    for c in _all_claims(repo):
        t = claim_type_of(c, dates.get(c["id"], ""))
        if t is None:
            untyped.append(c["id"])
            continue
        u = int(sha256_bytes(f"{seed}:{c['id']}".encode())[:15], 16) / float(16 ** 15)
        strata[t].append((u, c))
    chosen: list[dict[str, Any]] = []
    summary: dict[str, Any] = {}
    for t in CLAIM_TYPES:
        p = min(1.0, base * weights[t])
        rows = sorted(strata[t], key=lambda r: (r[0], r[1]["id"]))
        picked = [r for r in rows if r[0] < p]
        if rows and not picked:
            picked = rows[:1]
        summary[t] = {"weight": weights[t], "probability": p, "population": len(rows), "sampled": len(picked)}
        for _, c in picked:
            chosen.append({"claim_id": c["id"], "claim_type": t, "kind": c.get("kind"),
                           "standing": standing(c, entries, kr)["standing"]})
    chosen.sort(key=lambda r: r["claim_id"])
    return {"schema": "pcc.validation-sample/v1", "seed": seed, "base_probability": base, "strata": summary,
            "untyped_claims_excluded": untyped, "claims": chosen}


def _print_verdict(v: dict[str, Any], as_json: bool, out) -> None:
    if as_json:
        print(json.dumps(v, sort_keys=True), file=out)
        return
    print(f"{v['claim_id']}: {v['verdict']}", file=out)
    for r in v["reasons"]:
        print(f"  - {r}", file=out)
    for p in v["proofs"]:
        print(f"  {p['kind']}: {p['verdict']}", file=out)
        for r in p["reasons"]:
            print(f"    - {r}", file=out)
        for n in p["notes"]:
            print(f"    · {n}", file=out)


def _exit_for(verdict: str) -> int:
    return {"pass": 0, "fail": 1, "not_covered": 2}.get(verdict, 1)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="pcc", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, default=None, help="repository root (default: the enclosing git root)")
    ap.add_argument("--keyring", type=Path, default=None, help=f"keyring (default: {KEYRING_PATH})")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("keygen")
    s.add_argument("--out", type=Path, required=True)
    s.add_argument("--key-id", required=True)

    s = sub.add_parser("claim")
    cs = s.add_subparsers(dest="claim_cmd", required=True)
    n = cs.add_parser("new")
    n.add_argument("--kind", required=True, choices=sorted(CLAIM_KINDS))
    n.add_argument("--statement", required=True)
    n.add_argument("--scope", default="")
    n.add_argument("--claim-type", choices=list(CLAIM_TYPES), default=None,
                   help="data, literature or interpretive (required for claims created on or after "
                        f"{CLAIM_TYPE_REQUIRED_FROM})")
    n.add_argument("--proof", action="append", default=[], help="KIND:PATH, or KIND:JSON for lean/execution")
    n.add_argument("--session", default=os.environ.get("CLAUDE_SESSION_ID", ""))
    n.add_argument("--model", default="")

    for name in ("verify", "verdict"):
        s = sub.add_parser(name)
        s.add_argument("claim")
        s.add_argument("--json", action="store_true")
        if name == "verdict":
            s.add_argument("--sign-key", type=Path, required=True)
            s.add_argument("--key-id", required=True)
    s = sub.add_parser("verify-all")
    s.add_argument("--json", action="store_true")

    s = sub.add_parser("sign")
    s.add_argument("artifact", type=Path)
    s.add_argument("--sign-key", type=Path, required=True)
    s.add_argument("--key-id", required=True)
    s.add_argument("--subject-kind", required=True)

    s = sub.add_parser("ledger")
    ls = s.add_subparsers(dest="ledger_cmd", required=True)
    v = ls.add_parser("verify")
    v.add_argument("--base", default=None, help="git ref whose ledger must be a prefix of this one")
    ls.add_parser("init")
    b = ls.add_parser("append-bypass")
    b.add_argument("--reason", required=True)
    b.add_argument("--command", required=True)
    b.add_argument("--session", default=os.environ.get("CHECKPOINT_SESSION", ""))

    s = sub.add_parser("standing")
    s.add_argument("claim")
    s.add_argument("--json", action="store_true")

    s = sub.add_parser("standing-by-type")
    s.add_argument("--json", action="store_true")

    s = sub.add_parser("sample-for-validation")
    s.add_argument("--rate-data", type=float, default=1.0)
    s.add_argument("--rate-interpretive", type=float, default=3.0)
    s.add_argument("--rate-literature", type=float, default=None, help="default: the data rate")
    s.add_argument("--base", type=float, default=0.1, help="probability for weight 1 (default 0.1)")
    s.add_argument("--seed", type=int, required=True)
    s.add_argument("--out", type=Path, required=True)

    s = sub.add_parser("lint-prose")
    s.add_argument("files", nargs="*", type=Path)
    s.add_argument("--stdin", action="store_true")

    sub.add_parser("canary")

    a = ap.parse_args(argv)
    out = sys.stdout
    repo = (a.repo or repo_root()).resolve()
    kr = load_keyring(a.keyring or repo / KEYRING_PATH)

    if a.cmd == "keygen":
        secret = secrets.token_bytes(32)
        a.out.write_text(secret.hex() + "\n", encoding="utf-8")
        os.chmod(a.out, 0o600)
        print(json.dumps({"id": a.key_id, "algo": "ed25519", "public_key": ed25519_public(secret).hex(),
                          "role": "verifier"}), file=out)
        return 0

    if a.cmd == "claim":
        proofs = []
        for spec in a.proof:
            kind, _, rest = spec.partition(":")
            if kind not in PROOF_KINDS:
                raise PccError(f"unknown proof kind {kind!r}")
            if rest.startswith("{"):
                proofs.append({"kind": kind, **json.loads(rest)})
            else:
                p = (repo / rest).resolve()
                if not p.is_file():
                    raise PccError(f"no such proof file {rest}")
                pin = {"path": rest, "sha256": sha256_file(p)}
                proofs.append({"kind": kind, "subject": pin} if kind == "attestation"
                              else {"kind": kind, **pin})
        claim = {"schema": CLAIM_SCHEMA, "id": new_claim_id(), "kind": a.kind, "statement": a.statement,
                 "scope": a.scope, "proofs": proofs,
                 "producer": {"commit": head_commit(repo), "session": a.session, "model": a.model},
                 "created_at": utcnow()}
        if a.claim_type:
            claim["claim_type"] = a.claim_type
        reasons: list[str] = []
        if not validate_claim(claim, reasons):
            raise PccError("; ".join(reasons))
        path = repo / CLAIMS_DIR / f"{claim['id']}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(claim, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        append_entry(repo / LEDGER_PATH, "claim", {"claim_id": claim["id"], "claim_sha256": claim_digest(claim),
                                                   "path": path.relative_to(repo).as_posix()})
        print(path.relative_to(repo).as_posix(), file=out)
        return 0

    if a.cmd in ("verify", "verdict"):
        _, claim = _load_claim(repo, a.claim)
        v = verify_claim(claim, repo, kr)
        if a.cmd == "verdict":
            secret = read_secret(a.sign_key)
            if keyring_public(kr, a.key_id) != ed25519_public(secret):
                raise PccError(f"key {a.key_id} is not the keyring key for this secret; a verdict must be signed by a keyring key")
            sig = make_signature(secret, a.key_id, "verdict", verdict_subject(v))
            e = append_entry(repo / LEDGER_PATH, "verdict", v, sig)
            v = dict(v, ledger_seq=e["seq"], ledger_hash=e["hash"])
        _print_verdict(v, a.json, out)
        return _exit_for(v["verdict"])

    if a.cmd == "verify-all":
        worst = 0
        for p in sorted((repo / CLAIMS_DIR).glob("*.json")) if (repo / CLAIMS_DIR).is_dir() else []:
            v = verify_claim(load_json(p), repo, kr)
            _print_verdict(v, a.json, out)
            worst = max(worst, _exit_for(v["verdict"]), key=lambda x: {0: 0, 2: 1, 1: 2}[x])
        return worst

    if a.cmd == "sign":
        secret = read_secret(a.sign_key)
        sig = make_signature(secret, a.key_id, a.subject_kind, sha256_file(a.artifact))
        target = a.artifact.with_name(a.artifact.name.rsplit(".", 1)[0] + ".sig.json")
        target.write_text(json.dumps(sig, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(target, file=out)
        return 0

    if a.cmd == "ledger":
        path = repo / LEDGER_PATH
        if a.ledger_cmd == "init":
            if path.exists():
                raise PccError(f"{LEDGER_PATH} exists")
            e = append_entry(path, "genesis", {"repo": repo.name, "commit": head_commit(repo),
                                               "contract": "docs/SABOTAGE_RESISTANCE.md"})
            print(f"genesis {e['hash']}", file=out)
            return 0
        if a.ledger_cmd == "append-bypass":
            e = append_entry(path, "bypass", {"reason": a.reason, "command": a.command, "session": a.session,
                                              "commit": head_commit(repo), "host": socket.gethostname()})
            print(f"bypass recorded as ledger entry {e['seq']} ({e['hash'][:12]})", file=out)
            return 0
        errors: list[str] = []
        head = read_ledger(path)
        check_chain(head, errors)
        if a.base and not errors:
            text = git(repo, "show", f"{a.base}:{LEDGER_PATH}")
            if text is None:
                print(f"ledger: {a.base} has no {LEDGER_PATH}; nothing to compare", file=out)
            else:
                base = read_ledger_text(text)
                check_chain(base, errors)
                check_prefix(base, head, errors)
        if not errors:
            check_claim_types(repo, head, errors)
        for err in errors:
            print(err, file=out)
        print(f"ledger: {len(head)} entries, {'BROKEN' if errors else 'chain ok'}", file=out)
        return 1 if errors else 0

    if a.cmd == "standing":
        _, claim = _load_claim(repo, a.claim)
        st = standing(claim, read_ledger(repo / LEDGER_PATH), kr)
        if a.json:
            print(json.dumps(st, sort_keys=True), file=out)
        else:
            print(f"{st['claim_id']}: {st['standing']}", file=out)
            for v in st["verdicts"]:
                print(f"  seq {v['seq']}: {v['verdict']} at {v['commit'][:12]} key={v['key_id']} "
                      f"signed={v['signed']} current={v['current']}", file=out)
        return 0 if st["standing"] == "verified" else 2

    if a.cmd == "standing-by-type":
        table = standing_by_type(repo, kr)
        if a.json:
            print(json.dumps(table, sort_keys=True), file=out)
        else:
            for t, counts in table.items():
                if not counts and t not in CLAIM_TYPES:
                    continue
                body = ", ".join(f"{k}={v}" for k, v in sorted(counts.items())) or "none"
                print(f"{t}: {sum(counts.values())} claim(s): {body}", file=out)
        return 0

    if a.cmd == "sample-for-validation":
        sample = sample_for_validation(repo, kr, a.rate_data, a.rate_interpretive, a.seed, a.rate_literature, a.base)
        a.out.write_text(json.dumps(sample, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"sample: {len(sample['claims'])} claim(s) -> {a.out}", file=out)
        return 0

    if a.cmd == "lint-prose":
        standings = _standings(repo, kr)
        findings: list[str] = []
        if a.stdin:
            findings += [f"<stdin>: {f}" for f in lint_prose(sys.stdin.read(), standings)]
        for f in a.files:
            findings += [f"{f}: {x}" for x in lint_prose(f.read_text(encoding="utf-8", errors="replace"), standings)]
        for f in findings:
            print(f, file=out)
        print(f"lint-prose: {len(findings)} finding(s)", file=out)
        return 1 if findings else 0

    if a.cmd == "canary":
        return run_canary(out)
    return 3


if __name__ == "__main__":
    try:
        sys.exit(main())
    except PccError as e:
        print(f"pcc: {e}", file=sys.stderr)
        sys.exit(3)
