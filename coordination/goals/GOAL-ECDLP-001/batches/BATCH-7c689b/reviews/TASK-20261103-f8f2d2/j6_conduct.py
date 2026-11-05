#!/usr/bin/env python3
"""J6 successor write-conduct checks for RUN-SEMAEV-0e5876 (TASK-20261103-f8f2d2).

Usage: python3 j6_conduct.py <repo_root> <extracted_0e5876_dir> <out_json>
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tarfile

import yaml

RUN = "experiments/EXP-SEMAEV-6e9dcf/runs/RUN-SEMAEV-0e5876"
RUN_COMMIT = "93280014b7"
PROTECTED = [
    "experiments/EXP-MTIC-001", "experiments/EXP-SEMAEV-93d5cc", "experiments/EXP-SEMAEV-88c46c",
    "experiments/EXP-SEMAEV-6e9dcf/specification.yaml", "experiments/EXP-SEMAEV-6e9dcf/trial-plan.json",
    "experiments/EXP-SEMAEV-6e9dcf/implementation", "harness/semaev.py",
]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def git(root, *a):
    return subprocess.run(["git", "-C", root, *a], capture_output=True, text=True).stdout


def main():
    root, xdir, out_path = sys.argv[1:4]
    out = {}
    handoff = yaml.safe_load(open(os.path.join(root, "ledger/handoffs/TASK-20261019-212d85.yaml")))["handoff"]
    ap = set(handoff["artifact_paths"])
    added = [l.split("\t") for l in git(root, "show", "--format=", "--name-status", RUN_COMMIT).splitlines() if l]
    out["run_commit"] = {
        "files": len(added), "all_added": all(s == "A" for s, _ in added),
        "outside_artifact_paths": [p for _, p in added if p not in ap],
        "artifact_paths_not_written": sorted(ap - {p for _, p in added}),
    }
    # commits between launch and the run commit that touched protected paths (any branch line in HEAD history)
    launch = json.load(open(os.path.join(root, RUN, "launch.json")))["started_at"]
    touched = git(root, "log", "--format=%h %cI %s", f"--since={launch}", "--until=2026-10-24T19:18:26Z",
                  "--", *PROTECTED).splitlines()
    out["protected_paths_commits_between_launch_and_run_commit"] = touched
    # protected archived inputs: HEAD bytes == frozen plan input_sha256
    plan = json.load(open(os.path.join(root, "experiments/EXP-SEMAEV-6e9dcf/trial-plan.json")))
    inp_bad = []
    for p, h in plan["input_sha256"].items():
        fp = os.path.join(root, p)
        if p.endswith("RUN-SEMAEV-0e5876/arms.tar.gz"):
            continue
        if not os.path.exists(fp):
            inp_bad.append([p, "missing at HEAD"])
        elif sha(open(fp, "rb").read()) != h:
            inp_bad.append([p, "HEAD differs from plan"])
    out["plan_inputs_at_head"] = {"n": len(plan["input_sha256"]), "bad": inp_bad}
    # per-arm recorded reads (inputs.json) vs plan / HEAD / parent arms-manifest members
    parent = {"mtic-007": "experiments/EXP-SEMAEV-93d5cc/runs/RUN-SEMAEV-2a8498",
              "mtic-008": "experiments/EXP-SEMAEV-93d5cc/runs/RUN-SEMAEV-fcd67c"}
    arms = {}
    for arm in ("legacy", "repaired"):
        rec = json.load(open(os.path.join(xdir, "arms", arm, "inputs.json")))
        rows = []
        for dest, v in rec.items():
            src, h = v["source"], v["sha256"]
            row = {"dest": dest.split("/arms/")[-1], "source": src, "sha256": h}
            if src.startswith(RUN + "/deps/"):
                dep = src[len(RUN) + len("/deps/"):].split("/")[0]
                member = src.split(f"/deps/{dep}/", 1)[1]
                pm = json.load(open(os.path.join(root, parent[dep], "arms-manifest.json")))["members"]
                row["check"] = "parent arms-manifest member"
                row["ok"] = pm.get(member) == h
                with tarfile.open(os.path.join(root, parent[dep], "arms.tar.gz")) as tf:
                    row["ok_parent_tar_bytes"] = sha(tf.extractfile(member).read()) == h
            else:
                row["check"] = "plan input_sha256 and HEAD bytes"
                row["ok"] = plan["input_sha256"].get(src) == h and sha(open(os.path.join(root, src), "rb").read()) == h
            # the copy inside the arm archive has the recorded hash
            local = os.path.join(xdir, "arms", arm, dest.split(f"/arms/{arm}/", 1)[1])
            row["ok_copy_in_archive"] = os.path.exists(local) and sha(open(local, "rb").read()) == h
            rows.append(row)
        arms[arm] = {"n": len(rows), "all_ok": all(r["ok"] and r["ok_copy_in_archive"] and r.get("ok_parent_tar_bytes", True) for r in rows),
                     "rows": rows}
    out["recorded_reads"] = arms
    # parent dependency archives themselves match the successor plan's frozen hashes
    dep_bad = []
    for d in parent.values():
        for f in ("arms.tar.gz", "arms-manifest.json", "raw-result.json"):
            k = f"{d}/{f}"
            if sha(open(os.path.join(root, k), "rb").read()) != plan["input_sha256"].get(k):
                dep_bad.append(k)
    out["parent_dependency_files_vs_plan"] = {"bad": dep_bad}
    # every path recorded by the arms lies inside the run directory
    outside = [r["dest"] for a in arms.values() for r in a["rows"]
               if not r["dest"].startswith(("legacy/", "repaired/"))]
    out["recorded_writes_outside_run_dir"] = outside
    json.dump(out, open(out_path, "w"), indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in out.items() if k != "recorded_reads"}, indent=1))
    print({a: (v["n"], v["all_ok"]) for a, v in arms.items()})


if __name__ == "__main__":
    main()
