#!/usr/bin/env python3
"""J1 run-integrity checks for RP-BATCH-7c689b (TASK-20261103-f8f2d2), validator's own code.

Usage: python3 j1_integrity.py <repo_root> <hydrated_0e5876_arms_tar_gz> <out_json>
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tarfile

import yaml

RUNS = {
    "RUN-SEMAEV-9cab7b": ("EXP-SEMAEV-93d5cc", "icinv-m4"),
    "RUN-SEMAEV-3e69b6": ("EXP-SEMAEV-93d5cc", "fib-004"),
    "RUN-SEMAEV-4be606": ("EXP-SEMAEV-93d5cc", "fib-005"),
    "RUN-SEMAEV-894e27": ("EXP-SEMAEV-93d5cc", "fib-decision"),
    "RUN-SEMAEV-2a8498": ("EXP-SEMAEV-93d5cc", "mtic-007"),
    "RUN-SEMAEV-fcd67c": ("EXP-SEMAEV-93d5cc", "mtic-008"),
    "RUN-SEMAEV-0e5876": ("EXP-SEMAEV-6e9dcf", "mtic-010b"),
}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(root, *args, check=True):
    r = subprocess.run(["git", "-C", root, *args], capture_output=True)
    if check and r.returncode:
        return None
    return r.stdout


def git_blob_sha(root, commit, path):
    b = git(root, "show", f"{commit}:{path}")
    return None if b is None else sha(b)


def main():
    root, hydrated, out_path = sys.argv[1:4]
    out = {}
    for run, (exp, cell) in RUNS.items():
        rd = os.path.join(root, "experiments", exp, "runs", run)
        f = {}
        issues = []
        notes = []
        rec = json.load(open(os.path.join(rd, "execution-receipt.json")))
        launch = json.load(open(os.path.join(rd, "launch.json")))
        man = yaml.safe_load(open(os.path.join(rd, "manifest.yaml")))["run"]
        env = json.load(open(os.path.join(rd, "environment.json")))
        cmd = json.load(open(os.path.join(rd, "command.txt")))
        armsman = json.load(open(os.path.join(rd, "arms-manifest.json")))
        plan_path = os.path.join("experiments", exp, "trial-plan.json")
        spec_path = os.path.join("experiments", exp, "specification.yaml")
        launch_commit = rec["authority"]["commit"]

        # 1. artifact hashes vs execution receipt
        bad = []
        for name, h in rec["artifact_sha256"].items():
            p = os.path.join(rd, name)
            if run == "RUN-SEMAEV-0e5876" and name == "arms.tar.gz":
                p = hydrated
            if not os.path.exists(p):
                bad.append([name, "missing"])
            elif sha(open(p, "rb").read()) != h:
                bad.append([name, "mismatch"])
        on_disk = sorted(x for x in os.listdir(rd) if not x.startswith("."))
        unlisted = sorted(set(on_disk) - set(rec["artifact_sha256"]) - {"execution-receipt.json"})
        f["receipt_artifact_hashes"] = {"n": len(rec["artifact_sha256"]), "bad": bad, "unlisted_files": unlisted}
        if bad:
            issues.append(f"receipt artifact hash failures {bad}")
        if unlisted:
            notes.append(f"files in run dir not hashed by receipt: {unlisted}")

        # 2. status fields
        f["status"] = {"receipt_status": rec["status"], "returncode": rec["returncode"],
                       "check_returncode": rec["check_returncode"], "manifest_status": man["status"],
                       "manifest_valid": man["validity"]["valid"], "outcome": man["result"].get("outcome")}
        if rec["status"] != "output_validated" or rec["returncode"] != 0 or rec["check_returncode"] != 0:
            issues.append("receipt status/returncode not clean")
        if not man["validity"]["valid"]:
            issues.append("manifest validity false")

        # 3. argv consistency: plan trial argv == launch argv == command.txt == manifest command (python path aside)
        plan_now = json.load(open(os.path.join(root, plan_path)))
        plan_at_launch_raw = git(root, "show", f"{launch_commit}:{plan_path}")
        plan_at_launch = json.loads(plan_at_launch_raw) if plan_at_launch_raw else None
        trial = next(t for t in (plan_at_launch or plan_now)["trials"] if t["id"] == cell)
        want = [a.replace("{run_dir}", os.path.join("/home/user/crypto-autoresearcher", "experiments", exp, "runs", run)) for a in trial["argv"]]
        launch_argv = launch["argv"] if isinstance(launch["argv"], list) else None
        man_cmd = list(man["code"]["command"])
        man_cmd_norm = ["python3" if i == 0 and a.endswith("python3") else a for i, a in enumerate(man_cmd)]
        f["argv"] = {"plan": want, "command_txt_equal": cmd == want, "launch_equal": launch_argv == want,
                     "manifest_equal_mod_interpreter": man_cmd_norm == want,
                     "manifest_command": man_cmd, "plan_trial_run_id": trial["run_id"],
                     "check_argv_equal": launch.get("check_argv") == [a.replace("{run_dir}", want[want.index('--run-dir') + 1]) for a in trial["check_argv"]]}
        if not (cmd == want and launch_argv == want):
            issues.append("argv differs between plan, command.txt and launch.json")
        if man_cmd_norm != want:
            if exp == "EXP-SEMAEV-6e9dcf":
                notes.append("manifest code.command names the parent launch.py while command.txt records launch_successor.py (declared in the successor specification implementation.note)")
            else:
                issues.append("manifest command differs from plan argv")
        if trial["run_id"] != run:
            issues.append("plan trial run_id differs")

        # 4. plan and spec hashes at launch commit
        f["plan_sha256"] = {"receipt": rec["plan_sha256"], "launch": launch["plan_sha256"],
                            "at_launch_commit": sha(plan_at_launch_raw) if plan_at_launch_raw else None,
                            "at_head": sha(open(os.path.join(root, plan_path), "rb").read())}
        if not (rec["plan_sha256"] == launch["plan_sha256"] == f["plan_sha256"]["at_launch_commit"]):
            issues.append("plan sha256 does not match plan at launch commit")
        spec_at_launch = git(root, "show", f"{launch_commit}:{spec_path}")
        f["spec_sha256"] = {"environment": env.get("specification_sha256"),
                            "plan": (plan_at_launch or {}).get("specification_sha256"),
                            "at_launch_commit": sha(spec_at_launch) if spec_at_launch else None,
                            "at_head": sha(open(os.path.join(root, spec_path), "rb").read())}
        if not (f["spec_sha256"]["environment"] == f["spec_sha256"]["at_launch_commit"]):
            issues.append("environment specification_sha256 differs from the spec at the launch commit")
        if f["spec_sha256"]["at_head"] != f["spec_sha256"]["at_launch_commit"]:
            notes.append("specification changed after launch (head differs from launch commit; status-field edits expected)")

        # 5. commits
        man_commit = man["code"]["commit"]
        f["commits"] = {"receipt_authority": launch_commit, "launch_authority": launch["authority"]["commit"] if isinstance(launch["authority"], dict) else str(launch["authority"]),
                        "environment": env["commit"], "manifest": man_commit,
                        "manifest_dirty": man["code"].get("dirty")}
        if env["commit"] != launch_commit:
            issues.append("environment commit differs from receipt authority commit")
        if man_commit != launch_commit:
            anc = subprocess.run(["git", "-C", root, "merge-base", "--is-ancestor", launch_commit, man_commit]).returncode == 0
            srcs_same = all(git_blob_sha(root, man_commit, p) == h for p, h in man["code"]["source_sha256"].items())
            f["commits"]["manifest_commit_descends_from_launch"] = anc
            f["commits"]["sources_identical_at_manifest_commit"] = srcs_same
            log = git(root, "log", "-1", "--format=%cI %s", man_commit)
            f["commits"]["manifest_commit_subject"] = log.decode().strip() if log else None
            notes.append(f"manifest code.commit {man_commit[:10]} is not the launch commit {launch_commit[:10]} "
                         f"(descends={anc}, pinned sources identical there={srcs_same})")

        # 6. source hashes: manifest == environment == plan == git blob at launch commit
        man_src = man["code"]["source_sha256"]
        src_bad = []
        for p, h in man_src.items():
            if env["source_sha256"].get(p) != h:
                src_bad.append([p, "environment differs"])
            if (plan_at_launch or plan_now)["source_sha256"].get(p) != h:
                src_bad.append([p, "plan differs"])
            if git_blob_sha(root, launch_commit, p) != h:
                src_bad.append([p, "git blob at launch commit differs"])
        if set(man_src) != set(env["source_sha256"]):
            src_bad.append(["<set>", "manifest and environment source sets differ"])
        f["source_sha256"] = {"n": len(man_src), "bad": src_bad}
        if src_bad:
            issues.append(f"source hash problems {src_bad}")

        # 7. arms.tar.gz members vs arms-manifest.json
        tpath = hydrated if run == "RUN-SEMAEV-0e5876" else os.path.join(rd, "arms.tar.gz")
        mem_bad = []
        with tarfile.open(tpath, "r:gz") as tf:
            files = {m.name: m for m in tf.getmembers() if m.isfile()}
            for name, h in armsman["members"].items():
                if name not in files:
                    mem_bad.append([name, "missing"])
                elif sha(tf.extractfile(files[name]).read()) != h:
                    mem_bad.append([name, "mismatch"])
            extra = sorted(set(files) - set(armsman["members"]))
        f["arms_members"] = {"n_manifest": len(armsman["members"]), "n_tar_files": len(files), "bad": mem_bad, "extra": extra}
        if mem_bad or extra:
            issues.append(f"arms member problems bad={mem_bad} extra={extra}")

        # 8. timings
        f["timing"] = {"receipt": [rec["started_at"], rec["finished_at"]], "launch_started": launch["started_at"],
                       "manifest": [man["timing"]["started_at"], man["timing"]["finished_at"]],
                       "manifest_wall": man["timing"]["wall_seconds"]}
        if not (rec["started_at"] <= man["timing"]["started_at"] <= man["timing"]["finished_at"] <= rec["finished_at"]):
            issues.append("manifest timing not within receipt window")
        if launch["started_at"] != rec["started_at"]:
            issues.append("launch started_at differs from receipt")
        if rec["started_at"] > rec["authority"]["expires_at"]:
            issues.append("launched after authority expiry")

        # 9. environment vs spec statement
        f["environment"] = man["environment"]
        f["issues"] = issues
        f["notes"] = notes
        out[run] = f
        print(run, cell, "ISSUES" if issues else "clean", issues, "| notes:", notes)
    json.dump(out, open(out_path, "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
