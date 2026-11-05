import sys, json, random, time, sympy as sp
from build import *
from macaulay import *
def dsol(info):
    qs=[(r['D'],r['cols']-r['rank']) for r in info if 'rank' in r]
    ab=[r for r in info if 'aborted' in r]
    if ab or len(qs)<4 or len(set(q for _,q in qs[-4:]))!=1: return None,qs[-1][1] if qs else None,qs
    qf=qs[-1][1]
    D=qs[-1][0]
    for d,q in reversed(qs):
        if q==qf: D=d
        else: break
    return D,qf,qs
def one(m,p,base,B,seed,null,Dmax,tl):
    rng=random.Random(seed)
    if base=='SV':
        ring,gens,pt,meta=system_SV(m,p,B,rng)
    elif base=='S':
        ring,gens,pt,meta=system_S(m,p,B,rng)
    else:
        ring,gens,pt,meta=system(m,p,base,B,rng,null)
    t=time.time()
    info,_=macaulay_profile(ring,gens,Dmax,p,verbose=False,time_limit=tl,colcap=9000)
    D,qf,qs=dsol(info)
    ab=[r for r in info if 'aborted' in r]
    return dict(m=m,p=p,base=base,B=B,seed=seed,null=null,Dsol=D,K=qf,aborted=(ab[0]['aborted'] if ab else None),
                last_D=qs[-1][0] if qs else None,maxcols=max(r['cols'] for r in info),t=round(time.time()-t,1),nvars=ring.n,q=[q for _,q in qs])
if __name__=="__main__":
    m=int(sys.argv[1]); base=sys.argv[2]; Bs=[int(x) for x in sys.argv[3].split(',')]; nseeds=int(sys.argv[4]); null=sys.argv[5]=='null'
    Dmax=int(sys.argv[6]); tl=float(sys.argv[7]); outf=sys.argv[8]
    pmul_=float(sys.argv[9]) if len(sys.argv)>9 else 8
    for B in Bs:
        p=int(sp.nextprime(int(pmul_*B**m)))
        if p>=65536: p=int(sp.prevprime(65536))
        for seed in range(nseeds):
            r=one(m,p,base,B,seed,null,Dmax,tl)
            print(json.dumps(r),flush=True)
            open(outf,'a').write(json.dumps(r)+"\n")
