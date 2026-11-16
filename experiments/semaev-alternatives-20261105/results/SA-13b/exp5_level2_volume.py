# Numerical probe of the level-2 (modulus p^2, S_3^2 certificate) coverage:  c2(W)=#{x : |s2_j(x)|<=W_j, j=0..4}, s2 = T-coefficients of S_3^2 (n=5).
# Question: sup of c2 / omega^kappa, omega=prod W_j, for kappa=1/15 (full-box heuristic 2/(8+7+6+5+4)).
# Method A: regions {x1<=A, x2<=B, x2-x1<=D}.  Method B: coordinate hill-climb over general boxes from many random starts.
import numpy as np, math, json, sys
from lib import *
rng=np.random.default_rng(5)
a,b=0,7; E=int(float(sys.argv[1]))
X1,X2=pairs_upto(E); x1=X1.astype(np.float64); x2=X2.astype(np.float64)
G0,G1,G2=[np.abs(v) for v in G_arrays(x1,x2,a,b)]
g0,g1,g2=G_arrays(x1,x2,a,b)
S=np.stack([g0*g0,np.abs(2*g0*g1),np.abs(2*g0*g2+g1*g1),np.abs(2*g1*g2),g2*g2],1)   # |s2_j|
S=np.maximum(S,1.0)
res={}
# A
best=(0,None); rowsA=[]
Ag=np.unique(np.round(np.exp(np.linspace(0,math.log(E**0.5),24))))
Bg=np.unique(np.round(np.exp(np.linspace(0,math.log(E),30))))
for A in Ag:
    for B in Bg:
        if B<A: continue
        for Dd in np.unique(np.round(np.exp(np.linspace(0,math.log(B),14)))):
            m=(x1<=A)&(x2<=B)&((x2-x1)<=Dd)
            c=int(m.sum())
            if c<20: continue
            W=S[m].max(0); lw=np.log(W).sum()
            rowsA.append((c/math.exp(lw/15),c,math.exp(lw),A,B,Dd))
rowsA.sort(reverse=True); print("A: top",[tuple(round(v,3) for v in r) for r in rowsA[:4]])
# fit exponent on large c
big=[r for r in rowsA if r[1]>=2000]
x=np.array([math.log(r[2]) for r in big]); y=np.array([math.log(r[1]) for r in big])
print("A: max over regions with c>=2000 of log c/log omega =",max(y/x),"   (1/15=%.4f, 2/25=%.4f)"%(1/15,2/25))
res['A_top']=rowsA[:5]; res['A_max_logratio_c>=2000']=float(max(y/x))
# B hill-climb: maximise log c - kappa*log omega
def count(lW):
    return int(((S<=np.exp(lW)[None,:]).all(1)).sum())
bestB=(0,None)
for start in range(12):
    ref=S[rng.integers(0,len(S),size=1)[0]]
    cx=rng.uniform(math.log(30),math.log(E**0.5))
    lW=np.log(S[np.argmin(np.abs(np.log(x2)-cx)+0*x1)])+rng.normal(0,.3,5)
    cur=count(lW); score=lambda lW,c: math.log(max(c,1))-np.sum(lW)/15
    sc=score(lW,cur)
    for it in range(60):
        imp=False
        for j in rng.permutation(5):
            for step in (0.4,-0.2,0.1,-0.05):
                l2=lW.copy(); l2[j]+=step; c2=count(l2); s2=score(l2,c2)
                if s2>sc+1e-12 and c2>=20: lW,cur,sc=l2,c2,s2; imp=True
        if not imp: break
    r=cur/math.exp(np.sum(lW)/15)
    print("B start",start,"c=%d omega^(1/15)=%.3g ratio=%.3f logc/logomega=%.4f"%(cur,math.exp(np.sum(lW)/15),r,math.log(cur)/np.sum(lW)),flush=True)
    if r>bestB[0]: bestB=(r,(cur,list(lW)))
res['B_best']=bestB
json.dump(res,open('exp5_rows.json','w'),default=float,indent=1)
