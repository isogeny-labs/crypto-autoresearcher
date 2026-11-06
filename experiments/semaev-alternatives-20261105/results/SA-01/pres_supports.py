# Supports (exponent tuples) of the generators of each presentation (generic a,b,xR,yR symbols)
import sympy as sp, itertools, json
x=sp.symbols('x'); a,b,xR,yR=sp.symbols('a b xR yR')
def poly_support(expr, vars_):
    P=sp.Poly(sp.expand(expr),*vars_)
    return sorted(P.monoms())
def S3(u,v,w): return (u-v)**2*w**2-2*((u+v)*(u*v+a)+2*b)*w+(u*v-a)**2-4*b*(u+v)
def norm_system(m):
    """returns (varnames, list of supports) for the Riemann-Roch norm system, full-size vars first then e_k"""
    e=sp.symbols(f'e1:{m+1}')
    f=x**3+a*x+b
    if m==2:
        al=sp.symbols('al'); full=[al]
        h_poly=al*x+(yR-al*xR); N=h_poly**2-f; kappa=-1
    elif m==3:
        a1,a2=sp.symbols('a1 a2'); full=[a1,a2]
        a0=yR-a1*xR-a2*xR**2
        hp=a0+a1*x+a2*x**2; N=hp**2-f; kappa=a2**2
    elif m==4:
        b0,a1,a2=sp.symbols('b0 a1 a2'); full=[b0,a1,a2]
        a0=(b0+xR)*yR-a1*xR-a2*xR**2
        hp=a0+a1*x+a2*x**2; N=hp**2-f*(b0+x)**2; kappa=-1
    prod=(x-xR)*sum(((-1)**k)*(e[k-1] if k>0 else 1)*x**(m-k) for k in range(m+1))
    D=sp.expand(N-kappa*prod)
    P=sp.Poly(D,x)
    eqs=[P.coeff_monomial(x**j) for j in range(m+1)]
    # note x^{m+1} coefficient vanishes by choice of kappa
    vars_=list(full)+list(e)
    sups=[]
    for q in eqs:
        q=sp.expand(q)
        if q==0: continue
        sups.append(poly_support(q,vars_))
    return vars_,sups
if __name__=="__main__":
    out={}
    for m in (2,3,4):
        v,s=norm_system(m)
        print(m,v,[len(q) for q in s])
        out[m]=dict(vars=[str(z) for z in v],sups=s)
    # chain S3 supports
    x1,x2,x3,u=sp.symbols('x1 x2 x3 u')
    out['S3_x1x2u']=poly_support(S3(x1,x2,u),[x1,x2,u])
    out['S3_ux3']=poly_support(S3(u,x3,xR),[u,x3])
    print(out['S3_x1x2u']); print(out['S3_ux3'])
    json.dump(out,open('pres_supports.json','w'))
