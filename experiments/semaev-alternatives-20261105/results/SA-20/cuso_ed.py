import sys,time
from sage.all import PolynomialRing, QQ
from cuso.symbolic import SymbolicCoppersmithProblem, get_asymptotic_bounds
m=int(sys.argv[1]); k=int(sys.argv[2]); mode=sys.argv[3]  # mode: box | sub (box plus parity-lattice vertex set)
E3=lambda u,v,w:u**2*v**2*w**2-(u**2*v**2+u**2*w**2+v**2*w**2)+2*(u**2+v**2+w**2)-2*u*v*w-2
if m==2:
    R=PolynomialRing(QQ,"y1,y2"); y1,y2=R.gens(); f=E3(y1,y2,7); ys=[y1,y2]; d=2
else:
    P=PolynomialRing(QQ,"y1,y2,y3,u"); a,b,c,u=P.gens()
    r=E3(a,b,u).resultant(E3(c,7,u),u); R=PolynomialRing(QQ,"y1,y2,y3"); ys=list(R.gens()); f=R(r); d=4
import itertools
verts=[]
for e in itertools.product((0,1),repeat=m):
    mono=1
    for yi,ei in zip(ys,e): mono*=yi**(d*ei)
    verts.append(mono)
if mode=="sub" and m==2: verts=[1,ys[0]**2,ys[1]**2,ys[0]**2*ys[1]**2]  # same as box here
prob=SymbolicCoppersmithProblem([f],[1]*m,modulus_name="p")
t0=time.time()
dl,tau,cp=get_asymptotic_bounds(prob,[0.05]*m,verts,precompute_multiplicity=k,tshifts_to_include=[False]*m)
print("RESULT edwards m",m,"k_pre",k,"delta*",dl,float(dl),"terms",len(f.monomials()),round(time.time()-t0,1),"s",flush=True)
