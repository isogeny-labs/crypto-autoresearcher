#!/usr/bin/env python3
"""SA-23 per-cell analysis: reads work/s_{p}_{d}.txt (+Y listing), builds sections (+-Y), Gram, rank, lattice det,
specialisation coverage on 3 fibres. Usage: cell.py p d enum_seconds method"""
import sys, json, math, random, time
from fractions import Fraction
import numpy as np
p=int(sys.argv[1]); d=int(sys.argv[2]); enum_sec=float(sys.argv[3]); method=sys.argv[4]
chi=d//6; DX=2*chi; DY=3*chi
secs=[]
for line in open(f"work/s_{p}_{d}.txt"):
    a,b=line.split("|"); X=tuple(map(int,a.split())); Y=tuple(map(int,b.split()))
    secs.append((X,Y)); secs.append((X,tuple((-y)%p for y in Y)))
S=len(secs)
def trim(a):
    a=list(a)
    while a and a[-1]%p==0: a.pop()
    return a
def sub(a,b):
    n=max(len(a),len(b)); return trim([((a[i] if i<len(a) else 0)-(b[i] if i<len(b) else 0))%p for i in range(n)])
def pmod(a,b):
    a=list(a); inv=pow(b[-1],p-2,p)
    while len(a)>=len(b):
        c=a[-1]*inv%p; sh=len(a)-len(b)
        for i in range(len(b)): a[sh+i]=(a[sh+i]-c*b[i])%p
        a=trim(a)
        if not a: break
    return a
def gcd_deg(a,b):
    while b: a,b=b,pmod(a,b)
    return len(a)-1
def inter(P,Q):
    dx=sub(P[0],Q[0]); dy=sub(P[1],Q[1])
    if not dx and not dy: return None
    if dx and dy: aff=gcd_deg(dx,dy)
    else: aff=len(dx)-1 if dx else len(dy)-1   # one coordinate identical: the other's zeros
    ox=2*chi-(len(dx)-1) if dx else 10**9; oy=3*chi-(len(dy)-1) if dy else 10**9
    return aff+min(ox,oy)
# verify on surface
def pmul(a,b):
    r=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): r[i+j]=(r[i+j]+x*y)%p
    return r
for X,Y in secs[:200]+secs[-50:]:
    lhs=trim(pmul(Y,Y)); rhs=pmul(pmul(X,X),X); rhs=rhs+[0]*(d+1-len(rhs)); rhs[0]=(rhs[0]+1)%p; rhs[d]=(rhs[d]+1)%p
    assert lhs==trim(rhs), "section off surface"
t0=time.time()
G=np.zeros((S,S),dtype=np.int64)
for i in range(S):
    G[i,i]=2*chi
    for j in range(i+1,S):
        G[i,j]=G[j,i]=chi-inter(secs[i],secs[j])
tg=time.time()-t0
ev=np.linalg.eigvalsh(G.astype(float)); psd=bool(ev.min()>-1e-6)
# exact rank & greedy basis (fraction-free over Q via modular rank with big prime, double check with float)
Q1=(1<<61)-1
def greedy():
    basis=[]; rows=[]  # echelon in terms of Gram rows mod Q1
    ech=[]  # list of (pivot, row)
    for i in range(S):
        r=[int(x)%Q1 for x in G[i]]
        for pv,er in ech:
            c=r[pv]
            if c: r=[(a-c*b)%Q1 for a,b in zip(r,er)]
        nz=next((k for k,x in enumerate(r) if x),None)
        if nz is None: continue
        inv=pow(r[nz],Q1-2,Q1); r=[a*inv%Q1 for a in r]; ech.append((nz,r)); basis.append(i)
    return basis
basis=greedy(); r=len(basis)
import sympy
Gb=sympy.Matrix([[int(G[a,b]) for b in basis] for a in basis]); detb=Gb.det()
assert detb>0
# coordinates of every section in basis (rational), via Gb^-1
Gi=Gb.inv()
coords=[]
den=1
for i in range(S):
    v=sympy.Matrix([int(G[i,b]) for b in basis]); c=Gi*v
    coords.append(c)
    for x in c: den=den*sympy.denom(x)//math.gcd(den,sympy.denom(x))
rows=[[int(x*den) for x in c] for c in coords]
# integer row reduction (HNF-like) of rows -> basis of the coordinate lattice
def lattice_basis(rows,n):
    H=[]; rows=[list(x) for x in rows]
    for col in range(n):
        piv=[x for x in rows if x[col]!=0]; rest=[x for x in rows if x[col]==0]
        while len(piv)>1:
            piv.sort(key=lambda x:abs(x[col])); a=piv[0]; new=[a]
            for b in piv[1:]:
                q=b[col]//a[col]; b=[y-q*z for y,z in zip(b,a)]
                (new if b[col]!=0 else rest).append(b)
            piv=new
        if piv: H.append(piv[0])
        rows=[x for x in rest if any(x)]
    return H
H=lattice_basis(rows,r); assert len(H)==r
detH=abs(sympy.Matrix(H).det()); covol=sympy.Rational(detH,den**r)
detL=detb*covol**2
# supplementary: shortest vector of lattice via LLL if available (only report section min)
min_h=2*chi
# fibres
def E_add(P,Q,c):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P; x2,y2=Q
    if x1==x2:
        if (y1+y2)%p==0: return None
        l=3*x1*x1*pow(2*y1,p-2,p)%p
    else: l=(y2-y1)*pow(x2-x1,p-2,p)%p
    x3=(l*l-x1-x2)%p; return (x3,(l*(x1-x3)-y1)%p)
def E_mul(k,P,c):
    R=None
    while k:
        if k&1: R=E_add(R,P,c)
        P=E_add(P,P,c); k>>=1
    return R
def lpf(n):
    f=1;m=n;q=2
    while q*q<=m:
        while m%q==0: f=q; m//=q
        q+=1
    return max(f,m) if m>1 else f
fib=[]
for t in (2,3,5,7,11,13):
    if len(fib)==3: break
    c=(pow(t,d,p)+1)%p
    if c==0 or t%p==0: continue
    cnt=1+sum(1+(0 if ((x**3+c)%p==0) else (1 if pow((x**3+c)%p,(p-1)//2,p)==1 else -1)) for x in range(p))
    N=cnt
    if p%3==2: assert cnt==p+1  # supersingular: x->x^3 bijective
    ell=lpf(N); cof=N//ell
    imgs=set(); imgsE=set(); 
    for X,Y in secs:
        xv=sum(a*pow(t,i,p) for i,a in enumerate(X))%p; yv=sum(a*pow(t,i,p) for i,a in enumerate(Y))%p
        assert (yv*yv-xv**3-c)%p==0
        P=(xv,yv); imgsE.add(P); imgs.add(E_mul(cof,P,c))
    fib.append({"t0":t,"N":N,"ell":ell,"cofactor":cof,"distinct_G_images":len(imgs),"coverage_G":len(imgs)/ell,
                "distinct_E_images":len(imgsE),"coverage_E":len(imgsE)/N})
out={"p":p,"d":d,"chi":chi,"S":S,"rank":r,"det_lattice":str(detL),"det_greedy_basis":str(detb),"min_height_sections":min_h,
     "gram_psd":psd,"gram_seconds":round(tg,2),"fibres":fib,"coverage_G_mean":float(np.mean([f['coverage_G'] for f in fib])),
     "enumeration_method":method,"family":("supersingular" if p%d==d-1 else ("ordinary_control" if p%d==1 else "other")),"host_load":open("/proc/loadavg").read().split()[0],"seconds":enum_sec,"rank_bound_12chi_minus_4":12*chi-4}
print(json.dumps(out))
