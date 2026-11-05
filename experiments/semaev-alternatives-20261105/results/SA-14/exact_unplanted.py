"""Exact Macaulay degree of the INCONSISTENT (S nowhere zero on V^2) Kummer-tower Semaev system:
D = deg S + delta(1/S|_{V^2}) (Prop B), delta = max q-ary digit-sum of an exponent pair with nonzero coefficient
of 1/S in the group algebra F_p[Z/N x Z/N], N=q^t. Computed by 2D DFT over F_p."""
import numpy as np, random, json, sys
import kummer_sd as K
def digsum(k,q):
    s=0
    while k: s+=k%q; k//=q
    return s
def run(p,q,t,seed):
    N=q**t; rng=random.Random(seed)
    for _ in range(200):
        a,b,xr=K.instance(p,q,t,rng,planted=False)
        # generator of mu_N
        g=2
        while True:
            h=pow(g,(p-1)//N,p)
            if all(pow(h,N//r,p)!=1 for r in range(2,N+1) if N%r==0 and all(r%k for k in range(2,r))): break
            g+=1
        z=np.array([pow(h,i,p) for i in range(N)],dtype=np.int64)
        X1=z[:,None]; X2=z[None,:]
        S=((X1-X2)**2%p*(xr*xr%p)-2*xr*(((X1+X2)*((X1*X2+a)%p)+2*b)%p)+((X1*X2-a)**2)%p-4*b*((X1+X2)%p))%p
        if (S==0).any(): continue
        break
    else: return None
    # modular inverse elementwise
    inv=np.vectorize(lambda v:pow(int(v),p-2,p),otypes=[np.int64])(S)
    # coefficient c_{k1,k2} = N^-2 sum zeta1^{-k1} zeta2^{-k2} inv(zeta1,zeta2)
    hinv=pow(h,p-2,p)
    F=np.array([[pow(hinv,(i*k)%N,p) for i in range(N)] for k in range(N)],dtype=np.int64) # F[k,i]=h^{-ik}
    C=(F@inv)%p
    C=(C@F.T)%p
    Ninv=pow(N*N,p-2,p); C=C*Ninv%p
    nz=np.argwhere(C!=0)
    delta=max(digsum(int(i),q)+digsum(int(j),q) for i,j in nz)
    return dict(p=p,q=q,t=t,seed=seed,delta=delta,full=2*t*(q-1),D=4+delta,top_coeff_zero=bool(C[N-1,N-1]==0))
if __name__=="__main__":
    out=[]
    for t in range(1,9):
        for s in (1,2,3):
            r=run(12289,2,t,s); out.append(r); print(r,flush=True)
    for t in range(1,5):
        for s in (1,2,3):
            r=run(1459,3,t,s); out.append(r); print(r,flush=True)
    json.dump(out,open("out/exact_unplanted.json","w"))
