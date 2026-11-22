"""G30-004 instrument validation on the real object: Semaev S3 + membership polys.

Builds the m=3 decomposition system over GF(p):
    S3(x1,x2,x3,xQ) = 0,  h(x1) = 0, h(x2) = 0, h(x3) = 0
where h is the membership polynomial of the factor base (roots = base x-values).
Then:
  * computes the Groebner basis (grevlex) and its max degree (solving-degree proxy)
  * checks dim == 0 and compares the solution count against brute-force
    enumeration of base triples summing to the target.
If the counts agree, the instrument is validated on the object it will be used on.
"""
from sage.all import *
import json, itertools, sys

def curve_points(p, a, b):
    pts = []
    for x in range(p):
        rhs = (x*x*x + a*x + b) % p
        if rhs == 0:
            pts.append((x, 0))
        elif pow(rhs, (p-1)//2, p) == 1:
            y = pow(rhs, (p+1)//4, p) if p % 4 == 3 else None
            if y is None:
                # Tonelli-Shanks via Sage
                y = GF(p)(rhs).sqrt()
                y = int(y)
            pts.append((x, y)); pts.append((x, (-y) % p))
    pts.append(None)
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

def s3_odd(a, b):
    # S3(x1,x2,x3) for y^2 = x^3 + a x + b, odd characteristic
    R = PolynomialRing(QQ, 4, 'x1,x2,x3,X')
    x1, x2, x3, X = R.gens()
    f = lambda z: z**3 + a*z + b
    S2 = lambda u, v, w: (u - v)*w**2 - 2*((u + v)*(u*v + a) + 2*b)*w + (u*v - a)**2 - 4*b*(u + v)
    # S3(x1,x2,x3) = Res_D( S2(x1,x2,D), S2(x3,D,0) ) -- use the standard closed form instead:
    S3 = ((x1 - x2)**2 * x3**2
          - 2*((x1 + x2)*(x1*x2 + a) + 2*b)*x3
          + (x1*x2 - a)**2 - 4*b*(x1 + x2))
    return S3

def run(p, a, b, k, seed=1):
    set_random_seed(seed)
    pts = curve_points(p, a, b)
    aff = [P for P in pts if P is not None]
    xs_all = sorted(set(P[0] for P in aff))

    # window base: k smallest x-values, both signs  (negation-closed)
    Wx = xs_all[:k]
    base = [P for P in aff if P[0] in Wx]
    # target: a point that IS decomposable (so the system is nonempty) and one that is not
    basePts = base
    S = {}
    for P in basePts:
        for Q in basePts:
            S.add(P) if False else None
    pair = {}
    for P in basePts:
        for Q in basePts:
            pair.setdefault(add(P, Q, p, a), []).append((P, Q))

    def decompose(r):
        out = []
        for R, pqs in pair.items():
            # Q = R + T  => need T in base with R + T = r
            pass
        cnt = 0
        for P in basePts:
            for Q in basePts:
                for T in basePts:
                    if add(add(P, Q, p, a), T, p, a) == r:
                        cnt += 1
        return cnt

    # pick a decomposable target
    target = None
    for P in basePts:
        for Q in basePts:
            for T in basePts:
                target = add(add(P, Q, p, a), T, p, a)
                if target is not None: break
            if target is not None: break
        if target is not None: break
    brute = decompose(target)

    # build the system
    Fp = GF(p)
    R = PolynomialRing(Fp, 3, 'x1,x2,x3', order='degrevlex')
    x1, x2, x3 = R.gens()
    S3QQ = s3_odd(a % p, b % p)
    # substitute into GF(p)
    S3p = R(S3QQ(x1, x2, x3, 0)) if False else None
    # direct construction over Fp (same formula)
    S3p = ((x1 - x2)**2 * x3**2
           - 2*((x1 + x2)*(x1*x2 + a) + 2*b)*x3
           + (x1*x2 - a)**2 - 4*b*(x1 + x2))
    xQ = int(target[0])
    eq = S3p(x1, x2, x3) + 0
    # S3(x1,x2,x3) vanishes iff x1,x2,x3, xQ satisfy S4? No: S3 with one variable replaced by xQ.
    # Correct: S4(x1,x2,x3,xQ)=0 for a 3-sum. Use the resultant recursion S4 = Res_D(S3(x1,x2,D), S2(x3,xQ,D)).
    D = R.gen(2)
    # compute S4 via resultant in a bigger ring
    Rbig = PolynomialRing(Fp, 5, 'x1,x2,x3,xQ,D', order='degrevlex')
    y1, y2, y3, yQ, DD = Rbig.gens()
    S2b = lambda u, v, w: (u - v)*w**2 - 2*((u + v)*(u*v + a) + 2*b)*w + (u*v - a)**2 - 4*b*(u + v)
    S3b = lambda u, v, w: ((u - v)**2 * w**2 - 2*((u + v)*(u*v + a) + 2*b)*w
                           + (u*v - a)**2 - 4*b*(u + v))
    res = S3b(y1, y2, DD).resultant(S3b(y3, yQ, DD), DD)
    h = prod([x1 - w for w in Wx]) if False else None
    hpoly = prod([y - w for w in Wx]) if False else None
    hbig = prod([y1 - w for w in Wx])
    polys = [res(y1, y2, y3, xQ, 0),
             hbig(y1, y2, y3, xQ, 0),
             hbig(y2, y1, y3, xQ, 0),
             hbig(y3, y1, y2, xQ, 0)]
    polys = [Rbig(str(q).replace('xQ', str(xQ))) if False else q for q in polys]
    # project to 3 variables by substituting xQ
    S = PolynomialRing(Fp, 3, 'a1,a2,a3', order='degrevlex')
    sub = {y1: S.gen(0), y2: S.gen(1), y3: S.gen(2), yQ: Fp(xQ)}
    sysp = [S(q.subs(sub)) for q in polys]
    sysp = [q for q in sysp if q != 0]

    t0 = walltime()
    I = S.ideal(sysp)
    G = I.groebner_basis()
    dt = walltime(t0)
    degs = [g.degree() for g in G if g != 0]
    dim = I.dimension()
    # count solutions if 0-dimensional
    nsol = None
    if dim == 0:
        try:
            nsol = int(I.vector_space_dimension())
        except Exception as e:
            nsol = f"err:{e}"
    return dict(p=p, a=a, b=b, k=k, target=str(target), brute=brute,
                maxdeg=int(max(degs)) if degs else 0, gbsize=int(len(G)),
                dim=int(dim), nsol=nsol, secs=round(float(dt), 3),
                sys_degs=[int(q.degree()) for q in sysp])

if __name__ == "__main__":
    out = []
    for k in (4, 5, 6):
        r = run(4099, 1, 1, k)
        out.append(r); print(json.dumps(r, default=str), flush=True)
    json.dump(out, open('/Volumes/SSD990/llm/tmp/opencode/g30-004/validate.json','w'), indent=1, default=str)
