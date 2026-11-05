import ast, glob, numpy as np, json, random
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
rows=[]
for f in ("out/msolve_log.txt","out/msolve_log_b.txt"):
    for l in open(f):
        if l.startswith("{"): rows.append(ast.literal_eval(l))
json.dump(rows,open("out/msolve_rows_all.json","w"))
def tab(q,pl):
    d={}
    for r in rows:
        if r['q']==q and r['planted']==pl and isinstance(r['fdeg'],int): d.setdefault(r['t'],[]).append(r['fdeg'])
    return d
fig,ax=plt.subplots(1,2,figsize=(10,4))
res={}
for q,pl,lab in [(2,True,"q=2 planted"),(2,False,"q=2 no solution"),(3,True,"q=3 planted"),(3,False,"q=3 no solution")]:
    d=tab(q,pl); ts=sorted(d)
    if not ts: continue
    med=[float(np.median(d[t])) for t in ts]
    res[lab]=dict(medians=dict(zip(map(str,ts),med)),n={str(t):len(d[t]) for t in ts})
    ax[0].plot(ts,med,'o-',label=lab)
    if len(ts)>=4:
        sl=np.polyfit(ts,med,1)[0]; res[lab]["ols_slope_all_t"]=float(sl)
        # exact t>=2 half-sample slope of step function
tt=np.arange(1,11); ax[0].plot(tt,4+np.floor((tt-2)/4),'k:',label="repo fit 4+floor((t-2)/4)")
ax[0].set_xlabel("t"); ax[0].set_ylabel("msolve F4 max degree (m=2)"); ax[0].legend(fontsize=7)
d=tab(2,True); ts=sorted(d)
mr={}
for r in rows:
    if r['q']==2 and r['planted'] and isinstance(r.get('maxrows'),int): mr[r['t']]=r['maxrows']
ax[1].semilogy(sorted(mr),[mr[t] for t in sorted(mr)],'o-'); ax[1].set_xlabel("t"); ax[1].set_ylabel("max F4 matrix rows (q=2, planted)")
fig.tight_layout(); fig.savefig("fig_f4_degree.png",dpi=150)
json.dump(res,open("out/f4_summary.json","w"),indent=1); print(json.dumps(res,indent=1)); print(mr)
