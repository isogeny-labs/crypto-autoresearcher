import json, glob, math, sys
import numpy as np
SEED=24; NB=2000
def rd():
    A=[];R=[];Bn={}
    for f in sorted(glob.glob('results/a1_*_*.jsonl')):
        L=[json.loads(l) for l in open(f)]
        if not any('done' in x for x in L): continue
        k=None
        for x in L:
            if x.get('kind')=='a1': A.append(x)
            elif x.get('kind')=='rho': R.append(x)
            elif x.get('kind')=='bench':
                # key by file
                Bn.setdefault(f,[]).append(x)
    return A,R,Bn
def rho_ratios(Bn):
    out={}
    for f,L in Bn.items():
        ns={k:np.mean([b['ns'][k] for b in L]) for k in L[0]['ns']}
        k,idx=[int(t) for t in f.split('/')[-1][3:-6].split('_')]
        out[(k,idx)]=dict(ns=ns,load=[b['load'] for b in L],r={q:ns[q]/ns['e1add'] for q in ns})
    return out
def cost(c,r,keys=None):
    return c['e1add']+c['jadd']*r['jadd']+c['leg']*r['leg']+c['sqr']*r['sqr']+c['inv']*r['inv']+c['mul']*r['mulp']+c['la']*r['la']
def slope(x,y): return float(np.polyfit(x,y,1)[0])
def main():
    A,R,Bn=rd(); rr=rho_ratios(Bn); ks=sorted(set(a['k'] for a in A))
    deltas=sorted(set(a['delta'] for a in A))
    out=dict(sizes=ks,deltas=deltas,rho_ratios={f"{k}_{i}":v for (k,i),v in rr.items()})
    # instances
    for a in A:
        r=rr[(a['k'],a['idx'])]['r']; a['cost']=cost(a['cnt'],r); a['cost_early']=cost(a['early']['cnt'],r) if 'early' in a else float('nan')
        a['ok']=bool(a['solved'] and a['k_ok'])
    nfail=sum(1 for a in A if not a['ok']); out['a1_failures']=nfail; out['a1_runs']=len(A); out['rel_fail_total']=sum(a['rel_fail'] for a in A)
    # table: geometric mean cost per (k,delta)
    inst={}  # (k) -> list of instance keys (idx,t)
    for k in ks: inst[k]=sorted(set((a['idx'],a['t']) for a in A if a['k']==k))
    cost_tab={}  # (k,delta)-> dict inst->(cost, wall, trials, early cost)
    fail_tab={}
    for a in A:
        if a['ok']: cost_tab.setdefault((a['k'],a['delta']),{})[(a['idx'],a['t'])]=a
        else: fail_tab.setdefault((a['k'],a['delta']),[]).append((a['idx'],a['t'],a['rel'],a['trials']))
    out['failures']=[dict(k=k,delta=d,n_fail=len(v),example=v[0]) for (k,d),v in sorted(fail_tab.items())]
    for key in list(cost_tab):
        if len(cost_tab[key])<len(inst[key[0]]): del cost_tab[key]   # delta used only where all instances solved
    tab=[]
    for k in ks:
        for d in deltas:
            if (k,d) not in cost_tab: continue
            L=list(cost_tab[(k,d)].values()); g=float(np.exp(np.mean([math.log(x['cost']) for x in L])))
            ge=float(np.exp(np.mean([math.log(x['cost_early']) for x in L if x['cost_early']==x['cost_early']]))) if any('early' in x for x in L) else None
            tab.append(dict(k=k,p=L[0]['p'],delta=d,n=len(L),geomean_cost=g,geomean_cost_early=ge,mean_trials=float(np.mean([x['trials'] for x in L])),mean_wall=float(np.mean([x['wall'] for x in L])),B=int(np.mean([x['B'] for x in L])),F=int(np.mean([x['F'] for x in L]))))
    out['table']=tab
    import numpy as _n
    global RHO_J,RHO_L,RHO_S,RHO_I,RHO_M,RHO_LA
    allr=[v['r'] for v in rr.values()]; RHO_J,RHO_L,RHO_S,RHO_I,RHO_M,RHO_LA=[float(_n.mean([r[q] for r in allr])) for q in ('jadd','leg','sqr','inv','mulp','la')]
    out['rho_global']=dict(jadd=RHO_J,leg=RHO_L,sqr=RHO_S,inv=RHO_I,mulp=RHO_M,la=RHO_LA)
    def fit_variant(getcost, deltasel, rng, boot, ksub):
        xs=[];ys=[]
        for k in ksub:
            keys=inst[k]; sel=keys if not boot else [keys[i] for i in rng.integers(0,len(keys),len(keys))]
            dl=[d for d in deltas if (k,d) in cost_tab]
            if deltasel=='opt':
                best=None
                for d in dl:
                    g=np.mean([math.log(getcost(cost_tab[(k,d)][s])) for s in sel if s in cost_tab[(k,d)]])
                    if best is None or g<best[0]: best=(g,d)
                dd=best[1]
            else: dd=min(dl,key=lambda z:abs(z-deltasel))
            for s in sel:
                a=cost_tab[(k,dd)][s]; xs.append(math.log2(a['n1'])); ys.append(math.log2(getcost(a)))
        return slope(xs,ys)
    def ci_of(getcost,deltasel,ksub):
        est=fit_variant(getcost,deltasel,None,False,ksub); rng=np.random.default_rng(SEED)
        bs=[fit_variant(getcost,deltasel,rng,True,ksub) for _ in range(NB)]
        return dict(est=est,ci=[float(np.percentile(bs,2.5)),float(np.percentile(bs,97.5))],n_boot=NB,n_points=sum(len(inst[k]) for k in ksub),sizes=ksub)
    fits={}
    for name,ksub in [('all',ks),('k10_20',[k for k in ks if k<=20]),('drop_k10',[k for k in ks if k>=12]),('drop_k10_k12',[k for k in ks if k>=14])]:
        if len(ksub)<2: continue
        fits[f'A1_opt_{name}']=ci_of(lambda a:a['cost'],'opt',ksub)
        for dsel in (0.5,0.7,0.9): fits[f'A1_delta{dsel}_{name}']=ci_of(lambda a:a['cost'],dsel,ksub)
        fits[f'A1_early_opt_{name}']=ci_of(lambda a:a['cost_early'],'opt',[k for k in ksub])
        fits[f'A1_wall_opt_{name}']=ci_of(lambda a:a['wall'],'opt',ksub)
        fits[f'A1_jadd_count_opt_{name}']=ci_of(lambda a:a['cnt']['jadd'],'opt',ksub)
        fits[f'A1_cost_fixedrho_opt_{name}']=ci_of(lambda a:a['cnt']['e1add']+a['cnt']['jadd']*RHO_J+a['cnt']['leg']*RHO_L+a['cnt']['sqr']*RHO_S+a['cnt']['inv']*RHO_I+a['cnt']['mul']*RHO_M+a['cnt']['la']*RHO_LA,'opt',ksub)
    out['a1_fits']=fits
    # rho
    rho_inst={}; 
    for x in R: rho_inst.setdefault(x['k'],[]).append(x)
    rks=sorted(rho_inst)
    def rho_fit(getv,ksub,boot,rng):
        xs=[];ys=[]
        for k in ksub:
            L=rho_inst[k]; sel=L if not boot else [L[i] for i in rng.integers(0,len(L),len(L))]
            for x in sel: xs.append(math.log2(x['n1'])); ys.append(math.log2(getv(x)))
        return slope(xs,ys)
    rf={}
    for name,ksub in [('all',rks),('k10_20',[k for k in rks if k<=20]),('drop_k10',[k for k in rks if k>=12]),('drop_k10_k12',[k for k in rks if k>=14])]:
        if len(ksub)<2: continue
        for vn,gv in [('steps',lambda x:x['e1add']),('wall',lambda x:max(x['wall'],1e-9))]:
            est=rho_fit(gv,ksub,False,None); rng=np.random.default_rng(SEED); bs=[rho_fit(gv,ksub,True,rng) for _ in range(NB)]
            rf[f'rho_{vn}_{name}']=dict(est=est,ci=[float(np.percentile(bs,2.5)),float(np.percentile(bs,97.5))],n_boot=NB,n_points=sum(len(rho_inst[k]) for k in ksub),sizes=ksub)
    out['rho_fits']=rf
    out['rho_table']=[dict(k=k,n=len(rho_inst[k]),n1=float(np.mean([x['n1'] for x in rho_inst[k]])),geomean_steps=float(np.exp(np.mean([math.log(x['e1add']) for x in rho_inst[k]]))),geomean_wall=float(np.exp(np.mean([math.log(max(x['wall'],1e-9)) for x in rho_inst[k]]))),fail=sum(1 for x in rho_inst[k] if not x['k_ok'])) for k in rks]
    json.dump(out,open('results/a1_analysis.json','w'),indent=1)
    print(json.dumps({k:{kk:(round(vv,3) if isinstance(vv,float) else vv) for kk,vv in v.items() if kk in('est','ci','n_points')} for k,v in {**fits,**rf}.items()},indent=0))
main()
