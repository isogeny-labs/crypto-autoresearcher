import random, sympy as sp, math
A,B0=0,7
def mkp(bits): return int(sp.nextprime(2**bits))
def curve_funcs(p):
    def qr(x): return pow((x**3+A*x+B0)%p,(p-1)//2,p)==1
    def pt(x): return (x,int(sp.sqrt_mod((x**3+A*x+B0)%p,p)))
    def add(P,Q):
        (xp,yp),(xq,yq)=P,Q
        l=(yq-yp)*pow(xq-xp,-1,p)%p
        xr=(l*l-xp-xq)%p; return (xr,(l*(xp-xr)-yp)%p)
    def neg(P): return (P[0],(-P[1])%p)
    return qr,pt,add,neg
def plant(p,B,rng):
    qr,pt,add,neg=curve_funcs(p)
    while True:
        x1=rng.randint(1,B); x2=rng.randint(1,B)
        if x1!=x2 and qr(x1) and qr(x2): break
    P1,P2=pt(x1),pt(x2); R=add(P1,P2)
    return x1,x2,R
def verify(p,x1,x2,R):
    """check that x1,x2 give a genuine decomposition R = +-P1 +-P2 (some choice of y signs)"""
    qr,pt,add,neg=curve_funcs(p)
    if x1==x2 or not(qr(x1) and qr(x2)): return False
    P1,P2=pt(x1),pt(x2)
    for Q in (P2,neg(P2)):
        S=add(P1,Q)
        if S[0]==R[0]: return True
    return False
def S3poly_e1_coeffs(p,xR,u):
    """16*Q(e1,(e1^2-u^2)/4) mod p as coefficient list [c4..c0]; Q is the Vieta conic of report 3.2 with a=0,b=7"""
    w=u*u%p
    return [1,(-8*xR)%p,(-2*w)%p,(8*xR*w-64*B0)%p,(16*xR*xR*w-64*B0*xR+w*w)%p]
