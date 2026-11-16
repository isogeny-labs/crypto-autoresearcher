import json,sys
from arith import *
nb=json.load(open(sys.argv[1])); D=nb['D']; T=Tower(D)
ok=True
for e in nb['edges']:
    n,m,l=e['n'],e['m'],e['l']
    fa=T.fibres(n,l)
    fn=[sorted(g-1 for g in row) for row in e['nb']]
    same=[sorted(x) for x in fa]==fn
    print('edge',n,m,'h',len(fa),'fibres equal numeric:',same,flush=True); ok&=same
print('ALL EQUAL' if ok else 'MISMATCH')
