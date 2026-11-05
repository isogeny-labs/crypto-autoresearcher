# Is the affine curve Cbar_p : S_3(x,y,r)=0 over F_p smooth (so Spec Z[x,y,t]/(pt-f) is smooth over Z and normal)?
# Test by Groebner basis of (f, f_x, f_y) over F_p: smooth iff it is the unit ideal (no singular affine point over F_p-bar).
import sympy as sp, random, json
from planted import S3_dict
x,y=sp.symbols('x y'); out=[]
for bits in (40,48,56):
    p=int(sp.nextprime(2**bits)); rng=random.Random(bits); sing=0; N=60
    for _ in range(N):
        while True:
            x1=rng.randrange(1,300);x2=rng.randrange(1,300)
            if x1!=x2 and all(pow((t**3+7)%p,(p-1)//2,p)==1 for t in (x1,x2)):break
        ys=[int(sp.sqrt_mod(t**3+7,p)) for t in (x1,x2)]
        l=(ys[1]-ys[0])*pow(x2-x1,-1,p)%p; r=(l*l-x1-x2)%p
        f=sum(c*x**i*y**j for (i,j),c in S3_dict(0,7,r).items())
        G=sp.groebner([f,sp.diff(f,x),sp.diff(f,y)],x,y,modulus=p,order='grevlex')
        if list(G.exprs)!=[1]: sing+=1
    out.append(dict(bits=bits,instances=N,singular=sing)); print(out[-1],flush=True)
json.dump(out,open("smooth_check.json","w"),indent=1)
