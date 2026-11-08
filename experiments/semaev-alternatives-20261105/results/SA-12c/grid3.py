"""Exhaustive convex-family grid under cert.py metric, n<=200. usage: grid3.py t  -> out_grid_t{t}.json"""
import os,sys,json,time
os.environ['NCAP']='200'; os.environ['NROWS']='400'
import cert
from cert import *
cert.NCAP=200; cert.NROWS=400
t=int(sys.argv[1]); C=Cert(make_instance(1),tmax=9); rec=[]; seen=set(); t0=time.time()
def layers(A,B,sa,sb,k):
    L=[]
    for i in range(t+1):
        a=max(0,A-sa*i); b=max(0,B-sb*i)
        c=a+b if k is None else min(a+b,max(a,b)+k)
        L.append([a,b,c])
    return L
for A in range(0,10):
  for B in range(0,10):
    for sa in (0,1,2):
      for sb in (0,1,2):
        for k in (None,0,1,2,3):
            L=layers(A,B,sa,sb,k); key=tuple(map(tuple,L))
            if key in seen: continue
            seen.add(key)
            sh={(i,a,b,0) for i,(A_,B_,C_) in enumerate(L) for a in range(A_+1) for b in range(B_+1) if a+b<=C_}
            r=C.reach(sh)
            if r[0]>0: rec.append((r[0],r[1],L))
json.dump(dict(t=t,distinct=len(seen),evals=len(rec),elapsed=time.time()-t0,rec=rec),open(f'out_grid_t{t}.json','w'))
b=max(rec,key=lambda x:x[0]); print(t,len(seen),len(rec),round(time.time()-t0),round(b[0],5),b[1],b[2],flush=True)
