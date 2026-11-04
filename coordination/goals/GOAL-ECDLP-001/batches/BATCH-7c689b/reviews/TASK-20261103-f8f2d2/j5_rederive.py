#!/usr/bin/env python3
"""J5 blind re-derivation for RP-BATCH-7c689b (TASK-20261103-f8f2d2).

Written by the validator from the mathematical statement only:

    S3(u, v, w) = (u - v)^2 w^2 - 2((u + v)(u v + a) + 2b) w + (u v - a)^2 - 4b(u + v)
    S4(x1, x2, x3, x4) = Res_t( S3(x1, x2, t), S3(x3, x4, t) )          (exact)
    S4_drop(x1, x2, x4) = Res_t( S3(x1, x2, t), S3(t, x4, t) )          (sequential
        substitution x1->x3, x2->x4, x3->t applied to S3(x1,x2,x3): the x3 placed
        in the first slot is renamed to t by the last step, so x3 is dropped)

No code from experiments/EXP-SEMAEV-93d5cc/implementation/ or harness/semaev.py
is read, imported or executed. Polynomial arithmetic is a small sparse dict
engine over F_p written here; every resultant is cross-checked against
Singular's `resultant`, and every Groebner basis is computed by Singular
(the producer used sympy), reduced (option(redSB), option(redTail)), degrevlex
with x1 > x2 > x3, matching the FIB statement in
experiments/EXP-FIB-001/driver/decompcost.py (system only).

FIB parameters (curve, factor base, targets) are regenerated with
experiments/EXP-FIB-001/driver/instances.py, which imports harness.toycurve
only, and bound to frozen-instances.yaml by its sha256 fingerprint.

Usage: python3 j5_rederive.py <repo_root> <out_json>
"""
from __future__ import annotations

import itertools
import json
import os
import subprocess
import sys
import tempfile

SINGULAR = os.environ.get("SINGULAR_BIN", "/opt/conda-sage/envs/sage/bin/Singular")
VARS = ("x1", "x2", "x3", "x4")


# ---------------------------------------------------------------- sparse F_p polys
class P:
    """Sparse polynomial over F_p in x1..x4; keys are 4-tuples of exponents."""

    __slots__ = ("p", "d")

    def __init__(self, p, d=None):
        self.p = p
        self.d = {k: v % p for k, v in (d or {}).items() if v % p}

    @classmethod
    def const(cls, p, c):
        return cls(p, {(0, 0, 0, 0): c})

    @classmethod
    def var(cls, p, i):
        e = [0, 0, 0, 0]
        e[i] = 1
        return cls(p, {tuple(e): 1})

    def __add__(self, o):
        o = o if isinstance(o, P) else P.const(self.p, o)
        d = dict(self.d)
        for k, v in o.d.items():
            d[k] = (d.get(k, 0) + v) % self.p
        return P(self.p, d)

    __radd__ = __add__

    def __neg__(self):
        return P(self.p, {k: -v for k, v in self.d.items()})

    def __sub__(self, o):
        o = o if isinstance(o, P) else P.const(self.p, o)
        return self + (-o)

    def __rsub__(self, o):
        return (-self) + o

    def __mul__(self, o):
        if not isinstance(o, P):
            return P(self.p, {k: v * o for k, v in self.d.items()})
        d = {}
        p = self.p
        for k1, v1 in self.d.items():
            for k2, v2 in o.d.items():
                k = (k1[0] + k2[0], k1[1] + k2[1], k1[2] + k2[2], k1[3] + k2[3])
                d[k] = (d.get(k, 0) + v1 * v2) % p
        return P(p, d)

    __rmul__ = __mul__

    def nterms(self):
        return len(self.d)

    def total_degree(self):
        return max((sum(k) for k in self.d), default=-1)

    def free_vars(self):
        return sorted({VARS[i] for k in self.d for i in range(4) if k[i]})

    def eval(self, pt):
        s = 0
        for k, v in self.d.items():
            t = v
            for i in range(4):
                if k[i]:
                    t = t * pow(pt[i], k[i], self.p)
            s += t
        return s % self.p

    def subs_x4(self, val):
        d = {}
        for k, v in self.d.items():
            kk = (k[0], k[1], k[2], 0)
            d[kk] = (d.get(kk, 0) + v * pow(val, k[3], self.p)) % self.p
        return P(self.p, d)

    def singular(self):
        out = []
        for k, v in self.d.items():
            mon = "*".join(f"{VARS[i]}^{k[i]}" for i in range(4) if k[i])
            out.append(f"{v}*{mon}" if mon else f"{v}")
        return "+".join(out) if out else "0"


# ---------------------------------------------------------------- S3 / S4
def s3_coeffs(p, a, b, u, v):
    """Coefficients (A, B, C) of S3(u, v, t) = A t^2 + B t + C."""
    A = (u - v) * (u - v)
    B = -2 * ((u + v) * (u * v + a) + 2 * b)
    C = (u * v - a) * (u * v - a) - 4 * b * (u + v)
    return A, B, C


def s4_exact(p, a, b):
    X = [P.var(p, i) for i in range(4)]
    A1, B1, C1 = s3_coeffs(p, a, b, X[0], X[1])
    A2, B2, C2 = s3_coeffs(p, a, b, X[2], X[3])
    # Res_t(A1 t^2 + B1 t + C1, A2 t^2 + B2 t + C2) for two quadratics
    return (A1 * C2 - C1 * A2) * (A1 * C2 - C1 * A2) - (A1 * B2 - B1 * A2) * (B1 * C2 - C1 * B2)


def tpoly_mul(f, g, p):
    out = [P(p) for _ in range(len(f) + len(g) - 1)]
    for i, fi in enumerate(f):
        for j, gj in enumerate(g):
            out[i + j] = out[i + j] + fi * gj
    return out


def sylvester_resultant(f, g, p):
    """Res_t(f, g); f, g are coefficient lists (index = power of t) of P's."""
    m, n = len(f) - 1, len(g) - 1
    N = m + n
    zero = P(p)
    rows = []
    for i in range(n):
        row = [zero] * N
        for k in range(m + 1):
            row[i + k] = f[m - k]
        rows.append(row)
    for i in range(m):
        row = [zero] * N
        for k in range(n + 1):
            row[i + k] = g[n - k]
        rows.append(row)
    total = P(p)
    for perm in itertools.permutations(range(N)):
        term = None
        for r, c in enumerate(perm):
            e = rows[r][c]
            if not e.d:
                term = None
                break
            term = e if term is None else term * e
        if term is None:
            continue
        inv = sum(1 for i in range(N) for j in range(i + 1, N) if perm[i] > perm[j])
        total = total + (term if inv % 2 == 0 else -term)
    return total


def s4_drop(p, a, b):
    X = [P.var(p, i) for i in range(4)]
    A1, B1, C1 = s3_coeffs(p, a, b, X[0], X[1])
    f = [C1, B1, A1]  # S3(x1, x2, t)
    # S3(t, x4, t) expanded in t: (t - x4)^2 t^2 - 2((t + x4)(t x4 + a) + 2b) t + (t x4 - a)^2 - 4b(t + x4)
    x4 = X[3]
    one = P.const(p, 1)
    tm = [-x4, one]                       # t - x4
    sq = tpoly_mul(tm, tm, p)              # (t - x4)^2
    q1 = tpoly_mul(sq, [P(p), P(p), one], p)  # * t^2
    tp = [x4, one]                         # t + x4
    tx = [P.const(p, a), x4]               # t x4 + a
    q2 = tpoly_mul(tpoly_mul(tp, tx, p), [P(p), one], p)
    q2 = [c * (-2) for c in q2]
    q2b = [P(p), P.const(p, -4 * b)]       # -4b t   (from -2 * 2b * t)
    ta = [P.const(p, -a), x4]              # t x4 - a
    q3 = tpoly_mul(ta, ta, p)
    q4 = [x4 * (-4 * b), P.const(p, -4 * b)]  # -4b(t + x4)
    deg = max(len(q) for q in (q1, q2, q2b, q3, q4))
    g = [P(p) for _ in range(deg)]
    for q in (q1, q2, q2b, q3, q4):
        for i, c in enumerate(q):
            g[i] = g[i] + c
    while len(g) > 1 and not g[-1].d:
        g.pop()
    return sylvester_resultant(f, g, p)


# ---------------------------------------------------------------- Singular helpers
def run_singular(script: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".sing", delete=False) as fh:
        fh.write(script + "\nquit;\n")
        path = fh.name
    try:
        out = subprocess.run([SINGULAR, "-q", "--no-rc", path], capture_output=True, text=True, timeout=600)
    finally:
        os.unlink(path)
    if out.returncode != 0:
        raise RuntimeError(out.stderr)
    return out.stdout


def singular_s4_sizes(p, a, b):
    """Independent second derivation of both S4 term counts with Singular's resultant."""
    script = f"""
ring r = {p}, (x1,x2,x3,x4,t), dp;
poly a = {a}; poly b = {b};
proc S3(poly u, poly v, poly w) {{ return((u-v)^2*w^2 - 2*((u+v)*(u*v+a)+2*b)*w + (u*v-a)^2 - 4*b*(u+v)); }}
poly E = resultant(S3(x1,x2,t), S3(x3,x4,t), t);
poly D = resultant(S3(x1,x2,t), S3(t,x4,t), t);
print(string(size(E)) + " " + string(deg(E)) + " " + string(size(D)) + " " + string(deg(D)));
"""
    e, de, d, dd = run_singular(script).split()
    return int(e), int(de), int(d), int(dd)


def singular_gb(p, poly_str, V):
    fv = lambda x: "*".join(f"({x}-{v})" for v in V)
    script = f"""
option(redSB); option(redTail);
ring r = {p}, (x1,x2,x3), dp;
ideal I = {poly_str}, {fv('x1')}, {fv('x2')}, {fv('x3')};
ideal G = std(I);
int i; int md = 0;
for (i = 1; i <= size(G); i++) {{ if (deg(G[i]) > md) {{ md = deg(G[i]); }} }}
int triv = (size(G) == 1 && deg(G[1]) == 0);
print(string(size(G)) + " " + string(md) + " " + string(triv));
"""
    n, md, triv = run_singular(script).split()
    return int(n), int(md), bool(int(triv))


def to_xyz(poly: P) -> str:
    # after x4 substitution the polynomial lives in x1, x2, x3 only
    assert all(k[3] == 0 for k in poly.d)
    return poly.singular()


# ---------------------------------------------------------------- main
def main():
    root, out_path = sys.argv[1], sys.argv[2]
    res = {"fixture": {}, "icinv": [], "fib": {}}

    # Fixture (spec CTRL-ARM-FINGERPRINT statement): y^2 = x^3 + 2x + 3 over F_101, abscissae 1, 3, 5, 41.
    E = s4_exact(101, 2, 3)
    D = s4_drop(101, 2, 3)
    res["fixture"] = {
        "exact_free_vars": E.free_vars(), "exact_total_degree": E.total_degree(),
        "exact_residue": E.eval((1, 3, 5, 41)), "exact_nterms": E.nterms(),
        "drop_free_vars": D.free_vars(), "drop_total_degree": D.total_degree(), "drop_nterms": D.nterms(),
    }

    # ICINV: p and curves from the archived run's per-curve and control-set records.
    rd = os.path.join(root, "experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class")
    cls = json.load(open(os.path.join(rd, "per-curve-invariants.json")))
    ctl = json.load(open(os.path.join(rd, "control-set-invariants.json")))
    p = cls["p"]
    picks = [("class", i, cls["curves"][i]) for i in (0, 1, 2, 68, 137)] + \
            [("control", i, ctl["curves"][i]) for i in (0, 1, 137)]
    for setname, idx, c in picks:
        a, b = c["a"], c["b"]
        Ee, Dd = s4_exact(p, a, b), s4_drop(p, a, b)
        se, de, sd, dd = singular_s4_sizes(p, a, b)
        res["icinv"].append({
            "set": setname, "index": idx, "a": a, "b": b,
            "exact_nterms": Ee.nterms(), "exact_total_degree": Ee.total_degree(),
            "drop_nterms": Dd.nterms(), "drop_total_degree": Dd.total_degree(), "drop_free_vars": Dd.free_vars(),
            "singular_exact_nterms": se, "singular_exact_deg": de,
            "singular_drop_nterms": sd, "singular_drop_deg": dd,
            "archived_s4_support": c["m4"]["s4_support"],
        })

    # FIB C16-1: regenerate parameters with the archived instance builder (toycurve only) and bind to frozen sha256.
    sys.path.insert(0, os.path.join(root, "experiments/EXP-FIB-001"))
    sys.path.insert(0, root)
    from driver import instances  # noqa: E402

    import yaml  # noqa: E402
    frozen = yaml.safe_load(open(os.path.join(root, "experiments/EXP-FIB-001/frozen-instances.yaml")))
    spec = next(s for s in instances.MAIN_CURVES if s["id"] == "C16-1")
    ctx = instances.build_curve(spec)
    fp = instances.curve_fingerprint(ctx)
    assert "harness.semaev" not in sys.modules, "harness.semaev must not be imported"
    targets = instances.generate_targets(ctx, 200)
    pE, aE, bE = ctx.E.p, ctx.E.a, ctx.E.b
    S4e, S4d = s4_exact(pE, aE, bE), s4_drop(pE, aE, bE)
    rows = []
    for t in targets[:12]:
        xR = t["Rx"]
        ne, me, te = singular_gb(pE, to_xyz(S4e.subs_x4(xR)), ctx.V)
        nd, md, td = singular_gb(pE, to_xyz(S4d.subs_x4(xR)), ctx.V)
        rows.append({"target_index": t["index"], "Rx": xR,
                     "exact": {"basis_size": ne, "max_degree": me, "trivial": te},
                     "drop": {"basis_size": nd, "max_degree": md, "trivial": td}})
    res["fib"] = {"curve": "C16-1", "p": pE, "a": aE, "b": bE, "N": ctx.N, "B": ctx.B, "V": ctx.V,
                  "fingerprint_sha256": fp["sha256"], "frozen_sha256": frozen["main_curves"]["C16-1"]["sha256"],
                  "fingerprint_matches_frozen": fp["sha256"] == frozen["main_curves"]["C16-1"]["sha256"],
                  "harness_semaev_imported": "harness.semaev" in sys.modules,
                  "rows": rows}
    json.dump(res, open(out_path, "w"), indent=1, sort_keys=True)
    print(json.dumps(res["fixture"]))
    for r in res["icinv"]:
        print(r["set"], r["index"], r["a"], r["b"], "exact", r["exact_nterms"], r["singular_exact_nterms"],
              "drop", r["drop_nterms"], r["singular_drop_nterms"], "archived", r["archived_s4_support"])
    print("fib fingerprint match", res["fib"]["fingerprint_matches_frozen"], "V", ctx.V)
    for r in rows:
        print(r["target_index"], r["exact"], r["drop"])


if __name__ == "__main__":
    main()
