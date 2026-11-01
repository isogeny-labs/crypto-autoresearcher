# IC arity/oracle threshold: independent synthesis

Date: 2026-11-01. Task: TASK-20261101-bc06d9. Batch: BATCH-a68666.
Producer: TASK-20261024-9fbb0f. Archive owner: TASK-20261101-7e3b01.
Checkout at analysis: `14886d001e60d6bd6fdecd145e79c0153b56ee98` (clean before this task).

## Outcome at the reviewed scope

Fresh hosted machine verification passes for
`CryptoResearch.IC.ArityOracleThreshold.mitm_never_sub_generic`.
The declaration holds in its explicit real cost model. The frozen bundled
English claim needs revision: blanket attainment and literal pointwise
below-half wording are false. The independent blind derivation supplies the
complete envelopes and independently confirms the `m=2,k=2` nonattainment
counterexample. These are compatible findings on different joints, not votes.

No existence or nonexistence result for prime-field subexponential ECDLP
follows. GOAL-ECDLP-001 remains open. No scientific status is changed.

| Requested component | Actual evidence/status |
| --- | --- |
| Machine versus fidelity separation | Passed receipt, scoped MITM inequality, and bundled mismatch separated below |
| Two independent joints | A: breaks the bundled claim; B: holds for its own blind derivation; exact archived outputs cited below |
| Independence composition | PASS with externally pinned plan and one prospective addendum; command, complete stdout/stderr and hashes in independence-check.json |
| Complete scope and next step | Full formula envelopes, explicit failures, model-to-PFSE obligations and exactly one proposed next action |
| Editable visual/PDF | dependencies.dot/SVG and report.typ/PDF; page inspection recorded separately |
| Publication | Working-tree synthesis only; final archival/publication belongs to TASK-20261101-7e3b01 |

## Observation: machine evidence, not a bundled-claim certificate

Hosted workflow 41275109694, attempt 1, verified published source
`7e1827b530349c633d98c96185e8196669812cb4`.
The exact 67,574-byte target receipt has SHA-256
`75e52bc6bb7a034f81103166cf463d3f660b39b863177b797f7039f58394bc0a`,
losslessly committed in receipt-capture.json at
`e887f4cd75b16db6e47342d1f319bf393888707c`.
It reports machine_verified, build_passed=true, axiom_audit_passed=true,
no forbidden constructs and no infrastructure failure. The named audit shows:

```text
mitm_never_sub_generic (m beta k : Real)
  (hm : 2 <= m) (hbeta : 0 < beta) (hk : m / 2 <= k) :
  1 / 2 < costAll m beta k
```

Only standard axioms propext, Classical.choice and Quot.sound are reported.
The receipt names 894 project theorems in the project audit; only the MITM
declaration has this target's dedicated named audit. Module compilation is
not independent semantic approval of every clause in the English target.
Reviewer A counted 24 declarations and 19 supplementary printed-axiom lines;
printed lines alone are not fail-closed audits.

This synthesis decoded and rehashed the exact native bytes and checked both
complete maps against the committed validation record: 75 workspace and 10
verifier entries match. Earlier strict replay binds 191 tracked source blobs
to the workflow head. No fresh build, root generation, strict verifier rerun,
scientific trial or independent binary/kernel rechecker is claimed here.
The current review worktree lacks the generated root; that does not relabel
the older receipt as a run on the later metadata head. Dependency binaries
retain the documented Lean/Lake trust boundary.

The fresh verification snapshot is
`5b3ad6957cb48260d354d9aec6d47cc8159878d8`.
Review outputs were sealed at
`76320e68aef505292da6a9eff98aa219cca4ecc3`; the full five-artifact archive
is `5658c82b1de6f4fc6b44c864c91855c61c21d72e`, parent
`446bf35095bf2744a817b0fad7dd3bd170bcb507`.
Native GitRepositoryVerifier checks all five exact hashes, ancestry, parent
and all three required TASK IDs. Its frozen snapshot contains its originally
pending gate; later finalized metadata and the completed lifecycle at
`14886d001e60d6bd6fdecd145e79c0153b56ee98` discharge that historical gate.

## Comparison: owned joints and hypothesis deltas

| Claim component | Machine coverage | Independent fidelity and outcome |
| --- | --- | --- |
| Named MITM inequality | Fresh dedicated declaration audit | A: faithful_scoped; holds under m>=2, beta>0, k>=m/2 |
| Restricted real lower bounds/equality witnesses | Built module/project audit; exact names in A's table | Hold at their signatures; do not merge incompatible domains |
| Frozen “each bound attained” | No declaration proves that blanket sentence | A: mismatch, needs_revision; B independently derives unattained infimum above k=m-1 |
| Literal pointwise below-half iff | Existing lemmas threshold rational expressions | A: mismatch; B separates optimized and pointwise thresholds |
| Full envelopes | Not packaged as an infimum/IsLeast theorem in the current target | B: holds for symbolic derivation only; not newly machine verified |
| Algorithm/PFSE bridge | No curve, probability space or algorithm in theorem type | Partial/not supplied; all interfaces below remain open |

For the named MITM signature, A found no unexplained additional binder:
k>=0 follows from the stated m and k constraints. H1-H4 are not hidden
Lean hypotheses; they motivate definitions without proving algorithm coverage.
For other clauses, `costAll_large_attained` adds k>=2, a scoping condition
not implied by 0<=k<=m-1. Denominator positivity is implied within each
stated theorem domain. Fixed k=0,1,2 corollaries and m=3 are specializations.
Optimizing beta is an additional quantifier, not a pointwise fact.
A's complete per-declaration/hypothesis-delta tables remain authoritative
detail in its sealed report.

## Derived algebra: the full real-parameter answer

Use m>=2, beta>0, k>=0, all real. Let F=costAll and G=costOne:

```text
F = max(max(0,1-beta(m-1))+k beta, 2 beta)
G = max(max(0,1-beta m)+(1+k) beta, 2 beta)
d = m-1-k; q_F = max(k,2); q_G = max(k+1,2)
F = max(1-d beta, q_F beta); G = max(1-d beta, q_G beta).
```

For either q, d+q is positive. Splitting by the sign of d yields:

| Regime | Infimum over beta>0 | All minimizers |
| --- | --- | --- |
| k<m-1 (d>0) | q/(d+q) | Unique beta=1/(d+q) |
| k=m-1 (d=0) | 1 | 0<beta<=1/q |
| k>m-1 (d<0) | 1 | None; approached as beta tends to 0 from above |

Thus for F below k=m-1, the value is 2/(m+1-k) for k<=2,
and k/(m-1) for k>=2. For G below k=m-1, it is 2/(m+1-k)
for k<=1, and (1+k)/m for k>=1. Boundary formulas agree.
Above k=m-1, none of those rational branches may replace the infimum 1.

The optimized infimum is below/equal/above 1/2 exactly when d is
greater/equal/less than q. In particular F's optimized below-half
condition is m>k+3 for k<=2, or 2k<m-1 for k>=2.
For an individual beta, when d>q it is below 1/2 exactly on
1/(2d)<beta<1/(2q); when d=q equality occurs only at beta=1/(2q);
when d<q every value exceeds 1/2. These are different quantifiers.

F<=G pointwise. Equality is exactly k<=1 or beta<=1/m.
Optimized equality is exactly k<=1 or k>=m-1; strict optimized
inequality is exactly 1<k<m-1. Equal infima above m-1 are not minima.

The MITM condition k>=m/2 forces d<q_F and therefore F>1/2 at every
admitted beta. B independently derives the sharp envelope:
I_F>=4/(m+2) for 2<=m<=4, and I_F>=m/[2(m-1)] for m>=4;
I_G>=1/2+1/m. These margins approach zero with growing m, but the
pointwise lower bound 1/2 remains. No uniform positive margin above
1/2 is supplied for unbounded arity.

## Explicit defects and controls (symbolic, not new trials)

| Artifact/control | Exact result and consequence |
| --- | --- |
| F1: m=2,k=2 | F=max(1+beta,2 beta)>1; G=max(1+beta,3 beta)>1; both tend to 1 as beta->0+. No minimizer. A and blind B agree. |
| F2: m=5,k=0 | Middle bound k/(m-1)=0 is not attained; minimum is 1/3 at beta=1/6. |
| F3: pointwise threshold | m=5,k=1 satisfies m>k+3, but F(5,1,1)=2; beta=1/5 instead gives 2/5. Also m=7,k=2,beta=1 gives 2 despite the large-order condition. |
| F4: strictness | At m=3,k=2 both optima are 1. For 2<=k<=m-1, (1+k)/m-k/(m-1)=(m-1-k)/(m(m-1)); strictness requires k<m-1. |
| F4: equality threshold | m=5,k=2,beta=1/4 gives F=1/2; “cannot reach” is stronger than “never below.” |
| F5: unrestricted closed form | m=2,k=3/2 would give 4/3 from an unqualified small branch, but the infimum is 1, unattained; k<=m-2 fails. |
| Positive/nonvacuity | F(5,1/5,1)=2/5; F(3,1/4,0)=1/2. Universal model exclusion and strict arity-three claims fail. |
| Drop H3 | Attempts-only at m=3,k=0,beta=1/3 is 1/3; full F is 2/3. |
| Drop H1/H2 | beta=1/8 with k<=2 gives modified failure-free cost 1/4; modified H2 at m=3,k=0,beta=1/5 gives 2/5 instead of original 3/5. |
| Change H4 | At m=4 a free oracle reaches 2/5; order one has minimum 1/2. |
| Exception scope | No model-to-algorithm premise covers anomalous/pairing controls. No concrete curve or transfer fixture was run or certified. |

These exact substitutions are derivation/refutation artifacts in the sealed
reports, not newly compiled Lean counterexamples. The source target, header,
producer note and lead row remain unchanged. No erratum is silently applied.

## Inference and limitation: explicit formula-to-PFSE bridge

The PFSE scale is n=ceil(log2 r), log2 p=Theta(n).
The declared target needs a uniform classical randomized family algorithm,
success at least 2/3, and total expected time and memory 2^o(n), charging
all phases. A positive fixed exponent below 1/2 is still exponential in n.

| Open interface | Missing obligation |
| --- | --- |
| H1 yield/probability | Specify tuple/multiset counting, target distribution, multiplicities, tails and uniform success; a mean is not a hit probability |
| H2 useful relations/rank | Prove independent useful rank, duplicates/dependencies, stopping time, target linkage, failures and restarts |
| H3 linear algebra | Prove achieved arithmetic/bit complexity under actual matrix size/sparsity/rank; an implementation upper estimate is not a universal lower bound |
| H4 oracle semantics/output | Implement/specify all-return versus one-return success, enumeration/verification, output size, setup and cost; equal k is not established for two real solvers |
| Growing arity and m! | Control log2(m!)/log2 r, exact multiset correction, integer rounding, degrees, row length and every m-dependent constant uniformly |
| Family and model | Freeze measure/quantifiers and sampler certificates; generic random-label scope does not automatically include coordinates, maps or solvers |
| Setup/preprocessing | Charge base construction, membership, advice, tables, target dependence and amortization count |
| Transfer/descent/recovery | Supply explicit map, construction/evaluation, subgroup transport, source-scale destination costs, descent, scalar recovery and final verification |
| Memory and total success | Charge peak/persistent storage, processors, communication, repetitions and complete expected total cost |

A's mean-versus-success witness takes Y=L with probability mu/L, zero otherwise:
E[Y]=mu but Pr[Y>0]=mu/L. This is an abstract underdetermination witness,
not a curve construction. B relation rows may all coincide and have rank one.
Explicitly returning Y decompositions must price output; compression needs
decoding and rank costs.

For growing integer m, dropping m! requires m log m=o(n).
The exact multiset count is B^m/m! times the product of (1+j/B),
j=0,...,m-1; its logarithmic correction also needs uniform control.
The reviewed sufficient logarithmic condition m^2/B=o(n) is not a proved
property of an implemented algorithm. A fixed-m r^o(1) estimate does not
automatically hold for m=m(n).

The admitted model schedule k=1,beta=1/m has F=G=2/m for m>2.
Letting m grow makes the formula exponent tend to zero, but supplies no
solver, probability/rank, descent or memory certificate. Conversely the
MITM condition excludes vanishing exponent only inside that charged model.
Neither observation answers the unrestricted existence/nonexistence question.

## Provenance, independence and deviations

All mathematical evidence here is internal: the two sealed reports, the exact
definitions and archived machine packet. No primary external literature was
retrieved or newly verified. The supplied PFSE documents are cited as internal
scope specifications, not as new verification of the publications they discuss.
Tool discovery exposed no search_knowledge tool. Their recorded missing
full-text/family-fixture gates remain open; no novelty or exhaustive-search
claim is made.

The checker command, exact input hashes, complete stdout, empty stderr and exit
0 are in [independence-check.json](independence-check.json).
It composes one addendum widening protected paths, without altering the frozen
mathematical input. A and B declare no sibling access; B read only AGENTS,
its own card and blind input. Coordinator comparison occurs now, after archive.
Neither reviewer is unblinded, contacted or asked to amend its sealed output.
Requested model/effort/fork settings and backend separation remain unverified.
The checker checks declarations, not backend isolation or their truthfulness.

Procedure disclosures: the initial ordinary pip install was network-sandbox
blocked; a network-enabled retry installed Typst 0.15.0 in a scratch venv.
Only document rendering uses it. The first Typst compile failed on an unescaped
literal comparison sign (unclosed label); escaping it repaired the document
source. A crowded diagram edge label was shortened after page inspection.
These renderer attempts are recorded in visual-inspection.json.
Earlier pending-gate bytes remain historical,
with later archive/lifecycle verification cited rather than rewritten.
No new reviewer, build, experiment, trial, source/proof edit, EV/DEC/H record,
status transition, claim release, commit or publication occurred. Formal-review
erratum routing is deferred to the one proposed action, not written outside
this task's exclusive scope. Session/cost receipts outside the eight-file
allowlist and full corpus ledger validation are not produced here; scoped
checks do not substitute for corpus validation in this sparse checkout.

The study directory and knowledge/frontiers/ecdlp were checked for editable
DOT/Mermaid/SVG canonical graphs; none is present in this materialized scope.
The PFSE program's M0-M4 and full-cost tables were checked and left unchanged:
this packet supplies a technical correction, not a promoted frontier update.
No quantitative graph is appropriate: the source is symbolic algebra and
machine/review custody, not measured performance data.
[dependencies.svg](dependencies.svg) shows the actual evidence/model boundary;
its dashed red bridge is unresolved. All edges state their evidence status.
Documentation does not establish a speedup or lower bound.

## Exactly one bounded next action

Create a separately authorized additive correction/formalization packet for
the **complete real-model infimum, attainment and optimized/pointwise regimes**
of the existing target, before any model-to-PFSE use. Preserve frozen bytes.
Record the smallest m=2,k=2 counterexample in a dated formalization correction,
map affected target/header/note/lead citations, state the d/q piecewise theorem,
all minimizers and half-threshold quantifiers, and provide corresponding
new-version declaration coverage. Include F1-F5 and the positive/control
boundaries above. This is one corrective formal-model work unit, not a PFSE
bridge or a new algorithm search. Its acceptance requires exact complete
regime coverage and later fresh verification plus affected-joint fidelity
review under a prospective task. This synthesis authorizes none of those runs.
See [next-action.json](next-action.json).

The current eight-file synthesis remains pending its separate final archive.
