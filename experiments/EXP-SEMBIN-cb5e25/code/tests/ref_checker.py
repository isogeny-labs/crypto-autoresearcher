"""Producer-side REFERENCE checker for the unit tests and for fixture F-5.

It is NOT the independent certificate checker of the specification (that is
written by a Validator task, blind to code/). It imports nothing from the
producer modules; it works from the serialised system bytes and the
certificate JSON only, following ../../formats.md.
"""
from __future__ import annotations

import hashlib
import json
from itertools import combinations


def parse_system(data: bytes):
    obj = json.loads(data)
    assert obj["schema"] == "sembin-sys-v1"
    nv = obj["nv"]
    eqs = []
    for e in obj["eqs"]:
        eqs.append(sorted(sum(1 << i for i in mono) for mono in e))
    return nv, eqs, hashlib.sha256(data).hexdigest()


def deg(mask):
    return bin(mask).count("1")


def columns(nv, D):
    cols = []
    for d in range(D, -1, -1):
        cols.extend(sorted(sum(1 << i for i in c) for c in combinations(range(nv), d)))
    return cols


def macaulay_rows(nv, eqs, D, colidx):
    rows = []
    for e in eqs:
        if not e:
            continue
        de = max(deg(m) for m in e)
        for td in range(0, D - de + 1):
            for c in combinations(range(nv), td):
                t = sum(1 << i for i in c)
                acc = {}
                for m in e:
                    acc[t | m] = acc.get(t | m, 0) ^ 1
                v = 0
                for m, p in acc.items():
                    if p:
                        v |= 1 << colidx[m]
                rows.append(v)
    return rows


def _echelon(rows):
    """pivot = lowest set bit; returns dict lead->row (not fully reduced)."""
    piv = {}
    for v in rows:
        while v:
            low = (v & -v).bit_length() - 1
            if low in piv:
                v ^= piv[low]
            else:
                piv[low] = v
                break
    return piv


def _reduces(piv, v):
    while v:
        low = (v & -v).bit_length() - 1
        if low not in piv:
            return False
        v ^= piv[low]
    return True


def brute_Z(nv, eqs):
    sol = []
    for p in range(1 << nv):
        if all(sum(1 for m in e if m & ~p == 0) % 2 == 0 for e in eqs):
            sol.append(p)
    return sol


def check_ann(cert, sys_bytes, brute_max_nv=18):
    rep = {}
    nv, eqs, sha = parse_system(sys_bytes)
    D = cert["D"]
    rep["e_hash"] = (sha == cert["system_sha256"] and nv == cert["nv"])
    cols = columns(nv, D)
    colidx = {m: i for i, m in enumerate(cols)}
    C = len(cols)
    rows = macaulay_rows(nv, eqs, D, colidx)
    gv = 0
    for vs in cert["g"]:
        m = sum(1 << i for i in vs)
        gv ^= 1 << colidx[m]
    low_cols = [i for i, m in enumerate(cols) if deg(m) <= D - 1]
    low_mask = sum(1 << i for i in low_cols)
    # product map: column c (deg <= D-1) -> column of X_j * mono
    def prod_col(j, c):
        return colidx[cols[c] | (1 << j)]
    if cert["form"] == "dual":
        L = [int(h, 16) for h in cert["L_hex"]]
        par = lambda x: bin(x).count("1") & 1
        rep["a_rows_killed"] = all(par(l & r) == 0 for l in L for r in rows)
        # (b) closure
        lowL = _echelon([l & low_mask for l in L])
        ok = True
        for j in range(nv):
            for l in L:
                nu = 0
                for c in low_cols:
                    if (l >> prod_col(j, c)) & 1:
                        nu |= 1 << c
                if not _reduces(lowL, nu):
                    ok = False
                    break
            if not ok:
                break
        rep["b_closed"] = ok
        rep["c_g_not_killed"] = any(par(l & gv) for l in L)
    else:
        basis = _echelon([int(h, 16) for h in cert["basis_hex"]])
        rep["a_rows_killed"] = all(_reduces(basis, r) for r in rows)
        ok = True
        for lead, row in basis.items():
            if deg(cols[lead]) <= D - 1:
                for j in range(nv):
                    v = 0
                    for c in low_cols:
                        if (row >> c) & 1:
                            v ^= 1 << prod_col(j, c)
                    if not _reduces(basis, v):
                        ok = False
        rep["b_closed"] = ok
        rep["c_g_not_killed"] = not _reduces(basis, gv)
    # (d) g vanishes on Z (brute force Z, small nv only)
    if nv <= brute_max_nv:
        Z = brute_Z(nv, eqs)
        gm = [sum(1 << i for i in vs) for vs in cert["g"]]
        rep["d_g_vanishes_on_Z"] = all(sum(1 for m in gm if m & ~p == 0) % 2 == 0 for p in Z)
        rep["d_Z_matches_listed"] = sorted(int(z, 16) for z in cert.get("Z", [])) == Z
    else:
        rep["d_g_vanishes_on_Z"] = None
    rep["accept"] = all(v is True for k, v in rep.items() if k != "d_Z_matches_listed") and \
        rep.get("d_g_vanishes_on_Z") is not None
    return rep


def check_wdag(cert, sys_bytes, brute_max_nv=18):
    rep = {}
    nv, eqs, sha = parse_system(sys_bytes)
    D = cert["D"]
    rep["e_hash"] = (sha == cert["system_sha256"] and nv == cert["nv"])
    edeg = [max((deg(m) for m in e), default=-1) for e in eqs]
    polys = {}
    ok_a = ok_b = ok_c = ok_d = True
    for node in cert["nodes"]:
        i = node["id"]
        acc = {}
        for vs, k in node["rows"]:
            mu = sum(1 << x for x in vs)
            if not (0 <= k < len(eqs)) or deg(mu) + edeg[k] > D:
                ok_b = False
                continue
            for m in eqs[k]:
                acc[mu | m] = acc.get(mu | m, 0) ^ 1
        for j, c in node["prods"]:
            if c >= i or c not in polys:
                ok_a = False
                continue
            if max((deg(m) for m in polys[c]), default=-1) > D - 1:
                ok_c = False
            for m in polys[c]:
                acc[m | (1 << j)] = acc.get(m | (1 << j), 0) ^ 1
        polys[i] = frozenset(m for m, p in acc.items() if p)
        if max((deg(m) for m in polys[i]), default=-1) > D:
            ok_d = False
    rep.update(a_children_earlier=ok_a, b_rows_degree=ok_b, c_child_degree=ok_c, d_node_degree=ok_d)
    tg = [frozenset(sum(1 << x for x in vs) for vs in t) for t in cert["targets"]]
    rep["e_outputs_equal_targets"] = all(polys[o] == t for o, t in zip(cert["outputs"], tg))
    if nv <= brute_max_nv:
        Z = brute_Z(nv, eqs)
        rep["f_vanish_on_Z"] = all(sum(1 for m in t if m & ~p == 0) % 2 == 0 for t in tg for p in Z)
        # leads (grevlex: bigger = higher degree, then smaller mask) generate; standard count == |Z|
        leads = []
        for t in tg:
            leads.append(min(t, key=lambda m: (-deg(m), m)))
        std = 0
        for d in range(0, nv + 1):
            cnt = 0
            for c in combinations(range(nv), d):
                m = sum(1 << i for i in c)
                if not any(l & ~m == 0 for l in leads):
                    cnt += 1
            std += cnt
            if cnt == 0:
                break
        rep["f_standard_count_equals_Z"] = (std == len(Z))
    rep["accept"] = all(v is True for v in rep.values())
    return rep
