# Independent review — joint A: one-shot counts and repeated history

Task: `TASK-20261102-70be48`

Canonical reviewer task: `/root/review_one_shot`

Review head: `fbb6c5d6f8bbae160e51404172996c837efb0a07`

Producer snapshot: `674b3248a8b007748a2cf4f10e5063e7de123be4`

Joint: `A` only

## Verdict

**A: breaks as a formal target.** Exact hosted Lean 4.35 run `41503944712`
completed with failure at source line 117: `Unknown constant
Finset.sum_le_sum`. The declaration therefore is not formally discharged at
the reviewed snapshot.

Separately, the finite-cardinality countermodel and conditional real-sequence
repair are mathematically correct: the source statement matches the frozen
target, the hand derivation matches the intended proof structure, and the
same-marginals control fails exactly when the history recurrence is removed.
That semantic result does not convert the failed source into a Lean theorem.
No local formal build or axiom audit was run because the precommitted plan
budgets zero formal builds for reviewers.

| Dimension | Status | Exact scope |
| --- | --- | --- |
| Machine status | `failed` | Run `41503944712`; line 117 reports unknown constant `Finset.sum_le_sum` |
| Fidelity | `faithful_scoped` | Bool cardinalities plus the explicitly assumed recurrence over `S : ℕ → ℝ` |
| Joint verdict | `breaks` | The exact formal artifact does not elaborate; joint A only |

The theorem source, target spec, and source note at the review head are
byte-identical to their versions at the producer snapshot. Their SHA-256
values are respectively
`d0f23ea9395bc8b3a8e2da15f73fdb43d30025571b708cdb4f2ed8bb2b8e76c1`,
`454e43192383e8e38c465eca5b2d9827c844e1d3a3edef6207918bfcda9c037e`,
and `4834787c796eec875c33ca16ad75801c99102b31bbc565e0694311cc63b70a68`.

## Exact finite recomputation

The definitions at lines 26–32 make the complete truth table immediate:

| Process | Successful outcomes at trial `false` | Successful outcomes at trial `true` | Outcomes failing both |
| --- | ---: | ---: | ---: |
| `correlatedSuccess` | `{true}` | `{true}` | `{false}` |
| `complementarySuccess` | `{false}` | `{true}` | `∅` |

Thus each one-shot set has cardinality one. The joint-failure cardinalities
are one and zero respectively. For the natural-numbered correlated process,
`outcome = false` fails every trial because success is defined solely as
`outcome = true`.

### Clause-to-proof table

| Audited declaration clause | Independent recomputation | Source proof location | Result |
| --- | --- | --- | --- |
| Every correlated Bool trial has one successful outcome | The success set is `{true}`, independent of the trial | lines 34–41, assembled at 155 | holds |
| One outcome fails both correlated trials | `false` fails both; `true` fails neither, so the set is `{false}` | lines 43–54, assembled at 155 | holds |
| Every complementary Bool trial has one successful outcome | At trial `t`, success is exactly outcome `t`, so the set is `{t}` | lines 56–63, assembled at 156 | holds |
| No outcome fails both complementary trials | `false` succeeds in trial `false`; `true` succeeds in trial `true` | lines 65–76, assembled at 156 | holds |
| A correlated outcome fails forever | Witness `false`; it never equals `true` | lines 78–80, assembled at 157 | holds |
| Recurrence implies the geometric lower bound | Induct on `n`, multiplying by the nonnegative factor `1-ε` | lines 99–111 | holds |
| Geometric lower bound implies the finite tail inequality | Sum pointwise bounds, scale by `ε ≥ 0`, then use the finite geometric identity in the correct orientation | lines 113–126 | mathematics holds; Lean fails at line 117 before discharge |
| The repair occurs in the exact audited declaration | The final conjunct universally quantifies `S, ε` and takes every repair premise before returning both conclusions | lines 146–160 | type text is faithful, but declaration is not machine-verified |

No occurrence of `sorry`, `admit`, a custom `axiom`, `unsafe`, or
`native_decide` appears in this module. That textual check is not an axiom
audit and does not repair the failed machine status.

### Machine failure localization

The failing line is

```lean
exact Finset.sum_le_sum fun i _hi ↦ hgeometric i
```

In the pinned Mathlib tree, `sum_le_sum` is exposed in namespace `Finset` by
`Mathlib.Algebra.Order.BigOperators.Group.Finset`; none of this target's four
declared imports made that constant available in the hosted build. This is an
import/elaboration defect, not a counterexample to the inequality. Adding an
appropriate import or otherwise rewriting the finite-sum comparison would be
a producer change and would require a new immutable snapshot and exact rerun;
this reviewer did not edit or test such a repair.

## Recurrence and tail derivation

Set `q = 1 - ε`. The premise `ε ≤ 1` gives `q ≥ 0`.

For the geometric lower bound:

1. `q^0 = 1 = S 0`.
2. If `q^n ≤ S n`, nonnegativity of `q` gives
   `q * q^n ≤ q * S n`.
3. The recurrence gives `q * S n ≤ S (n+1)`.
4. Since `q^(n+1) = q * q^n`, induction gives `q^n ≤ S n` for all `n`.

For the finite tail, pointwise summation gives

```text
sum_{i < N} q^i <= sum_{i < N} S i.
```

Scaling by `ε ≥ 0` preserves the inequality. Mathlib's
`geom_sum_mul_neg` has the orientation

```text
(sum_{i < N} q^i) * (1 - q) = 1 - q^N.
```

Because `1-q = ε`, this yields exactly

```text
1 - q^N <= ε * sum_{i < N} S i.
```

The proof's `symm` at lines 123–124 is therefore necessary and correctly
orients the imported identity. The nonnegativity premise on `S` is stated as
the target requires, although this proof does not use it: `S 0 = 1`, `q ≥ 0`,
and the recurrence already propagate the lower bound needed by the argument.
That redundancy does not weaken the theorem or add a hidden assumption.

### Endpoint checks

| Case | Geometric clause | Tail clause |
| --- | --- | --- |
| `ε = 0` (`q = 1`) | Recurrence is `S n ≤ S (n+1)`, so `1 ≤ S n` from `S 0 = 1` | Both sides are zero for every `N` |
| `ε = 1` (`q = 0`) | At `n=0`, `1 = S 0`; at `n>0`, the claim is `0 ≤ S n` | For `N=0`, both sides are zero; for `N>0`, the left side is one and the sum contains `S 0 = 1` plus nonnegative terms |
| `N = 0`, any allowed `ε` | Not applicable | `1-q^0 = 0` and the range sum is empty, so equality holds |

There is no division by `ε`, so neither endpoint is silently excluded.

## Proves-too-much controls

### Same marginals, different history

Under the uniform two-outcome reading, both displayed processes have
one-shot success probability `1/2` at each Bool trial. After ordering the two
trials as `false`, then `true`, their survival prefixes are

| `n` | correlated `S n` | complementary `S n` |
| ---: | ---: | ---: |
| 0 | `1` | `1` |
| 1 | `1/2` | `1/2` |
| 2 | `1/2` | `0` |

Take `ε = 1/2`, so `q = 1/2`. For the complementary history the recurrence
at `n=1` would require `1/4 ≤ 0`, which is false. The geometric conclusion
also fails at `n=2`, again requiring `1/4 ≤ 0`. If the process is extended so
that survival stays zero after the second trial, then at `N=3` the proposed
tail conclusion without the recurrence would say

```text
7/8 <= (1/2) * (1 + 1/2 + 0) = 3/4,
```

also false. Therefore marginal counts cannot derive the recurrence or either
history conclusion. This is the required known-false control, not merely a
replay of the producer proof.

The correlated history, by contrast, has `S 0 = 1` and `S n = 1/2` for
`n ≥ 1`; it satisfies the `ε = 1/2` recurrence. Equal marginals therefore
coexist with different recurrence behavior.

### Probability-semantics control

The formal repair also applies to algebraic sequences that cannot be survival
probabilities. For example, `S n = 2^n` with `ε = 1/2` satisfies every typed
premise but exceeds one. Consequently, any attempt to read an expectation,
probability law, independence statement, or stopping-time theorem directly
from this type would prove too much. The type proves only the displayed
real-sequence inequalities.

## Hypothesis delta and missing bridges

There is **no hypothesis delta** between the frozen repair claim and the exact
audited declaration. `autoImplicit false` is set, and the declaration is
closed: every binder and side condition (`S`, `ε`, `S 0 = 1`, both epsilon
bounds, pointwise nonnegativity, and the recurrence) is present in the source
claim. The fixed `Bool`, `ℕ`, and `ℝ` types are also the types named by the
claim. No unstated `Fact`, probability instance, independence instance, or
xedni premise appears.

| Potential inference | Present in the theorem type? | Review finding |
| --- | --- | --- |
| Uniform probability measure on `Bool` | No | `Set.ncard` is only the explicitly declared two-point counting proxy |
| Conditional-event derivation of the recurrence | No | The recurrence is a premise, and the same-marginals control shows why it cannot be inferred here |
| Independence of repeated trials | No | The two processes are deterministic predicates on a shared outcome |
| Tail sum equals an expected waiting time | No | There is no probability space, random variable, stopping time, limit, or integrability statement |
| Infinite-tail limit or expected runtime | No | Only a finite sum indexed by `Finset.range N` is concluded |
| Xedni sampler, selected lifts, useful relation, or per-attempt cost | No | No corresponding object occurs in the type |
| Height/discriminant comparison or Lang input | No | No elliptic curve, height, discriminant, or conjectural premise occurs |
| JKSST Theorem 4.1 | No | The target neither instantiates nor refutes the paper's conditional one-attempt statement |

These are scope boundaries, not proof defects. Any downstream record must
retain them.

## Primary-source comparison

I retrieved the author-hosted JKSST PDF and verified SHA-256
`981bf955f7aecc5df4f271837f6653bd7666e5026f59df44196609d4a1dd6bc7`.
Section 3.2 defines the finite-field random choices and lift algorithm.
Theorem 4.1 states, under the paper's plausible assumptions, a one-attempt
success probability below `C0/p`. Lemma 4.1 assumes the selected-lift
height/discriminant comparison and invokes Lang's conjecture to obtain an
absolute relation-coefficient bound. The text after the theorem says the
algorithm must be repeated on the order of `p` times with different Step-3
choices, and Section 6 summarizes the asymptotic and empirical obstruction.

Those sections do not supply the formal history-uniform recurrence used here,
nor does this Lean target supply any JKSST premise. The target is therefore a
guardrail against promoting a marginal one-attempt statement into a joint-law
or expectation theorem. It is not an erratum to JKSST, a proof of its runtime
claim, or a refutation of Theorem 4.1 under its stated assumptions.

## Exact unresolved scope

- Hosted run `41503944712` failed at line 117. The reviewed declaration has no
  successful elaboration, named-target verification, transitive axiom audit,
  or kernel-acceptance evidence.
- A prospective import/proof repair has not been authored or tested here. It
  would be a new producer snapshot requiring fresh verification and affected-
  joint review.
- No independent binary/kernel rechecker was run.
- No general probability model connects the Bool counts to event
  probabilities, or `S` to an actual survival event.
- No theorem derives the recurrence from conditional success probabilities or
  identifies the finite/infinite tail sum with an expectation.
- No xedni sampler, selected-lift interface, JKSST height premise, Lang input,
  useful-relation recovery, attempt independence, or cost model is reviewed by
  this declaration.
- This report covers joint A only. It does not review joints B–F, read their
  reports, or compose a verdict for the five-target batch.

## Procedure and independence

I read no sibling-review directory or report and communicated with no other
reviewer. I derived the truth tables, recurrence, geometric identity, endpoint
cases, and same-marginals countercontrol before inspecting the Lean proof body.
That calculation is an independent specialist check; it is not claimed as the
round's designated blind re-derivation, which belongs to joint F. No
blindness lift or reviewer procedure deviation occurred. No scientific trial,
formal build, source edit, commit, or push was performed.
