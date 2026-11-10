#!/usr/bin/env python3
"""Per-trial checker (the plan's check_argv).

    python3 code/check_trial.py {run_dir} --shared-run-dir <SHARED>

Exit codes: 0 valid (a censored closure is a completed trial; its censoring is listed in
`warnings`; a recorded infrastructure kill is not a scientific result and not an invalid trial,
SR-7); 1 invalid scientific / measurement defect (the supervisor stops the plan on it);
2 usage error. One JSON line is printed: {"valid": bool, "reasons": [...], "warnings": [...], "trial": id}.

Checks (specification invalidation_rules / stopping_rules):
  * raw-result.json and manifest.yaml exist, agree with each other and with <SHARED>/trials/<id>.json
    (trial id, sha256 of the trial record) and the run's exit code is 0;
  * trial status completed, no error; no result "invalid" (IR-1/IR-2/IR-3: instance record valid:false,
    descent_check, brute-force disagreement, planted solution not a solution);
  * DER-3 versus direct membership agrees (a mismatch is an instrument defect);
  * IR-5: code/CODE_SHA256.json equals the current code hashes and every loaded-code hash in the
    trial record equals it;
  * no existing shared artifact was modified (adapter record);
  * PC-TRI (SR-4): M-1 at D=4 true and D_solve <= 3;
  * EQS4-AA (SR-5): exact equality with its EQS4 (or EQS4-U) source on M-1..M-5, M-7 at every D and on D_solve;
  * EQS4-FULLFE: C-FE-EQ agreement at every completed D (SR-5);
  * fixtures.json present in <SHARED> with sr1_all_pass.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import yaml

import _paths
import analyze


def sha256_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def check(run_dir, shared):
    reasons, warnings = [], []
    tid = None

    def bad(msg):
        reasons.append(msg)

    rp, mp = os.path.join(run_dir, "raw-result.json"), os.path.join(run_dir, "manifest.yaml")
    if not os.path.isfile(rp) or not os.path.isfile(mp):
        bad("raw-result.json or manifest.yaml missing")
        return reasons, warnings, tid
    raw = json.load(open(rp))
    try:
        man = yaml.safe_load(open(mp))["run"]
    except Exception as exc:     # noqa: BLE001
        bad(f"manifest.yaml unreadable: {exc!r}")
        return reasons, warnings, tid
    tid = raw.get("trial_id")
    if man.get("trial_id") != tid or (man.get("inputs") or {}).get("trial_id") != tid:
        bad("manifest trial_id disagrees with raw-result.json")
    if raw.get("exit_code") != 0:
        bad(f"driver exit code {raw.get('exit_code')}")
    if raw.get("shared_artifact_violations"):
        bad(f"existing shared artifacts modified: {raw['shared_artifact_violations']}")
    # ---- IR-5
    code_sha = os.path.join(_paths.CODE_DIR, "CODE_SHA256.json")
    import provenance
    try:
        recorded = json.load(open(code_sha))["files"]
    except Exception as exc:     # noqa: BLE001
        recorded = None
        bad(f"IR-5: CODE_SHA256.json unreadable: {exc!r}")
    if recorded is not None and provenance.compute()["files"] != recorded:
        bad("IR-5: code/CODE_SHA256.json is not current for the code on disk")
    # ---- fixtures (SR-1)
    fx = os.path.join(shared, "fixtures.json")
    if not os.path.isfile(fx):
        bad("SR-1: fixtures.json missing in the shared run dir")
    else:
        d = json.load(open(fx))
        if d.get("sr1_all_pass") is not True or len(d.get("fixtures", [])) < 8:
            bad("SR-1: fixtures.json does not show sr1_all_pass over F-1..F-8")
    kind = raw.get("kind")
    if kind == "certify":
        res = (raw.get("certify") or {})
        if "results" not in res:
            bad("certify output missing")
        for r in res.get("results", []):
            if r.get("status") == "not_emitted":
                warnings.append(f"wdag not_emitted for {r.get('key')} (guard; M-1 untouched)")
        return reasons, warnings, tid
    # ---- trial record
    tpath = os.path.join(shared, "trials", f"{tid}.json")
    if not os.path.isfile(tpath):
        bad("shared trial record missing")
        return reasons, warnings, tid
    if raw.get("trial_record_sha256") != sha256_file(tpath):
        bad("trial record sha256 differs from raw-result.json")
    rec = json.load(open(tpath))
    if rec != raw.get("trial_record"):
        bad("raw-result.json trial_record differs from the shared trial record")
    if rec.get("status") != "completed":
        bad(f"trial status {rec.get('status')!r}: {rec.get('error')}")
    res = rec.get("results") or {}
    if res.get("invalid"):
        bad(f"invalid instance: {res['invalid']}")
    for note in ("not_available", "note"):
        if res.get(note):
            warnings.append(f"{note}: {res[note]}")
    # loaded-code hashes (IR-5)
    loaded = ((rec.get("provenance") or {}).get("code_sha256_loaded")) or {}
    if recorded is not None:
        for rel, h in loaded.items():
            if rel in recorded and recorded[rel] != h:
                bad(f"IR-5: loaded {rel} differs from CODE_SHA256.json")
            if rel.startswith("experiments/") and rel not in recorded:
                bad(f"IR-5: loaded {rel} is not in CODE_SHA256.json")
    key, arm = rec.get("key"), rec.get("arm")
    inst, clos, summ = analyze.load(shared)
    my = [i for i in analyze.read_gz_jsonl(os.path.join(shared, "instances.jsonl.gz")) if i.get("key") == key]
    for i in my:
        if i.get("valid") is False:
            bad(f"IR-1/IR-2/IR-3: instance {key} invalid: {i.get('checks')}")
    rows = clos.get(key, [])
    for r in rows:
        if r.get("der3_mismatch"):
            bad(f"DER-3 versus direct membership mismatch at D={r.get('D')} (instrument defect)")
        if r.get("status") not in (None, "ok"):
            warnings.append(f"D={r.get('D')} status {r.get('status')} (censored or infrastructure; recorded, "
                            "not a scientific result)")
    s = summ.get(key)
    if arm == "PC-TRI" and s is not None:
        m1 = s.get("M1_at_4") or {}
        if m1.get("contained") is False or (isinstance(s.get("M3"), int) and s["M3"] > 3):
            bad(f"SR-4: PC-TRI M-1 at D=4 {m1} / D_solve {s.get('M3')} (instrument defect)")
        elif m1.get("contained") is not True or not isinstance(s.get("M3"), int):
            warnings.append(f"PC-TRI not decided (censored/budget): M1_at_4={m1} M3={s.get('M3')}")
    if arm == "PC-TRI" and s is None and rec.get("status") == "completed" and not res.get("not_available"):
        bad("SR-4: PC-TRI produced no summary")
    if arm == "EQS4-AA" and s is not None:
        cell, _, r = key.split("/")
        src_arm = "EQS4-U" if r.endswith("-U") else "EQS4"
        skey = f"{cell}/{src_arm}/{r[:-2] if r.endswith('-U') else r}"
        if skey not in clos or skey not in summ:
            bad(f"SR-5: source record {skey} missing; the A/A comparison cannot be made")
        else:
            for D in sorted(set(analyze.by_D(rows)) | set(analyze.by_D(clos[skey]))):
                if analyze.metrics_signature(rows, D) != analyze.metrics_signature(clos[skey], D):
                    bad(f"SR-5: EQS4-AA differs from {skey} at D={D} (M-1..M-5, M-7)")
            if s.get("M3") != summ[skey].get("M3"):
                bad(f"SR-5: D_solve differs from {skey}: {s.get('M3')} vs {summ[skey].get('M3')}")
    if arm == "EQS4-FULLFE":
        for r in rows:
            if r.get("status") == "ok" and r.get("C_FE_EQ_agree") is False:
                bad(f"SR-5: C-FE-EQ disagreement at D={r.get('D')}")
    return reasons, warnings, tid


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("run_dir")
    p.add_argument("--shared-run-dir", required=True)
    try:
        a = p.parse_args(argv)
    except SystemExit as exc:
        return 2 if exc.code not in (0, None) else 0
    if not os.path.isdir(a.run_dir) or not os.path.isdir(a.shared_run_dir):
        print(json.dumps({"valid": False, "reasons": ["usage: run_dir or shared run dir is not a directory"]}))
        return 2
    reasons, warnings, tid = check(os.path.abspath(a.run_dir), os.path.abspath(a.shared_run_dir))
    print(json.dumps({"valid": not reasons, "trial": tid, "reasons": reasons, "warnings": warnings}))
    return 1 if reasons else 0


if __name__ == "__main__":
    sys.exit(main())
