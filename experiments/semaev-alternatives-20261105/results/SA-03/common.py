import random, sympy as sp
A,B0=0,7
def prime34(bits):
    p=int(sp.nextprime(2**bits))
    while p%4!=3: p=int(sp.nextprime(p))
    return p
def is_qr(a,p): return pow(a%p,(p-1)//2,p)==1
def sqrt34(a,p): return pow(a%p,(p+1)//4,p)
def add(P,Q,p):
    (xp,yp),(xq,yq)=P,Q
    l=(yq-yp)*pow(xq-xp,-1,p)%p
    xr=(l*l-xp-xq)%p; return (xr,(l*(xp-xr)-yp)%p)
def neg(P,p): return (P[0],(-P[1])%p)
def pt(x,p): return (x,sqrt34(x**3+B0,p))
def planted(p,B,n,rng):
    """n targets R=P1+P2, x1<x2<=B, f(x_i) QR. returns list of (xR,x1,x2)"""
    out=[]
    if sum(is_qr(x**3+B0,p) for x in range(1,B+1))<2: return None
    while len(out)<n:
        x1=rng.randrange(1,B+1); x2=rng.randrange(1,B+1)
        if x1==x2 or not is_qr(x1**3+B0,p) or not is_qr(x2**3+B0,p): continue
        if x1>x2: x1,x2=x2,x1
        R=add(pt(x1,p),pt(x2,p),p)
        if R[0] in (0,): continue
        out.append((R[0],x1,x2))
    return out
def S3vec(x1,x2): return ((x1*x2)**2-28*(x1+x2), -2*((x1+x2)*x1*x2+14), (x1-x2)**2)
