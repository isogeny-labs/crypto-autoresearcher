"""Read-only independent replay of every sealed full-cohort candidate unit."""

import hashlib
import json
import os
from pathlib import Path
import tempfile

from candidate_batch import (expected_units, read_chunk, verify_complete_index,
                             sync_directory)
from candidate_binding import CandidateBinder
from independent_candidate_unit import IndependentCandidateChecker
from independent_check import verify_artifact


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check_batch(run_dir, cohort, binder, binary_sha256, *, scope="approved-cohort",
                full_geometry=False):
    """Check exact index and each member, writing a complete review only on success."""
    run_dir = Path(run_dir)
    if (scope not in ("approved-cohort", "software-fixture")
            or binder.cohort != cohort
            or (scope == "approved-cohort"
                and (not isinstance(binder, CandidateBinder) or binder.plan_path is None))):
        raise ValueError("checked production cohort binder required")
    index = verify_complete_index(run_dir, cohort, binder.plan,
                                  binder.plan_sha256, binary_sha256)
    units = expected_units(binder.plan)
    checker = IndependentCandidateChecker(binder.plan["field"])
    output = run_dir / "candidate-reviews.jsonl"
    partial = run_dir / "candidate-reviews.partial"
    summary_path = run_dir / "candidate-check.json"
    if any(path.exists() for path in (output, partial, summary_path)):
        raise FileExistsError("candidate review attempt already exists")
    total_exceptional = total_generic = 0
    review_hash = hashlib.sha256()
    with partial.open("xb") as stream:
        for chunk_name in dict.fromkeys(row["chunk"] for row in units):
            restored, _ = read_chunk(run_dir / "chunks" / chunk_name)
            for name, files in restored:
                ordinal = int(name[1:])
                row = units[ordinal]
                if row["name"] != name or row["chunk"] != chunk_name:
                    raise ValueError("review unit differs from fixed slot")
                binding = binder.bind(row["class_index"], row["T_index"])
                if binding["join_plan_sha256"] != binder.plan_sha256:
                    raise ValueError("review binding plan hash mismatch")
                with tempfile.TemporaryDirectory(prefix="pext-review-") as temporary:
                    directory = Path(temporary)
                    for filename, data in files.items():
                        (directory / filename).write_bytes(data)
                    review = verify_artifact(
                        directory, checker, binding["quotient_form"],
                        binary_sha256, scope=scope,
                        expected_binding=binding if scope == "approved-cohort" else None,
                        full_geometry=full_geometry)
                independent = review["independent"]
                total_exceptional += independent["exceptional"]
                total_generic += independent["structures"] - independent["exceptional"]
                compact = {"name": name, "class_index": row["class_index"],
                           "T_index": row["T_index"], "chunk": chunk_name,
                           "input_sha256": review["input_sha256"],
                           "receipt_sha256": review["receipt_sha256"],
                           "compressed_sha256": review["compressed_sha256"],
                           "raw_sha256": review["raw_sha256"],
                           "independent": independent,
                           "geometry_ordinals": review["geometry_ordinals"],
                           "generic_ordinals": review["generic_ordinals"]}
                line = json.dumps(compact, sort_keys=True, separators=(",", ":")).encode() + b"\n"
                stream.write(line)
                review_hash.update(line)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(partial, output)
    summary = {"schema": "pext.candidate-batch-check/v1", "valid": True,
               "scope": scope, "cohort": cohort,
               "join_plan_sha256": binder.plan_sha256,
               "binary_sha256": binary_sha256,
               "index_sha256": index["index_sha256"],
               "unit_count": index["unit_count"],
               "chunk_count": index["chunk_count"],
               "exceptional": total_exceptional, "generic": total_generic,
               "candidate_reviews_sha256": review_hash.hexdigest(),
               "geometry_mode": "all-exceptional" if full_geometry else "selected"}
    with summary_path.open("x") as stream:
        json.dump(summary, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    sync_directory(run_dir)
    return summary
