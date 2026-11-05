# SA-03: does the per-discriminant representation count n(Delta) (forms with root xR mod p, disc Delta, |c_i|<=B^4, c2>0)
# single out Delta in S_B? Compare Delta in S_F (excluding the planted one) with controls of the same size.
import numpy as np, random, json, math
from common import *
def nforms(p,xR,B,Delta):
    M=B**4; c2=np.arange(1,M+1,dtype=np.int64)
    if not is_qr(Delta,p): return 0,0
    r=sqrt34(Delta,p); tot=0; sq=0
    for e in (r,(-r)%p):
        c1=(e-2*c2*xR)%p; c1=np.where(c1>p//2,c1-p,c1)
        ok=np.abs(c1)<=M
        c1o=c1[ok]; c2o=c2[ok]
        num=c1o*c1o-Delta
        ok2=(num%(4*c2o)==0)
        c0=num[ok2]//(4*c2o[ok2]); c2k=c2o[ok2]
        k=np.abs(c0)<=M
        tot+=int(k.sum())
        s=np.sqrt(c2k[k]).astype(np.int64); sq+=int((s*s==c2k[k]).sum())
    return tot,sq
res=[]
for bits,B in ((20,11),(24,11),(24,16),(32,11)):
    p=prime34(bits); rng=random.Random(321+bits+B)
    pl=planted(p,B,20,rng)
    if pl is None: continue
    F=[x for x in range(1,B+1) if is_qr(x**3+7,p)]
    S=[(x,y) for i,x in enumerate(F) for y in F[i+1:]]
    stru=[];ctrlA=[];ctrlB=[]
    for (xR,x1,x2) in pl:
        for (a,b) in S:
            if (a,b)==(x1,x2): continue
            stru.append(nforms(p,xR,B,16*(a**3+7)*(b**3+7)))
        # control A: pairs just outside the box, B<x<=2B
        for _ in range(len(S)):
            while True:
                a=rng.randrange(B+1,2*B+1);b=rng.randrange(B+1,2*B+1)
                if a!=b and is_qr(a**3+7,p) and is_qr(b**3+7,p): break
            ctrlA.append(nforms(p,xR,B,16*(a**3+7)*(b**3+7)))
        # control B: random 16*QR of the same magnitude
        top=16*(B**3+7)**2
        for _ in range(len(S)):
            while True:
                d=16*rng.randrange(8*8,(B**3+7)**2+1)
                if is_qr(d,p): break
            ctrlB.append(nforms(p,xR,B,d))
    f=lambda L,i: (np.mean([t[i] for t in L]),len(L))
    rec=dict(pbits=bits,B=B,targets=len(pl),struct_all=f(stru,0),struct_sq=f(stru,1),ctrlA_all=f(ctrlA,0),ctrlA_sq=f(ctrlA,1),ctrlB_all=f(ctrlB,0),ctrlB_sq=f(ctrlB,1),
             struct_max=max(t[0] for t in stru))
    res.append(rec); print(rec,flush=True)
json.dump(res,open('repcount.json','w'),indent=1)
