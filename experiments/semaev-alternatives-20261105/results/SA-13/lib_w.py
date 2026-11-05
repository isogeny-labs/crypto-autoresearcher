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
