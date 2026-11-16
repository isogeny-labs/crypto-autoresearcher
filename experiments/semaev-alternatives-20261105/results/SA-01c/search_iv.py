import sys, json, time
from pres import *
from cuso.symbolic import SymbolicCoppersmithProblem, get_asymptotic_bounds
def evalc(k,cand,rels_extra=False):
    R,rels=chain(); x1,x2,x3,u=R.gens()
    base=[x1**(4*i)*x2**(4*j)*x3**(4*l) for i in (0,1) for j in (0,1) for l in (0,1)]
    ex=[x1**c[0]*x2**c[1]*x3**c[2]*u**c[3] for c in cand]
    prob=SymbolicCoppersmithProblem(rels,[[0,1],[0,1],[0,1],[1,0]],modulus_name="p")
    d,tau,cp=get_asymptotic_bounds(prob,[0.04,0.04,0.04,1.0],base+ex,precompute_multiplicity=k,tshifts_to_include=[False]*4)
    return float(d)
if __name__=="__main__":
    k=int(sys.argv[1]); cands=json.loads(sys.argv[2])
    for c in cands:
        t0=time.time()
        try: d=evalc(k,c)
        except Exception as e: d="ERR "+repr(e)[:50]
        print("CAND",c,"->",d,round(time.time()-t0,1),flush=True)
