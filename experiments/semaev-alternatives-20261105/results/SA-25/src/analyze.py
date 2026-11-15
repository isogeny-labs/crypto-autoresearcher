import json, math, numpy as np, glob, os
B='/home/user/semaev-runs/SA-25/'
rng=np.random.default_rng(25)
base=[o['p'] for o in json.load(open(B+'work/primes.json')) if 'p' in o]
ext=[o['p'] for o in json.load(open(B+'work/primes2.json'))['extras'] if 'p' in o]
supp=[o['p'] for o in json.load(open(B+'work/primes2.json'))['supp_largen']]
summ={}
for l in open(B+'results/prime_summary.jsonl'):
    r=json.loads(l)
    if not r.get('nofilter') and r.get('n_ok'): summ[r['p']]=r
def cls(p): return [json.loads(l) for l in open(B+f'results/classes_p{p}.jsonl')]
def ols(x,y):
    A=np.vstack([x,np.ones_like(x)]).T; b=np.linalg.lstsq(A,y,rcond=None)[0]; return b
def boot_fit(x,y,B_=2000):
    x=np.array(x);y=np.array(y);n=len(x); sl=[]
    for _ in range(B_):
        i=rng.integers(0,n,n)
        if len(set(x[i]))<2: continue
        sl.append(ols(x[i],y[i])[0])
    b=ols(x,y); return b[0],b[1],np.percentile(sl,2.5),np.percentile(sl,97.5),n
out={}
plist=sorted(set(p for p in base+ext+supp if p in summ))
rows=[]
for p in plist:
    r=summ[p]; cs=cls(p)
    big=[c for c in cs if c['size']>=50]
    rows.append(dict(p=p,n=r['n'],npts=r['npts'],amb=r['n_ambiguous_key'],spec=r['n_special_j'],ncls=len(cs),
        min_ratio_all=min(c['corank']/c['size'] for c in cs), min_ratio_ge50=min(c['corank']/c['size'] for c in big) if big else None,
        n_c_le10=sum(1 for c in cs if c['corank']<=10), n_c_le10_ge50=sum(1 for c in big if c['corank']<=10),
        min_c_ge50=min(c['corank'] for c in big) if big else None,
        min_cost_all=r['min_cost_all'],min_cost_usable=r['min_cost_usable'],min_cost_ge50=r['min_cost_ge50'],rho=r['rho_pred'],
        al_only_median_ratio=float(np.median([c['corank']/c['size'] for c in big if c['nH_rows_total']==0])) if any(c['nH_rows_total']==0 for c in big) else None))
out['rows']=rows
# fits
def fit(key,xkey,sel=lambda r:True,label=''):
    R=[r for r in rows if sel(r) and r[key]]
    x=[math.log2(r[xkey]) for r in R]; y=[math.log2(r[key]) for r in R]
    s,i,lo,hi,n=boot_fit(x,y); return dict(label=label,key=key,xkey=xkey,slope=s,intercept=i,ci_lo=lo,ci_hi=hi,n=n)
fits=[]
for key in ('min_cost_all','min_cost_usable','min_cost_ge50'):
    for xk in ('n','p'):
        fits.append(fit(key,xk,label='all primes'))
        fits.append(fit(key,xk,sel=lambda r:r['p']>=1e4,label='p>=1e4'))
fits.append(fit('rho','n',label='rho formula'))
out['fits']=fits
# covariates pooled over primes (classes size>=50)
allc=[]
for p in plist:
    for c in cls(p):
        c['ratio']=c['corank']/c['size']; allc.append(c)
big=[c for c in allc if c['size']>=50]
def bins(sub):
    d={}
    for c in sub:
        k=round(c['sigma_f'],3) if False else ('f=1' if c['f']==1 else ('sigma<0.5' if c['sigma_f']<0.5 else ('0.5-0.8' if c['sigma_f']<0.8 else '>=0.8')))
        d.setdefault(k,[]).append(c['ratio'])
    return {k:dict(n=len(v),mean=float(np.mean(v)),min=float(np.min(v)),max=float(np.max(v))) for k,v in d.items()}
out['bins_ge50']=bins(big)
# spearman sigma vs ratio with bootstrap
from math import sqrt
def spearman(a,b):
    ra=np.argsort(np.argsort(a)).astype(float); rb=np.argsort(np.argsort(b)).astype(float); return float(np.corrcoef(ra,rb)[0,1])
sg=np.array([c['sigma_f'] for c in big]); rt=np.array([c['ratio'] for c in big])
bs=[]
for _ in range(2000):
    i=rng.integers(0,len(big),len(big)); bs.append(spearman(sg[i],rt[i]))
out['spearman_sigma_ratio']=dict(rho=spearman(sg,rt),lo=float(np.percentile(bs,2.5)),hi=float(np.percentile(bs,97.5)),n=len(big))
# per-orbits
out['global_min_ratio_ge50']=float(rt.min()); out['n_classes_total']=len(allc); out['n_classes_ge50']=len(big)
out['pairs_c_le10_primes']=[r['p'] for r in rows if r['n_c_le10']>0]
out['pairs_c_le10_ge50_primes']=[r['p'] for r in rows if r['n_c_le10_ge50']>0]
json.dump(out,open(B+'work/analysis.json','w'),indent=1,default=float)
if __name__=='__main__':
    print('%9s %7s %8s %5s %4s %5s %7s %7s %5s %5s %12s %12s %9s'%('p','n','npts','amb','ncl','c<=10','minr_all','minr50','minc50','c10_50','mincost_all','mincost_ge50','rho'))
    for r in rows: print('%9d %7d %8d %5d %4d %5d %7.3f %7s %5s %5d %12.0f %12s %9.1f'%(r['p'],r['n'],r['npts'],r['amb'],r['ncls'],r['n_c_le10'],r['min_ratio_all'],'%.3f'%r['min_ratio_ge50'] if r['min_ratio_ge50'] is not None else '-',r['min_c_ge50'],r['n_c_le10_ge50'],r['min_cost_all'],'%.0f'%r['min_cost_ge50'] if r['min_cost_ge50'] else '-',r['rho']))
    for f in fits: print(f)
    print(out['bins_ge50']); print(out['spearman_sigma_ratio']); print(out['global_min_ratio_ge50'],out['n_classes_total'],out['n_classes_ge50'])
