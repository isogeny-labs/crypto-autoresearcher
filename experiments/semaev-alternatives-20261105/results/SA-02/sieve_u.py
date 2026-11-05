# (b) sieve-by-u: for each u=1,2,.. solve the quartic g_u(e1) mod p with PARI polrootsmod, keep roots with e1<=2B, verify in the group.
import random, time, json, sys, numpy as np
import cypari2
from common import *
pari=cypari2.Pari(); pari.allocatemem(200*10**6)
def sieve(p,B,xR,R,umax=None):
    calls=0
    for u in range(1,(umax or B)):
        calls+=1
        c=S3poly_e1_coeffs(p,xR,u)
        roots=pari.polrootsmod(pari.Pol(c),p)
        for r in roots:
            e1=int(r.lift())
            if e1<=2*B and (e1-u)%2==0 and e1>u:
                x1=(e1+u)//2;x2=(e1-u)//2
                if x2>=1 and x1<=B and verify(p,x1,x2,R): return calls,(x1,x2)
    return calls,None
if __name__=='__main__':
    pbits=int(sys.argv[1]); Bs=[2**k for k in range(int(sys.argv[2]),int(sys.argv[3])+1)]
    trials=int(sys.argv[4]); p=mkp(pbits); rng=random.Random(2026+pbits)
    rows=[]
    for B in Bs:
        n=trials if B<=2**13 else max(10,trials//3)
        ts=[];cs=[];ok=0
        for _ in range(n):
            x1,x2,R=plant(p,B,rng)
            t0=time.perf_counter(); calls,res=sieve(p,B,R[0],R); dt=time.perf_counter()-t0
            good = res is not None and verify(p,res[0],res[1],R)
            ok+=good; ts.append(dt);cs.append(calls)
        row=dict(pbits=pbits,B=B,trials=n,recovered=ok,mean_time=float(np.mean(ts)),times=ts,mean_calls=float(np.mean(cs)),us_per_call=float(np.sum(ts)/np.sum(cs)*1e6))
        rows.append(row); print({k:v for k,v in row.items() if k!='times'},flush=True)
    json.dump(rows,open(f'sieve_u_p{pbits}.json','w'))
