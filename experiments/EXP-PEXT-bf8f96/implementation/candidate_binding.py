"""Read-only binding of a published cohort and T to one candidate-unit input.

This module prepares execution input; it never launches a candidate or writes a
scientific row. The full join plan is recomputed from checked published inputs.
"""

import argparse
import json
from pathlib import Path

from check_compact_class_inputs import BasisField
from check_quotient_certificate import Curve
from input_manifest import INPUTS, ROOT, checked_file, digest
from join_plan import CENSUS_COHORTS, canonical, canonical_targets, expected_plan, verify_plan


DEFAULT_MANIFEST = ROOT / "experiments/EXP-PEXT-bf8f96/inputs/manifest.json"


def bind(cohort, class_index, t_index, manifest_path=DEFAULT_MANIFEST, plan_path=None):
    if cohort not in CENSUS_COHORTS:
        raise ValueError("not a geometric census cohort")
    if type(class_index) is not int or type(t_index) is not int:
        raise ValueError("class and T indices must be integers")
    plan = expected_plan(cohort, Path(manifest_path))
    plan_bytes = canonical(plan) + b"\n"
    plan_sha256 = digest(plan_bytes)
    if plan_path is not None:
        verified = verify_plan(Path(plan_path), cohort, Path(manifest_path))
        if verified["plan_sha256"] != plan_sha256 or Path(plan_path).read_bytes() != plan_bytes:
            raise ValueError("join plan bytes mismatch")
    classes = plan["classes"]
    if class_index < 0 or class_index >= len(classes):
        raise ValueError("class index outside published cohort")
    selected = classes[class_index]
    if t_index < 0 or t_index >= len(selected["targets"]):
        raise ValueError("T index outside canonical cosets")
    source = json.loads(checked_file(f"{INPUTS}/{cohort}.json"))
    if selected["model"] != source["representatives"][class_index]:
        raise ValueError("class model mismatch")
    field = BasisField(plan["field"])
    curve = Curve(field, selected["model"])
    if canonical_targets(curve) != selected["targets"]:
        raise ValueError("canonical T list mismatch")
    target = selected["targets"][t_index]
    form = curve.quotient_form(curve.read_point(target))
    structures = plan["structures_per_T"]
    offset = selected["offset"] + t_index * structures
    if offset + structures > plan["total_rows"]:
        raise ValueError("T block outside join plan")
    return {
        "schema": "pext.candidate-binding/v1",
        "experiment": "EXP-PEXT-bf8f96",
        "cohort": cohort,
        "class_index": class_index,
        "T_index": t_index,
        "model": selected["model"],
        "target": target,
        "quotient_form": form,
        "field": plan["field"],
        "input_sha256": plan["input_sha256"],
        "manifest_sha256": plan["manifest_sha256"],
        "join_plan_sha256": plan_sha256,
        "structure_offset": offset,
        "structures_per_T": structures,
        "structure_end_exclusive": offset + structures,
        "candidate_unit_args": [str(field.p), str(field.n), ",".join(map(str, form))],
        "status": "preview_only",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cohort", required=True, choices=CENSUS_COHORTS)
    parser.add_argument("--class-index", required=True, type=int)
    parser.add_argument("--t-index", required=True, type=int)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--plan", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(bind(args.cohort, args.class_index, args.t_index,
                              args.manifest, args.plan), sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError, IndexError) as error:
        parser.exit(2, "INVALID: " + str(error) + "\n")
