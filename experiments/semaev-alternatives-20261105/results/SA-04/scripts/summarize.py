import json, glob, collections, numpy as np, os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
O='../out/'
def load(f):
    return [json.loads(l) for l in open(O+f)] if os.path.exists(O+f) else []
def table(rows):
    d=collections.defaultdict(list)
    for r in rows: d[r['B']].append(r)
    out={}
    for B,rs in sorted(d.items()):
        ds=[r['Dsol'] for r in rs]
        out[B]=dict(Dsol=ds,K=[r['K'] for r in rs],aborted=[r['aborted'] for r in rs],nvars=rs[0]['nvars'],maxcols=max(r['maxcols'] for r in rs))
    return out
sets={'m2 norm digit':'m2_digit_real2.jsonl','m2 norm digit (null N1)':'m2_digit_null.jsonl','m2 S3 digit':'m2_S_real.jsonl',
      'm2 norm V':'m2_V_real.jsonl','m2 S3 V':'m2_SV_real.jsonl',
      'm3 norm digit':'m3_digit_real.jsonl','m3 norm digit (null N1)':'m3_digit_null.jsonl','m3 S4 digit':'m3_S_real.jsonl',
      'm3 norm V':'m3_V_real.jsonl','m3 S4 V':'m3_SV_real.jsonl'}
res={}
lines=[]
for name,f in sets.items():
    t=table(load(f)); res[name]=t
    lines.append("### "+name)
    lines.append("| B | nvars | D_sol (per seed) | K | note |"); lines.append("|---|---|---|---|---|")
    for B,v in t.items():
        lines.append(f"| {B} | {v['nvars']} | {v['Dsol']} | {v['K']} | {[a for a in v['aborted'] if a] or ''} |")
open(O+'dsol_tables.md','w').write("\n".join(lines))
json.dump(res,open(O+'dsol_tables.json','w'),indent=1)
fig,ax=plt.subplots(1,2,figsize=(11,4))
for name,t in res.items():
    if not t: continue
    Bs=[B for B,v in t.items() if all(d is not None for d in v['Dsol'])]
    if not Bs: continue
    y=[np.mean(t[B]['Dsol']) for B in Bs]
    a=ax[0] if name.startswith('m2') else ax[1]
    a.plot(Bs,y,'o-' if 'norm' in name else 's--',label=name)
for a,tt in zip(ax,('m = 2','m = 3')):
    a.set_xscale('log',base=2); a.set_xlabel('B'); a.set_ylabel('Macaulay solving degree D_sol'); a.set_title(tt); a.legend(fontsize=7); a.grid(alpha=.3)
plt.tight_layout(); plt.savefig(O+'fig_dsol.png',dpi=130)
print("\n".join(lines))
