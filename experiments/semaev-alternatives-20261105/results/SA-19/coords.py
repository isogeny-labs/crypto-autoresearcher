"""SA-19 family (a): budget of the summation polynomial S^phi for coordinate functions phi of several curve models,
classified by degree and pole divisor.  For each phi: interpolate S^phi(u1,u2,u3) over F_PR (u_i = phi(P_i),
P1+P2+P3 = O), take its u3-coefficients as polynomials in (u1,u2), and compute the degree sequence sum w.
Writes results/coords.json."""
import sys, json, random, time
sys.path.insert(0, '/home/user/semaev-runs/SA-19')
from lib19 import *

p = PR; rng = random.Random(19)
out = []

def inv(v): return pow(v, -1, p)

def analyse(label, E, phi, note='', dmaxmax=9):
    t = time.time()
    d, polys = minimal_summation_poly(E, phi, rng, p, dmaxmax=dmaxmax)
    if d is None:
        out.append(dict(label=label, note=note, degree=None)); print(label, 'no relation up to degree', dmaxmax); return
    S = polys[0]
    co = coeffs_in_last(S, 3)
    n, seq, w = budget(co, p)
    # also the weighted budget if the factor base is |u| <= B (same thing) ; total degree of S
    rec = dict(label=label, note=note, degree_per_var=d, nullity=len(polys), n_coeffs=len(co),
               coef_degrees=[pdeg(c) for c in co], n=n, seq=seq, w=w, reach=1 / w, total_degree=pdeg(S),
               nterms=len(S), secs=round(time.time() - t, 2))
    out.append(rec); print(json.dumps(rec), flush=True)
    return S

# ---- generic curve, even coordinates (Moebius functions of x)
a, b = 5, 11
E = Curve(a, b, p)
analyse('weierstrass_x', E, lambda x, y: x, 'pole 2(O); Montgomery x is affine in this')
analyse('affine_x', E, lambda x, y: (3 * x + 17) % p, 'pole 2(O), Montgomery/affine change')
c = 12345
analyse('moebius_generic', E, lambda x, y: None if x == c else (x - 1) * inv(x - c) % p,
        'even, poles (Q)+(-Q), Q generic: y_Edwards-like shape with generic pole')
analyse('inverse_generic', E, lambda x, y: None if x == c else inv(x - c), 'even, poles (Q)+(-Q), Q generic')
# ---- 2-torsion pole: y^2 = x(x^2 + c2 x + d2), T = (0,0)
E2 = Curve(13, 0, p, a2=7)
analyse('inverse_2torsion', E2, lambda x, y: None if x == 0 else inv(x), 'even, double pole at 2-torsion T')
# ---- 4-torsion pole (twisted Edwards y): Montgomery y^2 = x^3 + A x^2 + x with A+2 a square, Q=(1,.) order 4,
#      y_Ed = (x-1)/(x+1) has poles at x=-1 (points Q' with 2Q' = (0,0))
A = 7
while sqrt_mod(A + 2, p) is None: A += 1
EM = Curve(1, 0, p, a2=A)
Q = EM.lift_x(1); assert EM.mul(4, Q) is None and EM.mul(2, Q) is not None
analyse('edwards_y', EM, lambda x, y: None if x == p - 1 else (x - 1) * inv(x + 1) % p, 'twisted Edwards y: even, poles at the 4-torsion pair with x=-1')
analyse('montgomery_x', EM, lambda x, y: x, 'Montgomery x on the same curve')
analyse('edwards_x_odd', EM, lambda x, y: None if y == 0 else x * inv(y) % p, 'Edwards x = u/v on Montgomery: odd, degree 2, poles at two 2-torsion points (sum = third 2-torsion)')
# ---- 3-torsion: y^2 = x^3 + (lam x + s)^2, T=(0,s) is a flex
lam, s = 3, 5
E3 = Curve(2 * lam * s, s * s, p, a2=lam * lam)
T = (0, s); assert E3.on(T) and E3.mul(3, T) is None
analyse('inverse_3torsion', E3, lambda x, y: None if x == 0 else inv(x), 'even, poles (T)+(-T), T 3-torsion')
analyse('double_pole_3torsion', E3, lambda x, y: None if (y - lam * x - s) % p == 0 else x * inv(y - lam * x - s) % p,
        'non-even degree 2, double pole at 3-torsion T (summation poly degree 2 per variable)')
analyse('pole_O_minus_T', E3, lambda x, y: None if x == 0 else (y - s) * inv(x) % p, 'non-even degree 2, poles (O)+(-T), T 3-torsion')
analyse('deg3_O_T_minusT', E3, lambda x, y: None if x == 0 else (y + 7) * inv(x) % p, 'degree 3, poles O+T+(-T) (Hessian-type coordinate class)', dmaxmax=9)
# ---- non-even degree 2 with generic double pole: phi = (x - x_{2Q}) / tangent_Q
Qg = E.random_point(rng); Q2 = E.mul(2, Qg)
lamQ = (3 * Qg[0] * Qg[0] + a) * inv(2 * Qg[1]) % p; muQ = (Qg[1] - lamQ * Qg[0]) % p
analyse('double_pole_generic', E, lambda x, y: None if (y - lamQ * x - muQ) % p == 0 else (x - Q2[0]) * inv(y - lamQ * x - muQ) % p,
        'non-even degree 2, double pole at generic Q (summation poly degree 4 per variable)', dmaxmax=5)
# ---- degree 3 generic: y/(x-c)
analyse('deg3_generic', E, lambda x, y: None if x == c else y * inv(x - c) % p, 'degree 3, poles O + (Q) + (-Q) generic', dmaxmax=9)
json.dump(out, open('/home/user/semaev-runs/SA-19/results/coords.json', 'w'), indent=1)
