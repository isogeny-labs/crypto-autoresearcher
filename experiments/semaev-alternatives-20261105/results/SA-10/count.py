import pickle, numpy as np, json, collections
c=pickle.load(open('cores.pkl','rb'))
first={}; pairs=[]  # (x1,x2,s)
seen=collections.defaultdict(list)
for i,s in enumerate(c):
    x=i+1
    seen[s].append(x)
pairs=[]
for s,xs in seen.items():
    if len(xs)>1:
        for j in range(1,len(xs)):
            for k in range(j): pairs.append((xs[k],xs[j],s))
pairs.sort(key=lambda t:t[1])
json.dump(pairs,open('pairs.json','w'))
rows=[]
for e in range(8,23):
    B=2**e; n=sum(1 for p in pairs if p[1]<=B); rows.append((e,B,n))
    print(e,B,n)
e=np.array([r[0] for r in rows]);n=np.array([r[2] for r in rows])
# fit log2 n vs log2 B, over e>=8 where n>0
m=n>0
def fit(e,n):
    return np.polyfit(e,np.log2(n),1)[0]
print('slope all',fit(e[m],n[m]))
rng=np.random.default_rng(1)
# bootstrap: resample pairs' x2 positions? use poisson resampling of increments
inc=np.diff(np.concatenate([[0],n]))
bs=[]
for _ in range(2000):
    ii=rng.poisson(inc); nn=np.cumsum(ii)
    mm=nn>0
    if mm.sum()>=4: bs.append(fit(e[mm],nn[mm]))
print('boot CI',np.percentile(bs,[2.5,50,97.5]))
# slopes on sub-ranges
for lo in (8,12,16):
    mm=(e>=lo)&(n>0); print('slope e>=',lo,fit(e[mm],n[mm]))
json.dump(rows,open('counts.json','w'))
print(len(pairs), pairs[:30])
# class sizes
print(collections.Counter(len(v) for v in seen.values()))
