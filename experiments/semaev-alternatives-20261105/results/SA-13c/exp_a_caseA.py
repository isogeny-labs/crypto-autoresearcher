# Step (a), H-sep-free level-2 coverage, exact. p=103 (3 mod 4), E: y^2=x^3+7. For every pair x1<x2 of x-coordinates of E(F_p) with
# tau1 != tau2 (roots x(P1+P2), x(P1-P2) of S_x mod p), Lambda_x = {u in Z^5 : p^2 | u(tau_i), p | u'(tau_i), i=1,2} (step_a.md A1).
# For a box W (W_j < p^2/2) we enumerate (u2,u3,u4) in the box (numpy), solve (u0,u1) mod p^2 from u(tau_i)=0, lift symmetrically,
# test the box and p | u'(tau_i). Every box vector is classified: Case A (u != 0 mod p) structural (u parallel to s2(x) over Z) or
# wraparound; Case B (u = 0 mod p) structural (u/p divisible by S_x over Z) or wraparound.
import numpy as np, json, math, time, sys
p = 103; q = p * p; a, b = 0, 7
def legendre_sqrt(r):
    r %= p
    if r == 0: return 0
    if pow(r, (p - 1) // 2, p) != 1: return None
    return pow(r, (p + 1) // 4, p)   # p = 3 mod 4
xs = []
for x in range(1, p):
    y = legendre_sqrt(x ** 3 + a * x + b)
    if y: xs.append((x, y))
def add(P, Q):
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2:
        if (y1 + y2) % p == 0: return None
        l = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else: l = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (l * l - x1 - x2) % p; return (x3, (l * (x1 - x3) - y1) % p)
pairs = []
for i in range(len(xs)):
    for j in range(i + 1, len(xs)):
        P1, P2 = xs[i], xs[j]
        R1 = add(P1, P2); R2 = add(P1, (P2[0], (-P2[1]) % p))
        if R1 is None or R2 is None or R1[0] == R2[0]: continue
        x1, x2 = P1[0], P2[0]
        e1, e2 = x1 + x2, x1 * x2
        G = ((e2 - a) ** 2 - 4 * b * e1, -2 * (e1 * (e2 + a) + 2 * b), (x2 - x1) ** 2)
        assert (G[0] + G[1] * R1[0] + G[2] * R1[0] ** 2) % p == 0 and (G[0] + G[1] * R2[0] + G[2] * R2[0] ** 2) % p == 0
        pairs.append((x1, x2, R1[0], R2[0], G))
print("p=%d, %d x-coordinates, %d pairs with distinct roots" % (p, len(xs), len(pairs)), flush=True)
def divides_over_Z(u, G):            # does S_x divide the integer polynomial u (deg<=4)? exact long division
    G0, G1, G2 = G; r = list(u)
    if G2 == 0: return False
    for k in (4, 3, 2):
        if r[k] % G2: return False
        c = r[k] // G2; r[k] -= c * G2; r[k - 1] -= c * G1; r[k - 2] -= c * G0
    return r[0] == 0 and r[1] == 0
import sympy as sp
_T = sp.symbols('T')
def is_c_square(u):                  # u(T) = c * m(T)^2 over Z for an integer quadratic m (a short lift of S_x mod p, squared)?
    f = sp.Poly(sum(int(c) * _T ** k for k, c in enumerate(u)), _T)
    if f.degree() != 4: return False
    g = sp.gcd(f, f.diff(_T))
    if g.degree() != 2: return False
    qt, r = sp.div(f, g ** 2)
    return r.is_zero and qt.degree() == 0
def classify(u, G):
    G0, G1, G2 = G
    s2 = (G0 * G0, 2 * G0 * G1, 2 * G0 * G2 + G1 * G1, 2 * G1 * G2, G2 * G2)
    if any(c % p for c in u):
        par = all(u[j] * s2[k] == u[k] * s2[j] for j in range(5) for k in range(j + 1, 5))
        if par: return 'A_struct'
        return 'A_sq' if is_c_square(u) else 'A_wrap'
    v = [c // p for c in u]
    return 'B_struct' if divides_over_Z(v, G) else 'B_wrap'
def run_box(W):
    W0, W1, W2, W3, W4 = W
    g2, g3, g4 = np.meshgrid(np.arange(-W2, W2 + 1), np.arange(-W3, W3 + 1), np.arange(-W4, W4 + 1), indexing='ij')
    g2 = g2.ravel().astype(np.int64); g3 = g3.ravel().astype(np.int64); g4 = g4.ravel().astype(np.int64)
    flags = {k: 0 for k in ('A_struct', 'A_sq', 'A_wrap', 'B_struct', 'B_wrap')}; covered = 0; wrap_only = 0; n_struct = 0
    for (x1, x2, t1, t2, G) in pairs:
        inv = pow(t1 - t2, -1, q)
        r1 = (g2 * (t1 ** 2 % q) + g3 * (t1 ** 3 % q) + g4 * (t1 ** 4 % q)) % q
        r2 = (g2 * (t2 ** 2 % q) + g3 * (t2 ** 3 % q) + g4 * (t2 ** 4 % q)) % q
        u1 = (-(r1 - r2) * inv) % q; u0 = (-r1 - u1 * t1) % q
        u1 = np.where(u1 > q // 2, u1 - q, u1); u0 = np.where(u0 > q // 2, u0 - q, u0)
        ok = (np.abs(u0) <= W0) & (np.abs(u1) <= W1)
        d1 = (u1 + 2 * g2 * t1 + 3 * g3 * (t1 ** 2) + 4 * g4 * (t1 ** 3)) % p
        d2 = (u1 + 2 * g2 * t2 + 3 * g3 * (t2 ** 2) + 4 * g4 * (t2 ** 3)) % p
        ok &= (d1 == 0) & (d2 == 0)
        idx = np.nonzero(ok)[0]
        kinds = set()
        for i in idx:
            u = (int(u0[i]), int(u1[i]), int(g2[i]), int(g3[i]), int(g4[i]))
            if u == (0, 0, 0, 0, 0): continue
            kinds.add(classify(u, G))
        if kinds:
            covered += 1
            for k in kinds: flags[k] += 1
            if 'A_struct' in kinds or 'B_struct' in kinds: n_struct += 1
            else: wrap_only += 1
    om = W0 * W1 * W2 * W3 * W4
    return dict(W=W, omega=om, log_p_omega=math.log(om) / math.log(p), cost=max(1, 2 * (om // q)), covered=covered,
                x_with=flags, structural=n_struct, wrap_only=wrap_only, heuristic_wrap=len(pairs) * 32 * om / p ** 6)
boxes = [(50, 20, 5, 3, 2), (200, 100, 10, 5, 3), (1000, 300, 15, 6, 4), (5000, 1000, 20, 8, 5), (5000, 5000, 25, 10, 6),
         (5000, 5000, 30, 20, 10), (2, 2, 30, 30, 30), (5000, 2, 2, 2, 5000), (5000, 5000, 2, 30, 30),
         (256, 128, 64, 32, 16), (1296, 432, 144, 48, 16), (4096, 1024, 256, 64, 16), (5000, 2000, 500, 100, 20)]
rows = []
for W in boxes:
    t = time.time(); r = run_box(W); r['time'] = round(time.time() - t, 1); rows.append(r)
    print("W=%s log_p(omega)=%.2f cost=%d covered=%d structural=%d wrap_only=%d flags=%s heur_wrap=%.3f (%.0fs)" % (
        W, r['log_p_omega'], r['cost'], r['covered'], r['structural'], r['wrap_only'], r['x_with'], r['heuristic_wrap'], r['time']), flush=True)
json.dump(dict(p=p, n_pairs=len(pairs), rows=rows), open('exp_a_caseA.json', 'w'), indent=1)
