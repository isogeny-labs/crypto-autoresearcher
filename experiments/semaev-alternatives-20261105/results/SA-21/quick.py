import json,sys,collections,statistics as st
def load(f): return [json.loads(l) for l in open(f)]
for f in sys.argv[1:]:
    rs=load(f); d=collections.defaultdict(list)
    for r in rs: d[(r['fam'],r['k'])].append(r)
    for key in sorted(d, key=lambda t:(t[0],t[1])):
        v=d[key]; print(f.split('/')[-1],key,'n',len(v),'ok',sum(r['ok'] for r in v),'wall ms',round(1000*st.mean(r['wall'] for r in v),3),'adds',int(st.mean(r['adds'] for r in v)),'t_gae ns',round(1e9*st.mean(r['t_gae'] for r in v),1))
