# analytic extrapolation: points vs character-count rank, inert-prime conductors; h_m=3*m*prod(1+1/q), prim(m)=3m (m = product of distinct inert primes)
from sympy import primerange, jacobi_symbol
from itertools import combinations
import json
inert=[q for q in primerange(5,400) if q not in (23,) and jacobi_symbol(-23%q,q)==-1]
print('inert primes',inert[:12])
def prods(B):
    out=[1]
    def rec(start,cur):
        for i in range(start,len(inert)):
            if cur*inert[i]>B: break
            out.append(cur*inert[i]); rec(i+1,cur*inert[i])
    rec(0,1); return sorted(out)
rows=[]
from fractions import Fraction
for B in [1,5,7,35,100,200,500,1000,2000,5000,10**4,10**5,10**6]:
    ms=prods(B); N=Fraction(0); R=0
    for m in ms:
        h=Fraction(3*m)
        for q in inert:
            if m%q==0: h*=Fraction(q+1,q)
        N+=h; R+=3*m
    rows.append({'B':B,'levels':len(ms),'points':float(N),'rank_Euler':float(N)-R,'ratio':float((N-R)/N)})
    print(rows[-1])
json.dump(rows,open('theory_table.json','w'),indent=1)
