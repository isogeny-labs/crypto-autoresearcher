import json,sys,time
from model2 import *
P=json.load(open("results/step1_polytope.json"))
ts=[int(x) for x in sys.argv[1].split(',')]; tl=float(sys.argv[2])
out=[]
for t in ts:
    row=dict(t=t)
    for name,cosets in (("weier_m2",[None]),("edwards_m2",[(0,),(1,)]),("edwards_m2_box",[None])):
        key=name.replace("_box","")
        S=P[key]['support']
        if name.endswith("_box"):  # Edwards polynomial treated as a dense box support (no sparsity, ignoring parity) = control for 'what the generic box gets'
            S=[(a,b) for a in range(3) for b in range(3)]
        best=0;info=[]
        for c in cosets:
            M=Model2(S,(2,2),t,coset=c); t0=time.time()
            r=reach(M,lambda d:[d,d],hi=0.25,tl=tl); info.append((c,round(r,4),M.nz,round(time.time()-t0,1)))
            best=max(best,r)
        row[name]=round(best,4); row[name+"_info"]=info
    print(row,flush=True); out.append(row)
    json.dump(out,open(f"results/m2_ladder_{sys.argv[1].replace(',','_')}.json","w"))
