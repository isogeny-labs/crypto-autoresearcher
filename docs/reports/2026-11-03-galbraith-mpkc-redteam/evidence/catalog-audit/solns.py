import pymupdf,re,json,collections
A="/tmp/claude-0/-home-user/98db1f19-f745-5cea-bbb2-82920372e57a/scratchpad/catalog-audit/"
rows=[json.loads(l) for l in open(A+"out2/cat.jsonl")]
ex={r['label']:r for r in rows if r['kind']=="Exercise"}
d=pymupdf.open("/tmp/claude-0/-home-user/98db1f19-f745-5cea-bbb2-82920372e57a/scratchpad/src/main.pdf")
# locate Appendix B
for pn in range(600,640):
    t=d[pn-1].get_text("text")[:300].replace("\n"," ")
    if "Appendix B" in t or "APPENDIX B" in t or "HINTS" in t.upper() and "SOLUTIONS" in t.upper(): print(pn,t[:150])
