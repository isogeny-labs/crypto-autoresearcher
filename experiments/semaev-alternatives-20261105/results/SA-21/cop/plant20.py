"""Planted fpylll recovery, m=2: Edwards y (a=8,d=4) vs Weierstrass x control. usage: plant20.py <edwards|weier> <bits> <t> <ntrials> <deltas> <seed>"""
import sys, json, random, time, math, itertools
sys.path.insert(0,'/home/user/semaev-runs/SA-19'); sys.path.insert(0,'.')
from lib19 import Curve, sqrt_mod
import numpy as np, sympy
from fpylll import IntegerMatrix, LLL
_orig=LLL.reduction
LLLT=[0.0,0]
def _timed(A,*a,**k):
    t=time.perf_counter(); r=_orig(A,*a,**k); LLLT[0]+=time.perf_counter()-t; LLLT[1]+=1; return r
LLL.reduction=_timed
from model2 import *
kind,bits,t,nt=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]); deltas=[float(x) for x in sys.argv[5].split(',')]; seed=int(sys.argv[6])
rng=random.Random(seed)
P=json.load(open("results/step1_polytope.json"))
def rand_prime(bits):
    while True:
        p=int(sympy.nextprime(rng.getrandbits(bits)|(1<<(bits-1))))
        if p.bit_length()==bits and p%4==3: return p
# fixed shift set from the MILP at the certified delta (slightly below)
S=P['edwards_m2' if kind=='edwards' else 'weier_m2']['support']
coset=(0,) if kind=='edwards' else None
M=Model2(S,(2,2),t,coset=coset)
dc=reach(M,lambda d:[d,d],hi=0.25,tl=60)
d0=dc-0.0005
cz=M.P@np.array([d0,d0]); obj=np.concatenate([cz,-M.lev])
res=milp(obj,constraints=LinearConstraint(M.A,-np.inf,0),integrality=np.ones(M.N),bounds=Bounds(0,1),options=dict(time_limit=60,mip_rel_gap=1e-6))
x=np.round(res.x).astype(int); zs=[M.pts[i] for i in range(M.nz) if x[i]]
vsel={}
for q,(yi,k,cl) in enumerate(M.vl):
    if x[M.nz+q]: vsel[M.pts[yi]]=k
Mset=sorted(zs,key=lambda y:(sum(y),y)); dim=len(Mset); cidx={y:i for i,y in enumerate(Mset)}
print("kind",kind,"t",t,"cert",round(dc,4),"dim",dim,"rows with k>0",len(vsel),flush=True)
def pmul(a,b):
    r={}
    for m1,c1 in a.items():
        for m2,c2 in b.items():
            m=(m1[0]+m2[0],m1[1]+m2[1]); r[m]=r.get(m,0)+c1*c2
    return r
def fpoly_edwards(yR,p):
    # coefficients in (y1,y2) of E3(y1,y2,yR), lead y1^2y2^2 : yR^2-1
    c={(2,2):yR*yR-1,(2,0):-yR*yR+2,(0,2):-yR*yR+2,(1,1):-2*yR,(0,0):2*yR*yR-2}
    return c
def fpoly_weier(xR,p,A=3,B=5):
    x1,x2=sympy.symbols('x1 x2')
    Sx=(x1-x2)**2*xR**2-2*((x1+x2)*(x1*x2+A)+2*B)*xR+(x1*x2-A)**2-4*B*(x1+x2)
    return {m:int(c) for m,c in sympy.Poly(sympy.expand(Sx),x1,x2).terms()}
def make_inst(p,Bd):
    if kind=='edwards':
        E=Curve(1,0,p,a2=6)
        pts=[]
        while len(pts)<2:
            y=rng.randrange(2,Bd+2); u=(1+y)*pow(1-y,-1,p)%p; Pt=E.lift_x(u)
            if Pt is None: continue
            if rng.random()<.5: Pt=E.neg(Pt)
            if pts and pts[0][1][0]==Pt[0]: continue
            pts.append((y,Pt))
        R=E.add(pts[0][1],pts[1][1]); yR=(R[0]-1)*pow(R[0]+1,-1,p)%p
        return (pts[0][0],pts[1][0]),yR,fpoly_edwards(yR,p)
    E=Curve(3,5,p)
    while True:
        a=E.random_small(Bd,rng); b=E.random_small(Bd,rng)
        if a[0]!=b[0]: break
    R=E.add(a,b); return (a[0],b[0]),R[0],fpoly_weier(R[0],p)
def trial(p,Bd):
    root,tgt,f=make_inst(p,Bd)
    f={m:c%p for m,c in f.items()}
    assert sum(c*root[0]**m[0]*root[1]**m[1] for m,c in f.items())%p==0
    inv=pow(f[(2,2)],-1,p); f={m:(c*inv)%p for m,c in f.items()}; f[(2,2)]=1
    # monic with lead coefficient exactly 1 requires f-> f/lead mod p; keep integers
    X=Bd
    pw=[{(0,0):1}]
    for k in range(t): pw.append(pmul(pw[-1],f))
    A=IntegerMatrix(dim,dim)
    rows=[]
    for y in Mset:
        k=vsel.get(y,0); s=(y[0]-2*k,y[1]-2*k); row=[0]*dim
        if k==0: row[cidx[y]]=p**t*X**(y[0]+y[1])
        else:
            for m,c in pw[k].items():
                mm=(s[0]+m[0],s[1]+m[1]); row[cidx[mm]]=c*p**(t-k)*X**(mm[0]+mm[1])
        rows.append(row)
    for i,r in enumerate(rows):
        for j,v in enumerate(r): A[i,j]=v
    LLL.reduction(A,delta=0.99)
    good=[]
    for i in range(dim):
        h={};ok=True
        for j,y in enumerate(Mset):
            v=int(A[i,j])
            if v:
                d=X**(y[0]+y[1])
                if v%d: ok=False;break
                h[y]=int(v)//int(d)
        if not ok: continue
        if sum(c*root[0]**m[0]*root[1]**m[1] for m,c in h.items())==0: good.append(h)   # exact over Z
        if len(good)>=6: break
    for i in range(len(good)):
        for j in range(i+1,len(good)):
            a,b=sympy.symbols('a b')
            p1=sum(c*a**m[0]*b**m[1] for m,c in good[i].items()); p2=sum(c*a**m[0]*b**m[1] for m,c in good[j].items())
            if sympy.resultant(p1,p2,b)!=0: return True
    return False
out=[]
for dl in deltas:
    ok=0
    for _ in range(nt):
        p=rand_prime(bits); Bd=int(p**dl)
        ok+=trial(p,Bd)
    row=dict(kind=kind,bits=bits,t=t,delta=dl,succ=ok,n=nt,cert=round(dc,4),dim=dim); print(row,flush=True); out.append(row)
    row['lll_calls']=LLLT[1]; row['lll_s']=LLLT[0]; row['lll_ms_per_call']=1000*LLLT[0]/max(1,LLLT[1]); print(row,flush=True)
    open("results/cop.jsonl","a").write(json.dumps(row)+"\n")
