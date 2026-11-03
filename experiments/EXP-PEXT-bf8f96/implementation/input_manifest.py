"""Bind the prescribed compact class inputs to exact published file bytes.

This is input custody only. It does not compute cover, genus, or descent rows.
The stored check files are prior software checks; this verifier does not rerun
their independent class-coverage calculation.
"""

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
INPUTS = "experiments/EXP-PEXT-bf8f96/inputs/classes-20261102"
COHORTS = {
    "q3-n5": (3, 5, 488, ["geometric-baseline"]),
    "q5-n3": (5, 3, 252, ["geometric-minimum", "H1-ratio"]),
    "q7-n3": (7, 3, 690, ["geometric-minimum", "H1-ratio"]),
    "q11-n3": (11, 3, 2662, ["geometric-minimum", "H1-ratio"]),
    "q13-n3-descriptive": (13, 3, 4400, ["H1-descriptive", "H1-ratio"]),
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def checked_file(relative):
    path = ROOT / relative
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"missing or symlinked file: {relative}")
    return path.read_bytes()


def entry(name):
    prime, degree, classes, roles = COHORTS[name]
    input_path = f"{INPUTS}/{name}.json"
    check_path = f"{INPUTS}/{name}-check.json"
    source = checked_file(input_path)
    check_bytes = checked_file(check_path)
    record, check = json.loads(source), json.loads(check_bytes)
    if record.get("schema") != "pext.compact-class-inputs/v1" or record.get("cohort") != name:
        raise ValueError(f"input identity: {name}")
    field = record.get("field", {})
    if (field.get("prime"), field.get("degree")) != (prime, degree):
        raise ValueError(f"field identity: {name}")
    if record.get("class_count") != classes or len(record.get("representatives", [])) != classes:
        raise ValueError(f"class cardinality: {name}")
    wanted = {
        "schema": "pext.compact-class-check/v1", "cohort": name,
        "valid": True, "classes": classes,
        "candidate_models": record.get("candidate_models"),
        "normalized_models": record.get("normalized_models"),
    }
    if check != wanted:
        raise ValueError(f"stored class check mismatch: {name}")
    return {
        "cohort": name, "roles": roles, "prime": prime, "degree": degree,
        "classes": classes, "field_sha256": digest(canonical(field)),
        "input_path": input_path, "input_sha256": digest(source),
        "check_path": check_path, "check_sha256": digest(check_bytes),
    }


def expected_manifest():
    legacy_path = f"{INPUTS}/legacy-q3-n5-bijection.json"
    legacy_check_path = f"{INPUTS}/legacy-q3-n5-bijection-check.json"
    legacy = checked_file(legacy_path)
    legacy_check = checked_file(legacy_check_path)
    parsed = json.loads(legacy_check)
    if (parsed.get("schema") != "pext.legacy-class-bijection-check/v1"
            or parsed.get("valid") is not True or parsed.get("matched_classes") != 488
            or parsed.get("input_sha256") != digest(checked_file(f"{INPUTS}/q3-n5.json"))):
        raise ValueError("stored q3-n5 legacy bijection check mismatch")
    return {
        "schema": "pext.input-manifest/v1",
        "experiment": "EXP-PEXT-bf8f96",
        "scope": "published compact K-isomorphism class inputs; no trial rows",
        "cohorts": [entry(name) for name in COHORTS],
        "legacy_q3_n5_bijection": {
            "input_path": legacy_path, "input_sha256": digest(legacy),
            "check_path": legacy_check_path, "check_sha256": digest(legacy_check),
        },
    }


def verify(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError("missing or symlinked manifest")
    actual = json.loads(path.read_bytes())
    expected = expected_manifest()
    if actual != expected:
        raise ValueError("manifest or source file mismatch")
    return {"valid": True, "schema": expected["schema"],
            "experiment": expected["experiment"], "cohorts": len(expected["cohorts"]),
            "classes": sum(row["classes"] for row in expected["cohorts"]),
            "manifest_sha256": digest(path.read_bytes())}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify"))
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "build":
            if args.manifest.exists():
                raise ValueError("refusing to overwrite existing manifest")
            args.manifest.parent.mkdir(parents=True, exist_ok=True)
            args.manifest.write_bytes(canonical(expected_manifest()) + b"\n")
        print(json.dumps(verify(args.manifest), sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(2, "INVALID: " + str(error) + "\n")
