"""Bounded synthetic q3/n5 candidate and independent-checker software probe."""

import argparse
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import tempfile
import time

from independent_candidate_unit import IndependentCandidateChecker


HERE = Path(__file__).resolve().parent
FORM = [1, 1, 1, 0, 1]  # fixed synthetic quartic; no actual curve/T identity
ARGS = ["3", "5", "1,1,1,0,1", "243", "597861", "2391444",
        "5000000", "5000000", "597861"]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def run():
    with tempfile.TemporaryDirectory(prefix="pext-n5-profile-") as temporary:
        binary = Path(temporary) / "candidate_unit"
        source = HERE / "candidate_unit.rs"
        subprocess.run(["rustc", "--edition=2021", "-O", str(source), "-o", str(binary)],
                       check=True, capture_output=True)
        binary_sha256 = digest(binary.read_bytes())
        def limits():
            resource.setrlimit(resource.RLIMIT_AS, (4*1024**3, 4*1024**3))
            resource.setrlimit(resource.RLIMIT_CPU, (300, 300))
        t0 = time.monotonic()
        process = subprocess.run([binary, *ARGS], capture_output=True, timeout=300,
                                 preexec_fn=limits)
        t1 = time.monotonic()
        if process.returncode:
            raise ValueError(f"synthetic candidate exit {process.returncode}: "
                             + process.stderr.decode(errors="replace")[:300])
        unit = json.loads(process.stdout)
        checker = IndependentCandidateChecker(unit["field"])
        rows = unit["rows"]
        intervals = unit["generic_intervals"]
        result = checker.verify(unit, FORM,
                                geometry_ordinals=[rows[0][0], rows[-1][0]],
                                generic_ordinals=[intervals[0][0], intervals[-1][0]])
        t2 = time.monotonic()
        profile = {"schema": "pext.synthetic-n5-independent-profile/v1",
                   "scope": "fixed synthetic quartic in F_(3^5); no actual cohort/T binding",
                   "source_sha256": digest(source.read_bytes()),
                   "binary_sha256": binary_sha256,
                   "command": ["candidate_unit", *ARGS],
                   "limits": {"address_space_bytes": 4*1024**3,
                              "cpu_seconds": 300, "wall_seconds": 300},
                   "payload_sha256": digest(process.stdout),
                   "payload_bytes": len(process.stdout),
                   "stderr_sha256": digest(process.stderr),
                   "candidate_seconds": t1-t0, "checker_seconds": t2-t1,
                   "total_seconds": t2-t0,
                   "checker_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   "child_peak_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                   "checker": result}
        return process.stdout, profile


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit-out", required=True, type=Path)
    parser.add_argument("--profile-out", required=True, type=Path)
    args = parser.parse_args()
    if args.unit_out.exists() or args.profile_out.exists():
        parser.exit(2, "INVALID: refusing to overwrite synthetic software evidence\n")
    try:
        raw, profile = run()
        with args.unit_out.open("xb") as stream:
            stream.write(raw)
        with args.profile_out.open("x") as stream:
            json.dump(profile, stream, sort_keys=True, indent=2)
            stream.write("\n")
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(2, "INVALID: " + str(error) + "\n")
