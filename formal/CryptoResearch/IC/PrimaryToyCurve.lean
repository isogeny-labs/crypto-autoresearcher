import Init

/-!
Exact encoded arithmetic checks for the nine archived primary IC toy runs.
The three workload points are shared by the three factor-base candidates.
Field elements are polynomial-basis 13-bit masks. `modulus` is the mask for
X^13 + X^5 + X^2 + X + 1. The curve is y^2 + x*y = x^3 + 1.

This module proves finite equalities about the definitions below, checked by
Lean's kernel via `decide`. It does not prove that archived wall times were
measured as stated, that a historical run executed, or that the generic
formula is a group law over every represented element.
-/

set_option autoImplicit false

namespace CryptoResearch.IC.PrimaryToyCurve

/-- Archived polynomial-basis modulus encoding: 8231. -/
def modulus : Nat := 2^13 + 2^5 + 2^2 + 2 + 1
/-- Thirteen shift/XOR multiplication steps, with top-bit reduction. -/
def mul : Nat → Nat → Nat → Nat
  | 0, _, _ => 0
  | n + 1, a, b =>
    let shifted := 2*a
    let reduced := if shifted >= 2^13 then Nat.xor shifted modulus else shifted
    Nat.xor (if b % 2 == 1 then a else 0) (mul n reduced (b / 2))

/-- Multiplication on the archived 13-bit encodings. -/
def fm (a b : Nat) : Nat := mul 13 a b
/-- Binary powering, used only for the fixed inversion exponent. -/
def power : Nat → Nat → Nat → Nat
  | 0, _, _ => 1
  | n + 1, a, e =>
    let tail := power n (fm a a) (e / 2)
    if e % 2 == 1 then fm a tail else tail
/-- The candidate inverse is `a^(2^13-2)` in the encoded arithmetic. -/
def inv (a : Nat) : Nat := power 13 a (2^13 - 2)

abbrev Point := Option (Nat × Nat)
/-- Standard affine binary-curve formulas for `a2=0`, with `none` as infinity. -/
def add : Point → Point → Point
  | none, q => q
  | p, none => p
  | some (x1, y1), some (x2, y2) =>
    if x1 == x2 && Nat.xor y1 y2 == x1 then none
    else if x1 == x2 then
      if x1 == 0 then none else
      let slope := Nat.xor x1 (fm y1 (inv x1))
      let x3 := Nat.xor (fm slope slope) slope
      let y3 := Nat.xor (fm x1 x1) (fm (Nat.xor slope 1) x3)
      some (x3, y3)
    else
      let slope := fm (Nat.xor y1 y2) (inv (Nat.xor x1 x2))
      let x3 := Nat.xor (Nat.xor (Nat.xor (fm slope slope) slope) x1) x2
      let y3 := Nat.xor (Nat.xor (fm slope (Nat.xor x1 x3)) x3) y1
      some (x3, y3)

/-- Binary double-and-add with twelve bits of scalar fuel. -/
def scalarLoop : Nat → Nat → Point → Point
  | 0, _, _ => none
  | n + 1, k, p =>
    if k == 0 then none else
    let tail := scalarLoop n (k / 2) (add p p)
    if k % 2 == 1 then add p tail else tail

def scale (k : Nat) (p : Point) : Point := scalarLoop 12 k p
def generator : Point := some (2995, 1571)

/-- The archived curve equation on an affine encoded point. -/
def onCurve : Point → Bool
  | none => true
  | some (x, y) =>
    Nat.xor (fm y y) (fm x y) == Nat.xor (fm (fm x x) x) 1

set_option maxRecDepth 8192
set_option maxHeartbeats 0

/-- The recorded generator and target encodings satisfy the curve equation. -/
theorem archived_points_on_curve :
    onCurve generator = true ∧
    onCurve (some (2659, 1282)) = true ∧
    onCurve (some (6749, 6034)) = true ∧
    onCurve (some (4412, 6211)) = true := by decide

/-- The archived generator has encoded order dividing 2003. -/
theorem generator_2003_to_infinity : scale 2003 generator = none := by decide

/-- The three frozen workload targets are the recorded scalar multiples. -/
theorem archived_primary_targets :
    scale 1046 generator = some (2659, 1282) ∧
    scale 606 generator = some (6749, 6034) ∧
    scale 861 generator = some (4412, 6211) := by decide

/-- Nearby scalars and an altered coordinate are negative controls. -/
theorem nearby_controls_rejected :
    scale 1045 generator ≠ some (2659, 1282) ∧
    scale 605 generator ≠ some (6749, 6034) ∧
    scale 860 generator ≠ some (4412, 6211) ∧
    onCurve (some (2659, 1283)) = false := by decide

/-- Single target declaration for the exact finite certificate and controls. -/
theorem primary_archive_certificate :
    modulus = 8231 ∧
    onCurve generator = true ∧
    scale 2003 generator = none ∧
    scale 1046 generator = some (2659, 1282) ∧
    scale 606 generator = some (6749, 6034) ∧
    scale 861 generator = some (4412, 6211) ∧
    scale 1045 generator ≠ some (2659, 1282) ∧
    scale 605 generator ≠ some (6749, 6034) ∧
    scale 860 generator ≠ some (4412, 6211) ∧
    onCurve (some (2659, 1283)) = false := by
  exact ⟨by decide, archived_points_on_curve.1,
    generator_2003_to_infinity,
    archived_primary_targets.1, archived_primary_targets.2.1,
    archived_primary_targets.2.2,
    nearby_controls_rejected.1, nearby_controls_rejected.2.1,
    nearby_controls_rejected.2.2.1, nearby_controls_rejected.2.2.2⟩

end CryptoResearch.IC.PrimaryToyCurve
