# Summation polynomials S_{m+1}(x1..xm, r) over Z for y^2=x^3+a x+b, via PARI resultants; returns support (exponent tuples) + coeffs.
import cypari2, itertools, json, sys
pari = cypari2.Pari(); pari.allocatemem(600*10**6)
A,B0,R0 = 3,5,7   # generic small integers
def S3(u,v,w):
    return f"(({u}-{v})^2*{w}^2-2*(({u}+{v})*({u}*{v}+{A})+2*{B0})*{w}+({u}*{v}-{A})^2-4*{B0}*({u}+{v}))"
def build(m):
    """S_{m+1}(x1..xm, R0) as pari poly in x1..xm"""
    if m==2: return pari(S3('x1','x2',R0))
    # S_{m+1}(x1..xm,r) = Res_u( S_3(x1,x2,u), S_m(u,x3..xm,r) )
    inner = pari(f"subst(subst({inner_expr(m-1)},'x1,u),'xx,0)") if False else None
def S(m, names, r):
    # recursive in pari string form: returns pari polynomial in given variable names
    if m==2:
        return pari(S3(names[0],names[1],r))
    u=f"u{m}"
    inner = S(m-1, [u]+names[2:], r)
    outer = pari(S3(names[0],names[1],u))
    return pari.polresultant(outer, inner, u)
def support(poly, vars_):
    # expand to dict
    res={}
    p=pari(poly)
    def rec(q, vs, ex):
        if not vs:
            res[tuple(ex)]=int(q); return
        v=vs[0]
        d=int(pari.poldegree(q,v)) if q!=0 else -1
        for e in range(d+1):
            c=pari.polcoef(q,e,v)
            if c!=0: rec(c, vs[1:], ex+[e])
    rec(p, vars_, [])
    return res
if __name__=="__main__":
    out={}
    for m in (2,3,4):
        names=[f"x{i}" for i in range(1,m+1)]
        P=S(m,names,R0)
        sp=support(P,names)
        out[m]=sorted(sp.keys())
        print(m,len(sp),"max exps",[max(e[i] for e in sp) for i in range(m)], "max total deg",max(sum(e) for e in sp))
    json.dump({str(k):v for k,v in out.items()},open("supports_S.json","w"))
