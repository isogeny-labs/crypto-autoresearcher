# Blind input: IC arity/oracle complete real model

Task: TASK-20261101-bab1cb, phase one only. Date: 2026-11-01.

Work over the real numbers with
`m >= 2`, `k >= 0`, and `beta > 0`. Define

```text
d   = m - 1 - k
q_F = max(k, 2)
q_G = max(k + 1, 2)
F(beta) = max(1 - d beta, q_F beta)
G(beta) = max(1 - d beta, q_G beta).
```

Without reading any candidate proof, target, source note, receipt, earlier
review derivation, synthesis, Git history, or conversation, derive:

1. the infimum over `beta > 0` of `H_{d,q}(beta)=max(1-d beta,q beta)`
   and all minimizers or a proof of nonattainment in every sign regime for
   `d`;
2. exact optimized and pointwise comparisons with `1/2`, including every
   equality case;
3. exact pointwise and optimized comparison/equality regimes for `F` and
   `G`;
4. the best lower envelopes implied by the class restriction `k >= m/2`
   for both `F` and `G`, with equality witnesses and whether either
   margin above `1/2` is uniform as `m` grows;
5. small exact substitutions sufficient to catch false blanket attainment,
   false unrestricted branch formulas, optimized/pointwise confusion, and
   false strictness.

Use a genuine infimum argument. In a nonattained regime, give both a lower
bound and an `epsilon > 0` approximation (or an equivalent `IsGLB`
argument), not an informal limit alone. State the quantifier order.

Seal the phase-one derivation and exact source inventory before the dispatcher
lifts blindness. This packet supplies definitions and questions only; it
supplies no candidate closed form and makes no algorithm, PFSE, or novelty
claim.

