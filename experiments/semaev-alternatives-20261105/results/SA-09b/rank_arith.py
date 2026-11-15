# rank/points of the Kolyvagin norm-relation matrix from class-group data.  usage: rank_arith.py curve D N out B1,B2,...
import sys,json,time,math
import numpy as np
from arith import *
import cypari2
from sympy import primerange, jacobi_symbol
curve,D,Nn,out=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
Bs=[int(x) for x in sys.argv[5].split(',')]
pari=cypari2.Pari(); pari.allocatemem(10**8); pari(f'E=ellinit({curve})')
Bmax=max(Bs); inert=[q for q in primerange(3,Bmax+1) if Nn%q and D%q and jacobi_symbol(D%q,q)==-1]
a={q:int(pari(f'ellan(E,{q})[{q}]')) for q in inert}
P=2147483629
def rank_mod(M):
    M=M%P; r=0; rows,cols=M.shape
    for c in range(cols):
        nz=np.nonzero(M[r:,c])[0]
        if len(nz)==0: continue
        p=nz[0]+r
        if p!=r: M[[r,p]]=M[[p,r]]
        inv=pow(int(M[r,c]),-1,P); M[r]=(M[r]*inv)%P
        below=np.nonzero(M[r+1:,c])[0]+r+1
        if len(below):
            f=M[below,c].copy()
            M[below]=(M[below]-(f[:,None]*M[r][None,:])%P)%P
        r+=1
        if r==rows: break
    return r
T=Tower(D); fibcache={}
def conductors(B):
    out=[]
    def rec(start,m):
        out.append(m)
        for i in range(start,len(inert)):
            if m*inert[i]>B: break
            rec(i+1,m*inert[i])
    rec(0,1); return sorted(out)
res=[]; t0=time.time()
for B in Bs:
    cs=conductors(B); off={}; N=0
    for m in cs: off[m]=N; N+=len(T.classes(m))
    rows=[]
    for n in cs:
        for l in inert:
            m=n*l
            if n%l==0 or m>B or m not in off: continue
            key=(n,l)
            if key not in fibcache: fibcache[key]=T.fibres(n,l)
            for ci,fib in enumerate(fibcache[key]):
                rows.append(([off[m]+g for g in fib],off[n]+ci,a[l]))
    M=np.zeros((len(rows),N),dtype=np.int64)
    for r,(cols,c0,al) in enumerate(rows):
        for c in cols: M[r,c]+=1
        M[r,c0]-=al
    rk=rank_mod(M) if len(rows) else 0
    # conjectural character count: N - h_K * sum m  (h_K = class number of K)
    hK=len(T.classes(1)); pred=N-hK*sum(cs)
    rec={'B':B,'conductors':len(cs),'points':N,'relations':len(rows),'rank':rk,'ratio':rk/N,'character_count_rank':pred,'a_zero_primes':[q for q in inert if a[q]==0 and q<=B]}
    res.append(rec); print(rec,round(time.time()-t0,1),flush=True)
    json.dump(res,open(out,'w'),indent=1)
