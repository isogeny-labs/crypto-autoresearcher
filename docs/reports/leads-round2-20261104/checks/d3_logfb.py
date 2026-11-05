"""Derivation check for D3 (HD3): in log order, M is Toeplitz-plus-Hankel in the symbol c = 1_{+-log FB}, so the LOG
labelling's QTT rank should track the QTT rank of c. Prediction: (ii) small-x FB ~ random-log FB of equal size;
(iii) log-AP FB {+-[i]G : 1 <= i <= s} gives r_max <= 12; ratio r_max(M_LOG)/r_max(c) in [1, 4]."""
import json, sys, numpy as np
sys.path.insert(0, "/home/user/crypto-autoresearcher/docs/reports/holant-step-b-qtt-20261104")
from qtt_rank import pick_curves, add, qtt_ranks
def vec_qtt_rmax(v, L):
    N=2**L; w=np.zeros(N); w[:len(v)]=v; T=w.reshape([2]*L); r=[]
    for c in range(1,L):
        s=np.linalg.svd(T.reshape(2**c,-1),compute_uv=False); r.append(int((s>s[0]*max(2**c,2**(L-c))*1e-12).sum()) if s[0]>0 else 0)
    return max(r)
def M_log(n, logset):
    """E-block of M in orbit order j = min(k, n-k) - 1, j = 0..(n-3)/2, from the +-log set of FB."""
    m=(n-1)//2; S=set(logset)|{(-l)%n for l in logset}; M=np.zeros((m,m))
    for i in range(m):
        for j in range(m):
            P,Q=i+1,j+1
            M[i,j]=sum(1 for s in S if (Q-P)%n==s or (Q+P)%n==s)//1
    # each x in FB contributes once per (P,Q) pair as in transfer_matrix (sign pairs collapse): count distinct x(F)
    M2=np.zeros((m,m))
    xs={}
    for s in S: xs.setdefault(min(s,n-s),True)
    for i in range(m):
        for j in range(m):
            P,Q=i+1,j+1
            M2[i,j]=sum(1 for f in xs if (Q-P)%n in (f,n-f) or (Q+P)%n in (f,n-f))
    return M2
out=[]
rng=np.random.default_rng(7)
for L in (8,9,10):
    (p,a,b,E),=pick_curves(L,1,"D3-DERIVATION-CHECK")
    n=len(E); G=E[1]; R=None; logof={}
    for k in range(n): logof[R]=k; R=add(R,G,p,a)
    B=int(np.sqrt(p)); Ex=sorted({P[0] for P in E[1:]}); FBx=Ex[:B]
    sx=[logof[P] for P in E[1:] if P[0] in FBx]
    arms={"smallx":sorted({min(l,n-l) for l in sx})}
    arms["logAP"]=list(range(1,B+1))
    for d in range(5): arms[f"randlog{d}"]=sorted(rng.choice(np.arange(1,(n-1)//2+1),B,replace=False).tolist())
    m=(n-1)//2; Lm=int(np.ceil(np.log2(m)))
    for name,ls in arms.items():
        M=M_log(n,ls)
        c=np.zeros(n); 
        for l in ls: c[l]=1; c[n-l]=1
        rM=max(qtt_ranks(M,Lm,"interleaved")); rc=vec_qtt_rmax(c,int(np.ceil(np.log2(n))))
        out.append(dict(L=L,p=p,n=n,arm=name,fb=len(ls),rmax_M_LOG=rM,rmax_symbol=rc,ratio=round(rM/max(rc,1),2)))
        print(out[-1])
json.dump(out,open("d3.json","w"))
