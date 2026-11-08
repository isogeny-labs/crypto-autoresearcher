# Original h5 coefficient transport and conditional prefix density

UNREVIEWED. This strengthens the auxiliary-domain draft; it does not infer search speed or regularity.

Source: canonical_chart in research/prime_sat_full_chart_composition_20261101/composition.py lines156–181, chart_spec/basis in research/prime_sat_shared_signed_chart_20261030/charts.py. Finite target (a,b) on y²=x³+alpha x+beta; use alpha,beta for curve coefficients. h5 has poledegree6, normalization A=X³+vX²+A1X+A0, B=qX+B0 and norm A²−fB²=(X−a)U. Its target row is A(a)−bB(a)=0, so A0=b(qa+B0)−a³−va²−A1*a, with no target-coordinate division. The leading norm rows give u=a+2v−q² and j=au+v²+2A1−2qB0. These follow by equating X5 and X4 coefficients.

Fix original coefficient values v,q,B0 consistent with the chosen B stratum; retain all original source rows and all other chart obligations. Then S0=canonical(−u−5t) is fixed and

 E=2A1+c modp,
 c=canonical((a+4t)u+v²−2qB0+10t²).

This is a bijection from the original A1 field to E. Target elimination can be viewed solely as reconstruction, not modification of the original source: every original root obeys it, and for each A1 the target row uniquely fixes A0. No extension variables are needed for the proposed semantic clause, but its source authentication must verify the exact rows and chart premise. The original projection remains the full coefficient tuple including reconstructed A0. Full models still need all original constraints/witness checks; no row may be dropped.

For a canonical E arc[L,U], its exact A1 preimage is the union for m=0,1,2 of

 [ceil((L−c+mp)/2), floor((U−c+mp)/2)] intersect [0,p−1].

Indeed 0<=2A1+c<=3p−3; taking its canonical residue uses precisely these possible quotients. Empty intervals are discarded. For an original A1 LSB prefix r at depth d, intersect each interval[I,J] using ceil((I−r)/2^d)<=floor((J−r)/2^d). Signed mathematical floor/ceiling is essential. This works with the earlier full lift/arc algorithm, at most6h intervals, O(h) endpoint operations, plus parsing/authentication and literals. No moment fields or new range-state blocks are introduced in this specialized construction. The baseline two-field design still costs2ell+2g bits; do not claim it free or mandatory here.

Quantitative regime: M=B−1>=1, K=10M², h=5, 5M<p, H=2^ceil(log2(K+1))<p. Let d=log2H, ell=ceil(log2p); then d<ell. Fix a coefficient triple giving integer S0 in[0,M]. The global interval E in[0,K] has exactly K+1 preimage values since K<p. Its preimage is at most three intervals, each with at most floor(K/2)+1<=H integers. Each interval has distinct low-d prefixes. Thus if G is the set of original A1 prefixes having any global-envelope completion, |G|>=ceil((K+1)/3).

The exact necessary conditional moment interval for this S0 is[0,Emax(S0)], since packed offsets give Emin=0 for S0<=M; balanced offsets give Emax<=2S0²/5<=K/25. Let C be the A1 prefixes having a conditional-envelope completion. C is a subset of G and |C|<=floor(K/25)+1. The semantic predicate rejects every prefix in G minus C; all such prefixes have canonical global-envelope completions. Therefore the rejected fraction is at least

 max(0, 1−(floor(K/25)+1)/ceil((K+1)/3)),

which tends to22/25 as M grows in this prime/width regime. Uniformity is over shift c and fixed coefficient triples with S0 in[0,M], not over solver trajectories. At least one A1 bit is syntactically unassigned. Some global prefixes may already determine a unique completion; no residual branching-factor claim follows. For M=1, K10 the bound is3/4; no enumeration is required.

There are actual original coefficient triples realizing every S0 in[0,M]: choose q,B0 in the intended nonempty B stratum and set v=(q²−a−5t−S0)/2. This is possible because p is odd. This establishes nonempty coefficient-domain branches and a nonzero counted denominator, NOT existence of a full original curve-relation root on every branch. A1 varies and A0 is reconstructed. Remaining norm/interval/rationality/signed constraints can make the entire branch infeasible; the count is not evidence of work saved by a solver that already knows this.

A sound clause negates all fixed original v,q,B0 bits and the A1 prefix bits. It contains no S/E literals and need not fix A0. It is implied by the original full polynomial source, not range-only bootstrap CNF. Authenticate the triple and compute S0,c from it; do not accept caller-provided derived moments. Existing prefix-only checker cannot accept this arbitrary subcube without separately admitted semantic integration. No new fields are required, but source verification, learned-clause storage, model reconstruction and eventual final completeness checking remain charged.

Comparison: global E envelope is the required baseline. Comparing against unconstrained field prefixes would manufacture gains. Existing complete h5 pair/triple MITM baseline O(B³ log(B+1)+N) remains; no enumeration of all triples, moment pairs or rejected prefixes is proposed. This proves a useful necessary-condition test with uniform nonvanishing rejection on the stated incomplete original-coefficient prefix domain. Whether an effective search visits it cheaply and benefits after propagation remains the precise performance gap. Degree-two presentation does not imply reduced regularity; no such claim is made.

Controls: wrong target sign; h4 q0 exceptional fiber (outside this h5 proof); swapped u,j; missing B-stratum premises; p<=K or aliases; H>=p (no incomplete-bit guarantee); arbitrary c input; omitted v/q/B0 literals; lost original projection A0; prefix collisions across preimage intervals; tinyM; empty full-root branch; comparing denominator to p instead of global G; using RAT alone to admit semantic clause. Original six coefficient cells are coset support and remain outside applicability.
