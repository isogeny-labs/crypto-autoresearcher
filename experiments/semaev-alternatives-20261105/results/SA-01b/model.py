"""Exact (MILP) and relaxed (LP) shift-set optimiser; fixes the double counting of the LP when closures of different levels are not nested."""
import numpy as np, itertools, scipy.sparse as sps, time
from scipy.optimize import linprog, milp, LinearConstraint, Bounds
from coppersmith_lp import maxelems, sumset_max, powers_max, compositions

class Model:
    def __init__(self,n,gens,t):
        self.n=n; self.t=t; r=len(gens); lam=[g[1] for g in gens]
        maxs=[maxelems(g[0]) for g in gens]
        pw=[powers_max(maxs[i],t) for i in range(r)]
        ext=[0]*n
        for ks in compositions(r,t):
            for j in range(n): ext[j]=max(ext[j],sum(ks[i]*max(c[j] for c in maxs[i]) for i in range(r)))
        shape=[e+1 for e in ext]; self.shape=shape
        pts=list(itertools.product(*[range(s) for s in shape])); self.pts=pts
        idx={y:i for i,y in enumerate(pts)}; self.idx=idx; nz=len(pts); self.nz=nz
        clcache={}
        vl=[]
        for y in pts:
            for ks in compositions(r,t):
                yp=[y[j]-sum(ks[i]*lam[i][j] for i in range(r)) for j in range(n)]
                if min(yp)<0: continue
                if ks not in clcache:
                    cl=[tuple([0]*n)]
                    for i in range(r):
                        if ks[i]>0: cl=sumset_max(cl,pw[i][ks[i]])
                    clcache[ks]=cl
                cps=[tuple(yp[j]+c[j] for j in range(n)) for c in clcache[ks]]
                if any(cp[j]>ext[j] for cp in cps for j in range(n)): continue
                vl.append((idx[y],ks,[idx[cp] for cp in cps],sum(ks)))
        self.vl=vl; nv=len(vl); N=nz+nv; self.N=N
        rows=[];cols=[];vals=[];ri=0
        for q,(yi,ks,cl,lev) in enumerate(vl):
            for cp in cl:
                rows+=[ri,ri];cols+=[nz+q,cp];vals+=[1,-1];ri+=1       # v<=z_cp
        byy={}
        for q,(yi,ks,cl,lev) in enumerate(vl): byy.setdefault(yi,[]).append(q)
        for yi,qs in byy.items():
            for q in qs: rows.append(ri);cols.append(nz+q);vals.append(1)
            rows.append(ri);cols.append(yi);vals.append(-1);ri+=1     # sum v<=z_y
        for y in pts:
            for j in range(n):
                if y[j]+1<shape[j]:
                    y2=list(y);y2[j]+=1
                    rows+=[ri,ri];cols+=[idx[tuple(y2)],idx[y]];vals+=[1,-1];ri+=1   # down-closed
        self.A=sps.csr_matrix((vals,(rows,cols)),shape=(ri,N)); self.nrows=ri
        self.lev=np.array([v[3] for v in vl],float)
    def objective(self,cost):
        c=np.zeros(self.N)
        for y,i in self.idx.items(): c[i]=sum(cost[j]*y[j] for j in range(self.n))
        return c
    def milp_gain(self,cost,tl=60):
        """max over integer M of  sum level - sum cost  (>0 => feasible: det < p^{t dim})"""
        cz=self.objective(cost)
        obj=np.concatenate([cz[:self.nz],-self.lev])   # minimise cost - level
        res=milp(obj,constraints=LinearConstraint(self.A,-np.inf,0),integrality=np.ones(self.N),bounds=Bounds(0,1),options=dict(time_limit=tl,mip_rel_gap=1e-6))
        if res.x is None: return None,None,None
        gain=-res.fun
        return gain,res.x,getattr(res,'mip_dual_bound',None)
    def lp_ratio(self,cost):
        cz=self.objective(cost); nz=self.nz
        c=np.concatenate([np.zeros(nz),np.zeros(1),-self.lev])
        A=sps.hstack([self.A[:,:nz],sps.csr_matrix((self.nrows,1)),self.A[:,nz:]]).tocsr()
        # z<=tau
        Z=sps.hstack([sps.identity(nz),-np.ones((nz,1)),sps.csr_matrix((nz,self.N-nz))]).tocsr()
        Aub=sps.vstack([A,Z]); bub=np.zeros(Aub.shape[0])
        Aeq=sps.csr_matrix(np.concatenate([cz[:nz],[0],np.zeros(self.N-nz)]).reshape(1,-1))
        res=linprog(c,A_ub=Aub,b_ub=bub,A_eq=Aeq,b_eq=[1],bounds=[(0,None)]*nz+[(0,1e3)]+[(0,1)]*(self.N-nz),method='highs')
        return -res.fun if res.status==0 else None

def reach_milp(model,cost_fn,lo=0.0,hi=0.45,tol=1e-3,tl=60,use_lp_start=True):
    """bisection on delta using the exact integer gain; returns (reach_lower_bound, reach_LP_upper)"""
    for _ in range(30):
        mid=(lo+hi)/2
        g,x,db=model.milp_gain(cost_fn(mid),tl)
        if g is not None and g>1e-7: lo=mid
        else: hi=mid
        if hi-lo<tol: break
    return lo
def reach_lp(model,cost_fn,lo=0.0,hi=0.45,tol=1e-3):
    for _ in range(30):
        mid=(lo+hi)/2
        v=model.lp_ratio(cost_fn(mid))
        if v is not None and v>1+1e-9: lo=mid
        else: hi=mid
        if hi-lo<tol: break
    return lo
