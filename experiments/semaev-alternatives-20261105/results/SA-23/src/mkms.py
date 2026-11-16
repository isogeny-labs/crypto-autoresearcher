import sys
from collections import defaultdict
# polynomials as dict {monomial tuple of exponents: coeff mod p}; fast own expansion
def system(p,d,fix=None):
    chi=d//6; DX=2*chi; DY=3*chi; n=DX+1+DY+1
    def var(i):
        e=[0]*n; e[i]=1; return {tuple(e):1}
    def mulp(A,B):
        R=defaultdict(int)
        for ma,ca in A.items():
            for mb,cb in B.items():
                m=tuple(a+b for a,b in zip(ma,mb)); R[m]=(R[m]+ca*cb)%p
        return R
    def addp(R,A,c=1):
        for m,v in A.items(): R[m]=(R.get(m,0)+c*v)%p
    X=[var(i) for i in range(DX+1)]; Y=[var(DX+1+i) for i in range(DY+1)]
    X2=defaultdict(dict); 
    X2k=[defaultdict(int) for _ in range(2*DX+1)]
    for i in range(DX+1):
        for j in range(DX+1): addp(X2k[i+j],mulp(X[i],X[j]))
    X3k=[defaultdict(int) for _ in range(3*DX+1)]
    for k in range(2*DX+1):
        for j in range(DX+1): addp(X3k[k+j],mulp(X2k[k],X[j]))
    Y2k=[defaultdict(int) for _ in range(2*DY+1)]
    for i in range(DY+1):
        for j in range(DY+1): addp(Y2k[i+j],mulp(Y[i],Y[j]))
    names=[f"x{i}" for i in range(DX+1)]+[f"y{i}" for i in range(DY+1)]
    zero=tuple([0]*n)
    def fmt(P):
        ts=[]
        for m,c in sorted(P.items()):
            c%=p
            if c==0: continue
            mon="*".join(f"{names[i]}^{e}" if e>1 else names[i] for i,e in enumerate(m) if e)
            ts.append(f"{c}*{mon}" if mon else f"{c}")
        return "+".join(ts) if ts else "0"
    eqs=[]
    for k in range(2*DY+1):
        P=defaultdict(int); addp(P,Y2k[k]); addp(P,X3k[k],-1)
        c=(1 if k==d else 0)+(1 if k==0 else 0)
        if c: P[zero]=(P[zero]-c)%p
        eqs.append(fmt(P))
    if fix:
        t0,xR,yR=fix
        P=defaultdict(int)
        for i in range(DX+1): addp(P,X[i],pow(t0,i,p))
        P[zero]=(-xR)%p; eqs.append(fmt(P))
        P=defaultdict(int)
        for i in range(DY+1): addp(P,Y[i],pow(t0,i,p))
        P[zero]=(-yR)%p; eqs.append(fmt(P))
    return ",".join(names)+"\n"+str(p)+"\n"+",\n".join(eqs)+"\n"
if __name__=="__main__":
    p,d=int(sys.argv[1]),int(sys.argv[2]); open(sys.argv[3],"w").write(system(p,d))
