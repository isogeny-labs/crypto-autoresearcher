"""Short LLL micro-benchmark: Coppersmith-shaped triangular lattice, dim d=(2t+1)^2 (Weierstrass m=2 box shifts),
entries mimic p^(t-k)*X^mono diag + random lower-triangular mod p^t. 1 thread, fpylll LLL delta=.99."""
import sys, time, random, json, signal
from fpylll import IntegerMatrix, LLL
import sympy
def build(d, t, bits, delta, rng):
    p = int(sympy.nextprime(rng.getrandbits(bits)|(1<<(bits-1))))
    X = int(p**delta)+1
    M = IntegerMatrix(d,d)
    side = int(round(d**0.5))
    for i in range(d):
        a,b = divmod(i, side)
        k = min(t, (a+b)//2 + 0)   # shift power grows with monomial degree (shape only)
        diag = p**(t-k) * (X**(a+b))
        M[i,i]=diag
        for j in range(i):
            M[i,j]=rng.randrange(p**t)*(X**((j//side)+(j%side)))
    return M
class TO(Exception): pass
def h(*a): raise TO()
signal.signal(signal.SIGALRM,h)
rng=random.Random(1)
out=[]
for t in (2,3,4,5):
    d=(2*t+1)**2
    for bits in (64,128,256):
        M=build(d,t,bits,0.11,rng)
        signal.alarm(40)
        t0=time.process_time()
        try:
            LLL.reduction(M, delta=0.99); dt=time.process_time()-t0; st="ok"
        except TO: dt=None; st="timeout40"
        signal.alarm(0)
        r=dict(t=t,d=d,bits=bits,maxbits=t*bits+ int(0.11*bits*2*t),sec=dt,status=st)
        print(r,flush=True); out.append(r)
        if st!="ok": break
json.dump(out,open("lll_bench.json","w"),indent=1)
