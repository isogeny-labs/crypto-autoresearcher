from plant_m2 import *
rng=random.Random(5); p=mkprime(72,rng); dl=0.08; t=3
n,sups,cf,om=pres('i',2); lam=[(2,2)]; gens=[(sups[0],lam[0])]
val,M,lev=extract_M(n,gens,cf(dl),t)
print(val,len(M),M[:5], sorted(set(v[0] for v in lev.values())))
Bd=int(p**dl); x1,x2,xr,yr=instance(p,Bd,rng); print(Bd,x1,x2)
f=monic(poly_x(xr,p),lam[0],p); X=(Bd,Bd)
rows=build_lattice(2,[f],lam,M,lev,t,p,X); Mx=to_matrix(rows,M,X)
# sanity: all base rows vanish at root mod p^t
for (y,sh) in rows[:60]:
    v=sum(c*x1**e[0]*x2**e[1] for e,c in sh.items())
    assert v%(p**t)==0,(y,)
LLL.reduction(Mx)
R=[[Mx[i,j] for j in range(len(M))] for i in range(len(M))]
good=recover(R,M,X,(x1,x2)); print(len(good))
import math
print([ math.log2(max(abs(c) for c in r)) for r in R[:6]], "bound", t*72-math.log2(len(M)))
for i in range(3):
    for j in range(i+1,3):
        print(i,j,indep(good[i],good[j]))
a,b=sympy.symbols('a b')
P=[sum(c*a**e[0]*b**e[1] for e,c in h.items()) for h in good]
print(sympy.factor_list(P[0])[0], [ (sympy.degree(q,a),sympy.degree(q,b)) for q in P])
print(sympy.gcd(P[0],P[1]))
