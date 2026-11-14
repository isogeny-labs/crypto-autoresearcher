"""SA-15b solver 1: generic pair-table MITM on the frozen SA-15 instance set. Verification in Python (independent group law)."""
import json, hashlib, subprocess, sys, time
from sympy.ntheory import sqrt_mod
SRC="/home/user/semaev-runs/SA-15/instances.json"
WIT="/home/user/semaev-runs/SA-15/witnesses.json"
assert hashlib.sha256(open(SRC,'rb').read()).hexdigest()=="e9b681a6cd073f307ab434158bd18ab3c36d15c7f400ab7f0cb973c1f2958d62"
D=json.load(open(SRC)); W=json.load(open(WIT))
def add(P,Q,p):
    if P is None: return Q
    if Q is None: return P
    (x1,y1),(x2,y2)=P,Q
    if x1==x2 and (y1+y2)%p==0: return None
    l=(3*x1*x1)*pow(2*y1,-1,p)%p if P==Q else (y2-y1)*pow(x2-x1,-1,p)%p
    x3=(l*l-x1-x2)%p; return (x3,(l*(x1-x3)-y1)%p)
kbits=[int(a) for a in sys.argv[1].split(',')]; ninst=int(sys.argv[2]) if len(sys.argv)>2 else 100
out=[]
for g in D['groups']:
    if g['log2p'] not in kbits: continue
    p=int(g['p']); B=g['B']; pts=[]
    for x in range(1,B+1):
        r=(x**3+7)%p
        if pow(r,(p-1)//2,p)==1:
            y=int(sqrt_mod(r,p)); pts+= [(x,y),(x,p-y)]
    insts=g['instances'][:ninst]
    inp=f"{p} {len(pts)} {len(insts)}\n"+"\n".join(f"{x} {y}" for x,y in pts)+"\n"+"\n".join(f"{i['R']['x']} {i['R']['y']}" for i in insts)+"\n"
    t0=time.time()
    r=subprocess.run(["nice","-n","10","./pairtable"],input=inp,capture_output=True,text=True,timeout=3000)
    lines=r.stdout.strip().split("\n"); b=lines[0].split(); build_ops=int(b[1]); npairs=int(b[2]); build_s=float(b[3])
    res=[]; 
    for ln,inst in zip(lines[1:],insts):
        t=ln.split(); found=int(t[3]); scanned=int(t[5]); sec=float(t[7]); ok=False; planted=False; distinct=False
        if found:
            idx=list(map(int,t[8:12])); Q=[pts[i] for i in idx]
            R=None
            for q in Q: R=add(R,q,p)
            ok = R==(int(inst['R']['x']),int(inst['R']['y'])) and all(1<=q[0]<=B for q in Q)
            distinct = len({q[0] for q in Q})==4
            w=W['groups'][[gg['log2p'] for gg in D['groups']].index(g['log2p'])]['witnesses'] if 'groups' in W else None
            try:
                wi=[ww for ww in w if ww['id']==inst['id']][0]; planted = sorted(q[0] for q in Q)==sorted(int(pp['x']) for pp in wi['points'])
            except Exception: planted=None
        res.append(dict(id=inst['id'],found=found,verified=ok,distinct=distinct,planted=planted,scanned=scanned,sec=sec))
    nver=sum(r_['verified'] for r_ in res)
    N=int(g['N']); import math
    rho=math.sqrt(math.pi*N/4)
    mean_scan=sum(r_['scanned'] for r_ in res)/len(res)
    summ=dict(log2p=g['log2p'],p=p,B=B,n_signed_pts=len(pts),pair_table=npairs,build_ops=build_ops,build_sec=build_s,ninst=len(insts),recovered=nver,
              distinct_ok=sum(r_['distinct'] for r_ in res),planted_match=sum(bool(r_['planted']) for r_ in res),
              mean_scan_ops=mean_scan,mean_total_ops_single_shot=mean_scan+build_ops,mean_total_ops_amortized=mean_scan+build_ops/len(insts),
              rho_ops=rho,ratio_scan_over_rho=mean_scan/rho,ratio_single_over_rho=(mean_scan+build_ops)/rho,mean_sec_scan=sum(r_['sec'] for r_ in res)/len(res),
              B2=B*B,breakeven_p_1_10=p**0.1)
    print(json.dumps(summ),flush=True); out.append(dict(summary=summ,per_instance=res))
json.dump(out,open(f"pairtable_results_{'_'.join(map(str,kbits))}.json","w"))
