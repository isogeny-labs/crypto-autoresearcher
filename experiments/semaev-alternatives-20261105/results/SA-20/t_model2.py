import json,sys,time
from model2 import *
P=json.load(open("results/step1_polytope.json"))
for t in (2,3,4):
    for name in ("weier_m2",):
        S=P[name]['support']; M=Model2(S,(2,2),t)
        t0=time.time(); r=reach(M,lambda d:[d,d],hi=0.25); print(name,t,round(r,4),"dim",M.nz,round(time.time()-t0,1),flush=True)
