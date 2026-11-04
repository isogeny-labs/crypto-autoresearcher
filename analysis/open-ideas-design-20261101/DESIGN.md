# Open-idea experiment designs (2026-11-01)

Design pass for every open idea in the ledger under the `design-experiment`
skill. An idea is **open** when its proposal record has `status: proposed`,
no `dominated_by`, and its `IDEA-*` id appears in no hypothesis or experiment
index. That query returned 11 ideas, all designed below.

Each design fixes: the sentence under test and its class, the arms and the
A/A / positive / negative controls, the variable ledger, seeds and blinding,
the primary metrics and their units, the stopping and invalidation rules, the
decision rule with its verdict vocabulary, and the falsifier. Machine-readable
records are in `protocols/`; validate with
`python3 tools/experiment_protocol.py validate <file>`.

**Status: designed, not approved, not run.** No data was taken; every protocol
records `filed_before_affected_data: true`.

## Index

| area | idea | design | protocol |
|:--|:--|:--|:--|
| PFDR | `IDEA-20261029-2e292c` | Strong algebraic backdoors selected without witnesses | `protocols/IDEA-20261029-2e292c.json` |
| PFDR | `IDEA-20261029-3d0e71` | Shared divisor coefficients with a Graeffe membership tower | `protocols/IDEA-20261029-3d0e71.json` |
| PFDR | `IDEA-20261029-8d82e6` | Resume prime-field CDCL with certificate-producing finite-domain theory | `protocols/IDEA-20261029-8d82e6.json` |
| PFDR | `IDEA-20261029-e4edce` | Partial multigraded Macaulay layers instead of whole-degree expansion | `protocols/IDEA-20261029-e4edce.json` |
| PFDR | `IDEA-20261029-ec08bc` | Complete chart-local saturation before expensive closure | `protocols/IDEA-20261029-ec08bc.json` |

## IDEA-20261029-2e292c — Strong algebraic backdoors selected without witnesses

**Area:** PFDR  
**Question:** Does a witness-blind, instance-computable backdoor cut leave a cheaper complete residual than equal-entropy random cuts and best fixed-block guessing on tiny exact digit-system instances?

**Hypothesis H1.** A small instance-computable backdoor chosen without any witness reduces complete residual cost by at least 2x against equal-entropy random and fixed-block cuts.

*Mechanism.* Conditioning a small set of carry or intermediate variables splits the system; if the split is chosen from instance structure rather than the solution, the residual branches shrink faster than a uniform-entropy cut.

**Claims.**

- `C1` (exact computation): Every candidate cut's residual is certified by exhaustive enumeration over the frozen tiny instances, so a claimed strong backdoor with one unresolved legal assignment is detected.
- `C2` (comparative, decided by `C-gain`): The witness-blind policy's total backdoor solve cost is at least 2x lower than both equal-entropy random cuts and best fixed-block guessing at the same entropy.

**Predictions.**

- `P1` `total_backdoor_solve_cost` (total backdoor solve cost): lower, minimum effect <=0.5x random and fixed-block
- `P2` `verified_model_count` (verified model count): equal_within, minimum effect equal to the exact oracle
- `P3` `exception_coverage` (exception coverage): equal_within, minimum effect 1.0

**Arms.**

- `fixed-block` (reference): best fixed-block guessing at matched entropy
- `witness-blind` (candidate): instance-computable cut chosen without any witness
- `random-entropy` (control_aa): equal-entropy random cuts on the same instances
- `planted-backdoor` (control_positive): planted synthetic circuit with a known small strong backdoor
- `exact-oracle` (control_negative): matched algebraic null with no planted structure

**Controls.**
- A/A: comparison `C-aa`.
- Positive: `planted-backdoor` — the planted small backdoor is recovered.
- Negative: `exact-oracle` — null population {'description': 'matched algebraic null instances with no planted backdoor', 'generator': 'matched algebraic null instances with no planted backdoor', 'n': 100, 'why_n': 'enough independent null draws to resolve the stated alpha under the family correction; the null is exact where the proposal states an exact count, and sampled otherwise', 'matched_on': ['size', 'field and curve shape', 'instrument', 'seed law']}.

**Variable ledger.**

- `cut_policy`: crossed — witness-blind, random, min-fill, fixed-block, rank-guided
- `instances`: fixed — independent of arm
- Instrument: fixed (one commit, flags and thread count per arm).
- Arm order: interleaved; seeds from the frozen protocol hash; analyst blinded.

**Metrics (primary).**

- `total_backdoor_solve_cost` (derived, field operations): selection cost plus every residual branch cost, summed, per verified relation
- `verified_model_count` (exact, count): models verified against the exact tiny oracle
- `exception_coverage` (rate, fraction): declared chart exceptions covered by the census

**Sample size and stopping.**
- Instances 50, replicates 1, warmups 0; family of 3 tests with holm correction.
- fixed: every frozen tiny instance x five cut policies, exhaustive residual enumeration, then stop.

**Decision rule.**

C-gain is supported when the witness-blind cut costs at most 0.5x both baselines at equal verified model counts and full exception coverage; one unresolved legal assignment in a purported strong backdoor refutes it, and a policy that needs known roots or test tuning is inadmissible.

**Inadmissible.**

- treating lower first-fall degree as lower solving cost
- tuning the policy on test instances
- claiming an escape from KN-OPEN-020

## IDEA-20261029-3d0e71 — Shared divisor coefficients with a Graeffe membership tower

**Area:** PFDR  
**Question:** For p with d=2^k dividing p-1 and at least five usable distinct x, does a shared-coefficient Graeffe tower reduce complete five-point decomposition work by 2x against per-root PKM, symmetric S6 and quotient towers on three matched cells?

**Hypothesis H1.** A shared divisor-coefficient Graeffe membership tower cuts complete five-point decomposition work by 2x relative to per-root PKM towers, without a degree or exponent claim.

*Mechanism.* Sharing the coefficient tower across roots moves repeated membership work into one Graeffe evaluation; if the correspondence holds, the complete cost falls even though the intrinsic degree does not.

**Claims.**

- `C1` (exact computation): Exact model agreement is required on identical squarefree charts before any timing; a missing or spurious relation invalidates the arm.
- `C2` (comparative, decided by `C-gain`): After matching permutation multiplicity and root sets, the Graeffe arm's complete relation cost is at least 2x lower on three matched k=3,4 cells.

**Predictions.**

- `P1` `complete_relation_cost` (complete cost per verified relation): lower, minimum effect <=0.5x per-root PKM
- `P2` `verified_model_count` (verified model count): equal_within, minimum effect exact agreement
- `P3` `chart_coverage` (chart coverage): equal_within, minimum effect 1.0

**Arms.**

- `per-root-pkm` (reference): per-root PKM tower
- `graeffe` (candidate): shared divisor-coefficient Graeffe tower
- `tower-aa` (control_aa): per-root PKM with a second root ordering
- `planted-relation` (control_positive): a planted five-point relation the tower must recover exactly
- `k2-empty` (control_negative): k=2 empty-chart control, where no usable five-point chart exists

**Controls.**
- A/A: comparison `C-aa`.
- Positive: `planted-relation` — the planted relation is recovered exactly.
- Negative: `k2-empty` — null population {'description': 'k=2 empty-chart cells where no five-point decomposition exists', 'generator': 'k=2 empty-chart cells where no five-point decomposition exists', 'n': 100, 'why_n': 'enough independent null draws to resolve the stated alpha under the family correction; the null is exact where the proposal states an exact count, and sampled otherwise', 'matched_on': ['size', 'field and curve shape', 'instrument', 'seed law']}.

**Variable ledger.**

- `tower`: crossed — per-root PKM, symmetric S6, quotient, Graeffe
- `cell`: fixed — matched chart sets
- Instrument: fixed (one commit, flags and thread count per arm).
- Arm order: interleaved; seeds from the frozen protocol hash; analyst blinded.

**Metrics (primary).**

- `complete_relation_cost` (counted, field operations): setup, tower, membership and verification per verified relation
- `verified_model_count` (exact, count): models matching the exact oracle
- `chart_coverage` (rate, fraction): squarefree charts covered by the census

**Sample size and stopping.**
- Instances 3, replicates 1, warmups 0; family of 3 tests with holm correction.
- fixed: three matched cells x four towers; exact model agreement first, timing second; k=2 negative control; then stop.

**Decision rule.**

C-gain is supported when complete relation cost is at most 0.5x per-root PKM on three matched cells after matching permutation multiplicity and root sets, with exact model agreement; any missing or spurious relation, or a gain that is only a permutation constant, refutes it.

**Inadmissible.**

- timing before exact model agreement
- reading a permutation-constant gain as a cost gain
- claiming a degree or exponent improvement

## IDEA-20261029-8d82e6 — Resume prime-field CDCL with certificate-producing finite-domain theory

**Area:** PFDR  
**Question:** Does bounded-PC learning prune before whole-block enumeration and cut charged search cost by 2x against the strongest enumeration/SMT control on held-out cells, with certificates that agree with the exact oracle?

**Hypothesis H1.** Bounded-PC learning with certificate-producing finite-domain theory prunes before whole-block enumeration and halves charged search cost.

*Mechanism.* A learned theory prefix can exclude blocks earlier than enumeration; it pays only if the explanation construction is cheaper than the enumeration it replaces.

**Claims.**

- `C1` (exact computation): Every UNSAT verdict carries a checkable certificate and every model is verified by group replay; invalid certificates or omitted finite domains invalidate the arm.
- `C2` (comparative, decided by `C-gain`): Charged search cost, all theory calls included, is at most 0.5x the strongest enumeration/SMT control on held-out cells.

**Predictions.**

- `P1` `charged_search_cost` (charged search cost): lower, minimum effect <=0.5x strongest control
- `P2` `verified_model_count` (verified model count): equal_within, minimum effect exact agreement
- `P3` `actual_solving_degree` (actual solving degree): different, minimum effect reported, not asserted lower

**Arms.**

- `enumeration-smt` (reference): strongest enumeration/SMT control
- `bounded-pc` (candidate): bounded-PC closure with proof export
- `pc-aa` (control_aa): bounded-PC replay on the same fixtures
- `known-unsat` (control_positive): a planted UNSAT instance with a known certificate
- `planted-sat` (control_negative): a planted SAT instance where pruning must not declare UNSAT

**Controls.**
- A/A: comparison `C-aa`.
- Positive: `known-unsat` — the known certificate is reproduced.
- Negative: `planted-sat` — null population {'description': 'planted SAT instances on which a sound pruner must not derive UNSAT', 'generator': 'planted SAT instances on which a sound pruner must not derive UNSAT', 'n': 100, 'why_n': 'enough independent null draws to resolve the stated alpha under the family correction; the null is exact where the proposal states an exact count, and sampled otherwise', 'matched_on': ['size', 'field and curve shape', 'instrument', 'seed law']}.

**Variable ledger.**

- `method`: crossed — enumeration/SMT, bounded-PC, plain Macaulay replay
- `cell`: fixed — held-out cells frozen before the run
- `instance_class`: crossed — varied by comparison C-gain
- Instrument: fixed (one commit, flags and thread count per arm).
- Arm order: interleaved; seeds from the frozen protocol hash; analyst blinded.

**Metrics (primary).**

- `charged_search_cost` (derived, charged operations): search plus every theory explanation call, per verified relation
- `verified_model_count` (exact, count): models verified by group replay
- `actual_solving_degree` (counted, degree): measured degree of the residual solve

**Sample size and stopping.**
- Instances 6, replicates 1, warmups 0; family of 3 tests with holm correction.
- fixed: replay the three s4,5,6 fixtures, then the held-out cells x two methods, then stop.

**Decision rule.**

C-gain is supported when charged search cost is at most 0.5x the strongest control, every certificate agrees with the oracle and no SAT instance is declared UNSAT; pruning only after all but one block is fixed, or explanation cost matching the enumeration, refutes it.

**Inadmissible.**

- counting theory calls as free
- accepting an invalid or missing certificate
- reporting a lower equation degree as lower work

## IDEA-20261029-e4edce — Partial multigraded Macaulay layers instead of whole-degree expansion

**Area:** PFDR  
**Question:** Do source-defined partial Macaulay degree layers with valid multigrading lower peak matrix entries by 2x and complete solve work by 20% at equal memory, without increasing the UNKNOWN rate?

**Hypothesis H1.** Partial Macaulay layers plus valid multigrading reduce measured algebraic solving work on structured prime-field PDP without asserting lower intrinsic regularity.

*Mechanism.* Multigrading restricts rows to the needed degrees; if the required source rank assumptions hold, the selected submatrices stay smaller and the complete solve is cheaper.

**Claims.**

- `C1` (exact computation): Complete solve and refutation outputs are compared at equal memory caps, and every attempted submatrix rank and full-layer certificate is recorded.
- `C2` (comparative, decided by `C-gain`): The combined partial-layer and multigraded arm cuts peak entries by 2x and complete solve work by 20% with no increase in the UNKNOWN rate.

**Predictions.**

- `P1` `peak_matrix_entries_and_field_ops` (peak entries and field operations): lower, minimum effect 2x fewer entries and 20% lower work
- `P2` `actual_solving_degree` (actual solving degree): different, minimum effect reported, not asserted lower
- `P3` `unknown_rate` (UNKNOWN rate): equal_within, minimum effect no increase against baseline

**Arms.**

- `full-layer` (reference): full-layer Macaulay baseline
- `partial-multigraded` (candidate): partial source-defined layers with valid multigrading
- `layer-aa` (control_aa): full-layer baseline on a second memory cap
- `full-cert` (control_positive): an instance with a known full-layer certificate
- `random-grading` (control_negative): random grading preserving degree, which must not show the gain

**Controls.**
- A/A: comparison `C-aa`.
- Positive: `full-cert` — the full-layer certificate is reproduced.
- Negative: `random-grading` — null population {'description': 'degree-preserving random gradings that carry no usable multigrading', 'generator': 'degree-preserving random gradings that carry no usable multigrading', 'n': 100, 'why_n': 'enough independent null draws to resolve the stated alpha under the family correction; the null is exact where the proposal states an exact count, and sampled otherwise', 'matched_on': ['size', 'field and curve shape', 'instrument', 'seed law']}.

**Variable ledger.**

- `layer_selection`: crossed — full layers, partial layers, partial+multigrading
- `memory_cap`: fixed — frozen before the run
- `grading`: crossed — varied by comparison C-gain
- Instrument: fixed (one commit, flags and thread count per arm).
- Arm order: interleaved; seeds from the frozen protocol hash; analyst blinded.

**Metrics (primary).**

- `peak_matrix_entries_and_field_ops` (counted, entries / ops): peak matrix entries and charged field operations of the complete solve
- `actual_solving_degree` (counted, degree): measured solving degree
- `unknown_rate` (rate, fraction): share of targets left UNKNOWN

**Sample size and stopping.**
- Instances 6, replicates 1, warmups 0; family of 3 tests with holm correction.
- fixed: one source calibration instance, then the small solver corpus x four ablations at equal caps, then stop.

**Decision rule.**

C-gain is supported when peak entries fall 2x, complete work falls 20% and the UNKNOWN rate does not rise; improvements that vanish once selection, retries and root extraction are charged, or a full-size required rank before success, refute it.

**Inadmissible.**

- reporting a smaller submatrix as evidence that d_reg fell
- charging selection or retries outside the metric
- comparing at unequal memory caps

## IDEA-20261029-ec08bc — Complete chart-local saturation before expensive closure

**Area:** PFDR  
**Question:** In the exact prime-field encoding, do exceptional denominator components rather than the genuine decomposition component account for a material part of solving cost, so chart-local saturation is 2x cheaper than the unsaturated exact baseline at identical recovered solution sets?

**Hypothesis H1.** Exceptional denominator components account for a material share of solving cost, and chart-local saturation removes it without discarding valid relations.

*Mechanism.* Saturating exceptional factors before the expensive closure removes components that are not the decomposition component; the gain is real only if the recovered solution set is unchanged and the certificate cost does not cancel it.

**Claims.**

- `C1` (exact computation): The exhaustive small chart census must produce exact chart-union model equality, including generic additions, equal-x, doubling, infinity and norm-denominator-zero cases.
- `C2` (comparative, decided by `C-gain`): Chart-local saturation cuts complete chart-union solve cost by 2x against the unsaturated exact baseline with an identical recovered solution set.

**Predictions.**

- `P1` `complete_chart_union_solve_cost` (complete chart-union solve cost): lower, minimum effect <=0.5x unsaturated baseline
- `P2` `verified_model_count` (verified model count): equal_within, minimum effect identical recovered solution set
- `P3` `exception_coverage` (exception coverage): equal_within, minimum effect 1.0 across the chart census

**Arms.**

- `unsaturated` (reference): unsaturated exact baseline
- `saturated` (candidate): chart-local saturation before closure
- `baseline-aa` (control_aa): unsaturated baseline on a second chart ordering
- `certificate-check` (control_positive): an independently checked saturation certificate
- `discard-branch` (control_negative): a branch-discarding cut that removes valid relations, which must be rejected

**Controls.**
- A/A: comparison `C-aa`.
- Positive: `certificate-check` — the checked saturation certificate reproduces the saturated ideal.
- Negative: `discard-branch` — null population {'description': 'a cut that discards valid relations, whose solution set must differ', 'generator': 'a cut that discards valid relations, whose solution set must differ', 'n': 100, 'why_n': 'enough independent null draws to resolve the stated alpha under the family correction; the null is exact where the proposal states an exact count, and sampled otherwise', 'matched_on': ['size', 'field and curve shape', 'instrument', 'seed law']}.

**Variable ledger.**

- `saturation`: crossed — unsaturated, chart-local saturated, branch-discarding
- `chart_case`: crossed — generic, equal-x, doubling, infinity, norm-denominator zero
- `relation_set`: crossed — varied by comparison C-gain
- Instrument: fixed (one commit, flags and thread count per arm).
- Arm order: interleaved; seeds from the frozen protocol hash; analyst blinded.

**Metrics (primary).**

- `complete_chart_union_solve_cost` (counted, field operations): saturation certificate plus closure per verified relation
- `verified_model_count` (exact, count): solutions matching the exact chart-union oracle
- `exception_coverage` (rate, fraction): declared chart exceptions covered by the census

**Sample size and stopping.**
- Instances 5, replicates 1, warmups 0; family of 3 tests with holm correction.
- fixed: exhaustive small chart census x three saturation arms, exact model equality first, then stop.

**Decision rule.**

C-gain is supported when saturated cost is at most 0.5x unsaturated with an identical solution set and checked certificates; a gain entirely from discarded valid relations, or from an equation count that leaves pivot ranks unchanged, refutes it.

**Inadmissible.**

- discarding valid relations as a cost win
- timing before exact chart-union equality
- claiming reduced pivot rank from a reduced equation count

