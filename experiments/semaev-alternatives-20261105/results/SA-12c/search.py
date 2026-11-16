import random, json, sys, time, math, copy
import os, cert
from cert import Cert, make_instance
cert.NCAP=int(os.environ.get('NCAP',90)); cert.NROWS=int(os.environ.get('NROWS',160)); BMAX=int(os.environ.get('BMAX',5)); TMAX=int(os.environ.get('TMAX',5))
NMAX=int(sys.argv[3]) if len(sys.argv)>3 else 110
def flatten(g):
    sh=set()
    for i,(A,B,C) in enumerate(g['layers']):
        for a in range(A+1):
            for b in range(B+1):
                if a+b<=C: sh.add((i,a,b,0))
    sh -= {x for x in g['rem'] if x[:3] in {y[:3] for y in sh}} if False else set()
    sh={s for s in sh if (s[0],s[1],s[2]) not in g['rem']}
    for (i,a,b),h in g['h'].items():
        if (i,a,b,0) in sh: sh.discard((i,a,b,0)); sh.add((i,a,b,h))
    for (i,a,b,h) in g['add']: sh.add((i,a,b,h))
    return sh
def rand_genome(R,mode):
    t=R.randint(2,TMAX)
    layers=[]
    for i in range(t+1):
        A=R.randint(0,BMAX);B=R.randint(0,BMAX);layers.append([A,B,R.randint(max(A,B),A+B)])
    g=dict(layers=layers,rem=set(),h={},add=set())
    return g
def mutate(g,R,mode):
    g=copy.deepcopy(g)
    ops=['bound','bound','t'] + (['add','rem','h','add','rem'] if mode=='full' else [])
    op=R.choice(ops)
    L=g['layers']
    if op=='bound':
        l=R.choice(L); k=R.randrange(3); l[k]=max(0,l[k]+R.choice([-1,1]))
        l[2]=max(l[2],0)
    elif op=='t':
        if R.random()<.5 and len(L)>3: L.pop()
        elif len(L)<TMAX+3: L.append(list(L[-1]))
    elif op=='add':
        g['add'].add((R.randrange(len(L)),R.randint(0,6),R.randint(0,6),R.choice([0,0,0,1,2,3,4,5,6,7])))
    elif op=='rem':
        g['rem'].add((R.randrange(len(L)),R.randint(0,6),R.randint(0,6)))
    elif op=='h':
        g['h'][(R.randrange(len(L)),R.randint(0,5),R.randint(0,5))]=R.randint(1,7)
    g['add']={x for x in g['add'] if x[0]<len(L)}
    return g
def score(C,g,log):
    r=C.reach(flatten(g))
    d,n=r[0],r[1]
    val=d if d>0 else 0.0
    log.append(dict(delta=val,n=n,D=r[2],e=r[3],t=r[4]))
    return val-1e-6*n, r
def run(method,mode,seed,episodes=2000):
    R=random.Random(seed); C=Cert(make_instance(1),tmax=9); log=[]
    best=None; cur=rand_genome(R,mode); cs,_=score(C,cur,log); best=(cs,cur)
    pop=[(cs,cur)]
    T0=0.01; t0=time.time()
    TL=float(os.environ.get('TLIM',1e9))
    while len(log)<episodes and time.time()-t0<TL:
        k=len(log)
        if method=='random':
            g=rand_genome(R,mode)
            for _ in range(R.randint(0,6)): g=mutate(g,R,mode)
            s,_=score(C,g,log)
            if s>best[0]: best=(s,g)
        elif method=='sa':
            g=mutate(cur,R,mode)
            if R.random()<.3: g=mutate(g,R,mode)
            s,_=score(C,g,log)
            T=T0*(1-k/episodes)+1e-5
            if s>=cs or R.random()<math.exp((s-cs)/T): cur,cs=g,s
            if s>best[0]: best=(s,g)
        elif method=='ea':
            if len(pop)<20: g=rand_genome(R,mode)
            else:
                par=max(R.sample(pop,3),key=lambda x:x[0])[1]; g=mutate(par,R,mode)
                if R.random()<.3: g=mutate(g,R,mode)
            s,_=score(C,g,log); pop.append((s,g)); pop.sort(key=lambda x:-x[0]); pop=pop[:20]
            if s>best[0]: best=(s,g)
    # best-so-far curve
    bs=[];m=0
    for r in log: m=max(m,r['delta']); bs.append(m)
    sh=sorted(flatten(best[1])); r=C.reach(sh)
    return dict(method=method,mode=mode,seed=seed,best_reach=r[0],n=r[1],D=r[2],e=r[3],t=r[4],
        shifts=[list(x) for x in sh],curve=bs[::20],time=time.time()-t0,
        nonmono=sum(1 for x in sh if x[3]!=0), best_genome_layers=best[1]['layers'])
if __name__=="__main__":
    method,mode=sys.argv[1],sys.argv[2]
    out=[]
    for seed in range(int(sys.argv[4]) if len(sys.argv)>4 else 1):
        r=run(method,mode,seed); out.append(r); print(method,mode,seed,r['best_reach'],r['n'],r['t'],r['nonmono'],round(r['time']),flush=True)
    json.dump(out,open(f'out_{method}_{mode}_{os.environ.get("TAG","s")}.json','w'))
