# check: top-degree part of S4(x1,x2,x3,xR) in (x1,x2,x3) is c*x1^4 x2^4 x3^4 (so digit top form = Q1 Q2 Q3 with Qk = deg-4 part of l_k^4)
import sympy as sp
x1,x2,x3,x4,u,a,b=sp.symbols('x1 x2 x3 x4 u a b')
def S3(X,Y,Z): return (X-Y)**2*Z**2-2*((X+Y)*(X*Y+a)+2*b)*Z+(X*Y-a)**2-4*b*(X+Y)
S4=sp.expand(sp.resultant(S3(x1,x2,u),S3(u,x3,x4),u))
P=sp.Poly(S4,x1,x2,x3)
print('total deg',P.total_degree(),'deg per var',[sp.degree(S4,v) for v in (x1,x2,x3)])
top=[ (m,c) for m,c in P.terms() if sum(m)==P.total_degree()]
print(top)
