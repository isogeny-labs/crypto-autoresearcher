import sys; sys.path.insert(0,'.')
from lat import *
import random, time
rng=random.Random(5)
q,n=3,32
F=Field(q,n)
for s,t in [(2,1),(4,2)]:
    M,ks,pred=shift_params(s,t); print(s,t,len(M),pred, pred+1/n)
    for S in [4,6,8,10,12]:
        t0=time.time()
        r=[ff_trial(F,S,s,t,rng,12) for _ in range(3)]
        print(' S',S,[(x['success'],x['nvan'],x['d1'],x['d2'],x['tn'],round(x['avg'],1)) for x in r], round(time.time()-t0,2))
