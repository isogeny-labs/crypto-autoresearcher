"""m=3 Kummer tower (q=2) with S_4 = Res_z(S_3(x1,x2,z),S_3(x3,xR,z)); and support-matched random null (any m)."""
import sys,re,time,random,subprocess,json,resource,os
import cypari2
import msolve_sd as M, kummer_sd as K
from drv import maxdeg
pari=cypari2.Pari(); pari.allocatemem(400*2**20)
RED=int(os.environ.get("RED","0"))
SC="/home/user/semaev-runs/SA-14b/work"; os.makedirs(SC,exist_ok=True)
def S3(x,y,z,a,b): return f"(({x}-{y})^2*{z}^2-2*(({x}+{y})*({x}*{y}+{a})+2*{b})*{z}+({x}*{y}-{a})^2-4*{b}*({x}+{y}))"
def S4poly(p,a,b):
    pari(f"S3(x,y,z)=(x-y)^2*z^2-2*((x+y)*(x*y+{a})+2*{b})*z+(x*y-{a})^2-4*{b}*(x+y)")
    return pari(f"lift(polresultant(S3(x1,x2,z),S3(x3,x4,z),z)*Mod(1,{p}))")
def inst3(p,q,t,rng,planted):
    h=None
    g=2
    while True:
        h=pow(g,(p-1)//q**t,p)
        if pow(h,q**(t-1),p)!=1: break
        g+=1
    V=[pow(h,i,p) for i in range(q**t)]
    for _ in range(1000):
        a=rng.randrange(p);b=rng.randrange(p)
        if (4*a**3+27*b*b)%p==0: continue
        good=[(x,K.sqrt_mod((x**3+a*x+b)%p,p)) for x in V if (x**3+a*x+b)%p!=0 and K.sqrt_mod((x**3+a*x+b)%p,p)]
        if len(good)<1: continue
        if planted:
            P=rng.choices(good,k=3); R=K.ec_add(K.ec_add(P[0],P[1],a,p),P[2],a,p)
            if R is None: continue
            return a,b,R[0]
        return a,b,rng.randrange(p)
    raise RuntimeError
def system_m(p,q,t,m,a,b,xr,null_seed=None):
    vs=[];eqs=[]
    for s in range(1,m+1):
        names=[f"x{s}"]+[f"w{s}_{j}" for j in range(1,t)]
        vs+=names
        for j in range(1,t): eqs.append(f"{names[j]}-{names[j-1]}^{q}")
        eqs.append(f"{names[t-1]}^{q}-1")
    import sympy as sp
    syms=sp.symbols(vs); loc=dict(zip(vs,syms))
    if m==2:
        Sx=sp.sympify(S3("x1","x2",str(xr),a,b).replace("^","**"),locals=loc)
    else:
        P=S4poly(p,a,b).subst("x4",xr) if False else S4poly(p,a,b)
        Sx=sp.sympify(str(P).replace("^","**").replace("x4",str(xr)),locals=loc)
    Sx=sp.Poly(sp.expand(Sx),*[loc[f"x{s}"] for s in range(1,m+1)],modulus=p)
    if RED:
        from collections import defaultdict
        acc=defaultdict(int)
        for mon,c in Sx.terms():
            key=[]
            for s_,e in enumerate(mon):
                e%= q**t
                ds=[]
                for j in range(t):
                    ds.append(e%q); e//=q
                key.append(tuple(ds))
            acc[tuple(key)]=(acc[tuple(key)]+int(c))%p
        gens=[[loc[f"x{s_}"]]+[loc[f"w{s_}_{j}"] for j in range(1,t)] for s_ in range(1,m+1)]
        expr=0
        for key,c in acc.items():
            if c: expr+=c*sp.prod([g**d for gs,ds in zip(gens,key) for g,d in zip(gs,ds)])
        Sx=sp.Poly(expr,*[loc[v] for v in vs],modulus=p)
        vars_=[loc[v] for v in vs]
    else:
        vars_=[loc[f"x{s}"] for s in range(1,m+1)]
    if null_seed is not None:
        r=random.Random(null_seed)
        Sx=sp.Poly(sum(r.randrange(1,p)*sp.prod([v**e for v,e in zip(vars_,mon)]) for mon in Sx.monoms()),*vars_,modulus=p)
    return vs,eqs+[str(Sx.as_expr()).replace("**","^")],Sx.total_degree(),len(Sx.monoms())
def one(p,q,t,m,seed,planted,null,tmo):
    rng=random.Random(seed); a,b,xr=inst3(p,q,t,rng,planted)
    vs,eqs,dS,nm=system_m(p,q,t,m,a,b,xr,null_seed=(seed+777) if null else None)
    fn=f"{SC}/in3_{m}_{t}_{seed}_{int(planted)}_{int(null)}"
    open(fn,"w").write(",".join(vs)+"\n"+str(p)+"\n"+",\n".join(eqs)+"\n")
    t0=time.time()
    r=subprocess.run(["nice","-n","10","timeout",str(tmo),M.MS,"-g","2","-v","2","-t","1","-f",fn,"-o",fn+".out"],capture_output=True,text=True,preexec_fn=lambda:resource.setrlimit(resource.RLIMIT_AS,(2200*2**20,)*2))
    txt=r.stdout+r.stderr
    mm=re.search(r"max. matrix data\s+(\d+) x (\d+)",txt)
    d=dict(p=p,q=q,t=t,m=m,seed=seed,planted=planted,null=null,red=RED,degS=dS,nmon=nm,fdeg=maxdeg(txt),maxrows=int(mm.group(1)) if mm else None,secs=round(time.time()-t0,1),ok=bool(mm))
    os.remove(fn)
    if os.path.exists(fn+".out"): os.remove(fn+".out")
    return d
if __name__=="__main__":
    p=12289;q=2
    cfg=sys.argv[1]  # "m,tlist,seeds,planted,null"
    m=int(sys.argv[1]); ts=eval(sys.argv[2]); seeds=eval(sys.argv[3]); planted=int(sys.argv[4]); null=int(sys.argv[5]); tmo=int(sys.argv[6])
    for t in ts:
        for s in seeds:
            print(json.dumps(one(p,q,t,m,s,bool(planted),bool(null),tmo)),flush=True)
