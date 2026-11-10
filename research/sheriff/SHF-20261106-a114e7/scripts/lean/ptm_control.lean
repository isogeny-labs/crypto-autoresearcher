-- proves-too-much control: the same proof script on a wrong statement (3 • T) must FAIL
import Mathlib.Tactic.Abel
theorem wrong {E : Type} [AddCommGroup E] (S T : E) :
    (∀ P : E, -(P + S) + T = -(P + T + S)) ↔ (3 : ℕ) • T = 0 := by
  constructor
  · intro h
    have key : (3 : ℕ) • T = (-((0 : E) + S) + T) - -((0 : E) + T + S) := by abel
    rw [key, h 0, sub_self]
  · intro hT P
    have key : -(P + S) + T = -(P + T + S) + (3 : ℕ) • T := by abel
    rw [key, hT, add_zero]
