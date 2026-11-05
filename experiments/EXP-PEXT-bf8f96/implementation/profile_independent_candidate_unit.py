"""Replay retained synthetic q11 unit with a shared independent index.

Software resource profile only: the form comes from the synthetic payload,
not an approved actual curve/T binding.
"""

import gzip
import hashlib
import json
from pathlib import Path
import resource
import time

from independent_candidate_unit import IndependentCandidateChecker


PAYLOAD = Path(__file__).resolve().parent.parent / "reports/candidate-unit-20261103/q11-software-unit.json.gz"


def run():
    compressed = PAYLOAD.read_bytes()
    raw = gzip.decompress(compressed)
    unit = json.loads(raw)
    if (unit.get("field", {}).get("prime"), unit.get("field", {}).get("degree")) != (11, 3):
        raise ValueError("not the fixed synthetic q11 unit")
    t0 = time.monotonic()
    checker = IndependentCandidateChecker(unit["field"])
    t1 = time.monotonic()
    checker.index(1)
    t2 = time.monotonic()
    rows = unit["rows"]
    samples = sorted({rows[0][0], rows[len(rows)//2][0], rows[-1][0]})
    intervals = unit["generic_intervals"]
    generic = sorted({intervals[0][0], intervals[len(intervals)//2][0], intervals[-1][0]})
    report = checker.verify(unit, unit["form"], geometry_ordinals=samples,
                            generic_ordinals=generic)
    t3 = time.monotonic()
    return {"schema": "pext.synthetic-independent-profile/v1",
            "scope": "retained synthetic q11 software unit; no actual cohort/T binding",
            "payload_sha256": hashlib.sha256(compressed).hexdigest(),
            "raw_sha256": hashlib.sha256(raw).hexdigest(),
            "checker": report, "init_seconds": t1-t0,
            "index_seconds": t2-t1, "verify_seconds": t3-t2,
            "total_seconds": t3-t0,
            "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
