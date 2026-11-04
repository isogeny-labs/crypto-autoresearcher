import Mathlib

/-!
# Cubic evaluation rank is a premise, not a consequence of distinctness

Ten distinct affine representatives need not impose ten independent linear
conditions on the ten coefficients of a homogeneous ternary cubic.  The
points `(i, 0, 1)` all lie on the reducible cubic `Y * Z^2`, so their square
evaluation matrix has a nontrivial kernel.

The repair below keeps full rank explicit: a nonzero determinant makes the
evaluation map injective.  This is a finite linear-algebra boundary only.  It
does not construct a nonsingular cubic or make a claim about the rank-tested
`r <= 9` point families in the JKSST xedni algorithm.
-/

namespace CryptoResearch.AttackCorpus.CubicEvalRank

open scoped BigOperators Matrix

/-- A projective-coordinate representative.  Quotienting by coordinate
scaling is deliberately outside this finite evaluation target. -/
structure Point3 (F : Type*) where
  x : F
  y : F
  z : F

/-- Coefficients in the standard homogeneous-cubic monomial basis. -/
abbrev Coefficients (F : Type*) := Fin 10 → F

variable {F : Type*} [CommSemiring F]

/-- The monomial order is
`X^3, X^2*Y, X^2*Z, X*Y^2, X*Y*Z, X*Z^2,
Y^3, Y^2*Z, Y*Z^2, Z^3`. -/
def cubicMonomials (p : Point3 F) : Fin 10 → F :=
  ![p.x ^ 3,
    p.x ^ 2 * p.y,
    p.x ^ 2 * p.z,
    p.x * p.y ^ 2,
    p.x * p.y * p.z,
    p.x * p.z ^ 2,
    p.y ^ 3,
    p.y ^ 2 * p.z,
    p.y * p.z ^ 2,
    p.z ^ 3]

/-- Evaluation of a coefficient vector at one coordinate triple. -/
def cubicValue (c : Coefficients F) (p : Point3 F) : F :=
  ∑ j, cubicMonomials p j * c j

/-- The square matrix whose rows evaluate the ten standard monomials. -/
def evaluationMatrix (points : Fin 10 → Point3 F) : Matrix (Fin 10) (Fin 10) F :=
  fun i j ↦ cubicMonomials (points i) j

@[simp] theorem evaluationMatrix_mulVec_apply
    (points : Fin 10 → Point3 F) (c : Coefficients F) (i : Fin 10) :
    (evaluationMatrix points *ᵥ c) i = cubicValue c (points i) := by
  rfl

/-- Ten affine representatives on the line `Y = 0`. -/
def collinearPoints (i : Fin 10) : Point3 ℚ :=
  ⟨(i.val : ℚ), 0, 1⟩

/-- The coefficient vector of the homogeneous cubic `Y * Z^2`. -/
def lineCubic : Coefficients ℚ :=
  ![0, 0, 0, 0, 0, 0, 0, 0, 1, 0]

theorem collinearPoints_injective : Function.Injective collinearPoints := by
  intro i j hij
  apply Fin.ext
  have hx : (i.val : ℚ) = (j.val : ℚ) := congrArg Point3.x hij
  exact_mod_cast hx

theorem lineCubic_ne_zero : lineCubic ≠ 0 := by
  intro hzero
  have h8 := congrFun hzero (8 : Fin 10)
  norm_num [lineCubic] at h8

@[simp] theorem lineCubic_value (p : Point3 ℚ) :
    cubicValue lineCubic p = p.y * p.z ^ 2 := by
  simp [cubicValue, cubicMonomials, lineCubic, Fin.sum_univ_succ]

theorem lineCubic_vanishes :
    ∀ i : Fin 10, cubicValue lineCubic (collinearPoints i) = 0 := by
  intro i
  simp [collinearPoints]

theorem lineCubic_in_kernel :
    evaluationMatrix collinearPoints *ᵥ lineCubic = 0 := by
  funext i
  simpa using lineCubic_vanishes i

/-- Nonzero determinant is the exact square full-rank repair. -/
theorem coefficients_eq_zero_of_det_ne_zero
    {K : Type*} [Field K]
    (points : Fin 10 → Point3 K) (c : Coefficients K)
    (hdet : (evaluationMatrix points).det ≠ 0)
    (hvanish : ∀ i, cubicValue c (points i) = 0) :
    c = 0 := by
  apply Matrix.eq_zero_of_mulVec_eq_zero hdet
  funext i
  simpa using hvanish i

theorem collinear_evaluation_det_zero :
    (evaluationMatrix collinearPoints).det = 0 := by
  by_contra hdet
  exact lineCubic_ne_zero
    (coefficients_eq_zero_of_det_ne_zero collinearPoints lineCubic hdet
      lineCubic_vanishes)

/-- The exact audited declaration bundles the concrete rank countermodel and
the determinant-nonzero repair.  Distinctness alone does not supply the repair
premise. -/
theorem collinear_kernel_and_injective_repair :
    Function.Injective collinearPoints ∧
      lineCubic ≠ 0 ∧
      (∀ i : Fin 10, cubicValue lineCubic (collinearPoints i) = 0) ∧
      (∃ c : Coefficients ℚ,
        c ≠ 0 ∧ evaluationMatrix collinearPoints *ᵥ c = 0) ∧
      (evaluationMatrix collinearPoints).det = 0 ∧
      ∀ (K : Type*) [Field K]
        (points : Fin 10 → Point3 K) (c : Coefficients K),
        (evaluationMatrix points).det ≠ 0 →
        (∀ i, cubicValue c (points i) = 0) →
        c = 0 := by
  refine ⟨collinearPoints_injective, lineCubic_ne_zero,
    lineCubic_vanishes, ?_, collinear_evaluation_det_zero, ?_⟩
  · exact ⟨lineCubic, lineCubic_ne_zero, lineCubic_in_kernel⟩
  · intro K _ points c hdet hvanish
    exact coefficients_eq_zero_of_det_ne_zero points c hdet hvanish

end CryptoResearch.AttackCorpus.CubicEvalRank
