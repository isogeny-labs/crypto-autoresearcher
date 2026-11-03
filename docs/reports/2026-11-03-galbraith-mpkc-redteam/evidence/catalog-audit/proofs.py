import pymupdf,re,json,random,collections,sys
A="/tmp/claude-0/-home-user/98db1f19-f745-5cea-bbb2-82920372e57a/scratchpad/catalog-audit/"
sys.path.insert(0,A+"pm1266")
rows=[json.loads(l) for l in open(A+"out2/cat.jsonl")]
doc=pymupdf.open("/tmp/claude-0/-home-user/98db1f19-f745-5cea-bbb2-82920372e57a/scratchpad/src/main.pdf")
K="Theorem|Lemma|Corollary|Proposition|Conjecture|Heuristic|Definition|Example|Remark|Algorithm|Exercise|Notation"
head=re.compile(r"^(%s)(?:\s+((?:[A-Z]\.)?\d+(?:\.\d+)*))?\.?(?:\s|$)"%K)
# build line stream with bold-start flag
stream=[]  # (page, text, boldstart)
for pn,p in enumerate(doc,1):
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines",[]):
            sp=[s for s in l["spans"] if s["text"].strip()]
            if not sp: continue
            t="".join(s["text"] for s in l["spans"]).replace("ﬁ","fi").replace("ﬂ","fl")
            bold="CMBX" in sp[0]["font"]
            stream.append((pn,t,bold))
# headings
H=[]
for i,(pn,t,b) in enumerate(stream):
    if b:
        m=head.match(t.strip())
        if m and (m[2] or m[1] in("Definition","Theorem")) : H.append((i,m[1],m[2],pn))
print(len(H))
idx={}
for j,(i,k,l,pn) in enumerate(H):
    if l: idx[(k,l)]=j
res={}
for r in rows:
    if r['kind'] not in("Theorem","Lemma","Corollary","Proposition"): continue
    if not r['label']: continue
    j=idx[(r['kind'],r['label'])]
    i0=H[j][0]; i1=H[j+1][0] if j+1<len(H) else len(stream)
    seg=stream[i0:i1]
    txt="\n".join(t for _,t,_ in seg)
    pr=[k for k,(pn,t,b) in enumerate(seg) if re.search(r"\bProof\b",t)]
    boldproof=[k for k,(pn,t,b) in enumerate(seg) if t.strip().startswith("Proof") and b]
    res[r['label']]={"kind":r['kind'],"cat":r['book_proof']['status'],"page":r['pdf_page_start'],"has_proof_word":bool(pr),"bold_proof_start":bool(boldproof),"len":len(txt),"txt":txt}
json.dump(res,open(A+"proofseg.json","w"))
c=collections.Counter((v['cat'],v['has_proof_word'],v['bold_proof_start']) for v in res.values())
for k,v in sorted(c.items()): print(k,v)
print("absent but Proof word in segment:")
for l,v in res.items():
    if v['cat']=="absent_in_book" and v['has_proof_word']: print(l,v['page'])
print("non-absent but no proof word:",[(l,v['cat']) for l,v in res.items() if v['cat']!="absent_in_book" and not v['has_proof_word']])

# proof lines ownership
pl=[i for i,(pn,t,b) in enumerate(stream) if b and t.strip().startswith("Proof")]
print("bold Proof lines:",len(pl))
import bisect
starts=[h[0] for h in H]
odd=[]
for i in pl:
    j=bisect.bisect_right(starts,i)-1
    k,l,pn=H[j][1:]
    if k not in("Theorem","Lemma","Corollary","Proposition"): odd.append((stream[i][0],stream[i][1][:60],k,l))
print("Proof lines owned by non-theorem heading:",odd)
