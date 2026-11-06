#!/usr/bin/env python3
"""Independent certificate checker for EXP-SEMBIN-cb5e25.

Written from ``formats.md`` and ``specification.yaml`` only (blind to the
producer's ``code/``).  CLI::

    python3 check_certs.py --system SYS.json.gz --cert CERT.json.gz [--z-bruteforce]

prints a JSON verdict and exits 0 only when the certificate is accepted
(1 = rejected, 2 = usage / unreadable input, 3 = internal error; never accept
on an exception).  Dependencies: Python stdlib + numpy.

Layout of this file
  1. low level helpers (JSON, hashing, monomials as bitmasks)
  2. GF(2^n) arithmetic, Weil descent re-derivation, GF(2) RREF in grevlex
  3. column space COL(D, nv), Boolean Macaulay rows
  4. solution set Z: bit-sliced brute force, algebraic chain, reduced GB
  5. sembin-ann-v1 checks (a)-(e), dual and primal form
  6. sembin-wdag-v1 checks (a)-(g)
  7. orchestration and CLI
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import math
import random
import re
import sys
import time
import zlib

import numpy as np

SYS_SCHEMA = "sembin-sys-v1"
ANN_SCHEMA = "sembin-ann-v1"
WDAG_SCHEMA = "sembin-wdag-v1"
MAX_NV = 62                      # monomials are int64 bitmasks
MAX_COLS = 4_000_000             # refuse to build COL(D, nv) beyond this many columns
MAX_GB_MONOMIALS = 3_000_000     # monomials scanned for the reduced-GB comparison
MAX_CHAIN_PAIRS_LOG2 = 26        # chain enumerator budget: 2^((m-1)k) (X_1..X_{m-1}) combinations


class Malformed(Exception):
    """An input does not parse as the documented format."""


# ---------------------------------------------------------------------------
# 1. helpers
# ---------------------------------------------------------------------------

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _no_dup_pairs(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise Malformed(f"duplicate JSON key {k!r}")
        d[k] = v
    return d


def _bad_constant(x):
    raise Malformed(f"non-finite JSON constant {x}")


def load_json(data: bytes):
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=_no_dup_pairs,
                          parse_constant=_bad_constant)
    except (ValueError, UnicodeDecodeError, RecursionError) as e:
        raise Malformed(f"not valid JSON: {e}")


def read_maybe_gz(path: str):
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:2] == b"\x1f\x8b":
        try:
            return gzip.decompress(raw), True
        except (OSError, EOFError, zlib.error) as e:
            raise Malformed(f"bad gzip stream in {path}: {e}")
    return raw, False


def canon_json_bytes(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def is_int(x) -> bool:
    return type(x) is int


def popcount_arr(a: np.ndarray) -> np.ndarray:
    if a.size == 0:
        return np.zeros(0, dtype=np.int64)
    return np.bitwise_count(a.astype(np.uint64)).astype(np.int64)


def mask_to_mono(mask: int):
    out = []
    i = 0
    while mask:
        if mask & 1:
            out.append(i)
        mask >>= 1
        i += 1
    return out


def gkey(mask: int):
    """Grevlex key, larger = larger monomial: degree first, then smaller bitmask is larger."""
    return (mask.bit_count(), -mask)


def parse_mono(m, nv: int, strict_sorted: bool, what: str) -> int:
    if type(m) is not list:
        raise Malformed(f"{what}: monomial is not a list")
    mask = 0
    prev = -1
    for v in m:
        if not is_int(v) or v < 0 or v >= nv:
            raise Malformed(f"{what}: bad variable index {v!r} (nv={nv})")
        if strict_sorted and v <= prev:
            raise Malformed(f"{what}: monomial {m} is not strictly ascending")
        prev = v
        b = 1 << v
        if mask & b:
            raise Malformed(f"{what}: repeated variable in monomial {m}")
        mask |= b
    return mask


def parse_poly(lst, nv: int, strict_sorted: bool, what: str) -> np.ndarray:
    """polynomial -> sorted int64 array of distinct monomial masks."""
    if type(lst) is not list:
        raise Malformed(f"{what}: polynomial is not a list")
    masks = [parse_mono(m, nv, strict_sorted, what) for m in lst]
    arr = np.array(masks, dtype=np.int64)
    if np.unique(arr).size != arr.size:
        raise Malformed(f"{what}: repeated monomial in polynomial")
    arr.sort()
    return arr


def poly_degree(arr: np.ndarray) -> int:
    """largest monomial degree; the zero polynomial has degree -1."""
    return int(popcount_arr(arr).max()) if arr.size else -1


def pxor(arrs):
    """F2-sum of polynomials given as int64 mask arrays."""
    arrs = [a for a in arrs if a.size]
    if not arrs:
        return np.zeros(0, dtype=np.int64)
    a = arrs[0] if len(arrs) == 1 else np.concatenate(arrs)
    u, c = np.unique(a, return_counts=True)
    return u[(c & 1) == 1]


def parse_hex_field(h, what: str) -> int:
    if type(h) is not str or not re.fullmatch(r"[0-9a-f]+", h):
        raise Malformed(f"{what}: not a lowercase hex integer without prefix: {h!r}")
    return int(h, 16)


def int_to_bits(x: int, C: int) -> np.ndarray:
    nb = (C + 7) // 8
    return np.unpackbits(np.frombuffer(x.to_bytes(nb, "little"), dtype=np.uint8),
                         bitorder="little")[:C]


def cols_to_int(cols: np.ndarray) -> int:
    """XOR (parity) of unit vectors at the given column indices."""
    if cols.size == 0:
        return 0
    u, c = np.unique(cols, return_counts=True)
    u = u[(c & 1) == 1]
    if u.size == 0:
        return 0
    ba = bytearray(int(u[-1]) // 8 + 1)
    for i in u.tolist():
        ba[i >> 3] |= 1 << (i & 7)
    return int.from_bytes(ba, "little")


# ---------------------------------------------------------------------------
# system parsing, canonical bytes
# ---------------------------------------------------------------------------

class SystemData:
    pass


def canonical_system_bytes(nv: int, eq_masks) -> bytes:
    eqs = []
    for arr in eq_masks:
        monos = [mask_to_mono(int(x)) for x in arr]
        monos.sort(key=lambda m: (len(m), m))
        eqs.append(monos)
    return canon_json_bytes({"eqs": eqs, "neq": len(eqs), "nv": nv, "schema": SYS_SCHEMA})


def parse_system(data: bytes) -> SystemData:
    obj = load_json(data)
    if type(obj) is not dict or set(obj) != {"eqs", "neq", "nv", "schema"}:
        raise Malformed("system: keys must be exactly eqs, neq, nv, schema")
    if obj["schema"] != SYS_SCHEMA:
        raise Malformed(f"system: schema {obj['schema']!r} != {SYS_SCHEMA}")
    nv, neq, eqs = obj["nv"], obj["neq"], obj["eqs"]
    if not is_int(nv) or not (1 <= nv <= MAX_NV):
        raise Malformed(f"system: nv {nv!r} outside 1..{MAX_NV}")
    if type(eqs) is not list or not is_int(neq) or neq != len(eqs):
        raise Malformed("system: neq does not match len(eqs)")
    s = SystemData()
    s.nv, s.neq = nv, neq
    # monomial order inside the JSON must not matter for parsing
    s.eqs = [parse_poly(e, nv, False, f"system eq {i}") for i, e in enumerate(eqs)]
    s.degs = [poly_degree(a) for a in s.eqs]
    s.file_bytes = data
    s.canonical = canonical_system_bytes(nv, s.eqs)
    s.sha256 = sha256_hex(s.canonical)           # the system's identity
    s.file_sha256 = sha256_hex(data)
    s.file_is_canonical = (s.canonical == data)
    return s


# ---------------------------------------------------------------------------
# 2. GF(2^n), Weil descent, RREF
# ---------------------------------------------------------------------------

def _pmulmod(a: int, b: int, p: int) -> int:
    dp = p.bit_length() - 1
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if (a >> dp) & 1:
            a ^= p
    return r


def _pgcd(a: int, b: int) -> int:
    while b:
        while a and a.bit_length() >= b.bit_length():
            a ^= b << (a.bit_length() - b.bit_length())
        a, b = b, a
    return a


def _prime_factors(n: int):
    out, d = [], 2
    while d * d <= n:
        if n % d == 0:
            out.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        out.append(n)
    return out


def is_irreducible(p: int) -> bool:
    n = p.bit_length() - 1
    if n < 1 or not (p & 1):
        return False

    def frob(e):
        x = 2
        for _ in range(e):
            x = _pmulmod(x, x, p)
        return x

    if frob(n) != 2:
        return False
    for q in _prime_factors(n):
        if _pgcd(p, frob(n // q) ^ 2) != 1:
            return False
    return True


class GF:
    """F_2[t]/(p); element = int, bit i = coefficient of t^i."""

    def __init__(self, n: int, poly: int):
        if not (2 <= n <= 60) or poly.bit_length() != n + 1:
            raise Malformed(f"field_poly {poly} is not a degree-{n} polynomial")
        if not is_irreducible(poly):
            raise Malformed(f"field_poly {poly} is reducible")
        self.n, self.p = n, poly
        self.tp = []                       # t^e mod p, e = 0..2n-2
        x = 1
        for _ in range(2 * n - 1):
            self.tp.append(x)
            x <<= 1
            if (x >> n) & 1:
                x ^= poly
        self._build_wsq()

    def mul(self, a, b):
        n, p = self.n, self.p
        r = 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if (a >> n) & 1:
                a ^= p
        return r

    def sq(self, a):
        r, i = 0, 0
        while a:
            if a & 1:
                r ^= self.tp[2 * i]
            a >>= 1
            i += 1
        return r

    def reduce(self, x):
        while x.bit_length() > self.n:
            x ^= self.p << (x.bit_length() - 1 - self.n)
        return x

    def inv(self, a):
        if a == 0:
            raise ZeroDivisionError("inverse of 0")
        u, v, g1, g2 = a, self.p, 1, 0
        while u != 1:
            j = u.bit_length() - v.bit_length()
            if j < 0:
                u, v, g1, g2 = v, u, g2, g1
                j = -j
            u ^= v << j
            g1 ^= g2 << j
        return self.reduce(g1)

    def sqrt(self, a):
        for _ in range(self.n - 1):
            a = self.sq(a)
        return a

    def _build_wsq(self):
        ech = {}
        for i in range(self.n):
            w = 1 << i
            img, pre = self.mul(w, w) ^ w, w
            while img:
                hb = img.bit_length() - 1
                if hb in ech:
                    img ^= ech[hb][0]
                    pre ^= ech[hb][1]
                else:
                    ech[hb] = (img, pre)
                    break
        self._wsq = ech

    def solve_wsq(self, g):
        """a w with w^2 + w = g, or None (the other solution is w + 1)."""
        pre = 0
        while g:
            e = self._wsq.get(g.bit_length() - 1)
            if e is None:
                return None
            g ^= e[0]
            pre ^= e[1]
        return pre

    # S_3(x1,x2,x3) = (x1x2+x1x3+x2x3)^2 + x1x2x3 + B
    def s3(self, x1, x2, x3, B):
        e = self.mul(x1, x2) ^ self.mul(x1, x3) ^ self.mul(x2, x3)
        return self.sq(e) ^ self.mul(self.mul(x1, x2), x3) ^ B

    def roots_third(self, x1, x2, B):
        """all u in F with S_3(x1, x2, u) = 0 (S_3 is symmetric)."""
        a = self.sq(x1 ^ x2)
        b = self.mul(x1, x2)
        c = self.sq(b) ^ B
        if a == 0:
            if b == 0:
                if c != 0:
                    return []
                raise Malformed("degenerate S_3 (identically zero in u)")
            r = [self.mul(c, self.inv(b))]
        elif b == 0:
            r = [self.sqrt(self.mul(c, self.inv(a)))]
        else:
            ba = self.mul(b, self.inv(a))
            gam = self.mul(self.mul(c, a), self.inv(self.sq(b)))
            w = self.solve_wsq(gam)
            r = [] if w is None else [self.mul(ba, w), self.mul(ba, w ^ 1)]
        for u in r:                     # internal consistency: every root is a root
            assert self.mul(a, self.sq(u)) ^ self.mul(b, u) ^ c == 0
        return r


# ---- symbolic Weil descent over B = F2[X]/(X^2+X) ------------------------
# polynomial = python set of int monomial masks; field element = list of n polynomials

def _pmul(a, b):
    res = set()
    for x in a:
        for y in b:
            z = x | y
            if z in res:
                res.remove(z)
            else:
                res.add(z)
    return res


def _fconst(F: GF, val: int):
    return [({0} if (val >> b) & 1 else set()) for b in range(F.n)]


def _fadd(a, b):
    return [x ^ y for x, y in zip(a, b)]


def _fmul(F: GF, a, b):
    res = [set() for _ in range(F.n)]
    for i in range(F.n):
        if not a[i]:
            continue
        for j in range(F.n):
            if not b[j]:
                continue
            pr = _pmul(a[i], b[j])
            if not pr:
                continue
            t, r = F.tp[i + j], 0
            while t:
                if t & 1:
                    res[r] ^= pr
                t >>= 1
                r += 1
    return res


def _fsq(F: GF, a):
    """Frobenius: (sum c_a t^a)^2 = sum c_a t^(2a) because c_a^2 = c_a in B."""
    res = [set() for _ in range(F.n)]
    for i in range(F.n):
        if not a[i]:
            continue
        t, r = F.tp[2 * i], 0
        while t:
            if t & 1:
                res[r] ^= a[i]
            t >>= 1
            r += 1
    return res


def _fs3(F: GF, x1, x2, x3, B):
    e = _fadd(_fadd(_fmul(F, x1, x2), _fmul(F, x1, x3)), _fmul(F, x2, x3))
    return _fadd(_fadd(_fsq(F, e), _fmul(F, _fmul(F, x1, x2), x3)), _fconst(F, B))


INSTANCE_KEYS = ("n", "field_poly", "A", "B", "m", "k", "v", "x_R")
INSTANCE_OPT = ("num_points_E",)
NPE_MAX_N = 18                      # verify num_points_E (O(2^n)) only up to this n


def validate_instance(inst) -> dict:
    """structure of section 1; returns normalised dict. Raises Malformed."""
    if type(inst) is not dict:
        raise Malformed("instance is not an object")
    for key in INSTANCE_KEYS:
        if key not in inst:
            raise Malformed(f"instance lacks {key!r}")
    extra = set(inst) - set(INSTANCE_KEYS) - set(INSTANCE_OPT)
    if extra:
        raise Malformed(f"instance has undocumented key(s) {sorted(extra)}")
    if "num_points_E" in inst and not is_int(inst["num_points_E"]):
        raise Malformed("instance.num_points_E is not an integer")
    n, fp, A, B, m, k, v, xR = (inst[x] for x in INSTANCE_KEYS)
    for name, val in (("n", n), ("field_poly", fp), ("A", A), ("B", B), ("m", m), ("k", k), ("x_R", xR)):
        if not is_int(val):
            raise Malformed(f"instance.{name} is not an integer")
    if type(v) is not list or not all(is_int(x) for x in v) or len(v) != (m if is_int(m) else -1):
        raise Malformed("instance.v must be a list of m integers")
    if not (3 <= m <= 8) or not (2 <= n <= 60) or not (1 <= k < n):
        raise Malformed("instance: need 3 <= m <= 8 and 1 <= k < n")
    if instance_nv({"m": m, "k": k, "n": n}) > MAX_NV:
        raise Malformed("instance: N = m*k + (m-2)*n exceeds the checker's 62-variable limit")
    if A not in (0, 1) or not (2 <= B < (1 << n)) or not (1 <= xR < (1 << n)):
        raise Malformed("instance: need A in {0,1}, B in [2,2^n), x_R in [1,2^n)")
    if any(not (0 <= x < (1 << n)) for x in v):
        raise Malformed("instance.v out of field range")
    return {"n": n, "field_poly": fp, "A": A, "B": B, "m": m, "k": k, "v": list(v), "x_R": xR,
            "num_points_E": inst.get("num_points_E")}


def count_points(F: GF, A: int, B: int) -> int:
    """#E(F_{2^n}) for y^2 + x y = x^3 + A x^2 + B (B != 0), including the point at infinity.
    x = 0: y^2 = B has exactly one root.  x != 0: put y = x w, w^2 + w = x + A + B x^-2,
    which has 2 solutions iff the right side is in the image of w -> w^2 + w."""
    cnt = 2                                    # infinity and (0, sqrt B)
    for x in range(1, 1 << F.n):
        gam = x ^ A ^ F.mul(B, F.inv(F.sq(x)))
        if F.solve_wsq(gam) is not None:
            cnt += 2
    return cnt


def shifts_ok(inst) -> (bool, str):
    """EQS4: every v_i >= 2^k and (v_i xor v_j) >= 2^k; EQS2: all zero."""
    v, k = inst["v"], inst["k"]
    if all(x == 0 for x in v):
        return True, "EQS2 (all shifts 0)"
    if any(x < (1 << k) for x in v):
        return False, "some v_i < 2^k"
    for i, j in itertools.combinations(range(len(v)), 2):
        if (v[i] ^ v[j]) < (1 << k):
            return False, f"v_{i+1} xor v_{j+1} < 2^k"
    return True, "EQS4"


def instance_nv(inst):
    return inst["m"] * inst["k"] + (inst["m"] - 2) * inst["n"]


def descend(inst):
    """raw Weil-descent generators (list of sets of masks), nv."""
    F = GF(inst["n"], inst["field_poly"])
    n, k, m, v, B, xR = inst["n"], inst["k"], inst["m"], inst["v"], inst["B"], inst["x_R"]
    X = []
    for i in range(m):
        el = []
        for b in range(n):
            s = set()
            if (v[i] >> b) & 1:
                s.add(0)
            if b < k:
                s ^= {1 << (i * k + b)}
            el.append(s)
        X.append(el)
    U = [[{1 << (m * k + j * n + a)} for a in range(n)] for j in range(m - 2)]
    xr = _fconst(F, xR)
    links = [_fs3(F, X[0], X[1], U[0], B)]
    for j in range(1, m - 2):
        links.append(_fs3(F, U[j - 1], X[j + 1], U[j], B))
    links.append(_fs3(F, U[m - 3], X[m - 1], xr, B))
    gens = [coord for link in links for coord in link]
    assert len(gens) == (m - 1) * n
    return gens, instance_nv(inst), F


def numeric_descent_selfcheck(inst, gens, F: GF, npoints=64, seed=20261106) -> int:
    """number of mismatches between symbolic generators and field-side S_3 at random points."""
    n, k, m, v, B, xR = inst["n"], inst["k"], inst["m"], inst["v"], inst["B"], inst["x_R"]
    N = instance_nv(inst)
    rng = random.Random(seed)
    bad = 0
    for _ in range(npoints):
        s = rng.getrandbits(N)
        X = [v[i] ^ ((s >> (i * k)) & ((1 << k) - 1)) for i in range(m)]
        U = [(s >> (m * k + j * n)) & ((1 << n) - 1) for j in range(m - 2)]
        args = [(X[0], X[1], U[0])]
        for j in range(1, m - 2):
            args.append((U[j - 1], X[j + 1], U[j]))
        args.append((U[m - 3], X[m - 1], xR))
        for l, (x1, x2, x3) in enumerate(args):
            val = F.s3(x1, x2, x3, B)
            for a in range(n):
                g = gens[l * n + a]
                got = sum(1 for mm in g if (mm & s) == mm) & 1
                if got != (val >> a) & 1:
                    bad += 1
    return bad


def rref_grevlex(polys):
    """F2-span of the polynomials (sets of masks) -> reduced row echelon rows,
    monomials ordered by descending grevlex, pivot = largest monomial,
    rows by decreasing pivot, zero rows dropped."""
    piv = {}
    for p0 in polys:
        p = set(p0)
        while p:
            lm = max(p, key=gkey)
            q = piv.get(lm)
            if q is None:
                piv[lm] = p
                break
            p ^= q
    for lm in sorted(piv, key=gkey):
        row = piv[lm]
        while True:
            red = [mm for mm in row if mm != lm and mm in piv]
            if not red:
                break
            row ^= piv[max(red, key=gkey)]
    return [piv[lm] for lm in sorted(piv, key=gkey, reverse=True)]


def sets_to_canonical_bytes(nv, polys) -> bytes:
    return canonical_system_bytes(nv, [np.array(sorted(p), dtype=np.int64) for p in polys])


# ---------------------------------------------------------------------------
# 3. column space COL(D, nv), Boolean Macaulay rows, GF(2) linear algebra
# ---------------------------------------------------------------------------

def monomials_of_degree(nv: int, d: int) -> np.ndarray:
    ms = sorted(sum(1 << i for i in c) for c in itertools.combinations(range(nv), d))
    return np.array(ms, dtype=np.int64)


class ColSpace:
    """COL(D, nv): all monomials of degree <= D sorted by (-degree, bitmask ascending)."""

    def __init__(self, D: int, nv: int):
        self.D, self.nv = D, nv
        total = sum(math.comb(nv, d) for d in range(0, min(D, nv) + 1))
        if total > MAX_COLS:
            raise Malformed(f"B_{{<=D}} has {total} monomials (> checker limit {MAX_COLS})")
        parts = [monomials_of_degree(nv, d) for d in range(min(D, nv), -1, -1)]
        self.masks = np.concatenate(parts)
        self.C = int(self.masks.size)
        self.deg = popcount_arr(self.masks)
        self.n_top = int(parts[0].size) if D <= nv else 0     # number of degree-D columns
        self._order = np.argsort(self.masks, kind="stable")
        self._sorted = self.masks[self._order]
        self.by_degree = {d: monomials_of_degree(nv, d) for d in range(0, min(D, nv) + 1)}

    def index(self, arr: np.ndarray) -> np.ndarray:
        arr = np.asarray(arr, dtype=np.int64)
        pos = np.searchsorted(self._sorted, arr)
        if (pos >= self.C).any() or (self._sorted[np.minimum(pos, self.C - 1)] != arr).any():
            raise Malformed("monomial outside B_{<=D}")
        return self._order[pos]

    def poly_vec_int(self, arr: np.ndarray) -> int:
        return cols_to_int(self.index(arr)) if arr.size else 0


def macaulay_blocks(sysd: SystemData, D: int, cs: ColSpace, max_cells: int = 4_000_000):
    """Yield (k, t_masks, col_idx[n_t, |f_k|]): the Boolean Macaulay rows t*f_k
    (deg t + deg f_k <= D), as, for each t, the column of each union t|monomial.
    Collisions (multilinear reduction) are left for the consumer to XOR out."""
    for k, f in enumerate(sysd.eqs):
        dk = sysd.degs[k]
        if dk < 0 or D - dk < 0:
            continue
        tmax = min(D - dk, sysd.nv)
        T = np.concatenate([cs.by_degree[d] for d in range(0, tmax + 1)])
        step = max(1, max_cells // max(1, f.size))
        for s0 in range(0, T.size, step):
            Tc = T[s0:s0 + step]
            U = Tc[:, None] | f[None, :]
            yield k, Tc, cs.index(U.ravel()).reshape(U.shape)


def gf2_rref(M: np.ndarray):
    """RREF over GF(2) of a 0/1 uint8 matrix (rows x cols) -> (rref uint8, pivot columns)."""
    nr, nc = M.shape
    if nr == 0 or nc == 0:
        return np.zeros((0, nc), dtype=np.uint8), []
    W = (nc + 63) // 64
    pad = np.zeros((nr, W * 64), dtype=np.uint8)
    pad[:, :nc] = M
    P = np.packbits(pad, axis=1, bitorder="little").view("<u8").copy()
    pivots, row = [], 0
    one = np.uint64(1)
    for c in range(nc):
        if row >= nr:
            break
        w, b = divmod(c, 64)
        colbits = (P[:, w] >> np.uint64(b)) & one
        nz = np.flatnonzero(colbits[row:])
        if nz.size == 0:
            continue
        p = row + int(nz[0])
        if p != row:
            P[[row, p]] = P[[p, row]]
            colbits[[row, p]] = colbits[[p, row]]
        mask = colbits.astype(bool)
        mask[row] = False
        if mask.any():
            P[mask] ^= P[row]
        pivots.append(c)
        row += 1
    R = np.unpackbits(P[:row].view(np.uint8), axis=1, bitorder="little")[:, :nc]
    return np.ascontiguousarray(R), pivots


def gf2_nullspace_from_rref(R: np.ndarray, pivots, nc: int) -> np.ndarray:
    """basis (rows) of {x : R x = 0} from an RREF."""
    piv = np.array(pivots, dtype=np.int64)
    free = np.setdiff1d(np.arange(nc), piv)
    K = np.zeros((free.size, nc), dtype=np.uint8)
    K[np.arange(free.size), free] = 1
    if piv.size:
        K[:, piv] = R[:, free].T
    return K


def gf2_matmul_is_zero(X: np.ndarray, Y: np.ndarray, chunk_rows: int = 2048) -> bool:
    """(X @ Y) mod 2 == 0 ? X (a x b), Y (b x c) 0/1 matrices; float32 BLAS in chunks (exact: b < 2^24)."""
    if X.shape[0] == 0 or Y.shape[1] == 0 or X.shape[1] == 0:
        return True
    Yf = Y.astype(np.float32)
    for s0 in range(0, X.shape[0], chunk_rows):
        prod = X[s0:s0 + chunk_rows].astype(np.float32) @ Yf
        if (prod.astype(np.int64) & 1).any():
            return False
    return True


# ---------------------------------------------------------------------------
# 4. solution set Z
# ---------------------------------------------------------------------------

def eval_system_at(sysd: SystemData, s: int) -> bool:
    """does the point s satisfy every serialised generator?"""
    for arr in sysd.eqs:
        if arr.size and (int(np.count_nonzero((arr & s) == arr)) & 1):
            return False
    return True


def bruteforce_Z(nv: int, eq_masks, low_bits: int = 16):
    """All solutions in F_2^nv by bit-sliced evaluation (chunks of 2^low_bits points)."""
    low = min(nv, low_bits)
    npts = 1 << low
    W = (npts + 63) // 64
    idx = np.arange(npts, dtype=np.int64)

    def pack(bits):
        pad = np.zeros(W * 64, dtype=np.uint8)
        pad[:npts] = bits
        return np.packbits(pad, bitorder="little").view("<u8").copy()

    var_low = [pack(((idx >> i) & 1).astype(np.uint8)) for i in range(low)]
    ones = np.full(W, np.uint64(0xFFFFFFFFFFFFFFFF), dtype="<u8")
    zeros = np.zeros(W, dtype="<u8")
    valid = pack(np.ones(npts, dtype=np.uint8))
    eqs = [[tuple(mask_to_mono(int(x))) for x in arr] for arr in eq_masks]
    out = []
    for h in range(1 << (nv - low)):
        vt = var_low + [ones if (h >> (i - low)) & 1 else zeros for i in range(low, nv)]
        cache = {(): ones}

        def tab(mono):
            t = cache.get(mono)
            if t is None:
                t = tab(mono[:-1]) & vt[mono[-1]]
                cache[mono] = t
            return t

        alive = valid.copy()
        for eq in eqs:
            val = zeros.copy()
            for mono in eq:
                val ^= tab(mono)
            alive &= ~val
            if not alive.any():
                break
        if alive.any():
            bits = np.unpackbits(alive.view(np.uint8), bitorder="little")[:npts]
            for p in np.flatnonzero(bits).tolist():
                out.append((h << low) | p)
    return sorted(out)


def chain_Z(inst) -> list:
    """Algebraic chain enumeration of Z from the instance parameters (section 1)."""
    F = GF(inst["n"], inst["field_poly"])
    n, k, m, v, B, xR = inst["n"], inst["k"], inst["m"], inst["v"], inst["B"], inst["x_R"]
    if (m - 1) * k > MAX_CHAIN_PAIRS_LOG2:
        raise Malformed(f"chain enumeration needs 2^{(m - 1) * k} tuples (> 2^{MAX_CHAIN_PAIRS_LOG2})")
    cos = [[v[i] ^ x for x in range(1 << k)] for i in range(m)]
    found = []

    def finish(Xs, Us):
        s = 0
        for i, X in enumerate(Xs):
            s |= (X ^ v[i]) << (i * k)
        for j, U in enumerate(Us):
            s |= U << (m * k + j * n)
        found.append(s)

    def rec(Xs, Us):
        i = len(Xs)
        if i == m - 1:
            for Xm in F.roots_third(Us[-1], xR, B):
                if (Xm ^ v[m - 1]) < (1 << k):
                    finish(Xs + [Xm], Us)
            return
        for X in cos[i]:
            for U in F.roots_third(Us[-1], X, B):
                rec(Xs + [X], Us + [U])

    for X1 in cos[0]:
        for X2 in cos[1]:
            for U1 in F.roots_third(X1, X2, B):
                rec([X1, X2], [U1])
    return sorted(found)


def eval_poly_on_points(arr: np.ndarray, pts: np.ndarray) -> np.ndarray:
    """parity of the number of monomials of arr that evaluate to 1 at each point."""
    par = np.zeros(pts.size, dtype=np.uint8)
    for mm in arr.tolist():
        par ^= ((pts & mm) == mm).astype(np.uint8)
    return par


def _ev_ints(pts: np.ndarray, nv: int):
    """for every variable j, the |Z|-bit integer whose bit z is the value of X_j at pts[z]."""
    out = []
    for j in range(nv):
        bits = ((pts >> j) & 1).astype(np.uint8)
        out.append(int.from_bytes(np.packbits(bits, bitorder="little").tobytes(), "little"))
    return out


def monomials_in_grevlex_order(nv: int, dmax: int):
    """ascending grevlex: degree ascending, within a degree larger bitmask first."""
    for d in range(0, min(dmax, nv) + 1):
        for mask in monomials_of_degree(nv, d)[::-1].tolist():
            yield mask


def reduced_gb_elements(pts_list, nv: int, lms):
    """Reduced grevlex GB of I(Z) restricted to the leading monomials in `lms`:
    returns {lm: set(masks) or None}.  None = lm is not the leading monomial of an
    element of the reduced GB (it is standard, or divisible by a smaller non-standard
    monomial).  Buchberger-Moeller over F_2 on evaluation vectors."""
    lms = set(lms)
    result = {lm: None for lm in lms}
    if not lms:
        return result
    if sum(math.comb(nv, d) for d in range(0, max(lm.bit_count() for lm in lms) + 1)) > MAX_GB_MONOMIALS:
        raise Malformed("reduced-GB comparison would scan more monomials than the checker limit")
    pts = np.array(pts_list, dtype=np.int64)
    varev = _ev_ints(pts, nv)
    full = (1 << pts.size) - 1
    std, std_list = set(), []
    basis = {}                       # lowest set bit -> (vec, comb)
    dmax = max(lm.bit_count() for lm in lms)
    remaining = set(lms)
    for mask in monomials_in_grevlex_order(nv, dmax):
        ev = full
        mm = mask
        while mm:
            low = mm & -mm
            ev &= varev[low.bit_length() - 1]
            mm ^= low
        r, c = ev, 0
        while r:
            lowbit = (r & -r).bit_length() - 1
            b = basis.get(lowbit)
            if b is None:
                break
            r ^= b[0]
            c ^= b[1]
        if r:                                     # independent -> standard monomial
            basis[(r & -r).bit_length() - 1] = (r, c ^ (1 << len(std_list)))
            std.add(mask)
            std_list.append(mask)
        elif mask in lms:                         # non-standard
            minimal = all((mask ^ (1 << i)) in std for i in mask_to_mono(mask))
            if minimal:
                elem = {mask}
                cc = c
                while cc:
                    low = cc & -cc
                    elem.add(std_list[low.bit_length() - 1])
                    cc ^= low
                result[mask] = elem
        remaining.discard(mask)
        if not remaining:
            break
    return result


def count_standard_monomials(lms, nv: int, limit: int) -> int:
    """number of squarefree monomials not divisible by any lm, counted degree by
    degree and stopping at the first degree with none; gives up (returns limit+1)
    once the count exceeds `limit`."""
    lmset = set(lms)
    if 0 in lmset:
        return 0
    S, total = {0}, 1
    while S:
        nxt = set()
        for s in S:
            for j in range(s.bit_length(), nv):
                mm = s | (1 << j)
                if mm in lmset:
                    continue
                if all((mm ^ (1 << i)) in S for i in mask_to_mono(mm)):
                    nxt.add(mm)
        total += len(nxt)
        if total > limit:
            return limit + 1
        S = nxt
    return total


# ---------------------------------------------------------------------------
# reporting / context
# ---------------------------------------------------------------------------

def to_py(o):
    if isinstance(o, dict):
        return {str(k): to_py(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [to_py(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


class Report:
    def __init__(self):
        self.checks = {}
        self.warnings = []
        self.weakened = []
        self.info = {}

    def check(self, name, ok, detail=None):
        self.checks[name] = {"ok": bool(ok)}
        if detail is not None:
            self.checks[name]["detail"] = to_py(detail)
        return bool(ok)

    def all_ok(self):
        return bool(self.checks) and all(c["ok"] for c in self.checks.values())


class Options:
    z_bruteforce = False
    max_brute_nv = 24
    auto_brute_nv = 20
    expect_system_sha256 = None
    expect_cert_sha256 = None
    instances = None
    skip_descent = False
    allow_nonreduced_g = False
    allow_extra_keys = False
    lenient_canonical = False

    def __init__(self, **kw):
        for k, v in kw.items():
            if not hasattr(Options, k):
                raise TypeError(f"unknown option {k}")
            setattr(self, k, v)


class Ctx:
    def __init__(self, sysd: SystemData, opts: Options, rep: Report):
        self.sysd, self.opts, self.rep = sysd, opts, rep
        self.instance = None            # validated instance dict (if the cert carries one)
        self.descent_ok = None
        self.raw_sha256 = None
        self.Z = None                   # sorted list of ints once established
        self.Z_methods = []

    # -- solution set ------------------------------------------------------
    def establish_Z(self):
        sysd, opts, rep = self.sysd, self.opts, self.rep
        nv = sysd.nv
        res, notes, ok = {}, [], True
        want_brute = nv <= (opts.max_brute_nv if opts.z_bruteforce else opts.auto_brute_nv)
        if opts.z_bruteforce and nv > opts.max_brute_nv:
            ok = False
            notes.append(f"--z-bruteforce requested but nv={nv} > --max-brute-nv={opts.max_brute_nv}")
        if self.instance is not None and self.descent_ok is not False:
            chain = chain_Z(self.instance)
            res["chain"] = chain
            bad = [s for s in chain if not eval_system_at(sysd, s)]
            if bad:
                ok = False
                notes.append(f"{len(bad)} chain point(s) do not satisfy the serialised system")
        if want_brute:
            res["bruteforce"] = bruteforce_Z(nv, sysd.eqs)
        if not res:
            ok = False
            notes.append(f"no enumeration applicable (nv={nv}, instance={'yes' if self.instance else 'no'})")
        vals = list(res.values())
        if len(vals) == 2 and vals[0] != vals[1]:
            ok = False
            a, b = set(vals[0]), set(vals[1])
            notes.append(f"chain and brute force disagree: |chain\\brute|={len(a-b)}, |brute\\chain|={len(b-a)}")
        self.Z_methods = sorted(res)
        self.Z = (res.get("bruteforce") if "bruteforce" in res else res.get("chain")) if ok else None
        rep.check("Z_enumeration", ok, {"methods": sorted(res), "sizes": {k: len(v) for k, v in res.items()},
                                         "notes": notes})
        if ok and "bruteforce" not in res:
            rep.warnings.append("Z established by the algebraic chain only (nv above the brute-force limit): "
                                "every chain point was checked against the serialised system, "
                                "completeness rests on the chain argument and the descent re-derivation")
        return self.Z


# ---------------------------------------------------------------------------
# common checks
# ---------------------------------------------------------------------------

COMMON_REQ = ("schema", "D", "nv", "neq", "system_sha256")


def check_keys(cert, required, optional, opts: Options):
    for k in required:
        if k not in cert:
            raise Malformed(f"certificate lacks key {k!r}")
    extra = set(cert) - set(required) - set(optional)
    if extra and not opts.allow_extra_keys:
        raise Malformed(f"certificate has undocumented key(s) {sorted(extra)}")


def check_common(rep: Report, ctx: Ctx, cert, hash_check_name: str):
    sysd, opts = ctx.sysd, ctx.opts
    D = cert["D"]
    if not is_int(D) or not (1 <= D <= 64):
        raise Malformed(f"D {D!r} is not an integer in 1..64")
    if not is_int(cert["nv"]) or not is_int(cert["neq"]):
        raise Malformed("nv / neq not integers")
    claim = cert["system_sha256"]
    if type(claim) is not str or not re.fullmatch(r"[0-9a-f]{64}", claim):
        raise Malformed("system_sha256 is not 64 lowercase hex digits")
    ok = (claim == sysd.sha256 and cert["nv"] == sysd.nv and cert["neq"] == sysd.neq)
    rep.check(hash_check_name, ok, {"claimed": claim, "recomputed": sysd.sha256,
                                     "file_bytes_sha256": sysd.file_sha256,
                                     "nv": [cert["nv"], sysd.nv], "neq": [cert["neq"], sysd.neq]})
    canon_ok = sysd.file_is_canonical
    if opts.lenient_canonical:
        if not canon_ok:
            rep.warnings.append("system file bytes are not the canonical serialisation (lenient mode)")
        canon_ok = True
    rep.check("system_file_canonical", canon_ok,
              None if sysd.file_is_canonical else
              "decompressed system bytes differ from canonical sembin-sys-v1 bytes; sha256 of file bytes != system_sha256")
    if opts.expect_system_sha256 is not None:
        rep.check("system_expected_hash", sysd.sha256 == opts.expect_system_sha256,
                  {"expected": opts.expect_system_sha256, "recomputed": sysd.sha256})
    return D


def check_instance_block(rep: Report, ctx: Ctx, cert):
    """if the certificate carries an instance: validate, re-derive the raw descent and
    compare spans with the serialised system."""
    if "instance" not in cert:
        rep.warnings.append("no instance block: Z can only come from brute force over the serialised system")
        return
    inst = validate_instance(cert["instance"])
    sysd, opts = ctx.sysd, ctx.opts
    ok_sh, why = shifts_ok(inst)
    rep.check("instance_valid", ok_sh and instance_nv(inst) == sysd.nv,
              {"shifts": why, "nv_from_instance": instance_nv(inst), "nv_system": sysd.nv})
    if instance_nv(inst) != sysd.nv:
        ctx.descent_ok = False
        return
    ctx.instance = inst
    if inst["num_points_E"] is not None:
        if inst["n"] <= NPE_MAX_N:
            cnt = count_points(GF(inst["n"], inst["field_poly"]), inst["A"], inst["B"])
            rep.check("instance_num_points_E", cnt == inst["num_points_E"],
                      {"claimed": inst["num_points_E"], "recomputed": cnt})
        else:
            rep.warnings.append(f"num_points_E not verified (n={inst['n']} > {NPE_MAX_N})")
    if opts.skip_descent:
        rep.weakened.append("raw Weil descent not re-derived (--skip-descent)")
        return
    gens, _, F = descend(inst)
    mism = numeric_descent_selfcheck(inst, gens, F)
    ctx.raw_sha256 = sha256_hex(sets_to_canonical_bytes(sysd.nv, gens))
    rr_raw = rref_grevlex(gens)
    ser_sets = [set(a.tolist()) for a in sysd.eqs]
    rr_ser = rref_grevlex(ser_sets)
    span_equal = rr_raw == rr_ser
    exact = ser_sets == rr_ser
    ctx.descent_ok = span_equal and mism == 0
    rep.check("descent_span_equal", span_equal,
              {"rank_raw": len(rr_raw), "rank_serialised": len(rr_ser), "raw_system_sha256": ctx.raw_sha256,
               "serialised_is_exact_rref": exact})
    rep.check("descent_selfcheck_numeric", mism == 0, {"mismatches": mism, "points": 64})
    if span_equal and not exact:
        rep.warnings.append("serialised system spans the raw system but is not exactly its grevlex RREF")


def check_instances_record(rep: Report, ctx: Ctx, Z):
    opts = ctx.opts
    if not opts.instances:
        return
    data, _ = read_maybe_gz(opts.instances)
    recs = []
    for line in data.decode("utf-8").splitlines():
        if line.strip():
            recs.append(load_json(line.encode("utf-8")))
    mine = [r for r in recs if r.get("system_sha256") == ctx.sysd.sha256]
    if not mine:
        rep.check("m10_instances_record", False, "no instances record with this system_sha256")
        return
    r = mine[0]
    problems = []
    if ctx.raw_sha256 is not None and r.get("raw_system_sha256") != ctx.raw_sha256:
        problems.append("raw_system_sha256 differs from the checker's own raw descent")
    if Z is not None and "Z_hex" in r and sorted(int(h, 16) for h in r["Z_hex"]) != sorted(Z):
        problems.append("Z_hex differs from the checker's own Z")
    if Z is not None and "z" in r and r["z"] != len(Z):
        problems.append("z != |Z|")
    if ctx.instance is not None and "meta" in r:
        for key in ("A", "B", "field_poly", "k", "m", "n", "v", "x_R"):
            if r["meta"].get(key) != ctx.instance[key]:
                problems.append(f"meta.{key} differs from the certificate instance")
    if r.get("N") not in (None, ctx.sysd.nv):
        problems.append("N != nv")
    rep.check("m10_instances_record", not problems, problems or {"matched_records": len(mine)})


def check_Z_claim(rep: Report, cert, Z):
    if "Z" not in cert:
        return
    claim = cert["Z"]
    if type(claim) is not list:
        raise Malformed("Z is not a list")
    vals = [parse_hex_field(h, "Z") for h in claim]
    if Z is None:
        rep.check("Z_claim_matches", False, "Z not established")
        return
    rep.check("Z_claim_matches", sorted(vals) == sorted(Z) and len(set(vals)) == len(vals),
              {"claimed": len(vals), "enumerated": len(Z)})


# ---------------------------------------------------------------------------
# 5. sembin-ann-v1
# ---------------------------------------------------------------------------

ANN_REQ = COMMON_REQ + ("form", "g")
ANN_OPT = ("L_hex", "basis_hex", "g_gb_index", "Z", "instance")


def pack_columns(Lam: np.ndarray) -> np.ndarray:
    """(nL, C) 0/1 -> (C, W) uint64; bit l of word w of row c = Lam[64w+l, c]."""
    nL, C = Lam.shape
    W = (nL + 63) // 64
    pad = np.zeros((W * 64, C), dtype=np.uint8)
    pad[:nL] = Lam
    packed = np.packbits(pad, axis=0, bitorder="little")        # (W*8, C)
    return np.ascontiguousarray(packed.T).view("<u8")           # (C, W)


def dual_check_a(Lam, sysd, D, cs):
    nL, C = Lam.shape
    if nL == 0:
        return True, 0, None
    LT = pack_columns(Lam)
    W = LT.shape[1]
    rows = 0
    for k, Tc, idx in macaulay_blocks(sysd, D, cs, max_cells=max(1, 6_000_000 // W)):
        acc = np.bitwise_xor.reduce(LT[idx], axis=1)
        rows += Tc.shape[0]
        bad = np.flatnonzero(acc.any(axis=1))
        if bad.size:
            return False, rows, {"generator": k, "multiplier": mask_to_mono(int(Tc[bad[0]]))}
    return True, rows, None


def dual_check_b(Lam, cs, nv, route=None):
    """closure (b), dual form.  route: None (cheaper of the two), 'rowspace' or 'nullspace'
    (both are exact; the parameter exists so the tests can exercise each)."""
    nL, C = Lam.shape
    Ct = cs.n_top
    Cp = C - Ct
    if nL == 0 or Cp == 0:
        return True, {"rank_restricted": 0}
    R = Lam[:, Ct:]
    rref, piv = gf2_rref(R)
    r = len(piv)
    dK = Cp - r
    lower = cs.masks[Ct:]
    use_rowspace = (r <= dK) if route is None else (route == 'rowspace')
    if use_rowspace:
        Rf = rref.astype(np.float32)
    else:
        KT = gf2_nullspace_from_rref(rref, piv, Cp).T
    pivarr = np.array(piv, dtype=np.int64)
    for j in range(nv):
        idx_j = cs.index(lower | np.int64(1 << j))
        Nu = Lam[:, idx_j]
        if use_rowspace:
            for s0 in range(0, nL, 2048):
                ch = Nu[s0:s0 + 2048]
                pred = (ch[:, pivarr].astype(np.float32) @ Rf).astype(np.int64) & 1
                if (pred != ch).any():
                    return False, {"variable": j, "rank_restricted": r}
        else:
            if not gf2_matmul_is_zero(Nu, KT):
                return False, {"variable": j, "rank_restricted": r}
    return True, {"rank_restricted": r, "dim_U_cap_B_le_Dm1": dK}


class Echelon:
    """echelon basis of integer bit-vectors, leading entry = lowest set bit."""

    def __init__(self):
        self.rows = {}

    def reduce(self, v: int) -> int:
        while v:
            low = (v & -v).bit_length() - 1
            b = self.rows.get(low)
            if b is None:
                return v
            v ^= b
        return 0

    def add(self, v: int):
        v = self.reduce(v)
        if v:
            self.rows[(v & -v).bit_length() - 1] = v


def check_ann(rep: Report, ctx: Ctx, cert):
    sysd, opts = ctx.sysd, ctx.opts
    nv = sysd.nv
    form = cert["form"]
    if form not in ("dual", "primal"):
        raise Malformed(f"form {form!r} is neither dual nor primal")
    key = "L_hex" if form == "dual" else "basis_hex"
    other = "basis_hex" if form == "dual" else "L_hex"
    if key not in cert or other in cert:
        raise Malformed(f"form {form} needs exactly {key}")
    if type(cert[key]) is not list:
        raise Malformed(f"{key} is not a list")
    if "g_gb_index" in cert and (not is_int(cert["g_gb_index"]) or cert["g_gb_index"] < 0):
        raise Malformed("g_gb_index is not a non-negative integer")
    D = check_common(rep, ctx, cert, "e_system_hash")
    cs = ColSpace(D, nv)
    C = cs.C
    g = parse_poly(cert["g"], nv, True, "g")
    if g.size == 0:
        raise Malformed("g is the zero polynomial")
    if poly_degree(g) > D:
        raise Malformed("deg g > D")
    vals = [parse_hex_field(h, f"{key}[{i}]") for i, h in enumerate(cert[key])]
    if any(x.bit_length() > C for x in vals):
        raise Malformed(f"{key} has bits beyond the {C} columns of COL({D},{nv})")
    check_instance_block(rep, ctx, cert)
    Z = ctx.establish_Z()
    check_Z_claim(rep, cert, Z)

    gcols = cs.index(g)
    if form == "dual":
        Lam = np.zeros((len(vals), C), dtype=np.uint8)
        for i, x in enumerate(vals):
            Lam[i] = int_to_bits(x, C)
        ok_a, nrows, why = dual_check_a(Lam, sysd, D, cs)
        rep.check("a_macaulay_rows_in_U", ok_a, {"rows_checked": nrows, "violation": why})
        ok_b, det = dual_check_b(Lam, cs, nv)
        rep.check("b_closure", ok_b, det)
        lam_g = bool(len(vals)) and bool((Lam[:, gcols].astype(np.int64).sum(axis=1) & 1).any())
        rep.check("c_g_not_in_U", lam_g, {"|L|": len(vals)})
    else:
        ech = Echelon()
        for x in vals:
            ech.add(x)
        bad = None
        nrows = 0
        for k, Tc, idx in macaulay_blocks(sysd, D, cs, max_cells=200_000):
            for r_i in range(idx.shape[0]):
                nrows += 1
                if ech.reduce(cols_to_int(idx[r_i])):
                    bad = {"generator": k, "multiplier": mask_to_mono(int(Tc[r_i]))}
                    break
            if bad:
                break
        rep.check("a_macaulay_rows_in_U", bad is None, {"rows_checked": nrows, "violation": bad})
        ok_b, bad_b = True, None
        for low, row in sorted(ech.rows.items()):
            if low < cs.n_top:               # leading entry of degree D: not in B_{<=D-1}
                continue
            cols = int_to_bits(row, C).nonzero()[0]
            for j in range(nv):
                prod = cols_to_int(cs.index(cs.masks[cols] | np.int64(1 << j)))
                if ech.reduce(prod):
                    ok_b, bad_b = False, {"variable": j, "pivot_column": low}
                    break
            if not ok_b:
                break
        rep.check("b_closure", ok_b, {"echelon_rank": len(ech.rows), "violation": bad_b})
        rep.check("c_g_not_in_U", ech.reduce(cs.poly_vec_int(g)) != 0, {"dim_U": len(ech.rows)})

    # (d)
    if Z is None:
        rep.check("d_g_vanishes_on_Z", False, "Z not established")
        rep.check("d_g_is_reduced_gb_element", False, "Z not established")
    else:
        pts = np.array(Z, dtype=np.int64)
        vanishes = not eval_poly_on_points(g, pts).any() if pts.size else True
        rep.check("d_g_vanishes_on_Z", vanishes, {"|Z|": len(Z)})
        lm = max(g.tolist(), key=gkey)
        elem = reduced_gb_elements(Z, nv, {lm})[lm]
        is_red = elem is not None and elem == set(g.tolist())
        if not is_red and opts.allow_nonreduced_g and vanishes:
            rep.warnings.append("g is in I(Z) but is not the reduced GB element for its leading monomial "
                                "(--allow-nonreduced-g)")
            is_red = True
        rep.check("d_g_is_reduced_gb_element", is_red,
                  {"leading_monomial": mask_to_mono(lm), "g_equals_reduced_gb_element": elem == set(g.tolist())})
    check_instances_record(rep, ctx, Z)


# ---------------------------------------------------------------------------
# 6. sembin-wdag-v1
# ---------------------------------------------------------------------------

WDAG_REQ = COMMON_REQ + ("nodes", "outputs", "targets")
WDAG_OPT = ("Z", "instance", "levels")


def check_wdag(rep: Report, ctx: Ctx, cert):
    sysd, opts = ctx.sysd, ctx.opts
    nv, neq = sysd.nv, sysd.neq
    D = check_common(rep, ctx, cert, "g_system_hash")
    nodes, outputs, targets_raw = cert["nodes"], cert["outputs"], cert["targets"]
    if "levels" in cert and (not is_int(cert["levels"]) or cert["levels"] < 0):
        raise Malformed("levels is not a non-negative integer")
    if type(nodes) is not list or not nodes:
        raise Malformed("nodes must be a non-empty list")
    if type(outputs) is not list or type(targets_raw) is not list or len(outputs) != len(targets_raw):
        raise Malformed("outputs/targets must be lists of equal length")
    targets = [parse_poly(t, nv, True, f"targets[{i}]") for i, t in enumerate(targets_raw)]
    # parse the nodes
    P = []
    children = set()
    for i, nd in enumerate(nodes):
        if type(nd) is not dict or set(nd) != {"id", "rows", "prods"}:
            raise Malformed(f"node {i}: keys must be exactly id, rows, prods")
        if nd["id"] != i or not is_int(nd["id"]):
            raise Malformed(f"node {i}: id {nd['id']!r} does not equal its position")
        if type(nd["rows"]) is not list or type(nd["prods"]) is not list:
            raise Malformed(f"node {i}: rows/prods must be lists")
        rows = []
        for r in nd["rows"]:
            if type(r) is not list or len(r) != 2 or not is_int(r[1]):
                raise Malformed(f"node {i}: bad row {r!r}")
            rows.append((parse_mono(r[0], nv, True, f"node {i} row"), r[1]))
        prods = []
        for pr in nd["prods"]:
            if type(pr) is not list or len(pr) != 2 or not is_int(pr[0]) or not is_int(pr[1]) \
                    or not (0 <= pr[0] < nv):
                raise Malformed(f"node {i}: bad prod {pr!r}")
            prods.append((pr[0], pr[1]))
            children.add(pr[1])
        P.append((rows, prods))
    for o in outputs:
        if not is_int(o) or not (0 <= o < len(nodes)):
            raise Malformed(f"output {o!r} is not a node id")
    keep = children | set(outputs)

    # (a)..(d) with exact polynomial evaluation
    viol = {"a": None, "b": None, "c": None, "d": None}
    polys, deg = {}, []
    for i, (rows, prods) in enumerate(P):
        parts = []
        for (mu, k) in rows:
            if not (0 <= k < neq):
                viol["b"] = viol["b"] or f"node {i}: row index {k} outside 0..{neq-1}"
                continue
            if sysd.degs[k] < 0:
                viol["b"] = viol["b"] or f"node {i}: row references the zero generator {k}"
                continue
            if mu.bit_count() + sysd.degs[k] > D:
                viol["b"] = viol["b"] or f"node {i}: deg(mu)+deg(f_{k}) = {mu.bit_count() + sysd.degs[k]} > D"
            parts.append(sysd.eqs[k] | np.int64(mu))
        for (j, c) in prods:
            if not (0 <= c < i):
                viol["a"] = viol["a"] or f"node {i}: child {c} is not < {i}"
                continue
            if deg[c] > D - 1:
                viol["c"] = viol["c"] or f"node {i}: child {c} has degree {deg[c]} > D-1"
            parts.append(polys[c] | np.int64(1 << j))     # c in children, hence stored
        p = pxor(parts)
        d_i = poly_degree(p)
        deg.append(d_i)
        if d_i > D:
            viol["d"] = viol["d"] or f"node {i}: degree {d_i} > D"
        if i in keep:
            polys[i] = p
        if viol["a"]:
            break
    if not viol["a"]:
        reach, stack = set(outputs), list(set(outputs))
        while stack:
            for (_j, c) in P[stack.pop()][1]:
                if c not in reach:
                    reach.add(c)
                    stack.append(c)
        rep.info["nodes_total"] = len(P)
        rep.info["nodes_unreachable_from_outputs"] = len(P) - len(reach)
    names = {"a": "a_child_order", "b": "b_row_degree", "c": "c_child_degree", "d": "d_node_degree"}
    for key in "abcd":
        rep.check(names[key], viol[key] is None, {"first_violation": viol[key], "nodes": len(P)})
    if viol["a"]:
        rep.check("e_outputs_equal_targets", False, "not evaluated (child order violated)")
        e_ok = False
    else:
        bad = [t for t, (o, tg) in enumerate(zip(outputs, targets))
               if not np.array_equal(polys[o], tg)]
        e_ok = not bad
        rep.check("e_outputs_equal_targets", e_ok, {"targets": len(targets), "mismatched_targets": bad})

    # (f) targets are a Groebner basis of I(Z) (Z by the checker's own code)
    Zl = None
    check_instance_block(rep, ctx, cert)
    Zl = ctx.establish_Z()
    check_Z_claim(rep, cert, Zl)
    if Zl is None:
        rep.check("f_groebner_basis", False, "Z not established")
    else:
        pts = np.array(Zl, dtype=np.int64)
        zero_target = [t for t, tg in enumerate(targets) if tg.size == 0]
        van_bad = [t for t, tg in enumerate(targets)
                   if tg.size and pts.size and eval_poly_on_points(tg, pts).any()]
        lms = [max(tg.tolist(), key=gkey) for tg in targets if tg.size]
        nstd = count_standard_monomials(lms, nv, len(Zl))
        f_ok = not zero_target and not van_bad and nstd == len(Zl)
        rep.check("f_groebner_basis", f_ok,
                  {"|Z|": len(Zl), "standard_monomials": nstd if nstd <= len(Zl) else f">{len(Zl)}",
                   "targets_not_vanishing_on_Z": van_bad, "zero_targets": zero_target})
        if f_ok:
            try:
                red = reduced_gb_elements(Zl, nv, set(lms))
                exact = all(red[max(tg.tolist(), key=gkey)] == set(tg.tolist()) for tg in targets)
                rep.info["targets_are_reduced_gb"] = bool(exact)
                if not exact:
                    rep.warnings.append("targets form a Groebner basis of I(Z) but are not the reduced GB")
            except Malformed as e:
                rep.info["targets_are_reduced_gb"] = None
                rep.warnings.append(f"reduced-GB comparison skipped: {e}")
    check_instances_record(rep, ctx, Zl)


# ---------------------------------------------------------------------------
# 7. orchestration
# ---------------------------------------------------------------------------

REQUIRED = {
    ANN_SCHEMA: ("e_system_hash", "system_file_canonical", "Z_enumeration", "a_macaulay_rows_in_U",
                 "b_closure", "c_g_not_in_U", "d_g_vanishes_on_Z", "d_g_is_reduced_gb_element"),
    WDAG_SCHEMA: ("g_system_hash", "system_file_canonical", "Z_enumeration", "a_child_order", "b_row_degree",
                  "c_child_degree", "d_node_degree", "e_outputs_equal_targets", "f_groebner_basis"),
}


def run_check(system_bytes: bytes, cert_bytes: bytes, opts: Options = None) -> dict:
    """pure function used by the CLI and the tests -> verdict dict"""
    opts = opts or Options()
    rep = Report()
    out = {"verdict": "reject", "schema": None}
    t0 = time.time()
    try:
        sysd = parse_system(system_bytes)
        out["system_sha256"] = sysd.sha256
        out["nv"], out["neq"] = sysd.nv, sysd.neq
        cert = load_json(cert_bytes)
        if type(cert) is not dict:
            raise Malformed("certificate is not a JSON object")
        out["cert_file_sha256"] = sha256_hex(cert_bytes)
        out["cert_sha256"] = sha256_hex(canon_json_bytes(cert))
        if opts.expect_cert_sha256 is not None:
            rep.check("cert_expected_hash", out["cert_sha256"] == opts.expect_cert_sha256,
                      {"expected": opts.expect_cert_sha256, "recomputed": out["cert_sha256"]})
        schema = cert.get("schema")
        out["schema"] = schema if isinstance(schema, str) else None
        ctx = Ctx(sysd, opts, rep)
        if schema == ANN_SCHEMA:
            check_keys(cert, ANN_REQ, ANN_OPT, opts)
            check_ann(rep, ctx, cert)
        elif schema == WDAG_SCHEMA:
            check_keys(cert, WDAG_REQ, WDAG_OPT, opts)
            check_wdag(rep, ctx, cert)
        else:
            raise Malformed(f"unknown certificate schema {schema!r}")
        missing = [c for c in REQUIRED[schema] if c not in rep.checks]
        if missing:
            raise RuntimeError(f"internal error: mandatory checks not run: {missing}")
        out["verdict"] = "accept" if rep.all_ok() else "reject"
        if ctx.Z is not None:
            out["Z_size"] = len(ctx.Z)
        out["Z_methods"] = ctx.Z_methods
    except Malformed as e:
        out["verdict"] = "reject"
        out["malformed"] = str(e)
    except Exception as e:                      # never accept on an internal error
        out["verdict"] = "error"
        out["error"] = f"{type(e).__name__}: {e}"
    out["checks"] = rep.checks
    out["failed_checks"] = sorted(k for k, v in rep.checks.items() if not v["ok"])
    out["warnings"] = rep.warnings
    out["weakened"] = rep.weakened
    out["info"] = rep.info
    out["elapsed_s"] = round(time.time() - t0, 3)
    return to_py(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Independent checker for sembin-ann-v1 / sembin-wdag-v1 certificates.")
    ap.add_argument("--system", required=True, help="systems/<key>.sys.json.gz (sembin-sys-v1)")
    ap.add_argument("--cert", required=True, help="certificate json.gz (sembin-ann-v1 or sembin-wdag-v1)")
    ap.add_argument("--z-bruteforce", action="store_true",
                    help="also run the bit-sliced brute force for Z whenever nv <= --max-brute-nv "
                         "(without the flag it runs automatically when nv <= --auto-brute-nv)")
    ap.add_argument("--max-brute-nv", type=int, default=24)
    ap.add_argument("--auto-brute-nv", type=int, default=20)
    ap.add_argument("--expect-system-sha256", help="M-10 hash the system must have")
    ap.add_argument("--expect-cert-sha256", help="cert_sha256 the certificate must have")
    ap.add_argument("--instances", help="instances.jsonl.gz holding the M-10 record to cross-check")
    ap.add_argument("--skip-descent", action="store_true",
                    help="do not re-derive the raw Weil descent (WEAKENS the verdict; reported)")
    ap.add_argument("--allow-nonreduced-g", action="store_true")
    ap.add_argument("--allow-extra-keys", action="store_true")
    ap.add_argument("--lenient-canonical", action="store_true")
    ap.add_argument("--out", help="also write the JSON verdict to this file (the 'verdict file' keyed by cert_sha256)")
    a = ap.parse_args(argv)
    try:
        sb, _ = read_maybe_gz(a.system)
        cb, _ = read_maybe_gz(a.cert)
    except (OSError, Malformed) as e:
        print(json.dumps({"verdict": "error", "error": f"cannot read input: {e}"}, indent=2))
        return 2
    opts = Options(z_bruteforce=a.z_bruteforce, max_brute_nv=a.max_brute_nv, auto_brute_nv=a.auto_brute_nv,
                   expect_system_sha256=a.expect_system_sha256, expect_cert_sha256=a.expect_cert_sha256,
                   instances=a.instances, skip_descent=a.skip_descent, allow_nonreduced_g=a.allow_nonreduced_g,
                   allow_extra_keys=a.allow_extra_keys, lenient_canonical=a.lenient_canonical)
    res = run_check(sb, cb, opts)
    text = json.dumps(res, indent=2, sort_keys=True)
    if a.out:
        with open(a.out, "w") as f:
            f.write(text + "\n")
    print(text)
    return {"accept": 0, "reject": 1}.get(res["verdict"], 3)


if __name__ == "__main__":
    sys.exit(main())
