import random
from common import *
from solvers import smart_psi

def anomalous_curve(bits, rng):
    """p=(3u^2+1)/4 prime ~2^bits, u odd; curve y^2=x^3+b, smallest b with #E(F_p)=p (CM by Z[(1+sqrt-3)/2], trace 1)."""
    while True:
        u = rng.randrange(2 ** ((bits - 1) // 2 ), 2 ** ((bits + 1) // 2)) | 1
        if (3 * u * u + 1) % 4 or ((3 * u * u + 1) // 4) % 4 != 3: continue   # p = 3 mod 4: fast sqrt
        p = (3 * u * u + 1) // 4
        if p.bit_length() != bits or not sp.isprime(p): continue
        for b in range(1, 400):
            if int(pari.ellcard(pari.ellinit([0, b], p))) == p:
                return p, 0, b
