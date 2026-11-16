import sys, logging
from sage.all import PolynomialRing, QQ
from cuso.symbolic import SymbolicCoppersmithProblem, get_asymptotic_bounds
A,B,R0=3,5,7
R=PolynomialRing(QQ,"x1,x2")
x1,x2=R.gens()
S3=(x1-x2)**2*R0**2-2*((x1+x2)*(x1*x2+A)+2*B)*R0+(x1*x2-A)**2-4*B*(x1+x2)
def run(verts,k,bg=(0.1,0.1)):
    prob=SymbolicCoppersmithProblem([S3],[1,1],modulus_name="p")
    d,tau,cp=get_asymptotic_bounds(prob,list(bg),verts,precompute_multiplicity=k,tshifts_to_include=[False,False])
    return d
if __name__=="__main__":
    for k in (1,2):
        print(k, run([1,x1**2,x2**2,x1**2*x2**2],k), flush=True)
