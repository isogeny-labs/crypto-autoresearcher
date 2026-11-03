"""Derivation check (not a measurement): transfer matrix of the Semaev S_3 network
vs Cayley-graph character sums on E(F_p)/{+-1}. Toy primes, deterministic curve search."""
import numpy as np, sys, json

def pts(p,a,b):
    sq={}
    for y in range(p): sq.setdefault(y*y%p,[]).append(y)
    P=[None]
    for x in range(p):
        for y in sq.get((x**3+a*x+b)%p,[]): P.append((x,y))
    return P
def add(P,Q,p,a):
    if P is None: return Q
    if Q is None: return P
    if P[0]==Q[0] and (P[1]+Q[1])%p==0: return None
    if P==Q: l=(3*P[0]*P[0]+a)*pow(2*P[1],-1,p)%p
    else: l=(Q[1]-P[1])*pow(Q[0]-P[0],-1,p)%p
    x=(l*l-P[0]-Q[0])%p; return (x,(l*(P[0]-x)-P[1])%p)
def isprime(n): return n>1 and all(n%d for d in range(2,int(n**.5)+1))
def S3(x1,x2,x3,p,a,b):
    return ((x1-x2)**2*x3*x3-2*((x1+x2)*(x1*x2+a)+2*b)*x3+(x1*x2-a)**2-4*b*(x1+x2))%p

out=[]
for p in [61,101,163,211,307]:
  for a in range(1,p):
    b=1; E=pts(p,a,b); n=len(E)
    if not isprime(n) or n<5: continue
    G=E[1]; log={None:0}; R=None
    for k in range(n): log[R]=k; R=add(R,G,p,a)   # R ranges over all points
    break
  Ex=sorted({P[0] for P in E[1:]})            # x-coords of E(F_p)\{O}
  B=max(3,int(p**0.5)); FB=[x for x in Ex if x<=B*3][:B]
  # M over the FULL alphabet F_p (as the lead defines the network)
  M=np.zeros((p,p))
  for y in range(p):
    for z in range(p):
      M[y,z]=sum(1 for x in FB if S3(x,y,z,p,a,b)==0)
  idxE=Ex; idxT=[x for x in range(p) if x not in set(Ex)]
  cross=M[np.ix_(idxE,idxT)].sum()
  ME=M[np.ix_(idxE,idxE)]
  evM=np.sort(np.linalg.eigvalsh(ME))
  # character sums: S = {+-F : x(F) in FB}; lambda_j = sum_{s in S} cos(2 pi j log s / n)
  S=[log[P] for P in E[1:] if P[0] in FB]
  lam=np.array([sum(np.cos(2*np.pi*j*s/n) for s in S) for j in range((n-1)//2+1)])
  lamS=np.sort(lam)
  # Cauchy interlacing: deleting the O-orbit from a (symmetrised) (k+1)-matrix
  k=len(evM); inter=all(lamS[i]-1e-9<=evM[i]<=lamS[i+1]+1e-9 for i in range(k))
  exact=np.allclose(evM, lamS[1:]) or np.allclose(evM, lamS[:-1])
  out.append(dict(p=p,a=a,b=b,n=n,FB=len(FB),E_block=k,twist_block=len(idxT),
       cross_mass_E_twist=float(cross),interlaces=bool(inter),
       equals_char_sums=bool(exact),max_gap=float(np.max(np.abs(evM-lamS[1:])))))
print(json.dumps(out,indent=1))
