import json,numpy as np
res=json.load(open('crossings.json'))
out=[]
def fit(Ks,cs,x):  # c = c_inf + a*x(K)
    A=np.vstack([np.ones(len(Ks)),[x(k) for k in Ks]]).T; co=np.linalg.lstsq(A,cs,rcond=None)[0]; return co[0]
for kind in ('box','simplex'):
  for bits in (48,64,96):
    for pl in (True,False):
        R=sorted([r for r in res if r['kind']==kind and r['bits']==bits and r['planted']==pl and r['cross_l2'] is not None],key=lambda r:r['K'])
        for kmin in (2,3):
            S=[r for r in R if r['K']>=kmin]
            if len(S)<3: continue
            Ks=[r['K'] for r in S]; cs=[r['cross_l2'] for r in S]; ms=[r['mink'] for r in S]
            for name,x in (('1/K',lambda k:1/k),('1/K^2',lambda k:1/k**2)):
                c=fit(Ks,cs,x); loo=[fit(Ks[:i]+Ks[i+1:],cs[:i]+cs[i+1:],x) for i in range(len(Ks)) if len(Ks)>2]
                exc=[c_-m for c_,m in zip(cs,ms)]
                out.append(dict(kind=kind,bits=bits,planted=pl,kmin=kmin,model=name,Ks=Ks,ext=round(c,4),loo_min=round(min(loo),4),loo_max=round(max(loo),4),excess=[round(e,4) for e in exc]))
for o in out: print(o)
json.dump(out,open('extrapolation.json','w'),indent=1)
print("--- excess-corrected: 1/6 + extrapolated (cross_l2 - mink)")
out2=[]
for kind in ('box','simplex'):
  for bits in (48,64,96):
    for pl in (True,False):
        R=sorted([r for r in res if r['kind']==kind and r['bits']==bits and r['planted']==pl and r['cross_l2'] is not None],key=lambda r:r['K'])
        S=[r for r in R if r['K']>=3]
        if len(S)<3: continue
        Ks=[r['K'] for r in S]; ex=[r['cross_l2']-r['mink'] for r in S]
        for name,x in (('1/K',lambda k:1/k),('1/K^2',lambda k:1/k**2)):
            e=fit(Ks,ex,x); loo=[fit(Ks[:i]+Ks[i+1:],ex[:i]+ex[i+1:],x) for i in range(len(Ks))]
            o=dict(kind=kind,bits=bits,planted=pl,model=name,Ks=Ks,excess_inf=round(float(e),4),est=round(1/6+float(e),4),loo=[round(1/6+float(l),4) for l in loo]); out2.append(o); print(o)
json.dump(out2,open('extrapolation_excess.json','w'),indent=1)
