import sympy as sp, json
x1,x2,x3,X,T=sp.symbols('x1 x2 x3 X T')
a=b=1
def S3(u,v,w): return sp.expand((u-v)**2*w**2-2*((u+v)*(u*v+a)+2*b)*w+(u*v-a)**2-4*b*(u+v))
r=sp.resultant(S3(x1,x2,T),S3(x3,X,T),T)
P=sp.Poly(sp.expand(r),x1,x2,x3,X)
print(len(P.terms()), P.degree_list())
# top coefficient of x1^4 x2^4 x3^4
d={m:int(c) for m,c in P.terms()}
print({m:c for m,c in d.items() if m[:3]==(4,4,4)})
json.dump([[list(m),c] for m,c in d.items()],open('s4_a1_b1.json','w'))
