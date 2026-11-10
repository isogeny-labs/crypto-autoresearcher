# Compact source composition and odd-order Kummer descent

Date: 2026-11-09. **Source-only proof/interface proposal; formal review pending.**

This packet derives a sufficient descent criterion that can be applied to checked
rows without constructing a rational-function multiplication table or searching
for finite-field square roots for each row. It also specifies the exact row
premises and custody that such an application must retain. It changes no
certification status, approval, frozen contract, queue, or scientific result.
No cohort, benchmark, checker replay or compilation ran.

## Bound sources and literature

The baseline is `a066f7c73962c4b75b02e053e444a894dcf10287` (PR #3217 observed
head). [source-bindings.json](source-bindings.json) binds 31 committed files by
Git blob, byte count and SHA256; its SHA256 is
`1415469f465db8c00d92346c7ba736d4162b878afa976786aa0c05c57addc643`.
Concurrent working changes in `independent_fixed_model_check.py` and its test
are outside this inspection; the manifest binds their committed baseline.

The internal starting points are `specification.yaml`, `design-obligations.md`,
the collision-completeness and exceptional-descent-admission reports, and the
sealed-unit summary archived by TASK-20261109-d51e70. Paths below are relative
to `experiments/EXP-PEXT-bf8f96/` unless stated otherwise.

Primary sources checked through their indexed full PDF text:

- [A classification of elliptic curves with respect to the GHS attack in odd
  characteristic](https://eprint.iacr.org/2015/805.pdf), §§3.1–3.3: coefficient
  square classes, the order-degree lift condition, and ramification genus.
  In particular §3.2 and Example 3.2 require coefficient information beyond
  branch rank. This packet does not replace that information with a rank guess.
- [Igusa, Schur–Zassenhaus lemma, Theorem 13.7](https://people.brandeis.edu/~igusa/Math131b/SZL.pdf):
  a normal Hall subgroup has a complement. The elementary power argument below
  proves the particular cyclic odd-order quotient case needed here.

Initial direct PDF requests timed out/returned 403; opening the indexed primary
PDF results succeeded. The proof below is a proposed application of established
facts, not a novelty claim or an independent scientific review. Coordinator
Codex reasoning produced this packet; no exact serving identity is inferred.

## 1. Exact premises

Let `k=F_q`, `K=F_(q^n)`, with odd characteristic and odd `n` in {3,5,7}.
Here `sigma(c)=c^q`, fixing the rational coordinate. The current finite cohorts
use prime q; an implementation must not silently substitute p-Frobenius for
q-Frobenius in any future prime-power-q generalization.

For a single externally published canonical curve/T unit require:

1. An actual nonsingular K-Weierstrass model E, its origin, canonical rational
   T representing the declared E(K)/2E(K) class, and a checked separable quotient
   `K(E)=K(t,w)`, `w²=F_T(t,1)`. Include T=O, characteristic 3, twists,
   special j and exceptional projective charts. No division by 3 is used.
2. A complete checked join plan and canonical projective transversal. Every
   retained matrix N is invertible and equals the named structure ordinal.
   Input, model, target, plan and raw-unit hashes identify this exact unit.
3. The literal binary quartic, with its scalar, transported by N. Its four
   projective branch points are distinct. Infinity participates in support
   and square-class calculations.
4. The full coefficient-conjugate list `f_i=sigma^i(f_0)` for `0<=i<n`,
   closing at n. Shorter quartic orbits are allowed: the full list may contain
   repeats. No assumption of independence or exact minimal orbit length n is
   made for exceptional rows.
5. Exact geometric and arithmetic square-class kernels of this list, including
   leading coefficients. Write their span ranks as `r_g` over the algebraic
   closure and `r_a` over K(x). No subset relation is omitted.

Use the **coherent field**
`L=K(x)(sqrt(f_0),...,sqrt(f_(n-1)))` in a common separable closure, with
consistent relation witnesses. This is not the unconstrained tensor algebra
with independent formal signs on dependent generators. For actual quartics
`r_g>=1`; `r_a-r_g` is 0 or 1.

## 2. Universal same-source composition

Write N=(a,b;c,d), delta=ad-bc != 0. Define

```
x = (a*t+b)/(c*t+d)
y = delta^2*w/(c*t+d)^2
F_N(X,Z) = F_T(d*X-b*Z, -c*X+a*Z).
```

Substitution gives
`F_N(x,1)=delta^4*F_T(t,1)/(c*t+d)^4=y²`.
The rational inverse is

```
t = (d*x-b)/(a-c*x)
w = y*(c*t+d)^2/delta^2.
```

Thus this weighted projective change preserves the exact K-function field and
scalar, rather than reconstructing a curve from its branch set or j. The
checked base quotient inverse supplies E's original coordinates. Birational
maps between the smooth projective normalizations extend across the omitted
affine denominators; the implementation must still name/check the infinity
and exceptional charts so it cannot accept a singular or changed binary form.

**Amortization:** check the base elliptic quotient and its inverse once per
unit, check this universal polynomial identity once in the reviewed theorem,
then verify each row's determinant, ordinal and five literal transported
coefficients independently. Do not instantiate Python `FunctionField` for
every exceptional row. A universal proof does not excuse a row's incorrect
matrix, scalar, source quotient or coefficients.

Source interfaces: `implementation/source_map_binding.py::certify`,
`::certify_bound`, `independent_source_map_check.py::verify`,
`check_structure_certificate.py::transform`, and `source_fixed_unit.py::assess`.
The current last function takes a free row argument and builds a full fixed
model; a production wrapper must instead consume the exact sealed row and
full independent review, rather than accepting an unbound supplied example.

## 3. Odd-order lift and coefficient obstruction

### Lemma A: a lift exists for the coherent field

L/K(x) is a finite elementary-abelian 2-extension of degree `2^r_a` by Kummer
theory. The conjugate list is sigma-stable. Any extension of sigma to a
separable closure sends each radical to a root of the next conjugate, hence
preserves L. Thus L/k(x) is Galois and restriction gives an exact sequence

```
1 -> (C2)^r_a -> Gal(L/k(x)) -> C_n -> 1.
```

Choose any g above the specified sigma. Its order is `n*2^s`: g^n lies in
the 2-group kernel. Choose e with `e=1 (mod n)` and `e=0 (mod 2^s)`.
Then h=g^e still restricts to sigma and has exact order n. With
`D=L^<h>`, `D K=L` and `D∩K=k`; indeed h acts faithfully on K and
`[L:D]=[K:k]=n`. This proves effective field descent at the existence level.
It neither supplies the existing sign solver's output nor a serialized fixed
multiplication table. A sign-search miss cannot refute this lemma.

### Lemma B: equality of ranks gives a geometrically connected descent

After extending constants to an algebraic closure, the multiquadratic rank
is `r_g`, so the coherent K-field splits into `2^(r_a-r_g)` geometric
components. Equivalently, the kernel of the square-class map consists of
constant classes. This follows also from even valuations on P1: a rational
function with even divisor is a constant times a square; only the leading
coefficient square class remains. Finite K has just one nontrivial constant
square class.

If `r_a=r_g`, the constant field of L is exactly K, and D's constants are k.
The smooth projective curve of D is geometrically connected; after base change
to K its function field is L and it covers the source E through the specified
`sqrt(f_0)` embedding. Its geometric genus is that of L. This is the proposed
**equivalent sufficient descent certificate**, explicitly permitted by
H-PEXT-c3a11d's proof obligations and `design-obligations.md` item 4.

If `r_a=r_g+1`, an explicit geometric relation with nonsquare constant shows
that L contains `F_(q^(2n))`. This is the full extra constant extension:
the constant quotient of the elementary 2-group is cyclic and hence has order
at most 2. There are two geometric components. The order-n lift still exists,
but D has constants F_(q^2); it is not a geometrically connected curve over k.
Record a **constant-field connectedness obstruction for this exact coherent
construction**, with the relation mask/constant witness. Do not assert that
E has no other descent or that no order-n lift exists. Choosing a geometric
component after enlarging constants changes the object and is outside this
certificate.

For component genus let b count distinct projective branch points of the
geometric span, with irreducible factors weighted by degree and infinity
included. Tame inertia has order 2, so
`2*g-2 = -2*2^r_g + b*2^(r_g-1)`.
Independently check this using the character-subcover genus sum. In the
rank-difference-one case report the genus per geometric component, but do not
fill a connected k-curve genus. No coefficient twist is discarded.

**Reviewer challenge:** verify normality, coherent-field rather than tensor
semantics, the faithful constant action and D K identity, regularity and the
source embedding, the constant-field obstruction's scope, and equivalence to
the contract's descent requirement. The paper's scalar restriction must be
reconciled through the coefficient-aware kernel, never ignored. Until an
independent `review-adversarial/xhigh` session accepts these applications and
the exact checker interface, every affected production label stays unresolved.

## 4. Compact proof application and complete coverage

The existing `generic_interval_descent.py` handles the exact complement of the
exceptional ordinal set: disjoint supports force `r_g=r_a=n` and genus
`1+(n-1)*2^n`. Its coverage premise depends on the separately reviewable
collision-completeness proof. Preserve the checked rational/nonrational root
partition, cocycle index, infinity cases and full half-range collision powers.

Exceptional ordinals need not be contiguous. They may be grouped in a rank
class **only after** every member's premises are independently checked. A
matching rank pair or a representative's proof is insufficient. The generic
interval theorem cannot be applied to exceptional intervals by analogy.

Proposed minimal additional per-unit artifact, not a current native schema:

```
theorem_sha256, accepted_review_sha256 [null until actual formal acceptance]
base_quotient_certificate_sha256, published input/plan/model/T identity
raw_unit_sha256, full_independent_review_sha256
exceptional_rows_sha256, positional_squareclass_vector_sha256
generic_certificate_sha256, generic_interval_digest
checked row count; checked source/orbit/kernel/genus counts
admissible/inadmissible/unresolved counts; rank-pair counts
class-index membership digest in canonical ordinal order
generic + exceptional disjoint-union count and complete structure range
```

The source raw unit already retains ordinals, matrices and rank/branch/genus
rows plus positional arithmetic rank/constant flags. Do not duplicate one
large model, one source map or a separate 32-byte hash for every row. A
canonical streaming digest binds the checked row-to-class sequence; a checker
must recompute that sequence from sealed bytes. A digest alone is no proof.
Retain a concrete nonsquare-relation mask/constant witness for each applicable
row, encoded compactly or deterministically rederived by the complete checker.
Never discard old candidate bytes or overwrite old receipts to save space.

Exact status semantics after both review and implementation gates pass:

- Per structure: checked source + all premises + equal ranks gives a sufficient
  descent proof; a checked nonsquare-constant relation gives the scoped
  connectedness obstruction. Missing premise, review or coverage is unresolved.
- Per unit: `certified_admissible` iff every structure is checked admissible;
  `certified_inadmissible` iff every structure is checked inadmissible; `mixed`
  iff complete coverage contains both; any unknown gives `unresolved`.
- Derive a descriptive admissible minimum only from complete verified coverage.
  A partial candidate minimum is an upper bound, not an exhaustive minimum;
  unknown rows, including lower-genus rows, remain visible. Empty admissible
  sets get null, not an invented minimum. P3 remains geometric.

## 5. Concrete implementation and independent-verifier changes

These are proposed changes, not code introduced by this packet:

1. Add a compact source/descent proof-application module and a separate checker.
   Reuse unit-level published `CandidateBinder` identity, but independently
   verify base quotient equations/inverse and per-row scalar transport. Reuse
   per-cohort field/cocycle data without trusting producer table entries.
2. Extend `candidate_unit.rs`/the native candidate implementation to expose a
   compact relation witness when needed. `squareclass_relations.py` is the
   specification oracle, not the production per-row implementation. An
   incidence matrix has n columns and at most 4n branch-support rows, plus
   one coefficient row; bit-packed elimination obtains both ranks and a
   witness. Independent weighted-factor versus direct-incidence paths must
   agree. No brute-force square-root scan is needed for theorem application.
3. Implement independently owned compiled finite-field/polynomial replay for
   the complete exceptional pass, or demonstrate another exact checker with
   qualified fit. The current Python `independent_candidate_unit.py` full
   geometry path and `check_prospective_unit_descent.py` recompute every row;
   merely replacing the producer's model builder leaves that cost in place.
   The checker must not import the producer's rank/genus implementation or
   trust its multiplication table. Keep Python for small adversarial fixtures.
4. Join the new proof application with exact sealed artifacts in
   `candidate_unit_artifact.py`, `prospective_unit_descent.py`, its checker
   and `geometric_reducer.py`. Existing unresolved records remain immutable;
   new artifact/version names and additive contract changes require review.
5. Add final certified C5 metadata and blind custody separately from
   `c5_metadata_preview.py`/`c5_preview_stage.py`. `c5_selection.py` must run
   with preview=False only on a complete checked table. Retain the current
   refusal of unresolved rows. No rename of a preview into certified output.

For C5 retain first/lower-middle/last canonical unit in every occupied
cohort/torsion-count/T-index/descent-status stratum, **all T units of every
special-j class**, all counterexample units (including curve-level flags),
and all Type2-hyperelliptic-witness units with exact ordinals. The second
implementation recomputes selected units, including every structure's compact
premises and explicit source/action/fixed-model checks where applicable;
reserve the expensive full fixed-model path for selected units rather than
running it on the full cohort. Generic ranges can retain their proved
interval representation; no forced expansion of billions of generic rows.
If this complete mandatory selection cannot fit, C5 has not passed: do not
sample it down. For obstructed rows independently verify the obstruction;
never demand a nonexistent connected k-model as a control outcome.

Seal producer outputs and selection metadata first. Expose permitted identity,
source and witness flags to the independent implementation while withholding
producer genus/minimum answers and summaries until its recomputation is sealed.
The current candidate unit includes genus values, so blindly handing the same
raw JSON to the independent reviewer is not sufficient: a hash-bound sanitized
projection and later unblinding/full-custody check are a missing interface.
Exact independent serving/session and mandatory contract/tool access also
remain separate admission gates.

## 6. Cost model, ceilings and qualification

The optimization removes per-row Python rational-function model construction,
finite-field root scans and `d^2` fixed multiplication tables (`d=2^r_a`).
It does not remove exact row verification, candidate-set completeness, scalar
checks, C3 reverse-order work, storage or the mandatory C5 selection.

For each stage budget the sum

```
field/index setup + build + candidate generation and C3
+ unit base-map checks
+ E*(producer compact premises + independent compact replay + encode/hash/write)
+ Type2 checks + C0/C1/C2/C4/C6/C7 work
+ mandatory C5 selected-unit explicit model/replay costs
+ analysis/export/supervisor/receipt and cleanup costs.
```

E is the actual exceptional-row count, not the logical structure count.
The q11 synthetic-pattern scenario is 81,749,543 rows before two factor
patterns: not an actual cohort count, lower bound or completed observation.
Even giving that scenario the entire 28,800 s leaves only about 352 microseconds
per exceptional row for **all** work, or about 2,839 rows/s; setup, omitted
patterns and review reduce the allowance. Its 5,322 units allow about 5.41 s
per unit before those charges. Hence no Python per-row strategy is qualified
by this derivation, and the compiled approach is a feasibility proposal,
not a measured fit. Square-character/field tables may be built once per
cohort; no O(|K|) square-root lookup per row is allowed in the proposed path.

Preserve all six stages and ceilings: regression 7,200 s; orbits 3,600 s;
n3core 21,600 s; n3ext 28,800 s; n5 21,600 s; analyze 3,600 s. Total 86,400 s,
24 CPU-hours, one worker, 4 GB memory, six runs, zero retries and zero cloud
dollars. The existing producer worker has a 3 GiB sublimit: validate combined
worker/checker/supervisor memory, not each process in isolation. Qualify local
disk/encoded-byte volume and write/readback cost under actual available space;
no remote storage operation or cloud capacity is authorized here. If needed
storage or total remaining budget is unknown/unavailable, admission stays
blocked. A 256 MiB raw worker-line bound is not a whole-campaign storage budget.

Any later qualification needs its own allowed source-bound commands, published
inputs/configuration, finite caps and accounting; this packet runs none. A
source-cost upper bound or a separately authorized qualification must include
worst required factor patterns, maximum selected C5 load and independent
checker reserve before full-cohort admission. If it does not fit, preserve the
cohorts and stop/record the obstruction; do not widen caps or cut samples.

## 7. P1–P4, C0–C7 and failures retained

P1 branch types; P2 geometric spectra for abstract n=3/5/7; original P3
geometric minima on full q5/q7/q11 n3 and all 488 q3/n5 classes; and P4
Type2 signature versus its separate Mobius predicate remain unchanged.
Descent-admissible minima are descriptive. H1 q13 remains a separate
descriptive arm; it is neither substituted into P3 nor omitted to save cost.

C0 retains exact T=O historical alignment; C1 odd-order baseline; C2 valid
synthetic patterns and malformed-certificate rejection; C3 exact reversed
order equality; C4 scalar twists/same-j distinct models and the rank-two
restriction; C5 as above; C6 seeded same-curve projective transport including
scalar/infinity/inverse; C7 independently sampled matched random quartics,
weighted-factor versus direct incidence and separate destination identity.

A changed hash, matrix/ordinal, scalar, kernel, genus or coverage is invalid
instrument/custody evidence. Missing theorem review or unsupported premises
are unresolved. A sign search with no result remains an instrument error.
Timeout, OOM, disk cap, failed control or missing mandatory C5 unit stops the
dependent certification; retain exact partial coverage and remaining work,
without replacement curves, an extra seventh run or automatic retry. Only an
independently rederived, identity/coverage/control-valid discrepancy may enter
the mathematical counterexample path. No current status changes in this report.

## One next action

Coordinator: obtain a formal independent source-level review of the two lemmas,
source-composition proof, coefficient obstruction and proposed theorem-application
interface against these pinned sources; require explicit acceptance or an exact
gap before implementing any certified label. Then use that review to fix the
bounded compact checker and resource-qualification scope. No cohort dispatch or
approval follows from this packet.
