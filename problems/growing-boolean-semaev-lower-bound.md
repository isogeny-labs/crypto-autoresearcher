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
