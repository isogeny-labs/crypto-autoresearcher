import json, glob, math, os
import numpy as np
SEED=24; NB=2000
SA='/home/user/semaev-runs/SA-24/results/'
def jl(f): return [json.loads(l) for l in open(f)]
def fit(cellsd, minE=50):
    ks=sorted(set(k for k,_ in cellsd)); nd=max(di for _,di in cellsd)+1
    per={}; X=[];Y=[];D=[]
    for di in range(nd):
        pts=[(k,math.log2(cellsd[(k,di)][0]/cellsd[(k,di)][1])) for k in ks if (k,di) in cellsd and cellsd[(k,di)][1]>=minE and cellsd[(k,di)][0]>0]
        if len(pts)>=3:
            x=np.array([a for a,_ in pts],float); y=np.array([b for _,b in pts]); per[di]=np.polyfit(x,y,1)[0]
            for a,b in pts: X.append(a);Y.append(b);D.append(di)
    pooled=None
    if len(X)>=3:
        X=np.array(X);Y=np.array(Y);D=np.array(D); num=0;den=0
        for d in set(D):
            m=D==d
            if m.sum()>=3: xc=X[m]-X[m].mean(); yc=Y[m]-Y[m].mean(); num+=(xc*yc).sum(); den+=(xc*xc).sum()
        pooled=num/den if den>0 else None
    return per,pooled
def build(g):
    pre='a2' if g==2 else 'a3'; fpre='f2' if g==2 else 'f3'; dpre='den2' if g==2 else 'den3'
    cells={}   # (k,delta)-> dict(curves: idx-> dict(null, sa=(num,den arrays), fresh=(hits,sumw,trials arrays, expev), mw=(sumw,trials arrays)))
    deltas=None
    for f in sorted(glob.glob(SA+f'{pre}_*_*.jsonl')):
        L=jl(f); h=L[0]
        if not any('done' in x for x in L): continue
        bl=[x for x in L if 'blk' in x]; k,idx=h['k'],h['idx']; deltas=h['delta']
        for di,d in enumerate(h['delta']):
            c=cells.setdefault((k,d),{'curves':{},'di':di}); c['curves'][idx]=dict(null=h['null_stratum'][di],sa_num=np.array([b['num'][di] for b in bl],float),sa_den=np.array([b['den'] for b in bl],float),p=h['p'],B=h['B'][di],F=h['F'][di])
    for f in sorted(glob.glob(f'results/{fpre}_*_*_*.jsonl')):
        parts=os.path.basename(f)[:-6].split('_'); k=int(parts[1]); d=float(parts[2]); idx=int(parts[3])
        L=jl(f)
        if not any('done' in x for x in L): continue
        h=L[0]; bl=[x for x in L if 'blk' in x]
        c=cells[(k,d)]['curves'][idx]
        c['fr_hits']=np.array([b['hits'] for b in bl],float); c['fr_sumw']=np.array([b['sumw'] for b in bl],float); c['fr_tr']=np.array([b['trials'] for b in bl],float); c['fr_exp_events']=(h['events_per_trial']*sum(b['trials'] for b in bl) if 'events_per_trial' in h else sum(b['setsum'] for b in bl)*h['D']/float(h['p'])**2); c['fr_bad']=sum(b['bad'] for b in bl)
        c['fr_set']=h.get('set',h.get('mean_set_per_c2'))
    for f in sorted(glob.glob(f'results/{dpre}_*_*.jsonl')):
        parts=os.path.basename(f)[:-6].split('_'); k=int(parts[1]); idx=int(parts[2]); L=jl(f)
        if not any('done' in x for x in L): continue
        bl=[x for x in L if 'blk' in x]
        for (kk,d),c in cells.items():
            if kk==k and idx in c['curves']: c['curves'][idx]['mw_sumw']=np.array([b['sumw'] for b in bl],float); c['curves'][idx]['mw_tr']=np.array([b['trials'] for b in bl],float)
    return cells,deltas
def cell_stats(cell,rng=None):
    # returns dict: sa=(O,E), fr=(O,E) or None
    Osa=Esa=Ofr=Efr=0.0; has_fr=False
    for idx,c in cell['curves'].items():
        nb=len(c['sa_den']); sel=np.arange(nb) if rng is None else rng.integers(0,nb,nb)
        Osa+=c['sa_num'][sel].sum(); Esa+=c['null']*c['sa_den'][sel].sum()
        if 'fr_sumw' in c:
            has_fr=True; nf=len(c['fr_sumw']); sf=np.arange(nf) if rng is None else rng.integers(0,nf,nf)
            nm=len(c['mw_sumw']); sm=np.arange(nm) if rng is None else rng.integers(0,nm,nm)
            mw=c['mw_sumw'][sm].sum()/c['mw_tr'][sm].sum()
            Ofr+=c['fr_sumw'][sf].sum(); Efr+=c['null']*c['fr_tr'][sf].sum()*mw
    return (Osa,Esa),((Ofr,Efr) if has_fr else None)
def main():
    out={}
    for g in (2,3):
        cells,deltas=build(g); keys=sorted(cells)
        rng=np.random.default_rng(SEED)
        base={}; 
        for key in keys:
            sa,fr=cell_stats(cells[key]); base[key]=(sa,fr)
        def pooled(sa,fr): return (sa[0]+(fr[0] if fr else 0), sa[1]+(fr[1] if fr else 0))
        bs={key:{'sa':[],'fr':[],'po':[]} for key in keys}; bsslope=[]; bsper={}
        for b in range(NB):
            cd={}
            for key in keys:
                sa,fr=cell_stats(cells[key],rng); po=pooled(sa,fr)
                if sa[1]>0 and sa[0]>0: bs[key]['sa'].append(sa[0]/sa[1])
                if fr and fr[1]>0: bs[key]['fr'].append(fr[0]/fr[1])
                if po[0]>0: bs[key]['po'].append(po[0]/po[1])
                cd[(key[0],cells[key]['di'])]=po
            per,pl=fit(cd)
            if pl is not None: bsslope.append(pl)
            for di,sv in per.items(): bsper.setdefault(di,[]).append(sv)
        ci=lambda a:[float(np.percentile(a,2.5)),float(np.percentile(a,97.5))] if len(a)>10 else None
        res=[]
        for key in keys:
            sa,fr=base[key]; po=pooled(sa,fr); c=cells[key]
            ev_exp=sum(x.get('fr_exp_events',0) for x in c['curves'].values()); ev_obs=sum(x['fr_hits'].sum() for x in c['curves'].values() if 'fr_hits' in x)
            res.append(dict(k=key[0],delta=key[1],p=list(c['curves'].values())[0]['p'],B=list(c['curves'].values())[0]['B'],F=list(c['curves'].values())[0]['F'],
              sa=dict(obs=sa[0],exp=sa[1],ratio=sa[0]/sa[1],ci=ci(bs[key]['sa'])),
              fresh=(dict(obs=fr[0],exp=fr[1],ratio=fr[0]/fr[1],ci=ci(bs[key]['fr']),events_obs=float(ev_obs),events_exp=ev_exp,bad=int(sum(x.get('fr_bad',0) for x in c['curves'].values()))) if fr else None),
              pooled=dict(obs=po[0],exp=po[1],ratio=po[0]/po[1],ci=ci(bs[key]['po']))))
        cd0={(r['k'],deltas.index(r['delta'])):(r['pooled']['obs'],r['pooled']['exp']) for r in res}
        per0,pl0=fit(cd0)
        out[f'g{g}']=dict(cells=res,pooled_slope=dict(est=pl0,ci=ci(bsslope),n_boot=len(bsslope)),per_delta={str(deltas[di]):dict(est=v,ci=ci(bsper[di]),n_boot=len(bsper[di])) for di,v in per0.items()},deltas=deltas)
    json.dump(out,open('results/p1_analysis.json','w'),indent=1,default=float)
    for g,r in out.items():
        print(g,'pooled slope',r['pooled_slope']); print(' per-delta',{d:(round(v['est'],4),[round(x,4) for x in v['ci']]) for d,v in r['per_delta'].items()})
        for c in r['cells']:
            f=c['fresh']
            if f: print(c['k'],c['delta'],'fresh',round(f['ratio'],3),[round(x,3) for x in f['ci']],'ev',int(f['events_obs']),round(f['events_exp'],1),'| sa',round(c['sa']['ratio'],3),'| pooled',round(c['pooled']['ratio'],3),[round(x,3) for x in c['pooled']['ci']],'bad',f['bad'])
main()
