import Mathlib.LinearAlgebra.Dual.Lemmas
import Mathlib.LinearAlgebra.Pi
import Mathlib.Algebra.MvPolynomial.Basic

namespace CryptoResearch.FallDegree
open scoped BigOperators
open MvPolynomial
variable {ι τ k : Type*} [Field k] [Fintype ι] [Fintype τ]

/-- Linear inconsistency gives a scalar certificate. This asserts no
Boolean-to-field transfer in odd characteristic. -/
theorem affine_inconsistency_certificate (A : ι → τ → k) (c : ι → k)
    (hno : ¬ ∃ t : τ → k, ∀ i, c i + ∑ j, A i j * t j = 0) :
    ∃ w : ι → k, (∑ i, w i * c i) = 1 ∧
      ∀ j, (∑ i, w i * A i j) = 0 := by
  classical
  let col : τ → (ι → k) := fun j i => A i j
  let U := Submodule.span k (Set.range col)
  have hc : c ∉ U := by
    intro hc
    obtain ⟨t, ht⟩ := (Submodule.mem_span_range_iff_exists_fun k).mp hc
    apply hno
    refine ⟨fun j => -t j, fun i => ?_⟩
    have hi := congrFun ht i
    simp only [Finset.sum_apply, Pi.smul_apply, smul_eq_mul, col] at hi
    have hsum : (∑ j, A i j * t j) = c i := by
      simpa only [mul_comm] using hi
    simp_rw [mul_neg, Finset.sum_neg_distrib]
    rw [hsum]
    exact add_neg_cancel _
  obtain ⟨φ, hφc, hφU⟩ := U.exists_dual_map_eq_bot_of_notMem hc inferInstance
  have hz : ∀ j, φ (col j) = 0 := by
    intro j
    have hm : φ (col j) ∈ U.map φ := Submodule.mem_map.mpr
      ⟨col j, Submodule.subset_span ⟨j,rfl⟩,rfl⟩
    rw [hφU, Submodule.mem_bot] at hm
    exact hm
  let v : ι → k := fun i => φ ((Pi.basisFun k ι) i)
  have hrepr : ∀ x : ι → k, (∑ i, x i * v i) = φ x := by
    intro x
    have h := congrArg φ ((Pi.basisFun k ι).sum_repr x)
    simpa [v] using h
  refine ⟨fun i => (φ c)⁻¹ * v i, ?_, ?_⟩
  · simp_rw [mul_assoc, ← Finset.mul_sum]
    have hcv : (∑ i, v i * c i) = φ c := by
      simpa only [mul_comm] using hrepr c
    rw [hcv, inv_mul_cancel₀ hφc]
  · intro j
    simp_rw [mul_assoc, ← Finset.mul_sum]
    have h := hrepr (col j)
    simp only [col, mul_comm (A _ j)] at h
    rw [h, hz, mul_zero]

noncomputable def affinePolynomial (A : ι → τ → k) (c : ι → k) (i : ι) :
    MvPolynomial τ k := C (c i) + ∑ j, C (A i j) * X j

/-- A constant-coefficient polynomial refutation of any inconsistent affine
system over its coefficient field. -/
theorem affine_polynomial_refutation (A : ι → τ → k) (c : ι → k)
    (hno : ¬ ∃ t : τ → k, ∀ i, c i + ∑ j, A i j * t j = 0) :
    ∃ w : ι → k, (∑ i, w i • affinePolynomial A c i) = 1 := by
  obtain ⟨w, hwc, hwA⟩ := affine_inconsistency_certificate A c hno
  refine ⟨w, ?_⟩
  have hexp : (∑ i, w i • affinePolynomial A c i) =
      C (∑ i, w i * c i) + ∑ j, C (∑ i, w i * A i j) * X j := by
    simp_rw [affinePolynomial, smul_eq_C_mul, mul_add, Finset.mul_sum,
      ← mul_assoc, ← map_mul]
    rw [Finset.sum_add_distrib]
    congr 1
    · simp only [map_sum]
    · rw [Finset.sum_comm]
      simp only [map_sum, Finset.sum_mul]
  rw [hexp, hwc]
  simp only [hwA, map_zero, zero_mul, Finset.sum_const_zero, add_zero, map_one]

end CryptoResearch.FallDegree
#print axioms CryptoResearch.FallDegree.affine_inconsistency_certificate
#print axioms CryptoResearch.FallDegree.affine_polynomial_refutation
