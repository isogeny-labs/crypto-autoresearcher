import sys,re,json,collections
sys.path.insert(0,sys.argv[1]) if len(sys.argv)>1 and sys.argv[1]!='-' else None
import pymupdf
print(pymupdf.__version__)
P="/tmp/claude-0/-home-user/98db1f19-f745-5cea-bbb2-82920372e57a/scratchpad/src/main.pdf"
A="/tmp/claude-0/-home-user/98db1f19-f745-5cea-bbb2-82920372e57a/scratchpad/catalog-audit/"
K="Theorem|Lemma|Corollary|Proposition|Conjecture|Heuristic|Definition|Example|Remark|Algorithm|Exercise|Notation"
rx=re.compile(r"^(%s)\s+((?:[A-Z]\.)?\d+(?:\.\d+)*)"%K)
doc=pymupdf.open(P)
plain={}  # (kind,label)->pages
bold={}
for pn,page in enumerate(doc,1):
    for line in page.get_text("text").replace("\ufb01","fi").replace("\ufb02","fl").split("\n"):
        m=rx.match(line.strip())
        if m: plain.setdefault((m[1],m[2]),[]).append(pn)
    d=page.get_text("dict")
    for b in d["blocks"]:
        for l in b.get("lines",[]):
            sp=[s for s in l["spans"] if s["text"].strip()]
            if not sp: continue
            # join leading bold spans
            t="";
            for s in sp:
                if "Bold" in s["font"] or "CMBX" in s["font"] or s["flags"]&16: t+=s["text"].replace("\ufb01","fi").replace("\ufb02","fl")
                else: break
            m=rx.match(t.strip())
            if m: bold.setdefault((m[1],m[2]),[]).append(pn)
json.dump({"plain":{"|".join(k):v for k,v in plain.items()},"bold":{"|".join(k):v for k,v in bold.items()}},open(A+"indep.json","w"))
print(len(plain),len(bold))
