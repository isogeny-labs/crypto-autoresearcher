import sys,time,json,logging
from cuso.symbolic import SymbolicCoppersmithProblem, get_asymptotic_bounds
def run(rels,bounds,guess,verts,k,label=""):
    prob=SymbolicCoppersmithProblem(rels,bounds,modulus_name="p")
    t0=time.time()
    d,tau,cp=get_asymptotic_bounds(prob,guess,verts,precompute_multiplicity=k,tshifts_to_include=[False]*len(bounds))
    print("RESULT",label,"k_pre",k,"delta*",d,float(d),round(time.time()-t0,1),"s",flush=True)
    return d
