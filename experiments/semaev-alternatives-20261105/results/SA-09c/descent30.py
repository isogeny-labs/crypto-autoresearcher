# Rare-hit descent: target R in E(F_p) is a hit if R is a signed sum of <=3 elements of S (repeats allowed).
# U(S) = set of all such sums; hit <=> R in U(S).  Heegner S (49 pts) vs random sets of 49 points of E(F_p).
import json,sys,random,math,time
import numpy as np
from sympy.ntheory import sqrt_mod
CA=-16; CB=16
ntarg=int(sys.argv[1]); nctrl=int(sys.argv[2]); primes=[int(x) for x in sys.argv[3].split(',')]; out=sys.argv[4]
pts=json.load(open('pts30.json')); info={r['p']:r for r in json.load(open('pts30_info.json'))}
def add(P,Q,p):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P;x2,y2=Q
    if x1==x2:
        if (y1+y2)%p==0: return None
        l=(3*x1*x1+CA)*pow(2*y1,-1,p)%p
    else: l=(y2-y1)*pow(x2-x1,-1,p)%p
    x3=(l*l-x1-x2)%p; return (x3,(l*(x1-x3)-y1)%p)
def neg(P,p): return None if P is None else (P[0],(-P[1])%p)
def randpt(p,rng):
    while True:
        x=rng.randrange(p); r=(x**3+CA*x+CB)%p
        if r==0: continue
        y=sqrt_mod(r,p)
        if y is not None: return (x,y if rng.random()<.5 else p-y)
def Uset(S,p):
    one=[None]+list(S)+[neg(q,p) for q in S]
    T2=set()
    for i,P in enumerate(one):
        for Q in one[i:]: T2.add(add(P,Q,p))
    pm=one[1:]; U=set(T2)
    for R in T2:
        for s in pm: U.add(add(R,s,p))
    return U
res=[]; rng_np=np.random.default_rng(7)
for p in primes:
    t0=time.time(); rng=random.Random(p+int(__import__("os").environ.get("SEED","0"))); S=[tuple(q) for q in pts[str(p)]]; nE=info[p]['#E']
    targets=[randpt(p,rng) for _ in range(ntarg)]
    U=Uset(S,p); h=sum(t in U for t in targets)
    ch=[];cU=[]
    for c in range(nctrl):
        Sc=[randpt(p,rng) for _ in range(len(S))]; Uc=Uset(Sc,p)
        ch.append(sum(t in Uc for t in targets)); cU.append(len(Uc))
    r={'p':p,'#E':nE,'ntargets':ntarg,'heegner_hits':h,'heegner_U':len(U),'heegner_exact_rate':len(U)/nE,
       'control_hits':ch,'control_hits_mean':float(np.mean(ch)),'control_hits_sd':float(np.std(ch,ddof=1)),
       'control_U_mean':float(np.mean(cU)),'control_U_sd':float(np.std(cU,ddof=1)),'control_U_min_max':[min(cU),max(cU)],
       'control_exact_rate':float(np.mean(cU))/nE,'frac_controls_hits_ge':float(np.mean(np.array(ch)>=h)),'frac_controls_U_ge':float(np.mean(np.array(cU)>=len(U))),
       'sec':round(time.time()-t0,1)}
    res.append(r); print(json.dumps({k:v for k,v in r.items() if k!='control_hits'}),flush=True)
    json.dump(res,open(out,'w'),indent=1)
