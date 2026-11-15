import sys; sys.path.insert(0,'.')
from lat3 import *
import sympy, time
rng=random.Random(1); random.seed(1)
q,n=3,32; F=Field(q,n); p=int(sympy.nextprime(q**n))
for S in [3,4,5,6]:
    Ds=[S//3+(1 if i<S%3 else 0) for i in range(3)]
    t0=time.time(); r=ff_trial3(F,Ds,4,1,rng,12); a=time.time()-t0
    t0=time.time(); z=z_trial3(q,n,p,Ds,4,1,rng); b=time.time()-t0
    print(S,Ds,r,round(a,1),z,round(b,1),flush=True)
