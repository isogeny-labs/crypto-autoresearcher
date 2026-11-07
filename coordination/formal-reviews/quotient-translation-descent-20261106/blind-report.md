# Blind re-derivation (J4): TASK-20261106-bb6ab4

Authorized by DEC-20261106-2f9a94 (not read; the handoff's id only).
Session `session_01TCbLH9HCFyXdMUQej4nLk2`. Inputs: the handoff statement only.
Run budget 0; no experiment was run.

**Verdict: holds.** For every additive commutative group E and all S, T in E,
(∀ P, −(P+S)+T = −(P+T+S)) ⟺ 2T = 0. There is no counterexample. Formal part:
**infrastructure_error.** Lean source was written but not elaborated, because
this session could not install a Lean toolchain (see §5).

## 1. Statement, and what the two sides are

The statement takes E as an additive commutative group with S, T ∈ E, ι_S(P) = −(P+S)
and τ_T(P) = P+T. Then
τ_T(ι_S(P)) = −(P+S)+T and ι_S(τ_T(P)) = −((P+T)+S). The claim is
(∀P ∈ E, −(P+S)+T = −(P+T+S)) ⟺ T+T = 0.

## 2. Derivation

For any P, let D(P) = [−(P+S)+T] − [−(P+T+S)].

1. **Commutativity is used here (step C).** In any group, −(x+y) = −y + −x. In a
   commutative group this equals −x − y, so −(P+S) = −P − S and
   −(P+T+S) = −P − T − S. Then D(P) = (−P − S + T) + (P + T + S). Rearranging the
   terms, which also uses commutativity, gives D(P) = T + T.
2. D(P) is therefore 2T, whatever P is. So, for each P, the equation at P holds
   exactly when D(P) = 0, that is, exactly when 2T = 0 (because a − b = 0 ⟺ a = b in a group).
3. (⇒) Take P = 0, which exists because E is a group: the equation at 0 gives 2T = 0.
   (⇐) If 2T = 0, then D(P) = 0 for every P. ∎

Without commutativity (written multiplicatively), (PS)⁻¹T = S⁻¹P⁻¹T and
(PTS)⁻¹ = S⁻¹T⁻¹P⁻¹. Cancelling S⁻¹ on the left, the equation at P is
**P⁻¹T = T⁻¹P⁻¹**. At P = 1 this gives T = T⁻¹, so T² = 1. Substituting back
gives QT = TQ for every Q = P⁻¹. So in an arbitrary group:

> (∀P, (PS)⁻¹T = (PTS)⁻¹) ⟺ T² = 1 **and T is central**.

Step C is the step where "T commutes with −P" is assumed. It is the only place
commutativity is needed. The direction (⇒ T² = 1) holds in every group.

## 3. Minimal hypotheses

| hypothesis | needed? | evidence |
| --- | --- | --- |
| Inverses (group, not monoid) | Yes | A commutative monoid has no `−`, so the statement cannot even be written. In Mathlib's weaker `SubtractionCommMonoid` (involutive `−` with −(a+b) = −a + −b, but no a + −a = 0), it fails: ({0,1,2}, max, 0) with − = id, S = 0, T = 1. The left side holds for all P, but 2T = max(1,1) = 1 ≠ 0. See the enumeration output. |
| Commutativity of E | Sufficient, not necessary | The exact condition is "every element with T² = 1 is central". It holds in Q8 (the only involution, −1, is central), so the statement holds in Q8, a non-commutative group. It fails in S₃ and D₄ (non-central reflections). Smallest group where it fails: S₃ (order 6). Smallest non-commutative group where it holds: Q8 (order 8). |
| Commutativity of T with all of E, for this particular T | Needed exactly when T² = 1 | This is the group version above. |
| Any condition on S | No | S cancels: D(P) does not depend on S, and in the group version S⁻¹ cancels on the left. |
| E non-empty / P = 0 available | Automatic | A group contains 0. That is what makes the ∀ and ∃ forms agree. |
| Finiteness, torsion, characteristic | No | — |

**Placement of "for all P".** In a commutative group the equation at each single
P is already equivalent to 2T = 0 (step 2). So all three forms hold:
(∀P, eq) ⟺ 2T=0, ∀P (eq ⟺ 2T=0), and (∃P, eq) ⟺ 2T=0. In a non-commutative
group the forms come apart. In S₃ the ∀-inside form fails for T a transposition.
The ∃ form fails for T a 3-cycle: T is conjugate to T⁻¹, so some P satisfies
P⁻¹T = T⁻¹P⁻¹, but T² ≠ 1. The pointwise form fails at a P where commutation
breaks. In Q8, where the ∀-inside form holds, the ∃ and pointwise forms still
fail: at T = i, P = j, the equation holds but T² = −1. See the `exists` and
`pointwise` columns in the enumeration.

## 4. Controls (a)–(e)

Each control is decided by a full hand calculation below. The exhaustive
enumeration in `blind-evidence/enumerate_controls.out` cross-checks it over
every (S, T) in Z/1–Z/8, Z/2², Z/2×Z/4, Z/2³, S₃, D₄ and Q8. "Smallest"
means minimal group order.

**(a) Non-commutative group: the variant is false, and the argument fails as it should.**
Take S₃ with composition (pq)(i) = p(q(i)), S = e, T = (0 1), P = (1 2), so P⁻¹ = P.
T² = e, so the right side is true. On the left, P·T = [2,0,1] (in one-line notation) and
T·P = [1,2,0]. Then (PS)⁻¹T = P·T = [2,0,1], while (PTS)⁻¹ = T⁻¹P⁻¹ = T·P = [1,2,0].
They differ, so the left side is false. The iff fails for every S (18 of 36 pairs: the 3
transpositions × 6 values of S). The derivation breaks exactly at step C, because T does not commute with P.
S₃ is the smallest non-abelian group, so it is the smallest counterexample. Result: fails_as_expected.

**(b) Conclusion T = 0: false.** Take Z/2, S = 0, T = 1. At P = 0: −0+1 = 1 and
−(0+1) = −1 = 1. At P = 1: −1+1 = 0 and −(1+1) = −0 = 0. So the left side holds for all P,
but T = 0 is false. Z/1 has only T = 0, so Z/2 is the smallest counterexample. The derivation
yields 2T = 0, not T = 0, so it does not prove this variant. Result: fails_as_expected.

**(c) Conclusion 2S = 0: false.** Take Z/3, S = 1, T = 0. The left side is
−(P+1) = −(P+1), true for every P. But 2S = 2 ≠ 0. In groups of order ≤ 2 every element
satisfies 2x = 0, so the variant agrees with the true main statement there. Z/3 is the
smallest counterexample. The derivation never constrains S. Result: fails_as_expected.

**(d) ι_S replaced by τ_S: false.** The equation becomes P+S+T = P+T+S, which is true for
all P in any commutative group. The variant would then force 2T = 0 for every T. In Z/3
with S = 0 and T = 1, the left side is true and 2T = 2 ≠ 0. Groups of order ≤ 2 have
exponent ≤ 2, so the variant holds there. Z/3 is the smallest counterexample. The
derivation fails because, without the negation, D(P) = 0 instead of 2T. The sign flip
supplied by ι is what produces T + T. Result: fails_as_expected.

**(e) Conclusion 4T = 0: false.** Take Z/4, S = 0, T = 1. At P = 0: −0+1 = 1 but
−(0+1) = 3, so the left side is false, while 4T = 4 = 0 is true. In Z/1, Z/2 and Z/3,
4T = 0 ⟺ 2T = 0 (in Z/3, 4T = T). In Z/2² every element satisfies 2x = 0. So Z/4
(order 4) is the smallest counterexample. The derivation yields 2T = 0, which is
strictly stronger than 4T = 0. Result: fails_as_expected.

None of these is an elaboration failure or an infrastructure failure. They are
checked counterexamples to the variant statements. The main statement had 0
mismatches in every commutative group enumerated, and in Q8.

## 5. Formal statement and proof

The file is `blind-evidence/BlindDescent.lean`
(sha256 `7478c812fc73237488026b2e72023275dc7cb414748d00d5818def8153a12d19`).
It holds:

```lean
theorem main {E : Type*} [AddCommGroup E] (S T : E) :
    (∀ P : E, -(P + S) + T = -(P + T + S)) ↔ T + T = 0
```

It also has `pointwise`, `exists_form`, `group_version` (T² = 1 ∧ T central) and
kernel `decide` examples for controls (a)–(e). The proof of `main` is the
derivation in §2, with `abel` carrying step C.

**Status: infrastructure_error, not elaborated.** No Lean toolchain or Mathlib is
installed in this container. The session's permission layer refused the attempt
to install elan, and I did not work around that refusal. The Mathlib lemma names in the file
(`sub_eq_zero`, `mul_inv_rev`, `mul_right_inj`, `inv_eq_of_mul_eq_one_right`,
`mul_inv_cancel`, `abel`, `decide` on `ZMod`/`Equiv.Perm (Fin 3)`) are recalled
from memory, not checked. The file is a proposed formalization, not a verified one.
The mathematical proof in §2 does not depend on it.

## 6. Evidence files

| file | sha256 |
| --- | --- |
| `blind-evidence/BlindDescent.lean` | `7478c812fc73237488026b2e72023275dc7cb414748d00d5818def8153a12d19` |
| `blind-evidence/enumerate_controls.py` | `1a5424558de3a0919abcaee178f0529ff65f980724bd9d54c23fa75df6f917a2` |
| `blind-evidence/enumerate_controls.out` | `aba16f341eca7ced63927ca3cca99cbb902a6483d4883bb53dca56ac6f21b1d9` |

The enumeration was run with `python3 -I enumerate_controls.py`. It is a
deterministic finite check, not an experiment.
