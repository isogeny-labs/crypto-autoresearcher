# Second moments: conditional quartic elimination and cheap prefix exclusion

Separate-session, producer-visible mathematical critique accepted the main derivation, controls and complete deterministic baselines. The review was not blinded; no blind rederivation or native review-gate pass is claimed. The original plan is preserved and its missing fields are documented in review-procedure-supplement.json. The separate prefix critique accepted the necessary-superset rejection with the explicit field-width clarification below.

## Exact algebra and sharp bounds
For U=X^h+u X^(h−1)+j X^(h−2)+..., the h3/h4/h5 next norm coefficients are derived from the actual normalized source. At h3, fixed u,j leave the quartic

q⁴+(2u−6a)q²+8bq+u²−2au−3a²−4j=0,

so at most four distinct field coefficient candidates remain. All roots must be found with certified completeness, then all remaining rows/witnesses checked. At h4 the q=0 branch retains the full A1 fiber when its forced second moment is admissible. It may not be divided away.

For offsets0<=d_i<=M=B−1, S=sum d_i and E2=sum_{i<j}d_i d_j satisfy j=binom(h,2)t²+(h−1)tS+E2. Since2E2=S²−sum d_i², balanced offsets give the exact maximum E2 and packed offsets give its exact minimum. They are necessary interval bounds, not an exact feasible set: B4,h3,S3 allows E2={0,2,3}, with a hole at1. At B8, distinct multisets(0,3,3) and(1,1,4) both give(S,E2)=(6,9). First two moments do not identify support.

Replacing support coefficients by moment residues is affine and preserves quadratic row degree. Further coefficient elimination can be quadratic/rational and must not be described as affine or as regularity reduction.

## Avoid enumerating the moment grid
The necessary residue-pair envelope hasTheta(B min(p,B²)) entries in the stated injective-first-moment regime. In p≫B² it isTheta(B³). Complete baselines cost O(B²+N), O(B² log(B+1)+N), and O(B³ log(B+1)+N) for h3/h4/h5 respectively, plus charged factor-base preparation and arithmetic/witness costs. Pair/triple joins retain repeated points, identity intermediate sums and every colliding tuple. N denotes all ordered outputs before requested projection/deduplication.

These baselines do not justify naive moment-grid scaling. Saturation is rowwise: a saturated second-moment interval disables that bound for its sum, while trace restrictions and unsaturated cases can still prune.

## A concrete cheap conditional predicate
Fix full canonical S0. At most h integer lifts lie in[0,hM]; their necessary E2 intervals map to at most2h canonical arcs[L,U]. For an E2 LSB prefix r of depth d, H=2^d, an arc intersects precisely when ceil((L−r)/H)<=floor((U−r)/H). Reject iff every arc misses. Floor and ceiling are mathematical signed operations, not truncation toward zero. Endpoint calculation and checks use O(h) integer operations on O(log p)-bit operands, plus parsing/authentication and O(ell) input/clause-bit costs; no moment-grid or coefficient enumeration is involved. Here ell=ceil(log2p), and0<=d<=ell.

The clause conditions on all S0 bits plus the E2 prefix. E2 can remain auxiliary and original q projections remain unchanged. This is a semantic proof design: the old prefix-only/DRAT-RUP checker does not automatically admit it. A new authenticated lemma interface or checked derivation is required. Passing the predicate proves neither attainability nor a relation; no rejection-frequency or runtime claim is made.

Next action: specify that authenticated conditional-prefix lemma and its malformed/edge-case controls, then a bounded source implementation only under a new exact admission. Do not run grids. Original six coefficient cells are coset-based, not interval charts; support transport is still required. No changes to old k3-sharing restrictions,106+6/five-lead scope, attempt budgets or reserved scientific slot.

Sources: frozen design/baseline/controls/prefix-arcs notes and their critiques; source-bindings.json; definition-clarification.md; review-procedure-supplement.json. Prior-art context and primary links are in literature-notes.md; no novelty claim is made.
