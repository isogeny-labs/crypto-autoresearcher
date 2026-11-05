import json, sys, glob, math, collections, random
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
random.seed(1); rng=np.random.default_rng(1)
files=sys.argv[1].split(',')
rows=[json.loads(l) for f in files for l in open(f)]
cells=[rows[i:i+3] for i in range(0,len(rows),3)]
recs=[]
for rat,ctl,itg in cells:
    M=rat['p']/2
    recs.append(dict(k=rat['k'],p=rat['p'],h=rat['h'],B=rat['B'],N=rat['N'],
        gen_exp=rat['N']*rat['B']/M,          # expected number of (pair,sign) sums landing in base for an unstructured base
        rat_trip=rat['triples'],rat_dist=rat['triples_distinct_xR'],glob=rat['listed_global'],wr=rat['listed_wrapped'],
        ctl_trip=ctl['triples'],int_trip=itg['triples'],int_B=itg['B'],int_N=itg['N'],
        rat_collfrac=1-rat['D']/rat['N'],ctl_collfrac=1-ctl['D']/ctl['N'],rat_hits=rat['hits'],ctl_hits=ctl['hits']))
json.dump(recs,open('cells.json','w'),indent=0)
# ---- table by (k,h)
agg=collections.defaultdict(lambda: collections.defaultdict(float))
for r in recs:
    a=agg[(r['k'],r['h'])]; a['n']+=1
    for key in ('B','gen_exp','rat_trip','rat_dist','glob','wr','ctl_trip','int_trip','rat_hits','ctl_hits'): a[key]+=r[key]
lines=['| k | h | primes | mean B | structured triples (distinct x_R) | listed global / wrapped | control triples | integer-base triples | generic expectation N*B/M | ratio struct/generic |','|---|---|---|---|---|---|---|---|---|---|']
for key in sorted(agg):
    a=agg[key]; lines.append(f"| {key[0]} | {key[1]} | {int(a['n'])} | {a['B']/a['n']:.0f} | {int(a['rat_trip'])} ({int(a['rat_dist'])}) | {int(a['glob'])} / {int(a['wr'])} | {int(a['ctl_trip'])} | {int(a['int_trip'])} | {a['gen_exp']:.3f} | {a['rat_trip']/max(a['gen_exp'],1e-9):.1f} |")
open('table_main.md','w').write('\n'.join(lines)+'\n'); print('\n'.join(lines))
# ---- fit 1: log2(ratio) vs log2 p at fixed h (cells with h>=48), bootstrap over cells
def fit(x,y): 
    A=np.vstack([x,np.ones_like(x)]).T; return np.linalg.lstsq(A,y,rcond=None)[0]
out={}
for hh in (48,64,80,100):
    # pooled by k: ratio = sum(trip)/sum(gen) per k; bootstrap resampling primes within k
    byk=collections.defaultdict(list)
    for r in recs:
        if r['h']==hh: byk[r['k']].append(r)
    if len(byk)<3: continue
    ks=sorted(byk)
    def slope(sample):
        xs=[];ys=[]
        for k in ks:
            s=sample[k]; t=sum(r['rat_trip'] for r in s); g=sum(r['gen_exp'] for r in s)
            if t>0: xs.append(math.log2(np.mean([r['p'] for r in s]))); ys.append(math.log2(t/g))
        return fit(np.array(xs),np.array(ys))[0] if len(xs)>=2 else float('nan')
    s0=slope(byk); bs=[]
    for _ in range(2000):
        smp={k:[random.choice(byk[k]) for _ in byk[k]] for k in ks}; bs.append(slope(smp))
    bs=[b for b in bs if b==b]
    out[f'slope_log2ratio_vs_log2p_h{hh}']=(round(s0,3),round(float(np.percentile(bs,2.5)),3),round(float(np.percentile(bs,97.5)),3))
# ---- fit 2: exponent of global relation count in h at each k (per-prime counts), bootstrap
for k in sorted({r['k'] for r in recs}):
    hs=sorted({r['h'] for r in recs if r['k']==k and r['h']>=16})
    def sl(sample):
        xs=[];ys=[]
        for h in hs:
            v=[r['rat_trip'] for r in sample[h]]
            if np.mean(v)>0: xs.append(math.log2(h)); ys.append(math.log2(np.mean(v)))
        return fit(np.array(xs),np.array(ys))[0]
    byh={h:[r for r in recs if r['k']==k and r['h']==h] for h in hs}
    if any(len(v)==0 for v in byh.values()): continue
    s0=sl(byh); bs=[sl({h:[random.choice(byh[h]) for _ in byh[h]] for h in hs}) for _ in range(2000)]
    out[f'exponent_triples_vs_h_k{k}']=(round(s0,3),round(float(np.percentile(bs,2.5)),3),round(float(np.percentile(bs,97.5)),3))
    # triples per base point
json.dump(out,open('fits.json','w'),indent=1); print(json.dumps(out,indent=1))
# ---- figure
fig,ax=plt.subplots(1,2,figsize=(11,4))
for k,c in ((40,'C0'),(48,'C1'),(56,'C2')):
    hs=sorted({r['h'] for r in recs if r['k']==k})
    if not hs: continue
    ax[0].plot(hs,[np.mean([r['rat_trip'] for r in recs if r['k']==k and r['h']==h]) for h in hs],'o-',color=c,label=f'structured, p~2^{k}')
    ax[0].plot(hs,[np.mean([r['gen_exp'] for r in recs if r['k']==k and r['h']==h])+1e-6 for h in hs],'--',color=c,label=f'generic N*B/M, p~2^{k}')
ax[0].set_xscale('log');ax[0].set_yscale('log');ax[0].set_xlabel('height bound h');ax[0].set_ylabel('relations per prime (P,Q,P-Q in base)');ax[0].legend(fontsize=7)
for hh,c in ((64,'C3'),(100,'C4')):
    xs=[];ys=[]
    for k in (40,48,56):
        s=[r for r in recs if r['k']==k and r['h']==hh]
        if s and sum(r['rat_trip'] for r in s)>0: xs.append(k); ys.append(sum(r['rat_trip'] for r in s)/sum(r['gen_exp'] for r in s))
    ax[1].semilogy(xs,ys,'o-',color=c,label=f'h={hh}')
ax[1].set_xlabel('log2 p');ax[1].set_ylabel('measured / generic');ax[1].legend()
plt.tight_layout();plt.savefig('fig_yield.png',dpi=130)
