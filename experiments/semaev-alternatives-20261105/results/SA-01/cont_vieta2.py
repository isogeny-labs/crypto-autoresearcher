import numpy as np
N=260
def ratio(L,W):
    S=max(L,W); a=(np.arange(N)+.5)/N*S; A,Bm=np.meshgrid(a,a,indexing='ij')
    inR=(A+Bm<=L)&(A+2*Bm<=W)
    k=np.minimum(A/2,(W-A-2*Bm)/2); k=np.where(inR,np.maximum(k,0),0)
    c=((A+2*Bm)*inR).sum()
    return k.sum()/c if c>0 else 0
best=0
for L in np.linspace(0.5,4,15):
    for W in np.linspace(0.5,6,23):
        r=ratio(L,W)
        if r>best: best=r;arg=(L,W)
print(best,arg)
