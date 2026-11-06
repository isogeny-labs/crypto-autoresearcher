#!/usr/bin/env python3
"""Tests for check_certs.py.

Everything the checker is tested against is built here by *independent* code:
a log-table field, a truth-table + Moebius-transform derivation of the raw
Weil-descent generators (no symbolic descent), a dense RREF, an integer-bitvector
closure fixpoint with provenance (which also writes the wdag DAGs), and a
nullspace-based reduced Groebner basis.  Nothing from check_certs.py is used to
*build* a test object, only to check it.

Run:  python3 test_check_certs.py            (unit tests; a few seconds to ~1 min)
      python3 test_check_certs.py sweep [--full]   (single-bit-flip sweeps; prints a JSON summary)
Environment: SEMBIN_SAMPLES = directory holding the m3n05/ m3n06/ sample trials.
"""
import gzip
import itertools
import json
import os
import random
import subprocess
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_certs as cc  # noqa: E402

SAMPLES = os.environ.get(
    "SEMBIN_SAMPLES",
    "/tmp/claude-0/-home-user-crypto-autoresearcher/07fcda66-83c3-5bc6-99e7-f81af94fa447/scratchpad/blind_samples")
CLI = os.path.join(HERE, "check_certs.py")


# ===========================================================================
# reference (independent) implementations
# ===========================================================================

def popc(x):
    return bin(x).count("1")


class RefField:
    """F_2[t]/(p) with exp/log tables over a primitive element (found by search)."""

    def __init__(self, n, poly):
        self.n, self.q, self.poly = n, 1 << n, poly
        for g in range(2, self.q):
            e, exp = 1, []
            while True:
                exp.append(e)
                e = self._slow(e, g)
                if e == 1:
                    break
            if len(exp) == self.q - 1:
                self.exp = exp + exp
                self.log = {v: i for i, v in enumerate(exp)}
                return
        raise ValueError("no primitive element: polynomial not irreducible?")

    def _slow(self, a, b):
        prod = 0
        for i in range(self.n):
            if (b >> i) & 1:
                prod ^= a << i
        for bit in range(2 * self.n - 2, self.n - 1, -1):
            if (prod >> bit) & 1:
                prod ^= self.poly << (bit - self.n)
        return prod

    def mul(self, a, b):
        if a == 0 or b == 0:
            return 0
        return self.exp[self.log[a] + self.log[b]]

    def s3(self, x1, x2, x3, B):
        e = self.mul(x1, x2) ^ self.mul(x1, x3) ^ self.mul(x2, x3)
        return self.mul(e, e) ^ self.mul(self.mul(x1, x2), x3) ^ B


def ref_links(F, inst, s):
    n, k, m, v, B, xR = inst["n"], inst["k"], inst["m"], inst["v"], inst["B"], inst["x_R"]
    X = [v[i] ^ ((s >> (i * k)) & ((1 << k) - 1)) for i in range(m)]
    U = [(s >> (m * k + j * n)) & ((1 << n) - 1) for j in range(m - 2)]
    args = [(X[0], X[1], U[0])]
    for j in range(1, m - 2):
        args.append((U[j - 1], X[j + 1], U[j]))
    args.append((U[m - 3], X[m - 1], xR))
    return args


def ref_raw_generators(inst):
    """raw descended generators as sets of monomial masks, from the TRUTH TABLE of the
    field-side S_3 links and a Moebius transform (no symbolic descent)."""
    n, m, k = inst["n"], inst["m"], inst["k"]
    N = m * k + (m - 2) * n
    F = RefField(n, inst["field_poly"])
    M = (m - 1) * n
    tt = np.zeros((M, 1 << N), dtype=np.uint8)
    for s in range(1 << N):
        for l, (x1, x2, x3) in enumerate(ref_links(F, inst, s)):
            val = F.s3(x1, x2, x3, inst["B"])
            for a in range(n):
                tt[l * n + a, s] = (val >> a) & 1
    gens = []
    for g in range(M):
        a = tt[g].copy()
        for i in range(N):
            a = a.reshape(-1, 2, 1 << i)
            a[:, 1, :] ^= a[:, 0, :]
            a = a.reshape(-1)
        gens.append({int(s) for s in np.flatnonzero(a)})
    return gens, N


def ref_Z_field(inst):
    """Z by exhaustive search over field elements (X_i in the cosets, every U_j in F)."""
    n, k, m, v, B, xR = inst["n"], inst["k"], inst["m"], inst["v"], inst["B"], inst["x_R"]
    F = RefField(n, inst["field_poly"])
    out = []
    for xs in itertools.product(*[range(1 << k) for _ in range(m)]):
        X = [v[i] ^ xs[i] for i in range(m)]
        for U in itertools.product(range(1 << n), repeat=m - 2):
            if F.s3(X[0], X[1], U[0], B) != 0:
                continue
            ok = True
            for j in range(1, m - 2):
                if F.s3(U[j - 1], X[j + 1], U[j], B) != 0:
                    ok = False
                    break
            if ok and F.s3(U[m - 3], X[m - 1], xR, B) == 0:
                s = 0
                for i in range(m):
                    s |= xs[i] << (i * k)
                for j in range(m - 2):
                    s |= U[j] << (m * k + j * n)
                out.append(s)
    return sorted(out)


def ref_count_points(inst):
    F = RefField(inst["n"], inst["field_poly"])
    cnt = 1
    for x in range(F.q):
        x3 = F.mul(F.mul(x, x), x)
        rhs = x3 ^ F.mul(inst["A"], F.mul(x, x)) ^ inst["B"]
        for y in range(F.q):
            if F.mul(y, y) ^ F.mul(x, y) == rhs:
                cnt += 1
    return cnt


def make_instance(n, poly, A, B, m, k, v, xR):
    inst = {"n": n, "field_poly": poly, "A": A, "B": B, "m": m, "k": k, "v": list(v), "x_R": xR}
    inst["num_points_E"] = ref_count_points(inst)
    return inst


def find_xR(n, poly, A, B, m, k, v, want_Z):
    """smallest nonzero x_R such that |Z| == want_Z (reference field-level search)."""
    for xR in range(1, 1 << n):
        inst = {"n": n, "field_poly": poly, "A": A, "B": B, "m": m, "k": k, "v": list(v), "x_R": xR}
        if len(ref_Z_field(inst)) == want_Z:
            return xR
    raise ValueError("no x_R")


def ref_serialise(nv, eqs):
    """canonical sembin-sys-v1 bytes written independently."""
    out = []
    for e in eqs:
        monos = sorted(([i for i in range(nv) if (m >> i) & 1] for m in e), key=lambda l: (len(l), l))
        out.append(monos)
    return json.dumps({"eqs": out, "neq": len(out), "nv": nv, "schema": "sembin-sys-v1"},
                      sort_keys=True, separators=(",", ":")).encode()


def ref_rref_sets(polys):
    """dense GF(2) RREF over monomials in descending grevlex (degree, then smaller mask larger)."""
    monos = sorted({m for p in polys for m in p}, key=lambda m: (popc(m), -m), reverse=True)
    col = {m: i for i, m in enumerate(monos)}
    A = np.zeros((len(polys), len(monos)), dtype=np.uint8)
    for r, p in enumerate(polys):
        for m in p:
            A[r, col[m]] = 1
    row = 0
    for c in range(len(monos)):
        piv = [r for r in range(row, len(polys)) if A[r, c]]
        if not piv:
            continue
        A[[row, piv[0]]] = A[[piv[0], row]]
        for r in range(len(polys)):
            if r != row and A[r, c]:
                A[r] ^= A[row]
        row += 1
    return [{monos[c] for c in np.flatnonzero(A[r])} for r in range(row)]


# ---- integer bit-vector linear algebra (lowest set bit = pivot) -----------

def iv_reduce(basis, v):
    while v:
        low = (v & -v).bit_length() - 1
        if low not in basis:
            return v
        v ^= basis[low]
    return 0


def iv_rref(rows):
    basis = {}
    for r in rows:
        r = iv_reduce(basis, r)
        if r:
            basis[(r & -r).bit_length() - 1] = r
    for low in sorted(basis, reverse=True):          # fully reduce, high pivots first is fine
        pass
    for low in sorted(basis):
        v = basis[low]
        for other in sorted(basis):
            if other != low and (v >> other) & 1:
                v ^= basis[other]
        basis[low] = v
    # second pass guarantees reducedness (pivots processed ascending can re-introduce)
    changed = True
    while changed:
        changed = False
        for low in basis:
            for other in basis:
                if other != low and (basis[low] >> other) & 1:
                    basis[low] ^= basis[other]
                    changed = True
    return basis


def iv_nullspace(rows, C):
    """basis of {x in F_2^C : parity(x & row) = 0 for every row}."""
    R = iv_rref(rows)
    piv = set(R)
    out = []
    for f in range(C):
        if f in piv:
            continue
        x = 1 << f
        for p, vec in R.items():
            if (vec >> f) & 1:
                x |= 1 << p
        out.append(x)
    return out


def ref_cols(nv, D):
    masks = []
    for d in range(min(D, nv), -1, -1):
        masks += sorted(sum(1 << i for i in c) for c in itertools.combinations(range(nv), d))
    return masks


def mono_list(mask):
    return [i for i in range(mask.bit_length()) if (mask >> i) & 1]


class RefClosure:
    """W_D by the fixpoint iteration, with provenance, over python-int bit vectors."""

    def __init__(self, eqs, nv, D):
        self.eqs, self.nv, self.D = eqs, nv, D
        self.masks = ref_cols(nv, D)
        self.col = {m: i for i, m in enumerate(self.masks)}
        self.C = len(self.masks)
        self.n_top = sum(1 for m in self.masks if popc(m) == D)
        self.nodes = []
        self.basis = {}                   # low -> [vec, terms, node_id|None]
        for k, f in enumerate(eqs):
            if not f:
                continue
            dk = max(popc(m) for m in f)
            for d in range(0, D - dk + 1):
                for c in itertools.combinations(range(nv), d):
                    mu = sum(1 << i for i in c)
                    vec = 0
                    for m in f:
                        vec ^= 1 << self.col[m | mu]
                    self.add(vec, {("r", mu, k)})
        self.levels = 0
        changed = True
        while changed:
            changed = False
            self.levels += 1
            for low in sorted(self.basis):
                if low < self.n_top:
                    continue                      # leading degree D: not in B_{<=D-1}
                ent = self.basis[low]
                nid = self.node_of(ent)
                for j in range(nv):
                    if self.add(self.shift(ent[0], j), {("p", j, nid)}):
                        changed = True

    def shift(self, vec, j):
        out = 0
        c = 0
        while vec >> c:
            if (vec >> c) & 1:
                out ^= 1 << self.col[self.masks[c] | (1 << j)]
            c += 1
        return out

    def add(self, vec, terms):
        terms = set(terms)
        vec, terms = self.red(vec, terms)
        if vec:
            self.basis[(vec & -vec).bit_length() - 1] = [vec, terms, None]
            return True
        return False

    def red(self, vec, terms):
        terms = set(terms)
        while vec:
            low = (vec & -vec).bit_length() - 1
            b = self.basis.get(low)
            if b is None:
                break
            vec ^= b[0]
            terms ^= b[1]
        return vec, terms

    def node_of(self, ent):
        if ent[2] is None:
            ent[2] = self._make_node(ent[1])
        return ent[2]

    def _make_node(self, terms):
        rows = sorted([mono_list(t[1]), t[2]] for t in terms if t[0] == "r")
        prods = sorted([t[1], t[2]] for t in terms if t[0] == "p")
        self.nodes.append({"id": len(self.nodes), "rows": rows, "prods": prods})
        return len(self.nodes) - 1

    def vec(self, poly_masks):
        v = 0
        for m in poly_masks:
            v ^= 1 << self.col[m]
        return v

    def contains(self, poly_masks):
        return self.red(self.vec(poly_masks), set())[0] == 0

    def output_node(self, poly_masks):
        vec, terms = self.red(self.vec(poly_masks), set())
        assert vec == 0, "target not in W_D"
        return self._make_node(terms)

    def basis_vectors(self):
        return [e[0] for _, e in sorted(self.basis.items())]


def ref_gb(Z, nv, D):
    """reduced GB elements of degree <= D: (lm_mask, set(masks)), by nullspace of the evaluation
    matrix and an RREF in descending-grevlex column order (pivot = lowest set bit)."""
    masks = ref_cols(nv, D)
    C = len(masks)
    ev_rows = []
    for z in Z:
        v = 0
        for c, mk in enumerate(masks):
            if z & mk == mk:
                v |= 1 << c
        ev_rows.append(v)
    R = iv_rref(iv_nullspace(ev_rows, C))                # I(Z) cap B_{<=D}, reduced
    piv_masks = {low: masks[low] for low in R}
    out = []
    for low, vec in sorted(R.items()):
        lm = masks[low]
        if any(o != lm and (o & lm) == o for o in piv_masks.values()):
            continue                                      # LM divisible by another LM -> not in the reduced GB
        out.append((lm, {masks[c] for c in range(C) if (vec >> c) & 1}))
    return out


# ---- certificate builders --------------------------------------------------

def sys_bytes_of(nv, eqs):
    return ref_serialise(nv, eqs)


def gz(b):
    return gzip.compress(b, mtime=0)


def hexlist(zs):
    return [format(z, "x") for z in zs]


def poly_json(masks):
    return sorted(([mono_list(m) for m in masks]), key=lambda l: (len(l), l))


def common_fields(schema, D, nv, eqs, sysb):
    import hashlib
    return {"schema": schema, "D": D, "nv": nv, "neq": len(eqs), "system_sha256": hashlib.sha256(sysb).hexdigest()}


def build_ann(eqs, nv, D, Z, inst=None, form="dual", pick=0):
    cl = RefClosure(eqs, nv, D)
    gb = [(lm, el) for lm, el in ref_gb(Z, nv, D) if not cl.contains(el)]
    if not gb:
        return None
    lm, g = gb[pick % len(gb)]
    sysb = sys_bytes_of(nv, eqs)
    cert = common_fields("sembin-ann-v1", D, nv, eqs, sysb)
    cert["form"] = form
    if form == "dual":
        cert["L_hex"] = hexlist(iv_nullspace(cl.basis_vectors(), cl.C))
    else:
        cert["basis_hex"] = hexlist(cl.basis_vectors())
    cert["g"] = poly_json(g)
    cert["g_gb_index"] = pick
    cert["Z"] = hexlist(Z)
    if inst is not None:
        cert["instance"] = inst
    return cert, sysb, cl, g


def build_wdag(eqs, nv, D, Z, inst=None):
    cl = RefClosure(eqs, nv, D)
    gb = ref_gb(Z, nv, D)
    # the reduced GB may have elements above degree D; containment needs all of them in B_{<=D}
    # so first make sure the truncated GB really is the whole GB: |std monomials| == |Z|
    lms = [lm for lm, _ in gb]
    if cc.count_standard_monomials(lms, nv, len(Z)) != len(Z):
        return None
    if any(not cl.contains(el) for _, el in gb):
        return None
    outs = [cl.output_node(el) for _, el in gb]
    sysb = sys_bytes_of(nv, eqs)
    cert = common_fields("sembin-wdag-v1", D, nv, eqs, sysb)
    cert.update({"nodes": cl.nodes, "outputs": outs, "targets": [poly_json(el) for _, el in gb],
                 "Z": hexlist(Z), "levels": cl.levels})
    if inst is not None:
        cert["instance"] = inst
    return cert, sysb, cl


def jb(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def run(sysb, cert, **opts):
    cb = cert if isinstance(cert, bytes) else jb(cert)
    return cc.run_check(sysb, cb, cc.Options(**opts))


def eqs_from_instance(inst):
    """serialised system as the spec defines it: RREF of the raw generators (reference code)."""
    gens, N = ref_raw_generators(inst)
    return ref_rref_sets(gens), N, gens


# ---- fixed test instances (own parameters, not the samples') -----------------

_INSTANCE_CACHE = {}


def get_instance(name):
    if name in _INSTANCE_CACHE:
        return _INSTANCE_CACHE[name]
    spec = {
        # name: (n, poly, A, B, m, k, v, want_Z)
        "i4":   (4, 19, 0, 3, 3, 1, [2, 4, 8], 2),
        "i4e":  (4, 19, 1, 6, 3, 1, [2, 4, 8], 0),
        "i5":   (5, 37, 0, 11, 3, 1, [2, 4, 8], 1),
        "i5z":  (5, 37, 1, 7, 3, 1, [2, 4, 8], 2),
        "i6":   (6, 67, 1, 13, 3, 2, [8, 17, 33], 2),
        "eqs2": (5, 37, 1, 7, 3, 1, [0, 0, 0], 1),
        "m4":   (5, 37, 0, 9, 4, 1, [2, 4, 8, 16], 1),
    }[name]
    n, poly, A, B, m, k, v, wz = spec
    xR = find_xR(n, poly, A, B, m, k, v, wz)
    inst = make_instance(n, poly, A, B, m, k, v, xR)
    eqs, N, gens = eqs_from_instance(inst)
    Z = ref_Z_field(inst)
    _INSTANCE_CACHE[name] = (inst, eqs, N, gens, Z)
    return _INSTANCE_CACHE[name]
