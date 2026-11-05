import pymupdf,re,json,collections
A="/tmp/claude-0/-home-user/98db1f19-f745-5cea-bbb2-82920372e57a/scratchpad/catalog-audit/"
rows=[json.loads(l) for l in open(A+"out2/cat.jsonl")]
cats={(r['kind'],r['label']) for r in rows if r['label']}
doc=pymupdf.open("/tmp/claude-0/-home-user/98db1f19-f745-5cea-bbb2-82920372e57a/scratchpad/src/main.pdf")
K="Theorem|Lemma|Corollary|Proposition|Conjecture|Heuristic|Definition|Example|Remark|Algorithm|Exercise|Notation"
rx=re.compile(r"\b(%s)\b"%K)
fonts=collections.Counter(); found=collections.Counter(); extra=[]
for pn,p in enumerate(doc,1):
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines",[]):
            sp=l["spans"]
            for i,s in enumerate(sp):
                t=s["text"].replace("ﬁ","fi")
                if "CMBX" in s["font"] or "Bold" in s["font"]:
                    fonts[s["font"]]+=1
                    m=rx.fullmatch(t.strip())
                    if m:
                        # find label in following spans
                        rest="".join(x["text"] for x in sp[i+1:i+4]).strip()
                        mm=re.match(r"((?:[A-Z]\.)?\d+(?:\.\d+)*)",rest)
                        key=(m[1],mm[1].rstrip(".") if mm else None)
                        found[key]+=1
                        if key not in cats and key[0]!="Notation": extra.append((key,pn,i==0,"".join(x["text"] for x in sp)[:70]))
print(fonts.most_common(8)); print(len(found)); 
for e in extra: print(e)
