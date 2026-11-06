"""Write-once, exact-readback C5 metadata and roster previews for analyze.

Only complete checked geometric campaigns enter this component. Every output
states that descent and controls remain unresolved; no C5 review is claimed.
"""

import hashlib
import json
import os
from pathlib import Path

from c5_metadata_preview import assemble
from c5_selection import select
from candidate_stage import join_path


METADATA = "c5-metadata-preview.jsonl"
ROSTERS = "c5-rosters-preview.jsonl"
SUMMARY = "c5-preview.json"
COHORTS = ("q5-n3", "q7-n3", "q11-n3", "q3-n5")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def plans_from_campaign(campaign):
    """Read only the four plans already bound by the checked campaign."""
    cohorts = campaign.get("cohorts") if isinstance(campaign, dict) else None
    if (not isinstance(campaign, dict)
            or campaign.get("schema") != "pext.geometric-campaign/v1"
            or campaign.get("status") != "complete_checked_geometric_counts; controls_and_descent_pending"
            or not isinstance(cohorts, dict) or set(cohorts) != set(COHORTS)):
        raise ValueError("complete checked geometric campaign required")
    plans = {}
    for cohort in COHORTS:
        path = join_path(cohort)
        if path.is_symlink() or not path.is_file():
            raise ValueError("published C5 join plan missing or symlinked")
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != cohorts[cohort].get("join_plan_sha256"):
            raise ValueError("C5 join plan differs from checked campaign")
        plan = json.loads(data)
        if plan.get("cohort") != cohort:
            raise ValueError("C5 join plan cohort identity mismatch")
        plans[cohort] = plan
    return plans


def artifact_bytes(curves, plans, plan_sha256, source_runs):
    if (not isinstance(curves, list) or not isinstance(plans, dict)
            or set(plans) != set(COHORTS)):
        raise ValueError("all four C5 cohorts required")
    grouped = {cohort: [] for cohort in COHORTS}
    for curve in curves:
        cohort = curve.get("cohort") if isinstance(curve, dict) else None
        if cohort not in grouped:
            raise ValueError("C5 curve belongs to undeclared cohort")
        grouped[cohort].append(curve)
    metadata, rosters = [], []
    for cohort in COHORTS:
        preview = assemble(plans[cohort], grouped[cohort])
        roster = select(plans[cohort], preview["rows"], preview=True)
        if (preview["cohort"] != cohort or roster["cohort"] != cohort
                or roster["status"] != "incomplete_metadata_preview"
                or roster["unit_count"] != preview["unit_count"]):
            raise ValueError("C5 preview identity or incomplete status mismatch")
        metadata.append(preview)
        rosters.append(roster)
    metadata_bytes = b"".join(canonical(row) for row in metadata)
    roster_bytes = b"".join(canonical(row) for row in rosters)
    summary = {"schema": "pext.c5-preview-stage/v1",
               "status": "complete_geometric_identity; descent_and_controls_unresolved",
               "experiment": "EXP-PEXT-bf8f96", "plan_sha256": plan_sha256,
               "source_runs": source_runs,
               "metadata_sha256": hashlib.sha256(metadata_bytes).hexdigest(),
               "rosters_sha256": hashlib.sha256(roster_bytes).hexdigest(),
               "unit_count": sum(row["unit_count"] for row in metadata),
               "selected_preview_count": sum(row["selected_count"] for row in rosters)}
    return metadata_bytes, roster_bytes, canonical(summary)


def write_preview(run_dir, curves, plans, plan_sha256, source_runs):
    """Persist exact preview bytes once, preserving partial attempts."""
    run_dir = Path(run_dir)
    paths = [run_dir / name for name in (METADATA, ROSTERS, SUMMARY)]
    partials = [run_dir / (name + ".partial") for name in (METADATA, ROSTERS, SUMMARY)]
    if any(path.exists() or path.is_symlink() for path in paths + partials):
        raise FileExistsError("C5 preview attempt already exists")
    outputs = artifact_bytes(curves, plans, plan_sha256, source_runs)
    for path, partial, data in zip(paths, partials, outputs):
        with partial.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(partial, path)
    return json.loads(outputs[-1])


def compare_preview(run_dir, curves, plans, plan_sha256, source_runs):
    expected = artifact_bytes(curves, plans, plan_sha256, source_runs)
    for name, data in zip((METADATA, ROSTERS, SUMMARY), expected):
        path = Path(run_dir) / name
        if path.is_symlink() or not path.is_file() or path.read_bytes() != data:
            raise ValueError(f"C5 preview output differs from checked campaign: {name}")
    return {"schema": "pext.c5-preview-check/v1", "valid": True,
            "status": "incomplete_metadata_preview",
            "metadata_sha256": hashlib.sha256(expected[0]).hexdigest(),
            "rosters_sha256": hashlib.sha256(expected[1]).hexdigest()}
