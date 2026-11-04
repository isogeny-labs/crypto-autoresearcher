"""Derivation check for D2 (HD2a): do rank deficits of the low-degree evaluation matrix occur exactly when the
multipliers b_i satisfy a short integer relation sum c_i b_i = 0 mod N (|c|_inf <= 2)? Prediction from the memo:
>= 80% of random triples exact; every deficient triple has such a relation. p = 211 and p = 227, D = 3, 4, t = 3."""
import itertools, json, math, random, sys, numpy as np
sys.path.insert(0, "/home/user/crypto-autoresearcher/docs/reports/lowdeg-rank-20261104")
from modrank import rank_mod_p
from lowdeg_rank import add, find_point, isprime, monomials, eval_matrix, expected_generic
def pts_count(p,a,b): return p+1+sum((pow((x**3+a*x+b)%p,(p-1)//2,p)+1)%p-1 for x in range(p))
def short_rel(bs, N, bound=2):
    best=None
    for c in itertools.product(range(-bound,bound+1), repeat=len(bs)):
        if any(c) and sum(ci*bi for ci,bi in zip(c,bs))%N==0:
            n=max(abs(x) for x in c)
            if best is None or n<best[0]: best=(n,c)
    return best
out=[]
for p in (211, 227):
    a=next(a for a in range(1,p) if isprime(pts_count(p,a,1)) and pts_count(p,a,1)!=p); N=pts_count(p,a,1)
    G=find_point(p,a,1); mult=[None]; R=None
    for k in range(1,N): R=add(R,G,p,a); mult.append(R)
    triples=[]
    if p==211:
        for D in (3,4):   # the original seeds of lowdeg_rank_check.py
            rng=random.Random(20261104+3*10+D); triples.append(("orig",D,[rng.randrange(2,N) for _ in range(3)]))
    rng=np.random.default_rng(4242+p)
    for i in range(50): triples.append(("fresh",None,[int(x) for x in rng.integers(2,N-1,3)]))
    for tag,Dfix,bs in triples:
        for D in ((Dfix,) if Dfix else (3,4)):
            rows=[[c for P in [mult[(bi*k)%N] for bi in bs] for c in P] for k in range(1,N) if all(mult[(bi*k)%N] for bi in bs)]
            C=len(rows); mons=monomials(6,D); r=rank_mod_p(eval_matrix(np.array(rows),mons,p),p)
            exp=expected_generic(C,3,D); rel=short_rel(bs,N)
            out.append(dict(p=p,N=N,tag=tag,D=D,b=bs,rank=r,expected=exp,deficit=exp-r,short_relation=rel))
json.dump(out,open("d2.json","w"))
for p in (211,227):
    for D in (3,4):
        f=[o for o in out if o["p"]==p and o["D"]==D and o["tag"]=="fresh"]
        dfc=[o for o in f if o["deficit"]>0]
        print(p,D,"fresh exact %d/%d"%(len(f)-len(dfc),len(f)),"| deficient w/o rel<=2:",sum(1 for o in dfc if o["short_relation"] is None),"| exact with rel<=2:",sum(1 for o in f if o["deficit"]==0 and o["short_relation"]))
for o in out:
    if o["tag"]=="orig": print("orig",o)
