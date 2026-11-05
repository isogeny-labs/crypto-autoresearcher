"""Enumerate abstract branch placements and cross-check their F2[x] ranks.

This is a design component for the unapproved orbits stage. It takes no
curve-census data and does not establish realizability of a placement.
"""

import hashlib
import importlib.util
import itertools
import json
import math
import os
from pathlib import Path
import resource
import signal
import sys

from input_manifest import ROOT


TYPES = {"split": (1, 1, 1, 1), "Z2": (1, 1, 2), "odd": (1, 3)}
SOURCE = "experiments/EXP-PEXT-bf8f96/implementation/orbit_spectrum_stage.py"
DONOR = "experiments/EXP-PEXT-212d5c/implementation/spectrum.py"
INPUT_MANIFEST_SOURCE = "experiments/EXP-PEXT-bf8f96/implementation/input_manifest.py"
STAGES = ("regression", "orbits", "n3core", "n3ext", "n5", "analyze")
OUTPUT = "orbit-spectrum.json"
CHECK = "orbit-spectrum-check.json"
WATCHDOG = 3600
MAX_MEMORY_MB = 4096


def remainder(a, b):
    if b == 0:
        raise ZeroDivisionError
    while a and a.bit_length() >= b.bit_length():
        a ^= b << (a.bit_length() - b.bit_length())
    return a


def gcd(a, b):
    while b:
        a, b = b, remainder(a, b)
    return a


def polynomial_rank(n, vectors):
    """Ideal dimension in F2[x]/(x^n-1)."""
    common = (1 << n) | 1
    for vector in vectors:
        common = gcd(common, vector)
    return n - (common.bit_length() - 1)


def shift_rank(n, vectors):
    """Independent binary elimination on all cyclic shifts."""
    mask = (1 << n) - 1
    pivots = {}
    for vector in vectors:
        for offset in range(n):
            row = ((vector << offset) | (vector >> (n - offset))) & mask
            while row:
                bit = row.bit_length() - 1
                if bit not in pivots:
                    pivots[bit] = row
                    break
                row ^= pivots[bit]
    return len(pivots)


def placements(n, degrees):
    """Canonical labeled set partitions; each free orbit has distinct slots."""
    count = len(degrees)
    for labels in itertools.product(range(-1, count), repeat=count):
        seen = []
        valid = True
        for index, label in enumerate(labels):
            if label < 0:
                if math.gcd(degrees[index], n) != 1:
                    valid = False
                    break
            elif label not in seen:
                if label != len(seen):
                    valid = False
                    break
                seen.append(label)
        if not valid:
            continue
        members = {label: [i for i, value in enumerate(labels) if value == label]
                   for label in seen}
        if any(len({degrees[i] for i in indices}) != 1
               for indices in members.values()):
            continue
        for slots in itertools.product(range(n), repeat=sum(map(len, members.values()))):
            offset = 0
            positions = {}
            for label, indices in members.items():
                positions[label] = slots[offset:offset + len(indices)]
                offset += len(indices)
            if any(len(set(values)) != len(values)
                   for values in positions.values()):
                continue
            vectors = [((1 << n) - 1) for label in labels if label < 0]
            branch_count = sum(degrees[i] for i, label in enumerate(labels)
                               if label < 0)
            for label, values in positions.items():
                vectors.append(sum(1 << value for value in values))
                branch_count += n * degrees[members[label][0]]
            yield labels, positions, vectors, branch_count


def enumerate_spectrum(degrees=(3, 5, 7)):
    """Check every placement, retain exact counts and one canonical witness."""
    result = {"schema": "pext.orbit-spectrum/v1",
              "status": "abstract_placements_checked; realization_unasserted",
              "degrees": list(degrees), "cases": []}
    for n in degrees:
        if n not in (3, 5, 7):
            raise ValueError("only frozen n=3,5,7 allowed")
        for name, branch_degrees in TYPES.items():
            rows = {}
            total = 0
            digest = hashlib.sha256()
            for labels, positions, vectors, r in placements(n, branch_degrees):
                m = polynomial_rank(n, vectors)
                if shift_rank(n, vectors) != m:
                    raise ValueError("polynomial and binary rank disagree")
                witness = {"labels": labels, "positions": positions,
                           "vectors": vectors, "m": m, "r": r}
                encoded = json.dumps(witness, sort_keys=True,
                                     separators=(",", ":")).encode() + b"\n"
                digest.update(encoded)
                key = (m, r)
                if key not in rows:
                    rows[key] = {"m": m, "r": r, "count": 0,
                                 "first_witness": witness}
                rows[key]["count"] += 1
                total += 1
            result["cases"].append({"n": n, "type": name,
                                    "placement_count": total,
                                    "placement_stream_sha256": digest.hexdigest(),
                                    "m_r": [rows[key] for key in sorted(rows)]})
    return result


def write_once(path, value):
    path = Path(path)
    partial = path.with_suffix(path.suffix + ".partial")
    if path.exists() or path.is_symlink() or partial.exists() or partial.is_symlink():
        raise FileExistsError("orbit spectrum attempt already exists")
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    with partial.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(partial, path)
    return hashlib.sha256(data).hexdigest()


def compare_exact(path, degrees=(3, 5, 7)):
    """Recompute all placements and compare canonical bytes with saved output."""
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("orbit output missing or symlinked")
    expected = (json.dumps(enumerate_spectrum(degrees), sort_keys=True,
                           separators=(",", ":")).encode() + b"\n")
    if path.read_bytes() != expected:
        raise ValueError("orbit output differs from exact recomputation")
    return hashlib.sha256(expected).hexdigest()


def compare_donor(spectrum):
    """Check all nine abstract m/r sets against the pinned earlier algorithm."""
    path = ROOT / DONOR
    spec = importlib.util.spec_from_file_location("pext_prior_spectrum", path)
    if spec is None or spec.loader is None:
        raise ValueError("pinned abstract-spectrum derivation aid unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cases = spectrum.get("cases") if isinstance(spectrum, dict) else None
    if (not isinstance(spectrum, dict)
            or spectrum.get("degrees") != [3, 5, 7] or not isinstance(cases, list)
            or len(cases) != 9):
        raise ValueError("full frozen abstract spectrum missing")
    for n in (3, 5, 7):
        prior = module.spectrum(n)["types"]
        for name in TYPES:
            case = next((row for row in cases
                         if row.get("n") == n and row.get("type") == name), None)
            if case is None or [[row["m"], row["r"]] for row in case["m_r"]] != prior[name]["m_r"]:
                raise ValueError(f"abstract spectrum differs from pinned derivation aid: n={n} type={name}")
    return {"donor_source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "cases_matched": 9}


def _preflight(trial_plan, run_dir):
    sys.path.insert(0, str(ROOT / "tools"))
    from experiment_execution import (authorize, load_plan, read_json, run_root,
                                      sha256, trial_state)
    trial_plan, run_dir = Path(trial_plan), Path(run_dir)
    if run_dir.is_symlink() or not run_dir.is_dir():
        raise ValueError("orbit run directory missing or symlinked")
    plan = load_plan(ROOT, trial_plan)
    trials = plan.get("trials", [])
    if (plan.get("experiment_id") != "EXP-PEXT-bf8f96"
            or tuple(row.get("id") for row in trials) != STAGES):
        raise ValueError("orbit stage differs from frozen six-stage contract")
    trial = trials[1]
    if (trial.get("stage") != "orbits"
            or trial.get("watchdog_seconds") != WATCHDOG
            or trial.get("depends_on") != ["regression"]
            or type(trial.get("memory_mb")) is not int
            or not 1 <= trial["memory_mb"] <= MAX_MEMORY_MB
            or not {OUTPUT, CHECK} <= set(trial.get("artifacts", []))
            or not {SOURCE, DONOR, INPUT_MANIFEST_SOURCE} <= set(plan.get("source_sha256", {}))
            or run_root(ROOT, plan, trial) != run_dir.resolve()):
        raise ValueError("orbit component absent from frozen trial")
    for relative in (SOURCE, DONOR, INPUT_MANIFEST_SOURCE):
        path = ROOT / relative
        if path.is_symlink() or not path.is_file() or sha256(path) != plan["source_sha256"][relative]:
            raise ValueError(f"orbit source hash mismatch: {relative}")
    plan_hash = sha256(trial_plan)
    if trial_state(ROOT, plan, trials[0], plan_hash) != "output_validated":
        raise ValueError("historical regression has no validated supervisor output")
    launch = read_json(run_dir / "launch.json")
    if (launch.get("trial_id") != "orbits"
            or launch.get("run_id") != trial["run_id"]
            or launch.get("plan_sha256") != plan_hash):
        raise ValueError("orbit supervisor launch mismatch")
    authority = launch.get("authority")
    if not isinstance(authority, dict) or authorize(
            ROOT, trial_plan, plan, authority.get("owner"), authority.get("epoch")) != authority:
        raise ValueError("orbit component lacks current supervisor authority")
    return trial, launch


def _remaining(launch):
    from datetime import datetime, timezone
    started = datetime.fromisoformat(launch["started_at"].replace("Z", "+00:00"))
    if started.tzinfo is None:
        raise ValueError("orbit supervisor launch has no timezone")
    remaining = WATCHDOG - (datetime.now(timezone.utc) - started).total_seconds()
    if remaining < 1:
        raise TimeoutError("orbit stage watchdog reached")
    return remaining


def _timeout(signum, frame):
    raise TimeoutError("orbit stage watchdog reached")


def _limit_process(trial, launch):
    memory = trial["memory_mb"] * 1024 * 1024
    current_soft, current_hard = resource.getrlimit(resource.RLIMIT_AS)
    if current_soft != resource.RLIM_INFINITY:
        memory = min(memory, current_soft)
    resource.setrlimit(resource.RLIMIT_AS, (memory, current_hard))
    signal.signal(signal.SIGALRM, _timeout)
    signal.setitimer(signal.ITIMER_REAL, _remaining(launch))


def run_stage(trial_plan, run_dir):
    trial, launch = _preflight(trial_plan, run_dir)
    _limit_process(trial, launch)
    try:
        spectrum = enumerate_spectrum()
        donor = compare_donor(spectrum)
        output_hash = write_once(Path(run_dir) / OUTPUT, spectrum)
        return {"schema": "pext.orbit-stage/v1", "run_id": trial["run_id"],
                "plan_sha256": launch["plan_sha256"],
                "output_sha256": output_hash, **donor,
                "placement_count": sum(row["placement_count"] for row in spectrum["cases"])}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def check_stage(trial_plan, run_dir):
    trial, launch = _preflight(trial_plan, run_dir)
    _limit_process(trial, launch)
    try:
        path = Path(run_dir) / OUTPUT
        output_hash = compare_exact(path)
        donor = compare_donor(json.loads(path.read_bytes()))
        result = {"schema": "pext.orbit-stage-check/v1", "valid": True,
                  "run_id": trial["run_id"], "plan_sha256": launch["plan_sha256"],
                  "output_sha256": output_hash, **donor}
        write_once(Path(run_dir) / CHECK, result)
        return result
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("run", "check"), required=True)
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    result = (run_stage if args.mode == "run" else check_stage)(
        args.trial_plan, args.run_dir)
    print(json.dumps(result, sort_keys=True))
