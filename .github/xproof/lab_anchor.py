#!/usr/bin/env python3
"""Append one entry to the xproof lab chain, then sign it keylessly (Sigstore / GitHub OIDC).

Runs inside .github/workflows/xproof-anchor.yml. Standalone on purpose: it lives on main next to
the workflow and does not import the xproof package.

Inputs arrive ONLY through environment variables (never interpolated into a shell):
    XPROOF_DIGEST, XPROOF_KIND, XPROOF_EXPERIMENT_ID, XPROOF_REFS
plus the GitHub defaults GITHUB_REF, GITHUB_SHA, GITHUB_RUN_ID, GITHUB_RUN_ATTEMPT.
Every one of them is validated here before it touches the chain or git.

ORDER (this is the security argument, see docs/experiment-proofs.md section 7):
    1. append the line to chain.jsonl, commit, push to xproof-lab-anchors.
       A rejected push (race, protection) aborts here: nothing has been signed.
    2. sign the exact line bytes keylessly (Fulcio certificate bound to this workflow, Rekor entry).
    3. write bundles/<seq>.sigstore.json, commit, push (retried).
A lab-identity signature therefore cannot exist without a public chain line.
A line whose bundle never arrives is `unsigned` (void).

Chain format: chain.jsonl, one canonical-JSON object per line:
    {"seq","prev","kind","experiment_id","digest","refs","run_id","run_attempt","repo_sha","created"}
    prev = SHA-256 hex of the previous line's bytes without its newline (64 zeros for seq 0).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

LAB_BRANCH = "xproof-lab-anchors"
MAIN_REF = "refs/heads/main"
ZERO_HASH = "0" * 64
KINDS = ("protocol", "result", "capability", "abandon")
LINE_KEYS = ("seq", "prev", "kind", "experiment_id", "digest", "refs",
             "run_id", "run_attempt", "repo_sha", "created")

_HEX64 = re.compile(r"[0-9a-f]{64}")
_SHA1 = re.compile(r"[0-9a-f]{40}")
_EXP_ID = re.compile(r"[A-Za-z0-9._-]{1,64}")
_SEQ = re.compile(r"0|[1-9][0-9]{0,8}")
_UUID = re.compile(r"[0-9a-f]{64,96}")
_DIGITS = re.compile(r"[0-9]{1,18}")
_CREATED = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z")
MAX_REFS = 32


class Fail(Exception):
    """Refuse to continue. Raised before signing whenever anything is wrong."""


# ---- pure helpers -------------------------------------------------------------------------

def canonical(obj) -> bytes:
    """Same canonical JSON as xproof.core.canonical."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def line_hash(line: bytes) -> str:
    return hashlib.sha256(line).hexdigest()


def parse_refs(raw: str) -> list:
    """Comma-separated chain seqs (digits) or Rekor uuids (64-96 lowercase hex). Seqs become ints."""
    if raw is None or raw.strip() == "":
        return []
    out = []
    for item in raw.split(","):
        item = item.strip()
        if _SEQ.fullmatch(item):
            ref = int(item)
        elif _UUID.fullmatch(item):
            ref = item
        else:
            raise Fail(f"refs: {item[:40]!r} is neither a chain seq nor a Rekor uuid")
        if ref in out:
            raise Fail(f"refs: duplicate reference {item[:40]!r}")
        out.append(ref)
    if len(out) > MAX_REFS:
        raise Fail(f"refs: more than {MAX_REFS} references")
    return out


def validate_inputs(env) -> dict:
    ref = env.get("GITHUB_REF", "")
    if ref != MAIN_REF:
        raise Fail(f"refusing to run on {ref!r}: the lab identity is only valid for {MAIN_REF}")
    digest = env.get("XPROOF_DIGEST", "")
    if not _HEX64.fullmatch(digest):
        raise Fail("digest must be 64 lowercase hex characters")
    kind = env.get("XPROOF_KIND", "")
    if kind not in KINDS:
        raise Fail(f"kind must be one of {', '.join(KINDS)}")
    exp = env.get("XPROOF_EXPERIMENT_ID", "")
    if not _EXP_ID.fullmatch(exp):
        raise Fail("experiment_id must match [A-Za-z0-9._-]{1,64}")
    refs = parse_refs(env.get("XPROOF_REFS", ""))
    if kind == "abandon" and not refs:
        raise Fail("kind abandon needs refs naming the protocol seq(s) being abandoned")
    if kind in ("result", "capability") and refs:
        raise Fail(f"kind {kind} takes no refs")
    sha = env.get("GITHUB_SHA", "")
    if not _SHA1.fullmatch(sha):
        raise Fail("GITHUB_SHA is not a 40-hex commit id")
    run_id, attempt = env.get("GITHUB_RUN_ID", ""), env.get("GITHUB_RUN_ATTEMPT", "")
    if not _DIGITS.fullmatch(run_id) or not _DIGITS.fullmatch(attempt):
        raise Fail("GITHUB_RUN_ID / GITHUB_RUN_ATTEMPT are not integers")
    return {"kind": kind, "experiment_id": exp, "digest": digest, "refs": refs,
            "run_id": int(run_id), "run_attempt": int(attempt), "repo_sha": sha}


def check_line(line: bytes, seq: int, prev: str) -> dict:
    """Strictly validate one existing chain line. Raises Fail."""
    try:
        obj = json.loads(line.decode("utf-8"))
    except Exception as e:
        raise Fail(f"chain line {seq} does not parse: {e}")
    if not isinstance(obj, dict) or tuple(sorted(obj)) != tuple(sorted(LINE_KEYS)):
        raise Fail(f"chain line {seq} has the wrong field set")
    if canonical(obj) != line:
        raise Fail(f"chain line {seq} is not canonical JSON")
    if obj["seq"] != seq or isinstance(obj["seq"], bool):
        raise Fail(f"chain line {seq} carries seq {obj['seq']!r}")
    if obj["prev"] != prev:
        raise Fail(f"chain line {seq}: prev does not match the hash of line {seq - 1}")
    return obj


def read_chain(lab_dir: str) -> list:
    """The chain as a list of (line_bytes, parsed). Refuses to continue on any inconsistency."""
    path = os.path.join(lab_dir, "chain.jsonl")
    if not os.path.exists(path):
        return []
    with open(path, "rb") as f:
        raw = f.read()
    if raw and not raw.endswith(b"\n"):
        raise Fail("chain.jsonl does not end with a newline")
    out, prev = [], ZERO_HASH
    for i, line in enumerate(raw.split(b"\n")[:-1]):
        out.append((line, check_line(line, i, prev)))
        prev = line_hash(line)
    return out


def check_refs(inputs: dict, chain: list) -> None:
    """Integer refs must name earlier protocol entries of the same experiment."""
    for r in inputs["refs"]:
        if isinstance(r, int):
            if r >= len(chain):
                raise Fail(f"ref {r} is not an existing chain seq")
            target = chain[r][1]
            if target["kind"] != "protocol" or target["experiment_id"] != inputs["experiment_id"]:
                raise Fail(f"ref {r} is not a protocol entry of experiment {inputs['experiment_id']}")
        elif inputs["kind"] == "abandon":
            raise Fail("abandon refs must be chain seqs of protocol entries")


def build_line(inputs: dict, chain: list, now: datetime.datetime) -> bytes:
    prev = line_hash(chain[-1][0]) if chain else ZERO_HASH
    obj = {"seq": len(chain), "prev": prev, "kind": inputs["kind"], "experiment_id": inputs["experiment_id"],
           "digest": inputs["digest"], "refs": inputs["refs"], "run_id": inputs["run_id"],
           "run_attempt": inputs["run_attempt"], "repo_sha": inputs["repo_sha"],
           "created": now.strftime("%Y-%m-%dT%H:%M:%SZ")}
    line = canonical(obj)
    check_line(line, obj["seq"], prev)   # self-check
    return line


# ---- git ----------------------------------------------------------------------------------

def git(lab_dir: str, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    cmd = ["git", "-C", lab_dir, "-c", "user.name=xproof-lab-anchor",
           "-c", "user.email=xproof-lab-anchor@users.noreply.github.com", *args]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, cmd, p.stdout, p.stderr)
    return p


def push(lab_dir: str, remote: str) -> None:
    """Plain fast-forward push of HEAD to the lab branch. Never forced."""
    git(lab_dir, "push", remote, f"HEAD:refs/heads/{LAB_BRANCH}")


# ---- signing ------------------------------------------------------------------------------

def sign_with_sigstore(line: bytes) -> str:
    """Keyless signature over the exact line bytes with the ambient GitHub OIDC token.

    sigstore-python 4.5.1: SigningContext has no production() constructor; the equivalent is
    SigningContext.from_trust_config(ClientTrustConfig.production()).
    """
    from sigstore.models import ClientTrustConfig
    from sigstore.oidc import IdentityToken, detect_credential
    from sigstore.sign import SigningContext

    raw = detect_credential()
    if not raw:
        raise Fail("no ambient OIDC credential (the job needs `permissions: id-token: write`)")
    token = IdentityToken(raw)
    ctx = SigningContext.from_trust_config(ClientTrustConfig.production())
    with ctx.signer(token) as signer:
        bundle = signer.sign_artifact(line)
    return bundle.to_json()


def tlog_summary(bundle_json: str) -> tuple:
    entry = json.loads(bundle_json)["verificationMaterial"]["tlogEntries"][0]
    return entry.get("logIndex"), entry.get("integratedTime")


# ---- the run ------------------------------------------------------------------------------

def run(env, lab_dir: str, sign=sign_with_sigstore, now=None, remote: str = "origin", log=print) -> dict:
    inputs = validate_inputs(env)
    now = now or datetime.datetime.now(datetime.timezone.utc)
    chain = read_chain(lab_dir)
    check_refs(inputs, chain)
    line = build_line(inputs, chain, now)
    seq = len(chain)

    # 1. the line becomes public BEFORE any signature exists
    with open(os.path.join(lab_dir, "chain.jsonl"), "ab") as f:
        f.write(line + b"\n")
    git(lab_dir, "add", "chain.jsonl")
    git(lab_dir, "commit", "-q", "-m", f"xproof lab: {inputs['kind']} seq {seq} {inputs['experiment_id']}")
    try:
        push(lab_dir, remote)
    except subprocess.CalledProcessError as e:
        raise Fail(f"push of chain line {seq} was rejected (race or branch protection); NOTHING was signed.\n"
                   f"{(e.stderr or '').strip()}")
    log(f"chain line {seq} pushed ({line_hash(line)}); signing")

    # 2. sign the exact line bytes
    bundle_json = sign(line)
    log_index, integrated = tlog_summary(bundle_json)

    # 3. publish the bundle (retry: the signature already exists in Rekor and the line is public)
    rel = os.path.join("bundles", f"{seq}.sigstore.json")
    os.makedirs(os.path.join(lab_dir, "bundles"), exist_ok=True)
    with open(os.path.join(lab_dir, rel), "w", encoding="utf-8") as f:
        f.write(bundle_json)
    git(lab_dir, "add", rel)
    git(lab_dir, "commit", "-q", "-m", f"xproof lab: bundle {seq}")
    last = None
    for attempt in range(5):
        try:
            push(lab_dir, remote)
            last = None
            break
        except subprocess.CalledProcessError as e:
            last = e
            git(lab_dir, "pull", "--rebase", "-q", remote, LAB_BRANCH, check=False)
    if last is not None:
        # keep the bundle in the job log so it can be recovered by hand
        log("BUNDLE PUSH FAILED; bundle follows so it can be committed manually:")
        log(bundle_json)
        raise Fail(f"line {seq} is public and signed (Rekor index {log_index}) but its bundle could not be pushed")
    log(f"seq={seq} rekor_log_index={log_index} integratedTime={integrated}")
    return {"seq": seq, "line": line, "log_index": log_index, "integrated_time": integrated}


def main(argv=None, env=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--lab-dir", default=os.environ.get("LAB_DIR", "lab"))
    ap.add_argument("--remote", default="origin")
    args = ap.parse_args(argv)
    try:
        run(env if env is not None else os.environ, args.lab_dir, remote=args.remote)
    except Fail as e:
        print(f"xproof-lab-anchor: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
