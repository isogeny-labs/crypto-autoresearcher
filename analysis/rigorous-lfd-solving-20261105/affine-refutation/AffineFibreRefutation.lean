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


/-- The actual affine polynomial subspace, over arbitrarily many variables. -/
noncomputable def affinePolynomialSpace (σ k : Type*) [Field k] :
    Submodule k (MvPolynomial σ k) :=
  Submodule.span k ({1} ∪ Set.range fun j : σ => (X j : MvPolynomial σ k))

/-- Inconsistency of affine polynomials implies that one lies in their
constant-coefficient span. The hypothesis concerns field solutions. -/
theorem affine_span_refutation {σ : Type*} (p : ι → MvPolynomial σ k)
    (haff : ∀ i, p i ∈ affinePolynomialSpace σ k)
    (hno : ¬ ∃ t : σ → k, ∀ i, eval t (p i) = 0) :
    ∃ w : ι → k, (∑ i, w i • p i) = 1 := by
  classical
  let U := Submodule.span k (Set.range p)
  have h1 : (1 : MvPolynomial σ k) ∈ U := by
    by_contra h1
    obtain ⟨φ, hφ1, hφU⟩ := U.exists_dual_map_eq_bot_of_notMem h1 inferInstance
    let ψ : Module.Dual k (MvPolynomial σ k) := (φ 1)⁻¹ • φ
    have hψ1 : ψ 1 = 1 := by
      simp only [ψ, LinearMap.smul_apply, smul_eq_mul, inv_mul_cancel₀ hφ1]
    let t : σ → k := fun j => ψ (X j)
    have heval : ∀ q ∈ affinePolynomialSpace σ k, ψ q = eval t q := by
      intro q hq
      induction hq using Submodule.span_induction with
      | mem q hq =>
        rcases hq with hq | ⟨j,rfl⟩
        · have he : q = 1 := Set.mem_singleton_iff.mp hq
          rw [he, hψ1, map_one]
        · simp only [eval_X, t]
      | zero => simp
      | add q r _ _ hq hr => simp only [map_add, hq, hr]
      | smul c q _ hq => simp only [map_smul, smul_eval, hq, smul_eq_mul]
    apply hno
    refine ⟨t, fun i => ?_⟩
    rw [← heval (p i) (haff i)]
    have hm : φ (p i) ∈ U.map φ := Submodule.mem_map.mpr
      ⟨p i, Submodule.subset_span ⟨i,rfl⟩,rfl⟩
    rw [hφU, Submodule.mem_bot] at hm
    simp only [ψ, LinearMap.smul_apply, hm, smul_zero]
  exact (Submodule.mem_span_range_iff_exists_fun k).mp h1

end CryptoResearch.FallDegree
#print axioms CryptoResearch.FallDegree.affine_inconsistency_certificate
#print axioms CryptoResearch.FallDegree.affine_polynomial_refutation
#print axioms CryptoResearch.FallDegree.affine_span_refutation
