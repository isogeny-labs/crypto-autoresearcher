import sys,time
from cuso.symbolic import SymbolicCoppersmithProblem, get_asymptotic_bounds
from polys import vieta
V=vieta(); R=V.parent(); e1,e2,e3=R.gens(); print(len(V.monomials()),"terms")
k=int(sys.argv[1])
verts=[1,e1**4,e2**4,e3**4]
prob=SymbolicCoppersmithProblem([V],[1,2,3],modulus_name="p")
t0=time.time()
d,tau,cp=get_asymptotic_bounds(prob,[0.04,0.08,0.12],verts,precompute_multiplicity=k,tshifts_to_include=[False]*3)
print("RESULT (ii) Vieta k_pre",k,"delta*",d,float(d),round(time.time()-t0,1),flush=True)
