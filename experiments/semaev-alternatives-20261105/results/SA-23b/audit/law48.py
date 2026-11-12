#!/usr/bin/env python3
"""Main-session post-hoc analysis of SA-23b Jacobi data (results/jacobi.jsonl, executor's canonical convention:
primary pi = a+bi with a odd, b even, a+b = 1 mod 4, b > 0; chi = 12th-power residue symbol at the prime of Z[zeta12]
above (pi, rho)). Finds that the 20-exponent string is a function of (a mod 3, b mod 3, (2/p)_3, (2/p)_4) and writes the
48-cell table fitted on ALL p < 1e5, plus the closed form for R_J, for the SA-23c held-out test (1e5 < p < 1e6).
Usage: law48.py jacobi.jsonl out_table.json"""
import json,sys,collections
rs=[json.loads(l) for l in open(sys.argv[1])]
CAND=[1,2,3,4,6,8,9,12,18,24,27,36]; CAND=CAND+[-c for c in CAND]
i2=CAND.index(2)
def cell(r): return "%d,%d,%d,%d"%(r['a']%3,r['b']%3,r['s3'][i2],r['s4'][i2])
def string(r): return [x if x is not None else -1 for x in r['exps']]
tab=collections.defaultdict(collections.Counter)
for r in rs: tab[cell(r)][json.dumps(string(r))]+=1
assert all(len(c)==1 for c in tab.values()), "not functional"
out={"convention":"executor canonical (SA-23b DEVIATIONS.md); exponent -1 = piece not of root-of-unity type",
     "fitted_on":"all p = 1 mod 12, p < 1e5 (n=%d)"%len(rs),"cells":{k:json.loads(next(iter(c))) for k,c in sorted(tab.items())},
     "cell_counts":{k:sum(c.values()) for k,c in sorted(tab.items())},
     "R_J_closed_form":"R_J = 4 + 4*[2 is a cubic residue mod p] + 8*[3 | b and ((a mod 3 == 1) != (p mod 8 == 5))]"}
def RJ(r): return 4+4*(r['s3'][i2]==0)+8*((r['b']%3==0) and ((r['a']%3==1)!=(r['p']%8==5)))
out["R_J_closed_form_in_sample_exceptions"]=sum(1 for r in rs if RJ(r)!=r['R'])
json.dump(out,open(sys.argv[2],'w'),indent=1)
print("cells",len(tab),"functional on",len(rs),"primes; closed-form R_J exceptions:",out["R_J_closed_form_in_sample_exceptions"])
