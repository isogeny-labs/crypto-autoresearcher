"""Nonce-selected bounded pilot replay with an independent brute-force counter.

Curve generation uses the pinned vendored generator; base reconstruction,
point addition, and coincidence counting are local implementations here.
"""
import hashlib
import itertools
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
STUDY = ROOT / "experiments/EXP-PFDR-7c7c95"
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(STUDY / "implementation/vendor"))
import curve  # noqa: E402


def rng(*labels):
    label = "|".join(map(str, ("EXP-PFDR-ada71b",) + labels))
    return random.Random(int.from_bytes(hashlib.sha256(label.encode()).digest(), "big"))


def base_from_x_draws(p, a, bcoef, size, labels):
    """Rebuild the null base with an independent square-root path for p=3 mod 4."""
    assert p % 4 == 3
    stream = rng(*labels)
    seen, points = set(), []
    while len(points) < size:
        x = stream.randrange(p)
        if x in seen:
            continue
        seen.add(x)
        rhs = (x * x * x + a * x + bcoef) % p
        if rhs == 0 or pow(rhs, (p - 1) // 2, p) != 1:
            continue
        y = pow(rhs, (p + 1) // 4, p)
        assert (y * y - rhs) % p == 0
        points.extend(((x, y), (x, (-y) % p)))
    assert len(points) == size
    return points


def add_distinct_x(P, Q, p):
    x1, y1 = P
    x2, y2 = Q
    assert x1 != x2
    slope = ((y2 - y1) * pow(x2 - x1, -1, p)) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def count_coincidences(points, p):
    sums = Counter(add_distinct_x(P, Q, p)
                   for P, Q in itertools.combinations(points, 2) if P[0] != Q[0])
    pairs = sum(sums.values())
    coincidences = sum(m * (m - 1) // 2 for m in sums.values())
    return pairs, coincidences


def main():
    nonce_record = json.loads((HERE / "nonce.json").read_text())
    selection = json.loads((HERE / "selection.json").read_text())
    nonce = bytes.fromhex(nonce_record["nonce_hex"])
    source_rows = [json.loads(line) for line in
                   (STUDY / "runs/RUN-PFDR-1e5d2b/pilot-jobs.jsonl").read_text().splitlines()]
    eligible = [r for r in source_rows if r["bits"] in (16, 20)]
    def key(r):
        return f"b{r['bits']}-t{r['theta']:.2f}-d{r['d']}-c{r['c']}"
    ranked = sorted((hashlib.sha256(nonce + key(r).encode()).hexdigest(), r)
                    for r in eligible)
    expected = [(key(r), h) for h, r in ranked[:2]]
    observed = [(s["row_key"], s["selection_sha256"]) for s in selection["selected"]]
    assert observed == expected
    assert len(eligible) == selection["eligible_count"] == 384
    results = []
    for selected in selection["selected"]:
        key_str = selected["row_key"]
        bits, theta, d, c = re.fullmatch(r"b(\d+)-t(\d+\.\d+)-d(\d+)-c(\d+)", key_str).groups()
        bits, theta, d, c = int(bits), float(theta), int(d), int(c)
        r = next(r for r in eligible if key(r) == key_str)
        E, G = curve.generate_prime_order_curve(bits, seed=12000000 + c)
        generated = (E.p, E.a, E.b, E.order)
        reported = (r["p"], r["a"], r["b_coef"], r["N"])
        labels = ("null", "pilot", bits, theta, c, 0)
        base = base_from_x_draws(E.p, E.a, E.b, r["b"], labels)
        pairs, counted = count_coincidences(base, E.p)
        results.append({"row_key": key_str, "null_replicate": 0,
                        "curve_seed": 12000000 + c,
                        "generated_curve": {"p": E.p, "a": E.a, "b_coef": E.b, "N": E.order},
                        "reported_curve_equal_generated": generated == reported,
                        "base_size": len(base), "base_sha256": hashlib.sha256(
                            json.dumps(base, separators=(",", ":")).encode()).hexdigest(),
                        "pairs_counted": pairs, "pairs_reported": r["pairs"],
                        "coincidences_counted": counted, "coincidences_reported": r["null"][0],
                        "count_equal_reported": counted == r["null"][0],
                        "pairs_equal_reported": pairs == r["pairs"],
                        "shared_components": ["pinned vendored curve generator and its seeded curve stream",
                                              "Python SHA-256 and random.Random seed mapping"],
                        "independent_components": ["null x sampling and quadratic-residue lift",
                                                   "affine point addition", "unordered pair coincidence count"]})
    output = {"schema": "crypto.autoresearch.pfdr_replay/v1",
              "nonce_sha256": hashlib.sha256(nonce).hexdigest(),
              "eligible_bits": [16, 20], "eligible_rows": len(eligible),
              "selected_rows": len(results), "null_replicates_per_row": 1,
              "results": results,
              "all_equal_reported": all(x["reported_curve_equal_generated"] and
                                        x["count_equal_reported"] and x["pairs_equal_reported"]
                                        for x in results)}
    (HERE / "replay-results.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"all_equal_reported": output["all_equal_reported"],
                      "selected": [(r["row_key"], r["coincidences_counted"])
                                   for r in results]}, sort_keys=True))


if __name__ == "__main__":
    main()
