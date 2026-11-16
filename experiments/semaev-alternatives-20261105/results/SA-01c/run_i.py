import sys, time, logging, itertools
from sage.all import QQ
from cuso.symbolic import SymbolicCoppersmithProblem, get_asymptotic_bounds
from polys import S4_x
f=S4_x(); R=f.parent(); x1,x2,x3=R.gens()
k=int(sys.argv[1]); a=int(sys.argv[2]) if len(sys.argv)>2 else 4
verts=[x1**(a*i)*x2**(a*j)*x3**(a*l) for i in (0,1) for j in (0,1) for l in (0,1)]
prob=SymbolicCoppersmithProblem([f],[1,1,1],modulus_name="p")
t0=time.time()
d,tau,cp=get_asymptotic_bounds(prob,[0.04]*3,verts,precompute_multiplicity=k,tshifts_to_include=[False]*3)
print("RESULT (i) box",a,"k_pre",k,"delta*",d,float(d),"1/24=",1/24,round(time.time()-t0,1),"s",flush=True)
