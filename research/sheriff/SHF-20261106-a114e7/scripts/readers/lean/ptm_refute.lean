/-
LNX: the statements attempted in ptm_fail.lean are FALSE (kernel-checked
counterexamples). This file must elaborate with no error.
-/
import Mathlib.Data.ZMod.Basic
import Mathlib.GroupTheory.Perm.Basic

-- PTM-1 is false: in Additive (Perm (Fin 3)), T = swap 0 1 has T + T = 0 but does not
-- commute with iota_S for S = 0 (take P = swap 0 2).
example : ¬ (∀ (S T : Additive (Equiv.Perm (Fin 3))),
    (∀ P, -(P + S) + T = -(P + T + S)) ↔ (2 : ℕ) • T = 0) := by
  intro h
  have h2 := (h 0 (Additive.ofMul (Equiv.swap 0 1))).mpr (by
    rw [two_nsmul]; decide)
  have := h2 (Additive.ofMul (Equiv.swap 0 2))
  revert this; decide

-- PTM-2 is false: in ZMod 4, T = 1 has 4 • T = 0 but does not commute.
example : ¬ (∀ (S T : ZMod 4), (∀ P, -(P + S) + T = -(P + T + S)) ↔ (4 : ℕ) • T = 0) := by
  intro h
  have := (h 0 1).mpr (by decide)
  revert this; decide

-- PTM-3/4: the order-4 translation does not commute.
example : ¬ ∀ P : ZMod 4, -(P + 1) + 1 = -(P + 1 + 1) := by decide
