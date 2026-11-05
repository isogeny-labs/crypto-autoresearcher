# (a) closure test: heights of x(P+Q), x(P-Q), their sum/product, 2-step chains; same-twist vs different-twist
from common import *
import random, json, math
from collections import defaultdict
def ratrec(x,p):
    """return (num,den) with num/den = x mod p, |num|,den<=sqrt(p/2) or None"""
    bound=math.isqrt(p//2)
    r0,r1=p,x%p; t0,t1=0,1
    while r1>bound:
        q=r0//r1; r0,r1=r1,r0-q*r1; t0,t1=t1,t0-q*t1
    if t1==0 or abs(t1)>bound: return None
    if t1<0: r1,t1=-r1,-t1
    return (r1,t1)
def hbits(rr,p):
    return None if rr is None else math.log2(max(abs(rr[0]),rr[1]))
SLACK=6  # 'small' = reconstructed height at least 6 bits below the sqrt(p/2) uniqueness bound (false-positive prob ~2^-12)
def ratrec2(x,p,_f=ratrec):
    r=_f(x,p)
    if r is None: return None
    return r if math.log2(max(abs(r[0]),r[1]))<=0.5*math.log2(p/2)-SLACK else None
def add(P1,P2,p):
    (x1,y1),(x2,y2)=P1,P2
    if x1==x2:
        raise ValueError
    l=(y2-y1)*pow(x2-x1,-1,p)%p; x3=(l*l-x1-x2)%p; return (x3,(l*(x1-x3)-y1)%p)
def neg(P,p): return (P[0],(-P[1])%p)
def lift(x,p):
    y=pow((x**3+7)%p,(p+1)//4,p); return (x,y)
random.seed(5)
out=[]
for k in (40,48,56):
    p=primes_for(k,1)[0]; h=32
    pts=small_pts(p,h)
    cls=defaultdict(list)
    for a,b,x in pts: cls[twist(a,b)].append((a,b,x))
    big=[v for v in cls.values() if len(v)>=2]
    row_sizes=sorted((len(v) for v in cls.values()),reverse=True)[:5]
    row={'k':k,'p':p,'h':h,'npts':len(pts),'nclasses':len(cls),'classes_ge2':len(big),'top_class_sizes':row_sizes}
    def trial(sample):
        res={'n':0,'distinct_pairs':0,'pm_both_small':0,'sum_small':0,'prod_small':0,'hbits_pm':[]}
        res['distinct_pairs']=len({frozenset((A[2],B_[2])) for A,B_ in sample})
        for (A,B_) in sample:
            P1=lift(A[2],p);P2=lift(B_[2],p)
            if A[2]==B_[2]: continue
            Pp=add(P1,P2,p); Pm=add(P1,neg(P2,p),p)
            rp,rm=ratrec2(Pp[0],p),ratrec2(Pm[0],p)
            res['n']+=1
            if rp and rm: res['pm_both_small']+=1; res['hbits_pm'].append(max(hbits(rp,p),hbits(rm,p)))
            s=ratrec2((Pp[0]+Pm[0])%p,p); q=ratrec2(Pp[0]*Pm[0]%p,p)
            if s: res['sum_small']+=1
            if q: res['prod_small']+=1
        hb=res.pop('hbits_pm'); res['median_hbits_when_small']=sorted(hb)[len(hb)//2] if hb else None
        res['max_hbits_when_small']=max(hb) if hb else None
        return res
    same=[]; 
    for _ in range(2000):
        v=random.choice(big); same.append(tuple(random.sample(v,2)))
    diff=[]
    while len(diff)<2000:
        A,B_=random.sample(pts,2)
        if twist(A[0],A[1])!=twist(B_[0],B_[1]): diff.append((A,B_))
    row['same_twist']=trial(same); row['diff_twist']=trial(diff)
    # 2-step chains inside one twist class: R1=P+Q (rational?), R2=R1 +- S
    ch={'n':0,'R2_small':0,'hb':[]}
    for _ in range(2000):
        v=random.choice(big); 
        A,B_=random.sample(v,2)
        P1,P2=[lift(t[2],p) for t in (A,B_)]; P3=P1
        R1=add(P1,P2,p); R2=add(R1,P3,p) if R1[0]!=P3[0] else None
        if R2 is None: continue
        ch['n']+=1; rr=ratrec2(R2[0],p)
        if rr: ch['R2_small']+=1; ch['hb'].append(hbits(rr,p))
    hb=ch.pop('hb'); ch['median_hbits']=sorted(hb)[len(hb)//2] if hb else None; ch['max_hbits']=max(hb) if hb else None
    row['chain2_same_twist']=ch
    row['sqrt_p_bits']=0.5*math.log2(p)
    print(json.dumps(row)); out.append(row)
json.dump(out,open('closure_results.json','w'),indent=1)
