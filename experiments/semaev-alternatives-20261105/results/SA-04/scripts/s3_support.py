import sympy as sp
x1,x2,x3,a,b=sp.symbols('x1 x2 x3 a b')
S3=(x1-x2)**2*x3**2-2*((x1+x2)*(x1*x2+a)+2*b)*x3+((x1*x2-a)**2-4*b*(x1+x2))
P=sp.Poly(sp.expand(S3.subs({a:0,b:7})),x1,x2,x3)
print(sorted(P.monoms()))
