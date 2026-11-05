import json, numpy as np
rng=np.random.default_rng(1)
out={}
for pb in (40,52,64):
    rows=json.load(open(f'sieve_u_p{pb}.json'))
    Bs=np.array([r['B'] for r in rows],float)
    def fit(sel,key):
        y=[];
        for r in rows:
            arr=np.array(r['times'])
            y.append(arr)
        return y
    ts=[np.array(r['times']) for r in rows]
    def slope(ms): return np.polyfit(np.log2(Bs),np.log2(ms),1)[0]
    pt=slope([t.mean() for t in ts])
    bs=[slope([rng.choice(t,len(t)).mean() for t in ts]) for _ in range(2000)]
    lo,hi=np.percentile(bs,[2.5,97.5])
    # sub-fit on largest 5 doublings
    pt5=np.polyfit(np.log2(Bs[-6:]),np.log2([t.mean() for t in ts[-6:]]),1)[0]
    bs5=[np.polyfit(np.log2(Bs[-6:]),np.log2([rng.choice(t,len(t)).mean() for t in ts[-6:]]),1)[0] for _ in range(2000)]
    out[pb]=dict(Bmin=int(Bs[0]),Bmax=int(Bs[-1]),doublings=len(Bs)-1,exponent=pt,ci=[lo,hi],exp_top5=pt5,ci_top5=list(np.percentile(bs5,[2.5,97.5])),
                 recovered=sum(r['recovered'] for r in rows),trials=sum(r['trials'] for r in rows))
    print(pb,out[pb])
json.dump(out,open('fit_sieve.json','w'),indent=1)
