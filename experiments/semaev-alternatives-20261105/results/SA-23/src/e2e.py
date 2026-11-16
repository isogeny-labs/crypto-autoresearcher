#!/usr/bin/env python3
"""Protocol step 8: DLs in G by r+2 lifts (msolve) on one cell; verify [k]G0=Q; compare with matched rho.
usage: e2e.py p d nDL seed timeout"""
import sys, json, time, random, subprocess, os, ast, math, statistics
from fractions import Fraction
import sympy
sys.path.insert(0,os.path.dirname(__file__)); import mkms
MS="/usr/local/lib/python3.13/dist-packages/sage_wheels/bin/msolve"
p=int(sys.argv[1]); d=int(sys.argv[2]); nDL=int(sys.argv[3]); seed=int(sys.argv[4]); TO=float(sys.argv[5])
rng=random.Random(seed); chi=d//6; DX=2*chi; DY=3*chi
cell=[json.loads(l) for l in open("results/cells.jsonl") if json.loads(l)["p"]==p and json.loads(l)["d"]==d][0]
t0=cell["fibres"][0]["t0"]; ell=cell["fibres"][0]["ell"]; cof=cell["fibres"][0]["cofactor"]; c=(pow(t0,d,p)+1)%p
assert cof%ell!=0
secs=[]
for l in open(f"work/s_{p}_{d}.txt"):
    a,b=l.split("|"); X=tuple(map(int,a.split())); Y=tuple(map(int,b.split()))
    secs.append((X,Y)); secs.append((X,tuple((-y)%p for y in Y)))
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
pts=[(x,y) for x in range(p) for y in range(p) if (y*y-x**3-c)%p==0]
Gpts=[q for q in {mul(cof,P) for P in pts} if q is not None]
G0=rng.choice(Gpts); assert mul(ell,G0) is None
# --- lattice machinery
def trim(a):
    a=list(a)
    while a and a[-1]%p==0: a.pop()
    return a
def sub(a,b):
    n=max(len(a),len(b)); return trim([((a[i] if i<len(a) else 0)-(b[i] if i<len(b) else 0))%p for i in range(n)])
def pmod(a,b):
    a=list(a); inv=pow(b[-1],p-2,p)
    while len(a)>=len(b):
        cc=a[-1]*inv%p; sh=len(a)-len(b)
        for i in range(len(b)): a[sh+i]=(a[sh+i]-cc*b[i])%p
        a=trim(a)
        if not a: break
    return a
def gdeg(a,b):
    while b: a,b=b,pmod(a,b)
    return len(a)-1
def inter(P,Q):
    dx=sub(P[0],Q[0]); dy=sub(P[1],Q[1])
    if not dx and not dy: return None
    aff=gdeg(dx,dy) if (dx and dy) else (len(dx)-1 if dx else len(dy)-1)
    ox=2*chi-(len(dx)-1) if dx else 10**9; oy=3*chi-(len(dy)-1) if dy else 10**9
    return aff+min(ox,oy)
def pair(P,Q): return 2*chi if P==Q else chi-inter(P,Q)
# greedy independent basis (exact, Fractions via sympy rank)
basis=[]; M=None
for s in secs:
    cand=basis+[s]
    Gm=sympy.Matrix([[pair(a,b) for b in cand] for a in cand])
    if Gm.rank()==len(cand): basis=cand
Gb=sympy.Matrix([[pair(a,b) for b in basis] for a in basis]); Gbi=Gb.inv(); r=len(basis)
def vec(s): return Gbi*sympy.Matrix([pair(s,b) for b in basis])
# --- lift
def msolve_lift(R):
    fn=f"work/e2e_{p}_{d}.in"; outf=fn[:-3]+".out"
    open(fn,"w").write(mkms.system(p,d,(t0,R[0],R[1])))
    tb=time.time()
    try: rr=subprocess.run(["nice","-n","10",MS,"-v","0","-t","1","-f",fn,"-o",outf],capture_output=True,text=True,timeout=TO); rc=rr.returncode
    except subprocess.TimeoutExpired: return [],time.time()-tb,-9
    wall=time.time()-tb
    res=ast.literal_eval(open(outf).read().strip().rstrip(':'))
    if res==[-1]: return [],wall,rc
    char,nv,deg,names,lform,par=res[1]
    w=par[1][0][1]; den=par[1][1][1]; pars=par[1][2]
    pe=lambda cf,T: sum(a*pow(T,i,p) for i,a in enumerate(cf))%p
    out=[]
    for T in range(p):
        if pe(w,T): continue
        dv=pe(den,T)
        if dv==0: continue
        vals=[(-pe(pp[0][1],T)*pow(dv,p-2,p))%p for pp in pars]+[T]; v=dict(zip(names,vals))
        X=tuple(v[f"x{i}"] for i in range(DX+1)); Y=tuple(v[f"y{i}"] for i in range(DY+1))
        # verify surface and point
        lhs=[0]*(2*DY+1)
        for i,a in enumerate(Y):
            for j,b in enumerate(Y): lhs[i+j]=(lhs[i+j]+a*b)%p
        x2=[0]*(2*DX+1)
        for i,a in enumerate(X):
            for j,b in enumerate(X): x2[i+j]=(x2[i+j]+a*b)%p
        x3=[0]*(3*DX+1)
        for i,a in enumerate(x2):
            for j,b in enumerate(X): x3[i+j]=(x3[i+j]+a*b)%p
        x3[0]=(x3[0]+1)%p; x3[d]=(x3[d]+1)%p
        if lhs==x3 and (ev(X,t0),ev(Y,t0))==R: out.append((X,Y))
    return out,wall,rc
# --- matched rho in G (prime order ell), Python single thread
def rho(Q,Gg):
    while True:
        a0=rng.randrange(ell); b0=rng.randrange(ell); Xp=add(mul(a0,Gg),mul(b0,Q)); a,b=a0,b0
        def step(Xp,a,b):
            h=(Xp[0] if Xp else 0)%3
            if h==0: return add(Xp,Gg),(a+1)%ell,b
            if h==1: return add(Xp,Xp),(2*a)%ell,(2*b)%ell
            return add(Xp,Q),a,(b+1)%ell
        x1,a1,b1=Xp,a,b; x2,a2,b2=Xp,a,b
        for _ in range(4*ell+50):
            x1,a1,b1=step(x1,a1,b1); x2,a2,b2=step(*step(x2,a2,b2))
            if x1==x2:
                db=(b1-b2)%ell
                if db==0: break
                k=((a2-a1)*pow(db,-1,ell))%ell
                if mul(k,Gg)==Q: return k
                break
def tm(f,reps=1):
    ts=[]
    for _ in range(reps):
        tb=time.perf_counter(); out=f(); ts.append(time.perf_counter()-tb)
    return out,statistics.median(ts)
# --- precompute relations: r+2 lifts of random multiples of G0
rel=[]; calls=[]; tpre0=time.time(); tries=0
while len(rel)<r+2 and tries<40*(r+2):
    tries+=1; a=rng.randrange(1,ell); R=mul(a,G0); ss,wall,rc=msolve_lift(R); calls.append({"kind":"relation","a":a,"R":R,"wall":wall,"rc":rc,"nsec":len(ss)})
    if ss: rel.append((a,ss[0]))
t_pre=time.time()-tpre0
V=sympy.Matrix.hstack(*[vec(s) for a,s in rel]) if rel else None
results=[]
for inst in range(nDL):
    k=rng.randrange(1,ell); Q=mul(k,G0); tb=time.time(); got=None; status="fail"
    ntry=0
    for ntry in range(1,60):
        sh=rng.randrange(ell); Qs=add(Q,mul(sh,G0))   # randomised target Q+[sh]G0 (liftable with prob = coverage)
        if Qs is None: continue
        ss,wall,rc=msolve_lift(Qs); calls.append({"kind":"target","R":Qs,"wall":wall,"rc":rc,"nsec":len(ss)})
        if not ss: continue
        vq=vec(ss[0])
        # solve V m = vq over Q using r independent columns
        m=sympy.symbols(f"m0:{len(rel)}"); sol=sympy.linsolve((V,vq),*m)
        if not sol: continue
        sol=list(sol)[0]; sol=[x.subs({s_:0 for s_ in m}) for x in sol]   # free vars -> 0
        ok=all(math.gcd(int(sympy.denom(x)),ell)==1 for x in sol)
        if not ok: continue
        ksh=sum((int(sympy.numer(x))*pow(int(sympy.denom(x)),-1,ell)*rel[j][0]) for j,x in enumerate(sol))%ell
        got=(ksh-sh)%ell; status="ok" if mul(got,G0)==Q else "wrong"; break
    t_inst=time.time()-tb
    (_,t_rho)=tm(lambda: rho(Q,G0),reps=51)
    results.append({"k":k,"k_found":got,"verified":(got==k),"status":status,"lift_calls_for_Q":ntry,"wall_target_s":t_inst,"wall_with_precompute_share_s":t_inst+t_pre/nDL,"rho_median_s":t_rho})
out={"p":p,"d":d,"chi":chi,"r":r,"ell":ell,"cofactor":cof,"t0":t0,"G0":G0,"relation_lifts":len(rel),"relation_calls":tries,"precompute_wall_s":t_pre,
     "dl":results,"msolve_calls":calls,"host_load":open('/proc/loadavg').read().split()[0]}
json.dump(out,open(f"results/e2e_{p}_{d}.json","w"),indent=1)
print(json.dumps({k:v for k,v in out.items() if k!="msolve_calls"}))
