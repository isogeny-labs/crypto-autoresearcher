"""G30-004 / G32-001 WP2 first cell: regularity of window vs pullback membership systems.

Systems (m=3), over GF(p), target xQ fixed:
    S4(x1,x2,x3,xQ) = 0
    h_B(x_i) = 0, i = 1..3          (h_B = membership polynomial of the base x-set)

Two bases of the SAME number k of x-values:
  window   : Wx = k smallest x-values                       (generic membership poly)
  pullback : x^2 in T, |T| = k/2, so h(x) = prod (x^2 - t)   (even membership poly)

Reported per family: quotient dimension (number of solutions, with multiplicity),
Castelnuovo-Mumford regularity of the homogenized ideal, and the flat max degree
of the non-homogenized reduced basis (shown only to document that it is a bad proxy).
"""
from sage.all import *
import json

def curve_affine(p, a, b):
    pts = []
    F = GF(p)
    for x in range(p):
        rhs = (x*x*x + a*x + b) % p
        if rhs == 0:
            pts.append((x, 0))
        else:
            s = F(rhs).sqrt() if F(rhs).is_square() else None
            if s is not None:
                y = int(s); pts.append((x, y)); pts.append((x, (-y) % p))
    return pts

def add(P, Q, p, a):
    if P is None: return Q
    if Q is None: return P
    if P[0] == Q[0]:
        if (P[1] + Q[1]) % p == 0: return None
        lam = (3*P[0]*P[0] + a) * pow(2*P[1], -1, p) % p
    else:
        lam = (Q[1] - P[1]) * pow(Q[0] - P[0], -1, p) % p
    x3 = (lam*lam - P[0] - Q[0]) % p
    return (x3, (lam*(P[0]-x3) - P[1]) % p)

def build(p, a, b, Wx, xQ):
    F = GF(p)
    R = PolynomialRing(F, 4, 'x1,x2,x3,D', order='degrevlex')
    x1, x2, x3, D = R.gens()
    S3 = lambda u, v, w: ((u - v)**2 * w**2 - 2*((u + v)*(u*v + a) + 2*b)*w
                          + (u*v - a)**2 - 4*b*(u + v))
    res = S3(x1, x2, D).resultant(S3(x3, F(xQ), D), D)
    h = prod([x1 - w for w in Wx])
    # membership polys in each variable
    h1 = h
    h2 = prod([x2 - w for w in Wx])
    h3 = prod([x3 - w for w in Wx])
    S = PolynomialRing(F, 3, 'a1,a2,a3', order='degrevlex')
    y1, y2, y3 = S.gens()
    sub = {x1: y1, x2: y2, x3: y3}
    sysp = [S(res.subs(sub)), S(h1.subs(sub)), S(h2.subs(sub)), S(h3.subs(sub))]
    return S, [q for q in sysp if q != 0]

def measure(S, sysp):
    I = S.ideal(sysp)
    dim = int(I.dimension())
    G = I.groebner_basis()
    maxdeg = int(max([g.degree() for g in G if g != 0])) if G else 0
    reg = None
    try:
        Rh = PolynomialRing(S.base_ring(), 4, 'y1,y2,y3,h', order='degrevlex')
        hom = []
        for q in sysp:
            qq = Rh(str(q).replace('a1','y1').replace('a2','y2').replace('a3','y3'))
            hom.append(qq.homogenize(Rh.gen(3)))
        reg = int(Rh.ideal(hom).regularity())
    except Exception as e:
        reg = f"err:{type(e).__name__}:{e}"
    nsol = None
    if dim == 0:
        try: nsol = int(I.vector_space_dimension())
        except Exception as e: nsol = f"err:{e}"
    return dict(dim=dim, nsol=nsol, maxdeg=maxdeg, reg=reg)

def run(p, a, b, k):
    aff = curve_affine(p, a, b)
    xs_all = sorted(set(P[0] for P in aff))
    Wx = xs_all[:k]
    # pullback: T of size k//2, x-set = {x : x^2 in T}
    kk = max(2, 2 * (k // 2))
    T = [xs_all[0]**2 % p]
    for x in xs_all[1:]:
        if x**2 % p not in T: T.append(x**2 % p)
        if len(T) == kk // 2: break
    Px = [x for x in range(p) if x**2 % p in T]
    Px = Px[:kk]

    baseW = [P for P in aff if P[0] in Wx]
    baseP = [P for P in aff if P[0] in set(Px)]
    # a decomposable target for each family
    def dec(base):
        for P in base:
            for Q in base:
                for R in base:
                    t = add(add(P, Q, p, a), R, p, a)
                    if t is not None: return t
        return None
    out = dict(p=p, k=k, Wx=Wx, Px=Px)
    for name, base in (("window", baseW), ("pullback", baseP)):
        t = dec(base)
        if t is None:
            out[name] = dict(error="no decomposable target")
            continue
        S, sysp = build(p, a, b, Wx if name == "window" else Px, t[0])
        out[name] = measure(S, sysp)
        out[name]["sys_degs"] = [int(q.degree()) for q in sysp]
    return out

if __name__ == "__main__":
    res = []
    for k in (4, 6, 8):
        r = run(4099, 1, 1, k)
        res.append(r); print(json.dumps(r, default=str), flush=True)
    json.dump(res, open('/Volumes/SSD990/llm/tmp/opencode/g30-004/regcell.json','w'), indent=1, default=str)
