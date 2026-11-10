#!/usr/bin/env python3
"""Kernel spot-check (sheriff SHF-20261106-a114e7, reader pfdr): recount gap_C, gap_D, gap_meta, null_C and
null_D of sampled census jobs WITHOUT labelsum.c and without the producer's builders.

Producer semantics used (binding, declared): the seeded stream random.Random(sha256("EXP-PFDR-bb0d26|" +
"|".join(labels))) with labels ("gap"|"null", block, cell, c[, k]); the vendored curve generator and
Curve.random_point for the r base points (drawn first from the gap stream); null labels drawn by
rng.randrange(p). Own code: group law, multiples, half-box enumeration, label-universe test, counting.

usage: python3 -B kernel_spotcheck.py <vendor_dir> <jobs.jsonl> <out.json> <k> [nonce_hex]
"""
import hashlib, json, random, secrets, sys
import numpy as np

vendor, jobs_p, out_p, k = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
nonce = sys.argv[5] if len(sys.argv) > 5 else secrets.token_hex(8)
assert hashlib.sha256(open(vendor + "/curve.py", "rb").read()).hexdigest().startswith("fcca2beb699b4785")
sys.path.insert(0, vendor)
import curve as V  # vendored generator and random_point only

EXP = "EXP-PFDR-bb0d26"
SEED = {"main": 8100000}


def stream(*labels):
    d = hashlib.sha256("|".join(map(str, (EXP,) + labels)).encode()).digest()
    return random.Random(int.from_bytes(d, "big"))


def add(p, a, P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def counts(X, p):
    X = np.array(X, dtype=np.int64)
    iu = np.triu_indices(len(X), k=1)
    sums = (X[:, None] + X[None, :])[iu] % p
    _, m = np.unique(sums, return_counts=True)  # no p-sized table (p is up to 2^28)
    m = m.astype(np.int64)
    return int((m * (m - 1) // 2).sum()), int(len(m))


def own_gap(E, r, n, rng):
    p, a = E.p, E.a
    pts = [E.random_point(rng) for _ in range(r)]
    need = -(-102 * n // 100) + 8
    T = 1
    while ((2 * T + 1) ** r - 1) // 2 < need:
        T += 1
    tabs = []
    for P in pts:
        t = {0: None, 1: (P[0], P[1])}
        for j in range(2, T + 1):
            t[j] = add(p, a, t[j - 1], t[1])
        for j in range(1, T + 1):
            t[-j] = None if t[j] is None else (t[j][0], (-t[j][1]) % p)
        tabs.append(t)
    # own enumerator: odometer over [-T, T]^r in lexicographic order, keep first-nonzero-positive
    seen, labels, enum, dup, inf, first, last = set(), [], 0, 0, 0, None, None
    v = [-T] * r
    while True:
        nz = next((e for e in v if e != 0), 0)
        if nz > 0:
            enum += 1
            Q = None
            for t, ci in zip(tabs, v):
                Q = add(p, a, Q, t[ci])
            if Q is None:
                inf += 1
            elif Q[0] in seen:
                dup += 1
            else:
                seen.add(Q[0])
                labels.append(Q[0])
                first = first or list(v)
                last = list(v)
                if len(labels) == n:
                    break
        i = r - 1
        while i >= 0 and v[i] == T:
            v[i] = -T
            i -= 1
        if i < 0:
            break
        v[i] += 1
    meta = {"T": T, "enumerated": enum, "duplicate_skips": dup, "infinity_skips": inf, "first": first, "last": last}
    return (labels if len(labels) == n else None), meta


def is_label(p, a, b, x):
    f = (x * x * x + a * x + b) % p
    return f != 0 and pow(f, (p - 1) // 2, p) == 1


def own_null(p, a, b, n, rng):
    out, seen = [], set()
    while len(out) < n:
        x = rng.randrange(p)
        if x in seen or not is_label(p, a, b, x):
            continue
        seen.add(x)
        out.append(x)
    return out


jobs = [json.loads(l) for l in open(jobs_p)]
pool = [j for j in jobs if j["status"] == "ok" and j["n"] <= 1024]
order = sorted(range(len(pool)), key=lambda i: hashlib.sha256(f"{nonce}|{pool[i]['cell']}|{pool[i]['c']}".encode()).digest())
chosen = [pool[i] for i in order[:k]] + [j for j in jobs if j["status"] == "degenerate"]
res = {"nonce": nonce, "k_ok": k, "rows": []}
for j in chosen:
    E, _ = V.generate_prime_order_curve(j["bits"], SEED[j["block"]] + j["c"])
    assert (E.p, E.a, E.b) == (j["p"], j["a"], j["b_coef"])
    labels, meta = own_gap(E, j["r"], j["n"], stream("gap", j["block"], j["cell"], j["c"]))
    row = {"cell": j["cell"], "c": j["c"], "status": j["status"],
           "gap_meta_equal": meta == j["gap_meta"], "own_meta": meta}
    if labels is not None:
        gC, gD = counts(labels, E.p)
        row["gap_C_equal"] = gC == j["gap_C"]
        row["gap_D_equal"] = gD == j["gap_D"]
        nc = [counts(own_null(E.p, E.a, E.b, j["n"], stream("null", j["block"], j["cell"], j["c"], q)), E.p)
              for q in range(20)]
        row["null_C_equal"] = [x[0] for x in nc] == j["null_C"]
        row["null_D_equal"] = [x[1] for x in nc] == j["null_D"]
    else:
        row["degenerate_reproduced"] = j["status"] == "degenerate"
    res["rows"].append(row)
    print(json.dumps({x: y for x, y in row.items() if x != "own_meta"}), flush=True)
fields = [(r, f) for r in res["rows"] for f in ("gap_meta_equal", "gap_C_equal", "gap_D_equal", "null_C_equal",
                                                 "null_D_equal", "degenerate_reproduced") if f in r]
res["summary"] = {"jobs": len(res["rows"]), "checks": len(fields), "failures": sum(1 for r, f in fields if not r[f])}
json.dump(res, open(out_p, "w"), indent=1)
print(res["summary"])
