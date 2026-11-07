"""Visual note for retrieved sources and the ranked next question; no experiment."""
from pathlib import Path
import json,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]

def text(value):return '#text('+json.dumps(str(value),ensure_ascii=False)+')'
fig,ax=plt.subplots(figsize=(10,3.3));ax.axis('off')
nodes=[(.02,.70,'Retained residual-LP lead\nH-PFDR-cb9606', '#e4eef4'),(.36,.70,'Full primary reports\ncrypto, October 26','#e4eef4'),(.70,.70,'November 1 correction\nbytes are not operations','#f1e8d7'),(.02,.18,'A1/A2 finite cancellation\nold p4099 fixtures','#e4eef4'),(.49,.18,'Ranked prospective comparison\nfixed norm32 + unknown16\nscore after auxiliary + target cancellation','#e4ede3')]
for x,y,label,color in nodes:ax.text(x,y,label,transform=ax.transAxes,fontsize=9,va='center',bbox=dict(boxstyle='round,pad=.5',facecolor=color,edgecolor='#aab7bc'))
for a,b,style in [((.27,.7),(.35,.7),'-'),((.63,.7),(.69,.7),'-'),((.80,.55),(.73,.36),'--'),((.32,.18),(.48,.18),'--')]:ax.annotate('',xy=b,xytext=a,xycoords='axes fraction',arrowprops=dict(arrowstyle='->',linestyle=style,color='#4b6571'))
fig.tight_layout();fig.savefig(HERE/'source-map.svg');plt.close(fig)
doc='#set page(paper:"a4",margin:17mm)\n#set text(size:10pt)\n= Prior sources and the next information test\n'
doc+=text('Literature/source search on 2026-11-07. This note records retrieved sources and a prospective ranking; it performs no native experiment, scientific replay or official status transition.')+'\n\n#image("source-map.svg",width:100%)\n'
doc+=text('Solid arrows link source records and their later correction. Dashed arrows identify a different prospective question; they imply no measured advantage or execution allowance.')+'\n\n'
doc+='== What was checked\n'
doc+=text('Organization GitHub search returned the residual-partial-relations lead, H-PFDR-cb9606, and sibling crypto reports. Both full primary READMEs were fetched at crypto commit a1829d09d94c4a54220ab476b0a944610df2b46a. The retained copies match their retrieved Git blob hashes: 0d7509cd0fbec3824d4c51d39f7e0ed43013a285 and a4d9e2f624c76e613ee18a79877efbde49261755. Queries/results, URLs, copies and SHA256 checks are adjacent in retrieval.json and primary-integrity.json. Root also read A1/A2 results, the A14 unknown-pool worklist, query_index and the affine Registry. This is source verification, not independent validation of those experiments.')+'\n\n'
doc+='== Interpretation that the sources support\n'
doc+=text('Residual endpoints R plus/minus base points, retained and paired by collision, are an existing large-prime mechanism. The primary reports classify it as generic collision search using curve-free controls. Both append a November1 correction: byte counters were removed from operation pricing. Historical statements that it loses to the IC plan at weight1 use the earlier byte price and must not be repeated as the corrected conclusion. The reported generic interpretation and remaining gap to rho are separate from that pricing correction. No new numerical advantage or novelty claim is made here.')+'\n\n'
doc+='== A distinct next bounded question\n'
doc+=text('The administrative next-leads note ranks a fresh comparison on a fixed old norm32 base: no auxiliary pool,16 public coordinate-drawn points without supplied logs, and a separately paid known16 control. Keep source AP0/128 and GENERAL8 fixed, own construction/caches and all queries. Compare old-base information only after eliminating both auxiliary16 and requested-target8 columns: Delta = rank([[M,0],[B,U]]) - rank(U) - rank(M). M uses the same source-only old-base coordinates; constructor anchors remain owned paid additions. Native certificates, outside cancellation and individual target membership must be checked without requiring full old-base rank. Raw augmented rank and introduced unknowns are not information. No unknown-base query suppression is authorized.')+'\n\n'
doc+=text('A18 itself remains a separate completed finite panel:29 of32 public targets recovered by both programs, with3 nonrecoveries retained; PCC-20261107-f778b2 is producer-unverified/not covered. The new ranking grants no protocol, attempt allowance, capacity, deadline reset, signed proof or scientific status. Literature retrieval is limited to the stated repository/primary sources; no corpus-wide absence or novelty is inferred. Research-kb remains unavailable under the carried direct-source fallback.')+'\n'
(HERE/'report.typ').write_text(doc);typst.compile(str(HERE/'report.typ'),output=str(HERE/'report.pdf'),root=str(ROOT))
(HERE/'render.json').write_text(json.dumps(dict(renderer='typst',pdf_sha256=hashlib.sha256((HERE/'report.pdf').read_bytes()).hexdigest(),native_experiments=0,scope='source-search and administrative ranking diagram only',inspection_required=True),indent=2)+'\n')
print(str(HERE/'report.pdf'))
