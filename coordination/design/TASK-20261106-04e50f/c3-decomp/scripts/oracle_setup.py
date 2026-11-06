#!/usr/bin/env python3 -I
"""oracle_setup breakdown (incumbent) + formula-only alternatives. usage: oracle_setup.py records.jsonl outdir"""
import json,sys,math
import numpy as np
rec,out=sys.argv[1],sys.argv[2]
rs=[json.loads(l) for l in open(rec)]
inc=[r for r in rs if r['arm']=='incumbent' and not r['warmup']]
rng=np.random.default_rng(20261106); B=10000
def key(r): return (r['workload']['curve_spec']['seed'],r['workload']['target_index'])
ks=sorted({key(r) for r in inc})
def get(r,f): 
    p=[p for p in r['phases'] if p['name']=='oracle_setup'][0]; return f(p)
fields={'adds':lambda p:p['adds'],'doubles':lambda p:p['doubles'],'scalar_mults':lambda p:p['scalar_mults'],'gae':lambda p:p['gae'],
 'lookups(x_index reads)':lambda p:p['work_native']['lookups'],'table_insert_attempts':lambda p:p['work_native']['table_insert_attempts'],
 'index_point_negations(oracle_setup phase)':lambda p:p['work_native'].get('index_point_negations',0),'wall_ns':lambda p:p['wall_ns']}
res={'section':'oracle_setup breakdown, incumbent walk, 128 measured records, 16 targets','fields':{}}
idx=rng.integers(0,len(ks),(B,len(ks)))
for n,f in fields.items():
    v=np.array([np.mean([get(r,f) for r in inc if key(r)==k]) for k in ks],float)
    allv=[get(r,f) for r in inc]
    res['fields'][n]={'mean':float(v.mean()),'ci95':[float(np.percentile(v[idx].mean(1),2.5)),float(np.percentile(v[idx].mean(1),97.5))],'min':min(allv),'max':max(allv)}
fb=[ [p for p in r['phases'] if p['name']=='factor_base'][0] for r in inc][0]
res['factor_base_phase_counters_for_reference']=fb['work_native']|{'adds':fb['adds'],'doubles':fb['doubles'],'scalar_mults':fb['scalar_mults']}
res['table_entries']='NOT in records (no field carries PairTable.entries); only insert attempts (inserts tried, identity sums excluded)'
N=407
res['identities_skipped']=N*(N+1)-res['fields']['table_insert_attempts']['mean']
res['N_times_Nplus1']=N*(N+1)
# formula-only alternatives (MODELED). Premise note: oracle_setup performs 0 scalar mults.
L=28
def da(L): return (L-1,(L)/2)           # textbook: L-1 doublings, avg L/2 adds (L=28 bit scalar, top bit set)
d,a=da(L); tb=d+a
tab=[]
tab.append({'method':'textbook double-and-add (one fixed base)','precompute':0,'per_mult':tb,'N_mults':N*tb,'total_per_run':N*tb})
for w in range(4,9):
    h=math.ceil(L/w)
    pre=(2**w-1-w)+(w-1)*h   # Lim-Lee comb, single table: 2^w-1 entries, ~2^w-1-w adds + (w-1)*h doublings to get the w base multiples
    per=(h-1)+h*(1-2**-w)    # h-1 doublings, h table adds (digit zero skips)
    tab.append({'method':f'fixed-base comb w={w} (h={h})','precompute':pre,'per_mult':per,'N_mults':N*per,'total_per_run':pre+N*per})
for w in range(4,9):
    h=math.ceil(L/w)
    pre=h*(2**w-2)+ (w*(h-1))    # table of j*2^(w i) P, digits 1..2^w-1 per position: ~ (2^w-2) adds per pos + w(h-1) doublings
    per=h*(1-2**-w)-1+ (2**-w)     # h-1 adds minus zero-digit skips (approx)
    per=max(0,h*(1-2**-w)-1)
    tab.append({'method':f'fixed-base windowed, no doublings, w={w} (h={h} tables)','precompute':pre,'per_mult':per,'N_mults':N*per,'total_per_run':pre+N*per})
joint=(L-1)+0.75*L
tab.append({'method':'Shamir joint aP+bQ (a,b both 28-bit), P+Q precomputed','precompute':1,'per_mult':joint,'N_mults':N*joint,'total_per_run':1+N*joint})
res['modeled_alternatives']={'assumptions':'MODELED, formulas only, not measured. L=28-bit scalar, 1 GAE per add or double. Hypothetical: N=407 independent scalar mults of ONE fixed base (or N joint aP+bQ). The measured oracle_setup has 0 scalar mults and is N(N+1)=166,056 additions of factor-base points, so these rows are not alternatives to what it builds; they are the cost the stated premise would have.','measured_oracle_setup_gae':res['fields']['gae']['mean'],'rows':tab}
res['textbook_cost_per_mult_L28']={'doublings':d,'avg_adds':a,'total':tb}
res['implied_per_scalar_mult_cost_from_counters']='undefined: scalar_mults=0 in oracle_setup; 166,056 adds / 407 = 408 adds per base point (N+1) is the only ratio'
json.dump(res,open(out+'/oracle_setup.json','w'),indent=1)
for k,v in res['fields'].items(): print(k,v)
for t in tab: print(t['method'],round(t['precompute'],1),round(t['per_mult'],2),round(t['total_per_run'],1))
