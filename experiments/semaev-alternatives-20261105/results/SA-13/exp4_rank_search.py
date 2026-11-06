import sympy as sp, itertools, random, json, time
from lib_w import rank_mod, P, degree_sequence, S3
x1,x2,T,t1,t2=sp.symbols('x1 x2 T t1 t2')
a,b=0,7
s3=sp.expand(S3(x1,x2,T,a,b))
G=[sp.Poly(s3,T).coeff_monomial(T**k) for k in range(3)]
# ---------- (A)
sA,qA=sp.symbols('sA qA')
out=[]
for (ea,eb,ec) in itertools.combinations(range(0,7),3):
    g=lambda t:(t**ea,t**eb,t**ec)
    v1,v2=g(t1),g(t2)
    cross=[v1[1]*v2[2]-v1[2]*v2[1], v1[2]*v2[0]-v1[0]*v2[2], v1[0]*v2[1]-v1[1]*v2[0]]
    comps=[]
    for c in cross:
        c=sp.cancel(sp.expand(c)/(t1-t2))
        # symmetric poly in t1,t2 -> poly in e1=t1+t2, e2=t1*t2
        sym=sp.polys.polyfuncs.symmetrize(sp.expand(c),[t1,t2],formal=True)
        expr=sym[0].subs({sym[2][0][0]:sA,sym[2][1][0]:qA}) if sym[2] else sym[0]
        comps.append(sp.expand(expr))
    # s=-G1/G2, q=G0/G2 ; clear denominators
    Ns=[]
    G0,G1,G2=G
    deg=max(sp.Poly(c,sA,qA).total_degree() for c in comps)
    vec=[sp.together(c.subs({sA:-G1/G2,qA:G0/G2},simultaneous=True)) for c in comps]
    vec=[sp.cancel(v*G2**deg) for v in vec]
    gg=sp.gcd_list([sp.expand(v) for v in vec if v!=0])
    vec=[sp.cancel(v/gg) for v in vec]
    vec=[sp.expand(v) for v in vec]
    nz=[v for v in vec if v!=0]
    n,seq=degree_sequence(nz,(x1,x2))
    out.append(dict(support=(ea,eb,ec),n=n,seq=seq,w=sum(seq)))
out.sort(key=lambda r:r['w'])
print("(A) rank-3 monomial supports, smallest weights:")
for r in out[:6]: print(r)
print("(A) number of supports",len(out),"min w",out[0]['w'])
json.dump(out,open('exp4A_rows.json','w'),indent=1)
# ---------- (B)
def pmul(f,g):
    r={}
    for m1,c1 in f.items():
        for m2,c2 in g.items():
            m=(m1[0]+m2[0],m1[1]+m2[1]); r[m]=r.get(m,0)+c1*c2
    return {m:c for m,c in r.items() if c}
Gd=[{m:int(c) for m,c in sp.Poly(g,x1,x2).terms()} for g in G]
def wstar(Qcoef):   # Qcoef: dict l -> poly-dict in X ; F_k=sum_l Q_l G_{k-l}
    L=max(Qcoef)+2
    Fk=[]
    for k in range(L+1):
        acc={}
        for l,Ql in Qcoef.items():
            j=k-l
            if 0<=j<=2:
                for m,c in pmul(Ql,Gd[j]).items(): acc[m]=acc.get(m,0)+c
        acc={m:c for m,c in acc.items() if c}
        if acc: Fk.append(acc)
    mons=sorted({m for f in Fk for m in f},key=lambda m:(sum(m),m)); idx={m:i for i,m in enumerate(mons)}
    rows=[]
    for f in Fk:
        r=[0]*len(mons)
        for m,c in f.items(): r[idx[m]]=c%P
        rows.append(r)
    n=rank_mod(rows,len(mons)); maxd=max(sum(m) for m in mons)
    prev=0; w=0
    for d in range(maxd+1):
        cols=[i for i,m in enumerate(mons) if sum(m)>d]
        rk=rank_mod([[r[i] for i in cols] for r in rows],len(cols)) if cols else 0
        c=n-rk; w+=d*(c-prev); prev=c
    return n,w
def monos(dx): return [(i,j) for i in range(dx+1) for j in range(dx+1-i)]
res=[]
t0=time.time()
for (dT,dX,mode) in [(1,1,'exh'),(2,1,'exh'),(1,2,'rand'),(3,1,'rand'),(2,2,'rand')]:
    ms=monos(dX); nvar=(dT+1)*len(ms)
    best=None; cnt=0
    if mode=='exh': it=itertools.product([-1,0,1],repeat=nvar)
    else: it=(tuple(random.choice([-2,-1,0,0,1,2]) for _ in range(nvar)) for _ in range(6000))
    hist={}
    for co in it:
        if not any(co): continue
        Q={}
        for l in range(dT+1):
            f={ms[i]:co[l*len(ms)+i] for i in range(len(ms)) if co[l*len(ms)+i]}
            if f: Q[l]=f
        n,w=wstar(Q)
        hist[w]=hist.get(w,0)+1; cnt+=1
        if best is None or w<best[0]: best=(w,n,co)
    res.append(dict(dT=dT,dX=dX,mode=mode,tested=cnt,min_w=best[0],rank_at_min=best[1],coef_at_min=best[2],lowest_w_hist=dict(sorted(hist.items())[:4])))
    print(res[-1],round(time.time()-t0),flush=True)
json.dump(res,open('exp4B_rows.json','w'),indent=1)
