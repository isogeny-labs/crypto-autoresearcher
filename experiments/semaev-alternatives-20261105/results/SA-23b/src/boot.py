# bootstrap CI (2000 resamples, seed 23) for per-prime all-20 accuracy of the best frozen-class rule, and R_J frequencies
import json,random,collections
random.seed(23)
res=json.load(open('results/law_scan.json')); best=res[0]
rs=[json.loads(l) for l in open('results/jacobi.jsonl')]
# recompute per-prime correctness of best rule
CAND=[1,2,3,4,6,8,9,12,18,24,27,36]; CAND=CAND+[-c for c in CAND]
iu,iv=CAND.index(best[4]),CAND.index(best[5])
tr=[r for r in rs if r['p']<10000]; te=[r for r in rs if r['p']>10000]
T=[collections.defaultdict(collections.Counter) for _ in range(20)]
for r in tr:
    k=(r['s4'][iu],r['s3'][iv])
    for a in range(20): T[a][k][r['exps'][a]]+=1
tab=[{k:c.most_common(1)[0][0] for k,c in T[a].items()} for a in range(20)]
ok=[all(tab[a].get((r['s4'][iu],r['s3'][iv]))==r['exps'][a] for a in range(20)) for r in te]
def ci(v):
    n=len(v); bs=sorted(sum(random.choices(v,k=n))/n for _ in range(2000)); return bs[50],bs[1949]
print("best frozen-class rule u,v=",best[4],best[5],"heldout all20",sum(ok)/len(ok),"CI",ci(ok),"n",len(ok))
c=collections.Counter(r['R'] for r in rs); n=len(rs)
for k in sorted(c):
    v=[1 if r['R']==k else 0 for r in rs]; print("R_J=%d"%k,c[k],c[k]/n,ci(v))
