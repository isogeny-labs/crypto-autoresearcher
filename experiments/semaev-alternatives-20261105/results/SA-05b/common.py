import math, sympy
from math import gcd
import cypari2
pari = cypari2.Pari(); pari.allocatemem(300*10**6)
def primes_for(k, n):
    out=[]; q=2**k
    while len(out)<n:
        q=sympy.nextprime(q)
        if q%4==3: out.append(int(q))
    return out
def small_pts(p,h,integer_only=False):
    """rationals a/b, |a|<=h, 1<=b<=h, gcd=1, x^3+7 a QR mod p. returns list (a,b,x)"""
    res=[]
    for b in range(1,(2 if integer_only else h+1)):
        ib=pow(b,-1,p)
        for a in range(-h,h+1):
            if gcd(abs(a),b)!=1: continue
            x=a*ib%p
            f=(x**3+7)%p
            if f and pow(f,(p-1)//2,p)==1: res.append((a,b,x))
    return res
def twist(a,b):
    n=b*(a**3+7*b**3)
    return int(pari.core(n))
def is_global(x1,x2,x3):
    pass
