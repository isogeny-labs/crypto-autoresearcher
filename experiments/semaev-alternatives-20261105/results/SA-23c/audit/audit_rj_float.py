#!/usr/bin/env python3
"""Main-session audit for SA-23c: R_J at given primes by the pre-freeze algorithm (verify/jacobi_rank.py:
primitive-root character, complex floating point, R_J = #{pieces with J = p}), vectorised with numpy.
Independent of the executor's exact Z[zeta12] code. Usage: audit_rj_float.py p1 p2 ..."""
import sys, numpy as np, json
from sympy import primitive_root
for p in map(int, sys.argv[1:]):
    g=primitive_root(p); ind=np.zeros(p,dtype=np.int64); x=1
    for e in range(p-1): ind[x]=e; x=x*g%p
    z=np.exp(2j*np.pi*np.arange(12)/12)
    u=np.arange(2,p); iu=ind[u]; iv=ind[(1-u)%p]
    def J2(a,b): return np.sum(z[(a*iu+b*iv)%12])
    def chi(k,v): return z[(k*ind[v%p])%12]
    plus=0; absok=0
    for b in (4,8):
        for k in range(1,12):
            if (6+b+k)%12==0: continue
            J=J2(6,b)*J2((6+b)%12,k)*chi(b,-1)*chi(k,-1)
            absok+= abs(abs(J)-p)<1e-6*p; plus+= abs(J-p)<1e-6*p
    print(json.dumps({"p":p,"R_J_float":int(plus),"abs_ok":int(absok)}),flush=True)
