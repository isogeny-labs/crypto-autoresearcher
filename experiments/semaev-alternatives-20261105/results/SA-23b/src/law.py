import json, collections, itertools, random
sys_path=None
CAND=[1,2,3,4,6,8,9,12,18,24,27,36]; CAND=CAND+[-c for c in CAND]
rs=[json.loads(l) for l in open('results/jacobi.jsonl')]
tr=[r for r in rs if r['p']<10000]; te=[r for r in rs if r['p']>10000]
print("train",len(tr),"test",len(te))
def key(r,iu,iv): return (r['s4'][iu],r['s3'][iv])
def fit(rows,iu,iv):
    T=[collections.defaultdict(collections.Counter) for _ in range(20)]
    for r in rows:
        k=key(r,iu,iv)
        for a in range(20): T[a][k][r['exps'][a]]+=1
    return [{k:c.most_common(1)[0][0] for k,c in T[a].items()} for a in range(20)]
def score(rows,tab,iu,iv):
    allok=0; el=0; miss=0
    for r in rows:
        k=key(r,iu,iv); good=0
        for a in range(20):
            pr=tab[a].get(k,'NA')
            if pr==r['exps'][a]: good+=1
        el+=good; allok+= good==20
    return allok/len(rows), el/(20*len(rows))
res=[]
for iu in range(24):
    for iv in range(24):
        tab=fit(tr,iu,iv); s_tr=score(tr,tab,iu,iv); s_te=score(te,tab,iu,iv)
        res.append((s_te[0],s_te[1],s_tr[0],s_tr[1],CAND[iu],CAND[iv]))
res.sort(reverse=True)
print("top by held-out all-20 per-prime accuracy: (test_all20, test_per_exp, train_all20, train_per_exp, u, v)")
for x in res[:15]: print(x)
json.dump(res,open('results/law_scan.json','w'))
print("pairs with test_all20>=0.99:",sum(1 for x in res if x[0]>=0.99), "of",len(res))
