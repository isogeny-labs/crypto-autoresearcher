"""Render a construction diagram and report; performs no research trials."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst
D=Path(__file__).resolve().parent
fig,ax=plt.subplots(figsize=(10,4.4));ax.set_xlim(0,10);ax.set_ylim(0,4.4);ax.axis('off')
boxes=[(1.8,3.6,'#58 Orbit equations\nExact norms and rational lifts'),(7.5,3.6,'#69 Local bases\nDual maps and normalization'),(1.8,2.1,'#56 Parameter constraints\nShifts and root-readiness gates'),(7.5,2.1,'#71 Membership\nFactored equations and pole checks'),(4.7,.55,'#87 Fixed-base verifier\nFull signed sum; exhaustive controls')]
for x,y,t in boxes:
 ax.text(x,y,t,ha='center',va='center',fontsize=11,bbox=dict(boxstyle='round,pad=.6',fc='#e9f3f9',ec='#386381'))
for a,b in [((1.8,3.1),(1.8,2.6)),((7.5,3.1),(7.5,2.6)),((1.8,1.6),(3.7,.95)),((7.5,1.6),(5.8,.95))]:
 ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='->',color='#386381',lw=1.5))
fig.text(.5,.015,'Construction dependencies; arrows do not assert measured performance or completed pipeline integration.',ha='center',fontsize=9)
fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(D/'pipeline.svg');plt.close(fig)
svg = D/'pipeline.svg'
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
source='''#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
#set heading(numbering: "1.")
= Five prime-field IC directions
*Construction round — directions 58, 69, 71, 56 and 87*

Seven deterministic software checks pass. This report records exact constructions and their finite regression scope. The proposed scaling and performance panels have not run. Source base: `a0ca384c7a6984bcba83cf9ffa7f49f590e4612b`.

#image("pipeline.svg", width: 100%)

== Invariant elimination (58)
The implemented norm is `Res_y(y^k-v, Res_x(x^k-u, f3(x,y,z)))`, with k=2 for j=1728 and k=3 for j=0. Generic symbolic expansion gives:
#table(columns: 4, [Case], [Degree in u,v], [Degree in z], [Terms], [k=2], [4 each], [8], [45], [k=3], [6 each], [18], [175])
These are exact sizes over the integer polynomial ring, not timings. Every z exponent is divisible by k, permitting exact target compression w=z^k. The prototype retains rational lifting and signs; it does not identify resultant zeros with rational decompositions. F13 fixtures check all invariant pairs and automorphism scalar action on the selected prime subgroup.

== Transport and membership (69, 71)
For y²=x³+A x²+B x, the rational degree-2 map is (x+A+B/x, y(1−B/x²)). Applying the same construction to its target and scaling by (1/4,1/8) gives the dual. Both dual compositions and every rational point-pair homomorphism identity pass on the F101 fixture. Odd-prime subgroup normalization passes. A later coverage audit found zero internal relation tuples in the window fixture (base sizes 2 and 0), so its row-identity loop was vacuous; relation-row coverage is not claimed.

Membership uses factors N−sD with D nonzero. The recurrence N′=N²+A ND+B D², D′=ND retains shared map structure. Four coordinate values and chain lengths 0–3 agree with direct rational evaluation for all F101 elements. This fixture has no certified crater/floor labels.

#pagebreak()
== Lattices with the actual families (56)
The imported repository builders define small_x, multiplicative-coset and Dickson bases. The prototype uses x=t or x=t+c/t with the original coset constraints, not an invented replacement family. Chained m=3/4 summation equations retain internal coordinates and pole exclusions.

The shift builder records exact bound scaling and decoding. An l1 box bound strictly below the modulus certifies integer vanishing, conditional on modular vanishing and the stated root bounds. A separate ideal-dimension check rejects inconsistent or positive-dimensional systems as completed root extraction. A univariate positive control exercises LLL. Multivariate Semaev root recovery remains to be implemented and established.

== Fixed-base controls (87)
The complementary-point generator keeps each original base fixed. Tests compare all accepted signed arity-3/4 plants with exhaustive tuple oracles. Wrong targets and outside-base points are rejected through the same predicate. Trivial and duplicate rows are retained in this completeness test and must be classified in a future collector. Historic screening stages are not claimed replayed.

== Validation and custody
`checks/python39-import-failure.txt` preserves the first invocation’s Python 3.9 incompatibility. `checks/python311-tests.txt` records six passing tests. `checks/python311-final-tests.txt` records seven after adding compression and root-readiness checks. Limits were one process, 2 GiB, 180 seconds per invocation, three invocations total. Runner durations are not performance measurements. No EKS job or cloud experiment was launched.

Migration reconciliation preserved the working files and logs, inspected existing external ownership, and restarted no generator or unrelated job. See `migration-reconciliation.md`.

== Next technical work
- 58: exact solution-set equivalence between lifted equations and compressed invariant equations, then solver instrumentation.
- 69: connect digit solvers and certify endpoint conductors before level comparisons.
- 71: implement the nonexpanded straight-line circuit and count its actual operations.
- 56: joint shifts with truthful internal-coordinate bounds, followed by certified integer equations and root extraction.
- 87: integrate fixed-base plants into actual mitm screening and record the first rejecting stage.

Each measurement requires its own frozen protocol and launch admission. No official hypothesis or frontier status changes here.

== Sources and replay
Full provenance and limitations are in `SOURCES.md`; commands are in `README.md`. Primary retrieved sources: Kosters–Yeo, “Notes on summation polynomials,” arXiv:1503.08001v3, §2; SageMath isogeny reference (rational maps, duals and model isomorphisms). Semaev’s original PDF returned HTTP 403. Current repository factor-base and curve implementations were read directly. The KB search tool was unavailable; historical results were not independently re-reviewed.
'''
(D/'report.typ').write_text(source)
typst.compile(str(D/'report.typ'),output=str(D/'report.pdf'))
