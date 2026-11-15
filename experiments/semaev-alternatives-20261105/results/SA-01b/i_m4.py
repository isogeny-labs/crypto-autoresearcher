import sys, time, json
from model import *
from run_ceilings import pres
t=int(sys.argv[1]); lo=float(sys.argv[2]); hi=float(sys.argv[3])
n,sups,cf,om=pres('i',4); gens=[(list(sups[0]),sups[0][0] if False else max(sups[0]))]
print('lead',gens[0][1])
t0=time.time(); M=Model(n,gens,t); print('built dim',M.nz,'N',M.N,'rows',M.nrows,round(time.time()-t0,1),flush=True)
a,b=lo,hi
while b-a>1e-4:
    mid=(a+b)/2; v=M.lp_ratio(cf(mid)); print('  lp',round(mid,5),v,round(time.time()-t0,1),flush=True)
    if v is not None and v>1+1e-9: a=mid
    else: b=mid
print('RESULT i m4 t',t,'LP reach (box: LP=MILP)',a,round(time.time()-t0,1),flush=True)
