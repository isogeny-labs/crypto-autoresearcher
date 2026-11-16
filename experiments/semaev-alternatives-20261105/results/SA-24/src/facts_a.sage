# SA-24 step (a): parameters, Jacobian order factorisations, exact pullback homomorphism, genus-3 construction.
import sys, json
set_random_seed(24)
out = open('work/params.txt','w'); fl = open('results/facts.jsonl','w')
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

# ---------- (a1) A1 curves with prime-order target ----------
for k in [10,12,14,16,18,20,22,24]:
    p = prime_for(k)
    for idx in range(3):
        while True:
            F,R,r,ha,hb,h,g = make_g2(p)
            E1,E2 = E12(F,R,g)
            n1E = E1.order(); n2E = E2.order()
            fac = factor(n1E); n1 = int(fac[-1][0]); cof = int(n1E // n1)
            if fac[-1][1] == 1 and cof <= 16 and n2E % n1 != 0 and n1 > 100: break
        NJ = n1E*n2E
        logj(dict(kind="A1curve", k=k, p=p, idx=idx, r=int(r), ha=int(ha), hb=int(hb), nE1=int(n1E), nE2=int(n2E),
                  fac_nE1=str(factor(n1E)), fac_nE2=str(factor(n2E)), n1=n1, cof=cof, nJac=int(NJ), fac_nJac=str(factor(NJ)),
                  n1_divides_nE2=bool(n2E % n1 == 0), n1_sq_divides_nJac=bool(NJ % (n1^2) == 0)))
        out.write("A1 %d %d %d %d %d %d %d %d %d %d\n" % (k,idx,p,int(r),int(ha),int(hb),int(n1E),int(n2E),n1,cof))
        out.flush()
# ---------- (a1b) A2 curves (unconditioned) ----------
for k in [12,16,20,24]:
    p = prime_for(k)
    for idx in range(3):
        F,R,r,ha,hb,h,g = make_g2(p)
        E1,E2 = E12(F,R,g)
        n1E = E1.order(); n2E = E2.order()
        logj(dict(kind="A2curve", k=k, p=p, idx=idx, r=int(r), ha=int(ha), hb=int(hb), nE1=int(n1E), nE2=int(n2E), nJac=int(n1E*n2E), fac_nJac=str(factor(n1E*n2E))))
        out.write("A2 %d %d %d %d %d %d %d %d\n" % (k,idx,p,int(r),int(ha),int(hb),int(n1E),int(n2E)))
        out.flush()

# ---------- (a2) exact pullback homomorphism (no sign slack) ----------
def odd_model2(F,r,g):
    S.<x> = F[]; f6 = g(x^2); T.<z> = F[]
    Fz = T(sum(f6.list()[i]*(r*z+1)^i * z^(6-i) for i in range(7)))
    assert Fz.degree()==5
    return T,Fz
def pb_check(p, ntrial=200, cur=None):
    if cur is None: F,R,r,ha,hb,h,g = make_g2(p)
    else: F,R,r,ha,hb,h,g = cur
    E1,E2 = E12(F,R,g); T,Fz = odd_model2(F,r,g); z = T.gen()
    C5 = HyperellipticCurve(Fz); JF = C5.jacobian()(F)
    NJ = C5.frobenius_polynomial()(1) if p < 2^17 else None
    def pull(P):
        X0,Y0 = P.xy()
        u = T((r^2-X0)*z^2+2*r*z+1); u = u/u.leading_coefficient()
        v = T(Y0*z^3) % u
        return JF([u,v])
    exact=0; neg=0; n=0; skipped=0
    for _ in range(ntrial):
        P = E1.random_point(); Q = E1.random_point()
        if P==0 or Q==0 or P+Q==0 or P==Q or P.xy()[0]==r^2 or Q.xy()[0]==r^2 or (P+Q).xy()[0]==r^2: skipped+=1; continue
        lhs = pull(P+Q); rhs = pull(P)+pull(Q); n+=1
        exact += (lhs==rhs); neg += (lhs==-rhs and lhs!=rhs)
    return dict(p=p, n=n, exact_equal=exact, only_up_to_sign=neg, skipped=skipped, nJac_frob=(int(NJ) if NJ else None), nJac_E1E2=int(E1.order()*E2.order()))
for p in [1009, 65537]:
    d = pb_check(p, 200); d["kind"]="pullback_exact"; logj(d); print(d); sys.stdout.flush()
# order factorisation sanity of Jacobian by the Frobenius polynomial on actual A1 instances (small k)
for line in open('work/params.txt'):
    t = line.split()
    if t[0]=="A1" and int(t[1]) in (10,12,14,16):
        k,idx,p,r,ha,hb,nE1,nE2,n1,cof = map(int,t[1:])
        F = GF(p); R.<X> = F[]; h = X^2+ha*X+hb; g=(X-F(r)^2)*h
        d = pb_check(p, 100, (F,R,F(r),F(ha),F(hb),h,g)); d["kind"]="pullback_exact_A1inst"; d["k"]=k; d["idx"]=idx
        d["nJac_match"] = (d["nJac_frob"] == nE1*nE2); logj(d); print(d); sys.stdout.flush()

# ---------- (a3) genus 3 ----------
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
for k in [12,16,20]:
    p = prime_for(k)
    for idx in range(3):
        F,R,r,h3,g4 = make_g3(p)
        a = [int(c) for c in h3.list()]
        # E1: Y^2 = g4(X), monic quartic -> 2 points at infinity
        nE1 = count_aff_quartic(p, g4) + 2
        H = HyperellipticCurve(R(g4*R.gen())); PH = H.frobenius_polynomial(); nH = int(PH(1))
        # E1 frobenius poly
        tE = p+1-nE1; PE = PolynomialRing(ZZ,'T')([p,-tE,1])
        nJ = nE1*nH
        s2 = power_sum2(PE) + power_sum2(PH)
        c2proj = p^2+1 - s2
        d = dict(kind="A3curve", k=k, p=p, idx=idx, r=int(r), h3=a, nE1=int(nE1), nHJ=nH, nJac=int(nJ), fac_nJac=str(factor(nJ)), c2proj=int(c2proj))
        logj(d)
        out.write("A3 %d %d %d %d %d %d %d %d %d %d %d\n" % (k,idx,p,int(r),a[0],a[1],a[2],int(nE1),nH,int(nJ),int(c2proj)))
        out.flush(); print("A3",k,idx,flush=True)
# direct check of #Jac(C3) = #E1 * #Jac(H) on the odd degree-7 model at small p
for p in [211, 307, 1009]:
    for idx in range(2):
        F,R,r,h3,g4 = make_g3(p)
        T,Fz = odd_model3(F,r,g4); assert Fz.degree()==7, Fz.degree()
        C7 = HyperellipticCurve(Fz); P7 = C7.frobenius_polynomial()
        nE1 = count_aff_quartic(p,g4)+2; H = HyperellipticCurve(R(g4*R.gen())); PH=H.frobenius_polynomial()
        tE=p+1-nE1; PE = PolynomialRing(ZZ,'T')([p,-tE,1])
        ok = (P7 == PE*PH) if P7.parent()==PE.parent() else (P7.change_ring(ZZ)==(PE*PH).change_ring(ZZ))
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
