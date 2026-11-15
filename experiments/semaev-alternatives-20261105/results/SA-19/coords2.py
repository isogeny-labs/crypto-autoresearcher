"""SA-19 family (a), symmetric coordinates: eigenfunctions of torsion translations.
phi with phi(P+T) = zeta phi(P) (T torsion of order k, zeta a k-th root of unity) make S^phi sparse.
 - Z/2: twisted Edwards y (poles at a 4-torsion pair), done in coords.py (w = 8).
 - Z/3: Hessian-type coordinate, phi in L(O+T+2T) with eigenvalue omega.
 - Z/2 x Z/2: Jacobi-intersection-type coordinates, phi in L(O+T1+T2+T3) with a character of E[2].
Summation polynomials by interpolation restricted to the symmetry-allowed monomial classes.  Writes results/coords2.json."""
import sys, json, random, time, itertools
sys.path.insert(0, '/home/user/semaev-runs/SA-19')
from lib19 import *

p = PR; rng = random.Random(23); out = []
def inv(v): return pow(v, -1, p)

def translation_matrix(E, T, basis):
    """M with f_i(P+T) = sum_j M[i][j] f_j(P)."""
    k = len(basis)
    while True:
        pts = []
        while len(pts) < k + 3:
            P = E.random_point(rng)
            vals = [f(*P) for f in basis]; PT = E.add(P, T)
            if PT is None or any(v is None for v in vals): continue
            vt = [f(*PT) for f in basis]
            if any(v is None for v in vt): continue
            pts.append((vals, vt))
        A = [v for v, _ in pts]
        if rank_mod(A, p) < k: continue
        M = []
        for i in range(k):
            # solve A m = b, b = f_i(P+T) over points
            rows = [A[s] + [pts[s][1][i]] for s in range(len(pts))]
            R, piv = rref_mod(rows, p)
            assert piv[:k] == list(range(k)) and len(R) == k, 'inconsistent: basis not closed under translation'
            M.append([R[j][k] for j in range(k)])
        return M

def eigenvector(Ms, zetas, k):
    """common eigenvector: v with sum_i v_i (M^T)... we want phi = sum_i v_i f_i with phi(P+T) = zeta phi(P):
    sum_i v_i f_i(P+T) = sum_i v_i sum_j M_ij f_j(P) = zeta sum_j v_j f_j  ->  (M^T - zeta I) v = 0."""
    rows = []
    for M, z in zip(Ms, zetas):
        for j in range(k):
            rows.append([(M[i][j] - (z if i == j else 0)) % p for i in range(k)])
    ns = nullspace_mod(rows, p)
    return ns

def sym_summation_poly(E, phi, dmax, classes_fn, nsamp_extra=30):
    """interpolate S^phi restricted to each symmetry class of monomials; returns list of (class, polys)."""
    mons_all = [m for m in itertools.product(range(dmax + 1), repeat=3)]
    groups = {}
    for m in mons_all: groups.setdefault(classes_fn(m), []).append(m)
    nmax = max(len(g) for g in groups.values())
    samples = []
    while len(samples) < nmax + nsamp_extra:
        P1, P2 = E.random_point(rng), E.random_point(rng)
        P3 = E.neg(E.add(P1, P2))
        if P3 is None or P1[0] == P2[0]: continue
        u = [phi(*P) for P in (P1, P2, P3)]
        if any(v is None for v in u): continue
        samples.append(u)
    pw = [[[pow(u[i], e, p) for e in range(dmax + 1)] for i in range(3)] for u in samples]
    res = []
    for cls, mons in groups.items():
        M = np.zeros((len(samples), len(mons)), dtype=np.int64)
        for j, m in enumerate(mons):
            M[:, j] = [pw[s][0][m[0]] * pw[s][1][m[1]] % p * pw[s][2][m[2]] % p for s in range(len(samples))]
        ns = np_nullspace_mod(M, p)
        if ns:
            res.append((cls, [{mons[j]: int(v[j]) for j in range(len(mons)) if v[j]} for v in ns]))
    return res

def analyse(label, E, phi, classes_fn, dmaxmax, note=''):
    t = time.time()
    for d in range(1, dmaxmax + 1):
        res = sym_summation_poly(E, phi, d, classes_fn)
        if res: break
    if not res:
        out.append(dict(label=label, degree=None, note=note)); print(label, 'nothing up to', dmaxmax); return None
    cls, polys = res[0]
    S = polys[0]; co = coeffs_in_last(S, 3); co = [c for c in co]
    n, seq, w = budget(co, p)
    rec = dict(label=label, note=note, degree_per_var=d, nclasses_with_relation=len(res), nullity=len(polys), n_coeffs=len(co),
               coef_degrees=[pdeg(c) for c in co], n=n, seq=seq, w=w, reach=1 / w, total_degree=pdeg(S), nterms=len(S),
               monomials=sorted(S.keys()), secs=round(time.time() - t, 1))
    out.append(rec); print(json.dumps({k: v for k, v in rec.items() if k != 'monomials'}), flush=True)
    return S

# ---------------- Z/3 (Hessian class): y^2 = x^3 + (lam x + s)^2, T = (0, s) flex, L(O+T+2T) = <1, 1/x, y/x>
lam, s = 3, 5
E3 = Curve(2 * lam * s, s * s, p, a2=lam * lam); T = (0, s); assert E3.mul(3, T) is None
basis3 = [lambda x, y: 1, lambda x, y: None if x == 0 else inv(x), lambda x, y: None if x == 0 else y * inv(x) % p]
M3 = translation_matrix(E3, T, basis3)
om = pow(3, (p - 1) // 3, p)
while om == 1: om = pow(rng.randrange(2, p), (p - 1) // 3, p)
assert (om * om + om + 1) % p == 0
for z, zl in ((om, 'omega'), (om * om % p, 'omega^2'), (1, '1')):
    vs = eigenvector([M3], [z], 3)
    print('Z/3 eigenvalue', zl, 'eigenspace dim', len(vs))
    if zl == 'omega' and vs:
        v = vs[0]
        def phiH(x, y, v=v):
            vals = [f(x, y) for f in basis3]
            return None if any(t is None for t in vals) else sum(a * b for a, b in zip(v, vals)) % p
        # check eigen property
        P = E3.random_point(rng); assert phiH(*E3.add(P, T)) == om * phiH(*P) % p
        def cls3(m): return ((m[0] - m[1]) % 3, (m[0] - m[2]) % 3)
        SH = analyse('hessian_eigen_omega', E3, phiH, cls3, 9, 'degree 3, poles O+T+2T, phi(P+T) = omega phi(P)')
        json.dump(out, open('/home/user/semaev-runs/SA-19/results/coords2.json', 'w'), indent=1)

# ---------------- Z/2 x Z/2 (Jacobi intersection class): y^2 = x(x-1)(x-e), E[2] rational
e = 17
EJ = Curve(0, 0, p, a2=0); EJ = Curve((e) % p, 0, p, a2=(-(1 + e)) % p)   # x^3 - (1+e)x^2 + e x
T1, T2, T3 = (0, 0), (1, 0), (e, 0)
for T in (T1, T2, T3): assert EJ.on(T) and EJ.mul(2, T) is None
basisJ = [lambda x, y: 1, lambda x, y: None if y == 0 else inv(y), lambda x, y: None if y == 0 else x * inv(y) % p,
          lambda x, y: None if (x * (x - 1)) % p == 0 else y * inv(x * (x - 1)) % p]
MJ1 = translation_matrix(EJ, T1, basisJ); MJ2 = translation_matrix(EJ, T2, basisJ)
for chi in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
    vs = eigenvector([MJ1, MJ2], [chi[0] % p, chi[1] % p], 4)
    print('E[2] character', chi, 'eigenspace dim', len(vs))
    if chi != (1, 1) and vs:
        v = vs[0]
        def phiJ(x, y, v=v):
            vals = [f(x, y) for f in basisJ]
            return None if any(t is None for t in vals) else sum(a * b for a, b in zip(v, vals)) % p
        P = EJ.random_point(rng)
        assert phiJ(*EJ.add(P, T1)) == chi[0] * phiJ(*P) % p and phiJ(*EJ.add(P, T2)) == chi[1] * phiJ(*P) % p
        def cls2(m): return ((m[0] + m[1]) % 2, (m[0] + m[2]) % 2)
        analyse('jacobi_eigen_%d_%d' % chi, EJ, phiJ, cls2, 10, 'degree 4, poles O+T1+T2+T3, character %s of E[2]' % (chi,))
        json.dump(out, open('/home/user/semaev-runs/SA-19/results/coords2.json', 'w'), indent=1)
json.dump(out, open('/home/user/semaev-runs/SA-19/results/coords2.json', 'w'), indent=1)
