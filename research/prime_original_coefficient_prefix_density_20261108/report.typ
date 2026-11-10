#set page(paper: "a4", margin: 17mm)
#set text(size: 9.5pt)
#set par(justify: false)
= Moment pruning on an original coefficient
Source-only finite h5 interval-chart construction

#image("diagram.svg", width: 100%)

== Direct coefficient rule, without moment auxiliaries
Write A=X³+vX²+A1X+A0, B=qX+B0. Fix original v,q,B0. For target (a,b), the authenticated norm and target rows give u=a+2v−q², S=−u−5t, E=2A1+c with c=(a+4t)u+v²−2qB0+10t², and A0=b(qa+B0)−a³−va²−aA1. Retain every original row and the full projection including A0. No division by target coordinates is used.

An E arc [L,U] pulls back to at most three A1 intervals: [ceil((L−c+mp)/2),floor((U−c+mp)/2)] intersect [0,p−1], for m=0,1,2. Intersect these with an original A1 LSB prefix by signed mathematical floor/ceiling. The clause fixes every v,q,B0 bit and the A1 prefix, leaving A0 and witness bits unassigned. Numeric bit layout is unchanged; no new moment/range blocks are needed. The current contiguous-prefix checker still needs a separately admitted arbitrary-subcube semantic rule.

== Nonvanishing rejection beyond the global bound
Let M=B−1≥1, K=10M² and p>K. Set H to the least power of two at least ceil((K+1)/2), d=log2 H, ell=ceil(log2 p). Then d≤ell−1. Fix a triple whose integer S lies in [0,M]. If G contains the original A1 prefixes admitted by global E in [0,K], the three pullback intervals imply |G|≥ceil((K+1)/3). Conditional E has at most floor(2M²/5)+1 values. The rejected fraction within G is therefore at least

#align(center)[max(0, 1 − (floor(2M²/5)+1) / ceil((10M²+1)/3)).]

The guaranteed lower bound is at least 3/4 for every M≥1 and tends to 22/25 in the stated growing-width regime. It is uniform in the affine shift and qualifying fixed triples. Each S can be realized by choosing v=(q²−a−5t−S)/2; this proves coefficient-domain existence, not a nonempty full relation-root fiber. Unassigned bits need not give independent remaining choices. No search-frequency inference follows.

== Symbolic control, cost and remaining gap
At p17, y²=x³+1, target(0,1), B2,t0,q1,v0,B0=0: S1,E=2A1. Global pullback [0,5] and [9,13] yields six low-three-bit prefixes; conditional E0 retains only prefix0. Five of six are rejected by an 18-literal rule (15 fixed-triple plus3 prefix bits). The critic proved this triple root-empty: U=X⁴(X−1), A1=A0=0, but norm X⁶−X⁵−X² differs from XU. Thus this tests the predicate, not feasible-branch savings. No experiment or census was run. p≤K is outside the no-wrap density theorem; the h4 q0 fiber is outside this h5 transport.

The predicate costs O(h) endpoint operations plus arithmetic/authentication and O(log p) literal work. Charge proof, cache, model and witness verification. The earlier generic two-field extension pays additional compilation/variables; this specialized rule avoids them. Do not enumerate all triples/prefixes to exploit a constant fraction. The remaining gap is charged benefit in an actual search ordering versus existing propagation and direct h5 pair/triple MITM. No regularity reduction is inferred.

#text(size: 8pt)[Review status is recorded in review-disposition.json and independent-review.md. Source: composition.py canonical_chart and charts.py chart_spec; hashes in source-bindings.json. Frozen original-coefficient-draft.md, depth-addendum.md and hand-control.md give the proof. Scope: prospective interval charts, not original six coset cells without transport. All106+6/five leads and existing attempt/cap restrictions remain unchanged.]

