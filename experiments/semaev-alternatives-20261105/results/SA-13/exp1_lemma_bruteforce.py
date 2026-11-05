# Exact brute-force check of Theorem 1 (root-counting bound) and of the van der Corput list-size lower bound.
# Query class: n=3, one congruence c0 + c1 T + c2 T^2 = 0 mod p, weights (W0,W1,W2), D=2.
import numpy as np, sympy as sp, json, math
def box_vectors(W):
    W0,W1,W2=W
    c2=np.arange(-W2,W2+1); c1=np.arange(-W1,W1+1); c0=np.arange(-W0,W0+1)
    return c0,c1,c2
def exact_counts_small(p,W):
    """for every T in F_p count nonzero box vectors with c0+c1 T+c2 T^2=0 mod p. Returns array len p."""
    W0,W1,W2=W
    cnt=np.zeros(p,dtype=np.int64)
    T=np.arange(p,dtype=np.int64)
    T2=(T*T)%p
    nvec=0
    for c2 in range(-W2,W2+1):
        for c1 in range(-W1,W1+1):
            base=(c1*T+c2*T2)%p          # need c0 = -base mod p, with |c0|<=W0
            c0=(-base)%p
            # candidates c0 in [0,W0] or c0-p in [-W0,-1]
            ok=(c0<=W0)|(c0>=p-W0)
            if c2==0 and c1==0:
                # c0 = 0 mod p only if c0=0 (zero vector) since W0<p/2 ; exclude zero vector
                ok&=~(c0==0)
            cnt+=ok
    return cnt
rows=[]
p=100003
for W in [(6,4,3),(12,8,5),(24,12,8),(40,20,12),(80,40,20),(100,60,40),(200,100,60)]:
    cnt=exact_counts_small(p,W)
    V=(2*W[0]+1)*(2*W[1]+1)*(2*W[2]+1)
    frac=float(np.mean(cnt>0))
    tot=int(cnt.sum())            # sum over T of nonzero box vectors = sum_v #roots(v)
    bound_frac=2*(V-1)/p          # D*(V-1)/p with D=2
    vdc=2*math.floor(W[0]*W[1]*W[2]/p)  # van der Corput lower bound on nonzero vectors for every T
    rows.append(dict(p=p,W=W,V=V,frac_nonempty=frac,thm1_bound=min(1,bound_frac),
                     mean_count=tot/p,V_over_p=(V-1)/p,min_count=int(cnt.min()),vdc_lower=vdc,
                     holds=bool((frac<=bound_frac+1e-12) and cnt.min()>=vdc)))
    print(rows[-1])
json.dump(rows,open('exp1_rows.json','w'),indent=1)
# r=2 slack demo: n=4, two independent congruences, D=3. Sum_T #box vectors with both congruences, vs D*(#v)
def r2(p,W):
    T=np.arange(p,dtype=np.int64); pw=[np.ones(p,dtype=np.int64),T%p,(T*T)%p,(T*T%p)*T%p]
    cnt=np.zeros(p,dtype=np.int64); nv=0
    import itertools
    for v in itertools.product(*[range(-w,w+1) for w in W]):
        if not any(v): continue
        nv+=1
        e1=(v[0]*pw[0]+v[1]*pw[1]+v[2]*pw[2]+v[3]*pw[3])%p
        e2=(v[0]*pw[1]+2*v[1]*pw[2]+3*v[2]*pw[3]+5*v[3]*pw[0])%p   # second congruence, independent polynomial family
        cnt+=((e1==0)&(e2==0))
    return int(cnt.sum()),nv
p2=20011
for W in [(3,3,3,3),(5,5,5,5)]:
    s,nv=r2(p2,W)
    print("r=2:",dict(p=p2,W=W,sum_roots=s,n_vectors=nv,D_times_nv=3*nv,ratio=s/(3*nv),expected_ratio_heur=1/p2))
