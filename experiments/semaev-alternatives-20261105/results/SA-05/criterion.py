# (b) rational-reconstruction + factoring criterion on targets.
# R global on twist d <=> x_R=u/v with v(u^3+7v^3) = d*s^2, d squarefree.  For R=P+Q with P,Q,P-Q of height<=h in ONE twist class
# the class d is that of the base points, so d<=8h^4.  We measure core(v(u^3+7v^3)) for random targets and for true relations.
from common import *
import random, json, time, math, glob, sys
def ratrec(x,p):
    r0,r1=p,x%p; t0,t1=0,1; bound=math.isqrt(p//2)
    while r1>bound:
        q=r0//r1; r0,r1=r1,r0-q*r1; t0,t1=t1,t0-q*t1
    if t1<0: r1,t1=-r1,-t1
    return r1,t1
def corex(u,v):
    n=v*(u**3+7*v**3)
    return abs(int(pari.core(n))) if n!=0 else 0
random.seed(11)
out=[]
H=100
for k,nf in ((40,100000),(48,30000),(56,10000)):
    p=primes_for(k,1)[0]
    # all 1e5 targets: reconstruct (cost only)
    t=time.time(); heights=[]; ts=[]
    while len(ts)<100000:
        x=random.randrange(p)
        if pow((x**3+7)%p,(p-1)//2,p)!=1: continue
        ts.append(x); u,v=ratrec(x,p); heights.append(math.log2(max(abs(u),v)+1))
    t_rec=time.time()-t
    # factoring subset
    t=time.time(); cores=[]
    for x in ts[:nf]:
        u,v=ratrec(x,p); cores.append(corex(u,v))
    t_fac=time.time()-t
    thr=8*H**4
    small=sum(1 for c in cores if 0<c<=thr)
    # sqfree-part size relative to n: log2(core) vs log2(n)
    med_core_bits=sorted(math.log2(c+1) for c in cores)[len(cores)//2]
    row=dict(k=k,p=p,n_targets_reconstructed=len(ts),median_height_bits=sorted(heights)[len(heights)//2],sqrt_p_bits=0.5*math.log2(p),
             n_factored=nf,thr_core=thr,n_core_le_thr=small,median_core_bits=med_core_bits,t_rec=round(t_rec,1),t_fac=round(t_fac,1))
    # recall on true relations found by the yield run (any raw triples file for this k, h=64..100)
    rec=dict(global_n=0,global_pass=0,wrapped_n=0,wrapped_pass=0,wrapped_core_bits=[])
    from fractions import Fraction
    def S3(x1,x2,x3):
        e1=x1+x2; e2=x1*x2
        return x3*x3*(e1*e1-4*e2)-2*x3*(e1*e2+14)+e2*e2-28*e1
    for f in sorted(glob.glob(f'raw/k{k}_p{p}_h*_rat_triples.txt')):
        hh=int(f.split('_h')[1].split('_')[0])
        if hh<48: continue
        lk={x:(a,b) for a,b,x in small_pts(p,hh)}
        pp=p
        for l in open(f):
            x1,x2,xd,kk=map(int,l.split())
            # recompute x_R = other sign value
            def lift(x): return (x,pow((x**3+7)%p,(p+1)//4,p))
            P1,P2=lift(x1),lift(x2)
            def addp(A,B):
                l_=(B[1]-A[1])*pow(B[0]-A[0],-1,p)%p; x3=(l_*l_-A[0]-B[0])%p; return x3
            xa=addp(P1,P2); xb=addp(P1,(P2[0],-P2[1]%p))
            xR= xb if xa==xd else xa   # D=xd is one sign; R the other
            u,v=ratrec(xR,p); c=corex(u,v); hb=math.log2(max(abs(u),v)+1)
            isglob = S3(Fraction(*lk[x1]),Fraction(*lk[x2]),Fraction(*lk[xd]))==0   # exact test over Q
            if isglob: rec['global_n']+=1; rec['global_pass']+= (0<c<=thr)
            else: rec['wrapped_n']+=1; rec['wrapped_pass']+=(0<c<=thr); rec['wrapped_core_bits'].append(round(math.log2(c+1),1))
    rec['wrapped_core_bits']=sorted(rec['wrapped_core_bits'])[:5]
    row['relations']=rec
    print(json.dumps(row),flush=True); out.append(row)
json.dump(out,open('criterion_results.json','w'),indent=1)
