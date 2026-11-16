# (iii) Groebner generators at m=3: a1 eliminated linearly (gen 0 dropped), variables (a2,e1,e2,e3), a2 full size, e_k size p^{k delta}
import sys, json, time
from model import *
G=json.load(open('gb_iii_m3.json'))   # exps order (a1,a2,e1,e2,e3); first term of each = lex lead
sel=[int(z) for z in sys.argv[2].split(',')] if len(sys.argv)>2 and sys.argv[2]!='all' else list(range(1,len(G)))
t=int(sys.argv[1]); lo=float(sys.argv[3]) if len(sys.argv)>3 else 0.0; hi=float(sys.argv[4]) if len(sys.argv)>4 else 0.06
gens=[]
for i in sel:
    sup=[tuple(m[1:]) for m in G[i]]; gens.append((sup,sup[0]))
print('gens',sel,'leads',[g[1] for g in gens],flush=True)
cf=lambda dl:[1.0,dl,2*dl,3*dl]
t0=time.time(); M=Model(4,gens,t); print('built dim',M.nz,'N',M.N,round(time.time()-t0,1),flush=True)
v=M.lp_ratio(cf(1e-4)); print('LP ratio at delta=1e-4:',v,round(time.time()-t0,1),flush=True)
a,b=lo,hi
if v is not None and v>1:
    while b-a>4e-4:
        mid=(a+b)/2; v=M.lp_ratio(cf(mid)); print('  lp',round(mid,5),v,round(time.time()-t0,1),flush=True)
        if v is not None and v>1+1e-9: a=mid
        else: b=mid
print('RESULT iiiG m3 t',t,'LP reach',a,flush=True)
if len(sys.argv)>5 and sys.argv[5]=='milp' and a>0:
    tl=60; lo2=0.85*a; g,x,db=M.milp_gain(cf(lo2),tl)
    while (g is None or g<=1e-7) and lo2>1e-4:
        lo2*=0.85; g,x,db=M.milp_gain(cf(lo2),tl)
    hi2=a+0.0003
    while hi2-lo2>3e-4:
        mid=(lo2+hi2)/2; g,x,db=M.milp_gain(cf(mid),tl); print('  milp',round(mid,5),g,round(time.time()-t0,1),flush=True)
        if g is not None and g>1e-7: lo2=mid
        else: hi2=mid
    print('RESULT iiiG m3 t',t,'MILP lower',lo2,flush=True)
