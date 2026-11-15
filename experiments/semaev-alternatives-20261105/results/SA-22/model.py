"""SA-22 cost model. All costs in GAE (group additions) unless noted; work in log2 via python floats / math.
T = R * A * (1 + c_o) + build + lam*LA + lam*descent        (c_o = oracle cost per call in GAE, physical rate)
R = (B/2)(1-disc)+1 relations (B/2 columns, Aut={+-1}); A = max(1, m! N / B^m) attempts per relation; B <= N^delta_cap.
"""
import json, math, sys
import numpy as np
LOG2=math.log(2)
# ---------- host constants (measured, see fieldop.json / lll_bench.json)
def f_sec(n): return 60e-9*(max(n,64)/256.0)**1.6          # one n-bit mulmod, optimised C (gmpy2 loop gave 71 ns incl. interpreter)
def g_sec(n): return 14*f_sec(n)                              # one GAE = 14 field mult (projective add)
F31=3e-9                                                      # msolve 31-bit field op, s
# ---------- LLL law: sec = exp(c) d^a n^e  (fit to lll_bench.json)
bench=[r for r in json.load(open('lll_bench.json')) if r['status']=='ok']
X=np.array([[1,math.log(r['d']),math.log(r['bits'])] for r in bench]); y=np.array([math.log(r['sec']) for r in bench])
coef,res,_,_=np.linalg.lstsq(X,y,rcond=None); LLL_c,LLL_a,LLL_e=coef
LLL_resid=float(np.max(np.abs(X@coef-y)))
def lll_sec(d,n): return math.exp(LLL_c)*d**LLL_a*n**LLL_e
# ---------- msolve laws
# m=3 norm digit (SA-04): B=4,8,16 -> cols 655,5583,47696; secs .03,.5,124
ms3_B=np.array([4,8,16.]); ms3_cols=np.array([655,5583,47696.]); ms3_sec=np.array([.03,.5,124.])
ms3_colpow=np.polyfit(np.log(ms3_B),np.log(ms3_cols),1)           # cols ~ B^a
ms3_timepow_meas=np.polyfit(np.log(ms3_cols[1:]),np.log(ms3_sec[1:]),1)[0]   # time ~ cols^e (last 2 pts)
def ms3_sec_f(B,e):  # anchored at B=16
    cols=math.exp(ms3_colpow[1])*B**ms3_colpow[0]
    return 124.0*(cols/47696.0)**e
# tower m=2 (SA-14): t=6..9 rows, secs; F4 degree D(t)=4+floor((t-2)/4) for t>=2
tw_rows=np.array([2803,6354,11138,23644.]); tw_sec=np.array([.56,4.15,46.3,412.])
tw_e_meas=np.polyfit(np.log(tw_rows),np.log(tw_sec),1)[0]
def tw_rows_f(t):
    D=4+(t-2)//4; n=2*t
    return 0.6*math.comb(n+D,D)
def tw_sec_f(t,e): return 412.0*(tw_rows_f(t)/23644.0)**e
# ---------- certified finite-t reach tables (SA-01, SA-20)
W2={2:.1000,3:.1189,4:.1294,5:.1362,6:.1408,8:.1470,12:.1531,16:.1564}
E2={2:.1152,3:.1265,4:.1338,5:.1392,6:.1431,8:.1479,12:.1538}
W3={2:.0144,3:.0215,4:.0258,5:.0286,6:.0306}
E3={2:.0158,3:.0223}
def dimW2(t): return (2*t+1)**2
def dimE2(t): return ((2*t+1)**2+1)//2
def dimW3(t): return (t+1)**3          # favourable underestimate of the m=3 shift-set size
# ---------- arms
def attempts(N,B,m): return max(1.0, math.factorial(m)*N/B**m)
def total(n,lam,m,B,disc,c_o,build,w,lamo=None,target_only=False):
    """returns GAE cost. lam prices unpriced work (LA, descent) in GAE per field op.
    c_o: oracle cost per call in GAE (already physical)."""
    N=2.0**n
    cols=B/2.0
    R=1.0 if target_only else cols*(1-disc)+1
    A=attempts(N,B,m)
    la=0.0 if target_only else 2*w*cols*cols
    desc=2*m*cols
    return R*A*(1+c_o)+build+lam*(la+desc)
def best(n,lam,spec,**kw):
    """minimise over B (and rung t) for one arm. spec: dict(name,m,caps(t)->(delta,..)...) """
    pass
def betas(cap,n):
    return [b for b in np.arange(0.01,cap+1e-9,0.005)]
def arm_cost(arm,n,lam,target_only=False,variant=None):
    N=2.0**n; m=arm['m']; best=(float('inf'),None)
    for rung in arm['rungs'](n):
        cap=rung['cap']; 
        capb=min(cap+1.0/n,0.5)   # B counts points (+-), reach bounds x-coordinates by N^cap, so B<=2N^cap
        cand=[b for b in np.arange(0.01,capb+1e-12,0.0025)]
        if abs(cand[-1]-capb)>1e-9: cand.append(capb)
        for b in cand:
            B=N**b
            if B<4: continue
            c_o=rung['c_o'](B,n)
            build=rung.get('build',lambda B:0.0)(B)
            cost=total(n,lam,m,B,arm.get('disc',0.0),c_o,build,rung.get('w',m),target_only=target_only)
            if cost<best[0]: best=(cost,dict(beta=round(float(b),4),B_log2=round(math.log2(B),2),rung=rung.get('label')))
    return best
def mk_ladder(table,dimf,m,asym,extra=None,optimistic=False):
    def rungs(n):
        out=[]
        if optimistic:
            tt=max(table); d=dimf(tt)
            out.append(dict(label=f"asym{asym:.4f}@t{tt}",cap=asym,c_o=lambda B,n,d=d:lll_sec(d,n)/g_sec(n)))
            return out
        for t,dl in table.items():
            d=dimf(t)
            out.append(dict(label=f"t{t}",cap=dl,c_o=lambda B,n,d=d:lll_sec(d,n)/g_sec(n)))
        return out
    return rungs
def single(cap,c_o,label,build=lambda B:0.0,w=None):
    d=dict(label=label,cap=cap,c_o=c_o,build=build)
    if w: d['w']=w
    return d
ARMS={}
ARMS['PT2 generic pair table (m=2)']=dict(m=2,rungs=lambda n:[single(0.5,lambda B,n:0.0,'pair',build=lambda B:B*B/2)])
ARMS['PT2+Heegner (13% free rows)']=dict(m=2,disc=0.13,rungs=lambda n:[single(0.5,lambda B,n:0.0,'pair+H',build=lambda B:B*B/2)])
# m=3 generic: table of B pair sums (B^2/2 build); each attempt = B lookups R-P_i -> oracle cost B GAE per call
ARMS['PT3 generic table (m=3)']=dict(m=3,rungs=lambda n:[single(0.5,lambda B,n:B,'pt3',build=lambda B:B*B/2)])
def frm(delta,d=3): return lambda n:[single(delta,lambda B,n:max(lll_sec(d,n),1e-6)/g_sec(n),f'form d{d}')]
ARMS['Weierstrass form lattice (delta=1/9)']=dict(m=2,rungs=frm(1/9))
ARMS['Edwards form lattice (delta=1/8)']=dict(m=2,rungs=frm(1/8))
ARMS['Ladder Weierstrass m=2 (cert t<=16)']=dict(m=2,rungs=mk_ladder(W2,dimW2,2,1/6))
ARMS['Ladder Edwards m=2 (cert t<=12)']=dict(m=2,rungs=mk_ladder(E2,dimE2,2,1/6))
ARMS['Ladder m=2 OPTIMISTIC (delta=1/6, dim 85)']=dict(m=2,rungs=mk_ladder(E2,lambda t:85,2,1/6,optimistic=True))
ARMS['cuso/ladder m=3 (cert t<=6)']=dict(m=3,rungs=mk_ladder(W3,dimW3,3,1/24))
ARMS['cuso/ladder m=3 OPTIMISTIC (delta=1/24, dim 343)']=dict(m=3,rungs=mk_ladder(W3,lambda t:343,3,1/24,optimistic=True))
def ms3(e): return lambda n:[single(0.5,lambda B,n:ms3_sec_f(B,e)/(14*F31),'ms3 e=%.2f'%e,w=3)]
ARMS['msolve norm m=3 digit (time~cols^2.58 meas)']=dict(m=3,rungs=ms3(ms3_timepow_meas))
ARMS['msolve norm m=3 digit (time~cols^2 favourable)']=dict(m=3,rungs=ms3(2.0))
def tw_arm(e):
    return dict(m=2,rungs=lambda n:[single(0.5,lambda B,nn:tw_sec_f(max(2,int(round(math.log2(B)))),e)/(14*F31),'tower',w=2)])
ARMS['msolve Kummer tower m=2 (time~rows^meas)']=tw_arm(tw_e_meas)
ARMS['msolve Kummer tower m=2 (time~rows^2 favourable)']=tw_arm(2.0)
def rho(n): return math.sqrt(math.pi*2.0**n/4)
if __name__=="__main__":
    NS=[20,24,28,32,36,40,64,128,192,256]
    rows=[]
    for name,arm in ARMS.items():
        for n in NS:
            for lam in (0.0,0.1,1.0):
                c,info=arm_cost(arm,n,lam)
                ct,_=arm_cost(arm,n,lam,target_only=True)
                rows.append(dict(arm=name,n=n,lam=lam,log2_cost=math.log2(c),log2_rho=math.log2(rho(n)),log2_ratio=math.log2(c/rho(n)),
                    log2_target_only=(math.log2(ct) if ct else None),info=info))
    json.dump(dict(consts=dict(LLL=[LLL_c,LLL_a,LLL_e],LLL_maxresid=LLL_resid,ms3_colpow=list(ms3_colpow),ms3_time_e=ms3_timepow_meas,tw_e=tw_e_meas),rows=rows),open('model_out.json','w'),indent=1)
