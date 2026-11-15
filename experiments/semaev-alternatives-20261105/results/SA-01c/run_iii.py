import sys
from pres import *
from run_gen import run
R,eqs=norm_system(); a1,a2,e1,e2,e3=R.gens()
print([ (len(e.monomials()), e.degrees()) for e in eqs])
k=int(sys.argv[1]); mode=sys.argv[2]
bounds=[[1,0],[1,0],[0,1],[0,2],[0,3]]; guess=[1.0,1.0,0.04,0.08,0.12]
V=[1,e1**4,e2**4,e3**4]
if mode=="vieta": verts=V
elif mode.startswith("a2"):
    m=int(mode[2:]); verts=V+[a2**m]+[a2**m*e1**4,a2**m*e2**4,a2**m*e3**4]
elif mode=="a2e":  # a2^m with smaller e extents
    verts=V+[a2]
run(eqs,bounds,guess,verts,k,"iii "+mode)
