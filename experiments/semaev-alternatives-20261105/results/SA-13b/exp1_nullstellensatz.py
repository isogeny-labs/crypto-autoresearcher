# Content lemma: gcd(G0,G1,G2)(x1,x2) divides an explicit integer N0(a,b) for all integers x1,x2.
# We find rational cofactors A_i with sum A_i G_i = 1 (exact linear algebra over Q), clear denominators, and VERIFY the identity by expansion.
import sympy as sp, sys, json, time
x1,x2=sp.symbols('x1 x2')
def cert(a,b,maxdeg):
    e1=x1+x2; e2=x1*x2
    G=[(e2-a)**2-4*b*e1, -2*(e1*(e2+a)+2*b), (x1-x2)**2]
    for d in range(2,maxdeg+1):
        mons=[x1**i*x2**j for i in range(d+1) for j in range(d+1-i)]
        unk=[]; expr=0
        for k in range(3):
            cs=sp.symbols('c%d_0:%d'%(k,len(mons))); unk+=list(cs)
            expr+=G[k]*sum(c*m for c,m in zip(cs,mons))
        P=sp.Poly(sp.expand(expr-1),x1,x2)
        eqs=P.coeffs()
        sol=sp.linsolve(eqs,unk)
        if sol==sp.EmptySet: continue
        s=list(sol)[0]
        free=set().union(*[sp.sympify(v).free_symbols for v in s])
        s=[sp.sympify(v).subs({f:0 for f in free}) for v in s]
        A=[sum(s[k*len(mons)+i]*mons[i] for i in range(len(mons))) for k in range(3)]
        den=sp.ilcm(*[sp.Poly(sp.expand(Ai),x1,x2).as_dict().values().__iter__().__next__().q if False else 1 for Ai in A])
        # common denominator
        dens=[]
        for Ai in A:
            for c in sp.Poly(sp.expand(Ai),x1,x2).coeffs(): dens.append(sp.Rational(c).q)
        D=sp.ilcm(*dens)
        Ai=[sp.expand(D*Ai) for Ai in A]
        chk=sp.expand(sum(Ai[k]*G[k] for k in range(3)))
        assert chk==D and all(all(sp.Rational(c).q==1 for c in sp.Poly(q,x1,x2).coeffs()) for q in Ai)
        return d,int(D)
    return None
out={}
for (a,b) in [(0,7),(2,5),(-3,11),(0,1)]:
    t=time.time(); r=cert(a,b,8)
    print((a,b),r,round(time.time()-t,1),flush=True); out[str((a,b))]=r
json.dump(out,open('exp1_nullstellensatz.json','w'))
