# Determinant-method threshold: exact optimisation over down-closed monomial sets.
# Setting: F(x,y)=S_3(x,y,xR) mod p has bidegree (2,2), monic top term x^2y^2 (e2^2).
# Lattice of integer polys supported on M, vanishing mod p^t on C_R: rows p^{t-u(m)} F^{u(m)} x^.. y^..,
# u(m)=min(t, floor(min(mx,my)/2)).  Howgrave-Graham/Hadamard: a vector of l1-norm < p^t vanishes over Z.
# det = prod p^{t-u(m)} B^{mx+my}; need det^{1/s} < p^t  <=>  delta < sum u(m) / sum (mx+my)  (delta=log_p B)
import json, math
def best_delta(t, W=40, H=40, rect=False):
    def feasible(lam):
        # staircase DP, heights non-increasing in column index
        pref=[]
        for i in range(W):
            c=[0.0]
            for j in range(H):
                u=min(t,min(i,j)//2); c.append(c[-1]+u-lam*(i+j))
            pref.append(c)
        NEG=-1e18
        best=[0.0]+[NEG]*H  # before column 0: any height allowed -> use "inf" row
        prev=[0.0]*(H+1)    # prev[h]: best total with last height h; for col -1 treat all as allowed
        first=True; tot=0.0
        cur_best=0.0
        dp=[pref[0][h] for h in range(H+1)]
        res=max(dp)
        for i in range(1,W):
            # suffix max over h' >= h
            suf=[NEG]*(H+2)
            for h in range(H,-1,-1): suf[h]=max(suf[h+1],dp[h])
            dp=[pref[i][h]+suf[h] for h in range(H+1)]
            res=max(res,max(dp))
        return res
    lo,hi=0.0,0.5
    for _ in range(50):
        mid=(lo+hi)/2
        if feasible(mid)>1e-9: lo=mid
        else: hi=mid
    return lo
def rect_delta(t,N): # square [0..N]^2
    su=sum(min(t,min(i,j)//2) for i in range(N+1) for j in range(N+1))
    sw=sum(i+j for i in range(N+1) for j in range(N+1))
    return su/sw
out={'rect':{}, 'opt':{}}
print("Square [0..N]^2, delta_det(t,N)= sum u / sum w")
for t in (1,2,3,4,6,10):
    row={N:round(rect_delta(t,N),4) for N in (2,3,4,5,6,8,10,16,24,40,80)}
    out['rect'][t]=row; print(t,row, "best N<=80:",max((rect_delta(t,N),N) for N in range(2,81)))
print("Optimum over ALL staircase (down-closed) monomial sets in [0..W)x[0..H):")
for t,W in ((1,40),(2,40),(3,40),(4,40),(8,40),(100,40),(100,70)):
    d=best_delta(t,W,W); out['opt'][f"t={t},W={W}"]=d; print(f"t={t} W={W}: {d:.5f}")
json.dump(out,open('theory_out.json','w'),indent=1)
