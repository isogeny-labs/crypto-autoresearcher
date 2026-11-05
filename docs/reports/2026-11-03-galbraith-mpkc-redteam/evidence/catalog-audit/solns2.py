import sys
sys.path.insert(0,sys.argv[1]) if sys.argv[1]!='-' else None
import pymupdf,re,json,collections
A="/tmp/claude-0/-home-user/98db1f19-f745-5cea-bbb2-82920372e57a/scratchpad/catalog-audit/"
rows=[json.loads(l) for l in open(A+"out2/cat.jsonl")]
ex={r['label']:r for r in rows if r['kind']=="Exercise"}
cat={l for l,r in ex.items() if r['appendix_b_hint_or_solution']['detected']}
print(pymupdf.__version__,"catalog detected",len(cat))
d=pymupdf.open("/tmp/claude-0/-home-user/98db1f19-f745-5cea-bbb2-82920372e57a/scratchpad/src/main.pdf")
found=collections.defaultdict(set); lastpage=None
rx=re.compile(r"^\s*(\d+\.\d+\.\d+)\s*[:：]")
for mode in ("plain","sorted","dictline"):
    found=collections.defaultdict(set)
    for pn in range(605,697):
        if mode=="plain": lines=d[pn-1].get_text("text").split("\n")
        elif mode=="sorted": lines=d[pn-1].get_text("text",sort=True).split("\n")
        else:
            lines=[]
            for b in d[pn-1].get_text("dict")["blocks"]:
                for l in b.get("lines",[]): lines.append("".join(s["text"] for s in l["spans"]))
        for ln in lines:
            m=rx.match(ln)
            if m: found[m[1]].add(pn)
    ind={l for l in found if l in ex}
    notex=[l for l in found if l not in ex]
    print(mode,"entries",len(found),"exercise-labelled",len(ind),"not exercise:",notex[:10],
          "ind-not-cat",sorted(ind-cat)[:20],"cat-not-ind",sorted(cat-ind)[:20])
    if mode=="dictline": json.dump({k:sorted(v) for k,v in found.items()},open(A+"solnfound.json","w"))
print("last pages",max(p for v in found.values() for p in v))
