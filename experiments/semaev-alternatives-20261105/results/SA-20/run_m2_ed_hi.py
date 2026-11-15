import json,sys,time
from model2 import *
P=json.load(open("results/step1_polytope.json")); S=P['edwards_m2']['support']; out=[]
for t in (10,12,16,20):
    M=Model2(S,(2,2),t,coset=(0,)); t0=time.time(); r=reach(M,lambda d:[d,d],hi=0.25,tl=120,tol=2e-4)
    row=dict(t=t,edwards_m2=round(r,4),dim=M.nz,sec=round(time.time()-t0,1)); print(row,flush=True); out.append(row)
    json.dump(out,open("results/m2_ladder_ed_hi.json","w"))
