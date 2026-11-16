import json, math, sys
sys.path.insert(0,'.')
import model as M
d=json.load(open('model_out.json')); rows=d['rows']
arms=list(dict.fromkeys(r['arm'] for r in rows))
NS=[20,24,28,32,36,40,64,128,192,256]
def get(a,n,l): 
    for r in rows:
        if r['arm']==a and r['n']==n and r['lam']==l: return r
out=[]
out.append("# SA-22 projected cost / rho  (log2 of ratio; positive = worse than rho; inf = no admissible factor base B>=4)\n")
for lam in (0.0,0.1,1.0):
    out.append(f"\n## unpriced work (linear algebra, descent) at {lam} GAE per field op\n")
    out.append("| arm | "+" | ".join(f"{n}b" for n in NS)+" |\n|---|"+"---|"*len(NS))
    for a in arms:
        cells=[]
        for n in NS:
            r=get(a,n,lam); x=r['log2_ratio']; cells.append("inf" if x==float('inf') else f"{x:.1f}")
        out.append(f"| {a} | "+" | ".join(cells)+" |")
out.append("\n## target-only bound (all B/2 factor-base relations FREE; only the target's own relation is searched), lam=0.1, log2 ratio to rho\n")
out.append("| arm | "+" | ".join(f"{n}b" for n in NS)+" |\n|---|"+"---|"*len(NS))
for a in arms:
    out.append(f"| {a} | "+" | ".join(("inf" if get(a,n,0.1)['log2_target_only']==float('inf') else f"{get(a,n,0.1)['log2_target_only']-get(a,n,0.1)['log2_rho']:.1f}") for n in NS)+" |")
# checks
ok_all=True; summ={}
for n in (128,256):
    for lam in (0.0,0.1,1.0):
        mn=min((get(a,n,lam)['log2_ratio'],a) for a in arms)
        summ[f"{n}_{lam}"]=mn
nongen=[a for a in arms if not a.startswith('PT')]
summ['min_nongeneric_256']=min((min(get(a,256,l)['log2_ratio'] for l in (0.0,0.1,1.0)),a) for a in nongen)
summ['best_arm_each_n']={n:min((get(a,n,0.1)['log2_ratio'],a) for a in arms) for n in NS}
# is the ratio increasing with N for every arm? (n>=64)
mono={}
for a in arms:
    xs=[get(a,n,0.1)['log2_ratio'] for n in (64,128,192,256)]
    mono[a]=all(xs[i]<xs[i+1] for i in range(3))
summ['ratio_grows_64_to_256']=mono
# slope of log2 ratio vs n between 128 and 256 (exponent excess)
summ['excess_exponent_128_256']={a:(get(a,256,0.1)['log2_ratio']-get(a,128,0.1)['log2_ratio'])/128 for a in arms}
json.dump(summ,open('summary.json','w'),indent=1,default=str)
open('results_table.md','w').write("\n".join(out)+"\n")
print("\n".join(out)); print(json.dumps(summ,indent=1,default=str))
