"""SA-12b driver: reuses cert.py/search.py (copied unchanged). Adds wall-clock budget, per-episode (delta,n) log, best-by-n-cap table."""
import os, sys, json, time, random
os.environ.setdefault('NCAP','300'); os.environ.setdefault('NROWS','400'); os.environ.setdefault('BMAX','9'); os.environ.setdefault('TMAX','5')
import search, cert
from search import *
CAPS=[60,90,120,150,200,250,300]
def run2(mode,seed,budget):
    R=random.Random(1000*seed+7); C=Cert(make_instance(1),tmax=9); log=[]
    pop=[]; best=None; t0=time.time(); rec=[]
    while time.time()-t0<budget:
        if len(pop)<20: g=rand_genome(R,mode)
        else:
            par=max(R.sample(pop,3),key=lambda x:x[0])[1]; g=mutate(par,R,mode)
            if R.random()<.3: g=mutate(g,R,mode)
        sh=flatten(g); r=C.reach(sh); d=max(r[0],0.0); n=r[1]
        s=d-1e-6*n
        rec.append((round(time.time()-t0,1),d,n,r[4],g))
        pop.append((s,g)); pop.sort(key=lambda x:-x[0]); pop=pop[:20]
        # keep diversity by n: also keep best per n-cap? (not done; plain EA as in SA-12)
        if best is None or s>best[0]: best=(s,g)
    bycap={}
    for cap in CAPS:
        c=[x for x in rec if x[2]<=cap and x[1]>0]
        if c:
            m=max(c,key=lambda x:x[1]); bycap[cap]=dict(delta=m[1],n=m[2],t=m[3],genome=dict(layers=m[4]['layers'],rem=sorted(m[4]['rem']),h=[[list(k),v] for k,v in m[4]['h'].items()],add=sorted(m[4]['add'])))
    return dict(mode=mode,seed=seed,budget=budget,episodes=len(rec),elapsed=time.time()-t0,bycap=bycap,
                log=[(a,b,c,d) for a,b,c,d,_ in rec])
if __name__=="__main__":
    mode,seed,budget=sys.argv[1],int(sys.argv[2]),float(sys.argv[3])
    r=run2(mode,seed,budget)
    json.dump(r,open(f'out_{mode}_s{seed}.json','w'))
    print(mode,seed,'episodes',r['episodes'],{k:(round(v['delta'],5),v['n'],v['t']) for k,v in r['bycap'].items()},flush=True)
