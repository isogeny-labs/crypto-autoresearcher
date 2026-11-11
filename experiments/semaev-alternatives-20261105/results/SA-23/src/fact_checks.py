#!/usr/bin/env python3
"""Verify brief facts 1-4 numerically + controls. Writes results/controls.json (merged with rows added by other scripts)."""
import json, random, sys
import sympy
from sympy import Poly, symbols, GF
t=symbols('t')
def load(p,d):
    out=[]
    for l in open(f"work/s_{p}_{d}.txt"):
        a,b=l.split("|"); X=list(map(int,a.split())); Y=list(map(int,b.split()))
        out.append((X,Y)); out.append((X,[(-y)%p for y in Y]))
    return out
def P_(c,p): return Poly(list(reversed(c)),t,modulus=p)
def add_fibre(P,Q,p):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P;x2,y2=Q
    if x1==x2:
        if (y1+y2)%p==0: return None
        l=3*x1*x1*pow(2*y1,p-2,p)%p
    else: l=(y2-y1)*pow(x2-x1,p-2,p)%p
    x3=(l*l-x1-x2)%p; return (x3,(l*(x1-x3)-y1)%p)
def test_hom(p,d,npairs,seed):
    rng=random.Random(seed); S=load(p,d); chi=d//6; bad=0; checked=0; zero_denoms=0
    for _ in range(npairs):
        (X1,Y1),(X2,Y2)=rng.sample(S,2)
        x1,y1,x2,y2=[P_(c,p) for c in (X1,Y1,X2,Y2)]
        dx=x2-x1; dy=y2-y1
        if dx.is_zero:  # same X: P=Q or P=-Q
            continue
        # lambda=dy/dx ; X3=lambda^2-x1-x2 ; Y3=lambda(x1-X3)-y1 ; reduce fractions
        num=dy*dy-(x1+x2)*dx*dx; den=dx*dx; g=sympy.gcd(num,den); X3n=sympy.div(num,g)[0]; X3d=sympy.div(den,g)[0]
        # Y3 = (dy*(x1*X3d - X3n) - y1*dx*X3d) / (dx*X3d)
        yn=dy*(x1*X3d-X3n)-y1*dx*X3d; yd=dx*X3d; g2=sympy.gcd(yn,yd); Y3n=sympy.div(yn,g2)[0]; Y3d=sympy.div(yd,g2)[0]
        for t0 in range(p):
            c=(pow(t0,d,p)+1)%p
            if c==0: continue
            den1=int(X3d.eval(t0))%p; den2=int(Y3d.eval(t0))%p
            sp1=(int(x1.eval(t0))%p,int(y1.eval(t0))%p); sp2=(int(x2.eval(t0))%p,int(y2.eval(t0))%p)
            ref=add_fibre(sp1,sp2,p)
            if den1==0 or den2==0:
                zero_denoms+=1; continue   # specialisation of a non-integral section: pole at t0; not testable by evaluation
            got=(int(X3n.eval(t0))*pow(den1,p-2,p)%p, int(Y3n.eval(t0))*pow(den2,p-2,p)%p)
            checked+=1
            if got!=ref: bad+=1
            if checked>=4000: break
        if checked>=4000: break
    return {"p":p,"d":d,"pairs":npairs,"fibre_checks":checked,"mismatches":bad,"skipped_pole_fibres":zero_denoms}
res={"fact3_homomorphism":[test_hom(11,6,60,1),test_hom(23,6,60,2),test_hom(11,12,40,3),test_hom(23,12,30,4)]}
json.dump(res,open("results/controls_fact3.json","w"),indent=1); print(json.dumps(res))
