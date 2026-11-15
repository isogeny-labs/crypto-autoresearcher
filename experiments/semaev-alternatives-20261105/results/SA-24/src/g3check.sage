# SA-24 step (a): parameters, Jacobian order factorisations, exact pullback homomorphism, genus-3 construction.
import sys, json
set_random_seed(2424)
out = open('work/params_g3check.txt','w'); fl = open('results/facts_g3check.jsonl','w')
def logj(d): fl.write(json.dumps(d, default=lambda o: int(o) if hasattr(o,"__int__") else str(o))+"\n"); fl.flush()

def prime_for(k):
    p = 2^k - 1
    while True:
        p = previous_prime(p)
        if p % 4 == 3: return int(p)

def make_g2(p):
    F = GF(p); R.<X> = F[]
    while True:
        r = F.random_element(); ha = F.random_element(); hb = F.random_element()
        h = X^2 + ha*X + hb; g = (X - r^2)*h
        if r != 0 and g.is_squarefree() and h(r^2) != 0 and g(0) != 0: return F,R,r,ha,hb,h,g

def E12(F,R,g):
    a = g.list()
    E1 = EllipticCurve(F, [0, a[2], 0, a[1], a[0]])
    rr = list(reversed(a)); c = rr[3]
    E2 = EllipticCurve(F, [0, rr[1], 0, rr[2]*c, rr[3]*c^2]) if False else None
    # reversed cubic c0 X^3 + c1 X^2 + c2 X + 1 with (c0..)=g coefficients reversed: leading=g(0)
    rev = R(list(reversed(a))); cl = rev.leading_coefficient(); rl = rev.list()
    E2 = EllipticCurve(F, [0, rl[2], 0, rl[1]*cl, rl[0]*cl^2])
    return E1, E2

def prime_for(k):
    p = 2^k - 1
    while True:
        p = previous_prime(p)
        if p % 4 == 3: return int(p)
def make_g2(p):
    F = GF(p); R.<X> = F[]
    while True:
        r = F.random_element(); ha = F.random_element(); hb = F.random_element()
        h = X^2 + ha*X + hb; g = (X - r^2)*h
        if r != 0 and g.is_squarefree() and h(r^2) != 0 and g(0) != 0: return F,R,r,ha,hb,h,g
def E12(F,R,g):
    a = g.list()
    E1 = EllipticCurve(F, [0, a[2], 0, a[1], a[0]])
    rr = list(reversed(a)); c = rr[3]
    E2 = EllipticCurve(F, [0, rr[1], 0, rr[2]*c, rr[3]*c^2]) if False else None
    # reversed cubic c0 X^3 + c1 X^2 + c2 X + 1 with (c0..)=g coefficients reversed: leading=g(0)
    rev = R(list(reversed(a))); cl = rev.leading_coefficient(); rl = rev.list()
    E2 = EllipticCurve(F, [0, rl[2], 0, rl[1]*cl, rl[0]*cl^2])
    return E1, E2

def make_g3(p):
    F = GF(p); R.<X> = F[]
    while True:
        r = F.random_element(); h3 = X^3 + F.random_element()*X^2 + F.random_element()*X + F.random_element()
        g4 = (X-r^2)*h3
        if r!=0 and g4.is_squarefree() and h3(r^2)!=0 and g4(0)!=0 and (X*g4).is_squarefree(): return F,R,r,h3,g4
import numpy as np
def count_aff_quartic(p, g4):
    co = [int(c) for c in g4.list()]
    x = np.arange(p, dtype=np.int64); v = np.zeros(p, dtype=np.int64)
    for c in reversed(co): v = (v*x + c) % p
    qr = np.zeros(p, dtype=np.int8); sq = (x*x) % p; qr[sq] = 1
    isq = qr[v]; nz = (v != 0)
    return int(np.sum(np.where(v==0, 1, 2*isq)))
def odd_model3(F,r,g4):
    S.<x> = F[]; f8 = g4(x^2); T.<z> = F[]
    Fz = T(sum(f8.list()[i]*(r*z+1)^i * z^(8-i) for i in range(9)))
    return T,Fz
def power_sum2(P):  # sum alpha^2 for monic char poly P
    c = P.list(); n = P.degree(); a1 = c[n-1]; a2 = c[n-2]; return a1^2 - 2*a2
# direct check of #Jac(C3) = #E1 * #Jac(H) on the odd degree-7 model at small p
for p in [211, 307, 1009]:
    for idx in range(2):
        F,R,r,h3,g4 = make_g3(p)
        T,Fz = odd_model3(F,r,g4); assert Fz.degree()==7, Fz.degree()
        C7 = HyperellipticCurve(Fz); P7 = C7.frobenius_polynomial()
        nE1 = count_aff_quartic(p,g4)+2; H = HyperellipticCurve(R(g4*R.gen())); PH=H.frobenius_polynomial()
        tE=p+1-nE1; PE = PolynomialRing(ZZ,'T')([p,-tE,1])
        Z.<TT> = ZZ[]; ok = (Z(P7.list())==Z(PE.list())*Z(PH.list()))
        d = dict(kind="genus3_check", p=p, idx=idx, deg_odd=7, nJac_direct=int(P7(1)), nJac_E1_HJ=int(nE1*PH(1)), frob_poly_factorises=bool(ok), r=int(r), h3=[int(c) for c in h3.list()], nE1=int(nE1), nHJ=int(PH(1)), c2proj=int(p^2+1-(power_sum2(PE)+power_sum2(PH))), c2proj_direct=int(p^2+1-power_sum2(P7)))
        logj(d); print(d, flush=True)
        out.write("A3T %d %d %d %d %d %d %d %d %d %d\n" % (p,idx,int(r),int(h3[0]),int(h3[1]),int(h3[2]),int(nE1),int(PH(1)),int(nE1*PH(1)),d["c2proj"]))
        out.flush()
# A2/A1 tiny validation curves (genus 2) for exhaustive enumeration
for p in [1019, 4091]:
    F,R,r,ha,hb,h,g = make_g2(p); E1,E2 = E12(F,R,g)
    out.write("A2T %d %d %d %d %d %d\n" % (p,int(r),int(ha),int(hb),int(E1.order()),int(E2.order())))
    logj(dict(kind="A2tiny", p=p, r=int(r), ha=int(ha), hb=int(hb), nE1=int(E1.order()), nE2=int(E2.order())))
out.close(); fl.close()
print("done")
