"""Verify a retained candidate artifact against an external curve/T binding.

The pure verifier can replay fixed software fixtures. A production caller must
obtain its expected binding from the checked cohort join plan and its binary
digest from the frozen run/build record. This module never launches a trial.
"""

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path

from candidate_binding import CandidateBinder
from independent_candidate_unit import IndependentCandidateChecker
from join_plan import CENSUS_COHORTS


CAP_NAMES = ("field_elements", "structures", "image_entries", "rational_candidates",
             "nonrational_maps", "total_candidates")
MAX_RAW_BYTES = 256 * 1024 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def checked_file(directory, name):
    path = directory / name
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"missing or symlinked artifact: {name}")
    return path.read_bytes()


def checked_json(data, name):
    try:
        value = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid {name} JSON") from error
    if not isinstance(value, dict):
        raise ValueError(f"invalid {name} object")
    return value


def read_bounded_gzip(compressed):
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
            raw = stream.read(MAX_RAW_BYTES + 1)
    except (EOFError, OSError) as error:
        raise ValueError("invalid compressed unit") from error
    if len(raw) > MAX_RAW_BYTES:
        raise ValueError("candidate unit exceeds checker raw-byte cap")
    return raw


def selected_ordinals(unit, full_geometry):
    rows = unit.get("rows")
    intervals = unit.get("generic_intervals")
    if not isinstance(rows, list) or not isinstance(intervals, list):
        raise ValueError("candidate rows or intervals missing")
    exceptional = ([row[0] for row in rows] if full_geometry else
                   [rows[i][0] for i in (0, len(rows)//2, len(rows)-1)] if rows else [])
    generic = ([intervals[i][0] for i in (0, len(intervals)//2, len(intervals)-1)]
               if intervals else [])
    return sorted(set(exceptional)), sorted(set(generic))


def verify_artifact(directory, checker, expected_form, expected_binary_sha256,
                    *, scope, expected_binding=None, full_geometry=False):
    """Check exact custody, independent set coverage and selected geometry."""
    directory = Path(directory)
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("missing or symlinked unit directory")
    if scope not in ("software-fixture", "approved-cohort"):
        raise ValueError("invalid verifier scope")
    if (scope == "approved-cohort") != (expected_binding is not None):
        raise ValueError("external production binding required")
    if (not isinstance(expected_binary_sha256, str)
            or len(expected_binary_sha256) != 64
            or any(character not in "0123456789abcdef" for character in expected_binary_sha256)):
        raise ValueError("external binary SHA-256 required")
    if any((directory / name).exists() for name in
           ("failure.json", "unit.json.partial", "validation-error.txt", "launch-error.txt")):
        raise ValueError("unit has failure or partial artifacts")
    input_bytes = checked_file(directory, "input.json")
    receipt_bytes = checked_file(directory, "receipt.json")
    compressed = checked_file(directory, "unit.json.gz")
    stderr = checked_file(directory, "stderr.log")
    input_record = checked_json(input_bytes, "input")
    receipt = checked_json(receipt_bytes, "receipt")
    if (input_record.get("schema") != "pext.candidate-unit-input/v1"
            or input_record.get("scope") != scope
            or input_record.get("binary_sha256") != expected_binary_sha256
            or input_record.get("field") != checker.field_record
            or input_record.get("form") != expected_form
            or input_record.get("structures") != checker.transversal.count
            or input_record.get("binding") != expected_binding):
        raise ValueError("input does not match external binding")
    caps = input_record.get("caps")
    if (not isinstance(caps, dict) or set(caps) != set(CAP_NAMES)
            or any(type(caps[key]) is not int or caps[key] < 1 for key in CAP_NAMES)
            or type(input_record.get("memory_bytes")) is not int
            or not 0 < input_record["memory_bytes"] <= 4*1024**3
            or type(input_record.get("cpu_seconds")) is not int
            or not 0 < input_record["cpu_seconds"] <= 24*3600
            or type(input_record.get("wall_seconds")) is not int
            or not 0 < input_record["wall_seconds"] <= 86400):
        raise ValueError("candidate resource limits invalid")
    argv = input_record.get("argv")
    wanted = [str(checker.field.p), str(checker.field.n),
              ",".join(map(str, expected_form)), *(str(caps[key]) for key in CAP_NAMES)]
    if (not isinstance(argv, list) or len(argv) != 10 or not isinstance(argv[0], str)
            or not argv[0] or argv[1:] != wanted):
        raise ValueError("candidate command differs from bound input")
    if (receipt.get("schema") != "pext.candidate-unit-artifact/v1"
            or receipt.get("status") != "candidate_emitted"
            or receipt.get("scope") != scope or receipt.get("returncode") != 0
            or receipt.get("input_sha256") != digest(input_bytes)
            or receipt.get("compressed_sha256") != digest(compressed)
            or receipt.get("stderr_sha256") != digest(stderr)):
        raise ValueError("candidate artifact receipt or digest mismatch")
    raw = read_bounded_gzip(compressed)
    if receipt.get("raw_sha256") != digest(raw):
        raise ValueError("candidate raw digest mismatch")
    unit = checked_json(raw, "unit")
    geometry, generic = selected_ordinals(unit, full_geometry)
    independent = checker.verify(unit, expected_form,
                                 geometry_ordinals=geometry, generic_ordinals=generic)
    return {"schema": "pext.independent-unit-review/v1", "valid": True,
            "scope": scope, "input_sha256": digest(input_bytes),
            "receipt_sha256": digest(receipt_bytes),
            "compressed_sha256": digest(compressed), "raw_sha256": digest(raw),
            "binary_sha256": expected_binary_sha256,
            "binding": expected_binding, "independent": independent,
            "geometry_ordinals": geometry, "generic_ordinals": generic}


def verify_bound_artifact(directory, binder, class_index, t_index, checker,
                          expected_binary_sha256, *, full_geometry=False):
    """Use a checked published cohort binder as the external production input."""
    if not isinstance(binder, CandidateBinder) or binder.plan_path is None:
        raise ValueError("checked published join plan required")
    binding = binder.bind(class_index, t_index)
    if checker.field_record != binding["field"]:
        raise ValueError("checker field differs from published cohort")
    return verify_artifact(directory, checker, binding["quotient_form"],
                           expected_binary_sha256, scope="approved-cohort",
                           expected_binding=binding, full_geometry=full_geometry)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cohort", required=True, choices=CENSUS_COHORTS)
    parser.add_argument("--class-index", required=True, type=int)
    parser.add_argument("--t-index", required=True, type=int)
    parser.add_argument("--join-plan", required=True, type=Path)
    parser.add_argument("--artifact", required=True, type=Path)
    parser.add_argument("--binary-sha256", required=True)
    parser.add_argument("--full-geometry", action="store_true")
    args = parser.parse_args()
    try:
        binder = CandidateBinder(args.cohort, plan_path=args.join_plan)
        checker = IndependentCandidateChecker(binder.plan["field"])
        result = verify_bound_artifact(args.artifact, binder,
                                       args.class_index, args.t_index, checker,
                                       args.binary_sha256,
                                       full_geometry=args.full_geometry)
        print(json.dumps(result, sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError, IndexError) as error:
        parser.exit(2, "INVALID: " + str(error) + "\n")
