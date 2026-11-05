import json, numpy as np
from reach import *
out={}
for name in ['P1 (x1,x2) bounds (1,1)','P3 conic (e1,e2) bounds (1,2)']:
    P,(a,b)=pres[name]; rows=[]
    for t in (8,12,16,20,24):
        sK,s1,s2,n=build(P,t,(0,0),'sumset'); d=sK/(a*s1+b*s2); rows.append((t,d)); print(name,t,d,flush=True)
    ts=np.array([r[0] for r in rows],float); ds=np.array([r[1] for r in rows])
    # fit d = dinf - c/t - e/t^2 on last 4
    Amat=np.vstack([np.ones(4),-1/ts[1:],-1/ts[1:]**2]).T
    sol=np.linalg.lstsq(Amat,ds[1:],rcond=None)[0]
    print('  Richardson dinf (t>=12) =',sol[0],' 1/6=',1/6)
    out[name]={'rows':rows,'dinf':sol[0]}
json.dump(out,open('reach2_rows.json','w'),indent=1)
