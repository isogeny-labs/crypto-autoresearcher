"""Build or replay exact all-T join offsets from published class inputs.

This prepares a bounded execution index; it emits no structure or genus rows.
The independent Rust join engine must still replay production shards.
"""

import argparse
import json
from pathlib import Path

from check_compact_class_inputs import BasisField
from check_quotient_certificate import Curve, polynomial_value
from input_manifest import COHORTS, INPUTS, ROOT, checked_file, digest, verify as verify_manifest


ORDER = "log-point-coset-transversal/v1"
CENSUS_COHORTS = ("q3-n5", "q5-n3", "q7-n3", "q11-n3")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def canonical_targets(curve):
    doubles = {curve.add(point, point) for point in curve.points}
    uncovered = set(curve.points)
    targets = []
    while uncovered:
        target = min(uncovered, key=curve.key)
        members = {curve.add(target, double) for double in doubles}
        if not members <= uncovered:
            raise ValueError("target coset overlap")
        targets.append(target)
        uncovered -= members
    return [None if target is None else list(target) for target in targets]


def plan_for_models(field_record, models, cohort, input_sha256, manifest_sha256,
                    prime, degree, expected_classes):
    if len(models) != expected_classes or not models:
        raise ValueError("incomplete class input")
    field = BasisField(field_record)
    if (field.p, field.n) != (prime, degree):
        raise ValueError("cohort field mismatch")
    q = field.size
    numerator, denominator = q**3-q, prime**3-prime
    structures, remainder = divmod(numerator, denominator)
    if remainder or structures < 1:
        raise ValueError("nonintegral structure count")
    classes = []
    offset = 0
    for model in models:
        curve = Curve(field, model)
        targets = canonical_targets(curve)
        torsion_count = 1 + sum(polynomial_value(field, curve.cubic, x) == 0
                                for x in range(field.size))
        if torsion_count not in (1, 2, 4) or len(targets) != torsion_count:
            raise ValueError("target cosets do not match rational 2-torsion")
        classes.append({"model": model, "targets": targets, "offset": offset})
        offset += len(targets)*structures
        if offset >= 2**64:
            raise ValueError("join ordinal exceeds u64")
    return {
        "schema": "pext.join-plan/v1", "experiment": "EXP-PEXT-bf8f96",
        "cohort": cohort, "order": ORDER, "field": field_record,
        "input_sha256": input_sha256, "manifest_sha256": manifest_sha256,
        "structures_per_T": structures, "classes": classes,
        "total_rows": offset,
    }


def expected_plan(cohort, manifest_path):
    if cohort not in CENSUS_COHORTS:
        raise ValueError("all-T join requires a geometric census cohort")
    receipt = verify_manifest(manifest_path)
    manifest = json.loads(manifest_path.read_bytes())
    entry = next(row for row in manifest["cohorts"] if row["cohort"] == cohort)
    relative = f"{INPUTS}/{cohort}.json"
    if entry["input_path"] != relative:
        raise ValueError("manifest cohort path mismatch")
    source = checked_file(relative)
    if digest(source) != entry["input_sha256"]:
        raise ValueError("manifest cohort hash mismatch")
    record = json.loads(source)
    if record["cohort"] != cohort:
        raise ValueError("cohort identity mismatch")
    prime, degree, expected_classes, _ = COHORTS[cohort]
    return plan_for_models(record["field"], record["representatives"], cohort,
                           entry["input_sha256"], receipt["manifest_sha256"],
                           prime, degree, expected_classes)


def verify_plan(path, cohort, manifest_path):
    if path.is_symlink() or not path.is_file():
        raise ValueError("missing or symlinked join plan")
    actual = json.loads(path.read_bytes())
    expected = expected_plan(cohort, manifest_path)
    if actual != expected:
        raise ValueError("join plan, manifest or cohort source mismatch")
    return {"valid": True, "cohort": cohort, "classes": len(expected["classes"]),
            "T_classes": sum(len(row["targets"]) for row in expected["classes"]),
            "structures_per_T": expected["structures_per_T"],
            "total_rows": expected["total_rows"], "plan_sha256": digest(path.read_bytes())}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify"))
    parser.add_argument("--cohort", required=True, choices=CENSUS_COHORTS)
    parser.add_argument("--manifest", type=Path, default=ROOT / "experiments/EXP-PEXT-bf8f96/inputs/manifest.json")
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "build":
            if args.plan.exists():
                raise ValueError("refusing to overwrite existing join plan")
            args.plan.parent.mkdir(parents=True, exist_ok=True)
            args.plan.write_bytes(canonical(expected_plan(args.cohort, args.manifest)) + b"\n")
        print(json.dumps(verify_plan(args.plan, args.cohort, args.manifest), sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError, StopIteration) as error:
        parser.exit(2, "INVALID: " + str(error) + "\n")
