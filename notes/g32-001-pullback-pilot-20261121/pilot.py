"""G32-001 WP1 pilot, v2: size-matched comparison of preimage-defined bases.

All primary families are negation-closed (x and -x kept together) and are
trimmed to EXACTLY the same number of points, so density comparisons are
apples-to-apples. The uniform family is reported separately as a contrast and
is deliberately NOT the primary null (see the G31-001 replication: a
non-negation-closed null is not exchangeable).
"""
import random, json, math

def sqrt_mod(a, p):
    a %= p
    if a == 0: return 0
    if pow(a, (p - 1) // 2, p) != 1: return None
    if p % 4 == 3: return pow(a, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0: q //= 2; s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1: z += 1
    m_, c, t, r = s, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1: t2 = t2 * t2 % p; i += 1
        b = pow(c, 1 << (m_ - i - 1), p)
        m_, c, t, r = i, b * b % p, t * b * b % p, r * b % p
    return r

class Curve:
    def __init__(self, p, a, b): self.p, self.a, self.b = p, a % p, b % p
    def rhs(self, x): return (x * x % self.p * x + self.a * x + self.b) % self.p
    def points(self):
        p, out = self.p, []
        for x in range(p):
            y = sqrt_mod(self.rhs(x), p)
            if y is None: continue
            out.append((x, y))
            if y: out.append((x, (-y) % p))
        out.append(None)
        return out
    def neg(self, P): return None if P is None else (P[0], (-P[1]) % self.p)
    def add(self, P, Q):
        p = self.p
        if P is None: return Q
        if Q is None: return P
        if P[0] == Q[0]:
            if (P[1] + Q[1]) % p == 0: return None
            lam = (3 * P[0] * P[0] + self.a) * pow(2 * P[1], -1, p) % p
        else:
            lam = (Q[1] - P[1]) * pow(Q[0] - P[0], -1, p) % p
        x3 = (lam * lam - P[0] - Q[0]) % p
        return (x3, (lam * (P[0] - x3) - P[1]) % p)

def orbits(E, aff):
    seen, out = set(), []
    for P in aff:
        if P[0] in seen: continue
        seen.add(P[0]); out.append([P, E.neg(P)] if P[1] else [P])
    return out

def trim(orb_list, N):
    """Keep whole +-orbits until exactly N points."""
    out = []
    for orb in orb_list:
        if len(out) + len(orb) > N: break
        out.extend(orb)
    return out

def tuple_counts(E, base, m):
    cur = {P: 1 for P in base}
    for _ in range(m - 1):
        nxt = {}
        for P, cp in cur.items():
            for Q in base:
                S = E.add(P, Q)
                nxt[S] = nxt.get(S, 0) + cp
        cur = nxt
    return cur

def measure(E, base, targets, m, G):
    cnt = tuple_counts(E, base, m)
    hits = [cnt.get(t, 0) for t in targets]
    lam = len(base) ** m / G
    return dict(size=len(base), lam=lam, mean=sum(hits) / len(hits),
                mean_over_lam=(sum(hits) / len(hits)) / lam if lam else 0,
                rate=sum(1 for h in hits if h) / len(hits),
                pred_rate=1 - math.exp(-lam), maxhit=max(hits))

def sumset(E, base):
    S2, mult = set(), {}
    for P in base:
        for Q in base:
            S = E.add(P, Q); S2.add(S); mult[S] = mult.get(S, 0) + 1
    S3 = set()
    for P in S2:
        for Q in base: S3.add(E.add(P, Q))
    return dict(S2=len(S2), S3=len(S3), pair_max=max(mult.values()),
                at_O=mult.get(None, 0), pairs=len(base) ** 2)

def run(p, a, b, N=24, seed=1):
    rng = random.Random(seed)
    E = Curve(p, a, b); pts = E.points(); G = len(pts)
    aff = [P for P in pts if P is not None]
    orbs = orbits(E, aff)

    win_orbs = [o for o in orbs if o[0][0] < p]
    win_orbs.sort(key=lambda o: o[0][0])
    rng.shuffle(orbs)

    def pullback_orbs(c):
        xs = rng.sample(range(p), 8 * N)
        T = set((x * x + c) % p for x in xs)
        sel = [o for o in orbs if (o[0][0] ** 2 + c) % p in T]
        return sel

    fams = {
        "window": trim(win_orbs, N),
        "pullback_sq": trim(pullback_orbs(0), N),
        "pullback_sq+c": trim(pullback_orbs(12345 % p), N),
        "rand_neg": trim(orbs, N),
    }
    targets = rng.sample(aff, min(400, len(aff)))
    out = {}
    for name, B in fams.items():
        row = {"sumset": sumset(E, B)}
        for m in (3, 4):
            row[f"m{m}"] = measure(E, B, targets, m, G)
        out[name] = row
    # uniform contrast at the same nominal size
    uni = rng.sample(aff, min(N, len(aff)))
    out["rand_unif_CONTRAST"] = {"sumset": sumset(E, uni)}
    for m in (3, 4):
        out["rand_unif_CONTRAST"][f"m{m}"] = measure(E, uni, targets, m, G)
    out["_meta"] = dict(p=p, a=a, b=b, G=G, targets=len(targets))
    return out

if __name__ == "__main__":
    res = {}
    for (p, a, b) in [(4099, 1, 1), (8191, 3, 5), (12289, 1, 7), (16381, 5, 11)]:
        if (4 * a ** 3 + 27 * b ** 2) % p == 0: continue
        res[f"p{p}"] = run(p, a, b, 24, seed=p)
    json.dump(res, open("/Volumes/SSD990/llm/tmp/opencode/g32-001/pilot_results.json", "w"), indent=1)
    for k, v in res.items():
        m = v["_meta"]
        print(f"\n== {k}  G={m['G']}  N=24  targets={m['targets']}")
        print(f"{'family':18s} {'|B|':>4s} {'m3 mean/lam':>12s} {'m3 rate':>8s} {'m3 pred':>8s} "
              f"{'m4 mean/lam':>12s} {'S2':>4s} {'S3':>5s} {'pairmax':>7s} {'atO':>4s}")
        for name, row in v.items():
            if name == "_meta": continue
            s = row["sumset"]
            print(f"{name:18s} {row['m3']['size']:4d} {row['m3']['mean_over_lam']:12.3f} "
                  f"{row['m3']['rate']:8.3f} {row['m3']['pred_rate']:8.3f} "
                  f"{row['m4']['mean_over_lam']:12.3f} {s['S2']:4d} {s['S3']:5d} "
                  f"{s['pair_max']:7d} {s['at_O']:4d}")
