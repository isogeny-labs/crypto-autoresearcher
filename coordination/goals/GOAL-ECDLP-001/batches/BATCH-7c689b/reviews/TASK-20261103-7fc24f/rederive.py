#!/usr/bin/env python3
"""Blind re-derivation J5b (TASK-20261103-7fc24f).

Implements the definitions of blind-statement.yaml (BS-BATCH-7c689b-J5)
from scratch with sympy. Written in this session; uses no producer code and
reads no file other than the blind statement.

Outputs (in the directory of this script):
  blind-outputs.partial.jsonl  incremental rows, one JSON object per line
  blind-outputs.json           final assembled document

Usage:
  python3 rederive.py [--statement PATH] [--workers N]

Definitions implemented (quoted from the statement, interpretation notes in
review.md):
  S3(x1,x2,x3) = (x1-x2)^2*x3^2 - 2*((x1+x2)*(x1*x2+a) + 2*b)*x3
                 + ((x1*x2-a)^2 - 4*b*(x1+x2))
  S4_exact  = Res_t(S3(x1,x2,t), S3(x3,x4,t)) over Z with integer a, b,
              expanded.
  S4_legacy = Res_t(S3(x1,x2,t), R) where R is S3(x1,x2,x3) after the
              sequential substitutions x1->x3, then x2->x4, then x3->t.
  s4_support = number of terms of the expanded S4 in Z[x1..x4] whose
              coefficient is nonzero mod p.
  fib_system = <S4(x1,x2,x3,Rx), f_V(x1), f_V(x2), f_V(x3)> in F_p[x1,x2,x3],
              f_V(z) = prod_{v in V}(z - v).
  fib_quantities = reduced grevlex (x1>x2>x3) Groebner basis over F_p:
              size, max total degree, unit-ideal flag.

The statement does not say which S4 definition the FIB system uses; both are
computed and reported separately (see review.md, ambiguity A1).

Independent checks per row:
  ICINV: resultant recomputed as an explicit Sylvester determinant; gauge
         twin parameters recomputed as (u^4 a, u^6 b) mod p.
  FIB:   Groebner basis recomputed with a second algorithm (f5b) once per
         distinct (definition, Rx); unit flag cross-checked by evaluating S4
         on all of V^3 (the ideal is the unit ideal iff S4 has no zero on
         V^3, because the f_V split over F_p with distinct roots).
"""
import argparse
import hashlib
import json
import os
import sys
import time
from multiprocessing import Pool

import sympy as sp
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_STATEMENT = os.path.normpath(
    os.path.join(HERE, "..", "..", "blind-statement.yaml"))
FROZEN_SHA256 = "d2e97f75a1e579a9e6f7b4921bdddb3e9833f7e131113c6009e02f7e26e457e2"

x1, x2, x3, x4, t = sp.symbols("x1 x2 x3 x4 t")
GENS4 = (x1, x2, x3, x4)
GENS3 = (x1, x2, x3)


def S3(u, v, w, a, b):
    return ((u - v) ** 2 * w ** 2
            - 2 * ((u + v) * (u * v + a) + 2 * b) * w
            + ((u * v - a) ** 2 - 4 * b * (u + v)))


def right_factor(defn, a, b):
    if defn == "exact":
        return S3(x3, x4, t, a, b)
    if defn == "legacy":
        e = S3(x1, x2, x3, a, b)
        e = e.subs(x1, x3)   # sequential, one at a time
        e = e.subs(x2, x4)
        e = e.subs(x3, t)
        return e
    raise ValueError(defn)


def s4(defn, a, b):
    """S4 over Z (a, b integers), expanded, as a Poly in x1..x4 over ZZ."""
    r = sp.resultant(S3(x1, x2, t, a, b), right_factor(defn, a, b), t)
    return sp.Poly(sp.expand(r), *GENS4, domain=sp.ZZ)


def sylvester_det(f, g, var):
    """Independent resultant: explicit Sylvester matrix determinant."""
    F = sp.Poly(f, var)
    G = sp.Poly(g, var)
    m, n = F.degree(), G.degree()
    fc, gc = F.all_coeffs(), G.all_coeffs()
    size = m + n
    rows = []
    for i in range(n):
        rows.append([0] * i + fc + [0] * (size - m - 1 - i))
    for i in range(m):
        rows.append([0] * i + gc + [0] * (size - n - 1 - i))
    M = sp.Matrix(rows)
    return sp.Poly(sp.expand(M.det(method="berkowitz")), *GENS4, domain=sp.ZZ)


def support_mod_p(P, p):
    return sum(1 for c in P.coeffs() if int(c) % p != 0)


def icinv_task(job):
    rec_id, set_name, idx, role, a, b, p, extra = job
    t0 = time.time()
    row = {"kind": "icinv", "record_id": rec_id, "set": set_name,
           "curve_index": idx, "role": role, "p": p, "a": a, "b": b}
    row.update(extra)
    for defn in ("exact", "legacy"):
        try:
            P = s4(defn, a, b)
            sup = support_mod_p(P, p)
            Q = sylvester_det(S3(x1, x2, t, a, b), right_factor(defn, a, b), t)
            agree = (P - Q).is_zero
            row["s4_support_" + defn] = sup
            row["check_sylvester_agrees_" + defn] = bool(agree)
            row["s4_total_degree_mod_p_" + defn] = sp.Poly(
                P.as_expr(), *GENS4, modulus=p).total_degree()
        except Exception as exc:  # record, do not guess
            row["s4_support_" + defn] = None
            row["error_" + defn] = repr(exc)
    row["seconds"] = round(time.time() - t0, 3)
    return row


def fpoly(defn, a, b, p, Rx):
    P = s4(defn, a, b)
    f = sp.expand(P.as_expr().subs(x4, Rx))
    return f


def gb_quantities(gens, p, method):
    G = sp.groebner(gens, *GENS3, order="grevlex", modulus=p, method=method)
    exprs = list(G.exprs)
    unit = len(exprs) == 1 and sp.Poly(exprs[0], *GENS3).is_ground and exprs[0] != 0
    maxdeg = max(sp.Poly(g, *GENS3).total_degree() for g in exprs)
    return len(exprs), int(maxdeg), bool(unit)


def fib_task(job):
    tidx, defn, Rx, a, b, p, V, crosscheck = job
    t0 = time.time()
    row = {"kind": "fib", "target_index": tidx, "s4_definition": defn,
           "Rx": Rx, "p": p, "a": a, "b": b}
    try:
        f = fpoly(defn, a, b, p, Rx)
        fV = [sp.expand(sp.prod([z - v for v in V])) for z in GENS3]
        gens = [f] + fV
        size, maxdeg, unit = gb_quantities(gens, p, "buchberger")
        row["groebner_basis_size"] = size
        row["groebner_basis_max_degree"] = maxdeg
        row["unit_ideal"] = unit
        # unit-ideal cross-check by evaluation on V^3
        Fp = sp.Poly(f, *GENS3, modulus=p)
        zeros = sum(1 for u in V for v in V for w in V
                    if Fp.eval({x1: u, x2: v, x3: w}) % p == 0)
        row["check_zeros_on_V3"] = zeros
        row["check_unit_by_evaluation_agrees"] = (unit == (zeros == 0))
        if crosscheck:
            s2, d2, u2 = gb_quantities(gens, p, "f5b")
            row["check_f5b_agrees"] = (s2, d2, u2) == (size, maxdeg, unit)
    except Exception as exc:
        row["error"] = repr(exc)
    row["seconds"] = round(time.time() - t0, 3)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--statement", default=DEFAULT_STATEMENT)
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    args = ap.parse_args()

    raw = open(args.statement, "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != FROZEN_SHA256:
        sys.exit("statement sha256 mismatch: " + sha)
    st = yaml.safe_load(raw)["blind_statement"]

    ic = st["icinv"]
    p = int(ic["p"])
    jobs = []
    counters = {}
    for c in ic["curves"]:
        s = c["set"]
        i = counters.get(s, 0)
        counters[s] = i + 1
        a, b, u = int(c["a"]), int(c["b"]), int(c["gauge_u"])
        ga, gb = int(c["gauge_a"]), int(c["gauge_b"])
        gauge_ok = (ga == pow(u, 4, p) * a % p) and (gb == pow(u, 6, p) * b % p)
        jobs.append((f"{s}-{i:03d}-base", s, i, "base", a, b, p,
                     {"gauge_u": u, "gauge_params_consistent": gauge_ok}))
        jobs.append((f"{s}-{i:03d}-gauge", s, i, "gauge_twin", ga, gb, p,
                     {"gauge_u": u, "gauge_params_consistent": gauge_ok}))

    fib = st["fib_c16_1"]
    fp, fa, fb = int(fib["p"]), int(fib["a"]), int(fib["b"])
    V = [int(v) for v in fib["V"]]
    seen = set()
    fjobs = []
    for tg in fib["targets"]:
        for defn in ("exact", "legacy"):
            Rx = int(tg["Rx"])
            key = (defn, Rx)
            fjobs.append((int(tg["target_index"]), defn, Rx, fa, fb, fp, V,
                          key not in seen))
            seen.add(key)

    partial = os.path.join(HERE, "blind-outputs.partial.jsonl")
    done = {}
    if os.path.exists(partial):
        for line in open(partial):
            r = json.loads(line)
            k = (r["kind"], r.get("record_id"), r.get("target_index"),
                 r.get("s4_definition"))
            done[k] = r

    def key_ic(j):
        return ("icinv", j[0], None, None)

    def key_fib(j):
        return ("fib", None, j[0], j[1])

    todo_ic = [j for j in jobs if key_ic(j) not in done]
    todo_fib = [j for j in fjobs if key_fib(j) not in done]
    t0 = time.time()
    with open(partial, "a") as out, Pool(args.workers) as pool:
        n = 0
        for r in pool.imap_unordered(icinv_task, todo_ic):
            out.write(json.dumps(r, sort_keys=True) + "\n")
            out.flush()
            n += 1
            if n % 50 == 0:
                print(f"icinv {n}/{len(todo_ic)} {time.time()-t0:.0f}s", flush=True)
        n = 0
        for r in pool.imap_unordered(fib_task, todo_fib):
            out.write(json.dumps(r, sort_keys=True) + "\n")
            out.flush()
            n += 1
            if n % 20 == 0:
                print(f"fib {n}/{len(todo_fib)} {time.time()-t0:.0f}s", flush=True)

    rows = {}
    for line in open(partial):
        r = json.loads(line)
        k = (r["kind"], r.get("record_id"), r.get("target_index"),
             r.get("s4_definition"))
        rows[k] = r
    ic_rows = [rows[key_ic(j)] for j in jobs]
    fib_rows = [rows[key_fib(j)] for j in fjobs]
    for r in fib_rows:
        r.setdefault("check_f5b_agrees", None)
    not_computed = (
        [r["record_id"] for r in ic_rows
         if r.get("s4_support_exact") is None or r.get("s4_support_legacy") is None]
        + [f"fib-{r['target_index']}-{r['s4_definition']}" for r in fib_rows
           if "error" in r])
    doc = {
        "schema": "blind-outputs/v1",
        "task_id": "TASK-20261103-7fc24f",
        "joint": "J5b",
        "statement_id": st["id"],
        "statement_sha256": sha,
        "software": {"python": sys.version.split()[0], "sympy": sp.__version__},
        "counts": {"icinv_records": len(ic_rows), "fib_rows": len(fib_rows),
                   "fib_targets": len(fib["targets"])},
        "not_computed": not_computed,
        "notes": "FIB rows are given for both S4 definitions because the "
                 "statement does not name one (review.md, A1). f5b cross-check "
                 "runs once per distinct (definition, Rx); null means not run "
                 "for that row because an identical ideal was already checked.",
        "icinv": ic_rows,
        "fib_c16_1": fib_rows,
    }
    with open(os.path.join(HERE, "blind-outputs.json"), "w") as fh:
        json.dump(doc, fh, indent=1, sort_keys=False)
        fh.write("\n")
    print("done", len(ic_rows), len(fib_rows), "not_computed", len(not_computed))


if __name__ == "__main__":
    main()
