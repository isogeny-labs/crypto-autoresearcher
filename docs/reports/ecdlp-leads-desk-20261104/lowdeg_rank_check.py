"""Derivation check (not a measurement): rank over F_p of the evaluation matrix
V[k, monomial] = monomial(x_1,y_1,...,x_t,y_t) at the coordinates of [b_i k]P, k = 1..N-1,
for monomials of total degree <= D in 2t variables. Full rank N-1 means every subset S of
candidate logs is the zero set (on the candidates) of some degree-<=D test, so log2 N tests
binary-search k. b_i drawn at random (seed fixed)."""
import itertools, json, random
def isprime(n): return n>1 and all(n%d for d in range(2,int(n**.5)+1))
def pts(p,a,b):
    sq={}
    for y in range(p): sq.setdefault(y*y%p,[]).append(y)
    return [None]+[(x,y) for x in range(p) for y in sq.get((x**3+a*x+b)%p,[])]
def add(P,Q,p,a):
    if P is None: return Q
    if Q is None: return P
    if P[0]==Q[0] and (P[1]+Q[1])%p==0: return None
    l=((3*P[0]*P[0]+a)*pow(2*P[1],-1,p) if P==Q else (Q[1]-P[1])*pow(Q[0]-P[0],-1,p))%p
    x=(l*l-P[0]-Q[0])%p; return (x,(l*(P[0]-x)-P[1])%p)
def rank_mod(rows,p):
    M=[r[:] for r in rows]; r=0; cols=len(M[0]) if M else 0
    for c in range(cols):
        piv=next((i for i in range(r,len(M)) if M[i][c]%p),None)
        if piv is None: continue
        M[r],M[piv]=M[piv],M[r]; inv=pow(M[r][c],-1,p)
        M[r]=[v*inv%p for v in M[r]]
        for i in range(len(M)):
            if i!=r and M[i][c]:
                f=M[i][c]; M[i]=[(vi-f*vr)%p for vi,vr in zip(M[i],M[r])]
        r+=1
    return r
out=[]
for p in (101,211):
    a=next(a for a in range(1,p) if isprime(len(pts(p,a,1))))
    E=pts(p,a,1); N=len(E); G=E[1]
    mult=[None]; R=None
    for k in range(1,N): R=add(R,G,p,a); mult.append(R)
    for t,D in ((1,3),(2,3),(3,3),(4,3),(3,4)):
        rng=random.Random(20261104+t*10+D); bs=[rng.randrange(2,N) for _ in range(t)]
        mons=[e for e in itertools.product(range(D+1),repeat=2*t) if sum(e)<=D]
        rows=[]
        for k in range(1,N):
            coords=[]
            for bi in bs: Pk=mult[(bi*k)%N]; coords+= [Pk[0],Pk[1]]
            rows.append([ (lambda e: eval_mon(e,coords))(e) for e in mons ] if False else
                        [ __import__('math').prod(pow(c,ei,p) for c,ei in zip(coords,e))%p for e in mons])
        out.append(dict(p=p,N=N,t=t,D=D,monomials=len(mons),candidates=N-1,rank=rank_mod(rows,p),full=rank_mod(rows,p)==N-1))
print(json.dumps(out))
