import json, math, collections
rows=[json.loads(l) for l in open('yield_supp.jsonl')]
cells=[rows[i:i+3] for i in range(0,len(rows),3)]
# global reference: mean global-relation count per prime at the same h from the k>=48 runs
ref=collections.defaultdict(list)
for f in ('yield_48.jsonl','yield_56.jsonl'):
    R=[json.loads(l) for l in open(f)]
    for i in range(0,len(R),3): ref[R[i]['h']].append(R[i]['triples'])
agg=collections.defaultdict(lambda: collections.defaultdict(float))
for rat,ctl,itg in cells:
    a=agg[(rat['k'],rat['h'])]; M=rat['p']/2
    a['n']+=1; a['B']+=rat['B']; a['s']+=rat['triples']; a['c']+=ctl['triples']; a['i']+=itg['triples']; a['e']+=rat['N']*rat['B']/M
    a['sD']+=rat['N']-rat['D']; a['cD']+=ctl['N']-ctl['D']; a['N']+=rat['N']
    a['g']+=sum(ref[rat['h']])/len(ref[rat['h']])
lines=['| k | h | primes | mean B | structured | control | integer-base | generic N*B/M | struct/control (95% CI) | (struct - global ref)/control | sum collisions struct / ctl |','|---|---|---|---|---|---|---|---|---|---|---|']
out=[]
for key in sorted(agg):
    a=agg[key]
    if a['c']<5: continue
    r=a['s']/a['c']; se=math.sqrt(1/a['s']+1/a['c']) if a['s']>0 else float('nan')
    lo,hi=r*math.exp(-1.96*se),r*math.exp(1.96*se)
    w=(a['s']-a['g'])/a['c']
    lines.append(f"| {key[0]} | {key[1]} | {int(a['n'])} | {a['B']/a['n']:.0f} | {int(a['s'])} | {int(a['c'])} | {int(a['i'])} | {a['e']:.0f} | {r:.2f} ({lo:.2f}-{hi:.2f}) | {w:.2f} | {int(a['sD'])} / {int(a['cD'])} |")
    out.append(dict(k=key[0],h=key[1],ratio=r,lo=lo,hi=hi,wrapped_ratio=w))
open('table_supp.md','w').write('\n'.join(lines)+'\n'); print('\n'.join(lines))
json.dump(out,open('supp_ratios.json','w'),indent=1)
