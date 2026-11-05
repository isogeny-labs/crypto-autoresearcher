import json, numpy as np, time
from jm import *
sup=json.load(open('../out/vieta_support.json'))
s=[tuple(x) for x in sup['4']['support']]
t=time.time(); r=reach(s,(1,2,3,4),kmax=6)
print({k:round(v[0],6) for k,v in r.items()},{k:v[2] for k,v in r.items()},time.time()-t)
ks=sorted(r)
for use in (ks[-3:],ks[-4:-1]):
    M=np.array([[1,-1/k,-1/k**2] for k in use]); y=np.array([r[k][0] for k in use])
    print(use,float(np.linalg.solve(M,y)[0]))
json.dump({k:r[k][0] for k in r},open('../out/reach_m4_k6.json','w'))
