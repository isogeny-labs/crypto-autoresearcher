import sys; sys.path.insert(0,'.')
from lat import *
import random, time, sympy
rng=random.Random(5)
q,n=3,32
p=int(sympy.nextprime(q**n))
for s,t in [(2,1),(4,2)]:
    for S in [4,8,10,12,14,16]:
        t0=time.time()
        r=[z_trial(q,n,p,S,s,t,rng) for _ in range(6)]
        print(s,t,'S',S,sum(x['success'] for x in r),[x['nvan'] for x in r], round(time.time()-t0,2))
