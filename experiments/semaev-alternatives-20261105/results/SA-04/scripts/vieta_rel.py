# Eliminate alpha from the norm system: find the polynomial relation F(e_1..e_m)=0 (mod p) by kernel of evaluations.
import random, itertools, sys, json, numpy as np, sympy as sp
from nsys import *
def monos(n,d):
    out=[]
    for tot in range(d+1):
        for c in itertools.combinations_with_replacement(range(n),tot):
            e=[0]*n
            for i in c: e[i]+=1
            out.append(tuple(e))
    return out
def nullspace_mod(M,p):
    M=[list(map(int,r)) for r in M]; rows=len(M); cols=len(M[0])
    piv=[];r=0
    A=np.array(M,dtype=np.int64)%p
    for c in range(cols):
        nz=np.nonzero(A[r:,c])[0]
        if len(nz)==0: continue
        i=r+nz[0]; A[[r,i]]=A[[i,r]]
        A[r]=(A[r]*pow(int(A[r,c]),-1,p))%p
        for j in range(rows):
            if j!=r and A[j,c]: A[j]=(A[j]-A[j,c]*A[r])%p
        piv.append(c); r+=1
        if r==rows: break
    free=[c for c in range(cols) if c not in piv]
    ns=[]
    for f in free:
        v=np.zeros(cols,dtype=np.int64); v[f]=1
        for i,c in enumerate(piv): v[c]=(-A[i,f])%p
        ns.append(v)
    return ns
def relation(m,p=1000003,seed=3):
    rng=random.Random(seed)
    a,b=random_curve(p,rng)
    while True:
        xR=rng.randrange(2,p); yQ=sqrt_mod(xR**3+a*xR+b,p)
        if yQ: break
    al,lead,q,rem=norm_Q(m,a,b,p,xR,yQ)
    li=int(lead)
    fq=[sp.lambdify(al,qq,'math') for qq in q[1:]]
    for d in range(1,2*m+3):
        mons=monos(m,d)
        rows=[]
        for _ in range(len(mons)+15):
            av=[rng.randrange(p) for _ in al]
            e=[(int(fq[k-1](*av))*pow(li,-1,p)*(-1)**k)%p for k in range(1,m+1)]
            rows.append([(lambda v: __import__("functools").reduce(lambda x,y:x*y%p,v,1))([pow(e[i],mo[i],p) for i in range(m)]) for mo in mons])
        ns=nullspace_mod(rows,p)
        if ns:
            return d,mons,ns,(a,b,xR,yQ,p)
if __name__=="__main__":
    out={}
    for m in (2,3,4):
        d,mons,ns,par=relation(m)
        v=ns[0]
        supp=[mons[i] for i in range(len(mons)) if v[i]]
        print("m",m,"deg",d,"kernel dim",len(ns),"support size",len(supp),"of",len(mons),flush=True)
        out[m]=dict(deg=d,kdim=len(ns),support=supp)
    json.dump(out,open('../out/vieta_support.json','w'))
