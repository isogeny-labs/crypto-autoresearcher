import json, sys, time, itertools, random
import numpy as np
from coppersmith_lp import *
random.seed(1)
PS=json.load(open('pres_supports.json'))
def tup(l): return [tuple(q) for q in l]
def leads(sups, omegas):
    out=[]
    for om in omegas:
        lam=[]
        for s in sups:
            best=max(s,key=lambda c:(sum(om[j]*c[j] for j in range(len(c))),c))
            lam.append(best)
        key=tuple(lam)
        if key not in out: out.append(key)
    return out
def omegas_for(n,k=8):
    om=[[1]*n]
    for j in range(n):
        v=[1]*n; v[j]=10; om.append(v)
        v=[10]*n; v[j]=1; om.append(v)
    for _ in range(k):
        om.append([random.random()+0.05 for _ in range(n)])
    return om
def reach_best(n,sups,cost_fn,t,omegas,hi=0.5,tol=3e-4):
    best=(-1,None)
    for lam in leads(sups,omegas):
        gens=[(list(s),l) for s,l in zip(sups,lam)]
        r=reach(n,gens,cost_fn,t,hi=hi,tol=tol)
        if r>best[0]: best=(r,lam)
    return best
def pres(name,m):
    d=2**(m-1)
    if name=='i':   # S_{m+1} in x
        n=m; sups=[[tuple([d]*m),tuple([0]*m)]]
        return n,sups,(lambda dl:[dl]*n),[[1]*n]
    if name=='ii':  # Vieta, weights k
        n=m; sups=[[g for g in itertools.product(range(d+1),repeat=m) if sum(g)==d]]
        return n,sups,(lambda dl:[dl*(k+1) for k in range(n)]),omegas_for(n,4)
    if name=='iii': # norm system: full-size alphas then e_k
        v=PS[str(m)]; nf=len(v['vars'])-m; n=len(v['vars'])
        sups=[tup(s) for s in v['sups']]
        return n,sups,(lambda dl:[1.0]*nf+[dl*(k+1) for k in range(m)]),omegas_for(n,10)
    if name=='iiiG':  # m=2 only: Groebner generators {alpha - L(e), Vieta conic}; alpha full-size
        assert m==2
        lin=[(1,0,0),(0,1,0),(0,0,1),(0,0,0)]
        con=[(0,i,j) for i in range(3) for j in range(3) if i+j<=2]
        return 3,[lin,con],(lambda dl:[1.0,dl,2*dl]),omegas_for(3,6)
    if name=='iv':  # chained S3: x1..xm, aux u1..u_{m-2}
        if m==2: return pres('i',2)
        A=tup(PS['S3_x1x2u']); Bx=tup(PS['S3_ux3'])
        # variable order: x1..xm, u1..u_{m-2}
        n=m+(m-2); sups=[]
        def emb(sup,idxs):
            out=[]
            for s in sup:
                e=[0]*n
                for q,i in enumerate(idxs): e[i]=s[q]
                out.append(tuple(e))
            return out
        # S3(x1,x2,u1); S3(u_{j},x_{j+2},u_{j+1})...; last S3(u_{m-2},x_m,xR)
        sups.append(emb(A,[0,1,m]))
        for j in range(1,m-2):
            sups.append(emb(A,[m+j-1,j+1,m+j]))
        sups.append(emb(Bx,[m+m-3,m-1]))
        return n,sups,(lambda dl:[dl]*m+[1.0]*(m-2)),omegas_for(n,10)
    if name=='iv_tree': # m=4 balanced: S3(x1,x2,u1),S3(x3,x4,u2),S3(u1,u2,xR)
        A=tup(PS['S3_x1x2u']); Bx=tup(PS['S3_ux3'])
        n=6
        def emb(sup,idxs):
            out=[]
            for s in sup:
                e=[0]*n
                for q,i in enumerate(idxs): e[i]=s[q]
                out.append(tuple(e))
            return out
        return n,[emb(A,[0,1,4]),emb(A,[2,3,5]),emb(Bx,[4,5])],(lambda dl:[dl]*4+[1.0]*2),omegas_for(n,10)
    if name=='v':   # 2-torsion product S(x,xR)S(x,xR+T): box 2d
        n=m; sups=[[tuple([2*d]*m),tuple([0]*m)]]
        return n,sups,(lambda dl:[dl]*n),[[1]*n]
    if name=='vi':  # integer lift: S(x)-p*c ; c exponent (d-1)+delta*Dtop
        Dtop={2:2,3:6,4:12}[m]
        n=m+1; sups=[[tuple([d]*m+[0]),tuple([0]*m+[1]),tuple([0]*(m+1))]]
        return n,sups,(lambda dl:[dl]*m+[(d-1)+dl*Dtop]),[[1]*n]
if __name__=="__main__":
    name=sys.argv[1]; m=int(sys.argv[2]); tmax=int(sys.argv[3])
    n,sups,cf,om=pres(name,m)
    rows=[]
    for t in range(1,tmax+1):
        t0=time.time()
        r,lam=reach_best(n,sups,cf,t,om,hi=0.45)
        rows.append(dict(pres=name,m=m,t=t,reach=r,lam=lam,sec=round(time.time()-t0,1)))
        print(rows[-1],flush=True)
        if time.time()-t0>600: break
    json.dump(rows,open(f'ceil_{name}_m{m}.json','w'))
