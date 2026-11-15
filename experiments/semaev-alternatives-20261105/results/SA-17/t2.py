import sys; sys.path.insert(0,'.')
from lat import *
import random, time, sympy
rng=random.Random(5)
for q,n,kf in [(7,64,7),(3,64,12)]:
    F=Field(q,n); p=int(sympy.nextprime(q**n))
    for s,t in [(6,3),(8,4)]:
        S=int(2*n*0.12)
        t0=time.time(); r=ff_trial(F,S,s,t,rng,kf); a=time.time()-t0
        t0=time.time(); z=z_trial(q,n,p,S,s,t,rng); b=time.time()-t0
        print(q,n,s,t,S,'ff',r['success'],r['nvan'],r['d1'],r['d2'],r['tn'],round(a,1),'z',z['success'],z['nvan'],round(b,1),round(z['tred'],1),flush=True)
