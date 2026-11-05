import json,sys,collections
rows=[json.loads(l) for f in sys.argv[1:] for l in open(f)]
agg=collections.defaultdict(lambda: collections.defaultdict(float))
for r in rows:
    key=(r['k'],r['h'] if r['variant']!='integer' else 'int',r['variant'] if r['variant']!='integer' else 'integer')
for r in rows:
    if r['variant']=='integer': continue
    pass
by=collections.defaultdict(dict)
for r in rows: by[(r['k'],r['p'],r['h'] if r['variant']!='integer' else None, )] if False else None
# group by (k,p,h): rational+control share h; integer has h=B so index by order
i=0
cells=[]
while i<len(rows):
    cells.append(rows[i:i+3]); i+=3
agg=collections.defaultdict(lambda: collections.defaultdict(float))
for rat,ctl,itg in cells:
    a=agg[(rat['k'],rat['h'])]
    a['n']+=1; a['B']+=rat['B']
    for nm,r in (('rat',rat),('ctl',ctl),('int',itg)):
        a[nm+'_trip']+=r['triples']; a[nm+'_dist']+=r['triples_distinct_xR']; a[nm+'_N']+=r['N']; a[nm+'_D']+=r['D']
        a[nm+'_exp']+=r['N']*r['B']/(r['p']/2)
    a['rat_glob']+=rat['listed_global']; a['rat_wr']+=rat['listed_wrapped']; a['rat_hits']+=rat['hits']; a['ctl_hits']+=ctl['hits']
print('k h n B | rat_trip(glob/wr) ctl_trip int_trip | expected_generic | D/N rat ctl')
for key in sorted(agg):
    a=agg[key]
    print(key,int(a['n']),int(a['B']/a['n']),'|',int(a['rat_trip']),f"({int(a['rat_glob'])}/{int(a['rat_wr'])})",int(a['ctl_trip']),int(a['int_trip']),'|',round(a['rat_exp'],2),round(a['ctl_exp'],2),'|',round(a['rat_D']/a['rat_N'],6),round(a['ctl_D']/a['ctl_N'],6))
