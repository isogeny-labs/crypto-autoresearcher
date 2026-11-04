import pymupdf,re,json,collections
A="/tmp/claude-0/-home-user/98db1f19-f745-5cea-bbb2-82920372e57a/scratchpad/catalog-audit/"
rows=[json.loads(l) for l in open(A+"out2/cat.jsonl")]
labels={r['label'] for r in rows if r['label'] and r['kind']!='Algorithm'}
alg={r['label'] for r in rows if r['kind']=='Algorithm'}
cats={(r['kind'],r['label']) for r in rows if r['label']}
doc=pymupdf.open("/tmp/claude-0/-home-user/98db1f19-f745-5cea-bbb2-82920372e57a/scratchpad/src/main.pdf")
rx=re.compile(r"\b(Theorem|Lemma|Corollary|Proposition|Conjecture|Heuristic|Definition|Example|Remark|Exercise)s?\s+((?:[A-Z]\.)?\d+\.\d+(?:\.\d+)?)")
miss=collections.defaultdict(list); kindmis=collections.defaultdict(list)
for pn,p in enumerate(doc,1):
    if pn>600: pass
    t=p.get_text("text").replace("ﬁ","fi").replace("\n"," ")
    for m in rx.finditer(t):
        if m[2] not in labels: miss[(m[1],m[2])].append(pn)
        elif (m[1],m[2]) not in cats: kindmis[(m[1],m[2])].append(pn)
print("mentions of labels with no object at all:",len(miss))
for k,v in sorted(miss.items()): print(k,v[:5])
print("kind mismatch (label exists as different kind):",len(kindmis))
for k,v in sorted(kindmis.items())[:40]: print(k,v[:3])
