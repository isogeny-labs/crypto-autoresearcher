# Weighted vs unweighted LLL on the 3-dim kernel lattice L_R (planted 2-decompositions, y^2=x^3+7).
# Theory (Theorem W2/R1): weighted box (B^4,B^3,B^2), weight w=9, isolation for B^9 < p  => delta < 1/9=0.111.
# Unweighted (repo calibration): B^12 < p  => delta < 1/12 = 0.083.
import sympy as sp, random, json
from fpylll import IntegerMatrix, LLL
random.seed(13)
A,B0=0,7
def run(pbits,deltas,trials,weighted):
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
            while True:
                x1=random.randrange(1,Bnd); x2=random.randrange(1,Bnd)
                if x1!=x2 and on_curve(x1) and on_curve(x2): break
            P1=(x1,int(sp.sqrt_mod(x1**3+B0,p))); P2=(x2,int(sp.sqrt_mod(x2**3+B0,p)))
            xr=add(P1,P2)[0]
            s1,s2=(Bnd,Bnd*Bnd) if weighted else (1,1)   # column scalings: c0*1, c1*B, c2*B^2
            M=IntegerMatrix(3,3)
            M[0,0]=p; M[1,0]=(-xr)%p; M[1,1]=s1; M[2,0]=(-xr*xr)%p; M[2,2]=s2
            LLL.reduction(M)
            target=((x1*x2)**2-4*B0*(x1+x2), -2*((x1+x2)*(x1*x2)+2*B0), (x1-x2)**2)
            tw=(target[0],target[1]*s1,target[2]*s2)
            found=any(tuple(M[i,j] for j in range(3)) in (tw,tuple(-c for c in tw)) for i in range(3))
            succ+=found
        out.append(dict(p_bits=pbits,delta=round(d,3),B=Bnd,weighted=weighted,success=succ,trials=trials))
    return out
rows=[]
ds=[0.06,0.07,0.08,0.09,0.10,0.105,0.11,0.115,0.12,0.13]
for pb in (72,96,128):
    for w in (False,True):
        rows+=run(pb,ds,40,w)
for r in rows: print(r,flush=True)
json.dump(rows,open('exp3_rows.json','w'),indent=1)
