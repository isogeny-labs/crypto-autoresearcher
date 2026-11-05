import json,collections,re
A="/tmp/claude-0/-home-user/98db1f19-f745-5cea-bbb2-82920372e57a/scratchpad/catalog-audit/"
rows=[json.loads(l) for l in open(A+"out2/cat.jsonl")]
cat={(r['kind'],r['label']):r for r in rows if r['label']}
ind=json.load(open(A+"indep.json"))
pl={tuple(k.split("|")):v for k,v in ind["plain"].items()}
bd={tuple(k.split("|")):v for k,v in ind["bold"].items()}
print("cat labelled",len(cat),"plain",len(pl),"bold",len(bd))
print("in bold not cat:",[(k,bd[k]) for k in bd if k not in cat])
print("in cat not bold:",[(k,cat[k]['pdf_page_start']) for k in cat if k not in bd])
print("in plain not cat:",[(k,pl[k]) for k in pl if k not in cat])
print("in cat not plain:",[(k,cat[k]['pdf_page_start']) for k in cat if k not in pl])
print("multi-occ bold:",[(k,v) for k,v in bd.items() if len(v)>1])
print("multi-occ plain:",[(k,v) for k,v in pl.items() if len(v)>1][:20])
# page mismatches
print("page mismatch:",[(k,cat[k]['pdf_page_start'],bd[k]) for k in cat if k in bd and cat[k]['pdf_page_start'] not in bd[k]][:20])
# numbering
sec=collections.defaultdict(list)
for (kd,lb) in set(cat)|set(bd):
    if kd=="Algorithm": continue
    p=lb.split(".")
    sec[".".join(p[:-1])].append(int(p[-1]))
gaps=[];dups=[]
for s,v in sec.items():
    c=collections.Counter(v)
    for n,m in c.items():
        if m>1: dups.append((s,n))
    mx=max(v)
    miss=[i for i in range(1,mx+1) if i not in c]
    if miss: gaps.append((s,miss))
print("gaps",len(gaps),gaps[:80]);print("dups",dups)
print("counts bold-kind",collections.Counter(k[0] for k in bd))
