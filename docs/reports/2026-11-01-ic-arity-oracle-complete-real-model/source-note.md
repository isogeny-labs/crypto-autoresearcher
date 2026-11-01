# Complete real-model IC arity/oracle envelope: source note

Date: 2026-11-01  
Task: `TASK-20261101-978031`  
Formal target: `IC-ARITY-ORACLE-COMPLETE-REAL-MODEL-20261101`

## Result authored for verification

The separate module
`formal/CryptoResearch/IC/ArityOracleCompleteRealModel.lean` states and proves
the full real-valued envelope correction proposed by the sealed 2026-11-01
review. Its exact aggregate target is
`CryptoResearch.IC.ArityOracleCompleteRealModel.complete_real_model`.

This producer note records source authorship only. A later task owns the fresh
immutable machine receipt, and a separate independent session owns semantic
fidelity review. Successful source compilation here is not either of those
later gates.

## Mathematical definitions and result

For real `m>=2`, `k>=0`, `beta>0`, put

```text
d=m-1-k, q_F=max(k,2), q_G=max(k+1,2),
H(d,q,beta)=max(1-d beta,q beta).
```

The module proves the historical definitions rewrite to `H`. It defines
`IsPositiveInfimum f a` as both (i) `a` is a lower bound at every positive
argument and (ii) for every `epsilon>0` there is a positive argument with
value below `a+epsilon`. This directly covers the nonattained regime; no
minimum or compact-domain assumption is substituted.

For `q>0`, the complete envelope is:

- `d>0`: infimum `q/(d+q)`, uniquely minimized at `1/(d+q)`;
- `d=0`: infimum/minimum `1`, with all minimizers `0<beta<=1/q`;
- `d<0`: infimum `1`, with every positive-domain value strictly above `1`.

The optimized half-threshold, pointwise interval/endpoints, F/G comparison,
optimized equality/strictness, equal-unattained regime, sharp MITM class
bounds, boundary witnesses, and growing-arity no-uniform-gap schedule are all
fields of the aggregate proposition.

## Requirement-to-declaration map

| Requirement | Declaration(s) |
| --- | --- |
| `H`, explicit positive-domain infimum, `d/q` parameters | `envelope`, `IsPositiveInfimum`, `envelopeInf`, `dParam`, `qF`, `qG`, `infF`, `infG` |
| historical `F/G` normal forms | `costAll_eq_envelope`, `costOne_eq_envelope` |
| `d+q` positivity and specialized genuine infima | `dq_positive`, `cost_infima` |
| `d>0` infimum and unique minimizer | `envelope_infimum_pos`, `envelope_minimizer_pos` |
| `d=0` infimum and all minimizers | `envelope_infimum_zero`, `envelope_minimizer_zero` |
| `d<0` infimum and nonattainment | `envelope_infimum_neg`, `envelope_no_minimizer_neg` |
| optimized `<,=,>` half trichotomy | `envelopeInf_lt_half_iff`, `envelopeInf_eq_half_iff`, `half_lt_envelopeInf_iff` |
| pointwise open interval and two endpoints | `envelope_lt_half_iff`, `envelope_eq_half_of_d_gt_q` |
| pointwise `d=q` and `d<q` cases | `envelope_eq_half_of_d_eq_q`, `envelope_gt_half_of_d_lt_q` |
| pointwise F/G comparison and exact equality | `costAll_le_costOne_exact` |
| optimized equality and strictness | `infF_eq_infG_iff`, `infF_lt_infG_iff`, `optimized_equal_but_unattained` |
| MITM pointwise result | imported `mitm_never_sub_generic`, exposed by the aggregate |
| sharp MITM bounds | `mitm_infF_small_bound`, `mitm_infF_large_bound`, `mitm_infG_bound` |
| sharp witnesses | `mitm_infF_small_witness`, `mitm_infF_large_witness`, `mitm_infG_witness` |
| no uniform positive gap | `mitm_no_uniform_positive_gap` |
| F1 | `F1_nonattainment`, `blanket_attainment_control` |
| F2 | `F2_invalid_middle_bound` |
| F3 | `F3_pointwise_not_optimized` |
| F4 | `F4_strictness_boundaries` |
| F5 | `F5_unrestricted_branch_control` |
| positive/tie cases | `positive_exact_controls` |
| exact aggregate coverage | `CompleteRealModel`, `complete_real_model` |

## Sources actually read

Internal sources were read in full or in their directly relevant complete
sections before authoring:

- `formal/targets/ic-arity-oracle-threshold-20261024.yaml`;
- `formal/CryptoResearch/IC/ArityOracleThreshold.lean`;
- `ledger/proposals/IDEA-20261024-a2b05d.notes.md`;
- `ledger/proposals/IDEA-20261024-a2b05d.yaml`;
- `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-generic-oracle-arity-cost-floor.yaml`;
- both sealed reviewer reports under
  `docs/reports/2026-11-01-ic-arity-oracle-review/reviewers/`;
- the sealed synthesis report and `next-action.json` under
  `docs/reports/2026-11-01-ic-arity-oracle-review/synthesis/`;
- `src/crypto_autoresearcher/index_calculus/README.md`;
- `formal/README.md`, `formal/targets/README.md`, and
  `docs/formal-research-lane.md`.

No external literature is relied on for this elementary ordered-field/max
algebra. No novelty claim is made.

## Controls and open interfaces

F1-F5 are theorem-level exact substitutions, not prose examples. The named
known-false control proves that the `m=2,k=2` all-return infimum has no
positive-domain minimizer. The positive values are
`F(5,1/5,1)=2/5` and `F(3,1/4,0)=1/2`.

Still open and absent from every theorem type: an oracle implementation;
H1 yield and success probability; H2 useful independent relation rank and
stopping time; H3 achieved bit/arithmetic and memory complexity; H4 complete
oracle setup/output/verification cost; uniform growing-arity and factorial
terms; curve/family sampling; preprocessing/advice; transfer/descent and
scalar recovery; total expected time, memory, processors, communication, and
success amplification. Consequently this target supplies no algorithm,
speedup, global lower bound, or existence/nonexistence answer for prime-field
ECDLP or PFSE.

## Producer checks and attempts

The producer used exactly `leanprover/lean4:v4.35.0` (Lean 4.35.0, commit
`eb6cafb7290e8bd5f2937522d8d804f58f02bafc`) with the repository's pinned
`formal/lake-manifest.json`. The dependency materialization/build and final
module check were:

```text
PATH=/tmp/elan-ic-arity/bin:$PATH ELAN_HOME=/tmp/elan-ic-arity \
  lake build CryptoResearch.IC.ArityOracleThreshold
PATH=/tmp/elan-ic-arity/bin:$PATH ELAN_HOME=/tmp/elan-ic-arity \
  lake build CryptoResearch.IC.ArityOracleCompleteRealModel
PATH=/tmp/elan-ic-arity/bin:$PATH ELAN_HOME=/tmp/elan-ic-arity \
  lake env lean /tmp/ICArityProducerAudit.lean
python3 tools/formal_task.py \
  formal/targets/ic-arity-oracle-complete-real-model-20261101.yaml \
  --validate-only
```

The historical-module dependency build completed 1,018 jobs. The final named
module build completed 1,012 jobs. The audit printed the exact aggregate type
`CompleteRealModel` and reports only `propext`, `Classical.choice`, and
`Quot.sound`. The final source has no `sorry`, `admit`, custom `axiom`, or
`unsafe` declaration. The frozen target validator returns `OK` for the exact
task, theorem file, and qualified theorem name.

Two intermediate module builds failed before the successful build. The first
found proof-script normalization gaps in the epsilon witness, normal-form max
reassociation, division endpoints, witness rational identities, and concrete
controls. The second reduced these to endpoint denominator normalization,
equality orientation, three witness simplifications, and a concrete max
coefficient. No theorem statement, domain, quantifier, or required aggregate
field was weakened to repair either attempt. A scratch attempt summary is
preserved outside the repository at `/tmp/ic-arity-producer-attempts.md`.

Unresolved formal proof obligations: none in this producer module. Pending
workflow obligations are the separately owned immutable verifier receipt and
independent semantic-fidelity review.
