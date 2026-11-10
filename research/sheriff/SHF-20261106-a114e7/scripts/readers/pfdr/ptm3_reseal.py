#!/usr/bin/env python3
"""Proves-too-much control 3 (sheriff SHF-20261106-a114e7, reader pfdr): a FULL RESEAL forgery in a
scratch copy. Inflate gap_C of every ok job of cell b28-r2-n512 by 4%, regenerate the two analysis
units with the producer's run.py under python3.11, rewrite the three receipts' artifact hashes and the
journal's unit entries, and re-hash the journal chain. Expected: runbook verify/audit cannot see it
(unkeyed seals; census replay compares only raw-result.json /summary); only git history can.
usage: python3 -I ptm3_reseal.py <scratch_repo> <repo_tools_dir> <python3.11>"""
import hashlib, json, os, shutil, subprocess, sys
root, tools, py311 = sys.argv[1:4]
sys.path.insert(0, tools)
import runbook  # crypto-autoresearcher's own tools/runbook.py, for entry_hash only
E = os.path.join(root, "experiments/EXP-PFDR-bb0d26")
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
jobs_p = os.path.join(E, "runs/RUN-PFDR-4d8c71/toy-main-jobs.jsonl")
lines = open(jobs_p).read().splitlines()
changed = 0
out = []
for line in lines:
    r = json.loads(line)
    if r["cell"] == "b28-r2-n512" and r["status"] == "ok":
        new = int(round(r["gap_C"] * 1.04))
        line = line.replace(f'"gap_C": {r["gap_C"]},', f'"gap_C": {new},', 1)
        assert json.loads(line)["gap_C"] == new
        changed += 1
    out.append(line)
open(jobs_p, "w").write("\n".join(out) + "\n")
print("jobs changed:", changed)
for trial, run, files in (("analyze-main", "RUN-PFDR-243425", ["analysis-main.json", "flags.json", "raw-result.json"]),
                          ("analyze-final", "RUN-PFDR-089edc", ["analysis.json", "flags.json", "raw-result.json"])):
    tmp = os.path.join(root, "regen", run)
    shutil.rmtree(tmp, ignore_errors=True)
    so = open(os.path.join(root, f"regen-{run}.stdout"), "w")
    rc = subprocess.run([py311, "experiments/EXP-PFDR-bb0d26/implementation/run.py", "trial", "--run-dir", tmp,
                         "--run-id", run, "--trial-id", trial, "--plan", "experiments/EXP-PFDR-bb0d26/trial-plan.json"],
                        cwd=root, stdout=so, stderr=subprocess.STDOUT).returncode
    assert rc == 0, rc
    for f in files:
        shutil.copyfile(os.path.join(tmp, f), os.path.join(E, "runs", run, f))
    shutil.copyfile(os.path.join(root, f"regen-{run}.stdout"), os.path.join(E, "runs", run, "stdout.log"))
# reseal receipts
new_receipt_sha = {}
for run in ("RUN-PFDR-4d8c71", "RUN-PFDR-243425", "RUN-PFDR-089edc"):
    d = os.path.join(E, "runs", run)
    rp = os.path.join(d, "execution-receipt.json")
    rec = json.load(open(rp))
    for f in list(rec["artifact_sha256"]):
        rec["artifact_sha256"][f] = sha(os.path.join(d, f))
    open(rp, "w").write(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    new_receipt_sha[run] = (sha(rp), rec["artifact_sha256"])
# reseal journal
jp = os.path.join(E, "runbook-sessions/RBS-PFDR-bb0d26/journal.jsonl")
entries = [json.loads(l) for l in open(jp)]
prev = runbook.GENESIS
for e in entries:
    if e.get("type") == "unit_recorded" and e.get("run_id") in new_receipt_sha and e.get("valid"):
        rs, arts = new_receipt_sha[e["run_id"]]
        e["receipt_sha256"] = rs
        e["artifacts"] = {k: arts[k] for k in e["artifacts"]}
    e["prev"] = prev
    e["hash"] = runbook.entry_hash(e)
    prev = e["hash"]
open(jp, "w").write("".join(json.dumps(e, sort_keys=True) + "\n" for e in entries))
a = json.load(open(os.path.join(E, "runs/RUN-PFDR-089edc/analysis.json")))
c = next(x for x in a["cells"] if x["cell"] == "b28-r2-n512")
print("forged b28-r2-n512:", {k: c[k] for k in ("kappa", "ci95", "z", "cls")}, "summary-level:",
      {k: a[k] for k in ("outcome", "headline", "flagged_cells", "calibration")})
