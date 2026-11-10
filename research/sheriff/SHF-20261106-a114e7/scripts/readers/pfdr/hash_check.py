#!/usr/bin/env python3
"""Recompute every receipt-named sha256 of the five EXP-PFDR-bb0d26 runs, the journal's
receipt_sha256 per unit, the journal hash chain shape, and the manifest provenance fields.
usage: python3 -I hash_check.py <repo> <out.json>"""
import hashlib, json, os, sys
import yaml
repo, out_p = sys.argv[1], sys.argv[2]
exp = os.path.join(repo, "experiments/EXP-PFDR-bb0d26")
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()
journal = [json.loads(l) for l in open(os.path.join(exp, "runbook-sessions/RBS-PFDR-bb0d26/journal.jsonl"))]
units = {e["run_id"]: e for e in journal if e["type"] == "unit_recorded" and e.get("valid")}
res = {"runs": {}, "totals": {"files": 0, "match": 0}}
for rid in ["RUN-PFDR-e44a19", "RUN-PFDR-4d8c71", "RUN-PFDR-243425", "RUN-PFDR-cd03e2", "RUN-PFDR-089edc"]:
    d = os.path.join(exp, "runs", rid)
    rec = json.load(open(os.path.join(d, "execution-receipt.json")))
    files = rec["artifact_sha256"]
    mism = [f for f, h in files.items() if sha(os.path.join(d, f)) != h]
    present = sorted(os.listdir(d))
    extra = [f for f in present if f not in files and f != "execution-receipt.json"]
    man = yaml.safe_load(open(os.path.join(d, "manifest.yaml")))["run"]
    env = json.load(open(os.path.join(d, "environment.json")))
    u = units[rid]
    res["runs"][rid] = {"trial": rec["trial_id"], "status": rec["status"], "returncode": rec["returncode"],
        "check_returncode": rec["check_returncode"], "n_files": len(files), "mismatches": mism, "extra_files": extra,
        "receipt_sha256_equals_journal": sha(os.path.join(d, "execution-receipt.json")) == u["receipt_sha256"],
        "journal_artifacts_equal_receipt": all(files.get(k) == v for k, v in (u.get("artifacts") or {}).items()),
        "manifest_commit": man["code"]["commit"], "manifest_dirty": man["code"]["dirty"],
        "manifest_python": man["environment"]["python_version"], "env_python": env["python"],
        "manifest_plan_sha": man["code"]["trial_plan_sha256"], "receipt_plan_sha": rec["plan_sha256"],
        "started": man["timing"]["started_at"], "finished": man["timing"]["finished_at"]}
    res["totals"]["files"] += len(files)
    res["totals"]["match"] += len(files) - len(mism)
res["plan_sha256_now"] = sha(os.path.join(exp, "trial-plan.json"))
res["spec_sha256_now"] = sha(os.path.join(exp, "specification.yaml"))
res["implementation_sha256_now"] = {f: sha(os.path.join(exp, "implementation", f)) for f in
    ["check.py", "labelsum.c", "run.py", "test_unit.py", "vendor/curve.py", "fixtures/kat.json"]}
json.dump(res, open(out_p, "w"), indent=1)
print(json.dumps(res, indent=1))
