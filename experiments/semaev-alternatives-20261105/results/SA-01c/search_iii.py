import sys, json, time, itertools, multiprocessing as mp
from pres import *
from run_gen import run
import logging
def evalc(args):
    k,cand=args
    R,eqs=norm_system(); a1,a2,e1,e2,e3=R.gens()
    V=[1,e1**4,e2**4,e3**4]
    ex=[a1**c[0]*a2**c[1]*e1**c[2]*e2**c[3]*e3**c[4] for c in cand]
    bounds=[[1,0],[1,0],[0,1],[0,2],[0,3]]; guess=[1.0,1.0,0.04,0.08,0.12]
    from cuso.symbolic import SymbolicCoppersmithProblem, get_asymptotic_bounds
    prob=SymbolicCoppersmithProblem(eqs,bounds,modulus_name="p")
    d,tau,cp=get_asymptotic_bounds(prob,guess,V+ex,precompute_multiplicity=k,tshifts_to_include=[False]*5)
    return float(d)
if __name__=="__main__":
    k=int(sys.argv[1]); cands=json.loads(sys.argv[2])   # list of lists of exps
    out=[]
    for c in cands:
        t0=time.time()
        try: d=evalc((k,c))
        except Exception as e: d=str(e)[:60]
        print("CAND",c,"->",d,round(time.time()-t0,1),flush=True)
