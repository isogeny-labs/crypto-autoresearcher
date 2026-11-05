import random,time
from common import *
from bilat import solve
p=mkp(64); rng=random.Random(5)
xs,ys=sp_syms=None,None
def S3dict_x1_v(xR,c):
    # f(x1,v)=S3(x1,c+v,xR), a=0,b=7 ; expand via sympy once
    import sympy as sp
    X1,V=sp.symbols('X1 V'); x2=c+V
    e=sp.expand((X1-x2)**2*xR**2-2*((X1+x2)*(X1*x2)+14)*xR+(X1*x2)**2-28*(X1+x2))
    return {tuple(m):int(cf)%p for m,cf in sp.Poly(e,X1,V).terms()}
for B in (16,32,64):
    ok=0;T=0
    for _ in range(6):
        x1,x2,R=plant(p,B,rng)
        c=max(0,x2-B//4) ; c=x2-rng.randint(0,B//4)
        f=S3dict_x1_v(R[0],c)
        t0=time.time(); s=solve(f,p,B,B//4+1,2); T+=time.time()-t0
        ok+= (x1,x2-c) in s
    print(B,ok,'/6',T/6,'s each')
