"""Convex-only deterministic reference grid under the same cert metric (matched to search convex family)."""
import os,sys,json,time
os.environ.setdefault('NCAP','300'); os.environ.setdefault('NROWS','400')
import cert
from cert import *
cert.NCAP=300; cert.NROWS=400
C=Cert(make_instance(1),tmax=9); budget=float(sys.argv[1]); t0=time.time(); rec=[]
def fam(t,A,B,Cc,shr):
    sh=set()
    for i in range(t+1):
        a_=max(0,A-shr*i); b_=max(0,B-shr*i); c_=max(0,Cc-shr*i) if Cc is not None else a_+b_
        for a in range(a_+1):
            for b in range(b_+1):
                if a+b<=c_: sh.add((i,a,b,0))
    return sh
cands=[]
for t in range(2,6):
  for A in range(1,10):
    for B in range(A,10):
      for cc in (None,A,A+B//2,B+A//2):
        for shr in (0,1):
            cands.append((t,A,B,cc,shr))
import random; random.Random(0).shuffle(cands)
for (t,A,B,cc,shr) in cands:
    if time.time()-t0>budget: break
    sh=fam(t,A,B,cc,shr); r=C.reach(sh)
    if r[0]>0: rec.append((r[0],r[1],t,A,B,cc,shr))
out={}
for cap in [60,90,120,150,200,250,300]:
    c=[x for x in rec if x[1]<=cap]
    if c: out[cap]=max(c,key=lambda x:x[0])
json.dump(dict(evals=len(rec),tried=len(cands),bycap=out),open('out_grid_convex.json','w'))
print(len(rec),len(cands),{k:(round(v[0],5),)+tuple(v[1:]) for k,v in out.items()})
