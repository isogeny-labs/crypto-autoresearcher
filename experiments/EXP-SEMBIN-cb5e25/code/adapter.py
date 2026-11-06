#!/usr/bin/env python3
"""Per-trial wrapper between tools/experiment_execution.py and code/run.py / certify.py.

    python3 code/adapter.py --run-dir {run_dir} --shared-run-dir <SHARED> --kind trial|certify \\
        --cell C [--arm A --r R] --protocol-sha256 H [--aa-source EQS4|EQS4-U] [--wdag auto] \\
        [--total-seconds 43200 --reserve-seconds 1200] [--trial-id ID] [-- extra run.py args]

{run_dir} is the supervisor's per-trial directory (it already holds launch.json,
command.txt, environment.json). <SHARED> is the one run directory that run.py appends to
(instances.jsonl.gz, closures.jsonl.gz, cost.jsonl, systems/, certificates/, trials/).

What it does
  * records the session start once in <SHARED>/session_start.json (never overwritten) and
    computes remaining = total - reserve - elapsed on EVERY call; run.py gets
    --remaining-seconds (total - elapsed) and --reserve-seconds (so run.py's own SR-3 test
    "predicted > remaining - reserve" is the same inequality) and --timings-file <SHARED>/cost.jsonl;
  * runs run.py (or certify.py) as a subprocess, passing its exit code through; it sets no
    resource limit (never RLIMIT_AS); run.py keeps its own RSS watchdog;
  * writes {run_dir}/raw-result.json and {run_dir}/manifest.yaml;
  * refuses to rerun a finished trial and verifies that no existing shared artifact was changed
    (append-only logs may only grow, with their old bytes intact).

Exit codes: run.py's / certify.py's code when nonzero; 0 success; 2 usage; 3 refused rerun;
4 an existing shared artifact was modified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

import yaml

import _paths
import cells as CE

EXPERIMENT_ID = "EXP-SEMBIN-cb5e25"
HYPOTHESIS_ID = "H-SEMBIN-e5b2db"
APPEND_ONLY = ("instances.jsonl.gz", "closures.jsonl.gz", "cost.jsonl")


def sha256_file(path, limit=None):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        left = limit
        while True:
            chunk = f.read(1 << 20 if left is None else min(1 << 20, left))
            if not chunk:
                break
            h.update(chunk)
            if left is not None:
                left -= len(chunk)
                if left <= 0:
                    break
    return h.hexdigest()


def snapshot(shared):
    snap = {}
    for root, _dirs, files in os.walk(shared):
        for fn in files:
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, shared)
            if rel.endswith(".started"):
                continue
            snap[rel] = {"size": os.path.getsize(p), "sha256": sha256_file(p)}
    return snap


def trial_id_of(a):
    if a.trial_id:
        return a.trial_id
    if a.kind == "certify":
        return f"{a.cell}__certify"
    return f"{a.cell}__{a.arm}__r{a.r}" + (f"__{a.aa_source}" if a.arm == "EQS4-AA" else "")


def trial_key_of(a):
    if a.kind == "certify":
        return f"{a.cell}/certify"
    return f"{a.cell}/{a.arm}/r{a.r}" + ("-U" if a.arm == "EQS4-AA" and a.aa_source == "EQS4-U" else "")


def session_start(shared, tid, clock):
    path = os.path.join(shared, "session_start.json")
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        with open(path) as f:
            return json.load(f)["started_at_epoch"]
    now = clock()
    with os.fdopen(fd, "w") as f:
        json.dump({"started_at_epoch": now, "started_at": datetime.fromtimestamp(now, timezone.utc).isoformat(),
                   "written_by_trial": tid}, f)
    return now


def parse(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run-dir", required=True)
    p.add_argument("--shared-run-dir", required=True)
    p.add_argument("--kind", required=True, choices=["trial", "certify"])
    p.add_argument("--cell", required=True, choices=sorted(CE.CELLS))
    p.add_argument("--arm", choices=CE.ARMS)
    p.add_argument("--r", type=int)
    p.add_argument("--protocol-sha256", required=True)
    p.add_argument("--aa-source", default="EQS4", choices=["EQS4", "EQS4-U"])
    p.add_argument("--wdag", default="auto", choices=["auto", "always", "never"])
    p.add_argument("--total-seconds", type=float, default=43200.0)
    p.add_argument("--reserve-seconds", type=float, default=1200.0)
    p.add_argument("--trial-id", default=None)
    p.add_argument("--no-require-fixtures", action="store_true", help="tests only")
    p.add_argument("extra", nargs="*", help="extra arguments for run.py (after --)")
    a = p.parse_args(argv)
    if a.kind == "trial" and (a.arm is None or a.r is None):
        p.error("--kind trial needs --arm and --r")
    return a


def main(argv=None, clock=time.time):
    try:
        a = parse(argv)
    except SystemExit as exc:
        return 2 if exc.code not in (0, None) else 0
    shared, rdir = os.path.abspath(a.shared_run_dir), os.path.abspath(a.run_dir)
    os.makedirs(shared, exist_ok=True)
    tid, key = trial_id_of(a), trial_key_of(a)
    started = clock()
    t_start_iso = datetime.fromtimestamp(started, timezone.utc).isoformat()
    # ---- refuse reruns and clobbering
    for p in (os.path.join(rdir, "raw-result.json"), os.path.join(rdir, "manifest.yaml")):
        if os.path.exists(p):
            print(json.dumps({"refused": f"{p} exists: finished trial is never rerun"}), file=sys.stderr)
            return 3
    if a.kind == "trial":
        tp = os.path.join(shared, "trials", tid + ".json")
        if os.path.exists(tp) or os.path.exists(tp + ".started"):
            print(json.dumps({"refused": f"trial {tid} already exists in the shared run dir"}), file=sys.stderr)
            return 3
        safe = key.replace("/", "_")
        for rel in (f"systems/{safe}.sys.json.gz",):
            if os.path.exists(os.path.join(shared, rel)):
                print(json.dumps({"refused": f"shared artifact {rel} exists"}), file=sys.stderr)
                return 3
    # ---- dynamic budget
    t0 = session_start(shared, tid, clock)
    elapsed = started - t0
    remaining_net = a.total_seconds - a.reserve_seconds - elapsed
    before = snapshot(shared)
    py = sys.executable
    common = ["--remaining-seconds", repr(a.total_seconds - elapsed), "--reserve-seconds", repr(a.reserve_seconds),
              "--timings-file", os.path.join(shared, "cost.jsonl")]
    if a.kind == "trial":
        cmd = [py, os.path.join(_paths.CODE_DIR, "run.py"), "--run-dir", shared, "--cell", a.cell, "--arm", a.arm,
               "--r", str(a.r), "--protocol-sha256", a.protocol_sha256, "--wdag", a.wdag, *common]
        if a.arm == "EQS4-AA":
            cmd += ["--aa-source", a.aa_source]
        if not a.no_require_fixtures:
            cmd += ["--require-fixtures", os.path.join(shared, "fixtures.json")]
        cmd += list(a.extra)
    else:
        cmd = [py, os.path.join(_paths.CODE_DIR, "certify.py"), "--run-dir", shared, "--cell", a.cell,
               "--protocol-sha256", a.protocol_sha256]
    # no resource limits are set here: the subprocess inherits ours unchanged
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=None, text=True)
    sys.stdout.write(proc.stdout)
    sys.stdout.flush()
    finished = clock()
    after = snapshot(shared)
    # ---- shared artifacts: appended / new, and nothing old modified
    appended, violations = {}, []
    for rel, new in after.items():
        old = before.get(rel)
        if old is None:
            appended[rel] = {"new": True, "size": new["size"], "sha256": new["sha256"]}
        elif old["sha256"] != new["sha256"]:
            if rel in APPEND_ONLY and new["size"] >= old["size"] and \
                    sha256_file(os.path.join(shared, rel), old["size"]) == old["sha256"]:
                appended[rel] = {"new": False, "size_before": old["size"], "size": new["size"],
                                 "sha256": new["sha256"]}
            else:
                violations.append(rel)
    for rel in before:
        if rel not in after:
            violations.append(rel + " (deleted)")
    raw = {"schema": "sembin.trial_raw_result.v1", "experiment_id": EXPERIMENT_ID, "trial_id": tid,
           "trial_key": key, "kind": a.kind, "cell": a.cell, "arm": a.arm, "r": a.r,
           "protocol_sha256": a.protocol_sha256, "command": cmd, "exit_code": proc.returncode,
           "attack_claimed": False,
           "budget": {"total_seconds": a.total_seconds, "reserve_seconds": a.reserve_seconds,
                      "elapsed_seconds": elapsed, "remaining_seconds": remaining_net,
                      "passed_to_run_py": {"remaining_seconds": a.total_seconds - elapsed,
                                           "reserve_seconds": a.reserve_seconds},
                      "session_start_file": "session_start.json"},
           "shared_run_dir": shared, "shared_artifacts_appended": appended,
           "shared_artifact_violations": violations}
    if a.kind == "trial":
        tpath = os.path.join(shared, "trials", tid + ".json")
        if os.path.exists(tpath):
            raw["trial_record_path"] = os.path.relpath(tpath, shared)
            raw["trial_record_sha256"] = sha256_file(tpath)
            with open(tpath) as f:
                raw["trial_record"] = json.load(f)
    else:
        line = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "{}"
        try:
            raw["certify"] = json.loads(line)
        except ValueError:
            raw["certify"] = {"unparsed_stdout_line": line}
        raw["trial"] = tid
    ok = proc.returncode == 0 and not violations
    metrics = {"exit_code": proc.returncode, "appended_files": len(appended), "kind": a.kind}
    with open(os.path.join(rdir, "raw-result.json"), "x") as f:
        json.dump(raw, f, indent=1, sort_keys=True, default=str)
    command_txt = os.path.join(rdir, "command.txt")
    launched = open(command_txt).read().strip() if os.path.exists(command_txt) else json.dumps(sys.argv)
    env_file = os.path.join(rdir, "environment.json")
    commit = None
    if os.path.exists(env_file):
        commit = json.load(open(env_file)).get("commit")
    if not commit:
        import provenance
        commit = provenance.git_state()["commit"]
    run_id = os.path.basename(rdir.rstrip("/"))
    manifest = {"run": {
        "id": run_id, "experiment_id": EXPERIMENT_ID, "hypothesis_id": HYPOTHESIS_ID,
        "trial_id": tid, "status": "completed" if ok else "failed",
        "status_note": "Written by code/adapter.py when run.py/certify.py returned. Completed is not a validity ruling; "
                       "see code/check_trial.py.",
        "attack_claimed": False,
        "code": {"commit": commit, "command_file": "command.txt", "command": launched},
        "environment": {"file": "environment.json", "python": sys.version.split()[0]},
        "inputs": {"trial_id": tid,
                   "parameters": {"cell": a.cell, "arm": a.arm, "r": a.r, "kind": a.kind,
                                  "protocol_sha256": a.protocol_sha256, "shared_run_dir": shared}},
        "timing": {"started_at": t_start_iso, "finished_at": datetime.fromtimestamp(finished, timezone.utc).isoformat(),
                   "wall_seconds": finished - started, "source": "adapter clock"},
        "metrics": metrics,
        "result": {"raw_result": "raw-result.json", "metrics": metrics,
                   "certificate": {"kind": "none", "verified": None,
                                   "note": "measurement trial; certificates (if any) are shared artifacts judged by "
                                           "the independent checker, no discrete_log/decomposition claim"}},
        "artifacts": {"stdout": "stdout.log", "stderr": "stderr.log",
                      "check_stdout": "check.stdout.log", "check_stderr": "check.stderr.log"},
    }}
    with open(os.path.join(rdir, "manifest.yaml"), "x") as f:
        yaml.safe_dump(manifest, f, sort_keys=False)
    if violations:
        print(json.dumps({"error": "existing shared artifact modified", "files": violations}), file=sys.stderr)
        return 4
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
