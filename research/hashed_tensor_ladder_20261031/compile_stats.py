#!/usr/bin/env python3
"""Compile-only size statistics for the prime-field hashed-ECDL tensor encoding.

Builds the relation network of the Python reference
(cryptanalysis/experiments/hashed-ecdl-tensor-reference) for random prime-order
short-Weierstrass curves over F_p, for each requested field size ell (bits of p)
and slot count m, and records the encoder's own statistics: Boolean variables,
edges, maximum degree, multiplication blocks and the default contraction plan.
Nothing is contracted, counted or solved. The numbers are encoder-formula output;
--compile ELL:M additionally runs the real builder compile for that one cell as a
cross-check.

Requirements: Python >= 3.10, sympy, PARI/GP (`gp`, for ellcard point counting)
and a checkout of the reference directory (--ref).

    python3 compile_stats.py --ref /path/to/hashed-ecdl-tensor-reference \
        --ells 40,48,56,64,72,80 --slots 2,3,4,5,6,7 --jobs 4 --out compile-stats.json

Derived columns (all with every hidden constant of the counting bound set to 1):
    E          = N / sqrt(log2 N)           counting exponent for N Boolean variables
    rho        = ell / 2                     Pollard rho exponent
    E_over_rho = E / rho
    need       = (1/2 - 1/m) * ell           per-attempt exponent budget that would beat rho
    E_over_need                              None for m = 2 (budget is below one operation)
"""
import argparse
import json
import math
import multiprocessing as mp
import os
import random
import resource
import subprocess
import sys
import time
from collections import Counter

_REF = {}


def load_reference(ref):
    sys.path.insert(0, ref)
    from eccp import PrimeCurve, PrimeField, PrimeInstance, challenge
    from ecc2k import parameters
    from tensor_contraction import TensorContraction
    from tensor_prime import PrimeCurveEncoding
    from sympy import isprime, nextprime
    _REF.update(PrimeCurve=PrimeCurve, PrimeField=PrimeField, PrimeInstance=PrimeInstance,
                challenge=challenge, parameters=parameters, TensorContraction=TensorContraction,
                PrimeCurveEncoding=PrimeCurveEncoding, isprime=isprime, nextprime=nextprime)


def find_curve(ell, seed=1):
    """Random ell-bit prime p and a curve over F_p of prime order (cofactor 1), counted by PARI ellcard."""
    rng = random.Random(seed * 1000 + ell)
    p = int(_REF["nextprime"]((1 << (ell - 1)) + rng.randrange(1 << (ell - 2))))
    while True:
        a, b = rng.randrange(p), rng.randrange(p)
        if (4 * a ** 3 + 27 * b * b) % p == 0:
            continue
        out = subprocess.run(["gp", "-q"], input=f"print(ellcard(ellinit([{a},{b}],{p})))\n",
                             capture_output=True, text=True, timeout=600).stdout.strip()
        n = int(out)
        if _REF["isprime"](n) and n.bit_length() >= ell - 1:
            return p, a, b, n


def make_instance(ell, spec):
    if spec == "challenge":
        return _REF["challenge"]()
    p, a, b, n = spec
    curve = _REF["PrimeCurve"](_REF["PrimeField"](p), a, b)
    x = 2
    while not curve.decode(2 * x):
        x += 1
    pt = curve.decode(2 * x)
    return _REF["PrimeInstance"](f"synthetic-{ell}", curve, n, 1, pt, curve.mul(5, pt))


def stats_for(inst, m, compile_check=False):
    settings = _REF["parameters"](inst, m)
    prime = int(settings["hash_prime"])
    rng = random.Random(1)
    seeds = [{"prime": prime, "alpha": rng.randrange(1, prime), "beta": rng.randrange(prime),
              "threshold": settings["threshold"]} for _ in range(m)]
    t = time.monotonic()
    enc = _REF["PrimeCurveEncoding"](inst.curve)
    pts = enc.relation(inst.Q, seeds, inst.order, inst.cofactor)
    interface = tuple(v for pt in pts for w in pt.words for v in w)
    st = enc.circuit.statistics(interface)
    hist = Counter((x["type"], x["input_bits"], x["ring_bits"], x["transform_length"])
                   for x in st.pop("multiplication_encodings"))
    st["multiplication_blocks"] = [dict(type=a, input_bits=b, ring_bits=c, transform_length=d, count=n)
                                   for (a, b, c, d), n in hist.items()]
    st["n_multiplications"] = sum(hist.values())
    st["constraint_names"] = dict(Counter(n for _, _, n in enc.circuit.builder.constraints))
    st["encode_seconds"] = time.monotonic() - t
    st["plan"] = _REF["TensorContraction"]().plan(st["boolean_network_edges"], st["boolean_network_edges"] + 1)
    st["u0"] = st["plan"]["lambda"] // 131072
    st["hash_params"] = settings
    if compile_check:
        t = time.monotonic()
        net, _ = enc.circuit.builder.compile(interface)
        st["compile_seconds"] = time.monotonic() - t
        st["compiled_edges"], st["compiled_degree"] = net.edges, net.degree
    st["maxrss_MB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6
    return st


def derived(row):
    n, ell, m = row["variables"], row["ell"], row["m"]
    e = n / math.sqrt(math.log2(n))
    need = (0.5 - 1.0 / m) * ell
    row.update(log2_N=math.log2(n), N_per_bit_per_slot=n / (m * ell), E=e, rho=ell / 2,
               E_over_rho=e / (ell / 2), need=need, E_over_need=(e / need if need > 0 else None),
               b_over_m=ell / m)
    return row


def _job(task):
    ell, m, spec, compile_check = task
    inst = make_instance(ell, spec)
    st = stats_for(inst, m, compile_check)
    st.update(ell=ell, m=m, prime_bits=inst.curve.field.size.bit_length(),
              order_bits=inst.order.bit_length(), p=str(inst.curve.field.size))
    return derived(st)


def lsq(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx else 0.0
    return slope, my - slope * mx


def fits(rows):
    out = {"affine_in_m": {}, "power_law_N_per_m_vs_ell": {}}
    for ell in sorted({r["ell"] for r in rows}):
        pts = sorted((r["m"], r["variables"]) for r in rows if r["ell"] == ell)
        if len(pts) >= 2:
            s, f = lsq([a for a, _ in pts], [b for _, b in pts])
            out["affine_in_m"][str(ell)] = {"F": f, "S": s}
    for m in sorted({r["m"] for r in rows}):
        pts = sorted((r["ell"], r["variables"] / m) for r in rows if r["m"] == m)
        if len(pts) >= 3:
            a, c = lsq([math.log(x) for x, _ in pts], [math.log(y) for _, y in pts])
            out["power_law_N_per_m_vs_ell"][str(m)] = {"exponent": a, "constant": math.exp(c)}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", required=True, help="hashed-ecdl-tensor-reference directory")
    ap.add_argument("--ells", default="40,48,56,64,72,80")
    ap.add_argument("--slots", default="2,3,4")
    ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    ap.add_argument("--compile", action="append", default=[], metavar="ELL:M",
                    help="also run the real builder compile for this cell (repeatable)")
    ap.add_argument("--challenge", action="store_true", help="add the published ECCp-131 instance (ell = 131)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    load_reference(os.path.abspath(a.ref))
    ells = [int(x) for x in a.ells.split(",") if x]
    slots = [int(x) for x in a.slots.split(",") if x]
    specs = {ell: find_curve(ell) for ell in ells}
    if a.challenge:
        specs[131] = "challenge"
        ells.append(131)
    checks = {tuple(map(int, c.split(":"))) for c in a.compile}
    tasks = [(ell, m, specs[ell], (ell, m) in checks) for ell in ells for m in slots]
    t0 = time.monotonic()
    with mp.get_context("fork").Pool(a.jobs) as pool:
        rows = sorted(pool.map(_job, tasks, chunksize=1), key=lambda r: (r["ell"], r["m"]))
    doc = {"method": "compile-only encoder statistics; no contraction, counting or solving",
           "python": sys.version.split()[0], "wall_seconds": time.monotonic() - t0,
           "rows": rows, "fits": fits(rows)}
    with open(a.out, "w") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
    for r in rows:
        print(f"ell={r['ell']:3d} m={r['m']} N={r['variables']:>9,d} E/rho={r['E_over_rho']:8.0f} "
              f"edges={r['boolean_network_edges']:>10,d} u0={r['u0']}")


if __name__ == "__main__":
    main()
