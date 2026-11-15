import json, glob, math, sys, random
import numpy as np
SEED=24; NB=2000
def load(prefix):
    curves={}
    for f in sorted(glob.glob(f'results/{prefix}_*_*.jsonl')):
        L=[json.loads(l) for l in open(f)]
        hdr=L[0]; blocks=[x for x in L if 'blk' in x]
        if not any('done' in x for x in L): continue
        curves[(hdr['k'],hdr['idx'])]=dict(hdr=hdr, den=np.array([b['den'] for b in blocks],float), num=np.array([b['num'] for b in blocks],float))
    return curves
def cells(curves, rngsel=None):
    # returns dict (k,di)-> (obs, exp) for chosen blocks per curve
    out={}
    ks=sorted(set(k for k,_ in curves))
    for k in ks:
        cs=[c for (kk,i),c in curves.items() if kk==k]
        nd=len(cs[0]['hdr']['delta'])
        for di in range(nd):
            O=0.0;E=0.0
            for c in cs:
                nb=len(c['den']); sel=np.arange(nb) if rngsel is None else rngsel[id(c)]
                O+=c['num'][sel,di].sum(); E+=c['hdr']['null_stratum'][di]*c['den'][sel].sum()
            out[(k,di)]=(O,E)
    return out
def fit(cellsd, curves, minE=50):
    # per-delta slopes and pooled (delta fixed effects) slope of log2(ratio) on log2 p
    ks=sorted(set(k for k,_ in cellsd)); nd=max(di for _,di in cellsd)+1
    per={}; X=[];Y=[];D=[]
    for di in range(nd):
        pts=[(k,math.log2(cellsd[(k,di)][0]/cellsd[(k,di)][1])) for k in ks if cellsd[(k,di)][1]>=minE and cellsd[(k,di)][0]>0]
        if len(pts)>=3:
            x=np.array([a for a,_ in pts],float); y=np.array([b for _,b in pts]); per[di]=np.polyfit(x,y,1)[0]
            for a,b in pts: X.append(a);Y.append(b);D.append(di)
    pooled=None
    if len(set(D))>=1 and len(X)>=3:
        X=np.array(X);Y=np.array(Y);D=np.array(D); num=0;den=0
        for d in set(D):
            m=D==d
            if m.sum()>=3: xc=X[m]-X[m].mean(); yc=Y[m]-Y[m].mean(); num+=(xc*yc).sum(); den+=(xc*xc).sum()
        pooled=num/den if den>0 else None
    return per,pooled
def analyze(prefix,label):
    curves=load(prefix)
    if not curves: return None
    base=cells(curves); hdrs={k:[c for (kk,i),c in curves.items() if kk==k][0]['hdr'] for k in set(k for k,_ in curves)}
    per0,pooled0=fit(base,curves)
    rng=np.random.default_rng(SEED); bs_pooled=[]; bs_per={}; bs_cell={}
    for b in range(NB):
        sel={id(c):rng.integers(0,len(c['den']),len(c['den'])) for c in curves.values()}
        cd=cells(curves,sel); per,pooled=fit(cd,curves)
        if pooled is not None: bs_pooled.append(pooled)
        for di,s in per.items(): bs_per.setdefault(di,[]).append(s)
        for key,(O,E) in cd.items():
            if O>0 and E>0: bs_cell.setdefault(key,[]).append(O/E)
    ci=lambda a:(float(np.percentile(a,2.5)),float(np.percentile(a,97.5)))
    res=dict(label=label,cells=[],per_delta_slope={},pooled_slope=dict(est=pooled0,ci=ci(bs_pooled) if bs_pooled else None,n_boot=len(bs_pooled)))
    for (k,di),(O,E) in sorted(base.items()):
        h=hdrs[k]; cc=bs_cell.get((k,di),[1,1])
        res['cells'].append(dict(k=k,p=h['p'],delta=h['delta'][di],B=h['B'][di],F=h['F'][di],obs=O,exp=E,ratio=(O/E if E>0 else None),ci=ci(cc),powered=bool(E>=50),null_stratum_mean=E))
    for di,s in per0.items(): res['per_delta_slope'][str(hdrs[min(hdrs)]['delta'][di])]=dict(est=s,ci=ci(bs_per[di]),n_boot=len(bs_per[di]))
    return res
if __name__=="__main__":
    out={}
    for prefix,label in [('a2','A2 genus 2'),('a3','A3 genus 3')]:
        r=analyze(prefix,label)
        if r: out[prefix]=r
    json.dump(out,open('results/split_analysis.json','w'),indent=1)
    for pf,r in out.items():
        print(r['label'],'pooled slope',r['pooled_slope'])
        for c in r['cells']: print(c['k'],c['delta'],c['B'],c['F'],int(c['obs']),round(c['exp'],1),None if c['ratio'] is None else round(c['ratio'],3),[round(x,3) for x in c['ci']],c['powered'])
        print(json.dumps(r['per_delta_slope']))
