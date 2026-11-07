# Brute-force the kernel lattice mod p^2 for the monomial form (1,T,T^2), T in [0,p) an INTEGER representative, p=10007.
# For each T: cnt(T) = #{ nonzero v=(c0,c1,c2), |c_j|<=W_j : c0+c1 T+c2 T^2 = 0 mod p^2 }.
# Compare with Gaussian heuristic (V-1)/p^2, van der Corput lower bound 2*floor(omega/p^2), trivial sparsity bound D(V-1) on sum_T cnt(T),
# and split T into the 'exact-relation' segment T<T* (sum_j W_j T^j < p^2 => relation holds over Z) and the rest.
import numpy as np, json, math, sys
p=10007; q=p*p; T=np.arange(p,dtype=np.int64); T2=T*T
rows=[]
def run(W):
    W0,W1,W2=W
    cnt=np.zeros(p,dtype=np.int64)
    for c2 in range(-W2,W2+1):
        for c1 in range(-W1,W1+1):
            r=(c1*T+c2*T2)%q
            c0=(-r)%q                       # c0 mod q
            ok=(c0<=W0)|(c0>=q-W0)
            if c1==0 and c2==0: ok&=(c0!=0)
            cnt+=ok
    return cnt
settings=[]
for t in [0.01,0.1,1.0,4.0,16.0]:
    for (W1,W2) in [(30,20),(300,200)]:
        W0=int(t*q/(8*W1*W2)); 
        if W0>=1: settings.append((W0,W1,W2))
for W in settings:
    cnt=run(W); V=(2*W[0]+1)*(2*W[1]+1)*(2*W[2]+1); om=W[0]*W[1]*W[2]
    Tstar=min((q/(3*W[2]))**0.5,(q/(3*W[1])),q/(3*W[0]) if W[0]>0 else p)   # sum_j W_j T^j < q  guaranteed
    Ts=int(min(p,max(0,math.floor(min((q/(3*W[2]))**0.5,q/(3*W[1]),1e18)))))
    # exact-relation segment: all T with W0+W1*T+W2*T^2 < q
    seg=(W[0]+W[1]*T+W[2]*T2)<q
    rest=~seg
    mean_all=cnt.mean(); mean_rest=cnt[rest].mean() if rest.any() else float('nan')
    gh=(V-1)/q
    rows.append(dict(W=W,V=V,omega_over_q=om/q,gauss_heur=gh,mean_all=float(mean_all),mean_rest=float(mean_rest),frac_seg=float(seg.mean()),
        mean_seg=float(cnt[seg].mean()) if seg.any() else None,
        frac_nonempty=float((cnt>0).mean()),frac_nonempty_rest=float((cnt[rest]>0).mean()) if rest.any() else None,
        frac_nonempty_pred=min(1.0,gh),min_cnt=int(cnt.min()),min_cnt_rest=int(cnt[rest].min()) if rest.any() else None,vdc_lower=2*math.floor(om/q),
        sum_cnt=int(cnt.sum()),sparsity_bound=2*(V-1),ratio_sum_to_bound=float(cnt.sum())/(2*(V-1)),
        ratio_rest_to_GH=float(mean_rest/gh) if rest.any() else None))
    r=rows[-1]
    print("W=%s om/q=%.3f GH=%.4f mean(all)=%.4f mean(T>=T*)=%.4f ratio_rest/GH=%.3f seg=%.3f nonempty=%.4f pred=%.4f nonempty_rest=%s min=%d vdc=%d sum/(D(V-1))=%.2e"%(
        W,r['omega_over_q'],gh,r['mean_all'],r['mean_rest'],r['ratio_rest_to_GH'],r['frac_seg'],r['frac_nonempty'],r['frac_nonempty_pred'],
        None if r['frac_nonempty_rest'] is None else round(r['frac_nonempty_rest'],4),r['min_cnt'],r['vdc_lower'],r['ratio_sum_to_bound']),flush=True)
json.dump(rows,open('exp3_rows.json','w'),indent=1)
