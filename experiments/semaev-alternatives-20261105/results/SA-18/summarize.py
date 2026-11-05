import json,glob,collections
rows=[]
for f in sorted(glob.glob('out_*.txt')):
    for l in open(f):
        if l.startswith('{'): rows.append(json.loads(l))
json.dump(rows,open('all_rows.json','w'))
# threshold: largest delta such that success rate >=1/2 for all smaller delta tested (per bits,curve,t,N); then best over N
G=collections.defaultdict(list)
for r in rows: G[(r['curve'],r['t'],r['bits'],r['N'])].append(r)
th={}
lines=["curve,t,bits,N,dim,thr_delta(>=50%),first_delta_below_50%,max_mean_ncert"]
for k,v in sorted(G.items()):
    v.sort(key=lambda r:r['delta']); thr=0.0
    for r in v:
        if r['success']/r['trials']>=0.5: thr=r['delta']
        else: break
    nxt=next((r['delta'] for r in v if r['delta']>thr),None)
    th[k]=thr
    lines.append(f"{k[0]},{k[1]},{k[2]},{k[3]},{(k[3]+1)**2},{thr},{nxt},{max(r['mean_ncert'] for r in v):.1f}")
open('thresholds.csv','w').write("\n".join(lines)+"\n")
print("\n".join(lines))
best=collections.defaultdict(lambda:(0,0))
for k,thr in th.items():
    key=(k[0],k[1],k[2])
    if thr>best[key][0]: best[key]=(thr,k[3])
print("\nBEST over N (curve,t,bits)->(thr,N)");
for k,v in sorted(best.items()): print(k,v)
