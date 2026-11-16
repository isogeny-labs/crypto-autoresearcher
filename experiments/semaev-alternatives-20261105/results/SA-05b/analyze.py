import json, math, random, sys
import numpy as np
rows=[json.loads(l) for l in open('main.jsonl')]
random.seed(1); np.random.seed(1)
byk={}
for r in rows: byk.setdefault(r['k'],[]).append(r)
tab=[]; out={}
def pois_ci(n):  # exact-ish 95% CI for Poisson mean via chi2
    from scipy.stats import chi2
    lo=0 if n==0 else chi2.ppf(.025,2*n)/2; hi=chi2.ppf(.975,2*(n+1))/2; return lo,hi
for k,rs in sorted(byk.items()):
    W=sum(r['rational']['listed_wrapped'] for r in rs); G=sum(r['rational']['listed_global'] for r in rs)
    C=sum(r['control']['distinct'] for r in rs); I=sum(r['integer']['distinct'] for r in rs)
    E=sum(r['gen_trip'] for r in rs)
    ratio=W/E; lo,hi=pois_ci(W)
    # bootstrap over primes
    bs=[]
    for _ in range(4000):
        s=[random.choice(rs) for _ in rs]; bs.append(sum(r['rational']['listed_wrapped'] for r in s)/sum(r['gen_trip'] for r in s))
    # target arm: distinct targets hit
    th=lambda v,r: r[v]['tverify'][2]
    TS=sum(th('rational',r) for r in rs); TC=sum(th('control',r) for r in rs); TI=sum(th('integer',r) for r in rs)
    TE=sum(r['control']['T']*(r['B']*(r['B']-1))/(r['p']/2) for r in rs)
    bad=sum(r[v]['tverify'][1] for r in rs for v in('rational','control','integer'))
    out[k]=dict(primes=len(rs),B=np.mean([r['B'] for r in rs]),h=rs[0]['h'],p13=rs[0]['p13'],W=W,G=G,C=C,I=I,E=E,ratio=ratio,ratio_poisson_ci=[W/ E*0+lo/E,hi/E],ratio_boot_ci=[float(np.percentile(bs,2.5)),float(np.percentile(bs,97.5))],
        ctrl_over_E=C/E,int_over_E=I/E,struct_over_ctrl=W/C if C else None,
        T_struct=TS,T_ctrl=TC,T_int=TI,T_expected=TE,tyield_over_generic=TS/TE,tyield_over_ctrl=TS/TC,tyield_ci_over_ctrl=[pois_ci(TS)[0]/TC,pois_ci(TS)[1]/TC],bad_verifications=bad)
ks=sorted(out); x=np.array(ks,float)
ratios={k:[r['rational']['listed_wrapped']/r['gen_trip'] for r in byk[k]] for k in ks}
bs=[]
for _ in range(4000):
    ys=[np.mean([random.choice(ratios[k]) for _ in ratios[k]]) for k in ks]
    bs.append(np.polyfit(x,ys,1)[0])
slope=float(np.polyfit(x,[out[k]['ratio'] for k in ks],1)[0])
res=dict(per_k=out,slope_ratio_vs_log2p=slope,slope_ci=[float(np.percentile(bs,2.5)),float(np.percentile(bs,97.5))])
json.dump(res,open('results.json','w'),indent=1)
with open('table_main.md','w') as f:
    f.write('| k | h | mean B | B/p^(1/3) | primes | wrapped W | global G | generic E | ratio W/E (Poisson 95%) | ctrl/E | int/E | target hits struct/ctrl/int | struct/ctrl targets (95%) |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|\n')
    for k in ks:
        o=out[k]; f.write(f"| {k} | {o['h']} | {o['B']:.0f} | {o['B']/o['p13']:.2f} | {o['primes']} | {o['W']} | {o['G']} | {o['E']:.1f} | {o['ratio']:.3f} ({o['ratio_poisson_ci'][0]:.2f}-{o['ratio_poisson_ci'][1]:.2f}) | {o['ctrl_over_E']:.3f} | {o['int_over_E']:.3f} | {o['T_struct']}/{o['T_ctrl']}/{o['T_int']} | {o['tyield_over_ctrl']:.3f} ({o['tyield_ci_over_ctrl'][0]:.2f}-{o['tyield_ci_over_ctrl'][1]:.2f}) |\n")
print(json.dumps(res,indent=1)); print(open('table_main.md').read())
