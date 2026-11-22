"""run_pilot.py — G31-001 validation-hook experiment.

Frozen design (written to frozen_config.json with a timestamp BEFORE any
target is sampled; nothing below is re-tuned after seeing results):

  Curves: deterministic from seeds (toycurve-style sha256 derivation of p,a,b).
    bits 17,18,20  seeds 31001,31002,31003   (main ladder)
    bits 13        seed  31011               (scale check, >=1000 targets)
    Accept first t with nonsingular curve, #E = c*n, n prime, c in {1,2,3}.
  Subgroup G = <g> of order n (largest prime factor); factor base
    B_raw = {P in E(F_p) : 0 <= x(P) < N}, both y-signs; B_G = {c*P} deduped,
    O removed (recorded).  Arms: N3 = icbrt(p), N2 = isqrt(p).
  m in {3,4}; bonus m=5 (d=6, the hook's own r=5 embedding) at N5 on the
    scale curve.  Targets: 320 (main), 1200 (scale); rng keyed per cell.
  Dictionary embedding: d = m+1 (see sanity.py: containment of phi(+sum) at
    d=6 fails by design; the dictionary is phi(-sum P_i) in span of the
    scheme columns).  Hook-literal (d=6, phi(+Q), distinct-point columns) is
    recorded as the control.
  Charter test: same-size generic sets (uniform, and symmetric under negation)
    replacing B_G; same targets, same counts.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import sys
import time

import numpy as np

from ec import EC, phi, derivs, rank_p

T0 = time.time()
OKEY = np.uint64(1 << 52)


def ekey(P, p):
    return OKEY if P is None else np.uint64(P[0] * p + P[1])


def k2p(key, p):
    key = int(key)
    return None if key == 1 << 52 else (key // p, key % p)


def seed_int(seed: int, tag: str) -> int:
    return int(hashlib.sha256(f"{seed}:{tag}".encode()).hexdigest(), 16)


# --------------------------------------------------------------- curve setup
def find_curve(bits: int, seed: int, log):
    import sympy
    base = (1 << bits) + seed_int(seed, "p") % (1 << (bits - 6))
    p = int(sympy.nextprime(base))
    for t in range(1, 5000):
        a = seed_int(seed, f"a{t}") % p
        b = seed_int(seed, f"b{t}") % p
        try:
            E = EC(p, a, b)
        except AssertionError:
            continue
        nE = E.order_hasse()
        for c in (1, 2, 3):
            if nE % c == 0 and sympy.isprime(nE // c):
                n = nE // c
                if n < (1 << (bits - 3)):
                    continue
                # generator of G
                g = None
                for x in range(1, 10000):
                    R = E.lift_x(x)
                    if R is None:
                        continue
                    P = E.mul(c, R)
                    if P is not None and E.mul(n, P) is None:
                        g = P
                        break
                if g is None:
                    continue
                exact = E.order_naive()
                assert exact == nE, (exact, nE)
                log(f"curve bits={bits} seed={seed}: p={p} a={a} b={b} "
                    f"#E={nE} (= {c}*{n}, n prime; naive count verified)")
                return E, nE, c, n, g
    raise RuntimeError("no curve found")


class InvTable:
    def __init__(self, p: int):
        self.p = p
        inv = np.zeros(p, dtype=np.int64)
        inv[1] = 1
        # sequential linear modular inverse recurrence
        for i in range(2, p):
            inv[i] = (p - (p // i) * inv[p % i] % p) % p
        self.inv = inv


class Ctx:
    """Curve + inverse table + point-set with vectorized pair-sum table."""

    def __init__(self, E: EC, invt: InvTable):
        self.E = E
        self.p = E.p
        self.inv = invt

    def add_many(self, P, Ux, Uy):
        """P + U_i for int64 arrays of affine points U (no O in U; U may
        contain 2-torsion).  Returns int64 (Rx, Ry) and bool isO."""
        p = self.p
        px, py = P
        a = self.E.a
        isO = (Ux == px) & ((Uy + py) % p == 0)     # U == -P  =>  P+U = O
        same = (Ux == px) & (Uy == py)              # doubling case
        den = np.where(same, (2 * py) % p, (Ux - px) % p)
        den = np.where(isO | (den == 0), 1, den)
        num = np.where(same, (3 * px * px + a) % p, (Uy - py) % p)
        lam = (num * self.inv.inv[den]) % p
        Rx = (lam * lam % p - px - Ux) % p
        Ry = (lam * ((px - Rx) % p) % p - py) % p
        return Rx, Ry, isO

    def pair_table(self, B):
        """B: list of affine points (no O). Ordered pair sums P_i+P_j with
        counts and first-witness pair indices (into B). O-sums kept."""
        p = self.p
        b = len(B)
        Bx = np.array([P[0] for P in B], dtype=np.int64)
        By = np.array([P[1] for P in B], dtype=np.int64)
        keys = np.empty(b * b, dtype=np.uint64)
        for i in range(b):
            Rx, Ry, isO = self.add_many(B[i], Bx, By)
            k = (Rx * p + Ry).astype(np.uint64)
            k[isO] = OKEY
            keys[i * b:(i + 1) * b] = k
        uk, idx, cnt = np.unique(keys, return_index=True, return_counts=True)
        self.B = B
        self.uk = uk
        self.cnt = cnt.astype(np.int64)
        self.fp1 = (idx // b).astype(np.int64)
        self.fp2 = (idx % b).astype(np.int64)
        # decoded coordinates of the unique sums (O rows flagged)
        self.so = uk == OKEY
        Sx = (uk // np.uint64(p)).astype(np.int64)
        Sy = (uk % np.uint64(p)).astype(np.int64)
        Sx[self.so] = 0
        Sy[self.so] = 0
        self.Sx, self.Sy = Sx, Sy

    def r_m(self, Q, m):
        """Number of ordered m-tuples from B summing to Q (+ one witness).
        m=3: B x pair;  m=4: pair x pair."""
        p = self.p
        qx, qy = Q
        if m == 3:
            Bx = np.array([P[0] for P in self.B], dtype=np.int64)
            By = np.array([(-P[1]) % p for P in self.B], dtype=np.int64)
            Rx, Ry, isO = self.add_many(Q, Bx, By)     # Q - P3
            k = (Rx * p + Ry).astype(np.uint64)
            k[isO] = OKEY
            pos = np.clip(np.searchsorted(self.uk, k), 0, len(self.uk) - 1)
            hit = self.uk[pos] == k
            total = int((self.cnt[pos] * hit).sum())
            wit = None
            if total:
                w = int(np.argmax(hit))
                pk = int(k[w])
                pw = int(np.searchsorted(self.uk, np.uint64(pk)))
                i1, i2 = int(self.fp1[pw]), int(self.fp2[pw])
                wit = (self.B[i1], self.B[i2], self.B[w])
            return total, wit
        elif m == 4:
            Ux = self.Sx
            Uy = (-self.Sy) % p                        # S -> -S (O rows: 0)
            Rx, Ry, isO = self.add_many(Q, Ux, Uy)     # Q - S
            k = (Rx * p + Ry).astype(np.uint64)
            k[isO] = OKEY
            keyQ = np.uint64(qx * p + qy)
            k[self.so] = keyQ                          # Q - O = Q
            pos = np.clip(np.searchsorted(self.uk, k), 0, len(self.uk) - 1)
            hit = self.uk[pos] == k
            total = int((self.cnt * self.cnt[pos] * hit).sum())
            wit = None
            if total:
                w = int(np.argmax(hit))
                a1, a2 = int(self.fp1[w]), int(self.fp2[w])
                b1, b2 = int(self.fp1[pos[w]]), int(self.fp2[pos[w]])
                wit = (self.B[a1], self.B[a2], self.B[b1], self.B[b2])
            return total, wit
        raise ValueError(m)


# -------------------------------------------------------------- dictionaries
def scheme_cols(ctx_E, d, Ps):
    from collections import Counter
    cols = []
    for P, k in Counter(Ps).items():
        cols.extend(derivs(ctx_E, d, P, k - 1))
    return cols


def dict_check(E, Q, wit):
    """(correct, hook_literal) containment for witness decomposition sum=Q."""
    m = len(wit)
    d = m + 1
    cols = scheme_cols(E, d, wit)
    rk = rank_p(E.p, cols)
    correct = rank_p(E.p, cols, phi(E, d, E.neg(Q))) == rk
    # hook-literal control: d=6, distinct columns only, target phi(+Q)
    if 6 >= d:
        cols6 = []
        seen = set()
        for P in wit:
            if P not in seen:
                seen.add(P)
                cols6.append(phi(E, 6, P))
        rk6 = rank_p(E.p, cols6)
        hook = rank_p(E.p, cols6, phi(E, 6, Q)) == rk6
    else:
        hook = None
    return correct, hook


# ----------------------------------------------------------------- main cell
def run_cell(ctx, E, targets, m, rng, n_wit_dict=200, converse_n=3000):
    stats = dict(m=m, n_targets=len(targets), dec=0, r_tot=0, r_max=0,
                 dict_pass=0, dict_tot=0, hook_hit=0, hook_tot=0,
                 wit_repeat=0, wit_bad=0)
    dict_budget = n_wit_dict
    for Q in targets:
        r, wit = ctx.r_m(Q, m)
        stats["r_tot"] += r
        stats["r_max"] = max(stats["r_max"], r)
        if r:
            stats["dec"] += 1
            if wit is not None:
                S = None
                for P in wit:
                    S = E.add(S, P)
                if S != Q:                      # catches convolution bugs
                    stats["wit_bad"] += 1
                    wit = None
            if wit is not None and dict_budget > 0:
                dict_budget -= 1
                ok, hook = dict_check(E, Q, wit)
                stats["dict_tot"] += 1
                stats["dict_pass"] += 1 if ok else 0
                if hook is not None:
                    stats["hook_tot"] += 1
                    stats["hook_hit"] += 1 if hook else 0
                if len(set(wit)) < len(wit):
                    stats["wit_repeat"] += 1
    # converse: random schemes from B vs random Q (only m=3, d=4 is cheap)
    conv = None
    if m == 3 and converse_n:
        B = ctx.B
        b = len(B)
        n = ctx.n
        hit = trivial = bad = 0
        for _ in range(converse_n):
            Ps = [B[rng.randrange(b)] for _ in range(3)]
            k = rng.randrange(1, n)
            Q = E.mul(k, ctx.g)
            cols = scheme_cols(E, 4, Ps)
            rk = rank_p(E.p, cols)
            if rank_p(E.p, cols, phi(E, 4, Q)) == rk:
                hit += 1
                S = None
                for P in Ps:
                    S = E.add(S, P)
                negS = E.neg(S)
                if Q in Ps or Q == negS:
                    trivial += 1
                else:
                    bad += 1
        conv = dict(draws=converse_n, hits=hit, explained=trivial, violations=bad)
    stats["converse"] = conv
    return stats


def main():
    logf = open("run.log", "w")

    def log(*a):
        line = " ".join(str(x) for x in a)
        print(line)
        logf.write(line + f"   [+{time.time()-T0:.1f}s]\n")
        logf.flush()

    frozen = dict(
        frozen_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        ladder=[dict(bits=17, seed=31001), dict(bits=18, seed=31002),
                dict(bits=20, seed=31003)],
        scale=dict(bits=13, seed=31011),
        arms=dict(N3="icbrt(p)", N2="isqrt(p)"),
        bonus_N5_on_scale=True,
        m_values=[3, 4], m5_bonus=True,
        n_targets_main=320, n_targets_scale=1200,
        dict_witness_checks_per_cell=200,
        converse_draws=3000,
        charter_sets=["uniform", "symmetric"],
        rng_master_seed=77731001,
        note="parameters frozen here are never retuned after results",
    )
    with open("frozen_config.json", "w") as f:
        json.dump(frozen, f, indent=2)
    log("frozen config:", frozen["frozen_utc"])

    master_rng = random.Random(frozen["rng_master_seed"])
    results = dict(frozen=frozen, cells=[])

    jobs = [(c["bits"], c["seed"], False) for c in frozen["ladder"]] + \
           [(frozen["scale"]["bits"], frozen["scale"]["seed"], True)]

    for bits, seed, is_scale in jobs:
        E, nE, cof, n, g = find_curve(bits, seed, log)
        p = E.p
        invt = InvTable(p)
        nT = frozen["n_targets_scale"] if is_scale else frozen["n_targets_main"]
        arms = {}
        Ns = {"N2": math.isqrt(p), "N3": round(p ** (1.0 / 3.0))}
        if is_scale:
            Ns["N5"] = max(3, round(p ** 0.2))
        for arm, N in Ns.items():
            raw = E.points_x_window(N)
            Bset = {}
            removed_O = 0
            for P in raw:
                cP = E.mul(cof, P)
                if cP is None:
                    removed_O += 1
                    continue
                Bset[cP] = None
            B = list(Bset)
            sym = all(E.neg(P) in Bset for P in B)
            log(f"  arm {arm}: N={N} |B_raw|={len(raw)} |B_G|={len(B)} "
                f"cof={cof} O-removed={removed_O} closed_under_negation={sym}")
            ctx = Ctx(E, invt)
            ctx.n = n
            ctx.g = g
            ctx.pair_table(B)
            rng_key = seed_int(seed, f"{arm}.targets")
            rng = random.Random(rng_key)
            targets = []
            trng = random.Random(rng_key + 1)
            for _ in range(nT):
                targets.append(E.mul(trng.randrange(1, n), g))
            cell_info = dict(bits=bits, seed=seed, p=p, a=E.a, b=E.b, nE=nE,
                             cofactor=cof, n=n, arm=arm, N=N,
                             abs_B_raw=len(raw), abs_B=len(B), nT=nT)
            # sanity: r_m symmetry r(Q)=r(-Q) spot check
            for m in ([5] if arm == "N5" else [3, 4]):
                if arm == "N5" and not is_scale:
                    continue
                if m == 5:
                    st = run_m5(E, ctx, targets, log)
                else:
                    st = run_cell(ctx, E, targets, m, rng)
                b = len(B)
                lam = b ** m / n
                frac = st["dec"] / st["n_targets"]
                st.update(m=m, lam=lam, frac_dec=frac, mean_r=st["r_tot"] / st["n_targets"])
                log(f"    m={m}: |B|={b} frac_decomp={frac:.4f} "
                    f"mean_r={st['mean_r']:.2f} lambda={lam:.3f} "
                    f"dict {st['dict_pass']}/{st['dict_tot']} "
                    f"hook-literal-hits {st['hook_hit']}/{st['hook_tot']}")
                results["cells"].append(dict(cell_info, **st))
                # charter test (skip for bonus m=5 arm)
                if m != 5 and arm != "N5":
                    for kind in ("uniform", "symmetric"):
                        B2 = make_generic(E, n, g, b, kind,
                                          random.Random(seed_int(seed, f"{arm}.{kind}")))
                        ctx2 = Ctx(E, invt)
                        ctx2.n = n
                        ctx2.g = g
                        ctx2.pair_table(B2)
                        st2 = run_cell(ctx2, E, targets, m, rng,
                                       n_wit_dict=30, converse_n=0)
                        lam2 = b ** m / n
                        f2 = st2["dec"] / st2["n_targets"]
                        st2.update(m=m, kind=kind, lam=lam2, frac_dec=f2,
                                   mean_r=st2["r_tot"] / st2["n_targets"])
                        log(f"      charter[{kind}] m={m}: frac={f2:.4f} "
                            f"mean_r={st2['mean_r']:.2f}")
                        results["cells"].append(dict(cell_info, charter=st2))
            results.setdefault("curves", []).append(cell_info)
        log(f"curve bits={bits} done")

    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)
    log("WROTE results.json")


def make_generic(E, n, g, b, kind, rng):
    S = {}
    if kind == "uniform":
        ks = set()
        while len(ks) < b:
            ks.add(rng.randrange(1, n))
        for k in ks:
            S[E.mul(k, g)] = None
    else:  # symmetric under negation
        half = b // 2
        while len(S) < half:
            S[E.mul(rng.randrange(1, n), g)] = None
        S = {P: None for P in S}
        for P in list(S):
            S[E.neg(P)] = None
        if len(S) < b:  # odd b: add one more point (its neg then joins)
            extra = E.mul(rng.randrange(1, n), g)
            S[extra] = None
            S[E.neg(extra)] = None
    return list(S)


def run_m5(E, ctx, targets, log):
    """Bonus: m=5 decomposition counts by direct enumeration (small B) +
    dictionary at d=6 (the hook's own embedding)."""
    B = ctx.B
    b = len(B)
    # ordered counts: pc2 (pairs), tc3 (triples)
    pc2 = {}
    for i in range(b):
        for j in range(b):
            s = E.add(B[i], B[j])
            pc2[s] = pc2.get(s, 0) + 1
    tc3 = {}
    for i in range(b):
        for j in range(b):
            sij = E.add(B[i], B[j])
            for k in range(b):
                s = E.add(sij, B[k])
                tc3[s] = tc3.get(s, 0) + 1
    stats = dict(m=5, n_targets=len(targets), dec=0, r_tot=0, r_max=0,
                 dict_pass=0, dict_tot=0, hook_hit=0, hook_tot=0, wit_repeat=0,
                 converse=None)
    for Q in targets:
        r = 0
        wit = None
        for (s2, c2) in pc2.items():
            c3 = tc3.get(E.add(Q, E.neg(s2)) if s2 is not None else Q)
            if c3:
                r += c2 * c3
                if wit is None:
                    # reconstruct a witness
                    for i in range(b):
                        for j in range(b):
                            if E.add(B[i], B[j]) == s2:
                                for k in range(b):
                                    for l in range(b):
                                        for mm in range(b):
                                            if E.add(E.add(B[k], B[l]), B[mm]) == \
                                                    (E.add(Q, E.neg(s2)) if s2 is not None else Q):
                                                wit = (B[i], B[j], B[k], B[l], B[mm])
                                                break
                                        if wit: break
                                    if wit: break
                                if wit: break
                        if wit: break
                            # note: this reconstruction is O(b^5) worst case but
                            # fires once per cell only
        stats["r_tot"] += r
        stats["r_max"] = max(stats["r_max"], r)
        if r:
            stats["dec"] += 1
            if wit is not None and stats["dict_tot"] < 50:
                ok, hook = dict_check(E, Q, wit)
                stats["dict_tot"] += 1
                stats["dict_pass"] += 1 if ok else 0
                if hook is not None:
                    stats["hook_tot"] += 1
                    stats["hook_hit"] += 1 if hook else 0
                if len(set(wit)) < 5:
                    stats["wit_repeat"] += 1
    return stats


if __name__ == "__main__":
    main()
