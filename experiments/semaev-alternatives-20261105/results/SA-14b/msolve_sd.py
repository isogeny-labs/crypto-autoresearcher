"""F4 (msolve) solving degree: max 'deg' printed by msolve -g 2 -v 2 -t 1 (grevlex GB), same systems as kummer_sd.py"""
import subprocess, random, re, sys, json
import kummer_sd as K
MS="/usr/local/lib/python3.13/dist-packages/sage_wheels/bin/msolve"
def system(p,q,t,a,b,xr):
    vs=[];eqs=[]
    for s in (1,2):
        names=[f"x{s}"]+[f"w{s}_{j}" for j in range(1,t)]
        vs+=names
        for j in range(1,t): eqs.append(f"{names[j]}-{names[j-1]}^{q}")
        eqs.append(f"{names[t-1]}^{q}-1")
    S=f"(x1-x2)^2*{xr}^2-2*((x1+x2)*(x1*x2+{a})+2*{b})*{xr}+(x1*x2-{a})^2-4*{b}*(x1+x2)"
    import sympy as sp
    syms=sp.symbols(vs); loc=dict(zip(vs,syms))
    Sx=sp.expand(sp.sympify(S.replace("^","**"),locals=loc))
    Sx=sp.Poly(Sx,*syms,modulus=p).as_expr()
    return vs,eqs+[str(Sx).replace("**","^")]
def run(p,q,t,seed,planted,fn):
    rng=random.Random(seed); a,b,xr=K.instance(p,q,t,rng,planted)
    vs,eqs=system(p,q,t,a,b,xr)
    open(fn,"w").write(",".join(vs)+"\n"+str(p)+"\n"+",\n".join(eqs)+"\n")
    r=subprocess.run([MS,"-g","2","-v","2","-t","1","-f",fn,"-o",fn+".out"],capture_output=True,text=True,timeout=1500)
    txt=r.stdout+r.stderr
    degs=[int(x) for x in re.findall(r"deg\s*=?\s*(\d+)",txt)]
    return txt,degs
if __name__=="__main__":
    p,q,t,seed,pl=map(int,sys.argv[1:6])
    txt,d=run(p,q,t,seed,bool(pl),"/tmp/claude-0/-home-user/0da9d9f6-3ae4-593e-a458-8600b2afd79e/scratchpad/ms.in")
    print(txt[-1500:]); print(d)
