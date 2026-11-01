import Mathlib.FieldTheory.Finite.Basic

/-!
# Formal polynomials versus polynomial functions

Over a finite field, unrestricted formal polynomials are not determined by
their evaluations on the base field.  The first theorem gives the smallest
counterexample.  The second records the exact strict-degree hypothesis that
repairs the implication in the univariate setting.

No polynomial-commitment, evaluation-domain, quotient, or protocol semantics
are modeled here.
-/

namespace CryptoResearch.AttackCorpus.PolynomialFunctionAlias

open Polynomial

/-- In `(ZMod 2)[X]`, `X^2 - X` is a nonzero formal polynomial but induces
the zero function on the two-element field. -/
theorem nonzero_polynomial_zero_function :
    (X ^ 2 - X : (ZMod 2)[X]) ≠ 0 ∧
      ∀ x : ZMod 2, (X ^ 2 - X : (ZMod 2)[X]).eval x = 0 := by
  constructor
  · exact FiniteField.X_pow_card_sub_X_ne_zero (ZMod 2) (by norm_num)
  · intro x
    simpa using (FiniteField.pow_card x)

/-- Pointwise vanishing does determine a univariate formal polynomial when
its natural degree is strictly below the number of field elements. -/
theorem degree_bounded_zero_function_is_zero
    {F : Type*} [Field F] [Fintype F] (P : F[X])
    (hdegree : P.natDegree < Fintype.card F)
    (heval : ∀ x : F, P.eval x = 0) : P = 0 := by
  exact Polynomial.eq_zero_of_natDegree_lt_card_of_eval_eq_zero
    P Function.injective_id heval hdegree

end CryptoResearch.AttackCorpus.PolynomialFunctionAlias
