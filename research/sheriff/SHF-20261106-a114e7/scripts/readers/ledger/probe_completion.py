#!/usr/bin/env python3
"""Adversarial probes of tools/experiment_execution.complete_manifest and of the
YAML loaders on the ledger gate path, at crypto-autoresearcher origin/main.

Sheriff case SHF-20261106-a114e7, ledger reader (joint LGX). Independent of the
producer's tests: the fixture values, the contradiction list and the gap probes
are chosen here. Every write goes to a fresh temporary directory under the
scratch root given as argv[2]; the repository is only imported, never written.

usage: python3 -I -B probe_completion.py <repo> <scratch-root> > out.json
"""
import copy
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
SCRATCH = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(1, str(REPO))
sys.dont_write_bytecode = True

import yaml  # noqa: E402
import experiment_execution as ex  # noqa: E402
import validate_ledger as vl  # noqa: E402
import check_merge_hygiene as mh  # noqa: E402

EXP, RUN = "EXP-PROBE-5e1f2a", "RUN-PROBE-9c0d11"
PLAN = {"experiment_id": EXP, "task_id": "TASK-20261106-5e1f2a",
        "approved_by": "DEC-20261106-5e1f2a", "hypothesis_id": "H-PROBE-5e1f2a",
        "specification": f"experiments/{EXP}/specification.yaml",
        "specification_sha256": "5" * 64, "source_sha256": {"drv.py": "d" * 64},
        "runtime_lock": None, "runtime_lock_sha256": None}
TRIAL = {"id": "t-1", "run_id": RUN, "seed": 1,
         "parameters": {"bits": 24, "family": "toy"}, "curve_id": "ICV1-probe"}
AUTH = {"commit": "c" * 40}
ARGV = [sys.executable, "drv.py", "measure", "/rundir"]
CHECK = [sys.executable, "drv.py", "check", "/rundir"]
STARTED, FINISHED = "2026-11-06T00:00:00+00:00", "2026-11-06T00:00:10+00:00"
PLAN_REL, PLAN_HASH = f"experiments/{EXP}/trial-plan.json", "a" * 64
ENVJSON = {"python": sys.version, "platform": sys.platform,
           "source_sha256": PLAN["source_sha256"],
           "specification_sha256": PLAN["specification_sha256"], "commit": AUTH["commit"],
           "runtime_lock": None, "runtime_lock_sha256": None}
VERSION = sys.version.split()[0]


def base():
    return {"run": {"experiment_id": EXP, "run_id": RUN, "attack_claimed": False,
                    "metrics": {"m": 3}}}


def put(run, dotted, value):
    *parents, leaf = dotted.split(".")
    for part in parents:
        run = run.setdefault(part, {})
    run[leaf] = value


def complete(manifest, raw="default", plan=None, trial=None, command_txt=None):
    """Run complete_manifest in a fresh directory; return an outcome record."""
    directory = Path(tempfile.mkdtemp(dir=SCRATCH))
    try:
        text = manifest if isinstance(manifest, (str, bytes)) else yaml.safe_dump(manifest, sort_keys=False)
        if isinstance(text, str):
            text = text.encode("utf-8")
        (directory / "manifest.yaml").write_bytes(text)
        if raw is not None:
            rawtext = raw if isinstance(raw, str) else json.dumps(
                {"attack_claimed": False, "m": 3} if raw == "default" else raw)
            (directory / "raw-result.json").write_text(rawtext)
        (directory / "command.txt").write_text(
            command_txt if command_txt is not None else json.dumps(ARGV) + "\n")
        (directory / "environment.json").write_text(json.dumps(ENVJSON))
        for name in ("stdout.log", "stderr.log"):
            (directory / name).write_text("")
        before = (directory / "manifest.yaml").read_bytes()
        try:
            record = ex.complete_manifest(directory, plan or PLAN, PLAN_REL, PLAN_HASH,
                                          trial or TRIAL, AUTH, ARGV, CHECK, STARTED, FINISHED)
            after = (directory / "manifest.yaml").read_bytes()
            published = yaml.safe_load(after)
            return {"outcome": "accepted", "action": record.get("action"),
                    "added": record.get("added"),
                    "published_run": published.get("run") if isinstance(published, dict) else published,
                    "bytes_unchanged": after == before}
        except ex.EnvelopeRefused as error:
            after = (directory / "manifest.yaml").read_bytes()
            leftovers = sorted(p.name for p in directory.iterdir() if p.name.startswith("."))
            return {"outcome": "refused", "message": str(error)[:240],
                    "bytes_unchanged": after == before, "hidden_leftovers": leftovers}
        except Exception as error:  # noqa: BLE001 -- record, never hide
            return {"outcome": "error", "type": type(error).__name__, "message": str(error)[:240]}
    finally:
        shutil.rmtree(directory, ignore_errors=True)


results = {"repo": str(REPO), "python": sys.version, "cases": {}}
C = results["cases"]

# --- controls: the unmodified fixtures must be accepted -------------------------
controls = {"partial base (no contradiction)": complete(base())}
agreeing_full = {"run": {"id": RUN, "experiment_id": EXP, "task_id": PLAN["task_id"],
                         "status": "completed",
                         "code": {"commit": AUTH["commit"], "command": json.dumps(ARGV)},
                         "environment": {"python": VERSION}, "inputs": {"seed": 1},
                         "timing": {"wall_seconds": 1}, "result": {"certificate": {"kind": "none"}},
                         "attack_claimed": False}}
controls["complete agreeing envelope"] = complete(agreeing_full)
results["controls"] = controls

# --- A. every plan/trial/authority/environment/clock fact, contradicted ---------
contradictions = [
    ("id", RUN.replace("9c0d11", "ffffff")), ("run_id", RUN.replace("9c0d11", "ffffff")),
    ("experiment_id", "EXP-PROBE-ffffff"), ("task_id", "TASK-20991231-ffffff"),
    ("trial_id", "t-2"), ("approved_by", "DEC-20991231-ffffff"),
    ("hypothesis_id", "H-PROBE-ffffff"),
    ("code.commit", "b" * 40), ("code.commit", "c" * 12),
    ("code.command", json.dumps([sys.executable, "other.py"])),
    ("code.check_command", "true"), ("code.command_file", "cmd.txt"),
    ("environment.commit", "b" * 40), ("environment.source_sha256", {"drv.py": "e" * 64}),
    ("environment.specification_sha256", "6" * 64), ("environment.runtime_lock", "uv.lock"),
    ("environment.runtime_lock_sha256", "7" * 64), ("environment.file", "env.json"),
    ("environment.python", "2.7.18"),
    ("inputs.trial_plan", "experiments/other/trial-plan.json"), ("inputs.plan_sha256", "b" * 64),
    ("inputs.trial_id", "t-2"), ("inputs.seed", 2), ("inputs.seed", "1"), ("inputs.seed", 1.0),
    ("inputs.seed", True), ("inputs.parameters", {"bits": 25, "family": "toy"}),
    ("inputs.parameters", {"bits": "24", "family": "toy"}),
    ("inputs.parameters", {"bits": 24.0, "family": "toy"}),
    ("inputs.curve_id", "ICV1-other"),
    ("timing.started_at", "2026-11-05T23:59:00+00:00"),
    ("timing.finished_at", "2026-11-06T00:00:20+00:00"),
    ("timing.started_at", "2026-11-06T00:00:01"),
    ("timing.wall_seconds", 60), ("timing.wall_seconds", -0.5), ("timing.wall_seconds", float("nan")),
    ("timing.wall_seconds", True),
    ("result.metrics", {"m": 4}), ("result.metrics", {"m": 3.0}),
    ("result.raw_result", "raw.json"),
]
for dotted, value in contradictions:
    manifest = base()
    put(manifest["run"], dotted, value)
    C[f"A:{dotted}={value!r}"] = complete(manifest)

# The same three headline contradictions on an already complete envelope.
full = {"run": {"id": RUN, "experiment_id": EXP, "task_id": "TASK-20991231-ffffff",
                "status": "completed", "code": {"commit": "b" * 40, "command": json.dumps(ARGV)},
                "environment": {"python": VERSION}, "inputs": {"seed": 99},
                "timing": {"wall_seconds": 1}, "result": {"certificate": {"kind": "none"}},
                "attack_claimed": False}}
C["A:complete_envelope_task_seed_commit"] = complete(full)
for field, value in (("task_id", "TASK-20991231-ffffff"), ("inputs.seed", 99), ("code.commit", "b" * 40)):
    one = copy.deepcopy(agreeing_full)
    put(one["run"], field, value)
    C[f"A:complete_envelope_only_{field}"] = complete(one)
# attack_claimed disagreements
for m_claim, r_claim in ((False, True), (True, False)):
    manifest = base()
    manifest["run"]["attack_claimed"] = m_claim
    manifest["run"]["result"] = {"certificate": {"kind": "discrete_log", "verified": True}}
    C[f"A:attack_claimed manifest={m_claim} raw={r_claim}"] = complete(manifest, raw={"attack_claimed": r_claim})

# --- G. gap probes: values this reader expects NOT to be checked ---------------
gaps = {}
m = base(); m["run"]["seed"] = 99
gaps["G1 run.seed (outside inputs) contradicts trial seed"] = complete(m)
gaps["G2 flat shape seed: 99 (outside inputs)"] = complete(
    {"run_id": RUN, "experiment_id": EXP, "attack_claimed": False, "metrics": {"m": 3}, "seed": 99})
m = base(); m["run"]["parameters"] = {"bits": 64}
gaps["G3 run.parameters (outside inputs) contradicts trial parameters"] = complete(m)
m = base(); m["run"]["inputs"] = {"parameters": {"bits": 24, "family": "toy", "bits_effective": 64}}
gaps["G4 inputs.parameters with an extra key"] = complete(m)
m = base(); m["run"]["inputs"] = {"parameters": {}}
gaps["G5 inputs.parameters empty"] = complete(m)
m = base(); m["run"]["hypothesis_id"] = "H-PROBE-ffffff"
gaps["G6 hypothesis_id when the plan has none"] = complete(m, plan={k: v for k, v in PLAN.items() if k != "hypothesis_id"})
m = base(); m["run"]["inputs"] = {"seed": 12345}
gaps["G7 inputs.seed when the trial has no seed"] = complete(m, trial={k: v for k, v in TRIAL.items() if k != "seed"})
m = base(); m["run"]["timing"] = {"started_at": FINISHED, "finished_at": STARTED}
gaps["G8 timing started_at after finished_at (both inside interval)"] = complete(m)
m = base(); m["run"]["environment"] = {"python": f"not {VERSION}; ran under {VERSION}9"}
gaps["G9 environment.python naming another version that contains the version string"] = complete(m)
m = base(); m["run"]["result"] = {"certificate": {"kind": "discrete_log", "verified": True}}
gaps["G10 verified discrete_log certificate while attack_claimed false everywhere"] = complete(m)
gaps["G11 raw-result.json with duplicate attack_claimed (true then false)"] = complete(
    base(), raw='{"attack_claimed": true, "attack_claimed": false, "m": 3}')
gaps["G12 raw-result.json unparseable"] = complete(base(), raw="{not json")
m = base(); m["run"]["status"] = "failed"
gaps["G13 driver status failed after exit 0"] = complete(m)
gaps["G14 empty mapping {}"] = complete("{}\n")
gaps["G15 run: {} (empty nested envelope)"] = complete("run: {}\n")
gaps["G16 flat mapping with one unrelated key"] = complete("note: driver wrote nothing\n")
m = base(); m["run"]["inputs"] = {"Seed": 99}
gaps["G17 case-variant key inputs.Seed"] = complete(m)
m = base(); m["run"]["inputs"] = {"specification_sha256": "6" * 64}
gaps["G18 inputs.specification_sha256 contradicting the plan"] = complete(m)
results["gap_probes"] = gaps

# --- D. duplicate keys in the driver manifest ---------------------------------
dups = {
    "top-level attack_claimed true/false": f"run:\n  experiment_id: {EXP}\n  run_id: {RUN}\n  attack_claimed: true\n  attack_claimed: false\n  metrics: {{m: 3}}\n",
    "nested code.commit": f"run:\n  experiment_id: {EXP}\n  run_id: {RUN}\n  attack_claimed: false\n  metrics: {{m: 3}}\n  code:\n    commit: {'b'*40}\n    commit: {'c'*40}\n",
    "quoted vs plain key": f"run:\n  experiment_id: {EXP}\n  run_id: {RUN}\n  attack_claimed: false\n  metrics: {{m: 3}}\n  inputs:\n    'seed': 2\n    seed: 1\n",
    "merge-key override": f"x: &b {{task_id: TASK-20991231-ffffff}}\nrun:\n  <<: *b\n  task_id: {PLAN['task_id']}\n  experiment_id: {EXP}\n  run_id: {RUN}\n  attack_claimed: false\n  metrics: {{m: 3}}\n",
    "duplicate top-level run": f"run:\n  experiment_id: {EXP}\n  task_id: TASK-20991231-ffffff\nrun:\n  experiment_id: {EXP}\n  run_id: {RUN}\n  attack_claimed: false\n  metrics: {{m: 3}}\n",
}
results["duplicate_driver_keys"] = {k: complete(v) for k, v in dups.items()}

# --- E. empty manifests: complete_manifest and validate_ledger.check_run --------
empties = {"0-byte": b"", "comment-only": b"# nothing\n", "null": b"null\n", "tilde": b"~\n",
           "doc-start": b"---\n", "doc-start-end": b"---\n...\n", "bom-only": "﻿".encode(),
           "whitespace": b"   \n\n", "empty-list": b"[]\n", "scalar": b"just text\n",
           "empty-map": b"{}\n", "run-null": b"run:\n", "run-empty-map": b"run: {}\n"}
results["empty_manifest_complete"] = {k: complete(v) for k, v in empties.items()}


def check_run_on(text: bytes, name="manifest.yaml"):
    root = Path(tempfile.mkdtemp(dir=SCRATCH))
    try:
        run_dir = root / "experiments" / EXP / "runs" / RUN
        run_dir.mkdir(parents=True)
        (run_dir / name).write_bytes(text)
        for art in vl.RUN_CAPTURE_ARTIFACTS:
            (run_dir / art).write_text("{}" if art.endswith(".json") else "x")
        ctx = vl.Ctx(set())
        try:
            vl.check_run(str(run_dir / name), ctx)
        except Exception as error:  # noqa: BLE001
            return {"exception": f"{type(error).__name__}: {str(error)[:160]}"}
        return {"errors": [e.split(": ", 1)[-1] for e in ctx.errors],
                "registered": sorted(ctx.ids)}
    finally:
        shutil.rmtree(root, ignore_errors=True)


results["empty_manifest_check_run"] = {k: check_run_on(v) for k, v in empties.items()}

# A complete, schema-valid manifest, then the same with a planted duplicate key.
valid = {"run": {"id": RUN, "experiment_id": EXP, "status": "completed",
                 "code": {"commit": "c" * 40, "command": "python3 drv.py"},
                 "environment": {"python": "3"}, "inputs": {"seed": 1}, "timing": {"wall_seconds": 1},
                 "result": {"certificate": {"kind": "none"}}}}
valid_text = yaml.safe_dump(valid, sort_keys=False)
dup_text = valid_text.replace("  status: completed\n",
                              "  status: completed\n  experiment_id: EXP-PROBE-ffffff\n")
cert_dup = valid_text.replace("      kind: none\n", "      kind: discrete_log\n      kind: none\n")
results["check_run_duplicate_keys"] = {
    "control_valid_manifest": check_run_on(valid_text.encode()),
    "duplicate experiment_id (last wins)": check_run_on(dup_text.encode()),
    "duplicate certificate.kind discrete_log then none": check_run_on(cert_dup.encode()),
}

# --- F. registry and inventory loaders with a planted duplicate key -------------
def scratch_copy(rel, mutate):
    root = Path(tempfile.mkdtemp(dir=SCRATCH))
    target = root / rel
    target.parent.mkdir(parents=True)
    text = (REPO / rel).read_text(encoding="utf-8")
    target.write_text(mutate(text), encoding="utf-8")
    return root, target


def plant_after_first(key_line_prefix, extra):
    def mutate(text):
        lines = text.splitlines(keepends=True)
        for i, line in enumerate(lines):
            if line.lstrip().startswith(key_line_prefix):
                indent = line[: len(line) - len(line.lstrip())]
                if line.lstrip().startswith("- "):
                    indent += "  "
                lines.insert(i + 1, indent + extra + "\n")
                return "".join(lines)
        raise SystemExit(f"no line starting {key_line_prefix!r}")
    return mutate


loader_results = {}
root, target = scratch_copy("tools/schema_supersession_registry.yaml",
                            plant_after_first("superseded_path:", "superseded_path: ledger/decisions/DEC-PLANTED.yaml"))
try:
    vl.load_schema_supersessions(str(target)); loader_results["schema registry duplicate"] = "accepted"
except Exception as error:  # noqa: BLE001
    loader_results["schema registry duplicate"] = f"refused: {type(error).__name__}: {str(error)[:140]}"
root2, target2 = scratch_copy("tools/run_supersession_registry.yaml",
                              plant_after_first("superseded_path:", "superseded_path: experiments/X/runs/RUN-X-000000/manifest.yaml"))
try:
    vl.load_run_supersessions(str(target2)); loader_results["run registry duplicate"] = "accepted"
except Exception as error:  # noqa: BLE001
    loader_results["run registry duplicate"] = f"refused: {type(error).__name__}: {str(error)[:140]}"
# check_merge_hygiene's absolute registry check, pointed at the scratch copies.
saved = mh.REPO
try:
    combo = Path(tempfile.mkdtemp(dir=SCRATCH))
    (combo / "tools").mkdir()
    shutil.copy(target, combo / "tools/schema_supersession_registry.yaml")
    shutil.copy(REPO / "tools/run_supersession_registry.yaml", combo / "tools/run_supersession_registry.yaml")
    mh.REPO = str(combo)
    loader_results["check_merge_hygiene.check_registry_duplicate_keys (planted schema dup)"] = mh.check_registry_duplicate_keys()
    shutil.copy(REPO / "tools/schema_supersession_registry.yaml", combo / "tools/schema_supersession_registry.yaml")
    loader_results["check_merge_hygiene.check_registry_duplicate_keys (control, main bytes)"] = mh.check_registry_duplicate_keys()
    # Other gate-path registries read with plain safe_load.
    dup_ids = (REPO / "tools/duplicate_run_ids.yaml").read_text(encoding="utf-8")
    (combo / "dup.yaml").write_text(dup_ids + "\n" + dup_ids.split("\n", 1)[0] + "\n")
    try:
        doc = vl._safe_load(open(combo / "dup.yaml", encoding="utf-8"))
        loader_results["tools/duplicate_run_ids.yaml with its first line repeated (plain _safe_load)"] = (
            "accepted" if doc is not None else "accepted (None)")
    except Exception as error:  # noqa: BLE001
        loader_results["tools/duplicate_run_ids.yaml with its first line repeated (plain _safe_load)"] = f"refused: {error}"[:200]
    # check_parses on a ledger-like record with a duplicate key.
    (combo / "ledger" / "decisions").mkdir(parents=True)
    rec = combo / "ledger/decisions/DEC-20991231-ffffff.yaml"
    rec.write_text("decision:\n  id: DEC-20991231-ffffff\n  status: accepted\n  status: rejected\n")
    loader_results["check_merge_hygiene.check_parses on a decision with duplicate status"] = (
        mh.check_parses(["ledger/decisions/DEC-20991231-ffffff.yaml"], report_stale=False) or "no problems reported")
    try:
        loader_results["validate_ledger.load_yaml on the same decision"] = vl.load_yaml(str(rec), vl.Ctx(set()))
    except Exception as error:  # noqa: BLE001
        loader_results["validate_ledger.load_yaml on the same decision"] = f"raised {error}"
finally:
    mh.REPO = saved
results["registry_and_record_loaders"] = loader_results
for p in (root, root2, combo):
    shutil.rmtree(p, ignore_errors=True)

json.dump(results, sys.stdout, indent=1, default=str)
print()
