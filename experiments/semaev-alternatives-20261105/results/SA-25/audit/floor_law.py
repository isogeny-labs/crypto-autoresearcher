import json,glob,collections,statistics,sys
from sympy import factorint
from sympy import jacobi_symbol as legendre_symbol
def kron(D,l):
    if l==2:
        if D%2==0: return 0
        return 1 if D%8 in (1,7) else -1
    r=D%l
    return 0 if r==0 else legendre_symbol(r,l)
rows=[]
for f in glob.glob('classes_p*.jsonl'):
    if 'nofilter' in f or 'p4001' in f or 'p10007' in f: continue
    for l in open(f): rows.append(json.loads(l))
SMALL={2,3,5,7,13,17,19,23}
def divisors(fac):
    ds=[{}]
    for l,e in fac.items():
        ds=[{**d, l:k} for d in ds for k in range(e+1)]
    return ds
def predict(r):
    f=r['f']; D0=r['D0']; S=r['size']
    fac=factorint(f)
    tot=0; flo=0
    for d in divisors(fac):
        fp=1; w=1.0
        for l,k in d.items():
            if k>0: fp*=l**k; w*= l**k*(1-kron(D0,l)/l)
        if D0 in (-3,-4) and fp>1: w/= (3 if D0==-3 else 2)
        tot+=w
        if all(d.get(l,0)==fac[l] for l in fac if l in SMALL): flo+=w
    return float(S*flo/(2*tot)), fac
res=[]
for r in rows:
    if r['f']==1 or r['nH_rows_total']==0: continue
    pred,fac=predict(r)
    if 11 in fac: continue
    res.append((r['corank'],pred,r['size'],r['p'],len([l for l in fac if l in SMALL])))
d=[c-q for c,q,S,p,k in res]; rel=[(c-q)/S for c,q,S,p,k in res]
print("classes tested",len(res))
print("corank - predicted: mean %.3f  median %.3f"%(statistics.mean(d),statistics.median(d)))
a=sorted(map(abs,rel)); print("|err|/S: mean %.4f  95pct %.4f  max %.4f"%(statistics.mean(a),a[int(.95*len(a))],a[-1]))
for k in (1,2,3,4):
    sub=[(c,q,S) for c,q,S,p,kk in res if kk==k]
    if sub: print("k=%d n=%d  mean(c/S)=%.4f  mean(pred/S)=%.4f  |c-pred|<=1: %.3f"%(k,len(sub),statistics.mean(c/S for c,q,S in sub),statistics.mean(q/S for c,q,S in sub),sum(1 for c,q,S in sub if abs(c-q)<=1)/len(sub)))
big=[x for x in res if x[2]>=50]
print("|S|>=50: n=%d |c-pred|<=1: %.3f  within 2%% of S: %.3f"%(len(big),sum(1 for c,q,S,p,k in big if abs(c-q)<=1)/len(big),sum(1 for c,q,S,p,k in big if abs(c-q)/S<0.02)/len(big)))
worst=sorted(res,key=lambda x:-abs(x[0]-x[1])/x[2])[:8]; print("worst:",[(c,round(q,1),S,p,k) for c,q,S,p,k in worst])

# --- bound check: c/S >= (1/2) prod_{l | f, l in L} (1 - 1/l)  (per-prime floor fraction minimised at kron(D0,l)=+1)
from fractions import Fraction
viol=[]; atmin=[]
for r in rows:
    fac=factorint(r['f']); b=Fraction(1,2)
    for l in fac:
        if l in SMALL: b*=Fraction(l-1,l)
    if r['corank']/r['size'] < float(b)-1e-12 and r['size']>=50: viol.append((r['p'],r['t'],r['corank'],r['size'],float(b)))
    if r['size']>=50 and abs(r['corank']/r['size']-2/15)<1e-12: atmin.append((r['p'],r['f'],[(l,kron(r['D0'],l)) for l in factorint(r['f']) if l in SMALL]))
print("bound violations among |S|>=50:",len(viol),viol[:5])
print("classes at ratio 2/15:",len(atmin),atmin[:6])
L=sorted(SMALL); import math
print("floor bound for full Hecke set L:",0.5*math.prod(1-1/l for l in L))
