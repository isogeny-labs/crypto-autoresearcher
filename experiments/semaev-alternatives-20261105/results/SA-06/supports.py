# Supports of S_3,S_4,S_5 (resultants) for generic / j=0 / j=1728. Saves JSON.
import json, time
from polys import *
cells={"generic":(3,5),"generic2":(-7,11),"j0":(0,7),"j1728":(7,0)}
out={}
for name,(a,b) in cells.items():
    t=time.time(); o=build(a,b,4)
    for m,P in o.items():
        pari(f"TMPX={P};")
        s=get_support("TMPX",m+1)
        out[f"{name}|S{m+1}"]=dict(a=a,b=b,support=[e for e,c in s],ncoef=len(s))
        print(name,f"S{m+1}",len(s),round(time.time()-t,2),flush=True)
json.dump(out,open("supports.json","w"))
