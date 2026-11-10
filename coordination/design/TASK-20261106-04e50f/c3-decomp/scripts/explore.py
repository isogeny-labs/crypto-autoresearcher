import json,sys
import numpy as np
rs=[json.loads(l) for l in open(sys.argv[1])]
rows=[]
for r in rs:
    if r['arm']!='incumbent' or r['warmup']: continue
    ph={p['name']:p for p in r['phases']}
    rel=ph['relations']; n=rel['native']
    tot=rel['adds']+rel['doubles']
    pool_ops=n['walk_pool_ops']
    un=tot-n['walk_steps']-n['walk_pool_restarts']-17-pool_ops
    rows.append((un,rel['scalar_mults'],n['relations'],n['walk_pool_offsets'],n['walk_restarts'],n['walk_pool_ops'],n['trials'],n['walk_steps'],tot))
a=np.array(rows,float)
print(a[:8]); 
print('un/mult',(a[:,0]/ (a[:,1]-2*a[:,3])).mean())
# regress un - 38 per mult on relations
X=np.c_[a[:,1],a[:,2]]; c=np.linalg.lstsq(X,a[:,0],rcond=None)[0]; print(c)
