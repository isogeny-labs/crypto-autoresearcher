import sympy as sp, random, sys, json
from sympy import symbols, expand, Poly, discriminant, factor
x1,x2,X,e1,e2,a,b = symbols('x1 x2 X e1 e2 a b')
S3 = (x1-x2)**2*X**2 - 2*((x1+x2)*(x1*x2+a)+2*b)*X + (x1*x2-a)**2 - 4*b*(x1+x2)
# (1) symmetric form: substitute e1=x1+x2, e2=x1*x2
S3sym = expand(S3.subs({(x1-x2)**2: e1**2-4*e2}))
S3sym = expand(S3sym.subs(x1*x2, e2).subs(x1+x2, e1))
# brute: rewrite via resultant trick: express in e1,e2 by solving
from sympy import groebner
G = sp.groebner([S3sym], e1, e2, order='lex')
P = Poly(S3sym, e1, e2)
print("S3 in (e1,e2): total degree =", P.total_degree(), " monomials:", P.monoms())
# (2) discriminant in X equals 16 f(x1) f(x2)
f = lambda t: t**3 + a*t + b
d = discriminant(Poly(S3, X))
print("disc_X S3 == 16 f(x1) f(x2):", sp.simplify(d - 16*f(x1)*f(x2)) == 0)
# (3) numeric: secp256k1-like toy curve y^2=x^3+7 mod p; planted decomposition; integer value of S3
p = sp.nextprime(2**40)
A,B = 0,7
def on_curve(x):
    return sp.legendre_symbol((x**3+A*x+B)%p, p) == 1
def sqrtmod(n): return sp.sqrt_mod(n % p, p)
def add(P,Q):
    if P is None: return Q
    if Q is None: return P
    (xp,yp),(xq,yq)=P,Q
    if xp==xq and (yp+yq)%p==0: return None
    if P==Q: l = (3*xp*xp+A)*pow(2*yp,-1,p)%p
    else: l=(yq-yp)*pow(xq-xp,-1,p)%p
    xr=(l*l-xp-xq)%p; yr=(l*(xp-xr)-yp)%p
    return (xr,yr)
random.seed(1)
def smallpt(Bnd):
    while True:
        x=random.randrange(1,Bnd)
        if on_curve(x): return (x, sqrtmod(x**3+A*x+B))
rows=[]
for Bnd in [2**4,2**6,2**8,2**10,2**12,2**14]:
    P1=smallpt(Bnd); P2=smallpt(Bnd); R=add(P1,P2); Rm=add(P1,(P2[0],(-P2[1])%p))
    val = int(S3.subs({x1:P1[0],x2:P2[0],X:R[0],a:A,b:B}))
    assert val % p == 0
    # minimal polynomial over Z: S3(x1,x2,T) has roots x(P1+P2), x(P1-P2) mod p
    g = Poly(S3.subs({x1:P1[0],x2:P2[0],a:A,b:B}), X)
    c = [int(t) for t in g.all_coeffs()]
    r1 = g.eval(R[0]) % p; r2 = g.eval(Rm[0]) % p
    # product of the two roots as rational via Vieta, rational reconstruction check
    prod_mod = R[0]*Rm[0] % p
    num = (P1[0]*P2[0])**2 - 4*B*(P1[0]+P2[0]); den=(P1[0]-P2[0])**2
    ok = (num * pow(den,-1,p) - prod_mod) % p == 0
    rows.append(dict(B=Bnd, x1=P1[0], x2=P2[0], carry_bits=(abs(val)//p).bit_length(), coeff_bits=max(abs(t) for t in c).bit_length(), roots_ok=(r1==0 and r2==0), vieta_prod_ok=ok, p_bits=p.bit_length()))
for r in rows: print(r)
json.dump(rows, open('calib_rows.json','w'), indent=1)
