#!/usr/bin/env python3 -I
"""C3 per-phase decomposition of counted cost (w=0 GAE) from ecbench records.
usage: decomp.py records.jsonl outdir"""
import json,sys,hashlib,collections
import numpy as np
rec,out=sys.argv[1],sys.argv[2]
sha=hashlib.sha256(open(rec,'rb').read()).hexdigest()
rs=[json.loads(l) for l in open(rec)]
rs=[r for r in rs if not r['warmup']]
rng=np.random.default_rng(20261106)
B=10000
def key(r): return (r['workload']['curve_spec']['seed'],r['workload']['target_index'])
def pernum(r):
    """dict of named quantities in GAE for one record"""
    ph={p['name']:p for p in r['phases']}
    d={p['name']:p['gae'] for p in r['phases']}
    d['_total']=r['cost']['total_gae']
    d['_S']=r['cost']['s']
    if r['arm'] in('incumbent','candidate'):
        n=ph['relations']['native']; rel=ph['relations']
        ops=rel['adds']+rel['doubles']
        d['rel:walk_steps(additions)']=n['walk_steps']
        d['rel:restart_additions']=n['walk_pool_restarts']
        d['rel:restart_offset_draws(walk_pool_ops)']=n['walk_pool_ops']
        d['rel:jump_table+initial_point(derived)']=ops-n['walk_steps']-n['walk_pool_restarts']-n['walk_pool_ops']
        d['rel:_sum_check']=ops
    return d
groups=collections.defaultdict(lambda:collections.defaultdict(list))
for r in rs: groups[r['arm']][key(r)].append(pernum(r))
res={'records_sha256':sha,'bootstrap':{'B':B,'unit':'target (curve seed, target index); rounds averaged within target','seed':20261106,'stat':'ratio of means: sum_phase/sum_total across resampled targets'},'arms':{}}
for arm,g in groups.items():
    keys=sorted(g); T=len(keys)
    names=sorted({k for t in g.values() for d in t for k in d})
    M={k:np.array([np.mean([d.get(k,0.0) for d in g[t]]) for t in keys]) for k in names}
    tot=M['_total']; Sv=M['_S']
    phases=[k for k in names if not k.startswith('_') and not k.startswith('rel:')]
    subs=[k for k in names if k.startswith('rel:') and k!='rel:_sum_check']
    idx=rng.integers(0,T,(B,T))
    def ci(x):  # x: per-target values num; share vs total
        s=[]; 
        return None
    def stat(k,denom=tot):
        pt=M[k].sum()/denom.sum()
        bs=M[k][idx].sum(1)/denom[idx].sum(1)
        return {'share':pt,'ci95':[float(np.percentile(bs,2.5)),float(np.percentile(bs,97.5))]}
    def stat_S(k):
        # phase S = S * phase_gae/total_gae, per target
        v=Sv*M[k]/tot
        bs=v[idx].mean(1)
        return {'mean_S':float(v.mean()),'ci95':[float(np.percentile(bs,2.5)),float(np.percentile(bs,97.5))]}
    a={'n_records':sum(len(v) for v in g.values()),'n_targets':T,
       'mean_total_gae':float(tot.mean()),'mean_S':float(Sv.mean()),
       'S_ci95':[float(np.percentile(Sv[idx].mean(1),2.5)),float(np.percentile(Sv[idx].mean(1),97.5))],
       'phases':{},'relations_subdecomposition':{}}
    for k in phases:
        a['phases'][k]={'mean_gae':float(M[k].mean()),**stat(k),**{'S_'+x:y for x,y in stat_S(k).items()}}
    resid=tot-sum(M[k] for k in phases)
    bs=resid[idx].sum(1)/tot[idx].sum(1)
    a['residual_total_minus_sum_phases']={'mean_gae':float(resid.mean()),'share':float(resid.sum()/tot.sum()),'ci95':[float(np.percentile(bs,2.5)),float(np.percentile(bs,97.5))]}
    if subs:
        for k in subs:
            a['relations_subdecomposition'][k]={'mean_gae':float(M[k].mean()),**stat(k)}
        rr=M['relations']-sum(M[k] for k in subs)
        a['relations_subdecomposition']['(relations - sum of sub-items)']={'mean_gae':float(rr.mean()),'share':float(rr.sum()/tot.sum())}
    res['arms'][arm]=a
# native counters (unpriced at w=0), mean per record
nat=collections.defaultdict(lambda:collections.defaultdict(list))
for r in rs:
    for p in r['phases']:
        for k,v in (p.get('native') or {}).items(): nat[r['arm']][p['name']+'.'+k].append(v)
    for k,v in (r.get('counters') or {}).items(): nat[r['arm']]['counters.'+k].append(v)
res['mean_native_and_counters_per_record']={a:{k:float(np.mean(v)) for k,v in d.items()} for a,d in nat.items()}
# RANKING.md section-2 style check: S - oracle_setup_S - trials_S (trials as 1 GAE each), incumbent
inc=[r for r in rs if r['arm']=='incumbent']
ks=sorted({key(r) for r in inc}); 
def per(f): return np.array([np.mean([f(r) for r in inc if key(r)==k]) for k in ks])
Sr=per(lambda r:r['cost']['s']); tg=per(lambda r:r['cost']['total_gae'])
su=per(lambda r:[p for p in r['phases'] if p['name']=='oracle_setup'][0]['gae'])
tr=per(lambda r:r['counters']['targets_tried'])
sq=tg/Sr
rem=(tg-su-tr)/sq
idx=rng.integers(0,len(ks),(B,len(ks)))
res['ranking_style_check_incumbent']={'definition':'S - setup_S - trials_S where trials_S = targets_tried GAE / sqrt(r); per-target sqrt(r)=total_gae/S','mean_remainder_S':float(rem.mean()),'ci95':[float(np.percentile(rem[idx].mean(1),2.5)),float(np.percentile(rem[idx].mean(1),97.5))],'mean_setup_S':float((su/sq).mean()),'mean_trials_S':float((tr/sq).mean()),'mean_S':float(Sr.mean())}
res['per_curve_incumbent']={}
for cs in sorted({k[0] for k in ks}):
    m=[i for i,k in enumerate(ks) if k[0]==cs]
    r0=[r for r in inc if r['workload']['curve_spec']['seed']==cs][0]['workload']['curve']
    res['per_curve_incumbent'][str(cs)]={'r':r0['r'],'field_bits':r0['field_bits'],'mean_S':float(Sr[m].mean()),'setup_gae':float(su[m].mean()),'mean_total_gae':float(tg[m].mean()),'mean_trials':float(tr[m].mean()),'remainder_S':float(rem[m].mean())}
json.dump(res,open(out+'/decomp.json','w'),indent=1)
# chart
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,axs=plt.subplots(1,2,figsize=(12,4.5))
for ax,arm in zip(axs,['incumbent','rho-neg']):
    a=res['arms'][arm]; ks_=list(a['phases']); 
    v=[a['phases'][k]['share']*100 for k in ks_]
    lo=[a['phases'][k]['share']*100-a['phases'][k]['ci95'][0]*100 for k in ks_]
    hi=[a['phases'][k]['ci95'][1]*100-a['phases'][k]['share']*100 for k in ks_]
    ks_.append('residual'); v.append(a['residual_total_minus_sum_phases']['share']*100); lo.append(0); hi.append(0)
    ax.bar(ks_,v,yerr=[lo,hi],capsize=3); ax.set_title(f"{arm}: share of counted cost (w=0), 95% CI over targets")
    ax.set_ylabel('% of S'); ax.tick_params(axis='x',rotation=30)
plt.tight_layout(); plt.savefig(out+'/phase_shares.svg'); plt.savefig(out+'/phase_shares.png',dpi=130)
print(sha); print(json.dumps({a:{'S':res['arms'][a]['mean_S'],'phases':{k:(round(v['share'],5),[round(x,5) for x in v['ci95']]) for k,v in res['arms'][a]['phases'].items()},'resid':res['arms'][a]['residual_total_minus_sum_phases']} for a in res['arms']},indent=1))
print(json.dumps(res['arms']['incumbent']['relations_subdecomposition'],indent=1))
print(json.dumps(res['ranking_style_check_incumbent'],indent=1)); print(json.dumps(res['per_curve_incumbent'],indent=1))
