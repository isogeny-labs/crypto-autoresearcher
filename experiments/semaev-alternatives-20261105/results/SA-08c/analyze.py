import json,numpy as np,sys
def mink(K):
    A=2*K;S=[(u,v) for u in range(A+1) for v in range(A+1)]
    return sum(min(K,min(a,b)//2) for a,b in S)/sum(a+b for a,b in S)
def cross(ds,ys):
    for i in range(len(ds)-1):
        if ys[i]<0<=ys[i+1]: return ds[i]+(0-ys[i])*(ds[i+1]-ds[i])/(ys[i+1]-ys[i])
cr={}
old=json.load(open('../SA-08b/crossings.json'))
for r in old:
    if r['bits']==64 and r['kind']=='box' and r['planted'] and r['cross_l2'] and 3<=r['K']<=6: cr[r['K']]=r['cross_l2']
for K in (7,8):
    try: R=json.load(open(f'raw/box_64_{K}.json'))
    except: continue
    ds=sorted({r['delta'] for r in R}); ys=[np.mean([r['l2']-r['hg'] for r in R if r['delta']==d]) for d in ds]
    c=cross(ds,ys); print(K,ds,[round(y,2) for y in ys],c)
    # per-instance-resampled spread
    if c: cr[K]=c
out=dict(rows=[],fits=[])
for K in sorted(cr):
    out['rows'].append(dict(K=K,mink=mink(K),cross=cr[K],signed=cr[K]-mink(K),absolute=abs(cr[K]-mink(K))))
    print(K,round(mink(K),4),round(cr[K],4),'signed %+.4f'%(cr[K]-mink(K)))
Ks=sorted(cr)
def fit(ks,v,x): 
    A=np.vstack([np.ones(len(ks)),[x(k) for k in ks]]).T; return np.linalg.lstsq(A,v,rcond=None)[0][0]
for lab,fn in (('crossing',lambda k:cr[k]),('1/6+excess',lambda k:cr[k]-mink(k)+1/6)):
  for nm,x in (('1/K',lambda k:1/k),('1/K^2',lambda k:1/k**2)):
    v=[fn(k) for k in Ks]; e=fit(Ks,v,x)
    loo=[fit(Ks[:i]+Ks[i+1:],v[:i]+v[i+1:],x) for i in range(len(Ks))]
    out['fits'].append(dict(est=lab,model=nm,Ks=Ks,ext=e,loo_min=min(loo),loo_max=max(loo)))
    print(lab,nm,'ext %.4f LOO [%.4f,%.4f]'%(e,min(loo),max(loo)))
json.dump(out,open('results.json','w'),indent=1)
