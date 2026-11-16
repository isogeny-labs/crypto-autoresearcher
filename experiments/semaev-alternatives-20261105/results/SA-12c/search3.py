"""SA-12c driver: fixed episode budget (3000), NCAP=200. Same EA as SA-12b search2.py. usage: search3.py mode seed episodes"""
import os, sys, json, time, random
os.environ['NCAP']='200'; os.environ['NROWS']='400'; os.environ['BMAX']='9'; os.environ['TMAX']='5'
import search, cert
from search import *
import pickle
def run3(mode,seed,episodes,deadline=1e18):
    C=Cert(make_instance(1),tmax=9); ck=f'ck_{mode}_s{seed}.pkl'; t0=time.time()
    if os.path.exists(ck): R,cache,pop,rec,el0=pickle.load(open(ck,'rb'))
    else: R=random.Random(1000*seed+7); cache={}; pop=[]; rec=[]; el0=0.0
    ts=time.time()
    while len(rec)<episodes:
        if time.time()>deadline:
            pickle.dump((R,cache,pop,rec,el0+time.time()-ts),open(ck,'wb')); return None
        if len(pop)<20: g=rand_genome(R,mode)
        else:
            par=max(R.sample(pop,3),key=lambda x:x[0])[1]; g=mutate(par,R,mode)
            if R.random()<.3: g=mutate(g,R,mode)
        sh=flatten(g); key=frozenset(sh)
        if key not in cache: cache[key]=C.reach(sh)
        r=cache[key]; d=max(r[0],0.0); n=r[1]
        s=d-1e-6*n
        rec.append((d,n,r[4],g))
        pop.append((s,g)); pop.sort(key=lambda x:-x[0]); pop=pop[:20]
    c=[x for x in rec if x[1]<=200 and x[0]>0]
    m=max(c,key=lambda x:x[0])
    g=m[3]
    return dict(mode=mode,seed=seed,episodes=len(rec),elapsed=el0+time.time()-ts,delta=m[0],n=m[1],t=m[2],
      genome=dict(layers=g['layers'],rem=sorted(g['rem']),h=[[list(k),v] for k,v in g['h'].items()],add=sorted(g['add'])),
      shifts=[list(x) for x in sorted(flatten(g))],
      log=[(a,b,c_) for a,b,c_,_ in rec])
if __name__=="__main__":
    mode,seed,ep=sys.argv[1],int(sys.argv[2]),int(sys.argv[3])
    r=run3(mode,seed,ep,time.time()+float(sys.argv[4]))
    if r is None: print(mode,seed,'checkpointed'); sys.exit(3)
    json.dump(r,open(f'out_{mode}_s{seed}.json','w'))
    print(mode,seed,'episodes',r['episodes'],'delta',round(r['delta'],5),'n',r['n'],'t',r['t'],'sec',round(r['elapsed']),flush=True)
