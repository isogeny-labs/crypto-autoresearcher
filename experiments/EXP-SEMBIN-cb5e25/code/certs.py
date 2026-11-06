"""Certificate emitters: sembin-ann-v1 (non-containment) and sembin-wdag-v1
(containment), plus the serialisation hash (M-10). The formats are described
in ../formats.md (written for an author who has not read this file).

Reference: experiments/EXP-CERTBIN-060020/impl/closures.py (formats only; it is
not imported). The level-wise grouped DAG construction below follows the
same idea (rows of iteration i-1 plus v_j times the fallen rows used with j)
but is generalised to several targets and to generators of mixed degree.
"""
from __future__ import annotations

import gzip
import hashlib
import json

import numpy as np

import _paths  # noqa: F401
from crypto_autoresearcher.gf2 import closure as gclosure
from crypto_autoresearcher.gf2 import kernels

from closure import SembinClosure, popcount, reduce_member
from descent import canonical_bytes, system_sha256, _vars_of  # noqa: F401


def _optional(cert: dict, Z, meta) -> None:
    """Optional informational keys are written only when populated: an empty `instance`
    object or an empty `Z` list is never written (a checker treats an empty block as malformed)."""
    if Z:
        cert["Z"] = [format(z, "x") for z in Z]
    if meta:
        cert["instance"] = meta


def mask_vars(mask: int):
    return list(_vars_of(mask))


def poly_to_json(masks):
    """Polynomial -> sorted list of variable-index lists (constant = [])."""
    return [mask_vars(m) for m in sorted(masks, key=lambda m: (popcount(m), mask_vars(m)))]


def poly_from_json(lst):
    out = 0
    res = []
    for vs in lst:
        m = 0
        for i in vs:
            m |= 1 << i
        res.append(m)
    return sorted(res)


def row_hex(row) -> str:
    return format(int.from_bytes(np.ascontiguousarray(row).tobytes(), "little"), "x")


def cert_bytes(cert: dict) -> bytes:
    return json.dumps(cert, sort_keys=True, separators=(",", ":")).encode()


def cert_sha256(cert: dict) -> str:
    return hashlib.sha256(cert_bytes(cert)).hexdigest()


def write_cert(path: str, cert: dict, max_bytes=None) -> dict:
    """Gzip the canonical JSON. If max_bytes is given and the JSON (before gzip) is
    larger, nothing is written and {"not_emitted": reason} is returned."""
    data = cert_bytes(cert)
    if max_bytes is not None and len(data) > max_bytes:
        return {"not_emitted": f"JSON before gzip is {len(data)} bytes, guard {max_bytes}"}
    with gzip.GzipFile(path, "wb", mtime=0) as f:
        f.write(data)
    return {"path": path, "content_sha256": hashlib.sha256(data).hexdigest(),
            "content_bytes": len(data)}


# --------------------------------------------------------------------------
# ann-v1
# --------------------------------------------------------------------------
def _rref(basis, leads):
    R = basis.copy()
    leads = np.asarray(leads, dtype=np.int64)
    for t in np.argsort(-leads, kind="stable").tolist():
        c = int(leads[t])
        w, b = c >> 6, np.uint64(c & 63)
        col = (R[:, w] >> b) & np.uint64(1)
        col[t] = 0
        hit = np.flatnonzero(col)
        if hit.size:
            R[hit] ^= R[t]
    return R


def annihilator_hex(cl: SembinClosure):
    basis, leads = cl._final
    R = _rref(basis, leads)
    C, W = cl.C, cl.W
    b = R.view(np.uint8).reshape(R.shape[0], W * 8)
    Ru = np.unpackbits(b, axis=1, bitorder="little")[:, :C]
    leads = np.asarray(leads, dtype=np.int64)
    piv = np.zeros(C, dtype=bool)
    piv[leads] = True
    free = np.flatnonzero(~piv)
    Lu = np.zeros((free.size, C), dtype=np.uint8)
    Lu[np.arange(free.size), free] = 1
    Lu[:, leads] = Ru[:, free].T
    pad = W * 64 - C
    if pad:
        Lu = np.concatenate([Lu, np.zeros((Lu.shape[0], pad), np.uint8)], axis=1)
    packed = np.packbits(Lu, axis=1, bitorder="little")
    return [format(int.from_bytes(row.tobytes(), "little"), "x") for row in packed]


def primal_hex(cl: SembinClosure):
    basis, leads = cl._final
    return [row_hex(basis[t]) for t in range(basis.shape[0])]


def estimate_ann_bytes(cl: SembinClosure) -> int:
    dimW = int(cl._final[0].shape[0])
    return int(min(cl.C - dimW, dimW) * cl.C / 4)


def make_ann_cert(cl: SembinClosure, nv: int, eqs, g_masks, g_index: int, meta: dict,
                  Z: list, form: str = "auto", max_bytes: int = 512 << 20):
    """Non-containment certificate for the closure computed in cl (cl._final
    is W_D). g_masks must be a reduced-GB element not in W_D. Returns the cert
    dict, or a dict {"not_emitted": reason} when the size guard trips."""
    dimW = int(cl._final[0].shape[0])
    codim = cl.C - dimW
    if form == "auto":
        form = "primal" if codim > dimW else "dual"
    est = estimate_ann_bytes(cl)
    if est > max_bytes:
        return {"not_emitted": f"size estimate {est} bytes exceeds guard {max_bytes}", "form": form}
    cert = {
        "schema": "sembin-ann-v1", "D": cl.D, "nv": nv, "neq": len(eqs),
        "system_sha256": system_sha256(nv, eqs),
        "form": form,
        "g": poly_to_json(g_masks), "g_gb_index": g_index,
    }
    _optional(cert, Z, meta)
    if form == "dual":
        cert["L_hex"] = annihilator_hex(cl)
    else:
        cert["basis_hex"] = primal_hex(cl)
    return cert


# --------------------------------------------------------------------------
# wdag-v1 (multi-output)
# --------------------------------------------------------------------------
def build_levels(cl: SembinClosure, eqs):
    """Replays the engine's W_D iteration (same operations as
    Closure._w_closure) keeping every stack, op log and origin map."""
    M = cl.build_M(eqs)
    orig = M.copy()
    log = kernels.column_pass(M, cl.C, keep_ops=True)
    ps, cs = log.ps.astype(np.int64), log.cs.astype(np.int64)
    levels = [{"log": log, "origin": None, "orig": orig}]
    dims = [int(len(ps))]
    prev_low = set()
    while True:
        order = np.argsort(cs, kind="stable")
        prow, leads = ps[order], cs[order]
        basis = M[prow]
        low = cl.col_deg[leads] <= cl.D - 1
        lowidx = np.flatnonzero(low)
        new = np.array([t for t in lowidx if int(leads[t]) not in prev_low], dtype=np.int64)
        prev_low = set(int(x) for x in leads[low])
        P = cl.products(basis[new])
        M = np.concatenate([basis, P])
        del P
        orig = M.copy()
        log2 = kernels.column_pass(M, cl.C, keep_ops=True)
        ps2, cs2 = log2.ps.astype(np.int64), log2.cs.astype(np.int64)
        levels.append({"log": log2, "orig": orig,
                       "origin": {"nb": int(len(prow)), "prow": prow, "newrows": prow[new],
                                  "nnew": int(new.size)}})
        if len(ps2) == dims[-1]:
            return levels, dims
        dims.append(int(len(ps2)))
        ps, cs = ps2, cs2


def _top_sets(cl, levels, targets_packed):
    """Express each target (packed row in W_D) as an XOR of ORIGINAL rows of the
    top stack. Returns list of sets of original-row indices."""
    top = levels[-1]
    orig = top["orig"]
    R = orig.shape[0]
    T = len(targets_packed)
    ext = np.concatenate([orig, np.array(targets_packed, dtype=np.uint64).reshape(T, cl.W)])
    log = kernels.column_pass(ext.copy(), cl.C, keep_ops=True)
    nw = (T + 63) // 64
    S = np.zeros((R + T, nw), dtype=np.uint64)
    for i in range(T):
        S[R + i, i >> 6] ^= np.uint64(1 << (i & 63))
    kernels.backtrace(log, S)
    out = []
    for i in range(T):
        col = (S[:, i >> 6] >> np.uint64(i & 63)) & np.uint64(1)
        rows = np.flatnonzero(col).tolist()
        extra = [r for r in rows if r >= R and r != R + i]
        if extra or (R + i) not in rows:
            raise AssertionError("target is not expressible in the top stack (not in W_D?)")
        out.append(set(r for r in rows if r < R))
    return out


def make_wdag_cert(cl: SembinClosure, nv: int, eqs, targets, meta: dict, Z: list,
                   expected_final_dim: int = None):
    """Containment certificate: one DAG with one output per target polynomial
    (each a list of masks lying in W_D). Raises if a target is not in W_D."""
    levels, dims = build_levels(cl, eqs)
    if expected_final_dim is not None and dims[-1] != expected_final_dim:
        raise AssertionError(f"replayed W_D dim {dims[-1]} != engine {expected_final_dim}")
    tp = []
    for g in targets:
        tp.append(cl.vec(g))
    top_sets = _top_sets(cl, levels, tp)
    nodes = {}
    seq = [0]

    def new_node(key, level):
        nodes[key] = {"level": level, "seq": seq[0], "rows": {}, "prods": {}}
        seq[0] += 1

    pending = {}
    top = len(levels) - 1

    def handle_originals(level, key, rows):
        node = nodes[key]
        org = levels[level]["origin"]
        for r in rows:
            if org is None:
                pk = cl.row_pair(r)
                node["rows"][pk] = node["rows"].get(pk, 0) ^ 1
            elif r < org["nb"]:
                pr = int(org["prow"][r])
                pending.setdefault(level - 1, {}).setdefault(key, set()).symmetric_difference_update({pr})
            else:
                j, f = divmod(r - org["nb"], org["nnew"])
                x = int(org["newrows"][f])
                ck = ("g", key, j, level - 1)
                if ck not in nodes:
                    new_node(ck, level - 1)
                    node["prods"][(j, ck)] = 1
                pending.setdefault(level - 1, {}).setdefault(ck, set()).symmetric_difference_update({x})

    outs = []
    for i, rows in enumerate(top_sets):
        key = ("out", i)
        new_node(key, top)
        outs.append(key)
        handle_originals(top, key, sorted(rows))
    for level in range(top - 1, -1, -1):
        tg = {k: v for k, v in pending.pop(level, {}).items() if v}
        if not tg:
            continue
        keys = list(tg)
        nt = len(keys)
        nw = (nt + 63) // 64
        nrows = levels[level]["orig"].shape[0]
        S = np.zeros((nrows, nw), dtype=np.uint64)
        for t, key in enumerate(keys):
            for r in tg[key]:
                S[r, t >> 6] ^= np.uint64(1 << (t & 63))
        kernels.backtrace(levels[level]["log"], S)
        for t, key in enumerate(keys):
            col = (S[:, t >> 6] >> np.uint64(t & 63)) & np.uint64(1)
            handle_originals(level, key, np.flatnonzero(col).tolist())
    order = sorted(nodes, key=lambda k: (nodes[k]["level"], nodes[k]["seq"]))
    ids = {k: i for i, k in enumerate(order)}
    out_nodes = []
    for k in order:
        nd = nodes[k]
        rows = sorted([mask_vars(mu), kk] for (mu, kk), p in nd["rows"].items() if p)
        prods = sorted([j, ids[c]] for (j, c), p in nd["prods"].items() if p)
        out_nodes.append({"id": ids[k], "rows": rows, "prods": prods})
    cert = {
        "schema": "sembin-wdag-v1", "D": cl.D, "nv": nv, "neq": len(eqs),
        "system_sha256": system_sha256(nv, eqs),
        "nodes": out_nodes, "outputs": [ids[k] for k in outs],
        "targets": [poly_to_json(g) for g in targets],
        "levels": len(levels),
    }
    _optional(cert, Z, meta)
    return cert


# --------------------------------------------------------------------------
# irredundant Lambda (used by fixture F-5 so that a single flipped bit matters)
# --------------------------------------------------------------------------
def prune_dual(cert: dict, cols_low_mask: int, prod_cols, nv: int):
    """Greedy removal of functionals from a dual-form certificate while (b)
    closure and (c) Lambda(g) != 0 keep holding ((a) holds for any subfamily of
    an annihilator). prod_cols[j][c] = column of X_j * (column c monomial) for
    columns c of degree <= D-1. Returns the pruned certificate. Small
    instances only (python-int linear algebra)."""
    L = [int(h, 16) for h in cert["L_hex"]]
    gv = cert["_g_vec"]
    low_cols = sorted(prod_cols[0])

    def closed(Ls):
        piv = {}
        for l in Ls:
            v = 0
            for c in low_cols:
                if (l >> c) & 1:
                    v |= 1 << c
            while v:
                low = (v & -v).bit_length() - 1
                if low in piv:
                    v ^= piv[low]
                else:
                    piv[low] = v
                    break
        for l in Ls:
            for j in range(nv):
                nu = 0
                for c in low_cols:
                    if (l >> prod_cols[j][c]) & 1:
                        nu |= 1 << c
                while nu:
                    low = (nu & -nu).bit_length() - 1
                    if low not in piv:
                        return False
                    nu ^= piv[low]
        return True

    def sees_g(Ls):
        return any(bin(l & gv).count("1") & 1 for l in Ls)

    i = 0
    while i < len(L):
        trial = L[:i] + L[i + 1:]
        if trial and sees_g(trial) and closed(trial):
            L = trial
        else:
            i += 1
    out = dict(cert)
    out.pop("_g_vec", None)
    out["L_hex"] = [format(l, "x") for l in L]
    return out
