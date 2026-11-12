import cmath
exec(open('jacobi_rank.py').read().split("for p in [13")[0])
def detail(p,L=12):
    g=prim_root(p); ind=[0]*p; x=1
    for e in range(p-1): ind[x]=e; x=x*g%p
    z=[cmath.exp(2j*cmath.pi*k/L) for k in range(L)]
    chi=lambda k,u: 0 if u%p==0 else z[(k*ind[u%p])%L]
    J2=lambda a,b: sum(chi(a,u)*chi(b,1-u) for u in range(2,p))
    res={}
    for b in (4,8):
        for k in range(1,12):
            if (6+b+k)%12==0: continue
            J=J2(6,b)*J2((6+b)%12,k)*chi(b,-1)*chi(k,-1)
            r=J/p; e=None
            for m in range(12):
                if abs(r-z[m])<1e-6: e=m
            res[(b,k)]=e
    return res
for p in [13,37,61,73,97,109,157,181,193,229,241,277]:
    r=detail(p); alg=[a for a,e in r.items() if e is not None]
    print(p, "n_root_of_unity_type=",len(alg), "exponents:", "".join('.' if r[a] is None else "%x"%r[a] for a in sorted(r)))
