import json, glob, ast, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
rows=[]
for f in sorted(glob.glob('M_*.json')): rows+=json.load(open(f))
# add exact LP rows for boxes (i,v,vi) from ceil/ceilL files
box=[]
for f in sorted(glob.glob('ceil_*_m2.json'))+sorted(glob.glob('ceilL_i_m2.json')):
    for r in json.load(open(f)):
        if r['pres'] in ('i','iv','v','vi'): box.append(r)
def extrap(ts,v):
    ts=np.array(ts,float); v=np.array(v,float)
    if len(ts)<3: return None
    g=lambda t,d,a,b:d-a/t-b/t**2
    try:
        p,_=curve_fit(g,ts,v,maxfev=10000); return p[0]
    except Exception: return None
fig,ax=plt.subplots(figsize=(7,4.5))
for pres,lab,c in (('i','(i) x-coords','k'),('ii','(ii) Vieta MILP','C0'),('iii','(iii) norm','C1'),('iv','(iv) chain','C2')):
    pts=sorted([(r['t'],r.get('milp_lower',r.get('reach'))) for r in rows+box if r['pres']==pres and r['m']==2])
    if pts: ax.plot(*zip(*pts),'o-',color=c,label=lab)
ax.axhline(1/6,ls='--',color='gray'); ax.text(1,1/6+0.003,'1/6',color='gray')
ax.set_xlabel('shift level t'); ax.set_ylabel('certified delta (finite t)'); ax.set_title('m = 2: finite-t certified reach per presentation'); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig('ceilings_m2.png',dpi=130)
json.dump(dict(rows=rows,box=box),open('all_ceiling_rows.json','w'),indent=1)
print(len(rows),len(box))
