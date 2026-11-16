import json, glob, math, os
import numpy as np
SEED=24; NB=2000
def rd():
    F=[];Bn={}
    for f in sorted(glob.glob('results/p2_[0-9]*_*.jsonl')):
        L=[json.loads(l) for l in open(f)]
        if not any('done' in x for x in L): continue
        k,idx=[int(t) for t in os.path.basename(f)[3:-6].split('_')]
        for x in L:
            if x.get('kind')=='full': F.append(x)
            elif x.get('kind')=='bench': Bn.setdefault((k,idx),[]).append(x)
    return F,Bn
def main():
    F,Bn=rd(); rr={}
    for key,L in Bn.items():
        ns={q:np.mean([b['ns'][q] for b in L]) for q in L[0]['ns']}; rr[key]={q:ns[q]/ns['e1add'] for q in ns}
    def cost(a,dense=False):
        r=rr[(a['k'],a['idx'])]; c=a['cnt']; la=c['la']
        if dense: N=a['F']/2.0; la=N**3/3.0
        return c['e1add']+c['jadd']*r['jadd']+c['leg']*r['leg']+c['sqr']*r['sqr']+c['inv']*r['inv']+c['mul']*r['mulp']+la*r['la']
    runs=[a for a in F if not a.get('skipped')]; skipped=[a for a in F if a.get('skipped')]
    for a in runs: a['ok']=bool(a['solved'] and a['k_ok'] and not a['capped'])
    ks=sorted(set(a['k'] for a in F)); out=dict(sizes=ks,n_runs=len(runs),n_skipped=len(skipped),n_capped=sum(1 for a in runs if a['capped']),n_unsolved=sum(1 for a in runs if not a['ok'] and not a['capped']),rel_fail_total=sum(a['rel_fail'] for a in runs),
        skipped=[dict(k=a['k'],idx=a['idx'],t=a['t'],delta=a['delta'],expected_trials=a['expected_trials']) for a in skipped][:0])
    sk={}
    for a in skipped: sk.setdefault((a['k'],a['delta']),[]).append(a['expected_trials'])
    out['skipped_cells']=[dict(k=k,delta=d,n=len(v),expected_trials=float(np.mean(v))) for (k,d),v in sorted(sk.items())]
    tab={}  # (k,delta)-> list of ok runs
    insts={k:sorted(set((a['idx'],a['t']) for a in F if a['k']==k)) for k in ks}
    for a in runs:
        if a['ok']: tab.setdefault((a['k'],a['delta']),{})[(a['idx'],a['t'])]=a
    allruns={}
    for a in runs: allruns.setdefault((a['k'],a['delta']),[]).append(a)
    valid={key:v for key,v in tab.items() if len(v)==len(insts[key[0]])}
    cells=[]; rng=np.random.default_rng(SEED)
    for (k,d),v in sorted(valid.items()):
        L=list(v.values()); rel=np.array([a['rel'] for a in L],float); ex=np.array([a['trials']*a['null'] for a in L]); 
        bs=[]; 
        for _ in range(NB):
            i=rng.integers(0,len(L),len(L)); bs.append(rel[i].sum()/ex[i].sum())
        cells.append(dict(k=k,p=L[0]['p'],delta=d,n=len(L),B=int(np.mean([a['B'] for a in L])),F=int(np.mean([a['F'] for a in L])),rel=int(rel.sum()),expected_rel=float(ex.sum()),rate_over_null=float(rel.sum()/ex.sum()),ci=[float(np.percentile(bs,2.5)),float(np.percentile(bs,97.5))],
            geomean_cost=float(np.exp(np.mean([math.log(cost(a)) for a in L]))),geomean_cost_dense=float(np.exp(np.mean([math.log(cost(a,True)) for a in L]))),mean_trials=float(np.mean([a['trials'] for a in L])),mean_wall=float(np.mean([a['wall'] for a in L])),
            geomean_early=float(np.exp(np.mean([math.log(cost({**a,'cnt':a['early']['cnt']})) for a in L if 'early' in a]))) if all('early' in a for a in L) else None))
    out['cells']=cells
    ksv=sorted(set(c['k'] for c in cells)); out['sizes_with_data']=ksv
    def fitf(getcost,xkey,boot,rng,ksub,dense=False):
        xs=[];ys=[]
        for k in ksub:
            keys=insts[k]; sel=keys if not boot else [keys[i] for i in rng.integers(0,len(keys),len(keys))]
            dl=[d for (kk,d) in valid if kk==k]; best=None
            for d in dl:
                g=np.mean([math.log(getcost(valid[(k,d)][s])) for s in sel]); 
                if best is None or g<best[0]: best=(g,d)
            for s in sel:
                a=valid[(k,best[1])][s]; xs.append(math.log2(a['n1'] if xkey=='n1' else a['p'])); ys.append(math.log2(getcost(a)))
        return float(np.polyfit(xs,ys,1)[0])
    fits={}
    for nm,ksub in [('all',ksv),('k14_up',[k for k in ksv if k>=14]),('k10_20',[k for k in ksv if k<=20])]:
        if len(ksub)<3: continue
        for xk in ('p','n1'):
            for vn,gc in [('cost',lambda a:cost(a)),('cost_dense_LA',lambda a:cost(a,True)),('jadd_count',lambda a:a['cnt']['jadd']),('wall',lambda a:a['wall'])]:
                est=fitf(gc,xk,False,None,ksub); r2=np.random.default_rng(SEED); bs=[fitf(gc,xk,True,r2,ksub) for _ in range(NB)]
                fits[f'{vn}_vs_log2{xk}_{nm}']=dict(est=est,ci=[float(np.percentile(bs,2.5)),float(np.percentile(bs,97.5))],n_boot=NB,sizes=ksub,n_points=sum(len(insts[k]) for k in ksub))
    out['fits']=fits
    # optimum delta per size and comparison with SA-24 A1 (degenerate) and rho
    sa=json.load(open('/home/user/semaev-runs/SA-24/results/a1_analysis.json'))
    best={}
    for c in cells:
        if c['k'] not in best or c['geomean_cost']<best[c['k']]['geomean_cost']: best[c['k']]=c
    sab={}
    for t in sa['table']:
        if t['k'] not in sab or t['geomean_cost']<sab[t['k']]['geomean_cost']: sab[t['k']]=t
    rho={r['k']:r for r in sa['rho_table']}
    out['compare']=[dict(k=k,p=b['p'],opt_delta=b['delta'],full_cost=b['geomean_cost'],full_cost_dense=min(c['geomean_cost_dense'] for c in cells if c['k']==k),A1_degenerate_cost=sab[k]['geomean_cost'],rho_steps=rho[k]['geomean_steps'],full_trials_over_p=b['mean_trials']/b['p'],full_wall=b['mean_wall']) for k,b in sorted(best.items()) if k in sab]
    out['rho_global']={q:float(np.mean([r[q] for r in rr.values()])) for q in ('jadd','leg','sqr','inv','mulp','la')}
    json.dump(out,open('results/p2_analysis.json','w'),indent=1)
    print('runs',out['n_runs'],'skipped',out['n_skipped'],'capped',out['n_capped'],'unsolved',out['n_unsolved'],'relfail',out['rel_fail_total'])
    for c in cells: print(c['k'],c['delta'],c['n'],c['F'],round(c['rate_over_null'],3),[round(x,3) for x in c['ci']],f"{c['geomean_cost']:.3g}",f"{c['geomean_cost_dense']:.3g}",round(c['mean_trials']/c['p'],2))
    for k,v in fits.items(): print(k,round(v['est'],3),[round(x,3) for x in v['ci']],v['n_points'])
    for c in out['compare']: print(c['k'],c['opt_delta'],f"{c['full_cost']:.3g} A1deg {c['A1_degenerate_cost']:.3g} rho {c['rho_steps']:.0f}")
main()
