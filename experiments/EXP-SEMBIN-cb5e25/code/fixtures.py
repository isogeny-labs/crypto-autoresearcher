#!/usr/bin/env python3
"""Fixtures F-1..F-8 (specification fixtures). Each returns
{"id", "verdict": pass | fail | not_covered, "detail"}. A fixture that cannot
run (e.g. Sage missing for F-6) is reported not_covered with the reason and is
never reported as pass.

    python3 fixtures.py --out fixtures.json --protocol-sha256 <hex> [--only F-1,F-5] [--no-sage]
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import subprocess
import sys
import time
from itertools import combinations

import numpy as np

import _paths  # noqa: F401
import cells as CE
import certs
import closure as CL
import descent as DS
import dfeq
import enumz
from rng import HashRng, seed_for

SAGE = "/opt/conda-sage/bin/sage"


def _res(fid, ok, detail):
    return {"id": fid, "verdict": "pass" if ok else "fail", "detail": detail}


def _nc(fid, reason):
    return {"id": fid, "verdict": "not_covered", "detail": {"reason": reason}}


# --------------------------------------------------------------------------
def f1():
    two = dfeq.d_F_eq([], 2, include_fe=True, dmax_rank=3, rank_up_to=4)
    one = dfeq.d_F_eq([], 1, include_fe=True, dmax_rank=3, rank_up_to=4)
    w = two["witness"]
    ok = (two["value"] == 4 and w is not None and w["valid_fall"] and w["max_product_degree"] == 4
          and w["sum_degree"] == 2 and two["per_d"][4]["fall"]
          and not any(two["per_d"][d]["fall"] for d in (1, 2, 3))
          and one["value"] is None and not any(v["fall"] for v in one["per_d"].values()))
    return _res("F-1", ok, {"two_fe_value": two["value"], "witness": w, "single_fe_value": one["value"],
                            "single_fe_falls_d1_4": {d: v["fall"] for d, v in one["per_d"].items()}})


def f2():
    sys.path.insert(0, _paths.TOOLS)
    import lemma4_inside_form as L4
    cases = {
        "A (X^2 Y, XY + X)": (2, [frozenset({(0, 0, 1)}), frozenset({(0, 1), (0,)})],
                              [frozenset({(2, 1)}), frozenset({(1, 1), (1, 0)})]),
        "B (X1X2 + X3, X1X3 + X2)": (3, [frozenset({(0, 1), (2,)}), frozenset({(0, 2), (1,)})],
                                     [frozenset({(1, 1, 0), (0, 0, 1)}), frozenset({(1, 0, 1), (0, 1, 0)})]),
    }
    out, ok = {}, True
    for name, (N, mine, theirs) in cases.items():
        r = dfeq.d_F_eq(mine, N, include_fe=True, dmax_rank=3, rank_up_to=4)
        oracle = L4.first_fall_degree(list(theirs) + L4.field_equations(N), fake=False, n=N, dmax=4)
        out[name] = {"mine": r["value"], "oracle": oracle}
        ok &= (r["value"] == 3 and oracle == 3)
    return _res("F-2", ok, out)


def _mu_order(dmax, nv):
    out = []
    for d in range(dmax + 1):
        out.extend(combinations(range(nv), d))
    return out


def E_to_eqs(Ehex, nv=20):
    mons = _mu_order(2, nv)
    masks = [sum(1 << i for i in m) for m in mons]
    eqs = []
    for h in Ehex:
        v = int(h, 16)
        eqs.append(sorted(masks[j] for j in range(len(masks)) if (v >> j) & 1))
    return eqs


def f3():
    import artifact_store as AS
    base = os.path.join(_paths.REPO, "experiments/EXP-CERTBIN-060020/runs/RUN-CERTBIN-a3fc60")
    try:
        def lines(name):
            raw = AS.read_bytes(os.path.join(base, name))
            if raw[:2] == b"\x1f\x8b":
                raw = gzip.decompress(raw)
            return [json.loads(l) for l in raw.decode().splitlines() if l.strip()]
        insts = lines("instances.jsonl.gz")
        arch = {d["key"]: d for d in lines("closures.jsonl.gz")}
    except Exception as exc:     # noqa: BLE001
        return _nc("F-3", f"cannot read RUN-CERTBIN-a3fc60 through tools/artifact_store.py: {exc!r}")
    prim = [i for i in insts if i["arm"] == "S3-U400"][:10]
    rows, ok = [], True
    for inst in prim:
        eqs = E_to_eqs(inst["E_hex"])
        a = arch[inst["key"]]
        mrec, _ = CL.m_closure_record(20, 4, eqs)
        wrec, _ = CL.w_closure_record(20, 4, eqs)
        good = (wrec["one"] is True and mrec["one"] is False
                and a["W_4"]["one"] is True and a["M_4"]["one"] is False
                and mrec["rank"] == a["M_4"]["rank"] and mrec["dims_by_deg"] == a["M_4"]["dims_by_deg"]
                and wrec["dims_by_deg"] == a["W_4"]["dims_by_deg"] and wrec["dims"] == a["W_4"]["dims"])
        ok &= good
        rows.append({"key": inst["key"], "W4_one": wrec["one"], "M4_one": mrec["one"],
                     "M4_rank": mrec["rank"], "archived_M4_rank": a["M_4"]["rank"],
                     "W4_final_dim": wrec["final_dim"], "match": good})
    return _res("F-3", ok and len(rows) == 10, {"instances": rows})


# ---- independent set-based fixpoint (F-4) --------------------------------
def _poly_deg(p):
    return max((bin(m).count("1") for m in p), default=-1)


def _pack(rows, cols_index, C):
    from crypto_autoresearcher.gf2 import reference as REF  # noqa: F401
    W = (C + 63) // 64
    dense = np.zeros((len(rows), W * 64), dtype=np.uint8)
    for r, p in enumerate(rows):
        for m in p:
            dense[r, cols_index[m]] ^= 1
    b = np.packbits(dense, axis=1, bitorder="little")
    return np.ascontiguousarray(b).view(np.uint64).reshape(len(rows), W).copy()


def reference_fixpoint(nv, eqs, D):
    """Set-based fixpoint written for the fixture: polynomials are python sets,
    elimination is reference.column_pass, products are formed on sets."""
    from crypto_autoresearcher.gf2 import reference as REF
    cols = []
    for d in range(D, -1, -1):
        cols += sorted(sum(1 << i for i in c) for c in combinations(range(nv), d))
    idx = {m: i for i, m in enumerate(cols)}
    C = len(cols)
    rows = []
    for f in eqs:
        e = _poly_deg(f)
        if e < 0:
            continue
        for td in range(0, D - e + 1):
            for c in combinations(range(nv), td):
                t = sum(1 << i for i in c)
                acc = set()
                for m in f:
                    acc ^= {t | m}
                rows.append(acc)

    def echelon(rows_):
        M = _pack(rows_, idx, C) if rows_ else np.zeros((0, (C + 63) // 64), dtype=np.uint64)
        ps, cs, _, _ = REF.column_pass(M, C, keep_ops=False)
        # rows as polynomials again
        basis = []
        for p, c in sorted(zip(ps.tolist(), cs.tolist()), key=lambda x: x[1]):
            bits = np.unpackbits(M[p].view(np.uint8), bitorder="little")[:C]
            basis.append({cols[j] for j in np.flatnonzero(bits)})
        return basis, sorted(cs.tolist())

    basis, leads = echelon(rows)
    dims, prev_low = [len(basis)], set()
    while True:
        low = [(b, c) for b, c in zip(basis, leads) if bin(cols[c]).count("1") <= D - 1]
        new = [b for b, c in low if c not in prev_low]
        prev_low = {c for b, c in low}
        stack = list(basis)
        for j in range(nv):
            for b in new:
                stack.append({m | (1 << j) for m in b} if False else _mulvar(b, j))
        basis2, leads2 = echelon(stack)
        if len(basis2) == dims[-1]:
            break
        dims.append(len(basis2))
        basis, leads = basis2, leads2
    dbd = [sum(1 for c in leads if bin(cols[c]).count("1") <= d) for d in range(D + 1)]
    return {"dims": dims, "dims_by_deg": dbd, "final_dim": dims[-1], "rows_final": len(basis)}


def _mulvar(poly, j):
    acc = set()
    for m in poly:
        acc ^= {m | (1 << j)}
    return acc


def f4(n_systems=50):
    drv = os.path.join(_paths.REPO, "experiments/EXP-ECTD-9e4248/driver")
    sys.path.append(drv)
    try:
        from reused import macaulay as MAC
    finally:
        sys.path.remove(drv)
    rng = HashRng(40404, "F-4")
    bad, checked, oracle_checked = [], 0, 0
    for t in range(n_systems):
        nv = 5 + rng.randbelow(6)                        # 5..10
        neq = max(3, nv - 1 + rng.randbelow(3))
        eqs = []
        for k in range(neq):
            e = set()
            for d, cnt in ((1, 1 + rng.randbelow(2)), (2, 1 + rng.randbelow(4)), (3, rng.randbelow(3))):
                for _ in range(cnt):
                    pool = list(range(nv))
                    m = 0
                    for i in range(d):
                        j = i + rng.randbelow(nv - i)
                        pool[i], pool[j] = pool[j], pool[i]
                        m |= 1 << pool[i]
                    e ^= {m}
            if rng.randbelow(2):
                e ^= {0}
            eqs.append(sorted(e))
        for D in (2, 3, 4, 5):
            if nv >= 9 and D == 5:
                continue
            a, _ = CL.w_closure_record(nv, D, eqs, stream=bool(t % 2))
            b = reference_fixpoint(nv, eqs, D)
            same = (a["dims"] == b["dims"] and a["dims_by_deg"] == b["dims_by_deg"])
            # rank oracle on the first Macaulay matrix (small cases only)
            C = CL.C_le(nv, D)
            if C <= 140:
                cl = CL.SembinClosure(nv, D, eqs)
                Mm = cl.build_M(eqs)
                dense = np.unpackbits(Mm.view(np.uint8), axis=1, bitorder="little")[:, :C].tolist()
                rk = MAC.rank_mod_p(dense, C, 2)
                oracle_checked += 1
                same &= (rk == a["dims"][0])
            checked += 1
            if not same:
                bad.append({"system": t, "nv": nv, "D": D, "engine": a["dims"], "reference": b["dims"]})
    return _res("F-4", not bad, {"systems": n_systems, "comparisons": checked,
                                 "rank_mod_p_oracle_comparisons": oracle_checked, "mismatches": bad[:5]})




def _f5_impl():
    from tests import ref_checker as RC          # producer-side reference checker (NOT the independent one)
    nv, D = 5, 4
    f = [0b11111, 0]
    eqs = [f]
    Z = [0b11111]
    gb = enumz.groebner_from_Z(Z, nv)
    rec, cl = CL.w_closure_record(nv, D, eqs)
    ev = enumz.rank_ev_by_deg(gb, D)[D]
    dec = CL.decide(nv, D, rec, gb, ev)
    gp = enumz.gb_polys(gb)
    idx = next(i for i, g in enumerate(gp) if not cl.member(g))
    cert = certs.make_ann_cert(cl, nv, eqs, gp[idx], idx, {"fixture": "F-5"}, Z, form="dual")
    # irredundant Lambda
    cols = [int(m) for m in cl.col_mask]
    cidx = {m: i for i, m in enumerate(cols)}
    low = [i for i, m in enumerate(cols) if bin(m).count("1") <= D - 1]
    prod_cols = [{c: cidx[cols[c] | (1 << j)] for c in low} for j in range(nv)]
    gv = 0
    for m in gp[idx]:
        gv ^= 1 << cidx[m]
    full = dict(cert)
    tmp = dict(cert)
    tmp["_g_vec"] = gv
    pruned = certs.prune_dual(tmp, None, prod_cols, nv)
    sysb = DS.canonical_bytes(nv, eqs)
    acc_full = RC.check_ann(full, sysb)["accept"]
    acc = RC.check_ann(pruned, sysb)
    # tamper: flip one bit of Lambda (the constant-monomial column of the first functional) and,
    # for the statistics, every single bit of the pruned family.
    L = [int(h, 16) for h in pruned["L_hex"]]
    def flipped(i, c):
        L2 = list(L)
        L2[i] ^= 1 << c
        d = dict(pruned)
        d["L_hex"] = [format(x, "x") for x in L2]
        return d
    const_col = cl.const_col
    tamper = RC.check_ann(flipped(0, const_col), sysb)
    n_flips = rejected = 0
    for i in range(len(L)):
        for c in range(cl.C):
            n_flips += 1
            rejected += 0 if RC.check_ann(flipped(i, c), sysb)["accept"] else 1
    dimW = int(cl._final[0].shape[0])
    ok = (dimW == 0 and not dec["contained"] and dec["type"] == "L" and acc["accept"] and acc_full
          and not tamper["accept"])
    return _res("F-5", ok, {"dim_W4": dimW, "decision": dec, "n_functionals_full": len(cert["L_hex"]),
                            "n_functionals_pruned": len(L), "checker": "tests/ref_checker.py (producer-side; "
                            "the independent Validator checker is pending)",
                            "accepted_pruned": acc["accept"], "accepted_full": acc_full,
                            "tampered_constant_bit_accepted": tamper["accept"],
                            "single_bit_flips_rejected": f"{rejected}/{n_flips}"})


def f7():
    N = 6
    f = [[1 << 0], [1 << 0, 1 << 1], [1 << 2, 0b11], [1 << 3, 0b111], [1 << 4, 0b1110], [1 << 5, 0b10101]]
    # f0 = X0; f1 = X0+X1; f2 = X2+X0X1; f3 = X3+X0X1X2; f4 = X4+X1X2X3; f5 = X5+X0X2X4; s = 0
    # Hand-derived (see the report): rank M_2 = 12, dim W_2 = 15, linear forms 3, 1 not in W_2;
    # dim W_3 = C_3 - 1 = 41, linear forms 6, 1 not in W_3.
    out, ok = {}, True
    for mode, eqs in (("raw", f), ("adapted", CL.adapted_basis(f)[0])):
        for D, (m_rank, w_dim, lin) in ((2, (12, 15, 3)), (3, (None, 41, 6))):
            w, _ = CL.w_closure_record(N, D, eqs)
            m, _ = CL.m_closure_record(N, D, eqs)
            good = (w["final_dim"] == w_dim and w["linear_forms"] == lin and not w["one"]
                    and (m_rank is None or m["rank"] == m_rank))
            ok &= good
            out[f"{mode}/D{D}"] = {"W_dim": w["final_dim"], "expected": w_dim, "M_rank": m["rank"],
                                   "expected_M_rank": m_rank, "lin": w["linear_forms"], "match": good}
    Z = enumz.brute_force_Z(N, f)
    ok &= (Z == [0])
    gb = enumz.groebner_from_Z(Z, N)
    ok &= all(CL.decide(N, D, CL.w_closure_record(N, D, f)[0], gb, enumz.rank_ev_by_deg(gb, D)[D])["contained"] == (D == 3)
              for D in (2, 3))
    return _res("F-7", ok, out)


def f6(no_sage=False, tmpdir=None):
    if no_sage:
        return _nc("F-6", "disabled by --no-sage")
    if not os.path.exists(SAGE):
        return _nc("F-6", f"Sage not found at {SAGE}")
    cases, mine = [], []
    rng = HashRng(60606, "F-6")
    spec = [(3, 3, 1), (3, 4, 1), (3, 5, 1), (3, 6, 2), (4, 8, 2), (3, 8, 2)]
    for ci, (m, n, k) in enumerate(spec):
        for shifted in (False, True):
            F = DS.Field(n)
            A, B, v, _ = DS.draw_shared(F, m, k, rng)
            if not shifted:
                v = [0] * m
            curve = DS.Curve(F, A, B)
            vv = v if shifted else [0] * m
            # x_R need only be a nonzero field element for the descent comparison
            x_R = 1 + rng.randbelow((1 << n) - 1)
            sysd = DS.build_system(F, B, vv, k, x_R)
            cases.append({"n": n, "k": k, "m": m, "poly": F.poly, "A": A, "B": B, "v": vv, "x_R": x_R})
            mine.append({"eqs": sysd["eqs"], "E": curve.count_points(fast=False)})
    try:
        p = subprocess.run([SAGE, "-python", os.path.join(_paths.CODE_DIR, "f6_sage_oracle.py")],
                           input=json.dumps(cases), capture_output=True, text=True, timeout=900)
    except Exception as exc:       # noqa: BLE001
        return _nc("F-6", f"Sage invocation failed: {exc!r}")
    if p.returncode != 0:
        return _nc("F-6", f"Sage oracle failed (rc={p.returncode}): {p.stderr[-400:]}")
    oracle = json.loads(p.stdout.strip().splitlines()[-1])
    rows, ok = [], True
    for c, mi, o in zip(cases, mine, oracle):
        mine_nz = [sorted(e) for e in mi["eqs"] if e]
        same = mine_nz == o["gens"]
        e_same = mi["E"] == o["num_points_E"]
        ok &= same and e_same
        rows.append({"m": c["m"], "n": c["n"], "k": c["k"], "shifted": any(c["v"]), "generators_equal": same,
                     "E_mine": mi["E"], "E_sage": o["num_points_E"]})
    return _res("F-6", ok, {"cases": rows, "note": "Sage field built with the case's modulus; zero coordinate "
                            "polynomials are skipped by the oracle and by the comparison"})


def f8(protocol_sha256):
    """IR-2 standing fixture: Z enumeration == brute force on EQS4/EQS2 (N <= 20)
    and on nulls (N <= 24) for the small cells, seeds 0..2."""
    import run as RUN
    import nulls
    rows, ok = [], True
    for cid in ("m3n03", "m3n04", "m3n05", "m3n06", "m3n07", "m3n08", "m3n09", "m3n10", "m3n11"):
        cell = CE.CELLS[cid]
        for r in range(3):
            sh = RUN.shared_part(cell, r, protocol_sha256)
            for arm in ("EQS4", "EQS2"):
                try:
                    inst = RUN.eqs_instance(cell, sh, arm, r, protocol_sha256)
                except DS.PlantInfeasible:
                    rows.append({"cell": cid, "r": r, "arm": arm, "not_available": "no valid planted decomposition"})
                    continue
                bz = enumz.brute_force_Z(inst["nv"], inst["raw_eqs"])
                good = bz == inst["Z"] and inst["plant"]["s"] in bz
                ok &= good
                rows.append({"cell": cid, "r": r, "arm": arm, "N": inst["nv"], "z": len(bz), "match": good})
        # one null per cell (N <= 24)
        sh = RUN.shared_part(cell, 0, protocol_sha256)
        inst = RUN.eqs_instance(cell, sh, "EQS4", 0, protocol_sha256)
        raw, s = nulls.null_prof(inst["nv"], nulls.profile_of(inst["raw_eqs"]), HashRng(1, "f8null"))
        bz = enumz.brute_force_Z(inst["nv"], raw)
        ok &= s in bz
        rows.append({"cell": cid, "arm": "NULL-PROF", "N": inst["nv"], "z": len(bz), "planted_in_Z": s in bz})
    return _res("F-8", ok, {"instances": len(rows), "rows": rows})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--protocol-sha256", default="0" * 64)
    ap.add_argument("--only", default=None)
    ap.add_argument("--no-sage", action="store_true")
    a = ap.parse_args()
    want = set(a.only.split(",")) if a.only else None
    sys.path.insert(0, os.path.join(_paths.CODE_DIR))
    fns = {"F-1": f1, "F-2": f2, "F-3": f3, "F-4": f4, "F-5": _f5_impl, "F-6": lambda: f6(a.no_sage),
           "F-7": f7, "F-8": lambda: f8(a.protocol_sha256)}
    out = []
    for fid, fn in fns.items():
        if want and fid not in want:
            continue
        t0 = time.time()
        try:
            r = fn()
        except Exception as exc:    # noqa: BLE001
            import traceback
            r = {"id": fid, "verdict": "fail", "detail": {"exception": repr(exc), "tb": traceback.format_exc()}}
        r["wall_s"] = round(time.time() - t0, 2)
        out.append(r)
        print(fid, r["verdict"], r["wall_s"], flush=True)
    with open(a.out, "w") as f:
        json.dump({"fixtures": out, "all_pass_or_not_covered_explained": all(
            x["verdict"] != "fail" for x in out)}, f, indent=1, default=str)
    sys.exit(0 if all(x["verdict"] == "pass" for x in out) else 1)


if __name__ == "__main__":
    main()
