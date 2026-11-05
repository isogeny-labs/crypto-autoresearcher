# SA-03 (b): enumeration by discriminant. For each Delta=16 f(x1) f(x2) in S_F (factor base F={x<=B: f(x) QR}),
# find all forms (c0,c1,c2=S) with c1^2-4 c0 S = Delta, c0+c1 xR+S xR^2 = 0 mod p, S=s^2 <= B^2, |c1|<=C1, |c0|<=B^4.
# Derivation: with c2=S=s^2 the root condition is (c1+2 S xR)^2 = Delta mod p, so c1 + 2 xR S = eps*r mod p, r=sqrt(Delta):
# a 2-D lattice coset problem in (S,c1) of det p (the "Gamma_0(p) reduction step"), solved by Gauss reduction + box enumeration.
import random, json, math, sys
from common import *
def gauss(p,xR,k=1):
    # lattice {(k*S,c1): c1 + 2 xR S = 0 mod p}: basis (k,-2xR),(0,p); k balances the box [1,B^2]x[-C1,C1]
    a=(k,(-2*xR)%p); b=(0,p)
    def n(v): return v[0]*v[0]+v[1]*v[1]
    while True:
        if n(b)<n(a): a,b=b,a
        mu=round((a[0]*b[0]+a[1]*b[1])/n(a))
        if mu==0: break
        b=(b[0]-mu*a[0],b[1]-mu*a[1])
    return a,b
def enum_box(a,b,t,lo0,hi0,lo1,hi1,p):
    """all lattice-coset points t+i a+j b with coord0 in [lo0,hi0], coord1 in [lo1,hi1]. returns (points, n_istep)"""
    det=a[0]*b[1]-a[1]*b[0]
    pts=[];steps=0
    imin=1e300;imax=-1e300
    for c0 in (lo0,hi0):
        for c1 in (lo1,hi1):
            i=(b[1]*(c0-t[0])-b[0]*(c1-t[1]))/det
            imin=min(imin,i);imax=max(imax,i)
    for i in range(math.ceil(imin-1e-9),math.floor(imax+1e-9)+1):
        steps+=1
        b0=t[0]+i*a[0]; b1=t[1]+i*a[1]
        jl,jh=-1e300,1e300; ok=True
        for (base,v,lo,hi) in ((b0,b[0],lo0,hi0),(b1,b[1],lo1,hi1)):
            if v!=0:
                u=(lo-base)/v; w=(hi-base)/v
                if u>w:u,w=w,u
                jl=max(jl,u);jh=min(jh,w)
            elif not(lo<=base<=hi): ok=False
        if not ok or jl>jh: continue
        for j in range(math.ceil(jl-1e-9),math.floor(jh+1e-9)+1):
            c0=b0+j*b[0];c1=b1+j*b[1]
            if lo0<=c0<=hi0 and lo1<=c1<=hi1: pts.append((c0,c1))
    return pts,steps
def sweep(p,B,xR,x1t,x2t):
    F=[x for x in range(1,B+1) if is_qr(x**3+7,p)]
    pairs=[(x,y) for i,x in enumerate(F) for y in F[i+1:]]
    C1=4*B**3+60; M=B**4; Smax=B*B
    k=max(1,C1//Smax)
    a,b=gauss(p,xR,k)
    ops=dict(delta=0,cvp=0,isteps=0,cands=0,sq=0,integral=0)
    found=None; delta_at_found=None
    for (x1,x2) in pairs:
        Delta=16*(x1**3+7)*(x2**3+7)
        ops['delta']+=1
        r=sqrt34(Delta,p)
        for eps in (1,-1):
            ops['cvp']+=1
            t=(0,(eps*r)%p)   # point (S=0, c1 = eps r) ; coset c1+2xR S = eps r
            # shift c1 into centred rep by also allowing t - k*(0,p) : box [-C1,C1] handled since lattice contains (0,p)
            pts,steps=enum_box(a,b,t,k,k*Smax,-C1,C1,p)
            pts=[(c0//k,c1) for (c0,c1) in pts if c0%k==0]
            ops['isteps']+=steps; ops['cands']+=len(pts)
            for (S,c1) in pts:
                s=math.isqrt(S)
                if s*s!=S: continue
                ops['sq']+=1
                if (c1*c1-Delta)%(4*S): continue
                c0=(c1*c1-Delta)//(4*S)
                if abs(c0)>M: continue
                ops['integral']+=1
                if (c0+c1*xR+S*xR*xR)%p!=0: continue
                if found is None and (x1,x2)==(x1t,x2t) and (c0,c1,S)==S3vec(x1t,x2t): found=(x1,x2,c0,c1,S); delta_at_found=ops['delta']
    return ops,found,delta_at_found,len(pairs)
if __name__=="__main__":
    bits=int(sys.argv[1]); ntar=int(sys.argv[2]); p=prime34(bits); rng=random.Random(77+bits)
    out=open(f'bydisc_p{bits}.jsonl','w')
    for B in (6,8,12,16,24,32,48,64,96,128):
        recs=[]
        for (xR,x1,x2) in planted(p,B,ntar,rng):
            ops,found,at,npairs=sweep(p,B,xR,x1,x2)
            recs.append(dict(xR=xR,x1=x1,x2=x2,ops=ops,found=found is not None,delta_at_found=at,npairs=npairs))
        rec=dict(pbits=bits,B=B,recs=recs)
        out.write(json.dumps(rec)+"\n");out.flush()
        m=lambda k: sum(r['ops'][k] for r in recs)/len(recs)
        print(bits,B,'found',sum(r['found'] for r in recs),'/',ntar,'pairs',recs[0]['npairs'],'cvp',m('cvp'),'isteps',m('isteps'),'cands',m('cands'),'sq',m('sq'),'integral',m('integral'),flush=True)
