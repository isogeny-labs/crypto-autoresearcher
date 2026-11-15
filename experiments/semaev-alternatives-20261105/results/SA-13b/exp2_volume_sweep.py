# Exhaustive-grid check of the volume inequality  c(W) <= C * (W0 W1 W2)^{2/9}.
# c(W) = #{1<=x1<=x2 integers : |G_k(x1,x2)| <= W_k, k=0,1,2}.  All pairs with x1*x2<=E are enumerated; boxes with W0 < E^2/2 are then exact
# (for x1x2>E>=M, |G0|>=e2^2/2>W0).  For each (W0,W1) on a log grid, W2 = k-th smallest G2 among eligible pairs (tight boxes), all k scanned.
# Then each maximiser is tightened (W0,W1 := actual maxima over the chosen set) and re-evaluated.
import numpy as np, json, math, sys, time
from lib import *
E=int(float(sys.argv[1])); ng=int(sys.argv[2]); curves=[(0,7),(2,5),(-3,11)]
X1,X2=pairs_upto(E); print("pairs",len(X1),flush=True)
res={}
for (a,b) in curves:
    t0=time.time()
    G0,G1,G2=G_arrays(X1.astype(np.float64),X2.astype(np.float64),a,b)
    A0=np.abs(G0);A1=np.abs(G1);A2=np.abs(G2)
    dec={}
    best=[]  # (ratio_c_over_omega29, c, W0,W1,W2)
    W0max=E*E/2.5
    g0=np.unique(np.round(np.exp(np.linspace(0,math.log(W0max),ng))))
    g1=np.unique(np.round(np.exp(np.linspace(0,math.log(8*E**1.5),ng))))
    o0=np.argsort(A0,kind='stable'); A0s=A0[o0]
    for W0 in g0:
        idx0=o0[:np.searchsorted(A0s,W0,side='right')]
        if len(idx0)==0: continue
        a1=A1[idx0]; a2=A2[idx0]; a0=A0[idx0]
        for W1 in g1:
            m=a1<=W1
            if not m.any(): continue
            s2=np.sort(a2[m]); k=np.arange(1,len(s2)+1,dtype=np.float64)
            W2=np.maximum(s2,1.0)
            # use actual maxima of G0,G1 over the set? (approximation: grid values; tightened below for the top)
            r=k/((W0*W1*W2)**(2/9))
            j=int(np.argmax(r)); best.append((float(r[j]),int(k[j]),float(W0),float(W1),float(W2[j])))
            kk=np.log10(k).astype(int)
            for d in np.unique(kk):
                mm=kk==d; v=float(r[mm].max()); dec[int(d)]=max(dec.get(int(d),0),v)
    best.sort(reverse=True)
    # tighten top 20
    tight=[]
    for (r,c,W0,W1,W2) in best[:20]:
        m=(A0<=W0)&(A1<=W1)&(A2<=W2)
        c2=int(m.sum()); tW0=max(1.0,float(A0[m].max())); tW1=max(1.0,float(A1[m].max())); tW2=max(1.0,float(A2[m].max()))
        tight.append((c2/((tW0*tW1*tW2)**(2/9)),c2,tW0,tW1,tW2))
    tight.sort(reverse=True)
    res[str((a,b))]=dict(by_decade_of_c=dec,worst_c_over_omega29=tight[0][0],worst_c9_2_over_omega=tight[0][0]**4.5,box=tight[0][1:],top=tight[:5],grid_best=best[:3],time=time.time()-t0)
    print("  max ratio by decade of c:",{k:round(v,3) for k,v in sorted(dec.items())})
    print((a,b),"worst c/omega^(2/9) = %.4f  (c^{9/2}/omega = %.4f)  at c=%d W=(%.3g,%.3g,%.3g)  %.0fs"%(tight[0][0],tight[0][0]**4.5,*tight[0][1:],time.time()-t0),flush=True)
json.dump(res,open('exp2_volume_rows_E%g.json'%E,'w'),indent=1)
