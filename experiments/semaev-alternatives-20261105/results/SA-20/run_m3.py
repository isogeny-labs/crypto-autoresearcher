import json,sys,time
from model2 import *
P=json.load(open("results/step1_polytope.json")); S=P['edwards_m3']['support']; out=[]
cos=[(0,0)] if len(sys.argv)>3 else [(0,0),(1,0),(0,1),(1,1)]
for t in [int(x) for x in sys.argv[1].split(',')]:
    best=0;info=[]
    for c in cos:
        M=Model2(S,(4,4,4),t,coset=c); t0=time.time()
        r=reach(M,lambda d:[d,d,d],hi=0.1,tl=float(sys.argv[2]),tol=2e-4); info.append((c,round(r,4),M.nz,M.nrows,round(time.time()-t0,1))); best=max(best,r)
        print(t,info[-1],flush=True)
    out.append(dict(t=t,edwards_m3=round(best,4),info=info))
    json.dump(out,open("results/m3_ladder_%s.json"%sys.argv[1].replace(',','_'),"w"))
