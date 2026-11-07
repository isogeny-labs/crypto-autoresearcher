/-
Algebraic joints used by the A15 signed-pair construction.

Source: research/prime_field_a15_execution_20261107/pairbuild15.py
Target: formal/targets/prime-field-a15-batched-pairs.yaml

This file proves equalities in a field. It does not certify the NumPy uint64
implementation, the curve-membership guards, or an end-to-end experiment.
-/
import Mathlib.Algebra.Field.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

set_option autoImplicit false

namespace CryptoResearch.PrimeField.BatchedPairs

variable {F : Type*} [Field F]

/-- One parent inverse recovers the left child's inverse in a product tree. -/
theorem inverse_parent_left (x y : F) (hx : x ≠ 0) (hy : y ≠ 0) :
    (x * y)⁻¹ * y = x⁻¹ := by
  field_simp [hx, hy]

/-- One parent inverse recovers the right child's inverse in a product tree. -/
theorem inverse_parent_right (x y : F) (hx : x ≠ 0) (hy : y ≠ 0) :
    (x * y)⁻¹ * x = y⁻¹ := by
  field_simp [hx, hy]

/-- The slope expression used by the two A15 pair formulas. -/
def slope (xj yj xk yk : F) : F :=
  (yk - yj) * (xk - xj)⁻¹

/-- The candidate x coordinate of an affine pair sum. -/
def pairX (xj yj xk yk : F) : F :=
  slope xj yj xk yk * slope xj yj xk yk - (xj + xk)

/-- The candidate y coordinate of an affine pair sum. -/
def pairY (xj yj xk yk : F) : F :=
  slope xj yj xk yk * (xj - pairX xj yj xk yk) - yj

/-- Negating both input y coordinates negates the shared slope. -/
theorem slope_neg_both (xj yj xk yk : F) :
    slope xj (-yj) xk (-yk) = -slope xj yj xk yk := by
  unfold slope
  ring

/-- The two-input sign reversal keeps the pair x coordinate. -/
theorem pairX_neg_both (xj yj xk yk : F) :
    pairX xj (-yj) xk (-yk) = pairX xj yj xk yk := by
  simp only [pairX, slope_neg_both]
  ring

/-- The two-input sign reversal negates the pair y coordinate. -/
theorem pairY_neg_both (xj yj xk yk : F) :
    pairY xj (-yj) xk (-yk) = -pairY xj yj xk yk := by
  simp only [pairY, slope_neg_both, pairX_neg_both]
  ring

/-- The A15 `(-,+)` output is the negation of its `(+,-)` output. -/
theorem minus_plus_from_plus_minus (xj yj xk yk : F) :
    pairX xj (-yj) xk yk = pairX xj yj xk (-yk) ∧
      pairY xj (-yj) xk yk = -pairY xj yj xk (-yk) := by
  simpa using (And.intro
    (pairX_neg_both xj yj xk (-yk))
    (pairY_neg_both xj yj xk (-yk)))

/-- The exact algebraic equalities reused by the A15 product-tree step and
four-sign pair formulas. The field model is separate from the uint64 arrays. -/
theorem a15_algebraic_joints (x y xj yj xk yk : F)
    (hx : x ≠ 0) (hy : y ≠ 0) :
    (x * y)⁻¹ * y = x⁻¹ ∧
      (x * y)⁻¹ * x = y⁻¹ ∧
      pairX xj (-yj) xk (-yk) = pairX xj yj xk yk ∧
      pairY xj (-yj) xk (-yk) = -pairY xj yj xk yk ∧
      (pairX xj (-yj) xk yk = pairX xj yj xk (-yk) ∧
        pairY xj (-yj) xk yk = -pairY xj yj xk (-yk)) := by
  exact ⟨inverse_parent_left x y hx hy, inverse_parent_right x y hx hy,
    pairX_neg_both xj yj xk yk, pairY_neg_both xj yj xk yk,
    minus_plus_from_plus_minus xj yj xk yk⟩

end CryptoResearch.PrimeField.BatchedPairs
