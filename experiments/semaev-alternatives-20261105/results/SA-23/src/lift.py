#!/usr/bin/env python3
"""Gate B: msolve lift timing for one cell. usage: lift.py p d n_planted n_random timeout seed"""
import sys, json, time, random, subprocess, os, ast
sys.path.insert(0,os.path.dirname(__file__)); import mkms
MS="/usr/local/lib/python3.13/dist-packages/sage_wheels/bin/msolve"
p=int(sys.argv[1]); d=int(sys.argv[2]); npl=int(sys.argv[3]); nrd=int(sys.argv[4]); TO=float(sys.argv[5]); seed=int(sys.argv[6])
chi=d//6; DX=2*chi; DY=3*chi; U=DX+1+DY+1
rng=random.Random(seed)
secs=[]
for l in open(f"work/s_{p}_{d}.txt"):
    a,b=l.split("|"); X=list(map(int,a.split())); Y=list(map(int,b.split()))
    secs.append((tuple(X),tuple(Y))); secs.append((tuple(X),tuple((-y)%p for y in Y)))
cell=[json.loads(l) for l in open("results/cells.jsonl") if json.loads(l)["p"]==p and json.loads(l)["d"]==d][0]
t0=cell["fibres"][0]["t0"]; c=(pow(t0,d,p)+1)%p; ell=cell["fibres"][0]["ell"]; cof=cell["fibres"][0]["cofactor"]
def ev(poly,t): return sum(a*pow(t,i,p) for i,a in enumerate(poly))%p
def add(P,Q):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P;x2,y2=Q
    if x1==x2:
        if (y1+y2)%p==0: return None
        l=3*x1*x1*pow(2*y1,p-2,p)%p
    else: l=(y2-y1)*pow(x2-x1,p-2,p)%p
    x3=(l*l-x1-x2)%p; return (x3,(l*(x1-x3)-y1)%p)
def mul(k,P):
    R=None
    while k:
        if k&1: R=add(R,P)
        P=add(P,P); k>>=1
    return R
pts=[None]+[(x,y) for x in range(p) for y in range(p) if (y*y-x**3-c)%p==0]
assert len(pts)==p+1
tb=time.time(); table={}
for s in secs: table.setdefault((ev(s[0],t0),ev(s[1],t0)),[]).append(s)
t_table=time.time()-tb
Gset=sorted({mul(cof,P) for P in pts if mul(cof,P) is not None})
targets=[]
for i in range(npl):
    s=rng.choice(secs); targets.append(("planted",(ev(s[0],t0),ev(s[1],t0)),s))
for i in range(nrd): targets.append(("random_G",rng.choice(Gset),None))
def polmulmod(a,b):
    r=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): r[i+j]=(r[i+j]+x*y)%p
    return r
def check_section(X,Y,R):
    lhs=polmulmod(Y,Y); rhs=polmulmod(polmulmod(X,X),X); rhs=rhs+[0]*(len(lhs)-len(rhs)); rhs[0]=(rhs[0]+1)%p; rhs[d]=(rhs[d]+1)%p
    return lhs==rhs[:len(lhs)] and (ev(X,t0),ev(Y,t0))==R
def parse(txt):
    txt=txt.strip().rstrip(':'); return ast.literal_eval(txt)
log=open("results/gateB_calls.jsonl","a")
for k,(kind,R,planted) in enumerate(targets):
    fn=f"work/lift_{p}_{d}_{k}.in"; outf=fn[:-3]+".out"
    open(fn,"w").write(mkms.system(p,d,(t0,R[0],R[1])))
    tb=time.time(); status="ok"
    try:
        r=subprocess.run(["nice","-n","10",MS,"-v","0","-t","1","-f",fn,"-o",outf],capture_output=True,text=True,timeout=TO); rc=r.returncode
    except subprocess.TimeoutExpired:
        rc=-9; status="timeout"
    wall=time.time()-tb
    rec={"p":p,"d":d,"chi":chi,"U":U,"n_eq":6*chi+3,"t0":t0,"kind":kind,"R":list(R),"wall_s":round(wall,4),"msolve_rc":rc,"status":status,"load":open("/proc/loadavg").read().split()[0]}
    if status=="ok":
        try:
            res=parse(open(outf).read())
            if res==[-1]: rec.update(closure_solutions=0,fp_sections=0,verified=True)
            elif res[1][2]==-1: rec.update(closure_solutions="infinite",fp_sections=None,verified=False)
            else:
                char,nv,deg,names,lform,par=res[1]
                w=par[1][0][1]; den=par[1][1][1]; pars=par[1][2]
                def pe(cf,T): return sum(a*pow(T,i,p) for i,a in enumerate(cf))%p
                sols=set(); allok=True
                for T in range(p):
                    if pe(w,T)!=0: continue
                    dv=pe(den,T); 
                    if dv==0: allok=False; continue
                    vals=[(-pe(pp[0][1],T)*pow(dv,p-2,p))%p for pp in pars]+[T]
                    v=dict(zip(names,vals)); X=[v[f"x{i}"] for i in range(DX+1)]; Y=[v[f"y{i}"] for i in range(DY+1)]
                    if check_section(X,Y,R): sols.add((tuple(X),tuple(Y)))
                    else: allok=False
                rec.update(closure_solutions=deg,fp_sections=len(sols),verified=allok)
                if planted is not None: rec["planted_found"]=(planted in sols)
                # cross-check against enumeration table
                exp=set(table.get(R,[])); rec["enum_table_sections"]=len(exp); rec["matches_enumeration"]=(sols==exp)
        except Exception as e:
            rec.update(parse_error=repr(e)[:200],verified=False)
    log.write(json.dumps(rec)+"\n"); log.flush(); print(json.dumps(rec))
json.dump({"p":p,"d":d,"table_build_s":t_table,"S":len(secs)},open(f"work/lift_{p}_{d}_meta.json","w"))
