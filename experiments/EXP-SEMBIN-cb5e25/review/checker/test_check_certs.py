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


# ===========================================================================
# oracles used to classify single-bit flips
# ===========================================================================

def ann_truly_sound(cert, cl, Z, nv, D):
    """Independent soundness oracle for an ann certificate (dual or primal):
    W_D is inside U, g is in the reduced GB of I(Z), and g is outside U."""
    try:
        C = cl.C
        if cert.get("form") == "dual":
            Ls = [int(h, 16) for h in cert["L_hex"]]
            if any(x.bit_length() > C for x in Ls):
                return False
            if any(popc(x & w) & 1 for x in Ls for w in cl.basis_vectors()):
                return False
            gm = {sum(1 << i for i in mono) for mono in cert["g"]}
            gv = cl.vec(gm)
            if not any(popc(x & gv) & 1 for x in Ls):
                return False
        else:
            Bs = [int(h, 16) for h in cert["basis_hex"]]
            if any(x.bit_length() > C for x in Bs):
                return False
            ech = {}
            for b in Bs:
                b = iv_reduce(ech, b)
                if b:
                    ech[(b & -b).bit_length() - 1] = b
            if any(iv_reduce(ech, w) for w in cl.basis_vectors()):
                return False
            gm = {sum(1 << i for i in mono) for mono in cert["g"]}
            if iv_reduce(ech, cl.vec(gm)) == 0:
                return False
        gb = {frozenset(el) for _, el in ref_gb(Z, nv, D)}
        return frozenset(gm) in gb
    except Exception:
        return False


def wdag_truly_sound(cert, cl, Z, nv, D):
    """targets lie in W_D (closure oracle) and form a GB of I(Z) (explicit count over all 2^nv masks)."""
    try:
        T = [{sum(1 << i for i in mono) for mono in t} for t in cert["targets"]]
        if not T or any(not t for t in T):
            return False
        if any(not cl.contains(t) for t in T):
            return False
        for t in T:
            for z in Z:
                if sum(1 for m in t if z & m == m) & 1:
                    return False
        lms = [max(t, key=lambda m: (popc(m), -m)) for t in T]
        std = sum(1 for m in range(1 << nv) if not any(m & l == l for l in lms))
        return std == len(Z)
    except Exception:
        return False


def leaf_paths(a, b, path=()):
    """paths where two JSON values differ (lists are compared index-wise)."""
    if type(a) is not type(b):
        return [path]
    if isinstance(a, dict):
        out = []
        for k in set(a) | set(b):
            if k not in a or k not in b:
                out.append(path + (k,))
            else:
                out += leaf_paths(a[k], b[k], path + (k,))
        return out
    if isinstance(a, list):
        if len(a) != len(b):
            return [path]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += leaf_paths(x, y, path + (i,))
        return out
    return [] if a == b else [path]


INFORMATIONAL = {("levels",), ("g_gb_index",)}


def flip_bytes(data, i, b):
    ba = bytearray(data)
    ba[i] ^= 1 << b
    return bytes(ba)


def reachable_nodes(cert_obj):
    if "outputs" not in cert_obj:
        return None
    reach, stack = set(cert_obj["outputs"]), list(set(cert_obj["outputs"]))
    while stack:
        for _j, c in cert_obj["nodes"][stack.pop()]["prods"]:
            if c not in reach:
                reach.add(c)
                stack.append(c)
    return reach


def only_unreferenced_nodes(cert_obj, diff):
    reach = reachable_nodes(cert_obj)
    if reach is None or not diff:
        return False
    return all(len(p) >= 2 and p[0] == "nodes" and isinstance(p[1], int) and p[1] not in reach for p in diff)


def classify_text_flip(sysb, cert_obj, orig_bytes, i, b, oracle, opts):
    """run the checker on a single bit flip of the certificate JSON text.
    returns one of: rejected_malformed, rejected_check, accepted_informational,
    accepted_semantic_sound, ACCEPTED_UNSOUND"""
    fb = flip_bytes(orig_bytes, i, b)
    res = cc.run_check(sysb, fb, opts)
    if res["verdict"] == "error":
        return "ERROR:" + res.get("error", "")
    if res["verdict"] == "reject":
        return "rejected_malformed" if "malformed" in res else "rejected_check"
    try:
        flipped = json.loads(fb.decode())
    except Exception:
        return "ACCEPTED_UNSOUND(unparseable)"
    diff = leaf_paths(cert_obj, flipped)
    if all(tuple(p) in INFORMATIONAL for p in diff):
        return "accepted_informational"
    if only_unreferenced_nodes(cert_obj, diff):
        return "accepted_unreferenced_node" if oracle(flipped) else "ACCEPTED_UNSOUND"
    return "accepted_semantic_sound" if oracle(flipped) else "ACCEPTED_UNSOUND"


def summarise(classes):
    from collections import Counter
    c = Counter(classes)
    return {"flips": len(classes), **dict(sorted(c.items()))}


def _worker(args):
    sysb, cert_obj, orig_bytes, i, b, kind, ctxkey, optkw = args
    oracle = _ORACLES[ctxkey]()
    return classify_text_flip(sysb, cert_obj, orig_bytes, i, b, oracle, cc.Options(**optkw))


_ORACLES = {}


# ===========================================================================
# samples
# ===========================================================================

def sample(cell):
    d = os.path.join(SAMPLES, cell)
    sp = os.path.join(d, "systems", f"{cell}_EQS4_r0.sys.json.gz")
    cp = os.path.join(d, "certificates", f"{cell}_EQS4_r0.D4.wdag.json.gz")
    ip = os.path.join(d, "instances.jsonl.gz")
    if not (os.path.exists(sp) and os.path.exists(cp)):
        return None
    return sp, cp, ip


def read(path):
    data, _ = cc.read_maybe_gz(path)
    return data


def write_bytes(path, data):
    with open(path, "wb") as f:
        f.write(data)


def cli(*args):
    p = subprocess.run([sys.executable, "-I", CLI, *args], capture_output=True, text=True)
    return p.returncode, (json.loads(p.stdout) if p.stdout.strip().startswith("{") else None), p.stderr


# ===========================================================================
# unit tests
# ===========================================================================

class TestPrimitives(unittest.TestCase):
    def test_field_ops_against_log_table_field(self):
        rnd = random.Random(1)
        for n, poly in ((5, 37), (6, 67), (7, 131), (4, 19)):
            F, R = cc.GF(n, poly), RefField(n, poly)
            for _ in range(200):
                a, b = rnd.randrange(1 << n), rnd.randrange(1 << n)
                self.assertEqual(F.mul(a, b), R.mul(a, b))
                self.assertEqual(F.sq(a), R.mul(a, a))
                if a:
                    self.assertEqual(F.mul(a, F.inv(a)), 1)
                self.assertEqual(F.sq(F.sqrt(a)), a)

    def test_roots_third_matches_exhaustive_search(self):
        rnd = random.Random(2)
        for n, poly in ((4, 19), (5, 37), (6, 67)):
            F, R = cc.GF(n, poly), RefField(n, poly)
            for _ in range(150):
                x1, x2, B = rnd.randrange(1 << n), rnd.randrange(1 << n), rnd.randrange(2, 1 << n)
                want = sorted(u for u in range(1 << n) if R.s3(x1, x2, u, B) == 0)
                self.assertEqual(sorted(F.roots_third(x1, x2, B)), want, (n, x1, x2, B))
        # degenerate leading coefficient / zero arguments
        F, R = cc.GF(5, 37), RefField(5, 37)
        for x1, x2 in ((0, 0), (0, 5), (5, 0), (7, 7), (1, 1)):
            for B in (2, 9, 31):
                want = sorted(u for u in range(32) if R.s3(x1, x2, u, B) == 0)
                self.assertEqual(sorted(F.roots_third(x1, x2, B)), want)

    def test_irreducibility(self):
        self.assertTrue(cc.is_irreducible(37) and cc.is_irreducible(67) and cc.is_irreducible(19))
        self.assertFalse(cc.is_irreducible(0b100001))   # t^5+1 = (t+1)(...)
        self.assertFalse(cc.is_irreducible(0b10100))    # no constant term
        with self.assertRaises(cc.Malformed):
            cc.GF(5, 0b100011)                          # t^5+t+1 = (t^2+t+1)(t^3+t^2+1)

    def test_gf2_rref_and_nullspace(self):
        rnd = np.random.RandomState(3)
        for nr, nc in ((5, 9), (20, 70), (3, 130), (60, 40)):
            M = (rnd.rand(nr, nc) < 0.3).astype(np.uint8)
            R, piv = cc.gf2_rref(M)
            ints = [sum(int(b) << c for c, b in enumerate(row)) for row in M]
            ref = iv_rref(ints)
            self.assertEqual(sorted(ref), piv)
            for r, p in zip(R, piv):
                self.assertEqual(sum(int(b) << c for c, b in enumerate(r)), ref[p])
            K = cc.gf2_nullspace_from_rref(R, piv, nc)
            self.assertEqual(K.shape[0], nc - len(piv))
            self.assertFalse(((M.astype(int) @ K.T.astype(int)) & 1).any())

    def test_bruteforce_vs_naive_with_small_chunks(self):
        rnd = random.Random(4)
        for nv in (1, 3, 5, 6, 7, 9):
            for _ in range(8):
                eqs = []
                for _e in range(rnd.randrange(1, 5)):
                    ms = {rnd.getrandbits(nv) & rnd.getrandbits(nv) & rnd.getrandbits(nv) for _ in range(rnd.randrange(1, 7))}
                    eqs.append(np.array(sorted(ms), dtype=np.int64))
                naive = [s for s in range(1 << nv)
                         if all(sum(1 for m in e.tolist() if s & m == m) % 2 == 0 for e in eqs)]
                for lb in (2, 4, 16):
                    self.assertEqual(cc.bruteforce_Z(nv, eqs, low_bits=lb), naive)

    def test_columns_and_index(self):
        for nv, D in ((5, 3), (4, 6), (7, 2)):
            cs = cc.ColSpace(D, nv)
            self.assertEqual(cs.masks.tolist(), ref_cols(nv, D))
            self.assertEqual(cs.n_top, sum(1 for m in ref_cols(nv, D) if popc(m) == D))
            sel = np.array(ref_cols(nv, D)[::3], dtype=np.int64)
            self.assertEqual(cs.index(sel).tolist(), list(range(0, cs.C, 3)))
        with self.assertRaises(cc.Malformed):
            cc.ColSpace(2, 5).index(np.array([7], dtype=np.int64))      # degree 3 > D

    def test_reduced_gb_and_standard_count_vs_reference(self):
        rnd = random.Random(5)
        for nv in (4, 6, 7):
            for _ in range(10):
                Z = sorted(rnd.sample(range(1 << nv), rnd.randrange(0, 6)))
                ref = ref_gb(Z, nv, nv)               # full reduced GB (degree <= nv)
                lms = {lm for lm, _ in ref}
                got = cc.reduced_gb_elements(Z, nv, lms | {rnd.getrandbits(nv)})
                for lm, el in ref:
                    self.assertEqual(got[lm], el)
                self.assertEqual(cc.count_standard_monomials(list(lms), nv, 1 << nv), len(Z))
                # a non-minimal / standard monomial is not a GB leading monomial
                for m in range(1 << nv):
                    if m not in lms:
                        self.assertIsNone(cc.reduced_gb_elements(Z, nv, {m})[m])

    def test_rref_grevlex_vs_dense(self):
        rnd = random.Random(6)
        for _ in range(20):
            nv = 7
            polys = [{rnd.getrandbits(nv) & rnd.getrandbits(nv) for _ in range(rnd.randrange(0, 9))} for _ in range(6)]
            self.assertEqual(cc.rref_grevlex(polys), ref_rref_sets(polys))


class TestDescentAndZ(unittest.TestCase):
    def test_symbolic_descent_equals_truth_table_anf_and_rref_equals_reference(self):
        for name in ("i4", "i4e", "i5", "i5z", "i6", "eqs2", "m4"):
            inst, eqs, N, gens, Z = get_instance(name)
            I = cc.validate_instance(inst)
            mine, nv, F = cc.descend(I)
            self.assertEqual(nv, N)
            self.assertEqual(mine, gens, name)
            self.assertEqual(cc.rref_grevlex(mine), eqs, name)
            self.assertEqual(cc.numeric_descent_selfcheck(I, mine, F), 0)

    def test_sample_systems_match_producers_hashes_from_independent_derivation(self):
        for cell in ("m3n05", "m3n06"):
            s = sample(cell)
            if s is None:
                self.skipTest("samples not available")
            sp, cp, ip = s
            rec = json.loads(gzip.open(ip, "rt").readline())
            inst = rec["meta"]
            gens, N = ref_raw_generators(inst)                       # truth table + Moebius
            self.assertEqual(__import__("hashlib").sha256(ref_serialise(N, gens)).hexdigest(),
                             rec["raw_system_sha256"])
            eqs = ref_rref_sets(gens)
            self.assertEqual(__import__("hashlib").sha256(ref_serialise(N, eqs)).hexdigest(),
                             rec["system_sha256"])
            self.assertEqual(ref_serialise(N, eqs), read(sp))      # byte-identical to the stored file
            self.assertEqual(sorted(ref_Z_field(inst)), sorted(int(h, 16) for h in rec["Z_hex"]))

    def test_chain_equals_bruteforce_equals_field_search(self):
        for name in ("i4", "i4e", "i5", "i5z", "i6", "eqs2", "m4"):
            inst, eqs, N, gens, Z = get_instance(name)
            I = cc.validate_instance(inst)
            self.assertEqual(cc.chain_Z(I), Z, name)
            sysd = cc.parse_system(ref_serialise(N, eqs))
            self.assertEqual(cc.bruteforce_Z(N, sysd.eqs), Z, name)

    def test_shift_validation(self):
        base = get_instance("i5")[0]
        self.assertTrue(cc.shifts_ok(cc.validate_instance(base))[0])
        bad = dict(base, v=[2, 4, 3])                 # 2 xor 3 = 1 < 2^k
        self.assertFalse(cc.shifts_ok(cc.validate_instance(bad))[0])
        bad = dict(base, v=[1, 4, 8])                 # v_1 < 2^k
        self.assertFalse(cc.shifts_ok(cc.validate_instance(bad))[0])
        self.assertTrue(cc.shifts_ok(cc.validate_instance(dict(base, v=[0, 0, 0])))[0])


class TestSamples(unittest.TestCase):
    def setUp(self):
        self.samples = [sample(c) for c in ("m3n05", "m3n06")]
        if any(s is None for s in self.samples):
            self.skipTest("sample directory not found (set SEMBIN_SAMPLES)")

    def test_cli_accepts_both_sample_wdag_certificates(self):
        for sp, cp, ip in self.samples:
            code, res, err = cli("--system", sp, "--cert", cp, "--z-bruteforce", "--instances", ip)
            self.assertEqual(code, 0, (res or err))
            self.assertEqual(res["verdict"], "accept")
            self.assertEqual(res["failed_checks"], [])
            self.assertIn("bruteforce", res["Z_methods"])
            self.assertIn("chain", res["Z_methods"])
            self.assertTrue(res["info"]["targets_are_reduced_gb"])

    def test_cli_default_options_accept(self):
        for sp, cp, ip in self.samples:
            code, res, _ = cli("--system", sp, "--cert", cp)
            self.assertEqual(code, 0)

    def test_expected_hash_option(self):
        sp, cp, ip = self.samples[0]
        sysd = cc.parse_system(read(sp))
        code, res, _ = cli("--system", sp, "--cert", cp, "--expect-system-sha256", sysd.sha256)
        self.assertEqual(code, 0)
        code, res, _ = cli("--system", sp, "--cert", cp, "--expect-system-sha256", "0" * 64)
        self.assertEqual(code, 1)
        self.assertIn("system_expected_hash", res["failed_checks"])

    def test_cross_wiring_samples_is_rejected(self):
        (s5, c5, _), (s6, c6, _) = self.samples
        code, res, _ = cli("--system", s5, "--cert", c6)
        self.assertEqual(code, 1)
        code, res, _ = cli("--system", s6, "--cert", c5)
        self.assertEqual(code, 1)

    def test_io_errors_exit_2(self):
        sp, cp, _ = self.samples[0]
        code, res, _ = cli("--system", sp + ".nope", "--cert", cp)
        self.assertEqual(code, 2)


class TestOnProducerSystems(unittest.TestCase):
    """my own certificates, built by the reference code, for the producer's serialised systems"""

    def setUp(self):
        if any(sample(c) is None for c in ("m3n05", "m3n06")):
            self.skipTest("sample directory not found (set SEMBIN_SAMPLES)")

    def test_closure_dims_match_producer_records_and_ann_certificates_accepted(self):
        for cell in ("m3n05", "m3n06"):
            sp, cp, ip = sample(cell)
            sysb = read(sp)
            sysd = cc.parse_system(sysb)
            eqs = [set(a.tolist()) for a in sysd.eqs]
            rec = json.loads(gzip.open(ip, "rt").readline())
            inst = dict(rec["meta"])
            Z = sorted(int(h, 16) for h in rec["Z_hex"])
            closures = [json.loads(l) for l in gzip.open(os.path.join(os.path.dirname(ip), "closures.jsonl.gz"), "rt")]
            for r in closures:
                if "D" not in r or r["D"] > 4:
                    continue
                D = r["D"]
                cl = RefClosure(eqs, sysd.nv, D)
                lead = [popc(cl.masks[low]) for low in cl.basis]
                self.assertEqual([sum(1 for x in lead if x <= d) for d in range(D + 1)], r["engine"]["dims_by_deg"])
                gb = ref_gb(Z, sysd.nv, D)
                contained = all(cl.contains(el) for _, el in gb)
                self.assertEqual(contained, r["M1"]["contained"])
                if not contained:
                    for form in ("dual", "primal"):
                        cert, _, _, g = build_ann(eqs, sysd.nv, D, Z, inst, form)
                        res = run(sysb, cert, z_bruteforce=True, instances=ip)
                        self.assertEqual(res["verdict"], "accept", (cell, D, form, res["failed_checks"]))
                else:
                    cert, _, _ = build_wdag(eqs, sysd.nv, D, Z, inst)
                    res = run(sysb, cert, z_bruteforce=True, instances=ip)
                    self.assertEqual(res["verdict"], "accept", (cell, D, res["failed_checks"]))


class TestOwnCertificates(unittest.TestCase):
    def test_ann_dual_and_primal_accepted_at_D2_for_all_instances(self):
        for name in ("i4", "i4e", "i5", "i5z", "i6", "eqs2", "m4"):
            inst, eqs, N, gens, Z = get_instance(name)
            for form in ("dual", "primal"):
                built = build_ann(eqs, N, 2, Z, inst, form)
                self.assertIsNotNone(built, name)
                cert, sysb, cl, g = built
                res = run(sysb, cert, z_bruteforce=True)
                self.assertEqual(res["verdict"], "accept", (name, form, res.get("failed_checks"), res.get("malformed")))
                self.assertEqual(res["Z_size"], len(Z))

    def test_ann_noncontainment_at_D3_for_larger_cells(self):
        for name in ("i6", "m4"):
            inst, eqs, N, gens, Z = get_instance(name)
            for form in ("dual", "primal"):
                cert, sysb, cl, g = build_ann(eqs, N, 3, Z, inst, form)
                res = run(sysb, cert)
                self.assertEqual(res["verdict"], "accept", (name, form, res["failed_checks"]))
                # both closure routes of the dual closure check agree
        inst, eqs, N, gens, Z = get_instance("i6")
        cert, sysb, cl, g = build_ann(eqs, N, 3, Z, inst, "dual")
        cs = cc.ColSpace(3, N)
        Lam = np.array([[(int(h, 16) >> c) & 1 for c in range(cs.C)] for h in cert["L_hex"]], dtype=np.uint8)
        for route in ("rowspace", "nullspace", None):
            self.assertTrue(cc.dual_check_b(Lam, cs, N, route=route)[0])
        # not closed: annihilator of M_D only
        Mrows = [r for r in _macaulay_ints(eqs, N, 3, cl)]
        Lm = iv_nullspace(Mrows, cl.C)
        Lam2 = np.array([[(x >> c) & 1 for c in range(cs.C)] for x in Lm], dtype=np.uint8)
        for route in ("rowspace", "nullspace", None):
            self.assertFalse(cc.dual_check_b(Lam2, cs, N, route=route)[0])

    def test_wdag_accepted_where_contained(self):
        built = 0
        for name in ("i4", "i4e", "i5", "i5z", "eqs2", "i6", "m4"):
            inst, eqs, N, gens, Z = get_instance(name)
            for D in (3, 4):
                b = build_wdag(eqs, N, D, Z, inst)
                if b is None:
                    continue
                cert, sysb, cl = b
                res = run(sysb, cert, z_bruteforce=True)
                self.assertEqual(res["verdict"], "accept", (name, D, res["failed_checks"], res.get("malformed")))
                self.assertTrue(res["info"]["targets_are_reduced_gb"])
                built += 1
        self.assertGreaterEqual(built, 7)

    def test_wdag_with_empty_Z(self):
        inst, eqs, N, gens, Z = get_instance("i4e")
        self.assertEqual(Z, [])
        cert, sysb, cl = build_wdag(eqs, N, 3, Z, inst)
        self.assertEqual(cert["targets"], [[[]]])                 # GB = {1}
        res = run(sysb, cert)
        self.assertEqual(res["verdict"], "accept")
        # an empty-Z claim for an instance that has solutions must fail (f)
        inst2, eqs2_, N2, _, Z2 = get_instance("i5")
        cert2, sysb2, _ = build_wdag(eqs2_, N2, 3, Z2, inst2)
        bad = json.loads(json.dumps(cert2))
        bad["targets"], bad["outputs"], bad["Z"] = [[[]]], [len(bad["nodes"])], []
        bad["nodes"].append({"id": len(bad["nodes"]), "rows": [], "prods": []})
        res = run(sysb2, bad)
        self.assertEqual(res["verdict"], "reject")

    def test_toy_system_without_instance_block(self):
        rnd = random.Random(11)
        nv, found = 6, 0
        while found < 3:
            eqs = [{rnd.getrandbits(nv) & rnd.getrandbits(nv) for _ in range(rnd.randrange(2, 7))} - {0} for _ in range(3)]
            eqs = [e for e in eqs if e]
            if len(eqs) < 3:
                continue
            sysb = sys_bytes_of(nv, eqs)
            sysd = cc.parse_system(sysb)
            Z = cc.bruteforce_Z(nv, sysd.eqs)
            if not Z:
                continue
            built = build_ann(eqs, nv, 2, Z, None, "dual")
            if built is None:
                continue
            cert, sysb, cl, g = built
            res = run(sysb, cert)
            self.assertEqual(res["verdict"], "accept", res["failed_checks"])
            self.assertEqual(res["Z_methods"], ["bruteforce"])
            found += 1


def _macaulay_ints(eqs, nv, D, cl):
    for f in eqs:
        if not f:
            continue
        dk = max(popc(m) for m in f)
        for d in range(0, D - dk + 1):
            for c in itertools.combinations(range(nv), d):
                mu = sum(1 << i for i in c)
                v = 0
                for m in f:
                    v ^= 1 << cl.col[m | mu]
                yield v


class TestNegativeControls(unittest.TestCase):
    def setUp(self):
        self.inst, self.eqs, self.N, _, self.Z = get_instance("i5")      # contained at D=3, not at D=2
        self.inst6, self.eqs6, self.N6, _, self.Z6 = get_instance("i6")

    def _forge_nonclosed(self, D, form="dual"):
        """a 'non-containment' certificate with U = M_D (annihilator of the Macaulay rows only):
        (a) and (c) hold when g is outside M_D, but U is not closed, so (b) must fail."""
        cl = RefClosure(self.eqs, self.N, D)
        Mrows = list(_macaulay_ints(self.eqs, self.N, D, cl))
        gb = ref_gb(self.Z, self.N, D)
        Mech = {}
        for r in Mrows:
            r = iv_reduce(Mech, r)
            if r:
                Mech[(r & -r).bit_length() - 1] = r
        outside = [el for _, el in gb if iv_reduce(Mech, cl.vec(el))]
        self.assertTrue(outside, "need a GB element outside M_D")
        cert = common_fields("sembin-ann-v1", D, self.N, self.eqs, sys_bytes_of(self.N, self.eqs))
        cert.update({"form": form, "g": poly_json(outside[0]), "Z": hexlist(self.Z), "instance": self.inst})
        if form == "dual":
            cert["L_hex"] = hexlist(iv_nullspace(Mrows, cl.C))
        else:
            cert["basis_hex"] = hexlist(list(Mech.values()))
        return cert

    def test_false_noncontainment_claim_at_contained_degree_rejected(self):
        sysb = sys_bytes_of(self.N, self.eqs)
        for form in ("dual", "primal"):
            res = run(sysb, self._forge_nonclosed(3, form))
            self.assertEqual(res["verdict"], "reject")
            self.assertIn("b_closure", res["failed_checks"])
            self.assertNotIn("a_macaulay_rows_in_U", res["failed_checks"])
            self.assertNotIn("d_g_vanishes_on_Z", res["failed_checks"])

    def test_any_valid_closed_U_cannot_exclude_a_contained_g(self):
        # U = W_3 exactly (closed, contains M_3); every GB element is in W_3 here, so (c) must fail
        cl = RefClosure(self.eqs, self.N, 3)
        sysb = sys_bytes_of(self.N, self.eqs)
        for _, el in ref_gb(self.Z, self.N, 3):
            cert = common_fields("sembin-ann-v1", 3, self.N, self.eqs, sysb)
            cert.update({"form": "dual", "L_hex": hexlist(iv_nullspace(cl.basis_vectors(), cl.C)),
                         "g": poly_json(el), "Z": hexlist(self.Z), "instance": self.inst})
            res = run(sysb, cert)
            self.assertEqual(res["verdict"], "reject")
            self.assertEqual(res["failed_checks"], ["c_g_not_in_U"])

    def test_empty_L_and_zero_basis_rejected(self):
        sysb = sys_bytes_of(self.N, self.eqs)
        cert, _, _, g = build_ann(self.eqs, self.N, 2, self.Z, self.inst, "dual")
        for mod in ({"L_hex": []}, {"L_hex": ["0", "0"]}):
            res = run(sysb, dict(cert, **mod))
            self.assertEqual(res["verdict"], "reject")
            self.assertIn("c_g_not_in_U", res["failed_checks"])

    def test_g_not_in_ideal_or_not_reduced_rejected(self):
        cert, sysb, cl, g = build_ann(self.eqs6, self.N6, 2, self.Z6, self.inst6, "dual")
        # g + a monomial: either not in I(Z), or in I(Z) but not the reduced GB element
        extra = [[]] if [] not in cert["g"] else [[0]]
        bad = dict(cert, g=sorted(cert["g"] + extra, key=lambda l: (len(l), l)))
        res = run(sysb, bad)
        self.assertEqual(res["verdict"], "reject")
        self.assertTrue({"d_g_vanishes_on_Z", "d_g_is_reduced_gb_element", "c_g_not_in_U"} & set(res["failed_checks"]))
        # a polynomial in I(Z) that is not reduced: g + (another GB element)
        gb = ref_gb(self.Z6, self.N6, 2)
        if len(gb) >= 2:
            a, b = gb[0][1], gb[1][1]
            comb = a ^ b
            bad = dict(cert, g=poly_json(comb))
            res = run(sysb, bad)
            self.assertEqual(res["verdict"], "reject")
            self.assertIn("d_g_is_reduced_gb_element", res["failed_checks"])
            self.assertNotIn("d_g_vanishes_on_Z", res["failed_checks"])
            # ...but --allow-nonreduced-g accepts it exactly when (a)-(c) hold
            res2 = run(sysb, bad, allow_nonreduced_g=True)
            self.assertNotIn("d_g_is_reduced_gb_element", res2["failed_checks"])

    def test_system_tampering_changes_hash(self):
        cert, sysb, cl, g = build_ann(self.eqs, self.N, 2, self.Z, self.inst, "dual")
        obj = json.loads(sysb)
        obj["eqs"][0].append([0, 1, 2, 3])       # extra monomial
        res = run(jb(obj), cert)
        self.assertEqual(res["verdict"], "reject")
        self.assertIn("e_system_hash", res["failed_checks"])
        res = run(sysb + b"\n", cert)           # trailing newline: non canonical bytes
        self.assertEqual(res["verdict"], "reject")
        self.assertIn("system_file_canonical", res["failed_checks"])
        res = run(sysb + b"\n", cert, lenient_canonical=True)
        self.assertEqual(res["verdict"], "accept")
        # reordered monomials parse to the same system but are non-canonical bytes
        obj = json.loads(sysb)
        obj["eqs"][1] = obj["eqs"][1][::-1]
        reordered = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
        res = run(reordered, cert)
        self.assertEqual(res["verdict"], "reject")
        self.assertEqual(res["failed_checks"], ["system_file_canonical"])

    def test_wrong_system_for_cert_instance(self):
        # system of another instance with the same nv/neq shape but a different curve: descent must fail
        inst, eqs, N, _, Z = get_instance("i5z")
        cert, sysb, cl = build_wdag(eqs, N, 3, Z, inst)
        other, eqs_o, N_o, _, Z_o = get_instance("i5")
        self.assertEqual((N, len(eqs)), (N_o, len(eqs_o)))
        cert_o, sysb_o, _ = build_wdag(eqs_o, N_o, 3, Z_o, other)
        mixed = dict(cert_o, instance=inst)          # cert for system o claims instance i5z
        res = run(sysb_o, mixed)
        self.assertEqual(res["verdict"], "reject")
        self.assertIn("descent_span_equal", res["failed_checks"])

    def test_wdag_structural_violations(self):
        inst, eqs, N, _, Z = get_instance("i6")
        cert, sysb, cl = build_wdag(eqs, N, 4, Z, inst)
        self.assertEqual(run(sysb, cert)["verdict"], "accept")

        def mutated(fn):
            c = json.loads(json.dumps(cert))
            fn(c)
            return run(sysb, c)

        # (a) forward / self reference
        def fwd(c):
            c["nodes"][2]["prods"].append([0, 2])
        self.assertIn("a_child_order", mutated(fwd)["failed_checks"])
        # (b) row degree beyond D: use D-1 in the certificate
        r = mutated(lambda c: c.__setitem__("D", 3))
        self.assertEqual(r["verdict"], "reject")
        self.assertTrue({"b_row_degree", "d_node_degree"} & set(r["failed_checks"]))
        # (b) generator index out of range
        def badk(c):
            c["nodes"][0]["rows"][0][1] = len(eqs)
        self.assertIn("b_row_degree", mutated(badk)["failed_checks"])
        # (c) child with degree D: append a node of degree exactly D=4, then a node that uses it as child
        found = None
        for k in range(len(eqs)):
            dk = max(popc(m) for m in eqs[k])
            for mu in itertools.combinations(range(N), 4 - dk):
                acc = set()
                _toggle_all(acc, (m | sum(1 << i for i in mu) for m in eqs[k]))
                if max((popc(m) for m in acc), default=-1) == 4:
                    found = (list(mu), k)
                    break
            if found:
                break
        self.assertIsNotNone(found)

        def childtop(c):
            c["nodes"].append({"id": len(c["nodes"]), "rows": [[found[0], found[1]]], "prods": []})
            c["nodes"].append({"id": len(c["nodes"]), "rows": [], "prods": [[0, len(c["nodes"]) - 1]]})
        r = mutated(childtop)
        self.assertEqual(r["failed_checks"], ["c_child_degree"])
        # (d) node of degree D+1 (a mutant product of a degree-D child is excluded by (c); use a row instead)
        # (e) wrong output index / wrong target
        def swap(c):
            c["outputs"][0], c["outputs"][1] = c["outputs"][1], c["outputs"][0]
        self.assertIn("e_outputs_equal_targets", mutated(swap)["failed_checks"])
        # (f) drop a target: the remaining leading monomials leave too many standard monomials
        def drop(c):
            c["targets"].pop()
            c["outputs"].pop()
        self.assertIn("f_groebner_basis", mutated(drop)["failed_checks"])
        # an extra (valid) element of I(Z) among the targets does not break the Groebner-basis property
        def novanish(c):
            c["nodes"].append({"id": len(c["nodes"]), "rows": [[[], 0]], "prods": []})
            c["targets"].append(poly_json(set(sets_of(eqs[0]))))
            c["outputs"].append(len(c["nodes"]) - 1)
        r = mutated(novanish)
        self.assertEqual(r["verdict"], "accept")        # f_0 itself vanishes on Z
        # structural malformations
        for fn in (lambda c: c.pop("nodes"), lambda c: c.__setitem__("nodes", []),
                   lambda c: c["nodes"][1].__setitem__("id", 5), lambda c: c["nodes"][0].pop("rows"),
                   lambda c: c.__setitem__("outputs", c["outputs"][:-1]),
                   lambda c: c["outputs"].__setitem__(0, 10 ** 6),
                   lambda c: c["nodes"][0]["rows"].__setitem__(0, [[0, 0], 0]),
                   lambda c: c["nodes"][0]["rows"][0].__setitem__(0, [3, 1]),   # not ascending
                   lambda c: c["nodes"][0]["rows"][0].__setitem__(0, [0, 0]),
                   lambda c: c["nodes"][0]["rows"][0].__setitem__(0, [-1]),
                   lambda c: c["nodes"][0]["rows"][0].__setitem__(0, [N]),
                   lambda c: c.__setitem__("D", True), lambda c: c.__setitem__("D", 4.0),
                   lambda c: c.__setitem__("schema", "sembin-wdag-v2"),
                   lambda c: c.__setitem__("extra", 1),
                   lambda c: c["targets"][0].append(c["targets"][0][0]),
                   lambda c: c.__setitem__("system_sha256", c["system_sha256"].upper()),
                   lambda c: c.__setitem__("Z", ["0xdb"]), lambda c: c.__setitem__("Z", ["DB"])):
            r = mutated(fn)
            self.assertIn(r["verdict"], ("reject",), fn)
            self.assertNotEqual(r["verdict"], "error")

    def test_malformed_json_and_duplicate_keys(self):
        cert, sysb, cl, g = build_ann(self.eqs, self.N, 2, self.Z, self.inst, "dual")
        text = jb(cert).decode()
        for bad in (text[:-1], text + "x", "[]", "null", text.replace('"D":2', '"D":2,"D":3'),
                    text.replace('"D":2', '"D":NaN'), ""):
            res = cc.run_check(sysb, bad.encode(), cc.Options())
            self.assertEqual(res["verdict"], "reject", bad[:40])
        for badsys in (b"", b"{}", gz(sysb), sysb[:-3]):
            res = cc.run_check(badsys, jb(cert), cc.Options())
            self.assertEqual(res["verdict"], "reject")

    def test_internal_errors_never_accept(self):
        sysb = sys_bytes_of(self.N, self.eqs)
        res = cc.run_check(sysb, b'{"schema":"sembin-ann-v1"}', cc.Options())
        self.assertEqual(res["verdict"], "reject")

    def test_brute_force_refusal_above_limit(self):
        inst, eqs, N, _, Z = get_instance("i5")
        cert, sysb, cl, g = build_ann(eqs, N, 2, Z, inst, "dual")
        res = run(sysb, cert, z_bruteforce=True, max_brute_nv=4)
        self.assertEqual(res["verdict"], "reject")
        self.assertIn("Z_enumeration", res["failed_checks"])
        # without the instance block and above the limit nothing can establish Z
        c2 = dict(cert)
        del c2["instance"]
        res = run(sysb, c2, auto_brute_nv=4)
        self.assertEqual(res["verdict"], "reject")
        # with the instance, the chain alone suffices (and a warning is reported)
        res = run(sysb, cert, auto_brute_nv=4)
        self.assertEqual(res["verdict"], "accept")
        self.assertTrue(any("chain only" in w for w in res["warnings"]))


def sets_of(poly_set):
    return set(poly_set)


def _toggle_all(acc, monos):
    """acc ^= {monos} with F_2 cancellation of coinciding monomials (multilinear reduction)."""
    for m in monos:
        if m in acc:
            acc.remove(m)
        else:
            acc.add(m)


def _eval_node(cert, eqs, nid, memo=None):
    memo = {} if memo is None else memo
    if nid in memo:
        return memo[nid]
    nd = cert["nodes"][nid]
    acc = set()
    for mono, k in nd["rows"]:
        mu = sum(1 << i for i in mono)
        _toggle_all(acc, (m | mu for m in eqs[k]))
    for j, c in nd["prods"]:
        _toggle_all(acc, (m | (1 << j) for m in _eval_node(cert, eqs, c, memo)))
    memo[nid] = acc
    return acc


# ===========================================================================
# single-bit-flip sweeps
# ===========================================================================

def classify_obj(sysb, cert_obj, mutated, oracle, opts):
    """checker verdict on a structurally mutated certificate (python object)."""
    res = cc.run_check(sysb, jb(mutated), opts)
    if res["verdict"] == "error":
        return "ERROR:" + res.get("error", "")
    if res["verdict"] == "reject":
        if "malformed" in res:
            return "rejected_malformed"
        if mutated.get("schema") == "sembin-ann-v1" and \
                all(p and p[0] in ("L_hex", "basis_hex", "g") for p in leaf_paths(cert_obj, mutated)) and oracle(mutated):
            return "rejected_check_although_W_D_inside_U"   # (b) is sufficient, not necessary
        return "rejected_check"
    diff = leaf_paths(cert_obj, mutated)
    if all(tuple(p) in INFORMATIONAL for p in diff):
        return "accepted_informational"
    return "accepted_semantic_sound" if oracle(mutated) else "ACCEPTED_UNSOUND"


def flip_int_hex(h, c):
    return format(int(h, 16) ^ (1 << c), "x")


def ann_flip_sweeps(name="i5z", D=2, form="dual", stride=1):
    inst, eqs, N, gens, Z = get_instance(name)
    cert, sysb, cl, g = build_ann(eqs, N, D, Z, inst, form)
    opts = cc.Options()
    oracle = lambda c: ann_truly_sound(c, cl, Z, N, D)      # noqa: E731
    out = {}
    key = "L_hex" if form == "dual" else "basis_hex"
    classes = []
    for i in range(len(cert[key])):
        for c in range(0, cl.C, stride):
            m = json.loads(jb(cert))
            m[key][i] = flip_int_hex(m[key][i], c)
            classes.append(classify_obj(sysb, cert, m, oracle, opts))
    out[f"{key}_bits"] = summarise(classes)
    # monomial toggles in g (every monomial of B_{<=D})
    classes = []
    gm = {sum(1 << i for i in mono) for mono in cert["g"]}
    for mk in cl.masks[::stride]:
        m = json.loads(jb(cert))
        m["g"] = poly_json(gm ^ {mk})
        if not m["g"]:
            continue
        classes.append(classify_obj(sysb, cert, m, oracle, opts))
    out["g_monomial_toggles"] = summarise(classes)
    out.update(scalar_field_flips(sysb, cert, oracle, opts))
    return out


def scalar_field_flips(sysb, cert, oracle, opts):
    """single-bit flips of every numeric / hex scalar outside the big vectors"""
    out = {}
    # system_sha256: every bit of the 256
    classes = []
    for pos in range(64):
        for b in range(4):
            m = json.loads(jb(cert))
            h = m["system_sha256"]
            m["system_sha256"] = h[:pos] + format(int(h[pos], 16) ^ (1 << b), "x") + h[pos + 1:]
            classes.append(classify_obj(sysb, cert, m, oracle, opts))
    out["system_sha256_bits"] = summarise(classes)
    # D, nv, neq, g_gb_index, levels (low 8 bits)
    for key in ("D", "nv", "neq", "g_gb_index", "levels"):
        if key not in cert:
            continue
        classes = []
        for b in range(8):
            m = json.loads(jb(cert))
            m[key] = cert[key] ^ (1 << b)
            classes.append(classify_obj(sysb, cert, m, oracle, opts))
        out[f"{key}_bits"] = summarise(classes)
    # Z claim
    if "Z" in cert:
        classes = []
        for i, h in enumerate(cert["Z"]):
            for b in range(int(h, 16).bit_length() + 2):
                m = json.loads(jb(cert))
                m["Z"][i] = flip_int_hex(h, b)
                classes.append(classify_obj(sysb, cert, m, oracle, opts))
        out["Z_bits"] = summarise(classes)
    # instance block
    if "instance" in cert:
        classes = []
        inst = cert["instance"]
        for key, val in inst.items():
            vals = enumerate(val) if isinstance(val, list) else [(None, val)]
            for idx, v in vals:
                for b in range(max(1, int(v).bit_length()) + 1):
                    m = json.loads(jb(cert))
                    if idx is None:
                        m["instance"][key] = v ^ (1 << b)
                    else:
                        m["instance"][key][idx] = v ^ (1 << b)
                    classes.append(classify_obj(sysb, cert, m, oracle, opts))
        out["instance_bits"] = summarise(classes)
    return out


def system_flip_sweep(name="i5z", D=2):
    """toggle every monomial (deg <= 3) in every equation of the *system* and keep the old certificate
    and its old system_sha256: must always be rejected (hash mismatch)."""
    inst, eqs, N, gens, Z = get_instance(name)
    cert, sysb, cl, g = build_ann(eqs, N, D, Z, inst, "dual")
    classes = []
    obj = json.loads(sysb)
    allm = [m for m in ref_cols(N, 3)]
    for e in range(len(eqs)):
        for mk in allm:
            o2 = json.loads(sysb)
            cur = {sum(1 << i for i in mono) for mono in o2["eqs"][e]}
            o2["eqs"][e] = poly_json(cur ^ {mk})
            res = cc.run_check(jb(o2), jb(cert), cc.Options())
            classes.append("rejected_check" if res["verdict"] == "reject" else res["verdict"])
    return summarise(classes)


def wdag_text_sweep(sysb, cert_obj, cl, Z, nv, D, stride=1, workers=0, start=0):
    orig = jb(cert_obj)
    oracle_key = f"wdag{id(cert_obj)}"
    _ORACLES[oracle_key] = lambda: (lambda c: wdag_truly_sound(c, cl, Z, nv, D))
    optkw = {}
    idx = [(i, b) for i in range(start, len(orig)) for b in range(8)][::stride]
    tasks = [(sysb, cert_obj, orig, i, b, "text", oracle_key, optkw) for i, b in idx]
    if workers > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(workers) as pool:
            classes = pool.map(_worker, tasks, chunksize=64)
    else:
        classes = [_worker(t) for t in tasks]
    res = summarise(classes)
    res["bytes"] = len(orig)
    res["stride"] = stride
    return res


class TestFlips(unittest.TestCase):
    def _no_bad(self, summary):
        for k, v in summary.items():
            if isinstance(v, dict):
                self._no_bad(v)
            elif isinstance(k, str) and (k.startswith("ACCEPTED_UNSOUND") or k.startswith("ERROR")):
                self.fail(f"{k}: {v} in {summary}")

    def test_ann_dual_flips_all_bits(self):
        r = ann_flip_sweeps("i5z", 2, "dual")
        self._no_bad(r)
        self.assertEqual(r["system_sha256_bits"].get("rejected_check"), 256)
        self.assertEqual(r["Z_bits"]["flips"], r["Z_bits"].get("rejected_check", 0))
        # nothing but rejections in the instance block, including num_points_E
        self.assertEqual(r["instance_bits"]["flips"],
                         r["instance_bits"].get("rejected_check", 0) + r["instance_bits"].get("rejected_malformed", 0))
        self.assertGreater(r["L_hex_bits"].get("rejected_check", 0), 0)
        print("\nann dual i5z D=2:", json.dumps(r["L_hex_bits"]), json.dumps(r["g_monomial_toggles"]))

    def test_ann_primal_flips_all_bits(self):
        r = ann_flip_sweeps("i5z", 2, "primal")
        self._no_bad(r)
        print("\nann primal i5z D=2:", json.dumps(r["basis_hex_bits"]), json.dumps(r["g_monomial_toggles"]))

    def test_system_toggles_all_rejected(self):
        r = system_flip_sweep("i5z", 2)
        self.assertEqual(r["flips"], r.get("rejected_check"))

    def test_wdag_text_flips_own_certificate(self):
        inst, eqs, N, gens, Z = get_instance("i5z")
        cert, sysb, cl = build_wdag(eqs, N, 4, Z, inst)
        r = wdag_text_sweep(sysb, cert, cl, Z, N, 4, stride=13)
        self._no_bad(r)
        print("\nwdag text flips (own i5z D=4, stride 13):", json.dumps(r))

    def test_wdag_text_flips_sample(self):
        s = sample("m3n06")
        if s is None:
            self.skipTest("samples not available")
        sp, cp, ip = s
        sysb, cert_obj = read(sp), json.loads(read(cp))
        sysd = cc.parse_system(sysb)
        eqs = [set(a.tolist()) for a in sysd.eqs]
        cl = RefClosure(eqs, sysd.nv, 4)
        Z = sorted(int(h, 16) for h in cert_obj["Z"])
        r = wdag_text_sweep(sysb, cert_obj, cl, Z, sysd.nv, 4, stride=211)
        self._no_bad(r)
        print("\nwdag text flips (sample m3n06, stride 211):", json.dumps(r))


class TestCliOnOwnFiles(unittest.TestCase):
    def test_cli_roundtrip_and_exit_codes(self):
        import tempfile
        inst, eqs, N, gens, Z = get_instance("i6")
        cert, sysb, cl, g = build_ann(eqs, N, 3, Z, inst, "dual")
        with tempfile.TemporaryDirectory() as td:
            sp, cp = os.path.join(td, "s.sys.json.gz"), os.path.join(td, "c.ann.json.gz")
            write_bytes(sp, gz(sysb))
            write_bytes(cp, gz(jb(cert)))
            code, res, err = cli("--system", sp, "--cert", cp, "--z-bruteforce")
            self.assertEqual(code, 0, err)
            self.assertEqual(res["verdict"], "accept")
            bad = dict(cert)
            bad["L_hex"] = cert["L_hex"][:-1]
            write_bytes(cp, gz(jb(bad)))
            code, res, err = cli("--system", sp, "--cert", cp)
            self.assertEqual(code, 1)
            write_bytes(cp, b"\x1f\x8b not gzip")
            code, res, err = cli("--system", sp, "--cert", cp)
            self.assertEqual(code, 2)


# ===========================================================================
# entry point
# ===========================================================================

def sweep_main(argv):
    full = "--full" in argv
    workers = 4
    out = {}
    for name, D, form in (("i5z", 2, "dual"), ("i5z", 2, "primal"), ("i6", 3, "dual"), ("i6", 3, "primal"), ("m4", 3, "dual")):
        out[f"ann_{form}_{name}_D{D}"] = ann_flip_sweeps(name, D, form, stride=1)
        print(json.dumps({f"ann_{form}_{name}_D{D}": out[f"ann_{form}_{name}_D{D}"]}, sort_keys=True), flush=True)
    out["system_toggles_i5z"] = system_flip_sweep("i5z", 2)
    print(json.dumps({"system_toggles_i5z": out["system_toggles_i5z"]}), flush=True)
    stride = 1 if full else 17
    for cell in ("m3n05", "m3n06"):
        s = sample(cell)
        if s is None:
            continue
        sp, cp, ip = s
        sysb, cert_obj = read(sp), json.loads(read(cp))
        sysd = cc.parse_system(sysb)
        eqs = [set(a.tolist()) for a in sysd.eqs]
        cl = RefClosure(eqs, sysd.nv, 4)
        Z = sorted(int(h, 16) for h in cert_obj["Z"])
        out[f"wdag_text_sample_{cell}"] = wdag_text_sweep(sysb, cert_obj, cl, Z, sysd.nv, 4, stride=stride, workers=workers)
        print(json.dumps({f"wdag_text_sample_{cell}": out[f"wdag_text_sample_{cell}"]}, sort_keys=True), flush=True)
    for name in ("i5z", "i6", "m4"):
        inst, eqs, N, gens, Z = get_instance(name)
        D = 4
        b = build_wdag(eqs, N, D, Z, inst)
        cert, sysb, cl = b
        out[f"wdag_text_own_{name}"] = wdag_text_sweep(sysb, cert, cl, Z, N, D, stride=stride, workers=workers)
        print(json.dumps({f"wdag_text_own_{name}": out[f"wdag_text_own_{name}"]}, sort_keys=True), flush=True)
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sweep":
        sweep_main(sys.argv[2:])
    else:
        unittest.main(argv=[sys.argv[0]] + sys.argv[1:], verbosity=2)
