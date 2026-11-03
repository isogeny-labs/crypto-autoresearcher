"""Lemma 2.3.5: exhibit (t,s) needing n=-1 (h_{-1}=1,k_{-1}=0), i.e. failing with n in Z>=0."""
from fractions import Fraction
import math
al = Fraction(math.isqrt(2 * 10**60), 10**30)   # sqrt2 to 30 digits
# CF sqrt2 = [1;2,2,2,...]: h: h_{-1}=1,h_0=1,h_1=3,h_2=7 ; k: 0,1,2,5
h = [1, 1, 3, 7, 17, 41]; k = [0, 1, 2, 5, 12, 29]
c = 2
for s in range(1, 4):
    for t in range(1, 6):
        if abs(al - Fraction(t, s)) < Fraction(c, s * s):
            reps = []
            for i in range(len(h) - 1):
                for sg in (1, -1):
                    for u in range(0, 10):
                        for v in range(0, 10):
                            if u * v < 2 * c and (t, s) == (u * h[i + 1] + sg * v * h[i], u * k[i + 1] + sg * v * k[i]):
                                reps.append((i - 1, sg, u, v))
            print((t, s), "reps (n,sign,u,v):", sorted(set(reps))[:6], " any with n>=0:", any(r[0] >= 0 for r in reps))
