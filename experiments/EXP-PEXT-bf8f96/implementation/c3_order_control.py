"""Prospective full-cohort sealed-reduction A/A order control.

Canonical and reversed reads of the same independently checked candidate
artifacts must produce identical canonical curves, coverage and minima. Every
source unit must carry its checked reversed-candidate-enumeration marker.
"""

import hashlib
import json
import os
from pathlib import Path

from geometric_campaign import EXPECTED


ARTIFACT = "c3-order-aa.json"
CANDIDATE_AA = "reverse-cocycle-build-representatives-buckets-and-roots/v1"


def canonical_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def artifact_bytes(curves, campaign, reversed_curves, reversed_campaign,
                   plan_sha256, source_runs):
    if (not isinstance(curves, list) or not isinstance(reversed_curves, list)
            or not isinstance(campaign, dict) or not isinstance(reversed_campaign, dict)
            or campaign.get("schema") != "pext.geometric-campaign/v1"
            or set(campaign.get("cohorts", {})) != set(EXPECTED)
            or curves != reversed_curves or campaign != reversed_campaign):
        raise ValueError("C3 canonical and reverse sealed reductions differ")
    if (not isinstance(plan_sha256, str) or len(plan_sha256) != 64
            or not isinstance(source_runs, dict)
            or set(source_runs) != {"n3core", "n3ext", "n5"}):
        raise ValueError("C3 plan or source RUN identity invalid")
    grouped = {name: [] for name in EXPECTED}
    target_counts = {name: 0 for name in EXPECTED}
    for curve in curves:
        if not isinstance(curve, dict) or curve.get("cohort") not in grouped:
            raise ValueError("C3 curve cohort invalid")
        grouped[curve["cohort"]].append(curve.get("class_index"))
        units = curve.get("units")
        if (not isinstance(units, list) or len(units) != curve.get("T_count")
                or any(not isinstance(unit, dict)
                       or unit.get("candidate_order_aa") != CANDIDATE_AA
                       for unit in units)):
            raise ValueError("C3 candidate-order A/A missing from a curve/T unit")
        target_counts[curve["cohort"]] += len(units)
    if any(indices != list(range(campaign["cohorts"][name]["classes"]))
           for name, indices in grouped.items()):
        raise ValueError("C3 canonical curve coverage incomplete")
    if any(target_counts[name] != campaign["cohorts"][name]["T_blocks"]
           for name in EXPECTED):
        raise ValueError("C3 curve/T A/A coverage incomplete")
    record = {"schema": "pext.control-c3-sealed-order/v1",
              "status": "sealed_reduction_equal; candidate_unit_order_aa_checked",
              "scope": "all four complete checked cohorts; each unit has reverse candidate traversal",
              "plan_sha256": plan_sha256, "source_runs": source_runs,
              "curve_rows_sha256": hashlib.sha256(canonical_bytes(curves)).hexdigest(),
              "campaign_sha256": hashlib.sha256(canonical_bytes(campaign)).hexdigest(),
              "classes_by_cohort": {name: len(grouped[name]) for name in EXPECTED},
              "T_blocks_by_cohort": {name: campaign["cohorts"][name]["T_blocks"]
                                      for name in EXPECTED}}
    return canonical_bytes(record)


def write_artifact(run_dir, curves, campaign, reversed_curves,
                   reversed_campaign, plan_sha256, source_runs):
    path = Path(run_dir) / ARTIFACT
    if path.exists() or path.is_symlink():
        raise FileExistsError("C3 A/A artifact already exists")
    data = artifact_bytes(curves, campaign, reversed_curves,
                          reversed_campaign, plan_sha256, source_runs)
    with path.open("xb") as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno())
    return json.loads(data)


def compare_artifact(run_dir, curves, campaign, reversed_curves,
                     reversed_campaign, plan_sha256, source_runs):
    data = artifact_bytes(curves, campaign, reversed_curves,
                          reversed_campaign, plan_sha256, source_runs)
    path = Path(run_dir) / ARTIFACT
    if path.is_symlink() or not path.is_file() or path.read_bytes() != data:
        raise ValueError("C3 A/A artifact differs from independent readback")
    return {"schema": "pext.control-c3-sealed-order-check/v1", "valid": True,
            "artifact_sha256": hashlib.sha256(data).hexdigest()}
