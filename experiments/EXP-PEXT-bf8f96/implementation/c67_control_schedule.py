"""Prospective C6/C7 strata from published source forms, before any run.

Availability means that a checked join-plan class/T source quotient has the
projective factor pattern. No candidate output, genus, rank or status enters
the selection. The first class/T in canonical plan order is fixed for C6.
"""

import hashlib
import json
from pathlib import Path

from candidate_binding import CandidateBinder
from candidate_stage import join_path
from c7_matched_random import PATTERNS, SEED, factor_pattern
from check_quotient_certificate import Field


COHORTS = ("q5-n3", "q7-n3", "q11-n3", "q3-n5")
SCHEMA = "pext.c67-prospective-control-schedule/v1"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def cohort_schedule(cohort):
    if cohort not in COHORTS:
        raise ValueError("C6/C7 cohort outside fixed design")
    binder = CandidateBinder(cohort, plan_path=join_path(cohort))
    field = Field(binder.plan["field"])
    counts = {pattern: 0 for pattern in PATTERNS}
    first = {}
    for class_index, row in enumerate(binder.plan["classes"]):
        for t_index in range(len(row["targets"])):
            binding = binder.bind(class_index, t_index)
            pattern = factor_pattern(field, binding["quotient_form"])
            counts[pattern] += 1
            if pattern not in first:
                first[pattern] = {"class_index": class_index,
                                  "T_index": t_index,
                                  "structure_ordinal": 0,
                                  "source_form_sha256": digest(binding["quotient_form"]),
                                  "binding_sha256": digest(binding)}
    if sum(counts.values()) != sum(len(row["targets"])
                                    for row in binder.plan["classes"]):
        raise ValueError("C6/C7 source class/T coverage incomplete")
    strata = []
    for pattern in PATTERNS:
        count = counts[pattern]
        if count:
            strata.append({"pattern": list(pattern),
                           "source_T_blocks": count,
                           "C6": {**first[pattern], "seed": SEED, "slots": 16},
                           "C7": [{"scalar_class": scalar_class,
                                   "seed": SEED, "samples": 16,
                                   "draw_cap": 4096,
                                   "coefficient_block_cap": 4096}
                                  for scalar_class in (0, 1)]})
    return {"cohort": cohort, "join_plan_sha256": binder.plan_sha256,
            "field_sha256": digest(binder.plan["field"]),
            "source_T_blocks": sum(counts.values()), "strata": strata}


def schedule():
    rows = [cohort_schedule(cohort) for cohort in COHORTS]
    return {"schema": SCHEMA,
            "status": "prospective_published_source_schedule; no_cohort_output",
            "experiment": "EXP-PEXT-bf8f96", "seed": SEED,
            "cohorts": rows,
            "C6_selected_units": sum(len(row["strata"]) for row in rows),
            "C6_coordinate_slots": 16 * sum(len(row["strata"]) for row in rows),
            "C7_strata": 2 * sum(len(row["strata"]) for row in rows),
            "C7_requested_forms": 32 * sum(len(row["strata"]) for row in rows)}


def write_once(path):
    path = Path(path)
    if path.exists() or path.is_symlink():
        raise FileExistsError("C6/C7 prospective schedule already exists")
    value = schedule()
    data = canonical(value) + b"\n"
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
    return hashlib.sha256(data).hexdigest()


def check(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("C6/C7 prospective schedule missing or symlinked")
    actual = path.read_bytes()
    expected = canonical(schedule()) + b"\n"
    if actual != expected:
        raise ValueError("C6/C7 schedule differs from published source plans")
    return hashlib.sha256(actual).hexdigest()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("write", "check"))
    parser.add_argument("path")
    args = parser.parse_args()
    print(write_once(args.path) if args.action == "write" else check(args.path))
