"""SA-15b solver 4: SA-16 calibrated lattices (vieta_cvp, L2diag, and L3 as the uncalibrated reference).
(a) positive control on their native planted families (C1 degenerate conic, C2 R=[2]P1, G generic m=2) at B=floor(p^(1/5)), 40 trials;
(b) direct application to the 400 SA-15 m=4 instances (a 2-unknown solver returning any 2-decomposition of R; success needs a verified
    4-decomposition, so a 2-decomposition is reported separately)."""
import sys, json, random, time, math
sys.path.insert(0,"/home/user/semaev-runs/SA-16")
from common import *
from solvers import solve_vieta_cvp, solve_L2diag, solve_L3
SOL={'vieta_cvp':solve_vieta_cvp,'L2diag':solve_L2diag,'L3':solve_L3}
out=dict(control=[],m4=[])
rng=random.Random(15)
for bits in (40,56):
    p=nextprime_34(bits,rng); B=int(round(p**0.2))
    # make B exact floor(p^(1/5))
    while (B+1)**5<=p: B+=1
    while B**5>p: B-=1
    for fam in ('C1','C2','G'):
        insts=[]
        for t in range(40):
            if fam=='C1': insts.append(plant_degenerate_conic(p,B,rng=rng))
            elif fam=='C2': insts.append(plant_small_curve(p,B,rng=rng,diag=True))
            else: insts.append(plant_small_curve(p,B,rng=rng))
        for name,fn in SOL.items():
            succ=0; t0=time.process_time()
            for inst in insts:
                try: sols=fn(dict(inst))
                except Exception: sols=[]
                succ+=any(verify_decomp(a,b,inst['xr'],inst['a'],inst['b'],p,B) for a,b in sols)
            r=dict(bits=bits,p=p,B=B,family=fam,solver=name,trials=len(insts),succ=succ,sec_per_inst=(time.process_time()-t0)/len(insts)); print(json.dumps(r),flush=True); out['control'].append(r)
D=json.load(open("/home/user/semaev-runs/SA-15/instances.json"))
for g in D['groups']:
    p=int(g['p']); B=g['B']
    for name,fn in SOL.items():
        ncand=0; n2=0; t0=time.process_time()
        for i in g['instances']:
            inst=dict(p=p,a=0,b=7,B=B,xr=int(i['R']['x']))
            try: sols=fn(inst)
            except Exception: sols=[]
            ncand+=bool(sols); n2+=any(verify_decomp(a,b,inst['xr'],0,7,p,B) for a,b in sols)
        r=dict(log2p=g['log2p'],solver=name,instances=len(g['instances']),returned_candidates=ncand,verified_2_decomp=n2,verified_4_decomp=0,sec_per_inst=(time.process_time()-t0)/len(g['instances']))
        print(json.dumps(r),flush=True); out['m4'].append(r)
json.dump(out,open("sa16_solvers_results.json","w"),indent=1)
