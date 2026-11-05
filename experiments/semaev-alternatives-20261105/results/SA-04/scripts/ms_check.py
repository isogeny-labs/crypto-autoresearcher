# Known-answer check: every element of msolve's reduced GB must vanish at the planted point (mod p); also count solutions
# over F_p in the digit case by brute force over bits (m=2 only) to report the variety size.
import sys, os, random, subprocess, re, json, sympy as sp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ms_sweep as M
from build import system, system_S, system_SV
def check(m,base,B,seed,null=False):
    p=int(sp.nextprime(int(8*B**m))); rng=random.Random(seed)
    for _ in range(50):
        try:
            if base=='S': ring,gens,pt,meta=system_S(m,p,B,rng)
            elif base=='SV': ring,gens,pt,meta=system_SV(m,p,B,rng)
            else: ring,gens,pt,meta=system(m,p,base,B,rng,null)
            break
        except Exception: continue
    vs=M.names(m,base,ring,B); eqs=[M.pstr(g,vs) for g in gens]+[f"{v}^2-{v}" for v,bb in zip(vs,ring.bm) if bb]
    fn=M.SC+"/chk.ms"; open(fn,"w").write(",".join(vs)+"\n"+str(p)+"\n"+",\n".join(eqs)+"\n")
    subprocess.run(["nice","-n","10",M.MS,"-g","2","-t","1","-f",fn,"-o",fn+".out"],capture_output=True,timeout=300)
    txt=open(fn+".out").read().strip().rstrip(':').strip()
    body=txt[txt.index('[')+1:txt.rindex(']')]
    syms=sp.symbols(vs); loc=dict(zip(vs,syms)); sub=dict(zip(syms,pt))
    polys=[q for q in body.split(',') if q.strip()]
    bad=0
    for q in polys:
        e=sp.sympify(q.replace('^','**'),locals=loc)
        if int(e.subs(sub))%p: bad+=1
    os.remove(fn); os.remove(fn+".out")
    return dict(m=m,base=base,B=B,seed=seed,null=null,p=p,gb_len=len(polys),gb_nonvanishing_at_planted=bad,planted=pt)
if __name__=="__main__":
    out=[]
    for args in [(2,'digit',16,0),(2,'digit',64,1),(2,'S',64,0),(2,'V',32,0),(2,'SV',32,0),(3,'digit',8,0),(3,'digit',8,1),(3,'S',8,0),(3,'V',16,0),(3,'SV',16,0),(2,'digit',32,0,True),(3,'digit',8,0,True)]:
        r=check(*args); print(r,flush=True); out.append(r)
    json.dump(out,open(os.path.dirname(os.path.abspath(__file__))+'/../out/ms/planted_gb_check.json','w'),indent=1)
