# reduce the SA-09 levels 1,5,7 data (36a1, K=Q(sqrt-23)) mod 3 primes and dump the 45 points (read-only use of ../SA-09 data)
import json,math,sys
from fp import *   # SA-09's fp.py copy (y^2=x^3+1)
d=json.load(open('../SA-09/data_157.json')); lv=sorted(int(k) for k in d['levels'])
ps=find_primes(math.lcm(*lv),2**19,2**21,3); print(ps)
out={}
for p in ps:
    F=Fp(p,d); r1=F.roots(1)[0][0]; emb={1:r1}
    for m in lv:
        if m!=1: emb[m]=[r for r in F.roots(m)[0] if F.Hval(1,m,r)==r1][0]
    pts={m:F.points(m,emb[m]) for m in lv}
    assert all((y*y-x**3-1)%p==0 for m in lv for x,y in pts[m])
    out[p]={str(m):pts[m] for m in lv}
    print(p,sum(len(v) for v in pts.values()),len(set(q for v in pts.values() for q in v)))
json.dump(out,open('pts36.json','w'))
