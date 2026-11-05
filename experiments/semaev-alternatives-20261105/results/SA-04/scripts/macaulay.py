# Dense incremental Macaulay-matrix engine over F_p (p < 2^16), float64 BLAS exact arithmetic.
# Ring = F_p[vars]/(d^2-d for boolean vars). Monomial = exponent tuple (boolean entries capped at 1).
# Reports the maximal degree of a minimal leading monomial of the degree-D Macaulay row space (grevlex, "solving degree")
import numpy as np, itertools, time
from collections import defaultdict

class Ring:
    def __init__(self,nv,boolmask,p):
        self.n=nv; self.bm=boolmask; self.p=p
    def mmul(self,a,b):
        r=tuple(min(x+y,1) if bb else x+y for x,y,bb in zip(a,b,self.bm))
        return r
    def deg(self,a): return sum(a)
    def pmul_mono(self,poly,mu):
        out={}
        p=self.p
        for m,c in poly.items():
            r=self.mmul(m,mu); out[r]=(out.get(r,0)+c)%p
        return out
    def monos_deg(self,d):
        """all monomials of degree exactly d"""
        res=[]
        def rec(i,rem,cur):
            if i==self.n:
                if rem==0: res.append(tuple(cur))
                return
            mx=min(rem,1) if self.bm[i] else rem
            # remaining capacity check
            for e in range(mx+1):
                cur.append(e); rec(i+1,rem-e,cur); cur.pop()
        rec(0,d,[])
        return res
def grevkey(m):
    return (sum(m), tuple(-x for x in reversed(m)))

def macaulay_profile(ring,gens,Dmax,p,verbose=True,rowchunk=1500,colcap=9000,time_limit=1e9):
    """gens: list of dict poly (nonhomogeneous). Returns per-D info: pivots (leading monos), rank, #cols."""
    t0=time.time()
    n=ring.n
    gdeg=[max(sum(m) for m in g) for g in gens]
    colmono=[]; colidx={}
    E=np.zeros((0,0)); pivcols=[]   # rows RREF, pivot = highest column nonzero
    info=[]
    z=tuple([0]*n); colidx[z]=0; colmono.append(z); E=np.zeros((0,1))
    for D in range(1,Dmax+1):
        # add columns of degree D, sorted ascending grevlex (higher = larger)
        newm=sorted(ring.monos_deg(D),key=grevkey)
        if len(colmono)+len(newm)>colcap:
            info.append(dict(D=D,aborted='colcap',cols=len(colmono)+len(newm))); break
        for m in newm: colidx[m]=len(colmono); colmono.append(m)
        C=len(colmono)
        if E.shape[1]<C:
            E=np.hstack([E,np.zeros((E.shape[0],C-E.shape[1]))])
        # new rows: generator g times monomial mu with deg(g)+deg(mu)==D (nominal degree)
        def rows_iter():
            for gi,g in enumerate(gens):
                dm=D-gdeg[gi]
                if dm<0: continue
                for mu in ring.monos_deg(dm):
                    yield ring.pmul_mono(g,mu)
        buf=[]
        def flush(buf):
            nonlocal E,pivcols
            if not buf: return
            Bk=np.zeros((len(buf),C))
            for i,poly in enumerate(buf):
                for m,c in poly.items():
                    if c: Bk[i,colidx[m]]=c
            if len(pivcols):
                Bk=(Bk-(Bk[:,pivcols]@E))%p
            Bk=Bk[np.any(Bk!=0,axis=1)]
            if len(Bk)==0: return
            # echelonize block (pivot = highest nonzero col)
            newp=[];rows=[]
            R=Bk
            r=0
            while r<len(R):
                nz=np.nonzero(R[r])[0]
                if len(nz)==0:
                    R=np.delete(R,r,axis=0); continue
                c=nz[-1]
                inv=pow(int(R[r,c]),-1,p)
                R[r]=(R[r]*inv)%p
                col=R[:,c].copy(); col[r]=0
                idx=np.nonzero(col)[0]
                if len(idx): R[idx]=(R[idx]-np.outer(col[idx],R[r]))%p
                newp.append(c); r+=1
            # R now RREF within block (rows have pivot cols c, zero elsewhere in pivot cols)
            if len(newp):
                if E.shape[0]:
                    E=(E-(E[:,newp]@R))%p
                E=np.vstack([E,R]); pivcols=pivcols+newp
        cnt=0
        for poly in rows_iter():
            buf.append(poly)
            if len(buf)>=rowchunk: flush(buf); buf=[]
            if time.time()-t0>time_limit:
                info.append(dict(D=D,aborted='time',cols=C)); return info,colmono
        flush(buf)
        LM=[colmono[c] for c in pivcols]
        info.append(dict(D=D,cols=C,rank=len(pivcols),LM=LM,t=time.time()-t0))
        if verbose: print("  D",D,"cols",C,"rank",len(pivcols),"q",C-len(pivcols),"t %.1f"%(time.time()-t0),flush=True)
        qs=[r['cols']-r['rank'] for r in info if 'rank' in r]
        if len(qs)>=4 and len(set(qs[-4:]))==1: break
    return info,colmono

def divides(a,b): return all(x<=y for x,y in zip(a,b))
def analyse(info,ring):
    """From pivots per D compute: minimal generators of LM ideal, max degree of min gens at each D,
       standard-monomial count (quotient dim, counted in ring) if finite."""
    out=[]
    gens_sofar=[]
    for rec in info:
        if 'aborted' in rec: out.append(rec); continue
        LM=rec['LM']
        mins=[]
        for m in sorted(LM,key=lambda m:sum(m)):
            if not any(divides(g,m) for g in mins): mins.append(m)
        D=rec['D']
        maxdeg=max((sum(m) for m in mins),default=0)
        # finiteness: pure power for every non-boolean var, and the boolean ones are finite automatically
        nb=[i for i in range(ring.n) if not ring.bm[i]]
        pure=all(any(sum(g)==g[i] and g[i]>0 for g in mins) for i in nb)
        K=None
        if pure:
            # count standard monomials: enumerate over non-boolean exponents below pure power, boolean subsets
            lim=[min(g[i] for g in mins if sum(g)==g[i] and g[i]>0) for i in nb]
            K=0
            bi=[i for i in range(ring.n) if ring.bm[i]]
            import itertools
            for ex in itertools.product(*[range(l) for l in lim]):
                for sub in itertools.product((0,1),repeat=len(bi)):
                    m=[0]*ring.n
                    for i,e in zip(nb,ex): m[i]=e
                    for i,e in zip(bi,sub): m[i]=e
                    if not any(divides(g,tuple(m)) for g in mins): K+=1
        out.append(dict(D=D,cols=rec['cols'],rank=rec['rank'],n_min=len(mins),maxdeg_min=maxdeg,finite=pure,K=K))
    return out
