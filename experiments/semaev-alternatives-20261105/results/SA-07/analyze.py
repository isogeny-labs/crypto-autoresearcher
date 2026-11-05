import json, glob, math, random, collections
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
rows=[json.loads(l) for f in ['raw_m2.jsonl','raw_m3.jsonl'] for l in open(f)]
def cls(r):
    if r['status']=='timelimit': return 'timeout'
    if r['verified'] is True: return 'ok'
    if str(r['status']).startswith('error'): return 'error'
    return 'false'   # infeasible / optimal-but-spurious / other
def slope(pts, key):
    xs=np.log2([b for b,_ in pts]); ys=np.log2([max(v,1e-3) for _,v in pts])
    if len(set(xs))<2: return None
    return np.polyfit(xs,ys,1)[0]
def boot(pts,key,n=2000,rng=random.Random(0)):
    s=slope(pts,key)
    if s is None: return None
    # resample points within each B
    byB=collections.defaultdict(list)
    for b,v in pts: byB[b].append(v)
    out=[]
    for _ in range(n):
        q=[(b,rng.choice(vs)) for b,vs in byB.items() for _ in vs]
        sl=slope(q,key)
        if sl is not None: out.append(sl)
    out.sort()
    return s,out[int(.025*len(out))],out[int(.975*len(out))],len(byB)
tab=[]; summ=[]
groups=collections.defaultdict(list)
for r in rows: groups[(r['m'],r['form'],r['bits'])].append(r)
lines=["| m | form | bits | B | n | ok | false | timeout | median nodes (ok) | median CPU s (ok) |","|--|--|--|--|--|--|--|--|--|--|"]
for k in sorted(groups):
    byB=collections.defaultdict(list)
    for r in groups[k]: byB[r['B']].append(r)
    for B in sorted(byB):
        rs=byB[B]; c=collections.Counter(cls(r) for r in rs)
        ok=[r for r in rs if cls(r)=='ok']
        mn=np.median([r['nodes'] for r in ok]) if ok else float('nan')
        mt=np.median([r['time'] for r in ok]) if ok else float('nan')
        lines.append(f"| {k[0]} | {k[1]} | {k[2]} | {B} | {len(rs)} | {c['ok']} | {c['false']} | {c['timeout']} | {mn:.0f} | {mt:.2f} |")
open('results_table.md','w').write('\n'.join(lines)+'\n')
# exponent fits: pooled over bits per (m,form); successes only, plus censored-as-limit variant
fits=["| m | form | metric | variant | slope | 95% CI | #B levels | #points |","|--|--|--|--|--|--|--|--|"]
fig,axs=plt.subplots(2,3,figsize=(13,7))
for ci,m in enumerate([2,3]):
  for fj,form in enumerate(['raw','lll','vieta']):
    rs=[r for r in rows if r['m']==m and r['form']==form]
    for metric in ['nodes','time']:
        for variant in ['successes only','timeouts+false counted at cap']:
            pts=[]
            for r in rs:
                c=cls(r)
                if c=='ok': pts.append((r['B'],r[metric]))
                elif variant!='successes only' and c=='timeout': pts.append((r['B'],r[metric] if metric=='time' else r['nodes']))
            b=boot(pts,metric) if len(pts)>=4 else None
            if b: fits.append(f"| {m} | {form} | {metric} | {variant} | {b[0]:.2f} | [{b[1]:.2f}, {b[2]:.2f}] | {b[3]} | {len(pts)} |")
            else: fits.append(f"| {m} | {form} | {metric} | {variant} | n/a | n/a | - | {len(pts)} |")
    ax=axs[ci][fj]
    for bits in sorted(set(r['bits'] for r in rs)):
        pp=[(r['B'],max(r['nodes'],1)) for r in rs if r['bits']==bits and cls(r)=='ok']
        if pp: ax.scatter(*zip(*pp),label=f'p~2^{bits} ok',s=14)
        pt=[(r['B'],max(r['nodes'],1)) for r in rs if r['bits']==bits and cls(r)=='timeout']
        if pt: ax.scatter(*zip(*pt),marker='x',label=f'2^{bits} timeout')
    ax.set_xscale('log',base=2);ax.set_yscale('log');ax.set_title(f'm={m} {form}');ax.set_xlabel('B');ax.set_ylabel('SCIP nodes')
    ax.legend(fontsize=6)
plt.tight_layout();plt.savefig('fig_nodes.png',dpi=110)
open('fits_table.md','w').write('\n'.join(fits)+'\n')
print(open('results_table.md').read());print('\n'.join(fits))
