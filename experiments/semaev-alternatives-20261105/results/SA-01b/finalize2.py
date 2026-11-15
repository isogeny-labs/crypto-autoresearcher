import json, glob, numpy as np, csv
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
def L(f): return json.load(open(f))
series={}
def add(key,t,v): series.setdefault(key,{})[t]=v
for f in ['ceil_i_m2.json','ceilL_i_m2.json']:
    for r in L(f): add(('i',2),r['t'],r['reach'])          # box: LP = exact (checked, M_i_m3 lp==milp)
for r in L('M_i_m3.json')+L('M_i_m4.json'): add(('i',r['m']),r['t'],r['milp_lower'])
for r in L('M_ii_m2.json'): add(('ii',2),r['t'],r['milp_lower'])
add(('ii',2),3,0.1308)                                     # cert_t3_m2.log (MILP)
for r in L('M_iiiG_m2.json'): add(('iiiG',2),r['t'],r['milp_lower'])
for r in L('M_iii_m2.json')+L('M_iii_m3.json'): add(('iii',r['m']),r['t'],r['milp_lower'])
for r in L('ceil_iv_m2.json'): add(('iv',2),r['t'],r['reach'])
for r in L('M_iv_m3.json'): add(('iv',3),r['t'],r['milp_lower'])
for r in L('ceil_v_m2.json'): add(('v_naive',2),r['t'],r['reach'])
for r in L('ceil_vi_m2.json'): add(('vi',2),r['t'],r['reach'])
lpu={}
for f in ['M_ii_m2.json','M_iiiG_m2.json','M_iii_m2.json']:
    for r in L(f): lpu[(r['pres'],r['m'],r['t'])]=r['lp_upper']
def extrap(d):
    ts=np.array(sorted(t for t in d if t>=2),float); v=np.array([d[int(t)] for t in ts])
    if len(ts)<3 or v.max()<=0: return None
    g=lambda t,D,a,b:D-a/t-b/t**2
    p,_=curve_fit(g,ts,v,maxfev=20000)
    # leave-one-out spread
    loo=[]
    for k in range(len(ts)):
        if len(ts)-1<3: break
        m=np.ones(len(ts),bool); m[k]=False
        q,_=curve_fit(g,ts[m],v[m],maxfev=20000); loo.append(q[0])
    return p[0],(min(loo) if loo else None),(max(loo) if loo else None)
an={(r['pres'],r['m']):r['delta'] for r in L('analytic_reach.json')}
with open('ceilings_table.csv','w',newline='') as fh:
    w=csv.writer(fh); w.writerow(['pres','m','t','certified_delta_finite_t','lp_upper'])
    for (p,m),d in sorted(series.items()):
        for t in sorted(d): w.writerow([p,m,t,round(d[t],5),lpu.get((p,m,t),'')])
summ=[]
for (p,m),d in sorted(series.items()):
    e=extrap(d); summ.append(dict(pres=p,m=m,tmax=max(d),best_finite=round(max(d.values()),5),extrap=None if e is None else [round(x,4) if x is not None else None for x in e],analytic=an.get((p if p!='v_naive' else 'v_naive_product',m))))
for s in summ: print(s)
json.dump(summ,open('ceilings_summary.json','w'),indent=1)
fig,axs=plt.subplots(1,2,figsize=(11,4.3))
cols={'i':'k','ii':'C0','iiiG':'C1','iii':'C3','iv':'C2','v_naive':'C4','vi':'C5'}
labs={'i':'(i) S in x','ii':'(ii) Vieta','iiiG':'(iii) norm, Groebner gens','iii':'(iii) norm, raw gens','iv':'(iv) chained S3','v_naive':'(v) naive 2-torsion product','vi':'(vi) integer lift'}
for ax,m,ref in ((axs[0],2,1/6),(axs[1],3,1/24)):
    for (p,mm),d in sorted(series.items()):
        if mm!=m: continue
        ts=sorted(d); ax.plot(ts,[d[t] for t in ts],'o-',color=cols[p],label=labs[p],ms=4)
    ax.axhline(ref,ls='--',color='gray'); ax.text(1,ref*1.02,'single-poly asymptote %s'%('1/6' if m==2 else '1/24'),color='gray',fontsize=8)
    if m==3: ax.axhline(0.25,ls=':',color='r'); ax.text(1,0.235,'success line 1/4',color='r',fontsize=8); ax.set_yscale('symlog',linthresh=0.01)
    ax.set_xlabel('shift level t'); ax.set_ylabel('certified delta at finite t (exact MILP / box LP)'); ax.set_title('m = %d'%m); ax.legend(fontsize=7)
fig.tight_layout(); fig.savefig('ceilings_m2_m3.png',dpi=130)
