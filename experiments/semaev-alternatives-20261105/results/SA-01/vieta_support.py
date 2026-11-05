# Support of S_{m+1}(x1..xm, R0) written in elementary symmetric e_1..e_m (exponent tuples), via dominance-leading-term peeling.
import json, itertools, sys
import cypari2
from semaev_polys import S, support, R0, pari
def vieta(m):
    names=[f"x{i}" for i in range(1,m+1)]
    P=S(m,names,R0)
    # e_k as pari polys
    E=[]
    for k in range(1,m+1):
        tot=pari(0)
        for c in itertools.combinations(names,k):
            term=pari(1)
            for v in c: term=term*pari(v)
            tot=tot+term
        E.append(tot)
    rem=P; res={}
    # leading term in lex order on (x1..xm): use pari variables priority: x1 highest (created first)
    while rem!=0:
        # lex-leading monomial
        q=rem; ex=[]
        for v in names:
            d=int(pari.poldegree(q,v)); ex.append(d); q=pari.polcoef(q,d,v)
        c=q
        # symmetric => ex is non-increasing
        g=[ex[i]-(ex[i+1] if i+1<m else 0) for i in range(m)]
        prod=pari(c)
        for k in range(m):
            if g[k]: prod=prod*E[k]**g[k]
        rem=rem-prod
        res[tuple(g)]=int(c)
    return res
if __name__=="__main__":
    out={}
    for m in (2,3,4):
        r=vieta(m); out[m]=sorted(r.keys())
        print(m,len(r),"max exps",[max(e[i] for e in r) for i in range(m)])
        if m==2: print(sorted(r))
    json.dump({str(k):v for k,v in out.items()},open("supports_vieta.json","w"))
