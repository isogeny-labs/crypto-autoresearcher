import sys,re,time,random,subprocess,json,resource
import msolve_sd as M, kummer_sd as K
SC="/home/user/semaev-runs/SA-14b/work"
import os; os.makedirs(SC,exist_ok=True)
def maxdeg(txt):
    d=[int(m.group(1)) for m in re.finditer(r"^\s*(\d+)\s+\d+\s+\d+\s+\d+ x \d+",txt,re.M)]
    return max(d) if d else None
def one(p,q,t,seed,planted,tmo):
    rng=random.Random(seed); a,b,xr=K.instance(p,q,t,rng,planted)
    vs,eqs=M.system(p,q,t,a,b,xr)
    fn=f"{SC}/in_{q}_{t}_{seed}_{int(planted)}"
    open(fn,"w").write(",".join(vs)+"\n"+str(p)+"\n"+",\n".join(eqs)+"\n")
    t0=time.time()
    try:
        r=subprocess.run(["nice","-n","10","timeout",str(tmo),M.MS,"-g","2","-v","2","-t","1","-f",fn,"-o",fn+".out"],capture_output=True,text=True,preexec_fn=lambda:resource.setrlimit(resource.RLIMIT_AS,(2200*2**20,)*2))
        txt=r.stdout+r.stderr
    except Exception as e: txt=str(e)
    m=re.search(r"max. matrix data\s+(\d+) x (\d+)",txt)
    d=dict(p=p,q=q,t=t,seed=seed,planted=planted,fdeg=maxdeg(txt),maxrows=int(m.group(1)) if m else None,secs=round(time.time()-t0,1),tail=None if m else txt[-200:])
    open(f"out/log_{q}_{t}_{seed}_{int(planted)}.txt","w").write(txt)
    os.remove(fn); 
    if os.path.exists(fn+".out"): os.remove(fn+".out")
    print(json.dumps(d),flush=True); return d
if __name__=="__main__":
    p,q,t,seed,pl,tmo=map(int,sys.argv[1:7]); one(p,q,t,seed,bool(pl),tmo)
