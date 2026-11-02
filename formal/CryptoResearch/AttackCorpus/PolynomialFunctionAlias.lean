import Mathlib.FieldTheory.Finite.Basic

/-!
# Formal polynomials versus polynomial functions

Over a finite field, unrestricted formal polynomials are not determined by
their evaluations on the base field.  The reusable first theorem records the
exact strict-degree repair; the audited target then bundles that repair with
the smallest counterexample.

No polynomial-commitment, evaluation-domain, quotient, or protocol semantics
are modeled here.
-/

namespace CryptoResearch.AttackCorpus.PolynomialFunctionAlias

open Polynomial

/-- Pointwise vanishing does determine a univariate formal polynomial when
its natural degree is strictly below the number of field elements. -/
theorem degree_bounded_zero_function_is_zero
    {F : Type*} [Field F] [Fintype F] (P : F[X])
    (hdegree : P.natDegree < Fintype.card F)
    (heval : ∀ x : F, P.eval x = 0) : P = 0 := by
  exact Polynomial.eq_zero_of_natDegree_lt_card_of_eval_eq_zero
    P Function.injective_id heval hdegree

/-- In `(ZMod 2)[X]`, `X^2 - X` is a nonzero formal polynomial but induces
the zero function on the two-element field.  The exact audited declaration
also contains the finite-field strict-degree repair, so checking only this
named target cannot silently omit the conditional theorem. -/
theorem nonzero_polynomial_zero_function :
    (X ^ 2 - X : (ZMod 2)[X]) ≠ 0 ∧
      (∀ x : ZMod 2, (X ^ 2 - X : (ZMod 2)[X]).eval x = 0) ∧
      ∀ (F : Type*) [Field F] [Fintype F] (P : F[X]),
        P.natDegree < Fintype.card F →
        (∀ x : F, P.eval x = 0) →
        P = 0 := by
  refine ⟨FiniteField.X_pow_card_sub_X_ne_zero (ZMod 2) (by norm_num), ?_, ?_⟩
  · intro x
    simpa using (FiniteField.pow_card x)
  · intro F _ _ P hdegree heval
    exact degree_bounded_zero_function_is_zero P hdegree heval

end CryptoResearch.AttackCorpus.PolynomialFunctionAlias
