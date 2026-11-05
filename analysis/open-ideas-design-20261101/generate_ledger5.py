#!/usr/bin/env python3
"""Emit linked H/EXP records and protocol copies for the five PFDR designs."""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from orchestration import fast_yaml  # noqa: E402

spec = importlib.util.spec_from_file_location("g5", os.path.join(HERE, "generate5.py"))
g5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g5)

IDS = json.load(open("/tmp/alloc5.json"))
QID = "RQ-PFDR-ae2fba"


def prop(idea):
    return (fast_yaml.safe_load(open(os.path.join(ROOT, "ledger/proposals", idea + ".yaml"))) or {}).get("idea", {})


def main():
    out = []
    for i, d in enumerate(g5.IDEAS):
        hid, eid = IDS["h"][i], IDS["e"][i]
        p = prop(d["idea"])
        preds = [{"metric": m, "direction": ("different" if di == "equal_within" else di), "minimum_effect": eff}
                 for m, _n, di, eff in d["pred"]]
        h = {"hypothesis": {
            "id": hid, "area": "PFDR", "question_id": QID, "goal_id": None,
            "source_proposal": d["idea"], "proposal_id": d["idea"],
            "title": d["title"],
            "status": "specified", "proposed_by": "open-ideas design pass 2026-11-01",
            "designed_by": "opencode", "created": "2026-11-01", "updated": "2026-11-01",
            "depends_on": [d["idea"], QID],
            "statement": d["h_statement"], "mechanism": d["mechanism"],
            "assumptions": list(p.get("assumptions") or []),
            "predictions": preds,
            "test_boundary": {"instances": [f"cells named in {d['idea']} and DESIGN.md"],
                              "parameters": {"instances": d["instances"], "replicates": d["replicates"],
                                             "tests_in_family": d["tests"]},
                              "implementation": "Not built. The design names the harness and cells; no implementation is claimed ready.",
                              "budget": {"preflight_seconds": d["preflight"], "backend": d["backend"]}},
            "falsification_conditions": list(p.get("falsification_conditions") or []),
            "interpretation_limits": list(p.get("interpretation_limits") or []),
        }}
        # goal_id null is not allowed by the strict schema; drop it rather than invent one.
        h["hypothesis"].pop("goal_id", None)
        open(os.path.join(ROOT, "ledger/hypotheses", hid + ".yaml"), "w").write(
            fast_yaml.yaml.safe_dump(h, sort_keys=False))
        fals = list(p.get("falsification_conditions") or [])
        e = {"experiment": {
            "id": eid, "hypothesis_id": hid, "version": 1, "title": d["title"],
            "status": "review_required", "source_idea": d["idea"], "derived_from_idea": d["idea"],
            "objective": d["question"] + " " + d["comparative"],
            "inputs": {"proposal": f"ledger/proposals/{d['idea']}.yaml",
                       "design_protocol": f"experiments/{eid}/protocol.json",
                       "design_packet": "analysis/open-ideas-design-20261101/DESIGN.md"},
            "controls": [f"A/A: {d['controls']['aa']['comparison']}",
                         f"positive: {d['controls']['positive']['arm']}",
                         f"negative: {d['controls']['negative']['arm']}"],
            "independent_variables": ["arm"],
            "metrics": {"primary": list(d["primary"]), "secondary": []},
            "replication": {"seeds": [20261101, 20261102, 20261103], "independent_instances": max(1, d["instances"])},
            "budget": {"wall_clock_seconds_per_run": d["preflight"], "total_cpu_hours": None,
                       "maximum_memory_gb": 16.0, "maximum_runs": 64},
            "stopping_rules": [d["stopping"]],
            "invalidation_rules": ["a row whose instrument hash differs is excluded",
                                   "a failed control voids the cells it protects"],
            "success_criterion": d["decision"],
            "falsification_criterion": fals[0] if fals else "A primary metric outside the stated interval refutes the claim.",
            "required_artifacts": [f"experiments/{eid}/protocol.json", f"experiments/{eid}/runs/",
                                   f"experiments/{eid}/results/", f"experiments/{eid}/reports/"],
            "assigned_to": "executor-mechanical", "approved_by": None,
        }}
        edir = os.path.join(ROOT, "experiments", eid)
        for sub in ("", "amendments", "runs", "results", "reports"):
            os.makedirs(os.path.join(edir, sub), exist_ok=True)
        open(os.path.join(edir, "specification.yaml"), "w").write(
            fast_yaml.yaml.safe_dump(e, sort_keys=False))
        for sub in ("amendments", "runs", "results", "reports"):
            open(os.path.join(edir, sub, ".gitkeep"), "w").close()
        pd = json.load(open(os.path.join(HERE, "protocols", d["idea"] + ".json")))
        pd["protocol_id"] = eid
        pd["study_dir"] = f"experiments/{eid}"
        pd["links"]["proposal"] = f"ledger/proposals/{d['idea']}.yaml"
        pd["freeze"] = {"status": "draft", "protocol_sha256": None, "commit": None,
                        "frozen_at": None, "filed_before_affected_data": True}
        json.dump(pd, open(os.path.join(edir, "protocol.json"), "w"), indent=2)
        open(os.path.join(edir, "protocol.json"), "a").write("\n")
        out.append((d["idea"], hid, eid))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
