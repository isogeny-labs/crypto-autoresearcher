#!/usr/bin/env python3
"""Probes of tools/runbook.py (PRs #2689, #3059) at origin/main: float
tolerance bounds, interpreter-version parity helpers, and the session-id
collision guard, against throwaway inputs and a scratch git repository.

Sheriff case SHF-20261106-a114e7, ledger reader (joint LGX). Imports the
audited tool from argv[1]/tools; writes only under argv[2]. Prints JSON.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]).resolve() / "tools"))
SCRATCH = Path(sys.argv[2]).resolve()
sys.dont_write_bytecode = True
import runbook as rb  # noqa: E402

R = {}


def tol(spec):
    try:
        return rb.parse_tolerance(spec)
    except rb.RunbookError as exc:
        return f"refused: {exc}"


R["parse_tolerance"] = {s: tol(s) for s in (
    "rel_tol=1e-9,abs_tol=1e-12", "rel_tol=0.5", "rel_tol=1", "rel_tol=1e6", "abs_tol=1e300",
    "rel_tol=-1", "rel_tol=nan", "rel_tol=inf", "abs_tol=0")}
R["parse_tolerance mapping"] = {json.dumps(m): tol(m) for m in (
    {"rel_tol": 1.0}, {"abs_tol": 1e9}, {"rel_tol": True}, {}, {"ulps": 4})}

pairs = [
    ("recorded vs 3.13 replay (bb0d26 mean)", -0.26757013662385903, -0.26757013662383594),
    ("1% different", 0.5, 0.505), ("value doubled", 1.0, 2.0), ("sign flipped", 0.3, -0.3),
    ("1e3 vs 1e6", 1e3, 1e6), ("int vs float", 1, 1.0), ("ints differ", 1, 2),
]
tolerances = {"none(exact)": None, "suggested 1e-9/1e-12": {"rel_tol": 1e-9, "abs_tol": 1e-12},
              "rel_tol=0.5": {"rel_tol": 0.5}, "rel_tol=1": {"rel_tol": 1.0},
              "rel_tol=2": {"rel_tol": 2.0}, "abs_tol=1e9": {"abs_tol": 1e9}}
grid = {}
for name, a, b in pairs:
    grid[name] = {t: rb.compare_tolerant(a, b, v)["result"] for t, v in tolerances.items()}
R["compare_tolerant grid"] = grid
# Whole-document: only floats differ, booleans/ints equal -> tolerance governs.
doc_a = {"summary": {"calibration": {"mean": -0.2675, "sd": 0.97, "n": 44, "pass": True}}}
doc_b = {"summary": {"calibration": {"mean": -0.9, "sd": 5.0, "n": 44, "pass": True}}}
R["document: mean -0.2675->-0.9, sd 0.97->5.0, n/pass equal"] = {
    t: rb.compare_tolerant(doc_a, doc_b, v) for t, v in tolerances.items()}

# Interpreter version helpers (#3059).
R["_python_version_of"] = {s: rb._python_version_of(s) for s in (
    "3.11.15", "3.11.15 (main, Oct 1 2026) [GCC]", "CPython 3.13.17", "Python 3.12", "3", "3.11rc1",
    "pypy 3.10", 3.11)}
R["_same_version"] = {f"{a} vs {b}": rb._same_version(a, b) for a, b in (
    ("3.11.15", "3.11.15"), ("3.11.15", "3.11.17"), ("3.11", "3.11.17"), ("3.11.15", "3.13.17"),
    ("3.1", "3.11.17"))}

# Session-id collision guard (#2689), in a scratch git repository.
env = {**os.environ, "GIT_AUTHOR_NAME": "p", "GIT_AUTHOR_EMAIL": "p@x", "GIT_COMMITTER_NAME": "p",
       "GIT_COMMITTER_EMAIL": "p@x", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}
repo = Path(tempfile.mkdtemp(dir=SCRATCH))


def git(*a, check=True):
    return subprocess.run(["git", "-C", str(repo), *a], env=env, capture_output=True, text=True, check=check)


rel = "experiments/EXP-T-0a0a0a/runbook-sessions/RBS-T-0a0a0a/journal.jsonl"
git("init", "-q", "-b", "main")
(repo / "README").write_text("x\n")
git("add", "-A"); git("commit", "-q", "-m", "base")
git("checkout", "-q", "-b", "exec-a")
(repo / rel).parent.mkdir(parents=True)
journal_a = b'{"seq":0,"type":"session_started","owner":"A"}\n'
(repo / rel).write_bytes(journal_a)
git("add", "-A"); git("commit", "-q", "-m", "exec A")
git("checkout", "-q", "main")
os.environ.update({k: v for k, v in env.items() if k.startswith("GIT_")})
coll = {}
coll["no local journal, branch exec-a holds one"] = rb.session_id_collisions(repo, rel, None)
coll["local journal = A's bytes"] = rb.session_id_collisions(repo, rel, journal_a)
coll["local journal extends A (resume append)"] = rb.session_id_collisions(
    repo, rel, journal_a + b'{"seq":1,"type":"note"}\n')
coll["local journal unrelated (B)"] = rb.session_id_collisions(repo, rel, b'{"seq":0,"type":"session_started","owner":"B"}\n')
git("branch", "-D", "exec-a")
coll["after the branch is deleted (A only in unreachable objects)"] = rb.session_id_collisions(repo, rel, None)
R["session_id_collisions"] = coll
# journal_chain_findings: two unrelated chains in history, then a single chain.
git("checkout", "-q", "-b", "two")
(repo / rel).parent.mkdir(parents=True, exist_ok=True)
(repo / rel).write_bytes(journal_a)
git("add", "-A"); git("commit", "-q", "-m", "A")
(repo / rel).write_bytes(b'{"seq":0,"type":"session_started","owner":"B"}\n')
git("add", "-A"); git("commit", "-q", "-m", "B overwrites")
f2, c2 = rb.journal_chain_findings(repo, rel, (repo / rel).read_bytes())
(repo / rel).write_bytes(b'{"seq":0,"type":"session_started","owner":"B"}\n{"seq":1,"type":"note"}\n')
git("add", "-A"); git("commit", "-q", "-m", "B appends")
f3, c3 = rb.journal_chain_findings(repo, rel, (repo / rel).read_bytes())
R["journal_chain_findings"] = {"A then B overwrite: chains": len(c2), "findings": len(f2),
                               "after B appends: chains": len(c3)}
subprocess.run(["rm", "-rf", str(repo)])
print(json.dumps(R, indent=1, default=str))
