"""SA-19 step 5: symbolic degree sequence of S^phi for the whole family of even degree-2 coordinates
phi = 1/(x - c) on y^2 = x^3 + a x + b (every Moebius function of x is an affine function of such a phi, and affine
changes preserve the degree filtration).  S^phi(u1,u2,u3) = (u1 u2 u3)^2 S_3(c+1/u1, c+1/u2, c+1/u3).
W = span of the u3-coefficients; the degree sequence is [2,3,4] unless rank{c22,c21,c12} = 1 ([2,2,4]) and would
be [<=1, ., 4] only if rank of {c22,c21,c12,c20,c02,c11} <= 2.  We compute these rank conditions as polynomial
ideals in (a,b,c) and compare with the division polynomials."""
import sympy as sp, json, time
a, b, c, u1, u2, u3, X = sp.symbols('a b c u1 u2 u3 X')
def S3(x1, x2, x3): return (x1 - x2)**2 * x3**2 - 2*((x1 + x2)*(x1*x2 + a) + 2*b)*x3 + (x1*x2 - a)**2 - 4*b*(x1 + x2)
t0 = time.time()
Sphi = sp.expand((u1*u2*u3)**2 * S3(c + 1/u1, c + 1/u2, c + 1/u3))
P = sp.Poly(Sphi, u1, u2, u3)
assert all(e <= 2 for m in P.monoms() for e in m)
def cvec(i, j):   # coefficient vector in u3 of the u1^i u2^j coefficient: [u3^0, u3^1, u3^2]
    return [P.coeff_monomial(u1**i * u2**j * u3**l) for l in range(3)]
M3 = sp.Matrix([cvec(2, 2), cvec(2, 1), cvec(1, 2)])
M6 = sp.Matrix([cvec(2, 2), cvec(2, 1), cvec(1, 2), cvec(2, 0), cvec(0, 2), cvec(1, 1)])
print('c22 =', [sp.factor(e) for e in cvec(2, 2)])
print('c21 =', [sp.factor(e) for e in cvec(2, 1)])
print('c11 =', [sp.factor(e) for e in cvec(1, 1)])
print('c20 =', [sp.factor(e) for e in cvec(2, 0)])
print('c10 =', [sp.factor(e) for e in cvec(1, 0)])
print('c00 =', [sp.factor(e) for e in cvec(0, 0)])
# rank{c22,c21,c12} <= 1 : all 2x2 minors vanish
minors2 = [sp.factor(M3.extract([r1, r2], [k1, k2]).det()) for (r1, r2) in [(0, 1), (0, 2), (1, 2)] for (k1, k2) in [(0, 1), (0, 2), (1, 2)]]
minors2 = [m for m in minors2 if m != 0]
g2 = sp.gcd_list([sp.expand(m) for m in minors2])
print('\nrank{c22,c21,c12} <= 1 condition: gcd of 2x2 minors =', sp.factor(g2))
G2 = sp.groebner([sp.expand(m) for m in minors2], a, b, c, order='lex')
print('Groebner basis (lex a>b>c) of the 2x2 minors:', [sp.factor(g) for g in G2.exprs])
# division polynomial psi_4 / psi_2 (x-coordinates of points of exact order 4): psi_4 = 4y(x^6+5a x^4+20b x^3-5a^2x^2-4abx-8b^2-a^3)
psi4 = sp.expand(c**6 + 5*a*c**4 + 20*b*c**3 - 5*a**2*c**2 - 4*a*b*c - 8*b**2 - a**3)
print('psi_4/(4y) at x=c:', psi4)
print('generator divides psi_4/(4y)?', sp.simplify(sp.rem(psi4, sp.expand(g2), c)) == 0 if g2 != 1 else 'n/a',
      ' | ratio:', sp.factor(sp.cancel(psi4 / g2)) if g2 != 1 else 'n/a')
# rank of all six <= 2: all 3x3 minors vanish
import itertools
minors3 = []
for rows in itertools.combinations(range(6), 3):
    d = sp.expand(M6.extract(list(rows), [0, 1, 2]).det())
    if d != 0: minors3.append(d)
g3 = sp.gcd_list(minors3)
print('\nrank of six vectors <= 2: number of nonzero 3x3 minors', len(minors3), ' gcd =', sp.factor(g3))
disc = sp.expand(4*a**3 + 27*b**2)
t = sp.symbols('t')
G3 = sp.groebner(minors3 + [1 - t*disc], t, a, b, c, order='grevlex')
print('Groebner basis of (3x3 minors, 1 - t*disc):', G3.exprs if len(G3.exprs) < 6 else len(G3.exprs))
# also: the degree sequence at a 4-torsion x-coordinate, generic check
print('time', round(time.time() - t0, 1))
json.dump(dict(gcd_minors2=str(sp.factor(g2)), groebner_minors2=[str(sp.factor(g)) for g in G2.exprs], psi4=str(psi4),
               gcd_minors3=str(sp.factor(g3)), groebner_minors3_with_disc=[str(g) for g in G3.exprs]),
          open('/home/user/semaev-runs/SA-19/results/moebius_proof.json', 'w'), indent=1)
