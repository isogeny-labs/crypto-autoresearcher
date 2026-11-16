import sympy as sp, json, time
p=1000003; A,B=3,5; xr=7
x1,x2,x3,u=sp.symbols('x1 x2 x3 u')
def S3(a,b,c): return sp.expand((a-b)**2*c**2-2*((a+b)*(a*b+A)+2*B)*c+(a*b-A)**2-4*B*(a+b))
f1=S3(x1,x2,u); f2=S3(u,x3,xr)
V=(u,x3,x2,x1)
t0=time.time(); G=sp.groebner([f1,f2],*V,modulus=p,order='lex'); print('gb time',time.time()-t0)
out=[]
for g in G.exprs:
    P=sp.Poly(g,*V,modulus=p); sup=[list(m) for m,c in P.terms()]
    print(len(sup),'terms; vars',[str(v) for v in V if g.has(v)],'lead',sup[0]); out.append(sup)
perm=[3,2,1,0]  # to (x1,x2,x3,u)
out=[[[m[i] for i in perm] for m in s] for s in out]
json.dump(out,open('gb_iv_m3.json','w'))
