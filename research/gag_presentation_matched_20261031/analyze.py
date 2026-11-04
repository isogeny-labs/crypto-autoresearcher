"""Frozen analysis for the matched-presentation study (written before any data).

    python3 research/gag_presentation_matched_20261031/analyze.py \
        --protocol research/gag_presentation_matched_20261031/protocol.json \
        --rows <run>/rows.jsonl --out <run>/analysis.json

Exact checks first (claim C1); then, per prime and comparison, the paired
log2 ratio of F4 matrix cells (candidate / chain) per instance, its median,
a percentile bootstrap interval at the Bonferroni level, and an exact paired
sign-flip test of the mean log ratio.  Verdicts follow protocol.decision_rule.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys

BASE = "chain"
COMPARED = {"C-tree": "tree", "C-mono": "monolithic", "C-aa": "chain-aa"}
RESAMPLES = 20000
BOOT_SEED = 20261031


def log2_ratio(a: int, b: int) -> float:
    return math.log2(a / b)


def bootstrap_ci(xs: list[float], level: float, seed: int) -> tuple[float, float]:
    rng = random.Random(seed)
    n = len(xs)
    meds = sorted(statistics.median(rng.choice(xs) for _ in range(n)) for _ in range(RESAMPLES))
    lo = meds[int(math.floor((1 - level) / 2 * RESAMPLES))]
    hi = meds[min(RESAMPLES - 1, int(math.ceil((1 + level) / 2 * RESAMPLES)) - 1)]
    return lo, hi


def sign_flip_p(xs: list[float]) -> float:
    """Exact two-sided p of the mean under all 2^n sign flips (paired permutation)."""
    n = len(xs)
    observed = abs(sum(xs))
    hits = 0
    for mask in range(1 << n):
        s = sum(-x if mask >> i & 1 else x for i, x in enumerate(xs))
        if abs(s) >= observed - 1e-12:
            hits += 1
    return hits / (1 << n)


def load_design(protocol_path: str, proto: dict) -> dict:
    """links.design is '<path> sha256:<hex>'; the file must match its frozen hash."""
    import hashlib
    import os
    path, digest = proto["links"]["design"].rsplit(" sha256:", 1)
    local = os.path.join(os.path.dirname(os.path.abspath(protocol_path)), os.path.basename(path))
    data = open(local, "rb").read()
    if hashlib.sha256(data).hexdigest() != digest:
        raise SystemExit(f"design.json does not match its frozen sha256 {digest}")
    return json.loads(data)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol", required=True)
    ap.add_argument("--rows", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    proto = json.load(open(args.protocol))
    rows = [json.loads(line) for line in open(args.rows)]
    design = load_design(args.protocol, proto)
    family = len(COMPARED) - 1  # C-tree and C-mono are decisive; C-aa is the floor
    tests = family * len(design["primes"])
    alpha = design["alpha"]
    level = 1 - alpha / tests

    data = [r for r in rows if not r["warmup"]]
    by = {(r["instance"], r["arm"]): r for r in data}
    instances = sorted({r["instance"] for r in data})
    arms = sorted({r["arm"] for r in data})

    # -- C1: exact computation ---------------------------------------------------------
    exact = {"instances": len(instances), "violations": []}
    valid = set()
    for inst in instances:
        rs = [by.get((inst, a)) for a in arms]
        bad = []
        if any(r is None for r in rs):
            bad.append("missing arm row")
        else:
            if any(r["status"] != "ok" for r in rs):
                bad.append("status " + ",".join(f"{r['arm']}={r['status']}" for r in rs))
            if any(not r["planted_found"] for r in rs):
                bad.append("planted relation missing in " +
                           ",".join(r["arm"] for r in rs if not r["planted_found"]))
            rels = {json.dumps(r["relations"]) for r in rs}
            if len(rels) != 1:
                bad.append("relation sets differ across arms")
            degs = {r["ideal_degree"] for r in rs}
            if len(degs) != 1:
                bad.append(f"ideal degrees differ {sorted(degs)}")
        if bad:
            exact["violations"].append({"instance": inst, "problems": bad})
        else:
            valid.add(inst)
    exact["valid_instances"] = len(valid)
    exact["c1_holds"] = not exact["violations"]

    # -- comparisons ----------------------------------------------------------------------
    comps = {}
    for cid, arm in COMPARED.items():
        per_prime = {}
        for p in design["primes"]:
            xs = [log2_ratio(by[(i, arm)]["f4_cells"], by[(i, BASE)]["f4_cells"])
                  for i in instances if i in valid and by[(i, BASE)]["prime"] == p]
            if not xs:
                per_prime[str(p)] = None
                continue
            lo, hi = bootstrap_ci(xs, level, BOOT_SEED + p)
            per_prime[str(p)] = {
                "n": len(xs), "log2_ratios": xs,
                "median_log2_ratio": statistics.median(xs),
                "median_ratio": 2 ** statistics.median(xs),
                "ci_level": level, "ci_log2": [lo, hi],
                "sign_flip_p": sign_flip_p(xs),
                "max_abs_log2_ratio": max(abs(x) for x in xs),
            }
        comps[cid] = {"candidate": arm, "baseline": BASE, "per_prime": per_prime}

    # -- verdicts (protocol.decision_rule) ------------------------------------------------
    verdicts = {}
    aa = comps["C-aa"]["per_prime"]
    for cid in ("C-tree", "C-mono"):
        pp = comps[cid]["per_prime"]
        if not exact["c1_holds"] or any(pp[str(p)] is None or aa[str(p)] is None
                                        for p in design["primes"]):
            verdicts[cid] = "invalid_measurement"
            continue
        signs, beyond, within = set(), [], []
        for p in design["primes"]:
            c, floor = pp[str(p)], aa[str(p)]["max_abs_log2_ratio"]
            lo, hi = c["ci_log2"]
            excl = lo > 0 or hi < 0
            big = abs(c["median_log2_ratio"]) > floor
            beyond.append(excl and big and c["sign_flip_p"] <= alpha / tests)
            signs.add(1 if c["median_log2_ratio"] > 0 else -1)
            within.append(abs(c["median_log2_ratio"]) <= floor)
        if all(beyond) and len(signs) == 1:
            verdicts[cid] = "supported_within_scope"
        elif all(within):
            verdicts[cid] = "within_control_distribution"
        else:
            verdicts[cid] = "inconclusive"

    # -- secondary, descriptive only (wall time below the isolation level) -----------------
    secondary = {}
    for arm in arms:
        for p in design["primes"]:
            ts = [by[(i, arm)]["msolve_seconds"] for i in instances
                  if i in valid and by[(i, arm)]["prime"] == p]
            att = [by[(i, arm)]["attempt_count"] for i in instances if by.get((i, arm))
                   and by[(i, arm)]["prime"] == p]
            mx = [by[(i, arm)]["f4_max_deg"] for i in instances if i in valid
                  and by[(i, arm)]["prime"] == p]
            secondary[f"{arm}@{p}"] = {
                "median_msolve_seconds": statistics.median(ts) if ts else None,
                "attempts_total": sum(att), "f4_max_deg_median": statistics.median(mx) if mx else None,
                "wall_valid": False,
            }
    out = {"protocol_sha256": proto["freeze"]["protocol_sha256"], "exact": exact,
           "comparisons": comps, "verdicts": verdicts, "secondary_descriptive": secondary,
           "bootstrap": {"resamples": RESAMPLES, "seed_base": BOOT_SEED, "level": level}}
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps({"c1_holds": exact["c1_holds"], "verdicts": verdicts}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
