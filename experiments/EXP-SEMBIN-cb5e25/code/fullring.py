"""Full-ring closures for EQS4-FULLFE / EQS4-NOFE (C-FE-EQ, C-FE-OUT), N <= 20.

The ring is F_2[X_1..X_N] (squares allowed). W_D^full is the same fixpoint as
DC-1 in the full ring: W^(0) = M_D^full, W^(i+1) = W^(i) + sum_j X_j *
(W^(i) cap B_{<=D-1}). Elimination and the X_j-product use the shared engine
kernels (kernels.column_pass, kernels.products) with full-ring column maps;
the monomial bookkeeping is written here. Columns: non-multilinear monomials
first (so that rows whose lead is a multilinear column span W cap B), then
multilinear monomials in the engine order.
"""
from __future__ import annotations

from itertools import combinations, combinations_with_replacement
from math import comb

import numpy as np

import _paths  # noqa: F401
from crypto_autoresearcher.gf2 import kernels


def _mono_of_mask(mask):
    out, i = [], 0
    while mask:
        if mask & 1:
            out.append(i)
        mask >>= 1
        i += 1
    return tuple(out)


class FullRing:
    def __init__(self, nv: int, D: int):
        self.nv, self.D = nv, D
        cols = []
        for d in range(D, -1, -1):
            non, multi = [], []
            for c in combinations_with_replacement(range(nv), d):
                (multi if len(set(c)) == len(c) else non).append(c)
            multi.sort(key=lambda c: sum(1 << i for i in c))
            non.sort()
            cols += non + multi          # degree-compatible: lead degree = degree
        self.cols = cols
        self.C = len(self.cols)
        self.W = (self.C + 63) // 64
        self.index = {c: i for i, c in enumerate(self.cols)}
        self.col_deg = np.array([len(c) for c in self.cols], dtype=np.int64)
        self.is_multi = np.array([len(set(c)) == len(c) for c in self.cols])
        self.const_col = self.index[()]
        # product maps for kernels.products
        low = np.flatnonzero(self.col_deg <= D - 1)
        self.colmap = np.full((nv, self.C), -1, dtype=np.int32)
        self.maps = []
        for j in range(nv):
            tA = np.array([self.index[tuple(sorted(self.cols[c] + (j,)))] for c in low], dtype=np.int64)
            self.colmap[j, low] = tA
            self.maps.append((low.copy(), tA, np.zeros(0, dtype=np.int64)))

    def poly_cols(self, poly):
        """poly: iterable of monomial tuples -> list of columns (XOR-counted)."""
        acc = {}
        for m in poly:
            c = self.index[tuple(sorted(m))]
            acc[c] = acc.get(c, 0) ^ 1
        return [c for c, p in acc.items() if p]

    def build_M(self, gens):
        rows_r, rows_c = [], []
        r = 0
        for f in gens:
            e = max((len(m) for m in f), default=-1)
            if e < 0 or e > self.D:
                continue
            for d in range(0, self.D - e + 1):
                for t in combinations_with_replacement(range(self.nv), d):
                    acc = {}
                    for m in f:
                        c = self.index[tuple(sorted(m + t))]
                        acc[c] = acc.get(c, 0) ^ 1
                    for c, p in acc.items():
                        if p:
                            rows_r.append(r)
                            rows_c.append(c)
                    r += 1
        M = np.zeros((r, self.W), dtype=np.uint64)
        if rows_r:
            kernels.xor_bits(M, np.array(rows_r, dtype=np.int64), np.array(rows_c, dtype=np.int64))
        return M


def full_ring_closure(nv: int, D: int, gens, with_fe: bool):
    """gens: list of multilinear generators as mask lists. Returns record."""
    fr = FullRing(nv, D)
    polys = [[_mono_of_mask(m) for m in g] for g in gens]
    if with_fe:
        polys += [[(i, i), (i,)] for i in range(nv)]
    M = fr.build_M(polys)
    log = kernels.column_pass(M, fr.C, keep_ops=False)
    ps, cs = log.ps.astype(np.int64), log.cs.astype(np.int64)
    dims = [int(len(ps))]
    prev_low = set()
    while True:
        order = np.argsort(cs, kind="stable")
        prow, leads = ps[order], cs[order]
        basis = M[prow]
        low = fr.col_deg[leads] <= D - 1
        lowidx = np.flatnonzero(low)
        new = np.array([t for t in lowidx if int(leads[t]) not in prev_low], dtype=np.int64)
        prev_low = set(int(x) for x in leads[low])
        P = kernels.products(np.ascontiguousarray(basis[new]), fr.colmap, fr.maps, nv, fr.C, fr.W)
        M = np.concatenate([basis, P])
        del P
        log2 = kernels.column_pass(M, fr.C, keep_ops=False)
        ps2, cs2 = log2.ps.astype(np.int64), log2.cs.astype(np.int64)
        if len(ps2) == dims[-1]:
            final_leads = leads
            final_basis = basis
            break
        dims.append(int(len(ps2)))
        ps, cs = ps2, cs2
    # W cap B: re-eliminate the final basis with non-multilinear columns first
    bits = np.unpackbits(final_basis.view(np.uint8).reshape(final_basis.shape[0], fr.W * 8),
                         axis=1, bitorder="little")[:, :fr.C]
    nonidx = np.flatnonzero(~fr.is_multi)
    multiidx = np.flatnonzero(fr.is_multi)
    # engine order inside the multilinear part: degree desc, mask asc (already so in fr.cols)
    perm = np.concatenate([nonidx, multiidx])
    pb = bits[:, perm]
    n_non = len(nonidx)
    pad = fr.W * 64 - fr.C
    pp = np.packbits(np.concatenate([pb, np.zeros((pb.shape[0], pad), np.uint8)], axis=1),
                     axis=1, bitorder="little")
    pp = np.ascontiguousarray(pp).view(np.uint64).reshape(pb.shape[0], fr.W).copy()
    plog = kernels.column_pass(pp, fr.C, keep_ops=False)
    pcs = plog.cs.astype(np.int64)
    mcs = pcs[pcs >= n_non]                      # leads inside the multilinear block
    mdeg = fr.col_deg[perm[mcs]]
    by_deg = [int((mdeg <= d).sum()) for d in range(D + 1)]
    multi_lead = np.ones(len(mcs), dtype=bool)
    # rho(W): map every column to its multilinear reduction
    red = np.empty(fr.C, dtype=np.int64)
    for c, mono in enumerate(fr.cols):
        red[c] = fr.index[tuple(sorted(set(mono)))]
    rho = np.zeros_like(bits)
    for c in range(fr.C):
        rho[:, red[c]] ^= bits[:, c]
    rb = np.packbits(np.concatenate([rho, np.zeros((rho.shape[0], pad), np.uint8)], axis=1),
                     axis=1, bitorder="little")
    rb = np.ascontiguousarray(rb).view(np.uint64).reshape(rho.shape[0], fr.W).copy()
    rlog = kernels.column_pass(rb, fr.C, keep_ops=False)
    rcs = rlog.cs.astype(np.int64)
    one = bool(fr.const_col in set(final_leads.tolist()))
    return {
        "nv": nv, "D": D, "with_fe": with_fe, "C_full": fr.C, "final_dim_full": int(len(final_leads)),
        "dims": dims, "multilinear_part_dim": int(len(mcs)),
        "multilinear_part_dims_by_deg": by_deg, "rho_rank": int(rlog.K),
        "rho_dims_by_deg": [int((fr.col_deg[rcs] <= d).sum()) for d in range(D + 1)],
        "linear_forms": by_deg[1], "one_in_W": one,
    }
