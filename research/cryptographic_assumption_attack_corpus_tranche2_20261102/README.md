# Cryptographic assumption attack corpus: tranche two

Date: 2026-11-02. Status: exact source statements for five Lean targets;
formal proofs and independent semantic review are separate deliverables.

## Scope and literature check

This tranche turns five frequently overgeneralized algebraic or probabilistic
inferences into small countermodels paired with the hypotheses that repair
them. It does not claim a protocol vulnerability, an ECDLP algorithm, or a
refutation of the cited primary sources.

The following primary sources were retrieved and read before the statements
below were frozen:

- Jacobson--Koblitz--Silverman--Stein--Teske, *Analysis of the Xedni
  Calculus Attack*, especially Section 3.2, Lemma 4.1, Theorem 4.1, and the
  conclusion. Author-hosted PDF SHA-256:
  `981bf955f7aecc5df4f271837f6653bd7666e5026f59df44196609d4a1dd6bc7`.
- RFC 9380, especially Sections 2.1--3 and 7. Retrieved text SHA-256:
  `a2e6ab02b2117d6f52ac293020857752972b2e23ae005c33f612e40436ff4b6d`.
- Pointcheval--Stern, *Security Arguments for Digital Signatures and Blind
  Signatures*, especially the random-oracle definition, oracle-replay
  construction, and forking lemmas. Author-hosted PDF SHA-256:
  `e3604629da7ce69f76c77c8a35ac130e99844f78db35b4d0f03dd27e0f7e0718`.
- Pedersen, *Non-Interactive and Information-Theoretic Secure Verifiable
  Secret Sharing*, especially Section 3 and Theorem 3.1. Publisher PDF
  SHA-256:
  `79c0634a04b7bc869715770519eca9dcfcb3011012dbff054b9487b187558b18`.

Repository inputs checked include `KN-LIT-021`, the 2026-11-01 attack-corpus
source note, its five-target Lean review packet, and the Sadek/xedni dependency
audit. The ranked labels used by the first packet are reconciled here with
the earlier queue labels: `ONE-SHOT-HISTORY` refines `ONE-SHOT-REPEAT`,
`COFACTOR-PUSHFORWARD` refines `COFACTOR`, and
`PEDERSEN-RELATION-KERNEL` refines `PEDERSEN-IPA`. `CUBIC-EVAL-RANK` was
previously prose rather than a queue row.

## 1. ONE-SHOT-HISTORY

### Countermodel

Let the uniform sample space contain two outcomes. In a fully correlated
process, every trial succeeds exactly on outcome `true`. In a complementary
two-trial process, trial `false` succeeds exactly on outcome `false` and trial
`true` succeeds exactly on outcome `true`. Every individual trial in both
processes has one successful outcome out of two. Nevertheless, the correlated
process has one outcome that fails both trials, whereas the complementary
process has none. The correlated process also has an outcome that fails every
natural-numbered trial.

Thus equal one-shot marginals do not determine joint survival, independence,
eventual success, a geometric law, or an expected waiting time.

### Conditional repair

Let `S n` be a nonnegative survival sequence with `S 0 = 1`, and let
`0 <= epsilon <= 1`. If the history-uniform success upper bound is supplied in
division-free form

```text
(1 - epsilon) * S n <= S (n + 1),
```

then `(1-epsilon)^n <= S n`. The corresponding finite tail-sum inequality is

```text
1 - (1-epsilon)^N <= epsilon * sum_{i < N} S i.
```

A separate probability theorem must derive this recurrence from conditional
event probabilities and identify the survival tail sum with an expectation.

### JKSST boundary

JKSST Theorem 4.1 is a conditional one-attempt bound. The paper later says
that the algorithm must be repeated at least order `p` times, but it does not
state a history-uniform conditional-hazard theorem or an exact geometric
waiting-time law. This target therefore attacks a marginal-to-history
inference; it does not refute Theorem 4.1 or instantiate its xedni sampler.

## 2. CUBIC-EVAL-RANK

### Countermodel

Use the ten standard homogeneous cubic monomials

```text
X^3, X^2Y, X^2Z, XY^2, XYZ, XZ^2, Y^3, Y^2Z, YZ^2, Z^3.
```

Over the rationals, the ten projective representatives
`P_i = (i,0,1)` for `i : Fin 10` are distinct. The nonzero cubic `Y Z^2`
vanishes at every `P_i`. Consequently the square evaluation matrix has a
nontrivial kernel and determinant zero. Distinct points alone do not impose
independent cubic conditions.

### Conditional repair

For any field and any ten points, a nonzero determinant of the corresponding
ten-by-ten evaluation matrix makes its coefficient map injective. Hence a
cubic coefficient vector that evaluates to zero at all ten points is zero.

### JKSST boundary

JKSST does not make the false distinctness-to-rank inference. Section 3.2 uses
only `2 <= r <= 9` and explicitly requires the `r`-by-10 matrix to have rank
`r`; Remark 2 uses the valid implication from rank to distinctness. The
ten-point example is a square-matrix guardrail, not an erratum or refutation
of the paper. It also uses a reducible singular cubic and proves nothing about
existence or nonsingularity of a kernel elliptic cubic in the paper's range.

## 3. COFACTOR-PUSHFORWARD

### Countermodel and exact finite control

On `ZMod 2 x ZMod 2`, scalar multiplication by two is constant zero. It is
neither a bijection nor a surjection onto the intended second factor, and its
fibres cannot define a uniform pushforward there.

On `ZMod 2 x ZMod 3`, scalar multiplication by two kills the first factor and
permutes the second. Its image is exactly `{0} x ZMod 3`; every point in that
image has exactly two preimages. Thus a uniform ambient input has an exact
uniform pushforward on the designated factor in this model, even though the
map is not an ambient bijection or an idempotent retraction.

### Conditional repair

For finite additive groups `K` and `S`, scalar multiplication by `h` on
`K x S` has image `{0} x S` and constant fibre size `|K|` if it annihilates
`K` and acts bijectively on `S`. These decomposition and invertibility
hypotheses, not the word “cofactor,” justify the exact count.

### RFC boundary

RFC 9380 says that `clear_cofactor` maps curve points into the target subgroup.
It explicitly calls `encode_to_curve` nonuniform despite using cofactor
clearing, attributes near-uniformity of `hash_to_curve` to the complete
construction, and warns that a specified `h_eff` may differ from `h`. This
target is therefore a guardrail against an overbroad inference, not a
refutation of RFC 9380 or a concrete curve suite.

## 4. FS-ZERO-HASH

### Countermodel

For the Schnorr-style verification equation

```text
s G = R + H(m,R) X,
```

a constant-zero challenge accepts `R = s G` for every public key `X`; the
constructor needs no witness. More generally, any publicly known constant
challenge `c` accepts the adaptively chosen commitment `R = s G - c X`.
Merely changing zero to a fixed nonzero constant is therefore not a repair.

### Algebraic control

For one fixed transcript `(m,R,s)`, if the challenge is nonzero, two public
group elements satisfying the same equation are equal. This is only a
fixed-equation uniqueness fact. Actual extraction still needs two accepting
same-commitment transcripts with distinct challenges, as in the earlier
special-soundness target.

### Pointcheval--Stern boundary

Pointcheval--Stern assumes a random oracle and explicitly accounts for oracle
queries, replay, fixed random tape/oracle prefixes, successful forks, and
distinct challenges. A constant hash is outside that model. The finite Lean
countermodel refutes only the slogan that special soundness by itself implies
Fiat--Shamir security; it proves no ROM/QROM attack on a compliant scheme.

## 5. PEDERSEN-RELATION-KERNEL

### Countermodel and collision characterization

Let `F` be a field, let `G` generate an injective scalar action, and let
`H = alpha G` with nonzero `alpha`. For

```text
Com(m,r) = m G + r H,
```

the nonzero vector `(alpha,-1)` is in the kernel. Every opening can be changed
to any requested message `m'` by setting
`r' = r + (m-m')/alpha`. Conversely, two colliding openings with different
messages have different blinders and reveal
`alpha = (m-m')/(r'-r)`.

### Pedersen boundary

Pedersen's Theorem 3.1 already states the computational boundary: the
generators are chosen so that nobody knows their discrete-log relation, and
different-message openings reveal it. The target refutes the shorthand that
two generators of a cyclic group are literally linearly independent. It does
not show that an outsider can compute `alpha`, prove a real-world commitment
break, or formalize a DLP reduction, adversary, runtime, or success
probability.

## Shared non-implications

The five finite statements do not discharge the JKSST height/discriminant
premise, Lang's conjecture, the approximate bounded-relation probability, or a
selected-lift interface. They also do not prove uniform hashing, Fiat--Shamir
security, Pedersen computational binding, or any concrete implementation
refinement. Those are separate theorem or game obligations.
