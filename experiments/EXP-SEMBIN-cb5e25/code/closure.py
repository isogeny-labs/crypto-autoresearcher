"""Closure driver around the shared gf2 engine (src/crypto_autoresearcher/gf2).

What is imported and used unchanged: closure.Closure._w_closure (the W_D
fixpoint, the declared iteration), Closure.macaulay_closure, kernels.* (column
pass, products, backtrace) and rankprofile.Shape (column tables without 2^nv
arrays).

What is added here, and why (see implementation notes in the report):
  * SembinClosure(Closure): the engine's Closure.__init__ allocates a 2^nv
    table (infeasible beyond nv ~ 28) and its build_M assumes every generator
    has degree <= 2 (multipliers up to D-2). This subclass replaces ONLY the
    constructor tables and build_M/row_pair/vec: columns come from
    rankprofile.Shape (same order), generators of degree d_k get the
    multipliers of degree <= D - d_k (the specification's M_D), and zero rows
    are not materialised. The iteration (_w_closure) is inherited.
  * capture(): wraps kernels.column_pass while an engine call runs, to record
    the leading-degree profile of every fixpoint iteration (M-4) without
    altering the engine.
  * adapted_basis(): degree-adapted RREF of the generator span (see
    adapted_basis docstring: needed for the A/A exactness under equation
    recombination).
"""
from __future__ import annotations

import contextlib
import hashlib
import os
import time
from math import comb

import numpy as np

import _paths  # noqa: F401
from crypto_autoresearcher.gf2 import closure as gclosure
from crypto_autoresearcher.gf2 import kernels
from crypto_autoresearcher.gf2 import rankprofile


def popcount(x: int) -> int:
    return bin(x).count("1")


def poly_degree(mons) -> int:
    return max((popcount(x) for x in mons), default=-1)


def C_le(N: int, D: int) -> int:
    return sum(comb(N, d) for d in range(D + 1))


# --------------------------------------------------------------------------
# generator canonical form
# --------------------------------------------------------------------------
def adapted_basis(eqs):
    """Degree-adapted reduced row echelon form of the F_2-span of the
    generators, columns in descending grevlex (= engine column order: degree
    descending, mask ascending). Returns (eqs_adapted, stats).

    Why: M_D is defined as span{rho(t f_i): deg t + deg f_i <= D}. For a
    different basis of the same span (an equation recombination) the degrees
    deg f_i change, so M_D of the raw list is NOT invariant. For a basis whose
    leading monomials are distinct (RREF in a degree-compatible order) the
    degrees are the degrees of the leading monomials, and
    span{t g : g in span(F), deg t + deg g <= D} = span{t b_i : deg t + deg b_i
    <= D}. So M_D, W_D and every exact metric are functions of the span only.
    """
    mons = sorted({m for e in eqs for m in e}, key=lambda m: (-popcount(m), m))
    pos = {m: len(mons) - 1 - i for i, m in enumerate(mons)}   # bigger monomial = higher bit
    rows = []
    for e in eqs:
        v = 0
        for m in e:
            v ^= 1 << pos[m]
        rows.append(v)
    piv = {}
    zero = 0
    for v in rows:
        while v:
            h = v.bit_length() - 1
            if h in piv:
                v ^= piv[h]
            else:
                piv[h] = v
                break
        if v == 0:
            zero += 1
    # reduce fully (back-substitution from the lowest pivot upward)
    for h in sorted(piv):
        for h2 in piv:
            if h2 > h and (piv[h2] >> h) & 1:
                piv[h2] ^= piv[h]
    inv = {pos[m]: m for m in mons}
    out = []
    for h in sorted(piv, reverse=True):
        v = piv[h]
        out.append(sorted(inv[b] for b in range(v.bit_length()) if (v >> b) & 1))
    degs = [poly_degree(e) for e in out]
    return out, {"input_equations": len(eqs), "rank": len(out), "dependent_dropped": zero,
                 "degrees": sorted(degs)}


# --------------------------------------------------------------------------
# the engine subclass
# --------------------------------------------------------------------------
class SembinClosure(gclosure.Closure):
    STREAM_AUTO_C = 20000

    def __init__(self, nv: int, D: int, eqs, stream=None):
        self.nv, self.D, self.neq = nv, D, len(eqs)
        sh = rankprofile.shape(nv, D)
        self.sh = sh
        self.C, self.W, self.const_col = sh.C, sh.W, sh.const_col
        self.col_deg = sh.col_deg(np.arange(sh.C))
        self.col_mask = sh.masks.astype(np.int64)
        self.colmap, self.maps = sh.product_tables
        self.eq_deg = [poly_degree(e) for e in eqs]
        if any(d < 1 for d in self.eq_deg):
            # a constant generator (deg 0) means 1 is in the ideal; keep general
            pass
        mind = min([d for d in self.eq_deg if d >= 0] or [1])
        maxmu = max(D - max(mind, 0), 0)
        self.mus = gclosure.mu_order(maxmu, nv)
        mu_mask = np.array([gclosure.mono_mask(m) for m in self.mus], dtype=np.int64)
        mu_deg = np.array([len(m) for m in self.mus], dtype=np.int64)
        rows_mu, rows_k = [], []
        for k, dk in enumerate(self.eq_deg):
            if dk < 0:
                continue
            sel = np.flatnonzero(mu_deg <= D - dk)
            rows_mu.append(mu_mask[sel])
            rows_k.append(np.full(sel.size, k, dtype=np.int64))
        if rows_mu:
            rmu, rk = np.concatenate(rows_mu), np.concatenate(rows_k)
            # engine row order: multiplier index major (degree asc, then tuple), then k
            midx = {int(m): i for i, m in enumerate(mu_mask)}
            order = np.lexsort((rk, np.array([midx[int(m)] for m in rmu], dtype=np.int64)))
            self.row_mu, self.row_k = rmu[order], rk[order]
        else:
            self.row_mu = self.row_k = np.zeros(0, dtype=np.int64)
        self.R = int(self.row_mu.size)
        self.mu_mask = mu_mask   # kept for inherited helpers
        self.stream = (self.C >= self.STREAM_AUTO_C) if stream is None else bool(stream)
        self.loop = "streamed" if self.stream else "engine"

    # engine hooks ---------------------------------------------------------
    def row_pair(self, r):
        return int(self.row_mu[r]), int(self.row_k[r])

    def cols_of(self, masks):
        return self.sh.cols_of(np.asarray(masks, dtype=np.uint64))

    def vec(self, masks):
        d = np.zeros((1, self.C), dtype=np.uint8)
        for c in self.cols_of(list(masks)):
            d[0, c] ^= 1
        return self.pack(d)[0]

    def build_M(self, eqs):
        """Packed Macaulay matrix, written equation by equation in row chunks
        (bounded temporary memory even for dense generators)."""
        assert len(eqs) == self.neq
        M = np.zeros((self.R, self.W), dtype=np.uint64)
        budget = 1 << 24    # (row, monomial) pairs per scatter call
        for k, f in enumerate(eqs):
            if not len(f):
                continue
            rows_k = np.flatnonzero(self.row_k == k)
            if not rows_k.size:
                continue
            ms = np.asarray(f, dtype=np.int64)
            step = max(1, budget // ms.size)
            for s0 in range(0, rows_k.size, step):
                rk = rows_k[s0:s0 + step]
                prod = (self.row_mu[rk][:, None] | ms[None, :]).ravel()
                kernels.xor_bits(M, np.repeat(rk, ms.size), self.cols_of(prod))
        return M

    # memory-lean variant of the engine's fixpoint -------------------------
    def _w_closure(self, eqs, want_cert, M0):
        """Identical iteration to Closure._w_closure (same eliminations, same
        new-row rule, same record) when want_cert is False, but the stack
        [basis; products] is allocated once and filled in chunks, and the
        previous stack is released before the next one is allocated. The
        engine's loop holds old stack + basis + product block + the
        np.concatenate copy at once (about 2x the stack), which does not fit
        10 GB at nv = 40. Equality with the engine loop is a unit test."""
        if not self.stream or want_cert:
            return super()._w_closure(eqs, want_cert, M0)
        D, nv = self.D, self.nv
        M = self.build_M(eqs) if M0 is None else M0.copy()
        log = kernels.column_pass(M, self.C, keep_ops=False)
        ps, cs = log.ps.astype(np.int64), log.cs.astype(np.int64)
        del log
        dims = [int(len(ps))]
        one_first = 0 if self.const_col in set(cs.tolist()) else None
        prev_low = set()
        stack_rows = [int(M.shape[0])]
        new_fallen = []
        i = 0
        while True:
            order = np.argsort(cs, kind="stable")
            prow, leads = ps[order], cs[order]
            basis = M[prow]
            del M
            low = self.col_deg[leads] <= D - 1
            lowidx = np.flatnonzero(low)
            new = np.array([t for t in lowidx if int(leads[t]) not in prev_low], dtype=np.int64)
            prev_low = set(int(x) for x in leads[low])
            new_fallen.append(int(new.size))
            nb, nn = basis.shape[0], int(new.size)
            M = np.empty((nb + nv * nn, self.W), dtype=np.uint64)
            M[:nb] = basis
            chunk = max(1, (1 << 27) // (self.W * 8 * nv))      # ~128 MiB of products per call
            for f0 in range(0, nn, chunk):
                f1 = min(nn, f0 + chunk)
                P = self.products(np.ascontiguousarray(basis[new[f0:f1]]))
                c = f1 - f0
                for j in range(nv):
                    M[nb + j * nn + f0: nb + j * nn + f1] = P[j * c:(j + 1) * c]
                del P
            stack_rows.append(int(M.shape[0]))
            log2 = kernels.column_pass(M, self.C, keep_ops=False)
            ps2, cs2 = log2.ps.astype(np.int64), log2.cs.astype(np.int64)
            del log2
            if len(ps2) == dims[-1]:
                final_basis, final_leads = basis, leads
                break
            del basis
            i += 1
            dims.append(int(len(ps2)))
            if one_first is None and self.const_col in set(cs2.tolist()):
                one_first = i
            ps, cs = ps2, cs2
        rec = {
            "iterations_to_fixpoint": i, "dims": dims, "final_dim": dims[-1],
            "one": one_first is not None, "one_first_iteration": one_first,
            "dims_by_deg": [int((self.col_deg[final_leads] <= d).sum()) for d in range(D + 1)],
            "new_fallen_per_iteration": new_fallen, "stack_rows_per_iteration": stack_rows,
        }
        self._final = (final_basis, final_leads)
        return rec, None

    # membership / extraction in the last computed W_D -----------------------
    def member(self, masks):
        basis, leads = self._final
        return reduce_member(basis, leads, self.vec(masks))

    def linear_part(self):
        """Echelon rows of the last W_D with lead degree <= 1, as polynomials
        (lists of masks)."""
        basis, leads = self._final
        out = []
        for t in np.flatnonzero(self.col_deg[leads] <= 1).tolist():
            out.append(self.row_to_masks(basis[t]))
        return out

    def row_to_masks(self, row):
        bits = np.unpackbits(row.view(np.uint8), bitorder="little")[:self.C]
        return sorted(int(self.col_mask[c]) for c in np.flatnonzero(bits))


def reduce_member(basis, leads, v):
    """Is v (packed row) in the span of the echelon basis (lead = lowest set
    column, distinct leads sorted ascending)? Sequential reduction."""
    v = v.copy()
    lead_row = {int(c): t for t, c in enumerate(leads)}
    while True:
        nz = np.flatnonzero(v)
        if nz.size == 0:
            return True
        w = int(nz[0])
        word = int(v[w])
        c = w * 64 + ((word & -word).bit_length() - 1)
        t = lead_row.get(c)
        if t is None:
            return False
        v ^= basis[t]


# --------------------------------------------------------------------------
# instrumentation: per-iteration leading-degree profile (M-4)
# --------------------------------------------------------------------------
@contextlib.contextmanager
def capture(cl: SembinClosure):
    """Record, for every kernels.column_pass call made by an engine closure
    call, the cumulative lead-degree profile (dim W^(i) cap B_{<=d}, d=0..D),
    the rank and the wall time of that elimination. The engine is not
    modified: kernels.column_pass is wrapped for the duration of the call."""
    calls = []
    orig = kernels.column_pass

    def wrapped(M, C, *a, **kw):
        t0 = time.time()
        log = orig(M, C, *a, **kw)
        wall = time.time() - t0
        degs = cl.col_deg[np.asarray(log.cs, dtype=np.int64)]
        by = np.bincount(degs, minlength=cl.D + 1)[:cl.D + 1]
        calls.append({"rank": int(log.K), "dims_by_deg": np.cumsum(by).astype(int).tolist(),
                      "rows": int(M.shape[0]), "wall_s": round(wall, 4)})
        return log

    kernels.column_pass = wrapped
    try:
        yield calls
    finally:
        kernels.column_pass = orig


def w_closure_record(nv: int, D: int, eqs, want_cert: bool = False, deadline_s=None,
                     keep: bool = False, stream=None):
    """Run the engine's W_D fixpoint on eqs. Returns (record, cl) where record
    carries the engine fields plus 'series' (M-4: one entry per iteration;
    entry 0 is M_D) and timings. cl._final holds the echelon basis."""
    cl = SembinClosure(nv, D, eqs, stream=stream)
    t0, c0 = time.time(), time.process_time()
    with capture(cl) as calls:
        rec, cert = cl.w_closure(eqs, want_cert=want_cert, deadline_s=deadline_s)
    rec = dict(rec)
    rec["series"] = calls
    rec["nv"], rec["D"], rec["C"] = nv, D, cl.C
    rec["loop"] = cl.loop
    rec["macaulay_rows"] = cl.R
    rec["wall_s"] = round(time.time() - t0, 4)
    rec["cpu_s"] = round(time.process_time() - c0, 4)
    rec["linear_forms"] = int(rec["dims_by_deg"][1]) if D >= 1 else None
    rec["const_in_W"] = bool(rec["one"])
    return rec, cl


def m_closure_record(nv: int, D: int, eqs):
    """Plain Macaulay space M_D (no mutant steps): engine record + the
    echelon basis for membership tests."""
    cl = SembinClosure(nv, D, eqs)
    M = cl.build_M(eqs)
    Mc = M.copy()
    log = kernels.column_pass(M, cl.C, keep_ops=False)
    ps, cs = log.ps.astype(np.int64), log.cs.astype(np.int64)
    order = np.argsort(cs, kind="stable")
    basis, leads = M[ps[order]], cs[order]
    cl._final = (basis, leads)
    rec = {"rank": int(log.K), "one": bool(cl.const_col in set(cs.tolist())),
           "dims_by_deg": [int((cl.col_deg[leads] <= d).sum()) for d in range(D + 1)]}
    return rec, cl


# --------------------------------------------------------------------------
# containment decision (DER-3)
# --------------------------------------------------------------------------
def decide(N: int, D: int, rec: dict, gb: dict, rank_ev_D: int):
    """M-1 by DER-3: d_GB <= D and dim W_D = dim B_{<=D} - rank(ev_{Z,D}).
    Returns dict(contained, type, deficit)."""
    CD = C_le(N, D)
    dimW = int(rec["final_dim"])
    d_gb = gb["d_GB"]
    deficit = (CD - rank_ev_D) - dimW
    if d_gb > D:
        return {"contained": False, "type": "D", "deficit": deficit, "d_GB": d_gb}
    if deficit == 0:
        return {"contained": True, "type": None, "deficit": 0, "d_GB": d_gb}
    z = gb["z"]
    return {"contained": False, "type": "L" if z == 1 else "G", "deficit": deficit, "d_GB": d_gb}


def gb_membership(cl: SembinClosure, gb_polys, limit: int = 4000):
    """Direct check: is every reduced GB element (deg <= D) in the last W_D?
    Returns (all_in, per-element list) or None if over the limit."""
    if len(gb_polys) > limit:
        return None
    res = []
    for g in gb_polys:
        if poly_degree(g) > cl.D:
            res.append(None)
            continue
        res.append(bool(cl.member(g)))
    return all(r is True for r in res), res


# --------------------------------------------------------------------------
# provenance of the engine
# --------------------------------------------------------------------------
def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def engine_provenance() -> dict:
    d = _paths.GF2_DIR
    files = {}
    for fn in sorted(os.listdir(d)):
        if fn.endswith((".py", ".c")):
            files[f"src/crypto_autoresearcher/gf2/{fn}"] = sha256_file(os.path.join(d, fn))
    from crypto_autoresearcher.gf2 import _native
    kernels.backend()
    return {"closure_py_sha256": files.get("src/crypto_autoresearcher/gf2/closure.py"),
            "files": files, "backend": kernels.backend(), "build_info": dict(_native.build_info)}
