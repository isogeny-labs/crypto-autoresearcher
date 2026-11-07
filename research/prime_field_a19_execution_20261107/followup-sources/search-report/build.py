"""Static source follow-up and proposed discriminator; no native experiment."""
from pathlib import Path
import hashlib,json,subprocess
import typst
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
relative=str(Path(__file__).resolve().relative_to(ROOT))
if subprocess.check_output(['git','show','HEAD:'+relative],cwd=ROOT)!=Path(__file__).read_bytes():raise ValueError('publish source report builder first')
svg='''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="300" viewBox="0 0 960 300">
<defs><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6" fill="#34576d"/></marker></defs>
<g font-family="sans-serif" font-size="17" fill="#163549">
<rect x="10" y="15" width="285" height="95" rx="8" fill="#e6f0f5"/><text x="25" y="42">A19 finite producer panel</text><text x="25" y="67">unknown16: 22/32 targets</text><text x="25" y="92">Cancel aux AND target U</text>
<rect x="340" y="15" width="610" height="95" rx="8" fill="#edf3e7"/><text x="355" y="42">Existing generic ingredients: pair sums and sparse relations</text><text x="355" y="67">Z_aux = sign_i Z_i + sign_j Z_j; numeric logs unknown</text><text x="355" y="92">Construction, signs, aliases and all queries must be paid</text>
<rect x="10" y="180" width="410" height="100" rx="8" fill="#f5eddf"/><text x="25" y="207">Primary source: successful-work gap</text><text x="25" y="232">Support / presentation degree alone</text><text x="25" y="257">does not price successful decomposition</text>
<rect x="490" y="180" width="460" height="100" rx="8" fill="#eef0f6"/><text x="505" y="207">Unexecuted question: paid formal-pair16</text><text x="505" y="232">versus coordinate-hash unknown16</text><text x="505" y="257">Fresh targets, same old base, exact Delta + costs</text>
</g><g stroke="#34576d" fill="none" stroke-width="2" marker-end="url(#a)"><path d="M295,60 H330"/><path d="M650,110 V175" stroke-dasharray="7,5"/><path d="M420,230 H480" stroke-dasharray="7,5"/></g></svg>'''
(HERE/'source-map.svg').write_text(svg)
doc='''#set page(paper:"a4",margin:16mm)
#set text(size:9pt)
= Follow-up sources: dependent auxiliary points
Four plain organization queries covered pair-sum factor bases and dependent/formal auxiliary logarithms. All returned excerpts are retained in ../retrieval.json. Two complete crypto primary texts were fetched at commit 7ec6459ef1afa599735f9ce387c7d73fee7ea8b4; exact Git blob checks and SHA256/bytes are in ../primary-integrity.json. Root read both full texts. This is a scoped static source follow-up, not a corpus-wide absence claim, native replay or independent scientific review.

#image("source-map.svg",width:100%)
Solid edge: retained finite producer observation and existing algebraic ingredients. Dashed edges: proposed future discriminator, not tested improvements or verified performance.

== What the sources contribute
The current problem record “factor-base-shape-to-successful-work” explicitly leaves successful native decomposition, setup, membership, witness selection and independent relation rank unpriced even where finite support improves. Its later same-base recoding continuation separately reports canonical presentation-degree facts and still requires measured branch-summed work. No proof or performance standing transfers from this source read.

The historical prime-field synthesis provides background on structured bases, descent and generic relation search. Its broad presentation-invariance/no-go and initial-minor narratives are not adopted as proved facts here; current successful-work obligations require an actual system/order/certificate and matched execution. It does not establish impossibility of the proposed finite engineering comparison. Search also locates existing binary-field pair-sum/coverage selectors; those are prior methods and different field scopes, not a prime-field improvement receipt.

== Concrete next question, still unexecuted
A public point A = sign_i B_i + sign_j B_j has an exact formal logarithm relation even when none of the three numeric logarithms is known. A fixed sixteen-point dictionary built this way could be compared with A19's coordinate-hash unknown16 and independently paid known16, on the unchanged old norm base and fresh public targets. Definition rows alone add zero old-base information after eliminating A; any contribution must come from actual collected relations or explicit own public coincidences.

Freeze first-success pair/sign/alias rules before targets, charge all draws/construction/rejections/storage, retain the definition equations in native matrices and K attribution, and prohibit using unknown numeric labels in the P constructor. Query all mixed geometries; keep complete auxiliary-and-target cancellation and original-native/dense/kernel certificates. Composite three-sum rows may merely realize higher-arity generic old-base sums; no new algebra, symmetry, exponent, rho or novelty claim is proposed. The question is finite useful information and named target recovery at paid costs.

A19 raw publication a58e290e7d45c21e9d84ed012fef2029e8ea2b0a records targets11/32 norm,22/32 unknown16 and30/32 known16. Those are producer-unverified under PCC-20261107-c76c01, with separate unweighted costs and nonrecoveries. Source search and this candidate do not allocate another attempt or reset the original deadline. Prym B1/B2 and Dickson depth4 already executed in their recorded finite scopes; their historical “unexecuted” continuation notes are not current run status.
'''
(HERE/'report.typ').write_text(doc)
typst.compile(str(HERE/'report.typ'),output=str(HERE/'report.pdf'),root=str(ROOT))
value=dict(schema='prime-field-source-report/v1',kind='static_source_followup_no_new_native_experiment',pdf_sha256=hashlib.sha256((HERE/'report.pdf').read_bytes()).hexdigest(),inspection_required=True)
(HERE/'render.json').write_text(json.dumps(value,indent=2)+'\n')
print(json.dumps(value))
