import json
from reach import *
name='P1 (x1,x2) bounds (1,1)'; P,_=pres[name]
out={}
for t in (12,24):
    sK,s1,s2,n=build(P,t,(0,0),'sumset')
    print('t',t,'sK/n=%.4f s1/n=%.4f s2/n=%.4f'%(sK/n,s1/n,s2/n))
    rows=[]
    for beta in (0.10,0.14,0.16,0.18,0.20,0.22,0.25,0.30):
        v=min(beta,max(0.0,(sK-beta*s1)/s2))
        rows.append((beta,v,(beta-v)/beta)); print('   beta=%.2f  v*=%.4f  calls=p^%.4f = B^%.3f'%(beta,v,beta-v,(beta-v)/beta))
    out[t]=rows
json.dump(out,open('hybrid_asym.json','w'))
