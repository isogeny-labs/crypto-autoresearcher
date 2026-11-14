# Relation rows (Kolyvagin norm relations) from class-group fibres, one binary file per level m (resumable).
# usage: gen_rows.py curve D N Bmax cachedir [tlimit_sec]
import sys,os,time,struct,math
import numpy as np
from arith import project
from arith2 import redforms
import cypari2
from sympy import primerange, jacobi_symbol
curve,D,Nn,Bmax,cdir=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),sys.argv[5]
tlim=float(sys.argv[6]) if len(sys.argv)>6 else 1e9
os.makedirs(cdir,exist_ok=True)
P=2147483629
pari=cypari2.Pari(); pari.allocatemem(10**8); pari(f'E=ellinit({curve})')
inert=[q for q in primerange(3,Bmax+1) if Nn%q and D%q and jacobi_symbol(D%q,q)==-1]
an=pari(f'ellan(E,{Bmax})'); a={q:int(an[q-1]) for q in inert}
import random
MODE=os.environ.get('MODE','')
if MODE=='randa':
    rr=random.Random(5); a={q:rr.randrange(1,10**6) for q in inert}
SH=random.Random(11)
hK=len(redforms(D))
def conductors(B):
    out=[]
    def rec(start,m):
        out.append(m)
        for i in range(start,len(inert)):
            if m*inert[i]>B: break
            rec(i+1,m*inert[i])
    rec(0,1); return sorted(out)
cs=conductors(Bmax)
def hm(m):
    h=hK*m
    from fractions import Fraction
    f=Fraction(h)
    for l in inert:
        if m%l==0: f=f*(l+1)/l   # chi(l)=-1 for inert l ; requires O_K^*={+-1}
    assert f.denominator==1; return int(f)
H={m:hm(m) for m in cs}; off={}; N=0
for m in cs: off[m]=N; N+=H[m]
def primes_of(m): return [l for l in inert if m%l==0]
t0=time.time()
for m in cs:
    fn=f'{cdir}/rows_{m}.bin'
    if os.path.exists(fn) or m==1: continue
    if time.time()-t0>tlim: print('time limit; stopping at',m); break
    Cm=redforms(D*m*m); assert len(Cm)==H[m],(m,len(Cm),H[m])
    rows=[]
    for l in primes_of(m):
        n=m//l; Cn=redforms(D*n*n); idx={f:i for i,f in enumerate(Cn)}
        fib=[[] for _ in Cn]
        for g,f in enumerate(Cm): fib[idx[project(f,D,n,l)]].append(g)
        if MODE=='shuffle':
            perm=list(range(len(Cm))); SH.shuffle(perm); sizes=[len(x) for x in fib]; fib=[]; k=0
            for sz in sizes: fib.append(perm[k:k+sz]); k+=sz
        for ci,fb in enumerate(fib):
            ent=[(off[m]+g,1) for g in fb]
            if a[l]%P: ent.append((off[n]+ci,(-a[l])%P))
            ent.sort(); rows.append(ent)
    with open(fn+'.tmp','wb') as f:
        for ent in rows:
            f.write(struct.pack('<i',len(ent)))
            f.write(np.array([c for c,v in ent],dtype='<i4').tobytes()); f.write(np.array([v for c,v in ent],dtype='<u4').tobytes())
    os.rename(fn+'.tmp',fn)
    print(m,H[m],len(rows),round(time.time()-t0,1),flush=True)
import json
json.dump({'N':N,'conductors':cs,'H':H,'off':off,'a':{str(k):v for k,v in a.items()},'hK':hK,'P':P},open(f'{cdir}/meta.json','w'))
print('done',len(cs),'conductors N=',N,'time',round(time.time()-t0,1))
