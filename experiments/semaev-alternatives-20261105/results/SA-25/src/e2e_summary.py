import json, numpy as np
B='/home/user/semaev-runs/SA-25/'
rng=np.random.default_rng(25)
rows=[]
RT=json.load(open(B+'results/rho_times.json'))
for l in open(B+'results/e2e.jsonl'):
    o=json.loads(l)
    rho=o['rho']
    # per-run rho times unavailable in summary -> mean only; bootstrap needs per-run: not stored for rho (stored? ) 
    for name,c in o['classes'].items():
        w=np.array([r['wall_sec'] for r in c['runs']]); tr=np.array([r['trials'] for r in c['runs']])
        rows.append((o['p'],o['n'],name,c['t'],c['size'],c['corank'],c['n_correct'],c['n_runs'],w,tr,c['setup_sec'],rho))
print('%9s %8s %8s %5s %6s %4s %7s %12s %12s %10s %22s %9s'%('p','n','class','|S|','c','','solved','trials_mean','ours_ms','rho_us','ratio(95%CI)','rho_adds'))
out=[]
for p,n,name,t,S,c,nc,nr,w,tr,setup,rho in rows:
    # rho per-run times: recompute? use mean + treat as fixed with relative CI from file if present
    rs=np.array(RT[str(p)]['secs']); rho=dict(rho); rho['mean_adds']=float(np.mean(RT[str(p)]['adds']))
    bs=[]
    for _ in range(2000):
        a=w[rng.integers(0,len(w),len(w))].mean(); b=rs[rng.integers(0,len(rs),len(rs))].mean(); bs.append(a/b)
    r=w.mean()/rs.mean(); lo,hi=np.percentile(bs,[2.5,97.5])
    out.append(dict(p=p,n=n,cls=name,t=t,size=S,corank=c,solved=f'{nc}/{nr}',mean_trials=float(tr.mean()),ours_ms=float(w.mean()*1e3),rho_us=float(rs.mean()*1e6),ratio=float(r),lo=float(lo),hi=float(hi),rho_adds=rho['mean_adds'],setup_ms=setup*1e3,rho_correct=f"{rho['n_correct']}/{rho['n_runs']}"))
    print('%9d %8d %8s %5d %6d %4d %7s %12.0f %12.2f %10.2f %9.0f [%.0f,%.0f] %9.1f'%(p,n,name,S,c,0,f'{nc}/{nr}',tr.mean(),w.mean()*1e3,rs.mean()*1e6,r,lo,hi,rho['mean_adds']))
json.dump(out,open(B+'work/e2e_summary.json','w'),indent=1)
