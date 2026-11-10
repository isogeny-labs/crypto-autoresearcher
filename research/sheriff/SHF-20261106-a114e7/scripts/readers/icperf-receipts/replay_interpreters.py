#!/usr/bin/env python3
"""Replay every unit of both sessions under several local CPython versions and compare the
whole raw-result.json with the recorded one (ignoring /interpreter and /elapsed_seconds).

Runs the experiments' own bound run.py (crypto-autoresearcher code, allowed by the brief)
with the plan's argv, writing only to a scratch directory given on the command line.
Usage: replay_interpreters.py <repo> <scratch_dir> <python> [<python> ...]
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

repo, scratch = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
pythons = sys.argv[3:]
out = {}
for exp in ("EXP-ICPERF-284bc4", "EXP-ICPERF-283a70"):
    plan = json.loads((repo / "experiments" / exp / "trial-plan.json").read_text())
    for bound, digest in plan["source_sha256"].items():
        assert hashlib.sha256((repo / bound).read_bytes()).hexdigest() == digest, bound
    for py in pythons:
        for t in plan["trials"]:
            rd = scratch / Path(py).name / exp / t["run_id"]
            rd.parent.mkdir(parents=True, exist_ok=True)
            argv = [a.replace("{run_dir}", str(rd)) for a in t["argv"]]
            # the plan argv names the run dir via --run-dir; force it to scratch
            if "--run-dir" in argv:
                argv[argv.index("--run-dir") + 1] = str(rd)
            argv[0] = py
            env = dict(os.environ, PYTHONHASHSEED="0")
            p = subprocess.run(argv, cwd=repo, env=env, capture_output=True, text=True, timeout=120)
            rec = json.loads((repo / "experiments" / exp / "runs" / t["run_id"] / "raw-result.json").read_text())
            try:
                rep = json.loads((rd / "raw-result.json").read_text())
            except OSError as e:
                out[f"{exp}/{t['run_id']}/{Path(py).name}"] = {"rc": p.returncode, "error": str(e), "stderr": p.stderr[-400:]}
                continue
            ign = {"interpreter", "elapsed_seconds"}
            keys = (set(rec) | set(rep)) - ign
            diff = sorted(k for k in keys if rec.get(k, "<absent>") != rep.get(k, "<absent>"))
            out[f"{exp}/{t['run_id']}/{Path(py).name}"] = {"rc": p.returncode, "trial": t["id"],
                                                         "version": rep.get("interpreter", {}).get("version"),
                                                         "keys": len(keys), "differing": diff}
json.dump(out, sys.stdout, indent=1, sort_keys=True)
print()
