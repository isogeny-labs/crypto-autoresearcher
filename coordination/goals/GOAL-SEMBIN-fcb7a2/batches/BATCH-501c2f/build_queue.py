#!/usr/bin/env python3
"""Builds dispatch_queue.json for BATCH-501c2f and the final handoff preview from the final trial plan.
Run from the repo root: build_queue.py --design-dir coordination/design/<DA>/EXP-SEMBIN-cb5e25
Reads the trial plan and the template ledger/handoffs/TASK-20261106-9da2e3.yaml; writes the queue and
<design-dir>/handoff.preview.yaml. Launches nothing, changes no record."""
import argparse, hashlib, json, re, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "tools"))
from experiment_execution import GENERATED  # noqa: E402

EXP, GOAL, BATCH = "EXP-SEMBIN-cb5e25", "GOAL-SEMBIN-fcb7a2", "BATCH-501c2f"
EXEC, ARCH, DEC = "TASK-20261106-9da2e3", "TASK-20261106-c5d001", "DEC-20261106-e7576f"
TOKEN = "TRIAL-PLAN-SHA256-TOKEN"
EMBED = ("artifact_paths", "budget", "completion_gate", "constraints", "deliverables", "execution",
         "from", "id", "inference", "inputs", "objective", "to", "uncertainty_reduced")

ap = argparse.ArgumentParser()
ap.add_argument("--design-dir", required=True)
args = ap.parse_args()
design = ROOT / args.design_dir

plan_path = ROOT / f"experiments/{EXP}/trial-plan.json"
plan_bytes = plan_path.read_bytes()
plan = json.loads(plan_bytes)
plan_sha = hashlib.sha256(plan_bytes).hexdigest()
assert plan["task_id"] == EXEC and plan["approved_by"] == DEC, "plan task_id or approved_by wrong"
assert plan["queue"] == f"coordination/goals/{GOAL}/batches/{BATCH}/dispatch_queue.json"

per_trial = [f"experiments/{EXP}/runs/{t['run_id']}/{n}" for t in plan["trials"] for n in (*GENERATED, *t["artifacts"])]
text = (ROOT / f"ledger/handoffs/{EXEC}.yaml").read_text()
text = (f"# {EXEC}: prospective executor handoff for {EXP} (preview; canonical path "
        f"ledger/handoffs/{EXEC}.yaml after approval).\n") + text[text.index("handoff:\n"):]
text, n = re.subn(r"  # PER-TRIAL-ARTIFACT-PATHS-MARKER.*\n(?:  # .*\n)*",
                  lambda m: "".join(f"  - {p}\n" for p in per_trial), text, count=1)
assert n == 1 and TOKEN in text, "template markers missing"
text = text.replace(TOKEN, plan_sha)
handoff = yaml.safe_load(text)["handoff"]
if handoff["budget"]["maximum_runs"] != len(plan["trials"]):
    print(f"WARNING: handoff maximum_runs {handoff['budget']['maximum_runs']} != {len(plan['trials'])} trials; fix the template", file=sys.stderr)
design.mkdir(parents=True, exist_ok=True)
(design / "handoff.preview.yaml").write_text(text)

embedded = {k: handoff[k] for k in EMBED}
queue = {
    "batch_id": BATCH, "goal_id": GOAL, "max_concurrent": 1,
    "max_concurrent_basis": "One executor at a time. Machine headroom, not a research cap: the run holds up to 10 GiB resident on a 15 GB host.",
    "notes": ["Written under DEC-20261106-36e212. It launches nothing. Queued tasks have no execution authority until the approval decision is archived and execution_state is ready."],
    "objective": "Admit pass 1 of EXP-SEMBIN-cb5e25 as one runbook session, then its run archive.",
    "schema": "crypto.autoresearch.dispatch_queue.v1",
    "tasks": [
        {"archived_by": ARCH, "artifact_paths": handoff["artifact_paths"], "depends_on": [], "handoff": embedded, "id": EXEC,
         "priority": 10, "review_required": False, "role": "executor", "state": "queued",
         "title": "Run EXP-SEMBIN-cb5e25 pass 1 runbook session RBS-SEMBIN-19ce78",
         "read_scope": [f"experiments/{EXP}", "experiments/EXP-ECTD-9e4248/driver/reused/macaulay.py", "src/crypto_autoresearcher/gf2",
                        "src/semaev_tree.py", "tools", "ledger/hypotheses/H-SEMBIN-e5b2db.yaml", f"ledger/decisions/{DEC}.yaml",
                        f"ledger/handoffs/{EXEC}.yaml"],
         "write_scope": [f"experiments/{EXP}/runs", f"experiments/{EXP}/runbook-sessions", f"experiments/{EXP}/reports"]},
        {"archive": {"binding_mode": "commit", "commit_sha": None, "kind": "snapshot", "parent_sha": None, "path_sha256": {},
                     "record_ids": ["H-SEMBIN-e5b2db", EXP, DEC, EXEC, ARCH], "source_task_ids": [EXEC]},
         "artifact_paths": [f"coordination/design/{ARCH}/snapshot.json"], "depends_on": [EXEC],
         "handoff": {"budget": {"maximum_runs": 0},
                     "completion_gate": ["snapshot.json names the commit holding every run and session file"],
                     "constraints": ["Do not launch a trial."],
                     "deliverables": [f"coordination/design/{ARCH}/snapshot.json"],
                     "from": "coordinator", "id": ARCH, "inputs": [f"ledger/handoffs/{EXEC}.yaml"],
                     "objective": f"Archive the run and session records of {EXP}. Run nothing.", "to": "coordinator",
                     "uncertainty_reduced": "Whether the session and run records have a single commit."},
         "id": ARCH, "priority": 20, "review_required": False, "role": "coordinator", "state": "queued",
         "title": f"Archive {EXP} pass-1 run records",
         "read_scope": [f"experiments/{EXP}/runs", f"experiments/{EXP}/runbook-sessions", f"experiments/{EXP}/reports",
                        f"experiments/{EXP}", "ledger/hypotheses/H-SEMBIN-e5b2db.yaml", f"ledger/decisions/{DEC}.yaml",
                        f"ledger/handoffs/{EXEC}.yaml"],
         "write_scope": [f"coordination/design/{ARCH}"]},
    ],
}
qpath = ROOT / plan["queue"]
qpath.parent.mkdir(parents=True, exist_ok=True)
qpath.write_text(json.dumps(queue, indent=2, sort_keys=True) + "\n")
print("trial_plan_sha256", plan_sha)
print("queue_sha256", hashlib.sha256(qpath.read_bytes()).hexdigest())
print("handoff_preview_sha256", hashlib.sha256((design / "handoff.preview.yaml").read_bytes()).hexdigest())
print("per_trial_paths", len(per_trial), "trials", len(plan["trials"]))
