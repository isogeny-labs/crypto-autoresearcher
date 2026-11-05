"""Exact graded-annihilator ffd for the *real* digit system from its top form Q_1...Q_m (parameter free), m=2 s<=9, m=3 s=4..7.
Also the closed-form entropy predictor floor(s/2)+e/2+1+(m-1)e  (e=2^(m-1))."""
import json, itertools, sys, math
from math import comb
import lib
from lib import *
def Q(s, shift, e, p):
    out = {}
    for S in itertools.combinations(range(s), e):
        c = math.factorial(e)
        for i in S: c = c*pow(2,i,p) % p
        out[sum(1<<(shift+i) for i in S)] = c % p
    return out
def formula(m,s):
    e = 2**(m-1); return s//2 + e//2 + 1 + (m-1)*e
def lef_block(s,e):  # least j with C(s,j)>C(s,j+e)
    j=0
    while comb(s,j) <= comb(s,j+e): j+=1
    return j
rows=[]
for m,srange in ((2,range(2,9)),(3,range(4,7))):
    e=2**(m-1)
    for s in srange:
        p = 1000003
        top = {0:1}
        for k in range(m): top = pmul(top, Q(s,k*s,e,p), p)
        D = m*e
        n = m*s
        if s < e: print('skip', m, s); continue
        j = ann_degree(GrBool(n), top, D, p, jmax=6)
        rows.append(dict(m=m,s=s,D=D,ann=j,ffd_gr=D+j,formula=formula(m,s),lef_block=lef_block(s,e)+D))
        print(rows[-1], flush=True)
json.dump(rows, open('/home/user/semaev-runs/SA-11/out/digit_topform_rows.json','w'))
