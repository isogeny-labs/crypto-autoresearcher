# Bivariate Coppersmith (Jochemsz-May style, LM=(0,0), sumset monomial set) with real LLL, plus resultant root extraction.
import itertools, time, math
from fpylll import IntegerMatrix, LLL
import cypari2
pari=cypari2.Pari(); pari.allocatemem(300*10**6)
def pmul(f,g,mod):
    r={}
    for a,ca in f.items():
        for b,cb in g.items():
            k=(a[0]+b[0],a[1]+b[1]); r[k]=(r.get(k,0)+ca*cb)%mod
    return r
_cache={}
def plan(supp,t):
    key=(tuple(sorted(supp)),t)
    if key in _cache: return _cache[key]
    M={(0,0)}
    for _ in range(t): M={(a[0]+b[0],a[1]+b[1]) for a in M for b in supp}
    K=[{(0,0)}]
    for k in range(1,t+1): K.append({(a[0]+b[0],a[1]+b[1]) for a in K[-1] for b in supp})
    rows=[]
    for mu in M:
        for k in range(t,-1,-1):
            if all((mu[0]+c[0],mu[1]+c[1]) in M for c in K[k]): rows.append((mu,k));break
    order=sorted(M,key=lambda m:(m[0]+m[1],m[0],m[1])); rows.sort(key=lambda r:(r[0][0]+r[0][1],r[0][0],r[0][1]))
    _cache[key]=(order,rows); return order,rows
def solve(f,p,Xb,Yb,t,maxpairs=4):
    """f: dict {(i,j):coef mod p} with f(0,0)!=0. find small integer roots |x|<=Xb,|y|<=Yb of f mod p. returns list of (x,y)."""
    c0=f[(0,0)]; inv=pow(c0,-1,p); f={k:v*inv%p for k,v in f.items()}
    order,rows=plan(frozenset(f),t); idx={m:i for i,m in enumerate(order)}; n=len(order)
    pw=[f_pow for f_pow in [{(0,0):1}]]
    for k in range(1,t+1): pw.append(pmul(pw[-1],f,p**t))
    M=IntegerMatrix(n,n)
    for r,(mu,k) in enumerate(rows):
        mod=p**(t-k)
        for m,c in pw[k].items():
            col=idx.get((m[0]+mu[0],m[1]+mu[1]))
            M[r,col]=(c*mod)%(p**t) if k>0 else (mod if m==(0,0) else 0)
        # k==0 row: p^t * monomial
    # scale columns
    sc=[Xb**m[0]*Yb**m[1] for m in order]
    for r in range(n):
        for c in range(n):
            if M[r,c]!=0: M[r,c]=M[r,c]*sc[c]
    LLL.reduction(M,delta=0.99)
    polys=[]
    for r in range(n):
        h=0
        for c in range(n):
            v=M[r,c]
            if v!=0:
                q=int(v)//sc[c]
                h+= q*pari('x')**order[c][0]*pari('y')**order[c][1]
        polys.append(h)
    sols=[]
    cnt=0
    for i,j in itertools.combinations(range(min(n,6)),2):
        if cnt>=maxpairs: break
        h1,h2=polys[i],polys[j]
        if h1==0 or h2==0: continue
        cnt+=1
        try: res=pari.polresultant(h1,h2,pari('y'))
        except Exception: continue
        if res==0: continue
        for r in pari.nfroots(None,res):
            x0=int(r)
            if abs(x0)>Xb: continue
            g=pari.gcd(pari.subst(h1,'x',x0),pari.subst(h2,'x',x0))
            if g==0 or pari.poldegree(g)<1: continue
            for ry in pari.nfroots(None,pari.subst(g,'x',0) if False else g):
                y0=int(ry)
                if abs(y0)<=Yb: sols.append((x0,y0))
        if sols: break
    return sols
