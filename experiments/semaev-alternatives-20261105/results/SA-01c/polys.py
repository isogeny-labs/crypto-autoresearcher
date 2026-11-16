from sage.all import PolynomialRing, QQ, ZZ
A,B,R0=3,5,7
def S3(a,b,c): return (a-b)**2*c**2-2*((a+b)*(a*b+A)+2*B)*c+(a*b-A)**2-4*B*(a+b)
def S4_x():
    P=PolynomialRing(QQ,"x1,x2,x3,u"); x1,x2,x3,u=P.gens()
    f1=S3(x1,x2,u); f2=S3(u,x3,R0)
    r=f1.resultant(f2,u)
    Q=PolynomialRing(QQ,"x1,x2,x3"); return Q(r)
if __name__=="__main__":
    f=S4_x(); print(len(f.monomials()), [max(m.degree(v) for m in f.monomials()) for v in f.parent().gens()], f.total_degree())

def vieta():
    """S_4 in e1,e2,e3 (elementary symmetric of x1,x2,x3), simplex-supported, R0=7"""
    from sage.all import matrix, vector
    f=S4_x(); Rx=f.parent(); x1,x2,x3=Rx.gens()
    e=[x1+x2+x3, x1*x2+x1*x3+x2*x3, x1*x2*x3]
    mons=[(a,b,c) for a in range(5) for b in range(5) for c in range(5) if a+b+c<=4]
    cols=[]
    allm={}
    imgs=[]
    for (a,b,c) in mons:
        g=e[0]**a*e[1]**b*e[2]**c; imgs.append(g)
        for m in g.monomials(): allm.setdefault(m,len(allm))
    for m in f.monomials(): allm.setdefault(m,len(allm))
    M=matrix(QQ,len(allm),len(mons))
    for j,g in enumerate(imgs):
        for m,c in zip(g.monomials(),g.coefficients()): M[allm[m],j]=c
    v=vector(QQ,len(allm))
    for m,c in zip(f.monomials(),f.coefficients()): v[allm[m]]=c
    s=M.solve_right(v)
    E=PolynomialRing(QQ,"e1,e2,e3"); E1,E2,E3=E.gens()
    return sum(c*E1**a*E2**b*E3**cc for c,(a,b,cc) in zip(s,mons))
