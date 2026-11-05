import sys, json, random, time
from build import *
from macaulay import *
def run(m,p,base,B,seed,null=False,Dmax=12,tl=900,verbose=False):
    rng=random.Random(seed)
    ring,gens,pt,meta=system(m,p,base,B,rng,null)
    info,_=macaulay_profile(ring,gens,Dmax,p,verbose=verbose,time_limit=tl)
    an=analyse(info,ring)
    return an,meta
if __name__=="__main__":
    m=int(sys.argv[1]); base=sys.argv[2]; B=int(sys.argv[3]); p=int(sys.argv[4]); Dmax=int(sys.argv[5])
    an,meta=run(m,p,base,B,1,False,Dmax,verbose=True)
    for r in an: print(r)
