import sys, json, time
from model import *
G=json.load(open('gb_iv_m3.json'))  # exps (x1,x2,x3,u); first term = lex lead
sel=[int(z) for z in sys.argv[2].split(',')]; t=int(sys.argv[1]); lo=float(sys.argv[3]); hi=float(sys.argv[4])
gens=[]
for i in sel:
    sup=[tuple(m) for m in G[i]]; gens.append((sup,sup[0]))
cf=lambda dl:[dl,dl,dl,1.0]
t0=time.time(); M=Model(4,gens,t); print('built dim',M.nz,'N',M.N,round(time.time()-t0,1),flush=True)
a,b=lo,hi
while b-a>4e-4:
    mid=(a+b)/2; v=M.lp_ratio(cf(mid))
    if v is not None and v>1+1e-9: a=mid
    else: b=mid
print('RESULT ivG sel',sel,'t',t,'LP reach',a,round(time.time()-t0,1),flush=True)
if len(sys.argv)>5 and sys.argv[5]=='milp' and a>0:
    tl=60; lo2=0.9*a; g,x,db=M.milp_gain(cf(lo2),tl)
    while (g is None or g<=1e-7) and lo2>1e-4:
        lo2*=0.85; g,x,db=M.milp_gain(cf(lo2),tl)
    hi2=a+0.0003
    while hi2-lo2>3e-4:
        mid=(lo2+hi2)/2; g,x,db=M.milp_gain(cf(mid),tl)
        if g is not None and g>1e-7: lo2=mid
        else: hi2=mid
    print('RESULT ivG sel',sel,'t',t,'MILP lower',lo2,round(time.time()-t0,1),flush=True)
