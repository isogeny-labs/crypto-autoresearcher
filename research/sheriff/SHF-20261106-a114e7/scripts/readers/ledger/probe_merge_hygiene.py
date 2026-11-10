#!/usr/bin/env python3
"""Scratch-git-repo probes of tools/check_merge_hygiene.py at origin/main:
check_session_files (PR #2686, runbook-session bytes) and
check_new_run_manifests (PR #2659, PR-scoped check_run).

Sheriff case SHF-20261106-a114e7, ledger reader (joint LGX). Builds throwaway
git repositories under argv[2]; imports the audited tool from argv[1] and points
its REPO at each scratch repository. Prints JSON.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(sys.argv[1]).resolve() / "tools"
SCRATCH = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(TOOLS))
sys.dont_write_bytecode = True
import check_merge_hygiene as mh  # noqa: E402
import validate_ledger as vl  # noqa: E402

S = "experiments/EXP-T-0a0a0a/runbook-sessions/RBS-T-0a0a0a"
OUTP = f"{S}/steps/S01.out"
LOGP = f"{S}/steps/S01.log"
ENV = {**os.environ, "GIT_AUTHOR_NAME": "probe", "GIT_AUTHOR_EMAIL": "p@x",
       "GIT_COMMITTER_NAME": "probe", "GIT_COMMITTER_EMAIL": "p@x",
       "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}


def sh(repo, *args, check=True):
    return subprocess.run(["git", "-C", str(repo), *args], env=ENV, capture_output=True,
                          text=True, check=check)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def journal(out_bytes, log_bytes, extra_lines=()):
    lines = [{"type": "session_started", "seq": 0, "session_id": "RBS-T-0a0a0a"},
             {"type": "step_finished", "seq": 1, "step_id": "S01",
              "outputs": [{"path": OUTP, "sha256": sha(out_bytes)}],
              "logs": [{"path": LOGP, "sha256": sha(log_bytes)}]}]
    lines += list(extra_lines)
    return ("\n".join(json.dumps(x, sort_keys=True) for x in lines) + "\n").encode()


def write(repo, rel, data):
    p = Path(repo) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)


def new_repo():
    repo = Path(tempfile.mkdtemp(dir=SCRATCH))
    sh(repo, "init", "-q", "-b", "main")
    out, log = b"result 42\n", b"ok\n"
    write(repo, OUTP, out)
    write(repo, LOGP, log)
    write(repo, f"{S}/journal.jsonl", journal(out, log))
    sh(repo, "add", "-A")
    sh(repo, "commit", "-q", "-m", "base: sealed session")
    return repo


def run_check(repo, base):
    saved = mh.REPO
    mh.REPO = str(repo)
    try:
        return mh.check_session_files(base)
    finally:
        mh.REPO = saved


def scenario(name, mutate, base="main", absolute=False):
    repo = new_repo()
    sh(repo, "checkout", "-q", "-b", "pr")
    mutate(repo)
    sh(repo, "add", "-A")
    sh(repo, "commit", "-q", "-m", name, check=False)
    findings = run_check(repo, None if absolute else base)
    shutil.rmtree(repo, ignore_errors=True)
    return {"flagged": bool([f for f in findings if not f.startswith("SKIPPED")]),
            "findings": [f[:260] for f in findings]}


R = {}
R["control: no change to session (unrelated file added)"] = scenario(
    "unrelated", lambda r: write(r, "README.md", b"x\n"))
R["modify sealed output file"] = scenario(
    "modify", lambda r: write(r, OUTP, b"result 43\n"))
R["modify output AND rewrite journal digest to match (journal not a prefix)"] = scenario(
    "modify+journal", lambda r: (write(r, OUTP, b"result 43\n"),
                                 write(r, f"{S}/journal.jsonl", journal(b"result 43\n", b"ok\n"))))
R["delete a sealed file"] = scenario("delete", lambda r: os.remove(Path(r) / LOGP))
R["append a journal line (allowed)"] = scenario(
    "append", lambda r: write(r, f"{S}/journal.jsonl",
                              journal(b"result 42\n", b"ok\n", [{"type": "note", "seq": 2}])))
R["append a journal line re-binding the output to a new digest + add a second output file"] = scenario(
    "append-rebind", lambda r: (write(r, f"{S}/journal.jsonl", journal(
        b"result 42\n", b"ok\n",
        [{"type": "step_finished", "seq": 2, "step_id": "S01",
          "outputs": [{"path": f"{S}/steps/S01.v2.out", "sha256": sha(b"result 43\n")}]}])),
        write(r, f"{S}/steps/S01.v2.out", b"result 43\n")))
R["add an unrecorded extra file inside the sealed session"] = scenario(
    "extra", lambda r: write(r, f"{S}/steps/S01.extra.out", b"forged 43\n"))
R["absolute mode, non-merge commit modifying a sealed file"] = scenario(
    "abs-modify", lambda r: write(r, OUTP, b"result 43\n"), absolute=True)
R["session dir outside experiments/ and examples/ (research/...) modified"] = None


def splice():
    """Two executions of one session id on two branches; merge keeps B's journal and A's log."""
    repo = Path(tempfile.mkdtemp(dir=SCRATCH))
    sh(repo, "init", "-q", "-b", "main")
    write(repo, "README.md", b"base\n")
    sh(repo, "add", "-A"); sh(repo, "commit", "-q", "-m", "base")
    sh(repo, "checkout", "-q", "-b", "a")
    write(repo, OUTP, b"A\n"); write(repo, LOGP, b"log A 96 bytes\n")
    write(repo, f"{S}/journal.jsonl", journal(b"A\n", b"log A 96 bytes\n"))
    sh(repo, "add", "-A"); sh(repo, "commit", "-q", "-m", "exec A")
    sh(repo, "checkout", "-q", "main")
    sh(repo, "merge", "-q", "--no-ff", "a", "-m", "merge A")
    sh(repo, "checkout", "-q", "-b", "b", "main~1")
    write(repo, OUTP, b"B\n"); write(repo, LOGP, b"")
    write(repo, f"{S}/journal.jsonl", journal(b"B\n", b""))
    sh(repo, "add", "-A"); sh(repo, "commit", "-q", "-m", "exec B")
    # PR branch b merges main (A) and resolves: journal+out from B, log from A.
    sh(repo, "merge", "-q", "main", "-m", "merge main", check=False)
    write(repo, OUTP, b"B\n"); write(repo, LOGP, b"log A 96 bytes\n")
    write(repo, f"{S}/journal.jsonl", journal(b"B\n", b""))
    sh(repo, "add", "-A")
    sh(repo, "commit", "-q", "--no-edit", check=False)
    res = {"pr_scope": run_check(repo, "main"), "absolute_scope": run_check(repo, None)}
    shutil.rmtree(repo, ignore_errors=True)
    return {k: {"flagged": bool(v), "findings": [f[:260] for f in v]} for k, v in res.items()}


R["splice: merge keeps execution B's journal/output and execution A's log"] = splice()
R["session dir outside experiments/ and examples/ (research/...) modified"] = {
    "regex_matches": bool(mh.SESSION_FILE.match("research/x/runbook-sessions/RBS-X-000000/journal.jsonl")),
    "note": "SESSION_FILE only matches experiments/<EXP>/runbook-sessions/ and examples/**/runbook-sessions/"}


# --- PR-scoped check_run (check_new_run_manifests) -----------------------------
def manifests_probe():
    repo = Path(tempfile.mkdtemp(dir=SCRATCH))
    good = ("run:\n  id: RUN-T-0b0b0b\n  experiment_id: EXP-T-0a0a0a\n  status: completed\n"
            "  code: {commit: " + "c" * 40 + ", command: python3 x.py}\n  environment: {python: '3'}\n"
            "  inputs: {seed: 1}\n  timing: {wall_seconds: 1}\n  result:\n    certificate: {kind: none}\n")
    cases = {
        "valid": good,
        "flat (schema-failing)": "run_id: RUN-T-0b0b0b\nexperiment_id: EXP-T-0a0a0a\n",
        "empty": "",
        "duplicate certificate.kind discrete_log then none": good.replace(
            "    certificate: {kind: none}\n", "    certificate:\n      kind: discrete_log\n      kind: none\n"),
    }
    out = {}
    saved = mh.REPO
    try:
        mh.REPO = str(repo)
        for name, text in cases.items():
            for fname in ("manifest.yaml", "manifest_v2.yaml"):
                rel = f"experiments/EXP-T-0a0a0a/runs/RUN-T-0b0b0b/{fname}"
                d = repo / "experiments/EXP-T-0a0a0a/runs/RUN-T-0b0b0b"
                shutil.rmtree(d, ignore_errors=True)
                d.mkdir(parents=True)
                (d / fname).write_text(text)
                for art in vl.RUN_CAPTURE_ARTIFACTS:
                    (d / art).write_text("x")
                out[f"{name} as {fname}"] = mh.check_new_run_manifests([rel])
    finally:
        mh.REPO = saved
        shutil.rmtree(repo, ignore_errors=True)
    return out


R["check_new_run_manifests"] = manifests_probe()
json.dump(R, sys.stdout, indent=1)
print()
