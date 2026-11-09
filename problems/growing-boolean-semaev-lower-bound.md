# A growing fixed-degree Semaev lower bound needs a uniform separator

- **Status:** `open`
- **Kind:** mathematical proof gap; not an impossibility or resource result
- **Affected work:** [four-track request and proof note](../analysis/boolean-fall-certificates-20261104/THEORY.md), RQ-DREG-bd6c86, prime digit and binary descent lanes
- **Next action owner:** formal/theory continuation of the current owner request
- **Last updated:** 2026-11-09

## Problem

The characteristic-two fixed-degree growing lower bound remains unproved.
The 2026-11-05 continuation supplies a written prime-digit family theorem
with full closure and a fresh independent mathematical review; see the
scoped progress below. This record remains open for the binary requirement
and does not promote any official research claim.

The binary target is the exact normalized S3 subspace descent with explicit
Boolean equations (or a separately specified chained encoding). The prime
target is the F_p-coefficient Boolean-digit S3 presentation with explicit bit
equations, not a carry circuit or the degree-B membership polynomial model.
The arity, input normalization, target admissibility, subspace/digit maps,
auxiliary blocks and field must be fixed in the family statement. Point/group
interpretation is a separate obligation when the coordinate constraints omit
rational-lift or sign restrictions.

## Scoped progress, 2026-11-05

For the exact prime single-S3, two s-bit-block presentation, with all bit
equations, s>=2, p>=2^s prime and a nonsingular curve,
[the written theorem](../analysis/rigorous-lfd-solving-20261105/THEOREM.md)
proves `4+floor(s/2)<=d_F<=sd_sigma(F)<=2s+1` for every degree-compatible
order. It explicitly computes the full strict closure at the separating cap
and uses Boolean evaluation dimension to handle SAT as well as UNSAT.
Rational-target SAT and UNSAT families exist for every width.
[Fresh review](../analysis/rigorous-lfd-solving-20261105/prime-independent-review.md)
found no mathematical gap at written-proof scope, with analytical controls.
It supplies no complete Lean theorem or signed PCC/scientific promotion.
The old measured widths are not being extrapolated as the proof.

The characteristic-two lower bound remains open. The raw binary upper-bound
Lean instantiation now compiles and is described in
[BINARY-FORMAL.md](../analysis/rigorous-lfd-solving-20261105/BINARY-FORMAL.md).
The exact remaining scope is in [the obligation record](../analysis/rigorous-lfd-solving-20261105/problems/remaining-binary-obligations.md).
The earlier no-separator statements below describe the 2026-11-04 state;
they are superseded for this exact prime presentation, not for binary or
other encodings. The original requirement is retained.

## Evidence and uncertainty

- Observed software checks: the [new finite checker](../analysis/boolean-fall-certificates-20261104/certificate.py)
  tests both inclusions and produces explicit SAT missing-consequence
  witnesses; its N<=12 ceiling is a disclosed instrument boundary.
- Written argument: a uniform family of closed separating kernels at caps
  D tending to infinity, paired with UNSAT or an actual missing ideal
  consequence, would give the requested family lower bounds.
- Missing proof: a parameter-uniform formula for those kernels, or a
  degree-controlled reduction to these particular Semaev systems.
- The one-pass shortcut fails a deterministic quadratic software control:
  products of newly fallen combinations can escape the initial span.
  Hilbert-series or raw-row counts alone do not discharge closure.
- This is not evidence that a growing bound is false. The measured prime
  width law and binary finite ladder do not settle it either way.

## What would unblock it

- [ ] State an exact deterministic family or probability distribution and
  which parameters grow, preserving the production generators and degree.
- [ ] For arbitrarily increasing caps D, construct pi_D that kills every
  eligible input and whose low-degree kernel is closed under all variables.
- [ ] Prove pi_D(1) is nonzero with independent UNSAT, or exhibit an ideal
  consequence g_D separated by pi_D for SAT systems. Check source-to-model
  and degree bookkeeping in the polynomial/Boolean bridge.

These are sufficient conditions for family lower bounds, not requirements
that every other possible proof must use this route. Finite certificates and
formalizing a conditional composition lemma alone do not meet them.

## Next discriminating proof step

Derive candidate kernels after quotienting the known trace/degree-three
falls, then test the symbolic variable-closure identity. Begin with the
unchanged finite controls and degree-compatible elimination. If closure fails,
retain the escaping product and revise the candidate space; if it holds only
for finitely many parameters, retain the finite lower bound and do not infer
growth. A successful uniform construction proceeds to independent semantic
review under the existing claim-tier rules. No new trial or spending is
scheduled by this record.

## History

2026-11-04: Opened while delivering the two-sided certificate and scoped
formalization tranche. The original request remains unresolved at this
mathematical obligation; no goal or hypothesis status was changed.

2026-11-05: Added the scoped prime written theorem and independent review;
binary obligations and official research statuses remain unchanged.

## Fixed-m=2 proof continuation, 2026-11-09

[Parallel proof report](../docs/reports/2026-11-09-fixed-m2-lfd-unbounded/report.md) preserves the exact normalized binary m=2 target and adds two independently cross-checked written lemmas. For n=2k and the full quadratic-extension subfield V, UNSAT implies LFD<=3, eliminating that natural tower as an unbounded UNSAT construction. A closed-kernel certificate at cap D for UNSAT must have strict quotient-image filtration through D-1 and rank at least D. These are proof-route restrictions, not an unboundedness theorem, new experiment or formal promotion.

Unchanged-instance field extensions and disjoint conjunctions do not amplify refutation degree. Vanishing all cross quadratic coefficients between two nonzero subspaces forces both dimensions at most one; an arbitrary sparse hard gadget therefore needs a nontrivial degree-controlled reduction respecting the field tensor. The report records these deductions, independent reviews, historical-profile arithmetic, source hashes and the exact missing uniform certificate construction. No solver, certificate replay, build or cloud job was run. Existing finite evidence remains immutable.

Next: derive a parameter-uniform vector quotient for a genuinely varying half-dimensional subspace, prove full low-degree kernel multiplication closure, and combine it with UNSAT or a missing SAT consequence. R35a is a negative control for any rule predicting automatic degree-five survival. The original growing-lower-bound exit conditions above remain open.

## All-instance upper-bound continuation, 2026-11-09

The [additive upper/time report](../docs/reports/2026-11-09-fixed-m2-lfd-upper-time/report.md) now derives LFD<=k+3 for all normalized binary m=2 instances, including SAT, by selector-weighted normal forms and full arbitrary-degree induction. A separate independently worked SAT extension gives LFD<=3 for the quadratic-subfield family when z is outside the subfield. The target-inside-subfield SAT case is not covered by that constant bound. The general k+3 proof and the subfield proof have independent written audits; no Lean certification or official promotion is claimed.

The direct s-fibre enumeration algorithm has O(2^k n^3+n^4) Boolean arithmetic work and O(n^2) streaming working bits in the stated indexed-bit model, with separate output accounting. No native instruction count or F4 runtime is measured. The k-dependent general bound leaves the binary unboundedness-versus-constant-bound question open and constrains future lower bounds without settling them.

## Product/trace refinement and presentation correction, 2026-11-09

The [product/FFD continuation](../docs/reports/2026-11-09-fixed-m2-fibre-ffd/report.md) derives exact fibre-kernel labels from X(X+s)(X²+sX+z). Distinct-product exclusion yields the all-instance bound k+2; nonzero trace on V separately yields k+2, and together they yield k+1. Pair counting guarantees excluded-product field targets on the half-dimensional diagonal; fixed-curve admissibility remains separate. These are conditional upper bounds, not growth or constant-bound conclusions.

A hand-worked actual F16 Semaev example shows PQ FFD and small exact LFD changing from2 to1 under invertible output row recombination. The earlier row-span invariance statement is now explicitly restricted to caps D>=2. An additive correction also replaces the invalid diagonal inside-subfield witness with X=0,Y=sqrt(a6)/z. The SAT conclusion and higher-degree bounds remain intact; original archives are unchanged. Exact first-fall labels must bind their input presentation and definition.

### 2026-11-09: exact-input annotation prototype and inside-subfield normal form

The source-only packet `analysis/semaev-bound-labels-20261109/` reconstructs normalized m=2 Boolean coordinate inputs and annotates applicable written upper bounds with exact input/equation/theorem-source hashes. It leaves exact LFD and lower-bound fields unknown. Five fixed software controls pass; the independent algebra checker passes 34 checks after a preserved Python portability failure. There were no new scientific draws or closure runs.

The inside-subfield note derives G(x,r)=x²+x(r²+r+c)+zr² and exact affine/quadratic maps between solution sets. At caps D>=2 the forward simulation preserves D and the reverse simulation costs at most 2D. This does not transfer a constant satisfiable LFD bound: arbitrary output degree must be preserved in max(C,deg f). A family of full-closure lower-bound certificates surviving these identities remains missing. No unboundedness theorem is claimed.

### 2026-11-09: lower-bound transfer and executable finite feasibility encoding

The independently reviewed restriction-indicator argument shows d_ref(restriction)<=max(d_LFD(original),codimension,2). A hard restriction transfers its degree only when it exceeds the indicator cost. R35a's degree5 cannot transfer through its codimension34 restriction of the full-field system.

After trace elimination the exact alternate Semaev model is one quadratic Boolean definitional extension; UNSAT refutation degrees differ by at most two. This is a tighter reduction target, not SAT LFD invariance or an infinite-family construction.

`analysis/semaev-bound-labels-20261109/encode_certificate.py` emits an exact fixed-D/fixed-rank GF2 feasibility system for closed-kernel certificates, with all eligible multiplication constraints and a right inverse. Seven software controls and an emitted 24-equation hand-specified rank-two example pass. No solver search occurred. Independent checking and a separate UNSAT/count/missing-consequence bridge remain required for every proposed LFD lower bound. The growing-family obligation remains open.

### 2026-11-09: direct checking and count-sensitive SAT transfer

The bounded direct checker in `analysis/semaev-bound-labels-20261109/check_candidate.py` reconstructs coordinate rows by separate evaluation interpolation and checks the full low-degree kernel, not solver-supplied multiplication actions. Eight fixed software controls pass; no new scientific certificate or bridge is claimed.

The SAT one-bit note derives dF<=max(dG,b(M))+2 and dG<=max(dF,b(M)+1), where b(M)=max(2,floor(log2(M+1))). Thus bounded-solution-count families transfer LFD boundedness/unboundedness. A generic counterexample to additive invariance uses an input monomial of growing degree and does not answer the quadratic Semaev question. The target now has two separate requirements: a low-solution-count Semaev family and growing full-closure certificates, or a more specialized quadratic elimination theorem.

### 2026-11-09: infinite bounded-count family and capacity bridge

A reviewed averaging argument establishes: for every odd n>=3, some dimension-(n+1)/2 subspace V containing1 gives exactly two ordered Semaev zeros at z=a6=1. It uses an exact correspondence with E:y²+xy=x³+1, Hasse's bound, and subspace containment probabilities. The target has order four and the basis selection is existential; no growth of LFD is established. For qualifying V the ideal's affine-linear generators are explicitly known, giving concrete missing-consequence targets. An arbitrary V is not certified by this existence result.

`attach_capacity_bound.py` connects a freshly checked quotient map to independently reconstructed structural solution capacities: q>U implies LFD>=D+1. Six software controls pass; q=U remains inconclusive. No positive scientific lower-bound fixture was exercised, and production dataset admission remains false. The next mathematical obligation is simultaneous bounded solution count and a growing full-closure obstruction.

A separate reviewed conditioning argument also supplies infinitely many odd-degree UNSAT subspaces with nonzero restricted trace and 1 outside V. Positive Frobenius traces occur at infinitely many odd extensions, making the conditioned expected solution count below two. This excludes the single immediate constant-trace contradiction, not all low-degree refutations. No new LFD lower bound follows from this existence statement alone.

### 2026-11-09: infinite constant lower bounds and a checked positive fixture

The reviewed degree-two classification proves LFD>=3 for every qualifying two-solution containing1 subspace, and for infinitely many nonexceptional trace-active UNSAT subspaces. Product-span nondegeneracy is automatic on the odd diagonal. A symplectic count bounds the rank-one exceptional family below the available UNSAT population for r>=7 along the positive-trace subsequence. Exact nonexceptional codimension at D=2 is (N²-3N+6)/2, not a growing-degree result.

The explicit F8 control now exercises a positive bridge: rank5 atD2 exceeds capacity4, and cap3 multiplier identities derive its complete affine ideal, giving exactLFD3. No search was run. For the verified two-point family, growing LFD is exactly growing derivation cap of a named affine ideal generator; the density note states a sufficient exceptional-set counting bound, which remains unproved for increasingD.


### 2026-11-09: degree-three reduction and executable SAT export

Reviewed branch reduction gives h<=LFD(F)<=h+1 for the unique-zero system H=(uv)^2+uv+u+v^2. The full W3 criterion iterates all degree-two consequences and their variable products to stability. A non-Semaev family with the identical W2 dimension profile and exact LFD3 demonstrates why that profile alone cannot force growth. A tensor-specific invariant or growing obstruction remains missing.

The bounded DIMACS exporter and supplied-model checker pass five controls and an actual 1770-variable/5610-clause hand-witness replay through CNF, GF2, direct kernel, and capacity checks. The replay establishes lower bound3 for the existing F8 control. No solver search, production dataset admission, or growing lower-bound theorem is claimed.


### 2026-11-09: explicit no-reduction family and amplification obstructions

V=span(1,t,...,t^r), n>4r and z=a6=1 gives an explicit infinite exactly-two-point family, by a highest-polynomial-degree argument. Its r=1,2 members have cap-two derivations of the affine ideal; the odd-diagonal lower3 theorem does not apply. General dyadic coefficient saturation remains unresolved.

Reviewed transport gives cap max(sD,c) for degree-s substitutions with generator-image cap c. Field towers preserving V retain late closure; disjoint SAT products take maximum LFD, so neither amplifies degree. Field-trace dual separators give a concrete upper-bound route, while turning their degree into a lower bound requires an unproved normalization of arbitrary full-closure derivations. These negative routes and exact remaining obligations are retained in the proof packet.


### 2026-11-09: first explicit no-wrap obstruction, certified and symbolic

The frozen r1..12 W2 campaign completed all cells with independent DAG/closure checks. Cap2 derives the affine ideal for r1..5; r6..12 certify lower3. At r6 a polynomial-gcd argument independently proves rank71, affine dimension5 and stable reduced quadratic space dimension11. Selector lifting gives upper4. Restriction with the independently known two-point ideal gives lower3 for every r>=6,n>4r, including a constant-codimension35 certificate pullback construction. This disproves the proposed universal cap2 for this explicit family; it does not prove unboundedness. The next discriminating obligation is full W3 at r6 (degree3 versus4), then a growing-cap family. Original campaign allowance consumed; no automatic repeat.


### 2026-11-09: no-wrap route has uniformly bounded degree

Independent review accepts the leading-q selector-peeling proof LFD<=4 for every no-wrap member (n>4r,z=a6=1). Combining restriction lower3 gives3<=LFD<=4 for allr>=6. The exactr6 degree is3, proved symbolically before a frozen cap3 computation and confirmed by full DAG/closure replay (rank468, affine13). A presentation-qualified telescoping witness proves FFD2 for allr>=1. This resolves boundedness for this explicit subfamily; it cannot witness unboundedness. The next growing-family construction must use field modular reduction or a different permitted factor-base structure. Ordinary ambient extensions and disjoint products already fail to amplify degree. Both bounded local attempts are complete; no automatic rerun.


### 2026-11-09: modular correction and guarded original-polynomial labels

Polynomial division F=P Q+R shows that the no-wrap affine chains acquire the correction C_d(PQ). On the odd half diagonal, xy=J(x+y+1)^2+epsilon is exact on the trace slice, but J need not preserve polynomial degree. Exact quotient auxiliary definitions give W_D(R) subset W_D(G) and sigma(W_D(G)) subset W_(2D)(R), D>=2; padded refutation degrees differ by at most a factor two. A growing hard UNSAT family in this exact extension would suffice; none has been constructed. SAT target degree remains an extra obligation.

The inspector now applies the proven bounded-family labels to exactly recognized basis changes. A separate retained Weil-system join checks the full selector domain, coordinate maps and literal equations before admitting polynomial labels; it does not admit whole dataset records. Twenty-three software controls and actual CLI accept/refuse artifacts are retained. No new scientific campaign or native build ran.


### 2026-11-09: modular degree-three feedback and exact selector scope

The reviewed modular-degree-three-field-falls.md writes the odd half-diagonal system as ell=0 and G=xy+B(x,y)+epsilon=0, with B=J(s+Tr(s))^2 and s=x+y+1. Projection keeps J on its trace-zero domain, including subspaces not containing1. The field identities xG and yG have quadratic Boolean coordinates and are available at cap3. Scalar-output cubic cancellation is governed by explicit trace-orthogonality conditions; trace elimination can add further cancellations. These are mandatory consequences, not a completed W3 invariant or a growing bound.

The separately reviewed finite-selector note proves the safe normalized Boolean bound LFD<=N+1 for exact nonlinear/repeated selector maps. It preserves code multiplicities and gives sufficient nonlinear transport hypotheses. It supplies no growing lower bound and does not replace finite factor bases with their span. No new dataset replay or scientific trial accompanied these proofs. See modular-feedback-report.md and modular-feedback.pdf for the frontier and evidence links.


The Frobenius follow-up proves that simultaneously twisting xG produces no new coordinate span. Nonzero relative twists cannot cancel the entire field-valued cubic on a half-diagonal subspace. Scalar trace cancellation has an exact trilinear criterion; for coprime shifts it forces a specific inverse-power permutation to preserve the nonzero elements of V. This is a necessary condition before trace elimination, not a full closure certificate. See modular-frobenius-multiplier-obstruction.md and its review.


### 2026-11-09: exact trace-slice feedback and finite-selector CLI

The trace-slice note replaces x,y by independent x in V and t in W=V intersect kerTr. Its exact affine-multiplier conditions characterize the complete first quadratic feedback step. The epsilon multiplier space (VW)^perp has dimension at most one, with an exact rank-one trace-form characterization. Full iterative stability remains open. The inverse-Gold note supplies an F8 counterexample to blanket exclusion of inverse-power invariant subspaces, an exact subspace-polynomial divisibility criterion, and the inverse-cube necessary condition c2*c0^2=c1^3. None is a growing LFD lower bound.

`python3 join_finite_selector.py PARAMETERS.json WEIL-SYSTEM.json --output NEW.json` checks the exact cyclic sorted-code producer format, including repeated/nonlinear selectors and zero selector bits. Parameters use schema semaev.finite-selector-parameters/v1 with n,modulus,a6,z. It independently reconstructs maps and every original S3 row by field evaluation and Mobius inversion, then labels only LFD<=N+1. No solution count, exact LFD, FFD or whole-dataset admission is inferred. Wire limits are1MiB, n3..64 and selector bits0..6 per summand.

Seven new symbolic software controls and four existing retained-join controls pass. The accepted artifact in finite-selector-controls is a hand-constructed software fixture, not a production record. The saved CLI46 audit was inspected: its m2 cases are enumeration/PKM/double-large-prime; F4/F5 cases are m3. It therefore does not provide a production m2 Weil artifact for this join. No new scientific trial, solver run, native build or cloud job occurred.


### 2026-11-09: saturated closure cost bounds and the next quadratic forms

The generic strict-closure note proves a total feedback algorithm bound. Let M count degree<=D monomials and L count degree<=D-1 monomials; immutable degree-first echelon insertion processes each eligible pivot once. For R inputs, at most R+NL insertion attempts and (R+NL)M whole-row XORs suffice, including every later degree fall. Dense coefficient storage is at most M² bits, with indexing/metadata/provenance and other costs separately stated. Full Boolean cap N+1 gives M=L=2^N.

The finite-selector CLI now emits these exact combinatorial maxima in closure_algorithm_cost_bound after the original equation join passes. They describe the named hypothetical closure algorithm, not an executed native backend. Native instructions and wall time remain null; training_cost_eligible is false. Eight selector controls and four existing join controls pass. A new CLI output in operation-bound-controls preserves the previous control output unchanged.

The trace-feedback note calculates the complete first-step polynomials, including linked quadratic blocks and affine tails. A mandatory ax multiplier produces a pure-x term detected by Tr(a*x³), so the rectangular-plus-affine class cannot be invariant. This does not assert W3 differs from W2. The next obligation is stability of a larger linked-block space under all further cubic cancellations. No growing LFD bound is claimed.

No native build or new scientific/cloud run occurred. The native source remains4be27eee881663c44318ed2d9debfad05d071538; its saved owned-authentic-validation authorization is approved:false. Existing native telemetry policy still marks training_cost_eligible:false. The theorem-derived algorithm envelope does not override either condition.


### 2026-11-09: bounded exact Boolean LFD reference checker

`python3 inspect_retained_lfd.py PARAMETERS.json WEIL-SYSTEM.json --operation-limit 1000000 --output NEW.json` first verifies the exact finite-selector equation join, then enumerates the actual Boolean zero set and saturates every cap0..N+1. Evaluation ranks give the dimensions of the vanishing ideal in each cap. Exact LFD is one plus the last deficient cap, or zero when none is deficient. This preserves the normalized strict-closure convention and literal input presentation.

The core supports N<=12 and has explicit input/operation limits. CLI operation limits are1..10000000; the budget covers the reference analysis, separately from bounded loading/join/hashing/I/O. Exhaustion leaves exact_lfd null and retains completed cap summaries. Results are computed reference outputs, not standalone independently checked certificates; group-lift, authenticated producer, native-instruction and whole-dataset admission remain false. FFD is not inferred.

Twenty-four software controls pass across the core, CLI, finite-selector join and existing retained join. A hand-constructed F8 repeated-selector fixture produces six completed cap rows, four code solutions and reference LFD4, using36481 charged arithmetic units. These units are not retired instructions. The cutoff1 control produces no exact label. No production artifact or new scientific sample was executed. Source snapshots and outputs are in exact-lfd-controls/.

The parallel proof note shows every half-diagonal first-feedback space has at least r independent pure-x quadratic projections when n=2r+1. This rules out adding only a bounded number of such directions to the original rectangular ansatz. It is dimension growth at fixed degree3, not growth of LFD. A full stable linked-block space remains missing.


### 2026-11-09: independently checked all-cap certificates

The exact-LFD CLI now accepts --certificate-output NEW-CERTIFICATE.json. A complete run emits every cap's basis with a derivation for each row: eligible literal input or prior-row variable product, followed by XORs of prior rows. The certificate binds the exact input equations. Trace storage is budgeted and capped at200000 entries; exhaustion emits neither a partial certificate nor an exact label. The result binds the separately written certificate by SHA256.

`python3 verify_boolean_lfd_certificate.py CERTIFICATE.json --operation-limit 1000000 --output NEW-RESULT.json` uses no producer imports. It recomputes every derivation, validates degree-first independent pivots, checks all input containment and all eligible basis-variable products, and independently computes zero assignments and evaluation ranks. Every cap is required. Invalid proofs fail; budget exhaustion returns verified:false and exact_lfd:null. Wire input is capped at16MiB and N<=12. This verifies the supplied normalized mathematical system; its linkage to original curve/group data remains a separate exact join.

Thirty-five software controls pass, including altered rows, forward references, missing caps, unsaturated bases, invalid domains, budget exhaustion and an actual two-CLI certificate/hash roundtrip. The new hand-fixture certificate independently verifies LFD4 and four code solutions with68441 verifier accounting units. The earlier set-span cross-check failure remains unchanged; this is a new proof-carrying implementation, not a retry of that script or a production scientific sample.

The parallel proof eliminates epsilon exactly, obtaining an original trace-slice linear pencil in x for each t. A degree-c polynomial dual separator in t gives a direct original cap c+2 refutation. Explicit linear conditions characterize affine t-only separators and hence this particular cap-three refutation construction. Their solvability for an infinite family remains open, and their failure would not exclude arbitrary W3 refutations.
