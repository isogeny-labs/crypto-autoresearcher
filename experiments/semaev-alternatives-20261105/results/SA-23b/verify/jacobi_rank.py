# Rank of MW(F_p(t)) for y^2 = x^3 + t^d + 1, p = 1 mod lcm(6,d), via Jacobi sums (Shioda/Weil).
# Piece alpha=(chi^(6), chi^(4b'), chi^(k)) with chi of order 12 (d=12); eigenvalue ~ J(alpha);
# rank over F_p = #{alpha : J(alpha) == p} (Tate; K3 for d=12). Calibrate sign against enumeration.
import sys, cmath
def prim_root(p):
    fac=[q for q in range(2,p) if (p-1)%q==0 and all(q%r for r in range(2,int(q**.5)+1))]
    for g in range(2,p):
        if all(pow(g,(p-1)//q,p)!=1 for q in fac): return g
def ranks(p,d=12):
    L=12 if d==12 else d
    g=prim_root(p); ind=[0]*p; x=1
    for e in range(p-1): ind[x]=e; x=x*g%p
    z=[cmath.exp(2j*cmath.pi*k/L) for k in range(L)]
    def chi(k,u):  # character of exponent k (order | L) at u
        return 0 if u%p==0 else z[(k*ind[u%p])%L]
    def J2(a,b):   # sum_{u+v=1} chi^a(u) chi^b(v)
        return sum(chi(a,u)*chi(b,1-u) for u in range(2,p))
    out={"+p":0,"-p":0,"abs_ok":0,"n":0}
    for b in (L//3, 2*L//3):
        for k in range(1,L):
            a=L//2
            if (a+b+k)%L==0: continue
            # J3 = J(a,b) J(a+b,k) ; then twist by chi_b(-1) chi_k(-1)
            J=J2(a,b)*J2((a+b)%L,k)
            J*=chi(b,-1)*chi(k,-1)
            out["n"]+=1
            if abs(abs(J)-p)<1e-6*p: out["abs_ok"]+=1
            if abs(J-p)<1e-6*p: out["+p"]+=1
            if abs(J+p)<1e-6*p: out["-p"]+=1
    return out
for p in [13,37,61,73,97,109,157,181,193]:
    print(p, "7sq" if pow(7,(p-1)//2,p)==1 else "7nsq", ranks(p))
