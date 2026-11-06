/-
TASK-20261106-bb6ab4, blind re-derivation (J4). Written from the handoff
statement alone. NOT ELABORATED: no Lean toolchain in this session (installing
elan was refused by the session's permission layer) => infrastructure_error for
the formal part. Lemma names are recalled from Mathlib, not checked here.
Intended to compile standalone against Mathlib; imports nothing from this repo.
-/
import Mathlib

namespace BlindJ4

/-- Main statement, `∀ P` inside the iff. Commutativity enters through `abel`
(equivalently `neg_add`, `add_comm`). -/
theorem main {E : Type*} [AddCommGroup E] (S T : E) :
    (∀ P : E, -(P + S) + T = -(P + T + S)) ↔ T + T = 0 := by
  constructor
  · intro h
    have h0 := h 0
    -- -(0+S)+T = -(0+T+S)  ⇒  -S + T = -T - S  ⇒  T + T = 0
    have : T + T = (-(0 + S) + T) - (-(0 + T + S)) := by abel
    rw [this, h0, sub_self]
  · intro h P
    -- -(P+S)+T - (-(P+T+S)) = T + T
    have : -(P + S) + T - (-(P + T + S)) = T + T := by abel
    exact sub_eq_zero.mp (this.trans h)

/-- `∀ P` outside the iff, and `∃ P`, are equivalent here. -/
theorem pointwise {E : Type*} [AddCommGroup E] (S T P : E) :
    (-(P + S) + T = -(P + T + S)) ↔ T + T = 0 := by
  have key : -(P + S) + T - (-(P + T + S)) = T + T := by abel
  rw [← sub_eq_zero, key]

theorem exists_form {E : Type*} [AddCommGroup E] (S T : E) :
    (∃ P : E, -(P + S) + T = -(P + T + S)) ↔ T + T = 0 :=
  ⟨fun ⟨P, h⟩ => (pointwise S T P).mp h, fun h => ⟨0, (pointwise S T 0).mpr h⟩⟩

/-- General (possibly non-commutative) group: the exact condition is
`T * T = 1 ∧ T` central. -/
theorem group_version {G : Type*} [Group G] (S T : G) :
    (∀ P : G, (P * S)⁻¹ * T = (P * T * S)⁻¹) ↔ (T * T = 1 ∧ ∀ Q : G, Q * T = T * Q) := by
  have red : ∀ P : G, ((P * S)⁻¹ * T = (P * T * S)⁻¹ ↔ P⁻¹ * T = T⁻¹ * P⁻¹) := by
    intro P
    simp only [mul_inv_rev, mul_assoc, mul_right_inj]
  constructor
  · intro h
    have h1 : T = T⁻¹ := by simpa using (red 1).mp (h 1)
    have hT : T * T = 1 := by
      calc T * T = T * T⁻¹ := by rw [← h1]
        _ = 1 := mul_inv_cancel T
    refine ⟨hT, fun Q => ?_⟩
    have := (red Q⁻¹).mp (h Q⁻¹)
    rw [inv_inv, ← h1] at this
    exact this
  · rintro ⟨hT, hc⟩ P
    rw [red]
    have h1 : T⁻¹ = T := inv_eq_of_mul_eq_one_right hT
    rw [h1]; exact hc P⁻¹

/-! Controls, decided by the kernel on finite groups (Multiplicative for S₃). -/

-- (b) conclusion `T = 0`: fails in ZMod 2 at S = 0, T = 1.
example : ¬ ((∀ P : ZMod 2, -(P + 0) + 1 = -(P + 1 + 0)) ↔ (1 : ZMod 2) = 0) := by decide
-- (c) conclusion `S + S = 0`: fails in ZMod 3 at S = 1, T = 0.
example : ¬ ((∀ P : ZMod 3, -(P + 1) + 0 = -(P + 0 + 1)) ↔ (1 : ZMod 3) + 1 = 0) := by decide
-- (d) iota_S replaced by tau_S: fails in ZMod 3 at S = 0, T = 1.
example : ¬ ((∀ P : ZMod 3, P + 0 + 1 = P + 1 + 0) ↔ (1 : ZMod 3) + 1 = 0) := by decide
-- (e) conclusion `4 • T = 0`: fails in ZMod 4 at S = 0, T = 1.
example : ¬ ((∀ P : ZMod 4, -(P + 0) + 1 = -(P + 1 + 0)) ↔ (4 : ℕ) • (1 : ZMod 4) = 0) := by decide
-- (a) S₃, T = swap 0 1, S = 1: T*T = 1 but the commutation fails.
example : ¬ ((∀ P : Equiv.Perm (Fin 3),
    (P * 1)⁻¹ * Equiv.swap 0 1 = (P * Equiv.swap 0 1 * 1)⁻¹) ↔
    Equiv.swap (0 : Fin 3) 1 * Equiv.swap 0 1 = 1) := by decide

end BlindJ4
