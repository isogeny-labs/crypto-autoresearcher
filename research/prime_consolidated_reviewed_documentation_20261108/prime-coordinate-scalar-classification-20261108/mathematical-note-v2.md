# Projected scalar certificates in the coordinate encodings

Status: independently reviewed written mathematical derivation (SOURCE-STATIC-ONLY); no candidate imports, execution, samples, or official promotion. Assume p prime >3, s>=1, 2^s<=p, nonsingular curve Y²=X³+aX+b, target (r,t) with t!=0. Primality is an explicit mathematical assumption, not certified by build(). This classifies the coordinate construction used by the 106 coordinate cells, not the six separate coefficient charts. Full 106+6/five-lead target and all chart/projection/witness obligations remain. Both producer slots remain consumed; independent reserved slot untouched.

Sources: research/prime_sat_followup_20261029/encoding.py:36-78 (construction), :81-97 (certificate and prefix); research/prime_sat_prefix_adapter_20261030/adapter.py:110-200 (restriction, identity, projected coverage); research/prime_sat_transform_integration_20261103/engine_counted.py:213-275 (learner and scalar fallback), :442-449 (coordinate build). Separate coefficient chart compilation is research/prime_sat_transform_integration_20261103/transform.py:119. No literature novelty claim. Prior Semaev summation-polynomial literature is background; primary PDF retrieval has not supplied reviewed full text.

## Exact elimination and structural obstruction
Write C=2t, H=xy-r(x+y)-2r²-a, S=x+y+r, and L for auxiliary digit. Lifted originals are g1=L²-S, g2=CL-H. For any assignment to any subset of projected x,y bits, g2 retains the auxiliary bit-i singleton coefficient C2^i!=0. g1 retains auxiliary bit-0 singleton coefficient 1. Thus neither original generator can become a nonzero scalar under projected-only restriction. This remains true if the auxiliary range CNF is considered: L=0,1 are valid, and distinguish each generator. Reversing generator order in quadratic_aa changes nothing. This is a single-generator obstruction, not a prohibition on certificates or polynomial calculus.

The two-generator identity is

    E := H²-C²S = C²g1 -(CL+H)g2.

Using t²=r³+ar+b, direct expansion gives exactly the quartic built by encoding.py:

    E = r²(x-y)² -2r[(x+y)(xy+a)+2b] +(xy-a)² -4b(x+y).

For any projected restriction sigma with E|sigma=c!=0, the multipliers
q1=C²/c, q2=-(CL+H|sigma)/c certify 1 against the restricted lifted generators. Reverse their order for quadratic_aa. No auxiliary assignment is needed. Identity holds first in the ordinary polynomial ring and hence in the Boolean quotient. Multipliers have degree <=2 in Boolean digits, each product degree <=4. If a whole coordinate is fixed, H is affine, q2 degree <=1 and each product degree <=2. These are conditional certificate product bounds; they are not degree-of-regularity measurements. Checking still charges all restricted-generator/multiplier term pairs and inverse cost.

## Quartic scalar cylinders have at most four projected points
For fixed x=u, write E(u,y)=Ay²+By+K, where
A=(u-r)²,
B=-2[r u²+(r²+a)u+ar+2b],
K=(ru+2r²+a)²-C²(u+r).
If u!=r this is genuinely quadratic. If u=r then A=0 and B=-C²!=0, so it is genuinely linear. Therefore for EVERY u, E(u,y)-c is a nonzero polynomial of degree at most two, for any scalar c.

Consider an arbitrary projected bit subcube on which E is constant. If two or more y bits remain free, fix all other free bits, including x. The four resulting y values are distinct modulo p because they are distinct s-bit integers below p. A nonzero degree<=2 polynomial cannot vanish on all four. Contradiction. Symmetry proves at most one free x bit as well. Hence ANY scalar quartic cylinder contains at most four projected assignments, or fixes at least max(0,2s-2) bits. This necessary bound makes no existence or tightness claim. For the current x-first contiguous prefix interface and s>=2, any scalar witness must fix all x bits and at least s-1 y bits, depth >=2s-1; it covers at most two projected assignments. For s=1 use only the general bound unless further classification is given.

After x=u is fixed, if exactly one y bit of weight w is free, y=y0+wz (z Boolean), then E restricts to a scalar precisely when

    w(2Ay0+Aw+B)=0.

Its scalar is Ay0²+By0+K; it is a refutation only when that value is nonzero. If u=r no free bit is possible since wB!=0. This criterion is arithmetic after full x and the other y bits are fixed, not a search over all restrictions. The lift transport above inherits these same projected coverage bounds. It saves auxiliary assignments relative to full-leaf fallback, not arbitrary exponential projected coverage.

## Membership is a different certificate family
Membership adds M_x and M_y, each a Boolean-valued indicator of nonzero nonsquare curve RHS. A restriction gives M_x=1 iff every remaining x completion has nonsquare RHS; it then excludes ALL y completions. For a full invalid x, a one-entry multiplier 1 for M_x is a valid certificate, blocking 2^s partner choices. These predicates are necessary for a curve point; zero RHS stays allowed. For arbitrary subsets the criterion involves all surviving coordinate values; no universally cheap search is asserted. In the existing x-first prefix interface x-only clauses are representable at depth s, while y-only arbitrary-subset clauses are not. Such clauses require a new checker/interface or prefix-compatible restriction; auxiliary literals may never be discarded from an auxiliary-dependent proof.

As further explanation, discriminant_y(E)=4C²(u³+au+b). Thus a nonsquare nonzero curve RHS makes the genuinely quadratic equation rootless over F_p (u=r cannot be this case since target RHS=t²). Membership can summarize rootlessness although E itself remains nonconstant. This is logically stronger pruning than the scalar-quartic family, not a claim about all polynomial certificates or runtime.

The current builder computes each M using 2^(2s) truth-table entries and a 2s-variable Möbius transform. Since the truth function depends on one block, its unique multilinear representative has no other-block support: the paired Möbius differences along an irrelevant bit vanish. A support-local construction can use 2^s entries and the s-variable transform, then embed masks into the appropriate block. This is an exact source-design proposal, not executed code or measured improvement. Charge each predicate test, transform subtraction, mask lift, storage and certificate checking; do not silently exclude preprocessing.

## Ranked next construction and integration boundaries
1. Freeze/review this classification and the explicit lift multipliers, plus the exact one-free-bit criterion. This resolves whether projected scalar fallback can be broad in the actual coordinate encodings.
2. A future source-only design can expose a fixed algebraic elimination-certificate producer and support-local membership constructor, preserving canonical generator order and counted costs. No execution is admitted by this note. Start with current contiguous prefixes, so unchanged certificate schemas can express the result. Do not integrate arbitrary-S clauses through the prefix-only checker.
3. To obtain broader coordinate pruning, investigate rootlessness/membership certificates or combinations of generators beyond scalar E; running larger scalar-only searches cannot evade the proved coverage bound. The separate coefficient charts need their own classification.

The engine currently schedules only {0,s,2s,n} in run_cell (lines447-448), omitting depth2s-1 for s>1; it full-restricts all n bits at fallback and emits only depth-n clauses. The <=2 bound classifies the representable prefix family, not prefixes the current engine necessarily tries. It does not yet implement this transfer or the shorter-prefix criterion. Any comparison must retain complete projected model sets, witness reconstruction, chart coverage, certificate/coverage verification, and all cost accounting. No claims about general polynomial-calculus lower bounds, SAT hardness, regularity reduction, or measured speedup follow from this source-only classification.


# Coverage consequence (additional frozen review input)

Assume the derivation's prime-field coordinate chart and M=2^s. For each full x value, E(x,y) is a nonzero polynomial of degree at most two in y, so it has at most two roots among the M allowed coordinate values. Consequently the number of valid projected pairs is at most 2M (each valid pair must satisfy E=0). Thus N_bad >= M²-2M. This bound is useful for s>=2 and asymptotic only along eligible larger charts; no existence of an infinite chosen curve/parameter sequence is needed for its per-instance form.

Suppose a complete coverage argument covers every invalid projected pair solely by clauses whose excluded cylinders have certificates E|sigma=c!=0, either as scalar original-quartic certificates or via the explicit lifted two-generator transport. Each such arbitrary-S cylinder covers at most four projected pairs; each current ordered prefix covers at most two for s>=2. Their union has cardinality at most the sum of these cardinalities, even with overlap. Hence at least ceil(N_bad/4) arbitrary-S clauses, or ceil(N_bad/2) ordered-prefix clauses, are necessary for this restricted family. In particular the bounds ceil((M²-2M)/4) and ceil((M²-2M)/2) apply. The number of these clauses is Omega(M²) as M grows.

This is a coverage/counting lower bound for this precisely restricted rejection family. It does not bound all PC certificates, SAT resolutions/learned clauses, membership predicates, auxiliary-dependent rejection plus domain reasoning, coefficient-chart encodings, or degree of regularity. If another family covers some invalid pairs, the counting conclusion applies only to pairs left to this family. The current engine may use other PC proofs: no claim that its total behavior must meet this restriction is made.

Decision implication: do not scale this scalar-E-only family expecting broad projected pruning. Explicit lift transfer remains a bounded certificate construction, and membership/rootlessness mechanisms are structurally different next proposals. No scientific runtime or new attempt is authorized.

## Written review disposition

Independent review found no substantive algebraic defect. Its scope is mathematical derivation and cited source only; the supplied106+6 inventory, five-lead context and budget custody are administrative continuity, not newly audited by this review. Frozen v1 inputs and review remain retained. No execution or official status promotion follows. Source-bindings.json records exact inspected file hashes.
