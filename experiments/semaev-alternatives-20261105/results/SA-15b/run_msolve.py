"""SA-15b solver 5: msolve (F4) on the SA-04 norm presentation, vanishing-polynomial base, m=4, 60 s cap.
msolve refuses characteristic >= 2^31, so the SA-15 instances (p >= 2^40) cannot be given to it; we run a scaled replica with the same B = floor(p^(1/5))
(p = nextprime(B^5) < 2^31, same builder as SA-04, random curve, planted x_i <= B)."""
import sys, os, json, time
os.environ["SCR"]=os.path.abspath("scr")
sys.path.insert(0,"/home/user/semaev-runs/SA-04/scripts")
import sympy as sp
from ms_sweep import one
out=[]
for B in (4,8,16,32,64):
    p=int(sp.nextprime(B**5))
    assert p<2**31
    for seed in range(3):
        r=one(4,p,'V',B,seed,False,60); r['log2p']=round(__import__('math').log2(p),1); print(json.dumps(r),flush=True); out.append(r)
        if r['status']=='timeout': break
json.dump(out,open("msolve_scaled_results.json","w"),indent=1)
