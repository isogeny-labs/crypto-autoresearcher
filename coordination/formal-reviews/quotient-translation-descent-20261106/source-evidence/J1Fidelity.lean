/- TASK-20261106-6d4fa6 J1/J2 control file (source reviewer). Not part of the
   formal workspace; elaborated with `lake env lean` against the built module. -/
import CryptoResearch.Quotient.TranslationDescent
import Mathlib.Data.ZMod.Basic
import Mathlib.AlgebraicGeometry.EllipticCurve.Affine.Point
import Mathlib.FieldTheory.IsAlgClosed.AlgebraicClosure

open CryptoResearch.Quotient

-- (1) Elaborated type, with universes and implicit binders.
set_option pp.universes true in
set_option pp.explicit true in
#check @translation_commutes_iff_two_torsion

set_option pp.universes true in
#print translation_commutes_iff_two_torsion

-- (2) Axioms of the exact named declaration.
#print axioms translation_commutes_iff_two_torsion

-- (3) Reviewer's own reading of the target claim, written from the yaml text
--     (lines 19-23), with "2 T" read three ways.
def ClaimLHS {E : Type*} [AddCommGroup E] (S T : E) : Prop :=
  ∀ P : E, -(P + S) + T = -(P + T + S)

-- 2 T as T + T, as ℤ-smul and as ℕ-smul agree in any additive group:
example {E : Type*} [AddCommGroup E] (T : E) :
    ((2 : ℕ) • T = 0 ↔ T + T = 0) ∧ ((2 : ℤ) • T = 0 ↔ T + T = 0) :=
  ⟨by rw [two_nsmul], by rw [two_zsmul]⟩

-- The Lean statement is literally the claim with 2 T := T + T (forward/backward):
example {E : Type*} [AddCommGroup E] (S T : E) : ClaimLHS S T ↔ T + T = 0 := by
  rw [← two_nsmul]; exact translation_commutes_iff_two_torsion S T
example {E : Type*} [AddCommGroup E] (S T : E) : ClaimLHS S T ↔ (2 : ℤ) • T = 0 := by
  rw [two_zsmul, ← two_nsmul]; exact translation_commutes_iff_two_torsion S T

-- (4) Quantifier placement variants (is ∀ P placement load-bearing?).
--   ∃ P on the left side:
example {E : Type*} [AddCommGroup E] (S T : E) :
    (∃ P : E, -(P + S) + T = -(P + T + S)) ↔ (2 : ℕ) • T = 0 := by
  constructor
  · rintro ⟨P, hP⟩
    have key : (2 : ℕ) • T = (-(P + S) + T) - -(P + T + S) := by abel
    rw [key, hP, sub_self]
  · intro h; exact ⟨0, (translation_commutes_iff_two_torsion S T).2 h 0⟩
--   ∀ P pulled outside the iff:
example {E : Type*} [AddCommGroup E] (S T : E) :
    (∀ P : E, (-(P + S) + T = -(P + T + S) ↔ (2 : ℕ) • T = 0)) := by
  intro P
  have key : -(P + S) + T = -(P + T + S) + (2 : ℕ) • T := by abel
  rw [key]; constructor
  · intro h; simpa using h
  · intro h; rw [h, add_zero]

-- (5) Instantiation on the note's setting: Mathlib's elliptic-curve point group
--     over an arbitrary field. Mathlib's `AddCommGroup W.Point` instance carries
--     `[DecidableEq F]` (a computability device of the instance, always available
--     classically; it is not a binder of the theorem under review).
example {F : Type*} [Field F] [DecidableEq F] (W : WeierstrassCurve.Affine F) (S T : W.Point) :
    (∀ P : W.Point, -(P + S) + T = -(P + T + S)) ↔ (2 : ℕ) • T = 0 :=
  translation_commutes_iff_two_torsion S T

-- ... and with the classical instance only, over an algebraic closure (E(k̄)),
--     with the characteristic left free (the theorem needs no char k ≠ 2).
open Classical in
example {k : Type} [Field k] (W : WeierstrassCurve.Affine (AlgebraicClosure k))
    (S T : W.Point) :
    (∀ P : W.Point, -(P + S) + T = -(P + T + S)) ↔ (2 : ℕ) • T = 0 :=
  translation_commutes_iff_two_torsion S T

-- (6) Kernel `decide` on small groups, every S and T: claim (T + T reading)
--     vs the Lean proposition, and the claim's truth itself.
def agreeAll (E : Type) [AddCommGroup E] [Fintype E] [DecidableEq E] : Prop :=
  ∀ S T : E, ((∀ P : E, -(P + S) + T = -(P + T + S)) ↔ T + T = 0) ∧
             ((T + T = 0) ↔ (2 : ℕ) • T = 0)

instance (E : Type) [AddCommGroup E] [Fintype E] [DecidableEq E] :
    Decidable (agreeAll E) := by unfold agreeAll; infer_instance

theorem agree_ZMod1 : agreeAll (ZMod 1) := by decide
theorem agree_ZMod2 : agreeAll (ZMod 2) := by decide
theorem agree_ZMod4 : agreeAll (ZMod 4) := by decide
theorem agree_ZMod2xZMod4 : agreeAll (ZMod 2 × ZMod 4) := by decide

-- Degenerate cases named by the gate: trivial group (ZMod 1), exponent-2
-- groups (ZMod 2, ZMod 2 × ZMod 2: every T is 2-torsion, so the LHS holds for
-- every S, T), and S = 0.
theorem exp2_all_commute : ∀ S T : ZMod 2 × ZMod 2,
    ∀ P : ZMod 2 × ZMod 2, -(P + S) + T = -(P + T + S) := by decide
theorem S_zero_ZMod4 : ∀ T : ZMod 4,
    ((∀ P : ZMod 4, -(P + 0) + T = -(P + T + 0)) ↔ T + T = 0) := by decide

-- (7) Instrument discrimination control: the same `decide` harness REJECTS a
--     false variant (4 T in place of 2 T) on ZMod 4. Expected: this proves the
--     negation, i.e. the harness can see a disagreement.
theorem harness_sees_mutant :
    ¬ (∀ S T : ZMod 4, ((∀ P : ZMod 4, -(P + S) + T = -(P + T + S)) ↔ (4 : ℕ) • T = 0)) := by
  decide

#print axioms agree_ZMod2xZMod4
#print axioms harness_sees_mutant
