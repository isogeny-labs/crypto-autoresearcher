# Certificate weight w_S(m) for the "bottom rung": the vector of T-coefficients of S_{m+1}(x_1..x_m,T).
# w = sum of the degree sequence of the F_p-span of the coefficients (basis-invariant); reach delta=1/w.
import sympy as sp, json, sys, time
P=(1<<61)-1
def S3(u,v,z,a,b):
    return (u-v)**2*z**2-2*((u+v)*(u*v+a)+2*b)*z+(u*v-a)**2-4*b*(u+v)
def rank_mod(rows,ncols):
    rows=[r[:] for r in rows]; rk=0
    for c in range(ncols):
        piv=None
        for i in range(rk,len(rows)):
            if rows[i][c]%P: piv=i;break
        if piv is None: continue
        rows[rk],rows[piv]=rows[piv],rows[rk]
        inv=pow(rows[rk][c],-1,P)
        rows[rk]=[x*inv%P for x in rows[rk]]
        for i in range(len(rows)):
            if i!=rk and rows[i][c]%P:
                f=rows[i][c]; rows[i]=[(x-f*y)%P for x,y in zip(rows[i],rows[rk])]
        rk+=1
    return rk
def degree_sequence(polys,gens):
    """degree sequence of the Q-span of polys (c_d = dim of span inside P_{<=d})."""
    ps=[sp.Poly(q,*gens) for q in polys]
    mons=sorted({m for q in ps for m in q.monoms()},key=lambda m:(sum(m),m))
    idx={m:i for i,m in enumerate(mons)}
    rows=[]
    for q in ps:
        r=[0]*len(mons)
        for m,cf in q.terms():
            r[idx[m]]=int(cf)%P
        rows.append(r)
    n=rank_mod(rows,len(mons))
    maxd=max(sum(m) for m in mons)
    seq=[]; prev=0
    cd=[]
    for d in range(maxd+1):
        cols=[i for i,m in enumerate(mons) if sum(m)>d]
        # dim(W cap P_{<=d}) = n - rank(projection onto monomials of degree>d)
        if cols:
            sub=[[r[i] for i in cols] for r in rows]
            rk=rank_mod(sub,len(cols))
        else: rk=0
        cd.append(n-rk)
    seq=[]
    prev=0
    for d,c in enumerate(cd):
        seq+= [d]*(c-prev); prev=c
    return n,seq
res=[]
for (a,b,label) in [(0,7,'secp256k1-like a=0,b=7'),(2,5,'generic a=2,b=5'),(-3,11,'a=-3,b=11')]:
    x1,x2,x3,x4,x5,z,T=sp.symbols('x1 x2 x3 x4 x5 z T')
    # m=2
    s3=sp.expand(S3(x1,x2,T,a,b))
    co=[sp.Poly(s3,T).coeff_monomial(T**k) for k in range(3)]
    n,seq=degree_sequence(co,(x1,x2))
    res.append(dict(curve=label,m=2,Tdeg=2,n=n,seq=seq,w=sum(seq),reach=1/sum(seq),coef_degrees=[sp.Poly(c,x1,x2).total_degree() for c in co]))
    print(res[-1],flush=True)
    # m=3
    t0=time.time()
    s4=sp.expand(sp.resultant(S3(x1,x2,z,a,b),S3(x3,T,z,a,b),z))
    co=[sp.Poly(s4,T).coeff_monomial(T**k) for k in range(5)]
    n,seq=degree_sequence(co,(x1,x2,x3))
    res.append(dict(curve=label,m=3,Tdeg=4,n=n,seq=seq,w=sum(seq),reach=1/sum(seq),
                    coef_degrees=[sp.Poly(c,x1,x2,x3).total_degree() for c in co],secs=round(time.time()-t0,1)))
    print(res[-1],flush=True)
    if False:
        # m=4 attempt (S_5) with a time guard
        t0=time.time()
        try:
            s4g=sp.expand(sp.resultant(S3(x1,x2,z,a,b),S3(x3,x4,z,a,b),z))   # S_4(x1..x4) with last var x4 -> use as 'z' later
            # S_5(x1..x5)=Res_z(S_3(x1,x2,z), S_4(z,x3,x4,x5)); build S_4(z,x3,x4,x5)
            s4z=sp.expand(sp.resultant(S3(z,x3,x4,a,b) if False else S3(z,x3,sp.Symbol('y'),a,b),S3(x4,x5,sp.Symbol('y'),a,b),sp.Symbol('y')))
            s5=sp.resultant(sp.Poly(S3(x1,x2,z,a,b),z),sp.Poly(s4z,z))
            s5=sp.expand(s5.as_expr() if hasattr(s5,'as_expr') else s5)
            co=[sp.Poly(s5,x5).coeff_monomial(x5**k) for k in range(9)]
            n,seq=degree_sequence(co,(x1,x2,x3,x4))
            res.append(dict(curve=label,m=4,Tdeg=8,n=n,seq=seq,w=sum(seq),reach=1/sum(seq),secs=round(time.time()-t0,1)))
        except Exception as e:
            res.append(dict(curve=label,m=4,error=repr(e)))
        print(res[-1],flush=True)
json.dump(res,open('exp2_rows.json','w'),indent=1)
