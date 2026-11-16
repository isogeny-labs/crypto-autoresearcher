# faster version of SA-09b arith.py: numpy reduced-form enumeration; same projection code
import math, numpy as np
from arith import reduce_form, coprime_rep, egcd, project
def redforms(Del):
    L=[]; a=1
    amax=math.isqrt(-Del//3)+1
    par=Del&1  # b = Del mod 2
    for a in range(1,amax+1):
        if 3*a*a>-Del: break
        b=np.arange(-a+1,a+1,dtype=np.int64)
        b=b[(b&1)==par]
        t=b*b-Del
        m=(t%(4*a))==0
        b=b[m]; t=t[m]
        if len(b)==0: continue
        c=t//(4*a)
        k=(c>=a)&~((c==a)&(b<0))
        for bb,cc in zip(b[k].tolist(),c[k].tolist()):
            if math.gcd(math.gcd(a,abs(bb)),cc)==1: L.append((a,bb,cc))
    return L
