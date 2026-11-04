"""Read-only exact all-T unit/chunk inventory from published compact inputs."""

import hashlib
import json
from pathlib import Path
import time

from candidate_batch import MAX_CHUNK_BYTES, MAX_UNITS, expected_units
from input_manifest import ROOT, digest, verify as verify_manifest
from join_plan import CENSUS_COHORTS, canonical, expected_plan


MANIFEST = ROOT / "experiments/EXP-PEXT-bf8f96/inputs/manifest.json"


def inventory():
    manifest = verify_manifest(MANIFEST)
    rows = []
    for cohort in CENSUS_COHORTS:
        started = time.monotonic()
        plan = expected_plan(cohort, MANIFEST)
        units = expected_units(plan)
        chunks = len({unit["chunk"] for unit in units})
        rows.append({"cohort": cohort, "classes": len(plan["classes"]),
                     "T_blocks": len(units), "structures_per_T": plan["structures_per_T"],
                     "total_rows": plan["total_rows"],
                     "input_sha256": plan["input_sha256"],
                     "join_plan_sha256": digest(canonical(plan) + b"\n"),
                     "chunks": chunks,
                     "per_chunk_ceiling_bytes": MAX_CHUNK_BYTES,
                     "cohort_chunk_ceiling_bytes": chunks*MAX_CHUNK_BYTES,
                     "inventory_seconds": time.monotonic()-started})
    return {"schema": "pext.candidate-layout-inventory/v1",
            "scope": "published input preparation; no candidate or genus trial rows",
            "manifest_sha256": manifest["manifest_sha256"],
            "chunk_size_units": MAX_UNITS, "cohorts": rows,
            "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in (Path(__file__),
                                           Path(__file__).with_name("candidate_batch.py"),
                                           Path(__file__).with_name("join_plan.py"),
                                           Path(__file__).with_name("input_manifest.py"))}}


if __name__ == "__main__":
    print(json.dumps(inventory(), sort_keys=True))
