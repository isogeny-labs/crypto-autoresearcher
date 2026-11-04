import sys,json,re,collections
sys.path.insert(0,sys.argv[1])
import pymupdf
A="/tmp/claude-0/-home-user/98db1f19-f745-5cea-bbb2-82920372e57a/scratchpad/catalog-audit/"
rows=[json.loads(l) for l in open(A+"out2/cat.jsonl")]
ex={r['label']:r for r in rows if r['kind']=="Exercise"}
cat={l for l,r in ex.items() if r['appendix_b_hint_or_solution']['detected']}
d=pymupdf.open("/tmp/claude-0/-home-user/98db1f19-f745-5cea-bbb2-82920372e57a/scratchpad/src/main.pdf")
rx=re.compile(r"^\s*(\d+\.\d+\.\d+)\s*(?::|\s+See\b)")
found=collections.defaultdict(set)
for pn in range(605,697):
    for b in d[pn-1].get_text("dict")["blocks"]:
        for l in b.get("lines",[]):
            m=rx.match("".join(s["text"] for s in l["spans"]))
            if m: found[m[1]].add(pn)
inex={l for l in found if l in ex}
print("entries",len(found),"matching exercise labels",len(inex),"non-exercise",[l for l in found if l not in ex])
print("catalog-only",sorted(cat-inex),"indep-only count",len(inex-cat))
# ordering sanity: entries per chapter vs sequential
# exercises with entry label but exercise-section? check entries sorted appear in nondecreasing order
order=[]
for pn in range(605,697):
    for b in d[pn-1].get_text("dict")["blocks"]:
        for l in b.get("lines",[]):
            m=rx.match("".join(s["text"] for s in l["spans"]))
            if m: order.append(tuple(int(x) for x in m[1].split(".")))
print("monotone violations",sum(1 for a,b in zip(order,order[1:]) if b<a), len(order))
json.dump(sorted(inex),open(A+"solnlabels_indep.json","w"))
