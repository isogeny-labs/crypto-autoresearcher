#!/usr/bin/env python3
"""Emit ledger hypothesis records and experiment specifications for the 11
open-idea designs, plus a per-experiment copy of the frozen protocol.

Run from the repository root: PYTHONPATH=. python3 analysis/.../generate_ledger.py
"""
import importlib.util
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location("gen", os.path.join(HERE, "generate.py"))
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

from orchestration import fast_yaml  # noqa: E402

A = json.load(open("/tmp/alloc.json"))
QID = {
    "IDEA-20261016-397ac9": "RQ-WESO-8aff57",
    "IDEA-20261016-cdb5e4": "RQ-WESO-8aff57",
    "IDEA-20261016-fb1656": "RQ-WESO-8aff57",
    "IDEA-20261017-0e2dab": "RQ-SEMBIN-ade131",
    "IDEA-20261017-3079bc": "RQ-SEMBIN-ade131",
    "IDEA-20261017-3db2a8": "RQ-SEMBIN-ade131",
    "IDEA-20261017-e9f824": "RQ-SEMBIN-ade131",
    "IDEA-20261018-329d0a": "RQ-KIC-7502b9",
    "IDEA-20261018-5f37a1": "RQ-KIC-7502b9",
    "IDEA-20261018-d4cef4": "RQ-KIC-7502b9",
    "IDEA-20261018-f2cd4d": "RQ-KIC-7502b9",
}
# allocation order per area follows the IDEAS order
counters = {a: 0 for a in A}
MAPPING = {}
for d in gen.IDEAS:
    area = d["area"]
    i = counters[area]
    MAPPING[d["idea"]] = (A[area]["hypothesis"][i], A[area]["experiment"][i])
    counters[area] += 1


def proposal(idea):
    return (fast_yaml.safe_load(open(os.path.join(ROOT, "ledger/proposals", idea + ".yaml"))) or {}).get("idea", {})


def hyp_yaml(d, hid):
    p = proposal(d["idea"])
    preds = []
    for (mid, name, direction, effect) in d["pred"]:
        preds.append({"metric": mid,
                      "direction": "different" if direction == "equal_within" else direction,
                      "minimum_effect": effect})
    return {"hypothesis": {
        "id": hid,
        "question_id": QID[d["idea"]],
        "statement": d["h_statement"],
        "mechanism": d["mechanism"],
        "assumptions": list(p.get("assumptions") or
                            ["The proposal's frozen cells are the test boundary.", "The instrument is the one named in the frozen protocol."]),
        "predictions": preds,
        "test_boundary": {
            "instances": [f"cells and instances named in {d['idea']} and DESIGN.md"],
            "parameters": {"instances": d["instances"], "replicates": d["replicates"],
                           "warmups": d["warmups"], "tests_in_family": d["tests"]},
            "implementation": "Not built. The design names the harness and cells; no implementation is claimed ready.",
            "budget": {"preflight_seconds": d["preflight"], "backend": d["backend"]},
        },
        "falsification_conditions": list(p.get("falsification_conditions") or []),
        "interpretation_limits": list(p.get("interpretation_limits") or []),
        "status": "specified",
        "proposed_by": "open-ideas design pass 2026-10-31",
    }}


def exp_yaml(d, eid, hid):
    p = proposal(d["idea"])
    fals = list(p.get("falsification_conditions") or [])
    seeds = [20261031 + k for k in range(max(1, d["replicates"]))]
    return {"experiment": {
        "id": eid,
        "hypothesis_id": hid,
        "version": 1,
        "title": d["title"],
        "status": "review_required",
        "objective": d["question"] + " " + d["comparative"],
        "inputs": {
            "proposal": f"ledger/proposals/{d['idea']}.yaml",
            "design_protocol": f"experiments/{eid}/protocol.json",
            "design_packet": "analysis/open-ideas-design-20261031/DESIGN.md",
            "cells": {"instances": d["instances"], "replicates": d["replicates"], "warmups": d["warmups"]},
        },
        "controls": [f"A/A: {d['controls']['aa']['comparison']}",
                     f"positive: {d['controls']['positive']['arm']} ({d['controls']['positive']['expected_detection']})",
                     f"negative: {d['controls']['negative']['arm']} ({d['controls']['negative']['null_population']['description'] if isinstance(d['controls']['negative']['null_population'], dict) else d['controls']['negative']['null_population']})"],
        "independent_variables": ["arm"],
        "metrics": {"primary": list(d["primary"]), "secondary": []},
        "replication": {"seeds": seeds, "independent_instances": max(1, d["instances"])},
        "budget": {"wall_clock_seconds_per_run": d["preflight"],
                   "total_cpu_hours": None,
                   "maximum_memory_gb": 16.0,
                   "maximum_runs": max(2, len(d["arms"]) * max(1, d["replicates"]) * 2)},
        "stopping_rules": [d["stopping"]],
        "invalidation_rules": [
            "a row whose instrument hash differs from the frozen build is excluded and reported",
            "a control that fails its expected detection voids the clean cells it was meant to protect",
        ],
        "success_criterion": d["decision"],
        "falsification_criterion": fals[0] if fals else "A primary metric outside the stated interval refutes the claim within the frozen cells.",
        "required_artifacts": [f"experiments/{eid}/protocol.json",
                               f"experiments/{eid}/runs/",
                               f"experiments/{eid}/results/",
                               f"experiments/{eid}/reports/"],
        "assigned_to": "executor-mechanical",
        "approved_by": None,
    }}


def main():
    made = []
    for d in gen.IDEAS:
        hid, eid = MAPPING[d["idea"]]
        # hypothesis
        path = os.path.join(ROOT, "ledger/hypotheses", hid + ".yaml")
        with open(path, "w") as fh:
            fast_yaml.yaml.safe_dump(hyp_yaml(d, hid), fh, sort_keys=False)
        # experiment dir
        edir = os.path.join(ROOT, "experiments", eid)
        for sub in ("", "amendments", "runs", "results", "reports"):
            os.makedirs(os.path.join(edir, sub), exist_ok=True)
        with open(os.path.join(edir, "specification.yaml"), "w") as fh:
            fast_yaml.yaml.safe_dump(exp_yaml(d, eid, hid), fh, sort_keys=False)
        for sub in ("amendments", "runs", "results", "reports"):
            open(os.path.join(edir, sub, ".gitkeep"), "w").close()
        # protocol copy, re-identified
        pd = json.load(open(os.path.join(HERE, "protocols", d["idea"] + ".json")))
        pd["protocol_id"] = eid
        pd["study_dir"] = f"experiments/{eid}"
        pd["links"]["proposal"] = f"ledger/proposals/{d['idea']}.yaml"
        pd["freeze"] = {"status": "draft", "protocol_sha256": None, "commit": None,
                        "frozen_at": None, "filed_before_affected_data": True}
        with open(os.path.join(edir, "protocol.json"), "w") as fh:
            json.dump(pd, fh, indent=2)
            fh.write("\n")
        made.append((d["idea"], hid, eid))
    print(json.dumps(made, indent=2))


if __name__ == "__main__":
    main()
