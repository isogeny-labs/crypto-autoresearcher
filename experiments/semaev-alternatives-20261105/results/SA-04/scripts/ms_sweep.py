# msolve (F4, grevlex, -g 2, 1 thread) solving degree for the SA-04 systems; same builders as the Macaulay sweep (build.py).
# degree = max 'deg' column of msolve -v 2 F4 round table (same parse as SA-14).
import sys, json, random, time, re, subprocess, os, sympy as sp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import system, system_S, system_SV
MS="/usr/local/lib/python3.13/dist-packages/sage_wheels/bin/msolve"
SC=os.environ.get("SCR","/tmp/claude-0/-home-user-crypto-autoresearcher/0da9d9f6-3ae4-593e-a458-8600b2afd79e/scratchpad")
def names(m,base,ring,B):
    na=m-1
    if base in ('digit','V'):
        al=[f"a{k}" for k in range(2,m+1)]
        if base=='digit':
            s=B.bit_length()-1; return al+[f"b{i}_{j}" for i in range(m) for j in range(s)]
        return al+[f"x{i}" for i in range(m)]
    if base=='S':
        s=B.bit_length()-1; return [f"b{i}_{j}" for i in range(m) for j in range(s)]
    return [f"x{i}" for i in range(m)]
def pstr(g,vs):
    terms=[]
    for mon,c in g.items():
        if c==0: continue
        f=[str(c)]+[(v if e==1 else f"{v}^{e}") for v,e in zip(vs,mon) if e]
        terms.append("*".join(f))
    return "+".join(terms) if terms else "0"
def maxdeg(txt):
    d=[int(m.group(1)) for m in re.finditer(r"^\s*(\d+)\s+\d+\s+\d+\s+\d+ x \d+",txt,re.M)]
    return max(d) if d else None
def one(m,p,base,B,seed,null,tl):
    rng=random.Random(seed)
    for _try in range(50):
      try:
        if base=='SV': ring,gens,pt,meta=system_SV(m,p,B,rng)
        elif base=='S': ring,gens,pt,meta=system_S(m,p,B,rng)
        else: ring,gens,pt,meta=system(m,p,base,B,rng,null)
        break
      except Exception as e:  # singular alpha-interpolation matrix for this draw: redraw instance
        continue
    vs=names(m,base,ring,B); assert len(vs)==ring.n
    eqs=[pstr(g,vs) for g in gens]
    nfe=0
    for v,bb in zip(vs,ring.bm):
        if bb: eqs.append(f"{v}^2-{v}"); nfe+=1
    fn=f"{SC}/sa04_{m}_{base}_{B}_{seed}_{int(null)}.ms"
    open(fn,"w").write(",".join(vs)+"\n"+str(p)+"\n"+",\n".join(eqs)+"\n")
    t0=time.time()
    try:
        r=subprocess.run(["nice","-n","10",MS,"-g","2","-v","2","-t","1","-f",fn,"-o",fn+".out"],capture_output=True,text=True,timeout=tl)
        txt=r.stdout+r.stderr; deg=maxdeg(txt); st="ok" if r.returncode==0 else f"rc{r.returncode}"
        import resource; rss=round(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss/1024)  # max RSS of any msolve child so far (MB)
        mm=re.search(r"max. matrix data\s+(\d+) x (\d+)",txt); mx=[int(mm.group(1)),int(mm.group(2))] if mm else None
        # check: planted point satisfies GB? count GB size
        gbtxt=open(fn+".out").read() if os.path.exists(fn+".out") else ""
        ngb=gbtxt.count(",")+1 if gbtxt.strip() else None
        one_in_gb = gbtxt.strip().startswith("[1") or "[1]" in gbtxt.replace(" ","")
    except subprocess.TimeoutExpired:
        deg=None; st="timeout"; rss=None; mx=None; ngb=None; one_in_gb=None
    for f in (fn,fn+".out"):
        try: os.remove(f)
        except OSError: pass
    return dict(m=m,p=p,base=base,B=B,seed=seed,null=null,nvars=ring.n,neq=len(eqs),fdeg=deg,maxmat=mx,gb_len=ngb,
                trivial_gb=one_in_gb,status=st,rss_mb=rss,secs=round(time.time()-t0,2))
if __name__=="__main__":
    m=int(sys.argv[1]); base=sys.argv[2]; Bs=[int(x) for x in sys.argv[3].split(',')]; nseeds=int(sys.argv[4])
    null=sys.argv[5]=='null'; tl=float(sys.argv[6]); outf=sys.argv[7]; pm=float(sys.argv[8]) if len(sys.argv)>8 else 8
    for B in Bs:
        p=int(sp.nextprime(int(pm*B**m)))
        stop=False
        for seed in range(nseeds):
            r=one(m,p,base,B,seed,null,tl); print(json.dumps(r),flush=True); open(outf,"a").write(json.dumps(r)+"\n")
            if r['status']=='timeout': stop=True; break
        if stop: break
