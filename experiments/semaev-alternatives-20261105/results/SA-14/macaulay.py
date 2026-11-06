"""Independent Macaulay-matrix check of the solving degree (small n). Uses sympy for polynomial parsing,
numpy mod-p elimination. D_mac = min D s.t. leading monomials of the degree<=D Macaulay row space generate lead(I)."""
import itertools, subprocess, sys, numpy as np, random, re
import sympy as sp
from kummer_sd import instance, SING
def monos(n,D):
    # all exponent tuples of total degree <= D, sorted dp descending (degree, then grevlex)
    out=[]
    for d in range(D+1):
        for c in itertools.combinations_with_replacement(range(n),d):
            e=[0]*n
            for i in c: e[i]+=1
            out.append(tuple(e))
    # grevlex key: higher degree first; ties: smaller last variable exponent is bigger
    out.sort(key=lambda e:(-sum(e),) + tuple(e[::-1]))
    return out
def system(p,q,t,a,b,xr):
    vs=[];eqs=[]
    for s in (1,2):
        names=[f"x{s}"]+[f"w{s}_{j}" for j in range(1,t)]
        vs+=names
        for j in range(1,t): eqs.append(f"{names[j]}-{names[j-1]}**{q}")
        eqs.append(f"{names[t-1]}**{q}-1")
    S=f"(x1-x2)**2*{xr}**2-2*((x1+x2)*(x1*x2+{a})+2*{b})*{xr}+(x1*x2-{a})**2-4*{b}*(x1+x2)"
    return vs,eqs+[S]
def leads_full(p,vs,eqs):
    code=f"ring r={p},({','.join(vs)}),dp; ideal I={','.join(e.replace('**','^') for e in eqs)}; ideal G=std(I); int i; for(i=1;i<=size(G);i++){{print(\"L \"+string(leadexp(G[i])));}} quit;"
    out=subprocess.run([SING,"-q"],input=code,capture_output=True,text=True).stdout
    return [tuple(int(x) for x in l[2:].split(",")) for l in out.splitlines() if l.startswith("L ")]
def rank_leads(rows,ncols,p):
    M=rows.copy()%p; r=0; leads=[]
    for c in range(ncols):
        piv=np.nonzero(M[r:,c])[0]
        if len(piv)==0: continue
        k=r+piv[0]; M[[r,k]]=M[[k,r]]
        M[r]=(M[r]*pow(int(M[r,c]),p-2,p))%p
        nz=np.nonzero(M[:,c])[0]; nz=nz[nz!=r]
        if len(nz): M[nz]=(M[nz]-np.outer(M[nz,c],M[r]))%p
        leads.append(c); r+=1
        if r==M.shape[0]: break
    return leads
def dmac(p,q,t,seed,Dmax=12,planted=True):
    rng=random.Random(seed); a,b,xr=instance(p,q,t,rng,planted)
    vs,eqs=system(p,q,t,a,b,xr); n=len(vs)
    syms=sp.symbols(vs); polys=[sp.Poly(sp.sympify(e,locals=dict(zip(vs,syms))),*syms,modulus=p) for e in eqs]
    LG=leads_full(p,vs,eqs)
    for D in range(2,Dmax+1):
        ms=monos(n,D); idx={m:i for i,m in enumerate(ms)}
        rows=[]
        for f in polys:
            df=f.total_degree(); terms=f.terms()
            for mm in monos(n,D-df):
                r=np.zeros(len(ms),dtype=np.int64)
                for e,c in terms:
                    r[idx[tuple(x+y for x,y in zip(e,mm))]]=int(c)%p
                rows.append(r)
        if len(rows)*len(ms)>3e8: return None
        L=[ms[c] for c in rank_leads(np.array(rows),len(ms),p)]
        if all(any(all(l[i]<=g[i] for i in range(n)) for l in L) for g in LG): return D
    return None
if __name__=="__main__":
    p,q,t,seed=map(int,sys.argv[1:5]); print(p,q,t,seed,dmac(p,q,t,seed))
