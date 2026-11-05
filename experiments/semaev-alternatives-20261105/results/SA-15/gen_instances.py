"""SA-15: frozen planted m=4 box instance set. Deterministic (seeded). Single-threaded."""
import json, random, hashlib, math, sys
import cypari2
pari = cypari2.Pari(); pari.allocatemem(400*10**6)
from sympy.ntheory import sqrt_mod

A, Bc = 0, 7                       # y^2 = x^3 + 7
KS = [40, 56, 72, 96]
NINST = 100
SEED0 = 20261105

def iroot(n, k):
    lo, hi = 0, 1 << (n.bit_length() // k + 2)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid ** k <= n: lo = mid
        else: hi = mid - 1
    return lo

def pick_prime(k):
    """first prime >= 2^k with p = 1 mod 3 (ordinary j=0 curve) and prime group order N != p."""
    p = int(pari.nextprime(2 ** k))
    while True:
        if p % 3 == 1:
            E = pari.ellinit([A, Bc], p)
            N = int(pari.ellcard(E))
            if N != p and pari.isprime(N):
                return p, N
        p = int(pari.nextprime(p + 1))

# ---- implementation (1): affine, python ints
def add_aff(P, Q, p):
    if P is None: return Q
    if Q is None: return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and (y1 + y2) % p == 0: return None
    if P == Q: l = (3 * x1 * x1 + A) * pow(2 * y1, -1, p) % p
    else: l = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (l * l - x1 - x2) % p
    return (x3, (l * (x1 - x3) - y1) % p)

# ---- implementation (2): Jacobian coordinates (independent code path)
def jac_add(P, Q, p):
    if P is None: return Q
    if Q is None: return P
    X1, Y1, Z1 = P; X2, Y2, Z2 = Q
    Z1Z1 = Z1 * Z1 % p; Z2Z2 = Z2 * Z2 % p
    U1 = X1 * Z2Z2 % p; U2 = X2 * Z1Z1 % p
    S1 = Y1 * Z2 * Z2Z2 % p; S2 = Y2 * Z1 * Z1Z1 % p
    if U1 == U2:
        if S1 != S2: return None
        # doubling
        XX = X1 * X1 % p; YY = Y1 * Y1 % p; YYYY = YY * YY % p
        S = 2 * ((X1 + YY) ** 2 - XX - YYYY) % p
        M = (3 * XX + A * Z1Z1 * Z1Z1) % p
        X3 = (M * M - 2 * S) % p
        return (X3, (M * (S - X3) - 8 * YYYY) % p, 2 * Y1 * Z1 % p)
    H = (U2 - U1) % p; I = 4 * H * H % p; J = H * I % p; r = 2 * (S2 - S1) % p; V = U1 * I % p
    X3 = (r * r - J - 2 * V) % p
    return (X3, (r * (V - X3) - 2 * S1 * J) % p, ((Z1 + Z2) ** 2 - Z1Z1 - Z2Z2) * H % p)
def to_jac(P): return (P[0], P[1], 1)
def from_jac(J, p):
    if J is None: return None
    zi = pow(J[2], -1, p); return (J[0] * zi * zi % p, J[1] * zi ** 3 % p)

def S3(x1, x2, X, p):
    return ((x1 - x2) ** 2 * X * X - 2 * ((x1 + x2) * (x1 * x2 + A) + 2 * Bc) * X + (x1 * x2 - A) ** 2 - 4 * Bc * (x1 + x2)) % p

def solve_c(pts, p):
    """RR: f = xy + c1 x^2 + c2 y + c3 x + c4 vanishing at 4 points -> (c1..c4) mod p (Gaussian elim)."""
    M = [[x * x % p, y, x, 1, (-x * y) % p] for (x, y) in pts]
    n = 4
    for i in range(n):
        piv = next(r for r in range(i, n) if M[r][i] % p)
        M[i], M[piv] = M[piv], M[i]
        inv = pow(M[i][i], -1, p); M[i] = [v * inv % p for v in M[i]]
        for r in range(n):
            if r != i and M[r][i]:
                f = M[r][i]; M[r] = [(a - f * b) % p for a, b in zip(M[r], M[i])]
    return [M[i][4] for i in range(n)]

def e_of_alpha(c1, c2, c3, xR, yRneg, p):
    """e1..e4 from the three free alphas (c1,c2,c3); c4 from f(-R)=0; all quadratic in alpha."""
    c4 = (-(xR * yRneg + c1 * xR * xR + c2 * yRneg + c3 * xR)) % p
    s1 = (c1 * c1 - 2 * c2) % p
    s2 = (A + c2 * c2 - 2 * c1 * c3) % p
    s3 = (c3 * c3 + 2 * c1 * c4 - Bc - 2 * A * c2) % p
    s4 = (2 * Bc * c2 + A * c2 * c2 - 2 * c3 * c4) % p
    e1 = (s1 - xR) % p
    e2 = (s2 - xR * e1) % p
    e3 = (s3 - xR * e2) % p
    e4 = (s4 - xR * e3) % p
    return (e1, e2, e3, e4), c4

def sgn_pm(v, p): return v if v <= p // 2 else v - p

def build(k):
    p, N = pick_prime(k)
    B = iroot(p, 5)
    E = pari.ellinit([A, Bc], p)
    rng = random.Random(SEED0 + k)
    inst, wit = [], []
    while len(inst) < NINST:
        xs = []
        while len(xs) < 4:
            x = rng.randrange(1, B + 1)
            if x in xs: continue
            r = (x ** 3 + A * x + Bc) % p
            if pow(r, (p - 1) // 2, p) != 1: continue
            xs.append(x)
        pts = []
        for x in xs:
            y = sqrt_mod((x ** 3 + A * x + Bc) % p, p)
            if rng.random() < 0.5: y = p - y
            pts.append((x, int(y)))
        # (1) affine, left-to-right
        R1 = add_aff(add_aff(add_aff(pts[0], pts[1], p), pts[2], p), pts[3], p)
        # (2) Jacobian, (P4+P2)+(P3+P1)
        J = jac_add(jac_add(to_jac(pts[3]), to_jac(pts[1]), p), jac_add(to_jac(pts[2]), to_jac(pts[0]), p), p)
        R2 = from_jac(J, p)
        # (3) PARI
        acc = pari.elladd(E, [pts[0][0], pts[0][1]], [pts[1][0], pts[1][1]])
        for q in pts[2:]: acc = pari.elladd(E, acc, [q[0], q[1]])
        assert R1 is not None and R1 == R2, "affine/jacobian mismatch"
        assert [int(acc[0]), int(acc[1])] == list(R1), "pari mismatch"
        xR, yR = R1
        # skip degenerate: x_R must differ from every x_i and be nonzero y
        if xR in xs or yR == 0: continue
        assert (yR * yR - (xR ** 3 + A * xR + Bc)) % p == 0
        # (4) group order kills R (R has prime order N)
        assert list(map(int, pari.ellmul(E, [xR, yR], N))) == [0] or str(pari.ellmul(E, [xR, yR], N)) == "[0]"
        # (5) S_5 chain witness (S_3 relations hold mod p along the addition chain)
        Q12 = add_aff(pts[0], pts[1], p); Q123 = add_aff(Q12, pts[2], p)
        assert S3(xs[0], xs[1], Q12[0], p) == 0 and S3(Q12[0], xs[2], Q123[0], p) == 0 and S3(Q123[0], xs[3], xR, p) == 0
        # (6) Riemann-Roch / Abel: f through P1..P4 must also vanish at -R
        c = solve_c(pts, p)
        c1, c2, c3, c4 = c
        xm, ym = xR, (-yR) % p
        assert (xm * ym + c1 * xm * xm + c2 * ym + c3 * xm + c4) % p == 0, "RR/Abel check failed"
        # (7) quadratic map alpha -> e reproduces the true Vieta coordinates
        es, c4b = e_of_alpha(c1, c2, c3, xR, ym, p)
        e_true = (sum(xs), sum(xs[i] * xs[j] for i in range(4) for j in range(i + 1, 4)),
                  sum(xs[i] * xs[j] * xs[l] for i in range(4) for j in range(i + 1, 4) for l in range(j + 1, 4)),
                  xs[0] * xs[1] * xs[2] * xs[3])
        assert c4b == c4 and es == tuple(v % p for v in e_true), "alpha->e mismatch"
        # (8) Vieta box
        assert e_true[0] <= 4 * B and e_true[1] <= 6 * B ** 2 and e_true[2] <= 4 * B ** 3 and e_true[3] <= B ** 4
        # (9) octic: x_R is a root of prod over the 8 sign classes of (T - x(P1 +- P2 +- P3 +- P4))
        roots = set()
        for s2 in (1, -1):
            for s3 in (1, -1):
                for s4 in (1, -1):
                    q = pts[0]
                    for s, pt in ((s2, pts[1]), (s3, pts[2]), (s4, pts[3])):
                        q = add_aff(q, pt if s == 1 else (pt[0], (-pt[1]) % p), p)
                    roots.add(q[0])
        assert xR in roots and len(roots) == 8
        idx = len(inst)
        inst.append({"id": f"p{k}-{idx:03d}", "R": {"x": str(xR), "y": str(yR)}})
        wit.append({"id": f"p{k}-{idx:03d}", "points": [{"x": str(x), "y": str(y)} for x, y in pts],
                    "e": [str(v) for v in e_true], "alpha_c1_c2_c3": [str(c1), str(c2), str(c3)], "c4": str(c4)})
    return {"log2p": k, "p": str(p), "N": str(N), "a": A, "b": Bc, "B": B, "instances": inst}, wit

if __name__ == "__main__":
    pub = {"name": "SA-15 planted m=4 box instance set", "campaign": "semaev-alternatives-20261105",
           "problem": "given R and B, find x_1..x_4 in [1,B] and signs with sum(+-P_i)=R on y^2=x^3+7 over F_p; B=floor(p^(1/5))",
           "seed_base": SEED0, "groups": []}
    wits = {"name": "SA-15 planted witnesses (answers)", "groups": []}
    for k in KS:
        g, w = build(k)
        pub["groups"].append(g); wits["groups"].append({"log2p": k, "witnesses": w})
        print(k, g["p"], g["N"], g["B"], len(g["instances"]), flush=True)
    for name, obj in (("instances.json", pub), ("witnesses.json", wits)):
        s = json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n"
        open(f"/home/user/semaev-runs/SA-15/{name}", "w").write(s)
        print(name, hashlib.sha256(s.encode()).hexdigest())
