import CryptoResearch.Nagao.Lemma4Witness

/-!
# Nagao 2015/984 Lemma 4, outside (printed) placement: finite `F_2` counterexample

Source: `knowledge/findings/KN-FIND-936151.md` (the outside form was first refuted
in Python, `CORR-20260916-96f47d`; witnesses as in `Lemma4Witness.lean`).

`Lemma4Witness.lean` refutes the *inside* form, where both quantities are taken of
`F ++ S_fe`. Lemma 4 as printed takes the true first fall degree `d_F` of
`{f_1, ..., f_M}` alone, with the field equations NOT among its generators, and
the fake first fall degree `d'_F` modulo `S_fe`. This module refutes that
placement, in the same model and under the same equality reading of condition
(1), with the same two witnesses:

* `Lemma4Outside n F`: `d_F(F) <= d'_F(F)`, the fake side computed from `F`.
* `Lemma4OutsideFe n F`: `d_F(F) <= d'_F(F ++ S_fe)`, the fake side computed from
  `F ++ S_fe`. In the model the field equations reduce to zero and are dropped on
  the fake side, so the two fake quantities agree; both placements are stated so
  that neither reading of the fake side is left open.

For both witnesses `d_F(F) = 3`:
* A: `f_1 + X * f_2 = X^2 Y + X^2 Y + X^2 = X^2`;
* B: `X_3 * f_1 + X_2 * f_2 = X_2^2 + X_3^2`;
and no fall exists at degree 1 or 2. `d'_F = 2` as in `Lemma4Witness.lean`.
Every fact is checked by `decide +kernel` (no `native_decide`).

## What is NOT proved

The same prerequisites as `Lemma4Witness.lean`: that the list-of-exponent-vectors
model transcribes Nagao's Definitions 5 and 6; that restricting cofactors to
monomials of degree `<= D` loses nothing; that dropping fake-side generators that
reduce to zero is harmless. Nothing about the literal `>=` reading, Proposition 5,
`p >= 3`, `N > 3`, or any elliptic curve.
-/

namespace CryptoResearch.Nagao.Lemma4Outside

open CryptoResearch.Nagao.Lemma4Witness

/-- Nagao 2015/984 Lemma 4, outside (printed) placement, fake side from `F`. -/
def Lemma4Outside (n : Nat) (F : List Poly) : Prop :=
  ∀ d d', FirstFall n false F d → FirstFall n true F d' → d ≤ d'

/-- Outside placement with the fake side computed from `F ++ S_fe`. -/
def Lemma4OutsideFe (n : Nat) (F : List Poly) : Prop :=
  ∀ d d', FirstFall n false F d → FirstFall n true (F ++ fieldEqs n) d' → d ≤ d'

/-! ### Witness A: `F_2[X,Y]`, `F = {X^2 Y, X Y + X}`, no field equations -/

def FA : List Poly := [fA₁, fA₂]

/-- True fall at 3 without field equations: `g_1 = 1`, `g_2 = X`. -/
def gA_out : List Poly := [[[0, 0]], [[1, 0]]]

theorem A_out_true_fall3 : FallAt 2 false FA 3 :=
  ⟨gA_out, by unfold gens FA fA₁ fA₂ gA_out; decide +kernel,
    by unfold gens FA fA₁ fA₂ gA_out; decide +kernel⟩

theorem A_out_true_nofall1 : ¬ FallAt 2 false FA 1 :=
  noFall (by unfold NoFallDec gens FA fA₁ fA₂; decide +kernel)

theorem A_out_true_nofall2 : ¬ FallAt 2 false FA 2 :=
  noFall (by unfold NoFallDec gens FA fA₁ fA₂; decide +kernel)

theorem A_out_fake_fall2 : FallAt 2 true FA 2 :=
  ⟨gA_fake, by unfold gens FA fA₁ fA₂ gA_fake; decide +kernel,
    by unfold gens FA fA₁ fA₂ gA_fake; decide +kernel⟩

theorem A_out_fake_nofall1 : ¬ FallAt 2 true FA 1 :=
  noFall (by unfold NoFallDec gens FA fA₁ fA₂; decide +kernel)

theorem A_out_dF : FirstFall 2 false FA 3 := by
  refine ⟨A_out_true_fall3, fun D' h1 h2 => ?_⟩
  interval_cases D'
  · exact A_out_true_nofall1
  · exact A_out_true_nofall2

theorem A_out_dF' : FirstFall 2 true FA 2 := by
  refine ⟨A_out_fake_fall2, fun D' h1 h2 => ?_⟩
  interval_cases D'
  exact A_out_fake_nofall1

/-- The fake side of `FA ++ S_fe` is the inside system's fake side. -/
theorem A_out_dF'_fe : FirstFall 2 true (FA ++ fieldEqs 2) 2 := A_dF'

/-- **Lemma 4, printed placement, is false at witness A** (`d_F = 3 > 2 = d'_F`). -/
theorem lemma4_outside_false_A : ¬ Lemma4Outside 2 FA := fun h => by
  have := h 3 2 A_out_dF A_out_dF'
  omega

theorem lemma4_outside_fe_false_A : ¬ Lemma4OutsideFe 2 FA := fun h => by
  have := h 3 2 A_out_dF A_out_dF'_fe
  omega

/-! ### Witness B: `F_2[X_1,X_2,X_3]`, `F = {X_1X_2 + X_3, X_1X_3 + X_2}` -/

def FB : List Poly := [fB₁, fB₂]

/-- True fall at 3 without field equations: `g_1 = X_3`, `g_2 = X_2`. -/
def gB_out : List Poly := [[[0, 0, 1]], [[0, 1, 0]]]

theorem B_out_true_fall3 : FallAt 3 false FB 3 :=
  ⟨gB_out, by unfold gens FB fB₁ fB₂ gB_out; decide +kernel,
    by unfold gens FB fB₁ fB₂ gB_out; decide +kernel⟩

theorem B_out_true_nofall1 : ¬ FallAt 3 false FB 1 :=
  noFall (by unfold NoFallDec gens FB fB₁ fB₂; decide +kernel)

theorem B_out_true_nofall2 : ¬ FallAt 3 false FB 2 :=
  noFall (by unfold NoFallDec gens FB fB₁ fB₂; decide +kernel)

theorem B_out_fake_fall2 : FallAt 3 true FB 2 :=
  ⟨gB_fake, by unfold gens FB fB₁ fB₂ gB_fake; decide +kernel,
    by unfold gens FB fB₁ fB₂ gB_fake; decide +kernel⟩

theorem B_out_fake_nofall1 : ¬ FallAt 3 true FB 1 :=
  noFall (by unfold NoFallDec gens FB fB₁ fB₂; decide +kernel)

theorem B_out_dF : FirstFall 3 false FB 3 := by
  refine ⟨B_out_true_fall3, fun D' h1 h2 => ?_⟩
  interval_cases D'
  · exact B_out_true_nofall1
  · exact B_out_true_nofall2

theorem B_out_dF' : FirstFall 3 true FB 2 := by
  refine ⟨B_out_fake_fall2, fun D' h1 h2 => ?_⟩
  interval_cases D'
  exact B_out_fake_nofall1

theorem B_out_dF'_fe : FirstFall 3 true (FB ++ fieldEqs 3) 2 := B_dF'

/-- **Lemma 4, printed placement, is false at witness B** (`d_F = 3 > 2 = d'_F`). -/
theorem lemma4_outside_false_B : ¬ Lemma4Outside 3 FB := fun h => by
  have := h 3 2 B_out_dF B_out_dF'
  omega

theorem lemma4_outside_fe_false_B : ¬ Lemma4OutsideFe 3 FB := fun h => by
  have := h 3 2 B_out_dF B_out_dF'_fe
  omega

/-- The universal printed-placement statement over finite `F_2` systems is false,
for either reading of the fake side. -/
theorem lemma4_outside_false :
    ¬ (∀ (n : Nat) (F : List Poly), Lemma4Outside n F) ∧
    ¬ (∀ (n : Nat) (F : List Poly), Lemma4OutsideFe n F) :=
  ⟨fun h => lemma4_outside_false_A (h 2 FA), fun h => lemma4_outside_fe_false_A (h 2 FA)⟩

end CryptoResearch.Nagao.Lemma4Outside
