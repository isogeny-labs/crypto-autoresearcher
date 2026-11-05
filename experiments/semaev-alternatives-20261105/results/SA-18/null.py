# Null: random targets xR with NO planted decomposition (and generically none in the box). Count false positives.
import random,json
from exp import *
res=[]
for bits,d,N,t in ((64,0.08,4,1),(96,0.08,4,1),(96,0.10,6,2)):
    rng=random.Random(5+bits); p,a,b=mk_curve(bits,'small',rng); B=int(p**d)
    fp=cert=n=0
    for _ in range(40):
        xR=rng.randrange(p)
        if sqrtm((xR**3+a*xR+b)%p,p) is None: continue
        r=trial(p,a,b,B,N,t,rng,plant=False,nullxR=xR); n+=1; fp+=r['fp']; cert+=r['ncert']
    res.append(dict(bits=bits,delta=d,N=N,t=t,B=B,targets=n,false_positives=fp,mean_ncert=cert/n)); print(res[-1])
json.dump(res,open('null_out.json','w'),indent=1)
