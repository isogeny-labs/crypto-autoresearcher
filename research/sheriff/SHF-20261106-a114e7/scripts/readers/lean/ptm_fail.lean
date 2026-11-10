/-
LNX proves-too-much controls: EVERY declaration below must FAIL to elaborate.
Expected: exactly 4 errors (one per declaration, tagged PTM-1..PTM-4), exit 1.
-/
import CryptoResearch.Quotient.TranslationDescent
import Mathlib.Data.ZMod.Basic

open CryptoResearch.Quotient

-- PTM-1: drop commutativity ([AddGroup] instead of [AddCommGroup]); producer's proof verbatim.
theorem ptm1_noncomm {E : Type} [AddGroup E] (S T : E) :
    (∀ P : E, -(P + S) + T = -(P + T + S)) ↔ (2 : ℕ) • T = 0 := by
  constructor
  · intro h
    have key : (2 : ℕ) • T = (-((0 : E) + S) + T) - -((0 : E) + T + S) := by abel
    rw [key, h 0, sub_self]
  · intro hT P
    have key : -(P + S) + T = -(P + T + S) + (2 : ℕ) • T := by abel
    rw [key, hT, add_zero]

-- PTM-2: 4-torsion instead of 2-torsion; producer's proof verbatim.
theorem ptm2_four {E : Type} [AddCommGroup E] (S T : E) :
    (∀ P : E, -(P + S) + T = -(P + T + S)) ↔ (4 : ℕ) • T = 0 := by
  constructor
  · intro h
    have key : (4 : ℕ) • T = (-((0 : E) + S) + T) - -((0 : E) + T + S) := by abel
    rw [key, h 0, sub_self]
  · intro hT P
    have key : -(P + S) + T = -(P + T + S) + (4 : ℕ) • T := by abel
    rw [key, hT, add_zero]

-- PTM-3: the theorem must not let an order-4 translation commute in ZMod 4.
example : ∀ P : ZMod 4, -(P + 1) + 1 = -(P + 1 + 1) :=
  (translation_commutes_iff_two_torsion (1 : ZMod 4) 1).mpr (by decide)

-- PTM-4: "descends for every T" (drop the torsion condition) must not be derivable.
theorem ptm4_all {E : Type} [AddCommGroup E] (S T : E) :
    ∀ P : E, -(P + S) + T = -(P + T + S) := by
  intro P
  exact (translation_commutes_iff_two_torsion S T).mpr (by simp) P
