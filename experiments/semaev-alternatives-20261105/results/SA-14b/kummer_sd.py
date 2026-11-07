"""Solving-degree measurement for Kummer-tower Semaev systems (m=2 summands, S_3) using Singular.
Encoding (own, see DEVIATIONS): V_t={x: x^(q^t)=1}; per summand variables x=w0,w1..w_{t-1};
w_j - w_{j-1}^q (j=1..t-1), w_{t-1}^q - 1 ; plus S_3(x1,x2,xR)=0 with xR fixed (planted or random).
solving degree sd = min D with lead(std with degBound D) containing lead(full dp GB)."""
import re, random, subprocess, sys, json, statistics, os, time
SING="/usr/local/lib/python3.13/dist-packages/sage_wheels/bin/Singular"
def inv(a,p): return pow(a,p-2,p)
def ec_add(P,Q,a,p):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P;x2,y2=Q
    if x1==x2 and (y1+y2)%p==0: return None
    l=(3*x1*x1+a)*inv(2*y1,p)%p if P==Q else (y2-y1)*inv(x2-x1,p)%p
    x3=(l*l-x1-x2)%p; return (x3,(l*(x1-x3)-y1)%p)
def sqrt_mod(n,p):
    n%=p
    if n==0: return 0
    if pow(n,(p-1)//2,p)!=1: return None
    # p=1 mod 4: Tonelli-Shanks
    s=0;Q=p-1
    while Q%2==0: Q//=2;s+=1
    z=2
    while pow(z,(p-1)//2,p)!=p-1: z+=1
    M=s;c=pow(z,Q,p);t=pow(n,Q,p);R=pow(n,(Q+1)//2,p)
    while t!=1:
        i=0;tt=t
        while tt!=1: tt=tt*tt%p;i+=1
        b=pow(c,1<<(M-i-1),p);M=i;c=b*b%p;t=t*c%p;R=R*b%p
    return R
def instance(p,q,t,rng,planted=True):
    # V = q^t-th roots of unity
    g=2
    while True:
        # find element of exact order q^t
        h=pow(g,(p-1)//q**t,p)
        if all(pow(h,q**t//r,p)!=1 for r in {f for f in range(2,q+1) if q%f==0 and all(f%k for k in range(2,f))}): break
        g+=1
    V=[pow(h,i,p) for i in range(q**t)]
    for _ in range(1000):
        a=rng.randrange(p);b=rng.randrange(p)
        if (4*a**3+27*b*b)%p==0: continue
        f=lambda x:(x**3+a*x+b)%p
        good=[(x,sqrt_mod(f(x),p)) for x in V if f(x)!=0 and sqrt_mod(f(x),p)]
        if len(good)<2: continue
        if planted:
            P1,P2=rng.sample(good,2)
            R=ec_add(P1,P2,a,p)
            if R is None: continue
            return a,b,R[0]
        return a,b,rng.randrange(p)
    raise RuntimeError
def singular_code(p,q,t,a,b,xr,null_seed=None):
    vs=[];eqs=[]
    for s in (1,2):
        names=[f"x{s}"]+[f"w{s}_{j}" for j in range(1,t)]
        vs+=names
        for j in range(1,t): eqs.append(f"{names[j]}-{names[j-1]}^{q}")
        eqs.append(f"{names[t-1]}^{q}-1")
    x1,x2="x1","x2"
    if null_seed is None:
        S=f"({x1}-{x2})^2*{xr}^2-2*(({x1}+{x2})*({x1}*{x2}+{a})+2*{b})*{xr}+({x1}*{x2}-{a})^2-4*{b}*({x1}+{x2})"
    else:
        r=random.Random(null_seed)
        mons=["x1^2*x2^2","x1^2*x2","x1*x2^2","x1^2","x2^2","x1*x2","x1","x2","1","x1^3*x2","x1*x2^3","x1^2","x1^3","x2^3"]
        S="+".join(f"{r.randrange(1,p)}*{m}" for m in set(mons))
    code=f"""ring r={p},({','.join(vs)}),dp;
ideal I={','.join(eqs+[S])};
option(prot); ideal G=std(I); option(noprot); ideal LG=lead(G);
int md=0; int i; for(i=1;i<=size(G);i++){{ if(deg(G[i])>md){{md=deg(G[i]);}} }}
int D; int sd=-1;
for(D=2;D<=60;D++){{ degBound=D; ideal H=std(I); degBound=0; ideal LH=std(lead(H)); if(size(reduce(LG,LH))==0){{sd=D;break;}} kill H; kill LH; }}
print("RESULT maxdeg="+string(md)+" sd="+string(sd)+" vdim="+string(vdim(G))+" nG="+string(size(G)));
quit;
"""
    return code
def run(p,q,t,seed,planted=True,null=False,timeout=120):
    rng=random.Random(seed)
    a,b,xr=instance(p,q,t,rng,planted)
    code=singular_code(p,q,t,a,b,xr,null_seed=seed if null else None)
    t0=time.time()
    try:
        out=subprocess.run([SING,"-q"],input=code,capture_output=True,text=True,timeout=timeout).stdout
        protdeg=max([int(x) for x in re.findall(r"\((\d+)\)",out)] or [0])
    except subprocess.TimeoutExpired:
        return dict(p=p,q=q,t=t,seed=seed,planted=planted,null=null,status="timeout")
    line=[l for l in out.splitlines() if l.startswith("RESULT")]
    if not line: return dict(p=p,q=q,t=t,seed=seed,status="err",out=out[-300:])
    d=dict(kv.split("=") for kv in line[0].split()[1:])
    return dict(p=p,q=q,t=t,seed=seed,planted=planted,null=null,status="ok",protdeg=protdeg,secs=round(time.time()-t0,2),**{k:int(v) for k,v in d.items()})
if __name__=="__main__":
    p,q,t,seed=map(int,sys.argv[1:5]); print(run(p,q,t,seed,planted=True))
