# Calibration: 'algebraic reconstruction' = level-1 Coppersmith lattice for S3 (3-dim lattice L_R).
import sympy as sp, random, json
from fpylll import IntegerMatrix, LLL
random.seed(7)
A,B0=0,7
def run(pbits, deltas, trials=24):
    p=int(sp.nextprime(2**pbits))
    def on_curve(x): return pow((x**3+A*x+B0)%p,(p-1)//2,p)==1
    def add(P,Q):
        (xp,yp),(xq,yq)=P,Q
        l=(yq-yp)*pow(xq-xp,-1,p)%p
        xr=(l*l-xp-xq)%p; return (xr,(l*(xp-xr)-yp)%p)
    out=[]
    for d in deltas:
        Bnd=int(p**d)
        if Bnd<32: continue
        succ=0
        for _ in range(trials):
            for _k in range(10000):
                x1=random.randrange(1,Bnd); x2=random.randrange(1,Bnd)
                if x1!=x2 and on_curve(x1) and on_curve(x2): break
            P1=(x1,int(sp.sqrt_mod(x1**3+B0,p))); P2=(x2,int(sp.sqrt_mod(x2**3+B0,p)))
            xr=add(P1,P2)[0]
            M=IntegerMatrix(3,3)
            M[0,0]=p; M[1,0]=(-xr)%p; M[1,1]=1; M[2,0]=(-xr*xr)%p; M[2,2]=1
            LLL.reduction(M)
            target=((x1*x2)**2-4*B0*(x1+x2), -2*((x1+x2)*(x1*x2)+2*B0), (x1-x2)**2)
            found=any(tuple(M[i,j] for j in range(3)) in (target, tuple(-c for c in target)) for i in range(3))
            succ+=found
        out.append(dict(p_bits=pbits,delta=round(d,3),B=Bnd,success=succ,trials=trials))
    return out
rows=[]
for pb in (40,56,72,96):
    rows+=run(pb,[0.05,0.06,0.07,0.08,0.09,0.10,0.11,0.12,0.14])
json.dump(rows,open('lat_rows.json','w'),indent=1)
for r in rows: print(r)
