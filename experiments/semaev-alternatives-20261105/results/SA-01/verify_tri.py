import sys, math, random
from plant_m2 import *
t=int(sys.argv[1]); dl=float(sys.argv[2]); bits=int(sys.argv[3]); kind=sys.argv[4]
n,sups,cf,om=pres('i' if kind=='x' else 'ii',2)
lam=[(2,2)] if kind=='x' else [(2,0)]
gens=[(sups[0],lam[0])]
val,M,lev=extract_M(n,gens,cf(dl),t)
rng=random.Random(3); p=mkprime(bits,rng); xr=rng.randrange(2,p)
f=poly_x(xr,p) if kind=='x' else poly_e(xr,p)
f=monic(f,lam[0],p)
Bd=int(p**dl); X=(Bd,Bd) if kind=='x' else (2*Bd,Bd*Bd)
rows=build_lattice(2,[f],lam,M,lev,t,p,X)
# triangular check: leading monomial of row for y must be y under order with weights: use om-like generic weight
w=(1000,1) if kind=='e' else (1000,1)  # lam=(2,0): e1 dominates ; for x: lam=(2,2) dominated by any positive weights
ok=True; logdet=0
for y,sh in rows:
    lead=max(sh.keys(),key=lambda e:(w[0]*e[0]+w[1]*e[1],e))
    if lead!=y: ok=False
    logdet+=math.log2(sh[y])+sum(math.log2(X[j])*y[j] for j in range(2))
print(kind,t,dl,"dim",len(M),"triangular",ok,"log2det/(t*dim*bits)=",round(logdet/(t*len(M)*bits),4),"LP val",round(val,4), "ratio det<p^(t dim)?",logdet<t*len(M)*math.log2(p))
