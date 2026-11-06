#!/usr/bin/env python3
"""Generator for EXP-SEMBIN-cb5e25's trial-plan.json and runbook.yaml (experiment-director, compile mode, round 2).

    python3 experiments/EXP-SEMBIN-cb5e25/compile/build_plan_runbook.py [--run-ids FILE]

Run it from anywhere; paths are derived from this file's location (repo root = four levels up).
It reads and never edits: compile/step_helpers.py (bound by the runbook), specification.yaml, protocol.json, collision-search.json, code/plan.py,
code/cells.py, code/CODE_SHA256.json, the approved-bytes specification preview, and the run-id list.
It writes exactly two files: experiments/EXP-SEMBIN-cb5e25/trial-plan.json and runbook.yaml.

Every value it writes is copied from one of those inputs or from DEC-20261106-36e212 and
experiments/EXP-SEMBIN-cb5e25/design-notes.md, section 6. The pinned constants below are asserted against
the files, so a changed input stops the script instead of producing a plan nobody approved.

--run-ids FILE: newline-delimited RUN-SEMBIN-xxxxxx ids; line 1 is the shared run directory, the next
587 lines are the per-trial run ids in plan order. Default compile/run-ids.txt (checked with
`python3 tools/allocate_id.py --check-file`). With no file present the script allocates them with
`python3 tools/allocate_id.py --next run --area SEMBIN --count 588`.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
EXP = "EXP-SEMBIN-cb5e25"
BASE = f"experiments/{EXP}"
CODE = f"{BASE}/code"
SESSION = "RBS-SEMBIN-19ce78"
TASK_ID = "TASK-20261106-9da2e3"
APPROVED_BY = "DEC-20261106-e7576f"
QUEUE = "coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-501c2f/dispatch_queue.json"
HELPERS = f"{BASE}/compile/step_helpers.py"
PREVIEW = "coordination/design/TASK-20261106-d8dbfa/EXP-SEMBIN-cb5e25/specification.preview.yaml"

# Pinned values (design-notes.md section 6 and the Coordinator's dispatch); each is asserted below.
PH = "a1b0063ed17ded481a3f5d40e71f3227a3fc71661643fd331a7ad9c76e5b8ace"      # protocol canonical hash
PF = "265e0d6788b5192562393650efc638ab852c2a59032af25fad0e817bcdfa0279"      # protocol.json file sha256
S_R = "2276130dc363314e9621ff8a8179a98d88aa1cb7f6283f76ff7d6a3aa17a8a6a"     # specification, review_required bytes
S_A = "3e8ad23cac0135a7cdb0c2a1e01ea8e6d03b19845c6197d53b608dada66677f5"     # approved-bytes preview
MEMORY_MB = 32768            # RUL-3: loose virtual ceiling for the supervisor's RLIMIT_AS; no watchdog_seconds
TOTAL_SECONDS = 43200
RESERVE_SECONDS = 1200
CERT_EXPECTED = ["m3n12", "m4n08", "m3n13", "m3n14", "m4n09"]
BLOB_PAYLOAD = b"EXP-SEMBIN-cb5e25 blob store round trip\n"       # same bytes as compile/step_helpers.py PAYLOAD


def sha(path):
    return hashlib.sha256((REPO / path).read_bytes()).hexdigest()


sys.path.insert(0, str(REPO / CODE))
import cells as CE  # noqa: E402
import plan as PL  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--run-ids", default=str(HERE / "run-ids.txt"))
ap.add_argument("--spec-state", choices=["review_required", "approved"], default="review_required",
                help="review_required (default): specification.yaml must hash to S_R and the runbook binds S_R. "
                     "approved: run after the approval archive swapped the bytes; the file must hash to S_A and the "
                     "runbook binds S_A. The trial plan is identical in both states (it always names S_A).")
args = ap.parse_args()

proto = json.loads((REPO / BASE / "protocol.json").read_text())
spec = yaml.safe_load((REPO / BASE / "specification.yaml").read_text())["experiment"]
assert proto["freeze"]["status"] == "frozen" and proto["freeze"]["protocol_sha256"] == PH
assert sha(f"{BASE}/protocol.json") == PF
assert sha(f"{BASE}/specification.yaml") == (S_R if args.spec_state == "review_required" else S_A)
assert sha(PREVIEW) == S_A
assert BLOB_PAYLOAD == b"EXP-SEMBIN-cb5e25 blob store round trip\n" and len(BLOB_PAYLOAD) == 40
assert 'PAYLOAD = b"EXP-SEMBIN-cb5e25 blob store round trip\\n"' in (REPO / HELPERS).read_text()
COLLISION_SHA = sha(f"{BASE}/collision-search.json")

rows = PL.plan()
assert len(rows) == 582, len(rows)
need = 1 + len(rows) + len(CERT_EXPECTED)
if Path(args.run_ids).is_file():
    run_ids = [x.strip() for x in Path(args.run_ids).read_text().splitlines() if x.strip()]
else:
    out = subprocess.run([sys.executable, str(REPO / "tools/allocate_id.py"), "--next", "run", "--area", "SEMBIN",
                          "--count", str(need)], capture_output=True, text=True, check=True, cwd=REPO).stdout
    run_ids = [x for x in out.splitlines() if x.startswith("RUN-SEMBIN-")]
assert len(run_ids) >= need and len(set(run_ids)) == len(run_ids), (len(run_ids), need)
SHARED = run_ids[0]
assert SHARED == "RUN-SEMBIN-d1204f", SHARED
RUN_DIR = f"{BASE}/runs/{SHARED}"
FIXTURES = f"{RUN_DIR}/fixtures.json"

code_sha = json.loads((REPO / CODE / "CODE_SHA256.json").read_text())["files"]
sources = dict(sorted(code_sha.items()))
for p, h in sources.items():
    assert sha(p) == h, p
for needed in (f"{CODE}/adapter.py", f"{CODE}/check_trial.py", "tools/artifact_store.py"):
    assert needed in sources, needed
sources[f"{CODE}/CODE_SHA256.json"] = sha(f"{CODE}/CODE_SHA256.json")
sources = dict(sorted(sources.items()))

# ---------------------------------------------------------------- trials (plan.py order; certify after the cell's last trial)
CERT_CELLS = [c for c in CE.EXECUTION_ORDER if 21 <= CE.CELLS[c]["N"] <= 26]
assert CERT_CELLS == CERT_EXPECTED, CERT_CELLS
last_of_cell = {}
for i, t in enumerate(rows):
    last_of_cell[t["cell"]] = i
seq = []
for i, t in enumerate(rows):
    seq.append(("run", t))
    if last_of_cell[t["cell"]] == i and t["cell"] in CERT_CELLS:
        seq.append(("certify", {"cell": t["cell"]}))
assert len(seq) == 587

ADAPTER = f"{CODE}/adapter.py"
CHECKER = f"{CODE}/check_trial.py"
COMMON_TAIL = ["--protocol-sha256", PH]
BUDGET = ["--total-seconds", str(TOTAL_SECONDS), "--reserve-seconds", str(RESERVE_SECONDS)]
trials, meta, members = [], {}, {}
for n, (kind, t) in enumerate(seq):
    rid = run_ids[1 + n]
    head = ["python3", ADAPTER, "--run-dir", "{run_dir}", "--shared-run-dir", RUN_DIR]
    if kind == "run":
        cell, arm, r = t["cell"], t["arm"], t["r"]
        tid = f"{cell}__{arm}__r{r}" + ("__EQS4" if arm == "EQS4-AA" else "")     # adapter.trial_id_of
        key = f"{cell}/{arm}/r{r}"                                                  # adapter.trial_key_of
        argv = head + ["--kind", "trial", "--cell", cell, "--arm", arm, "--r", str(r), *COMMON_TAIL,
                       "--wdag", "auto", *BUDGET]
        if arm == "EQS4-AA":
            argv += ["--aa-source", "EQS4"]
        note = f"plan.py row {n}: cell {cell}, arm {arm}, r {r}"
        members.setdefault(cell, []).append(tid)
        meta[tid] = dict(kind="trial", cell=cell, arm=arm, r=r, key=key)
        depends = []
    else:
        cell = t["cell"]
        tid = f"{cell}__certify"
        argv = head + ["--kind", "certify", "--cell", cell, *COMMON_TAIL, *BUDGET]
        note = f"wdag selection pass for {cell} (21 <= N <= 26), after the cell's trials"
        meta[tid] = dict(kind="certify", cell=cell)
        depends = list(members[cell])
    trials.append({
        "argv": argv,
        "check_argv": ["python3", CHECKER, "{run_dir}", "--shared-run-dir", RUN_DIR],
        "artifacts": ["manifest.yaml", "raw-result.json"],
        "depends_on": depends,
        "id": tid,
        "memory_mb": MEMORY_MB,
        "note": note,
        "run_id": rid,
    })
ids = [t["id"] for t in trials]
assert len(set(ids)) == len(ids) and len(trials) == 587

plan = {
    "approved_by": APPROVED_BY,
    "experiment_id": EXP,
    "frozen": True,
    "goal_id": spec["goal_id"],
    "hypothesis_id": spec["hypothesis_id"],
    "input_sha256": {f"{BASE}/protocol.json": PF},
    "queue": QUEUE,
    "question_id": spec["question_id"],
    "schema": "crypto.autoresearch.trial_plan.v1",
    "scope_note": ("Pass 1 of EXP-SEMBIN-cb5e25 (DEC-20261106-36e212): the static grid in code/plan.py order, 582 trials, "
                   "each followed for the five cells m3n12, m4n08, m3n13, m3n14, m4n09 by one wdag selection pass after "
                   "that cell's last trial, 587 in all. Every trial calls code/adapter.py with the frozen protocol hash "
                   "and is checked by code/check_trial.py. memory_mb is the loose virtual ceiling of DR-11, not a "
                   "resource cap. Generated by experiments/EXP-SEMBIN-cb5e25/compile/build_plan_runbook.py."),
    "source_sha256": sources,
    "specification": f"{BASE}/specification.yaml",
    "specification_sha256": S_A,
    "stop_on_invalid_output": True,
    "task_id": TASK_ID,
    "trials": trials,
}
(REPO / BASE / "trial-plan.json").write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
T = sha(f"{BASE}/trial-plan.json")


# ---------------------------------------------------------------- runbook
def eq(ptr, val):
    return {"pointer": ptr, "equals": val}


by_trial = {}
for tid, m in meta.items():
    if m["kind"] == "trial":
        a = [eq("/experiment_id", EXP), eq("/trial_key", m["key"]), eq("/kind", "trial"), eq("/cell", m["cell"]),
             eq("/arm", m["arm"]), eq("/r", m["r"]), eq("/protocol_sha256", PH), eq("/attack_claimed", False),
             {"pointer": "/shared_artifact_violations", "length": 0},
             {"pointer": "/trial_record_sha256", "type": "string"}]
    else:
        a = [eq("/experiment_id", EXP), eq("/trial", tid), eq("/kind", "certify"), eq("/cell", m["cell"]),
             eq("/protocol_sha256", PH), eq("/attack_claimed", False),
             {"pointer": "/shared_artifact_violations", "length": 0},
             {"pointer": "/certify", "type": "object"}]
    by_trial[tid] = {"files": [{"path": "raw-result.json", "json": True, "assertions": a}]}

validity_common = {"files": [{"path": "raw-result.json", "json": True, "assertions": [eq("/trial_id", "{trial_id}")]}]}
run_trial_ids = [t for t, m in meta.items() if m["kind"] == "trial"]
controls = [t for t, m in meta.items() if m["kind"] == "trial" and m["arm"] not in ("EQS4", "EQS4-U")]

binds = [{"path": f"{BASE}/specification.yaml", "sha256": S_R if args.spec_state == "review_required" else S_A},
         {"path": f"{BASE}/protocol.json", "sha256": PF},
         {"path": f"{BASE}/trial-plan.json", "sha256": T},
         {"path": f"{BASE}/collision-search.json", "sha256": COLLISION_SHA},
         {"path": HELPERS, "sha256": sha(HELPERS)}]
binds += [{"path": p, "sha256": h} for p, h in sources.items()]

cells_spec = spec["parameter_grid"]["cells"]
cell_index = {c["id"]: i for i, c in enumerate(cells_spec)}


def sb(ptr, val, f=f"{BASE}/specification.yaml"):
    return {"file": f, "pointer": ptr, "equals": val}


spec_bindings = [
    sb("/experiment/budget/wall_clock_seconds_total", spec["budget"]["wall_clock_seconds_total"]),
    sb("/experiment/budget/peak_rss_gb", spec["budget"]["peak_rss_gb"]),
    sb("/experiment/budget/wall_clock_seconds_per_instance_per_D/N_le_32",
       spec["budget"]["wall_clock_seconds_per_instance_per_D"]["N_le_32"]),
    sb("/experiment/budget/wall_clock_seconds_per_instance_per_D/N_40",
       spec["budget"]["wall_clock_seconds_per_instance_per_D"]["N_40"]),
    sb("/experiment/budget/maximum_workers", spec["budget"]["maximum_workers"]),
    sb("/experiment/fixtures/7/id", "F-8"),
]
for cid in ["m3n11"] + CERT_CELLS + ["m4n10"]:
    spec_bindings.append(sb(f"/experiment/parameter_grid/cells/{cell_index[cid]}", cells_spec[cell_index[cid]]))
spec_bindings += [
    sb("/execution/placement/memory_mb", proto["execution"]["placement"]["memory_mb"], f"{BASE}/protocol.json"),
    sb("/execution/timeout_seconds", proto["execution"]["timeout_seconds"], f"{BASE}/protocol.json"),
    sb("/freeze/status", "frozen", f"{BASE}/protocol.json"),
    sb("/freeze/protocol_sha256", PH, f"{BASE}/protocol.json"),
]
assert spec["budget"]["wall_clock_seconds_total"] == TOTAL_SECONDS
assert proto["execution"]["timeout_seconds"] == TOTAL_SECONDS

DISK_MIN = 6 * 1024 ** 3          # 6442450944
MEM_MIN_KB = 11534336             # 11 GiB in kB
assert DISK_MIN == 6442450944 and MEM_MIN_KB == 11 * 1024 * 1024

steps = []
steps.append({
    "id": "S01-probe-host", "kind": "command", "purpose": "probe",
    "title": "Record the interpreter, the cores, the available memory, the load, the free disk space and the blob store setting",
    "explain": ("Writes environment.json in this step output directory with the free disk space in bytes at the experiment "
                "directory, the MemAvailable line of /proc/meminfo in kilobytes, the value of the CRYPTO_AR_BLOBSTORE "
                "environment variable, and whether the Sage executable named by fixture F-6 exists."),
    "argv": ["python3", HELPERS, "probe", "--out", "{out}/environment.json", "--experiment-dir", BASE,
             "--sage", "/opt/conda-sage/bin/sage", "--meminfo", "/proc/meminfo"],
    "timeout_seconds": 60,
    "validity": {"exit_code": 0, "outputs": [{"path": "{out}/environment.json", "json": True, "assertions": [
        {"pointer": "/py", "equals": 3},
        {"pointer": "/cpus", "type": "integer"},
        {"pointer": "/disk_free", "type": "integer"},
        {"pointer": "/disk_free", "min": DISK_MIN},
        {"pointer": "/load", "type": "number"},
        {"pointer": "/mem_kb", "type": "integer"},
        {"pointer": "/mem_kb", "min": MEM_MIN_KB},
        {"pointer": "/blobstore", "matches": "^(s3://|file:///)"},
        {"pointer": "/sage", "equals": True}]}]},
    "on_failure": [{"when": {"timed_out": True}, "class": "resource_exhaustion", "action": "retry", "max_attempts": 2}],
    "tell_on_failure": ("The host probe failed. One of these holds: the Sage executable is absent, the free disk space is below "
                        "6442450944 bytes, the available memory is below 11534336 kilobytes, or CRYPTO_AR_BLOBSTORE does not "
                        "begin with s3:// or file:///. The session has stopped. Report this step stderr log path and the "
                        "failed assertion."),
})
steps.append({
    "id": "S02-blobstore-round-trip", "kind": "command", "purpose": "probe",
    "title": "Store a fixed small byte string in the blob store and read it back",
    "explain": ("Runs store_from_env().put and .get of tools/artifact_store.py on a fixed 40 byte string and writes "
                "blob-roundtrip.json in this step output directory with the object address, the sha256, the length and "
                "whether the bytes read back are equal to the bytes stored."),
    "argv": ["python3", HELPERS, "blob", "--store-module", "tools/artifact_store.py", "--out", "{out}/blob-roundtrip.json"],
    "timeout_seconds": 120,
    "validity": {"exit_code": 0, "outputs": [{"path": "{out}/blob-roundtrip.json", "json": True, "assertions": [
        {"pointer": "/match", "equals": True},
        {"pointer": "/sha256", "equals": hashlib.sha256(BLOB_PAYLOAD).hexdigest()},
        {"pointer": "/length", "equals": len(BLOB_PAYLOAD)},
        {"pointer": "/uri", "matches": "^(s3://|file:///)"}]}]},
    "on_failure": [{"when": {"timed_out": True}, "class": "resource_exhaustion", "action": "retry", "max_attempts": 2}],
    "tell_on_failure": ("The blob store round trip failed or the bytes read back differ. The session has stopped before any "
                        "run directory exists. Report this step stderr log path and the failed assertion."),
})
steps.append({
    "id": "S03-create-run-dir", "kind": "command", "purpose": "coordination",
    "title": "Create the one run directory that every trial of this session writes into",
    "explain": f"Creates {RUN_DIR} and fails if it already exists.",
    "argv": ["python3", "-c", "import os, sys; os.makedirs(sys.argv[1], exist_ok=False)", RUN_DIR],
    "timeout_seconds": 60,
    "validity": {"exit_code": 0},
    "tell_on_failure": "The run directory could not be created or already exists. The session has stopped. Report this step stderr log path.",
})
steps.append({
    "id": "S04-copy-collision-search", "kind": "command", "purpose": "coordination",
    "title": "Copy collision-search.json into the run directory before the first measurement",
    "explain": (f"Copies {BASE}/collision-search.json to {RUN_DIR}/collision-search.json without overwriting, and writes "
                "collision-copy.json in this step output directory with the sha256 of the source and of the copy."),
    "argv": ["python3", HELPERS, "copy", "--src", f"{BASE}/collision-search.json", "--dst",
             f"{RUN_DIR}/collision-search.json", "--out", "{out}/collision-copy.json"],
    "timeout_seconds": 60,
    "validity": {"exit_code": 0, "outputs": [{"path": "{out}/collision-copy.json", "json": True, "assertions": [
        eq("/source_sha256", COLLISION_SHA), eq("/copy_sha256", COLLISION_SHA)]}]},
    "tell_on_failure": "The collision search record could not be copied into the run directory. The session has stopped. Report this step stderr log path.",
})
steps.append({
    "id": "S05-fixtures", "kind": "command", "purpose": "verification",
    "title": "Run fixtures F-1 to F-8 before any trial",
    "explain": ("Runs code/fixtures.py with the protocol hash and writes fixtures.json into the run directory. It exits 0 only "
                "when every fixture passes (SR-1). The time of this step is outside the 43200 second total of SR-8 and is "
                "recorded in the session journal."),
    "argv": ["python3", f"{CODE}/fixtures.py", "--out", FIXTURES, "--protocol-sha256", PH],
    "timeout_seconds": 3600,
    "validity": {"exit_code": 0, "stdout_matches": "F-8 pass"},
    "on_failure": [{"when": {"timed_out": True}, "class": "resource_exhaustion", "action": "retry", "max_attempts": 2},
                   {"when": {"exit_code": 1}, "class": "implementation_error", "action": "stop"}],
    "tell_on_failure": "A fixture failed or was not covered. SR-1 stops the run before any trial. Report this step stdout log path and run no later step.",
})
fx = [eq("/sr1_all_pass", True), {"pointer": "/fixtures", "length": 8}]
for i in range(8):
    fx += [eq(f"/fixtures/{i}/id", f"F-{i + 1}"), eq(f"/fixtures/{i}/verdict", "pass")]
steps.append({
    "id": "S06-fixtures-record", "kind": "command", "purpose": "verification",
    "title": "Copy fixtures.json into this step output directory and check all eight verdicts",
    "explain": "Binds the fixture verdicts to the journal by digest and asserts that F-1 to F-8 each report pass.",
    "argv": ["python3", "-c", "import shutil, sys; shutil.copyfile(sys.argv[1], sys.argv[2])", FIXTURES,
             "{out}/fixtures.json"],
    "timeout_seconds": 60,
    "validity": {"exit_code": 0, "outputs": [{"path": "{out}/fixtures.json", "json": True, "assertions": fx}]},
    "tell_on_failure": "The recorded fixtures.json does not show eight passing fixtures. SR-1 stops the run. Report this step stderr log path.",
})
steps.append({
    "id": "S07-trials", "kind": "trials",
    "title": "Run the 582 planned trials and the 5 wdag selection passes in plan order",
    "explain": ("Runs each code/adapter.py invocation of the frozen plan in its own supervisor run directory, followed by "
                "code/check_trial.py. All of them write their records into the one run directory of step S03. The 43200 "
                "second total of SR-8 is charged from the first trial."),
    "plan": f"{BASE}/trial-plan.json", "engine": "supervisor", "claim": {"ttl_minutes": 750},
    "timeout_seconds": TOTAL_SECONDS,
    "validity": validity_common, "by_trial": by_trial, "controls": controls,
    "replay": {"mode": "exempt", "exempt_reason": (
        "Every trial argv writes to the shared run directory by a literal path, and the instrument refuses to overwrite a "
        "finished trial, so a re-execution under the audit directory is not possible with the frozen argv. The replay is "
        "reported not_covered.")},
    "on_invalid": "stop",
    "on_failure": [{"when": {"timed_out": True}, "class": "resource_exhaustion", "action": "stop"}],
    "tell_on_failure": ("The trial step stopped. Report the printed failure class and the run directory named by the "
                        "plan. A timeout means the 43200 second total budget (SR-8) is spent: do not run the session again."),
})
steps.append({
    "id": "S08-analysis", "kind": "command", "purpose": "verification",
    "title": "Aggregate the run directory with code/analyze.py",
    "explain": "Writes controls.json and summary.json into the run directory and prints the validity flags.",
    "argv": ["python3", f"{CODE}/analyze.py", "--run-dir", RUN_DIR],
    "timeout_seconds": 1800,
    "validity": {"exit_code": 0, "stdout_matches": "\"flags\""},
    "tell_on_failure": "The analysis script failed. Report this step stderr log path.",
})
steps.append({
    "id": "S09-analysis-record", "kind": "command", "purpose": "verification",
    "title": "Copy controls.json and summary.json into this step output directory and check the validity flags",
    "explain": "Binds the analysis outputs to the journal by digest and asserts that the SR-4 and SR-5 flags are false.",
    "argv": ["python3", "-c",
             "import shutil, sys; [shutil.copyfile(sys.argv[1] + '/' + n, sys.argv[2] + '/' + n) for n in ('controls.json', 'summary.json')]",
             RUN_DIR, "{out}"],
    "timeout_seconds": 60,
    "validity": {"exit_code": 0, "outputs": [
        {"path": "{out}/controls.json", "json": True, "assertions": [{"pointer": "", "type": "object"}]},
        {"path": "{out}/summary.json", "json": True, "assertions": [
            eq("/flags/SR-4_pc_violation", False), eq("/flags/SR-5_aa_discrepancy", False),
            eq("/flags/SR-5_fe_eq_disagreement", False), {"pointer": "/decisive_count", "type": "integer"}]}]},
    "on_failure": [{"when": {"validity": False}, "class": "invalid_measurement", "action": "stop"}],
    "tell_on_failure": "A validity flag is set. SR-4 or SR-5 makes the run invalid. Report this step stderr log path and the failed assertion.",
})

runbook = {
    "schema": "crypto.autoresearch.runbook.v1",
    "experiment_id": EXP,
    "session_id": SESSION,
    "title": ("Run the EXP-SEMBIN-cb5e25 grid, pass 1: fixtures first, then 582 trials and the 5 wdag selection passes, "
              "then the analysis"),
    "purpose": ("Counterexample search against the degree-4 mutant closure of coset-shifted EQS4 systems (Nagao 2015/984 "
                "binary chain). The run writes the closure records M-1 to M-10, the controls and the certificate "
                "records into one run directory and aggregates them with the pre-registered analysis script. "
                "Observations only: the run states no verdict on the hypothesis."),
    "executor_tier": "mechanical",
    "approval": {"mode": "decision_record"},
    "binds": binds,
    "spec_bindings": spec_bindings,
    "environment": {"programs": ["python3"]},
    "steps": steps,
    "metrics": [
        {"name": "trial_wall_seconds", "unit": "seconds", "label": "measured", "step": "S07-trials",
         "file": "raw-result.json", "pointer": "/trial_record/wall_s", "aggregate": ["count", "sum", "median", "max"],
         "trials": run_trial_ids},
        {"name": "closure_censored_fraction", "unit": "fraction", "label": "measured", "step": "S07-trials",
         "file": "raw-result.json", "pointer": "/trial_record/results/summary/censored",
         "aggregate": ["count", "fraction_true"], "trials": run_trial_ids},
    ],
    "report": {"graph_metric": "trial_wall_seconds"},
}
header = ("# Runbook for EXP-SEMBIN-cb5e25, pass 1, compiled by experiment-director (round 2) with\n"
          "# experiments/EXP-SEMBIN-cb5e25/compile/build_plan_runbook.py. Not approved: a committed decision record\n"
          "# must name this file's sha256 (DEC-20261106-e7576f is reserved). The specification bind is the\n"
          "# review_required bytes; the approval archive rebinds it to the approved bytes.\n")
with open(REPO / BASE / "runbook.yaml", "w") as f:
    f.write(header)
    yaml.safe_dump(runbook, f, sort_keys=False, width=100000, default_flow_style=False)
print("trial-plan sha256:", T)
print("trials:", len(trials), "shared run dir:", RUN_DIR)
