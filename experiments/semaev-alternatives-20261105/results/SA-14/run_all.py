import json, kummer_sd as K, sys
rows=[]
def go(p,q,ts,seeds,**kw):
    for t in ts:
        for s in seeds:
            r=K.run(p,q,t,s,timeout=150,**kw); rows.append(r); print(r,flush=True)
go(12289,2,range(1,7),range(1,6),planted=True)
go(12289,2,range(1,7),range(1,6),planted=False)
go(12289,2,range(1,6),range(1,4),planted=True,null=True)
go(7*243+1 if False else 1459,3,range(1,5),range(1,4),planted=True)
json.dump(rows,open("out/sd_rows.json","w"))
