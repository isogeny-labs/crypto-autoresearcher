import json, numpy as np, random
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
rows=json.load(open('out/sd_rows.json'))
def get(q,pl,null):
    d={}
    for r in rows:
        if r['q']==q and r['planted']==pl and r['null']==null and r['status']=='ok': d.setdefault(r['t'],[]).append(r['sd'])
    return d
def slope(d,rng,B=2000):
    ts=sorted(d); 
    def fit(vals): return np.polyfit(ts,vals,1)[0]
    pt=fit([np.median(d[t]) for t in ts]); bs=[]
    for _ in range(B):
        bs.append(fit([np.median([rng.choice(d[t]) for _ in d[t]]) for t in ts]))
    return pt,np.percentile(bs,[2.5,97.5])
rng=random.Random(0); out={}
fig,ax=plt.subplots(figsize=(6,4))
for (q,pl,null,lab) in [(2,True,False,"q=2 planted"),(2,False,False,"q=2 no solution"),(2,True,True,"q=2 random same-support null"),(3,True,False,"q=3 planted")]:
    d=get(q,pl,null); ts=sorted(d); s,ci=slope(d,rng); out[lab]=dict(slope=float(s),ci=[float(c) for c in ci],medians={t:float(np.median(d[t])) for t in ts})
    ax.plot(ts,[np.median(d[t]) for t in ts],'o-',label=f"{lab}: slope {s:.2f}")
ts=np.arange(1,9); ax.plot(ts,2*ts+4,'k--',label="exact Macaulay D=2t+4 (q=2, S nowhere 0)")
ax.plot(np.arange(1,11),[3,4,4,4,4,5,5,5,5,6],'s:',color='gray',label="repo F4 medians (their encoding)")
ax.set_xlabel("tower length t"); ax.set_ylabel("solving degree (m=2)"); ax.legend(fontsize=6); fig.tight_layout(); fig.savefig("fig_slope.png",dpi=150)
json.dump(out,open("out/slopes.json","w"),indent=1); print(json.dumps(out,indent=1))
