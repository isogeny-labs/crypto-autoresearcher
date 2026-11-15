import json, numpy as np, math
rng=np.random.default_rng(1)
out={}
def fit(bits,klo,khi,stat):
    rows=[r for r in json.load(open('exp6_rows_%d.json'%bits)) if klo<=r['k']<=khi]
    ks=np.array([r['k'] for r in rows]); L=[np.array(r['nodes_list'],float) for r in rows]
    def slope(Ls):
        y=np.log2([stat(v) for v in Ls]); return np.polyfit(ks,y,1)[0]
    s=slope(L); bs=[]
    for _ in range(2000):
        bs.append(slope([v[rng.integers(0,len(v),len(v))] for v in L]))
    return s,np.percentile(bs,[2.5,97.5]),len(ks),ks.max()-ks.min()
res={}
for (bits,klo,khi) in [(96,5,13),(96,5,12),(64,4,8),(64,5,9),(52,4,7),(40,3,5)]:
    for name,stat in (('median',np.median),('mean',np.mean)):
        s,ci,n,dbl=fit(bits,klo,khi,stat)
        res['%d_k%d-%d_%s'%(bits,klo,khi,name)]=dict(slope=s,ci=list(ci),points=n,doublings=int(dbl))
        print("bits=%d k=%d..%d (%d doublings) %-6s slope %.3f  95%% CI [%.3f, %.3f]"%(bits,klo,khi,dbl,name,s,*ci))
json.dump(res,open('exp6_fit.json','w'),indent=1)
print("--- per-iteration overhead  nodes/(B+1)  (median over trials); asymptotic exponent of the loop = 1 + slope of this ratio")
for bits,klo,khi in [(96,6,12),(64,5,8)]:
    rows=[r for r in json.load(open('exp6_rows_%d.json'%bits)) if klo<=r['k']<=khi]
    print(bits,[(r['k'],round(float(np.median(r['nodes_list']))/(r['B']+1),3)) for r in rows])
