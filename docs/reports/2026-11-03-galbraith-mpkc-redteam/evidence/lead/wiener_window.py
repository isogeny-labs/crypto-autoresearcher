"""Galbraith v2 Thm 24.5.2 prints 0<d<N^(1/4)/sqrt3; official erratum: sqrt6.
Search p<q<2p, d in the window [N^(1/4)/sqrt6, N^(1/4)/sqrt3) with gcd(d,phi)=1,
for cases where d is NOT the denominator of any continued-fraction convergent of
e/N (the Euclidean-algorithm route of the printed proof)."""
import math, json, sys
def primerange(a,b):
    s=bytearray([1])*b; s[0:2]=b"\x00\x00"
    for i in range(2,int(b**.5)+1):
        if s[i]: s[i*i::i]=bytearray(len(s[i*i::i]))
    return [i for i in range(a,b) if s[i]]
def convergent_denoms(a,b):
    h0,h1,k0,k1=0,1,1,0
    out=set()
    while b:
        q=a//b; a,b=b,a-q*b
        h0,h1=h1,q*h1+h0; k0,k1=k1,q*k1+k0
        out.add(k1)
    return out
fails=[]; tested=0; inwin=0
ps=list(primerange(3,2000))
for i,p in enumerate(ps):
    for q in ps[i+1:]:
        if q>=2*p: break
        N=p*q; phi=(p-1)*(q-1)
        lo=N**0.25/math.sqrt(6); hi=N**0.25/math.sqrt(3)
        for d in range(max(2,math.ceil(lo)), math.ceil(hi)):
            if not (lo<=d<hi) or math.gcd(d,phi)!=1: continue
            e=pow(d,-1,phi); tested+=1
            if d not in convergent_denoms(e,N):
                fails.append(dict(p=p,q=q,N=N,d=d,e=e,bound3=hi,bound6=lo))
# control: below sqrt6 bound, Wiener must always succeed
ctrl_fail=0; ctrl=0
for i,p in enumerate(ps[:150]):
    for q in ps[i+1:]:
        if q>=2*p: break
        N=p*q; phi=(p-1)*(q-1)
        for d in range(2, math.ceil(N**0.25/math.sqrt(6))):
            if d>=N**0.25/math.sqrt(6) or math.gcd(d,phi)!=1: continue
            e=pow(d,-1,phi); ctrl+=1
            ctrl_fail += d not in convergent_denoms(e,N)
json.dump(dict(window_cases=tested, window_failures=len(fails), first_failures=fails[:5],
   control_cases=ctrl, control_failures=ctrl_fail), sys.stdout, indent=1)
