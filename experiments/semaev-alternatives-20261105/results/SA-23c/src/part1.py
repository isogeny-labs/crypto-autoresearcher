import sys,json,time
sys.path.insert(0,'/home/user/semaev-runs/SA-23c/src')
import jac
from sympy import primerange
lo,hi,out=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
f=open(out,'a')
for p in primerange(lo,hi):
    if p%12==1: f.write(json.dumps(jac.analyse(p))+"\n"); f.flush()
