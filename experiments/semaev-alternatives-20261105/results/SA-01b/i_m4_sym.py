# S_m-symmetrised LP for presentation (i), box support, single generator: orbit reduction of model.Model LP.
import sys, time, numpy as np, scipy.sparse as sps
from scipy.optimize import linprog
from model import *
from run_ceilings import pres
t=int(sys.argv[1]); m=int(sys.argv[2]); dl=float(sys.argv[3])
n,sups,cf,om=pres('i',m); gens=[(list(sups[0]),max(sups[0]))]
t0=time.time(); M=Model(n,gens,t); print('built dim',M.nz,'N',M.N,'rows',M.nrows,round(time.time()-t0,1),flush=True)
# orbit ids
key={}; col=np.zeros(M.N,int)
for i,y in enumerate(M.pts):
    k=('z',tuple(sorted(y))); col[i]=key.setdefault(k,len(key))
for q,(yi,ks,cl,lev) in enumerate(M.vl):
    k=('v',tuple(sorted(M.pts[yi])),ks); col[M.nz+q]=key.setdefault(k,len(key))
K=len(key); print('orbits',K,round(time.time()-t0,1),flush=True)
P=sps.csr_matrix((np.ones(M.N),(np.arange(M.N),col)),shape=(M.N,K))
Ar=(M.A@P).tocsr(); Ar.sum_duplicates()
# dedupe rows
Ar=Ar.tocsr(); Ar.eliminate_zeros()
h={}; keep=[]
for r in range(Ar.shape[0]):
    s,e=Ar.indptr[r],Ar.indptr[r+1]
    kk=(tuple(Ar.indices[s:e]),tuple(Ar.data[s:e]))
    if kk not in h: h[kk]=1; keep.append(r)
Ar=Ar[keep]; print('rows',M.nrows,'->',Ar.shape[0],round(time.time()-t0,1),flush=True)
cz=M.objective(cf(dl)); cfull=np.concatenate([cz[:M.nz],-M.lev])      # minimise cost - level pieces separately
lev_full=np.concatenate([np.zeros(M.nz),M.lev]); cost_full=np.concatenate([cz[:M.nz],np.zeros(M.N-M.nz)])
levr=P.T@lev_full; costr=P.T@cost_full
# Charnes-Cooper: vars w (K) , tau. max levr.w  s.t. Ar w<=0, z-orbits<=tau, costr.w=1
isz=np.array([k[0]=='z' for k in sorted(key,key=key.get)])
zi=np.where(isz)[0]
Z=sps.hstack([sps.csr_matrix((np.ones(len(zi)),(np.arange(len(zi)),zi)),shape=(len(zi),K)),-np.ones((len(zi),1))])
Aub=sps.vstack([sps.hstack([Ar,sps.csr_matrix((Ar.shape[0],1))]),Z]).tocsr()
res=linprog(np.concatenate([-levr,[0]]),A_ub=Aub,b_ub=np.zeros(Aub.shape[0]),A_eq=sps.csr_matrix(np.concatenate([costr,[0]]).reshape(1,-1)),b_eq=[1],
            bounds=[(0,1)]*K+[(0,1e3)],method='highs')
v=-res.fun; print('RESULT sym LP ratio at delta',dl,'=',v,'  => reach = ratio*delta =',v*dl,round(time.time()-t0,1),flush=True)
