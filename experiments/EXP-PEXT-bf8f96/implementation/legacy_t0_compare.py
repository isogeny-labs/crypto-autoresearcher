"""Prospective C0 class/T=O histogram comparison after checked cohort runs.

The historical executable's separate full-fixture byte replay remains another
regression gate. This checker compares the new checked T=O cover distribution
to every historical class row under the published class alignments.
"""

import hashlib
import json
import os
from pathlib import Path

from legacy_n3_alignment import (FIXTURES, INPUTS, OLD, check_alignment,
                                 compare_certificate)
from legacy_class_bijection import old_models, verify_file


Q3_FIXTURE = OLD / "fixtures/D-n5-q3-cosets.jsonl"
Q3_INPUT = INPUTS / "q3-n5.json"
Q3_FIELD = INPUTS / "q3-n5-field.json"
Q3_MAPPING = INPUTS / "legacy-q3-n5-bijection.json"
COHORTS = {"q5-n3": (5, 3, 252), "q7-n3": (7, 3, 690),
           "q3-n5": (3, 5, 488)}
ARTIFACT = "legacy-t0-comparison.json"


def class_rows(path, q, n, count):
    rows = [json.loads(raw) for raw in path.read_bytes().splitlines()]
    selected = [row for row in rows if row.get("rec") == "curve" and row.get("role") == "class"]
    if len(selected) != count or any(row.get("q") != q or row.get("n") != n
                                     for row in selected):
        raise ValueError("historical class fixture coverage or identity mismatch")
    return selected


def historical_projection(histogram, structures):
    """Keep the old convention: rank one is separate from connected genera."""
    if (not isinstance(histogram, dict) or not histogram
            or any(type(value) is not int or value <= 0 for value in histogram.values())
            or sum(histogram.values()) != structures):
        raise ValueError("new T=O histogram lacks exact structure coverage")
    genus_counts = {}
    rank_one = 0
    for key, count in histogram.items():
        try:
            m, r = map(int, key.split(","))
        except (ValueError, AttributeError):
            raise ValueError("invalid m/r histogram key") from None
        if m < 1 or r < 4:
            raise ValueError("invalid m/r histogram support")
        if m == 1:
            rank_one += count
            continue
        numerator = (1 << m) * (r-4)
        if numerator % 4:
            raise ValueError("nonintegral connected genus")
        genus = numerator // 4 + 1
        genus_counts[str(genus)] = genus_counts.get(str(genus), 0) + count
    if not genus_counts:
        raise ValueError("T=O histogram has no connected structure")
    return {"structures_by_m_r": histogram,
            "structures_by_genus": genus_counts,
            "m1_structures": rank_one,
            "min_genus": min(map(int, genus_counts))}


def compare_cohort(cohort, curves):
    """Compare every checked new curve/T=O summary with the pinned fixture."""
    if cohort not in COHORTS:
        raise ValueError("cohort outside frozen C0 scope")
    q, n, count = COHORTS[cohort]
    if cohort == "q3-n5":
        mapping = json.loads(Q3_MAPPING.read_bytes())
        check = verify_file(mapping, Q3_INPUT, Q3_FIELD, Q3_FIXTURE)
        if check.get("valid") is not True or check.get("matched_classes") != count:
            raise ValueError("q3/n5 identity bijection invalid")
        old = class_rows(Q3_FIXTURE, q, n, count)
        new_indices = [row["class_index"] for row in mapping["rows"]]
    else:
        check_alignment(q)
        old = class_rows(OLD / "fixtures" / FIXTURES[q][0], q, n, count)
        new_indices = list(range(count))
    source = json.loads((INPUTS / f"{cohort}.json").read_bytes())
    representatives = source["representatives"]
    if (not isinstance(curves, list) or len(curves) != count
            or [row.get("class_index") for row in curves] != list(range(count))
            or any(row.get("cohort") != cohort or row.get("model") != representatives[i]
                   for i, row in enumerate(curves))):
        raise ValueError("new checked curve coverage or published identity mismatch")
    for historical_index, (fixture, class_index) in enumerate(zip(old, new_indices)):
        curve = curves[class_index]
        units = curve.get("units")
        if (not isinstance(units, list) or not units
                or units[0].get("T_index") != 0):
            raise ValueError("new checked T=O unit missing")
        unit = units[0]
        projected = historical_projection(unit.get("m_r_histogram"),
                                          unit.get("structures"))
        for key, actual in projected.items():
            if fixture.get(key) != actual:
                raise ValueError(f"C0 {cohort} historical row {historical_index} {key} mismatch")
    fixture_path = Q3_FIXTURE if cohort == "q3-n5" else OLD / "fixtures" / FIXTURES[q][0]
    return {"schema": "pext.legacy-t0-comparison/v1", "cohort": cohort,
            "status": "all_historical_class_cover_histograms_match",
            "historical_class_rows": count,
            "fixture_sha256": hashlib.sha256(fixture_path.read_bytes()).hexdigest()}


def artifact_bytes(curves, plan_sha256, source_runs):
    alignment_hash = compare_certificate(INPUTS / "legacy-n3-alignment.json")
    grouped = {cohort: [] for cohort in COHORTS}
    for curve in curves:
        if curve.get("cohort") in grouped:
            grouped[curve["cohort"]].append(curve)
    checks = [compare_cohort(cohort, grouped[cohort]) for cohort in COHORTS]
    all_rows = b"".join(json.dumps(curve, sort_keys=True,
                                   separators=(",", ":")).encode() + b"\n"
                        for curve in curves)
    result = {"schema": "pext.legacy-t0-stage/v1", "experiment": "EXP-PEXT-bf8f96",
              "status": "all_three_class_cover_histograms_match; full_fixture_replay_separate",
              "plan_sha256": plan_sha256, "source_runs": source_runs,
              "n3_alignment_sha256": alignment_hash,
              "curve_rows_sha256": hashlib.sha256(all_rows).hexdigest(),
              "checks": checks}
    return json.dumps(result, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def write_artifact(run_dir, curves, plan_sha256, source_runs):
    path = Path(run_dir) / ARTIFACT
    partial = path.with_suffix(path.suffix + ".partial")
    if path.exists() or path.is_symlink() or partial.exists() or partial.is_symlink():
        raise FileExistsError("historical T=O comparison attempt already exists")
    data = artifact_bytes(curves, plan_sha256, source_runs)
    with partial.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(partial, path)
    return json.loads(data)


def compare_artifact(run_dir, curves, plan_sha256, source_runs):
    path = Path(run_dir) / ARTIFACT
    if path.is_symlink() or not path.is_file():
        raise ValueError("historical T=O comparison artifact missing or symlinked")
    expected = artifact_bytes(curves, plan_sha256, source_runs)
    if path.read_bytes() != expected:
        raise ValueError("historical T=O comparison differs from exact readback")
    return {"schema": "pext.legacy-t0-stage-check/v1", "valid": True,
            "artifact_sha256": hashlib.sha256(expected).hexdigest()}
