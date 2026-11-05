import CryptoResearch.FallDegree.LastFall
import Mathlib.Algebra.BigOperators.Ring.Finset

/-!
Source: analysis/boolean-fall-certificates-20261104/THEORY.md, sections 2--3.
Ordinary polynomial closure certificates and final localization assembly.
No Boolean-normal-form transfer or growing-family lower bound is assumed.
-/
namespace CryptoResearch.FallDegree
open MvPolynomial
open scoped BigOperators
variable {σ k : Type*} [Field k]

theorem V_le_closed_space {F : Set (MvPolynomial σ k)} {d : ℕ}
    (U : Submodule k (MvPolynomial σ k))
    (hinput : ∀ f ∈ F, f.totalDegree ≤ d → f ∈ U)
    (hmul : ∀ f ∈ U, ∀ g : MvPolynomial σ k,
      f.totalDegree + g.totalDegree ≤ d → f * g ∈ U) :
    V F d ≤ U := sInf_le ⟨hinput, hmul⟩

/-- Every bounded derivation is an actual ideal consequence. -/
theorem V_le_ideal_span (F : Set (MvPolynomial σ k)) (d : ℕ) :
    V F d ≤ (Ideal.span F).restrictScalars k := by
  apply V_le_closed_space
  · intro f hf _
    exact Ideal.subset_span hf
  · intro f hf g _
    exact (Ideal.span F).mul_mem_right g hf

/-- Equality needs primal inclusion as well as a closed superspace. -/
theorem exact_closure_of_two_sides {F : Set (MvPolynomial σ k)} {d : ℕ}
    (U : Submodule k (MvPolynomial σ k))
    (hinput : ∀ f ∈ F, f.totalDegree ≤ d → f ∈ U)
    (hmul : ∀ f ∈ U, ∀ g : MvPolynomial σ k,
      f.totalDegree + g.totalDegree ≤ d → f * g ∈ U)
    (hprimal : U ≤ V F d) : U = V F d :=
  le_antisymm hprimal (V_le_closed_space U hinput hmul)

theorem not_mem_V_of_closed_separator {F : Set (MvPolynomial σ k)} {d : ℕ}
    (U : Submodule k (MvPolynomial σ k))
    (hinput : ∀ f ∈ F, f.totalDegree ≤ d → f ∈ U)
    (hmul : ∀ f ∈ U, ∀ g : MvPolynomial σ k,
      f.totalDegree + g.totalDegree ≤ d → f * g ∈ U)
    {q : MvPolynomial σ k} (hsep : q ∉ U) : q ∉ V F d :=
  fun h => hsep (V_le_closed_space U hinput hmul h)

/-- Once one is derived, every higher-degree consequence is available. -/
theorem lastFallSet_of_refutation {F : Set (MvPolynomial σ k)} {d : ℕ}
    (h : (1 : MvPolynomial σ k) ∈ V F d) : d ∈ lastFallSet F := by
  intro q _
  have h1 := V_mono F (Nat.le_max_left d q.totalDegree) h
  have hm := mul_mem_V (g := q) h1 (by simp)
  simpa using hm

/-- The unit-ideal bridge is explicit. -/
theorem exact_lastFallDegree_of_refutation {F : Set (MvPolynomial σ k)} {d : ℕ}
    (hupper : (1 : MvPolynomial σ k) ∈ V F d)
    (hlower : (1 : MvPolynomial σ k) ∉ V F (d-1)) :
    lastFallDegree F = d := by
  have hunit : (1 : MvPolynomial σ k) ∈ Ideal.span F := V_le_ideal_span F d hupper
  have hb := lastFallSet_of_refutation hupper
  have hu : lastFallDegree F ≤ d := Nat.sInf_le hb
  have hmin : lastFallDegree F ∈ lastFallSet F := Nat.sInf_mem ⟨d, hb⟩
  have h1 : (1 : MvPolynomial σ k) ∈ V F (lastFallDegree F) := by
    simpa using hmin 1 hunit
  by_contra heq
  have hlt : lastFallDegree F < d := lt_of_le_of_ne hu heq
  exact hlower (V_mono F (by omega) h1)

/-- SAT lower bounds need a missing ideal consequence, not missing one. -/
theorem lastFallDegree_gt_of_missing_consequence
    {F : Set (MvPolynomial σ k)} {d : ℕ}
    (hfin : (lastFallSet F).Nonempty) {q : MvPolynomial σ k}
    (hq : q ∈ Ideal.span F) (hdeg : q.totalDegree ≤ d)
    (hmiss : q ∉ V F d) : d < lastFallDegree F := by
  by_contra h
  have hd : lastFallDegree F ≤ d := by omega
  have hmin := Nat.sInf_mem hfin
  have hqV : q ∈ V F (max (lastFallDegree F) q.totalDegree) := hmin q hq
  exact hmiss (V_mono F (max_le hd hdeg) hqV)

noncomputable def assignmentIndicator [DecidableEq σ] (s t : Finset σ) : MvPolynomial σ k :=
  (∏ i ∈ t, X i) * ∏ i ∈ s \ t, (1-X i)

/-- Uses x and 1-x: valid also in odd characteristic. -/
theorem assignmentIndicator_partition [DecidableEq σ] (s : Finset σ) :
    ∑ t ∈ s.powerset, (assignmentIndicator s t : MvPolynomial σ k) = 1 := by
  have h : ∀ i : σ, (X i : MvPolynomial σ k) + (1-X i) = 1 := by
    intro i
    rw [add_comm]
    exact sub_add_cancel 1 (X i)
  unfold assignmentIndicator
  rw [← Finset.prod_add]
  simp_rw [h]
  simp

/-- Final assembly only. Support-aware derivation of the localized rows is
an explicit prerequisite, not a proved Semaev upper bound. -/
theorem refutation_of_localized_fibres {ι α : Type*} [Fintype ι] [Fintype α]
    {F : Set (MvPolynomial σ k)} {d : ℕ}
    (delta : ι → MvPolynomial σ k) (q : ι → α → MvPolynomial σ k)
    (weight : ι → α → k)
    (hrows : ∀ a i, delta a * q a i ∈ V F d)
    (hcontradiction : ∀ a, ∑ i, weight a i • q a i = 1)
    (hpartition : ∑ a, delta a = 1) : (1 : MvPolynomial σ k) ∈ V F d := by
  have hdelta : ∀ a, delta a ∈ V F d := by
    intro a
    have hm : (∑ i, weight a i • (delta a * q a i)) ∈ V F d :=
      (V F d).sum_mem fun i _ => (V F d).smul_mem (weight a i) (hrows a i)
    have heq : (∑ i, weight a i • (delta a * q a i)) = delta a := by
      simp_rw [← mul_smul_comm]
      rw [← Finset.mul_sum, hcontradiction a, mul_one]
    rwa [heq] at hm
  rw [← hpartition]
  exact (V F d).sum_mem fun a _ => hdelta a

end CryptoResearch.FallDegree
#print axioms CryptoResearch.FallDegree.exact_closure_of_two_sides
#print axioms CryptoResearch.FallDegree.exact_lastFallDegree_of_refutation
#print axioms CryptoResearch.FallDegree.lastFallDegree_gt_of_missing_consequence
#print axioms CryptoResearch.FallDegree.assignmentIndicator_partition
#print axioms CryptoResearch.FallDegree.refutation_of_localized_fibres
