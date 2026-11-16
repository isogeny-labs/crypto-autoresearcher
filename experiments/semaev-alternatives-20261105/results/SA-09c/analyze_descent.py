import json,glob,math
import numpy as np
from scipy import stats
def garwood(k,alpha=0.05):
    lo=0 if k==0 else stats.chi2.ppf(alpha/2,2*k)/2; hi=stats.chi2.ppf(1-alpha/2,2*k+2)/2; return lo,hi
out={}
for tag,pat in (('primary','descent30_1*.json'),('replication','descent30rep_*.json')):
    R=[json.load(open(f))[0] for f in sorted(glob.glob(pat))]
    n=sum(r['ntargets'] for r in R); h=sum(r['heegner_hits'] for r in R)
    cmean=sum(r['control_hits_mean'] for r in R)
    lam0=sum(r['heegner_exact_rate']*r['ntargets'] for r in R)          # expected hits from exact |U_H|/#E
    lamc=sum(r['control_exact_rate']*r['ntargets'] for r in R)
    lo,hi=garwood(h); pone=stats.poisson.sf(h-1,lam0); ptwo=min(1,2*min(pone,stats.poisson.cdf(h,lam0)))
    d=h-cmean; sd=math.sqrt(h+cmean)
    # control-set distribution of the pooled hit count (sum over primes of per-set counts is not paired across primes; use independent resampling)
    rng=np.random.default_rng(3); 
    pooled=sum(rng.choice(np.array(r['control_hits']),200000) for r in R)
    out[tag]={'primes':[r['p'] for r in R],'n_targets':n,'heegner_hits_per_prime':[r['heegner_hits'] for r in R],'heegner_hits':h,'heegner_rate':h/n,
      'control_hits_mean_per_prime':[r['control_hits_mean'] for r in R],'control_hits_mean':cmean,'control_rate':cmean/n,
      'expected_hits_from_exact_Heegner_U':lam0,'expected_hits_from_exact_control_U':lamc,
      'heegner_U':[r['heegner_U'] for r in R],'control_U_mean':[r['control_U_mean'] for r in R],'#E':[r['#E'] for r in R],
      'garwood95_heegner_hits':[lo,hi],'garwood95_rate':[lo/n,hi/n],
      'diff_hits':d,'diff_rate':d/n,'diff95_normal_hits':[d-1.96*sd,d+1.96*sd],'diff95_rate':[(d-1.96*sd)/n,(d+1.96*sd)/n],
      'poisson_p_one_sided_vs_exact_expectation':float(pone),'poisson_p_two_sided':float(ptwo),
      'frac_pooled_control_sets_ge_heegner':float((pooled>=h).mean()),'n_control_sets_per_prime':[len(r['control_hits']) for r in R]}
    print(tag,json.dumps(out[tag],indent=0)[:2500])
# exact-rate comparison (zero target noise)
ex=[]
for f in sorted(glob.glob('descent30_1*.json')):
    r=json.load(open(f))[0]
    sd=r['control_U_sd']; ex.append({'p':r['p'],'U_heegner':r['heegner_U'],'U_control_mean':r['control_U_mean'],'U_control_sd':sd,'frac_controls_U_ge':r['frac_controls_U_ge'],'ratio':r['heegner_U']/r['control_U_mean']})
out['exact_rate']=ex
# combined
h=out['primary']['heegner_hits']+out['replication']['heegner_hits']; lam=out['primary']['expected_hits_from_exact_Heegner_U']+out['replication']['expected_hits_from_exact_Heegner_U']
n=out['primary']['n_targets']+out['replication']['n_targets']
out['combined']={'n':n,'hits':h,'expected':lam,'p_one_sided':float(stats.poisson.sf(h-1,lam)),'garwood_rate':[x/n for x in garwood(h)]}
print(json.dumps(out['combined']),json.dumps(ex))
json.dump(out,open('descent30_summary.json','w'),indent=1)
