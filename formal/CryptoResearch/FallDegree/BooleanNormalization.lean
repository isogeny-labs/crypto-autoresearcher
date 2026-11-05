/-
Boolean normalization and repair at the ORIGINAL polynomial degree.

Source: analysis/boolean-fall-certificates-20261104/THEORY.md, section 1.
The variables are arbitrary and coefficients lie in any field.  This is
normalization by X_i^2 = X_i, not coefficient reduction to characteristic two.
The filtration is the ordinary polynomial `V` from LastFall.lean.

Also proved: for `N` variables, the ordinary last fall degree of a Boolean
system is at most `D` when `D >= N+1` and all raw inputs have degree at most
`D`. In particular multilinear inputs give the generic upper bound `N+1`.
No lower bound, Semaev-family result, or solving-degree theorem is asserted.
-/
import CryptoResearch.FallDegree.FirstFallBounded
import CryptoResearch.FallDegree.ClosureCertificates
import Mathlib.LinearAlgebra.Finsupp.LSum

namespace CryptoResearch.FallDegree

open MvPolynomial

variable {σ k : Type*} [Field k]

/-- Replace each positive exponent by one. -/
noncomputable def booleanExponent (s : σ →₀ ℕ) : σ →₀ ℕ :=
  s.mapRange (fun a => min a 1) (by simp)

@[simp] theorem booleanExponent_apply (s : σ →₀ ℕ) (i : σ) :
    booleanExponent s i = min (s i) 1 := rfl

@[simp] theorem booleanExponent_zero : booleanExponent (0 : σ →₀ ℕ) = 0 := by
  ext i
  simp

@[simp] theorem booleanExponent_idempotent (s : σ →₀ ℕ) :
    booleanExponent (booleanExponent s) = booleanExponent s := by
  ext i
  simp

theorem booleanExponent_single_add {i : σ} {a : ℕ} {t : σ →₀ ℕ}
    (ha : a ≠ 0) (hi : i ∉ t.support) :
    booleanExponent (Finsupp.single i a + t) =
      Finsupp.single i 1 + booleanExponent t := by
  classical
  have ht : t i = 0 := Finsupp.notMem_support_iff.mp hi
  ext j
  by_cases hji : j = i
  · subst j
    simp [ht, Nat.min_eq_right (show 1 ≤ a by omega)]
  · simp [hji]

theorem wt_booleanExponent_le (s : σ →₀ ℕ) : wt (booleanExponent s) ≤ wt s := by
  classical
  unfold wt booleanExponent
  rw [Finsupp.sum_mapRange_index (fun _ => rfl)]
  exact Finset.sum_le_sum fun i _ => min_le_left (s i) 1

/-- Coefficient-linear multilinear normal form. -/
noncomputable def booleanNF : MvPolynomial σ k →ₗ[k] MvPolynomial σ k :=
  (Finsupp.lsum k fun s : σ →₀ ℕ => monomial (R := k) (booleanExponent s)).comp
    (AddMonoidAlgebra.coeffLinearEquiv k).toLinearMap

@[simp] theorem booleanNF_monomial (s : σ →₀ ℕ) (c : k) :
    booleanNF (monomial s c) = monomial (booleanExponent s) c :=
  Finsupp.lsum_single k (fun t : σ →₀ ℕ => monomial (R := k) (booleanExponent t)) s c

theorem booleanNF_as_sum (p : MvPolynomial σ k) :
    booleanNF p = ∑ s ∈ p.support, monomial (booleanExponent s) (p.coeff s) := rfl

/-- Normalization never increases total degree. -/
theorem totalDegree_booleanNF_le (p : MvPolynomial σ k) :
    (booleanNF p).totalDegree ≤ p.totalDegree := by
  rw [booleanNF_as_sum]
  exact totalDegree_finsetSum_le fun s hs =>
    (totalDegree_monomial_le _ _).trans ((wt_booleanExponent_le s).trans (le_totalDegree hs))

@[simp] theorem booleanNF_idempotent (p : MvPolynomial σ k) :
    booleanNF (booleanNF p) = booleanNF p := by
  conv_lhs => rw [booleanNF_as_sum p, map_sum]
  simp only [booleanNF_monomial, booleanExponent_idempotent]
  exact (booleanNF_as_sum p).symm

/-- The one-variable repair uses cap `a`, with no factor of two. -/
theorem X_pow_sub_X_mem_V (i : σ) (a : ℕ) (ha : 1 ≤ a) :
    ((X i : MvPolynomial σ k) ^ a - X i) ∈ V (fieldEqGens σ k 2) a := by
  induction a with
  | zero => omega
  | succ a ih =>
    rcases Nat.eq_zero_or_pos a with rfl | hpos
    · simp
    · have hprev := ih hpos
      have hkey : ((X i : MvPolynomial σ k) ^ (a + 1) - X i) =
          ((X i : MvPolynomial σ k) ^ a - X i) * X i +
          ((X i : MvPolynomial σ k) ^ 2 - X i) := by ring
      rw [hkey]
      refine Submodule.add_mem _ ?_ ?_
      · refine mul_mem_V (V_mono _ (Nat.le_succ a) hprev) ?_
        have hdeg := totalDegree_le_of_mem_V hprev
        simpa only [totalDegree_X] using Nat.add_le_add_right hdeg 1
      · exact V_mono _ (by omega) (fe_mem_V (by omega : 1 ≤ 2) i)

/-- Repair a monomial by induction on its finitely supported exponent vector.
Every multiplication stays within the original monomial weight. -/
theorem monomial_boolean_repair_mem_V (s : σ →₀ ℕ) :
    (monomial s (1 : k) - monomial (booleanExponent s) 1) ∈
      V (fieldEqGens σ k 2) (wt s) := by
  classical
  induction s using Finsupp.induction with
  | zero => simp
  | single_add i a t hi ha ih =>
    have hkey :
        (monomial (Finsupp.single i a + t) (1 : k) -
          monomial (booleanExponent (Finsupp.single i a + t)) 1) =
        (monomial t (1 : k) - monomial (booleanExponent t) 1) * X i ^ a +
        ((X i : MvPolynomial σ k) ^ a - X i) * monomial (booleanExponent t) 1 := by
      rw [booleanExponent_single_add ha hi, monomial_single_add, monomial_single_add]
      simp only [pow_one]
      ring
    rw [hkey, wt_single_add]
    refine Submodule.add_mem _ ?_ ?_
    · refine mul_mem_V (V_mono _ (by omega : wt t ≤ a + wt t) ih) ?_
      have hdeg := totalDegree_le_of_mem_V ih
      simp only [totalDegree_X_pow]
      omega
    · have hpow := X_pow_sub_X_mem_V (k := k) i a (by omega)
      refine mul_mem_V (V_mono _ (by omega : a ≤ a + wt t) hpow) ?_
      have hdeg := totalDegree_le_of_mem_V hpow
      rw [totalDegree_monomial_one]
      have hwt := wt_booleanExponent_le t
      omega

/-- Scalar-weighted monomial repair at the original exponent weight. -/
theorem monomial_boolean_repair_coeff_mem_V (s : σ →₀ ℕ) (c : k) :
    (monomial s c - monomial (booleanExponent s) c) ∈
      V (fieldEqGens σ k 2) (wt s) := by
  have h : monomial s c - monomial (booleanExponent s) c =
      c • (monomial s (1 : k) - monomial (booleanExponent s) 1) := by
    simp [smul_sub, smul_monomial, smul_eq_mul]
  rw [h]
  exact Submodule.smul_mem _ c (monomial_boolean_repair_mem_V s)

/-- **Original-degree Boolean repair.** For every polynomial, its difference
from multilinear normal form is derivable from the bit equations at exactly
its original total-degree cap. No variable-count or characteristic hypothesis
is required. -/
theorem boolean_repair_mem_V (p : MvPolynomial σ k) :
    p - booleanNF p ∈ V (fieldEqGens σ k 2) p.totalDegree := by
  have hsum : p - booleanNF p =
      ∑ s ∈ p.support, (monomial s (p.coeff s) -
        monomial (booleanExponent s) (p.coeff s)) := by
    rw [Finset.sum_sub_distrib, ← p.as_sum, ← booleanNF_as_sum]
  rw [hsum]
  exact Submodule.sum_mem _ fun s hs =>
    V_mono _ (le_totalDegree hs) (monomial_boolean_repair_coeff_mem_V s (p.coeff s))

/-- At any adequate cap, ordinary derivability is unchanged by normalization
when the original system includes the bit equations. -/
theorem mem_V_iff_booleanNF_mem_V {F : Set (MvPolynomial σ k)}
    {p : MvPolynomial σ k} {D : ℕ} (hdeg : p.totalDegree ≤ D) :
    p ∈ V (F ∪ fieldEqGens σ k 2) D ↔
      booleanNF p ∈ V (F ∪ fieldEqGens σ k 2) D := by
  have hr : p - booleanNF p ∈ V (F ∪ fieldEqGens σ k 2) D :=
    V_mono_set Set.subset_union_right D (V_mono _ hdeg (boolean_repair_mem_V p))
  constructor
  · intro hp
    simpa using Submodule.sub_mem _ hp hr
  · intro hp
    simpa using Submodule.add_mem _ hr hp

@[simp] theorem booleanExponent_single (i : σ) (a : ℕ) :
    booleanExponent (Finsupp.single i a) = Finsupp.single i (min a 1) := by
  classical
  ext j
  by_cases h : j = i <;> simp [h]

/-- Capping before adding exponents gives the same final squarefree support. -/
theorem booleanExponent_add_left (s t : σ →₀ ℕ) :
    booleanExponent (booleanExponent s + t) = booleanExponent (s + t) := by
  ext i
  simp only [booleanExponent_apply, Finsupp.add_apply]
  omega

/-- Normalization is compatible with multiplication through its first input. -/
theorem booleanNF_mul_left (p q : MvPolynomial σ k) :
    booleanNF (booleanNF p * q) = booleanNF (p * q) := by
  induction p using MvPolynomial.induction_on' with
  | monomial s c =>
    induction q using MvPolynomial.induction_on' with
    | monomial t d =>
      simp [booleanExponent_add_left]
    | add q r hq hr =>
      simp only [mul_add, map_add, hq, hr]
  | add p r hp hr =>
    simp only [map_add, add_mul, hp, hr]

theorem booleanNF_mul_right (p q : MvPolynomial σ k) :
    booleanNF (p * booleanNF q) = booleanNF (p * q) := by
  simpa only [mul_comm] using booleanNF_mul_left q p

@[simp] theorem booleanNF_bit_equation (i : σ) :
    booleanNF ((X i : MvPolynomial σ k) ^ 2 - X i) = 0 := by
  rw [map_sub, X_pow_eq_monomial]
  change booleanNF (monomial (Finsupp.single i 2) (1 : k)) -
    booleanNF (monomial (Finsupp.single i 1) 1) = 0
  simp

/-- Every normal form on a finite variable type has degree at most its size. -/
theorem totalDegree_booleanNF_le_card [Fintype σ] (p : MvPolynomial σ k) :
    (booleanNF p).totalDegree ≤ Fintype.card σ := by
  classical
  have hweight : ∀ s : σ →₀ ℕ, wt (booleanExponent s) ≤ Fintype.card σ := by
    intro s
    unfold wt
    rw [Finsupp.sum_fintype _ _ (fun _ => rfl)]
    calc
      ∑ i : σ, booleanExponent s i ≤ ∑ _i : σ, 1 :=
        Finset.sum_le_sum fun i _ => min_le_right (s i) 1
      _ = Fintype.card σ := by simp
  rw [booleanNF_as_sum]
  exact totalDegree_finsetSum_le fun s _ => (totalDegree_monomial_le _ _).trans (hweight s)

/-- Variable closure of normalized rows implies closure under every multiplier.
No degree condition is hidden in this helper: the supplied variable closure
must hold for every normal form already in `W`. -/
theorem booleanNF_mul_mem_of_variable_closed
    (W : Submodule k (MvPolynomial σ k))
    (hX : ∀ p : MvPolynomial σ k, booleanNF p ∈ W →
      ∀ i : σ, booleanNF (booleanNF p * X i) ∈ W)
    {p : MvPolynomial σ k} (hp : booleanNF p ∈ W) (q : MvPolynomial σ k) :
    booleanNF (p * q) ∈ W := by
  induction q using MvPolynomial.induction_on with
  | C c =>
    rw [mul_comm p (C c), C_mul', map_smul]
    exact W.smul_mem c hp
  | add q r hq hr =>
    simpa only [mul_add, map_add] using W.add_mem hq hr
  | mul_X q i hq =>
    rw [← mul_assoc, ← booleanNF_mul_left]
    exact hX (p * q) hq i

/-- With one degree above the maximal squarefree degree, normalized rows are
closed under every variable. The raw-generator degree hypothesis keeps input
eligibility explicit. -/
theorem booleanNF_mem_V_of_mem_ideal_span [Fintype σ]
    {F : Set (MvPolynomial σ k)} {D : ℕ}
    (hcap : Fintype.card σ + 1 ≤ D)
    (hgen : ∀ f ∈ F, f.totalDegree ≤ D)
    {p : MvPolynomial σ k} (hp : p ∈ Ideal.span (F ∪ fieldEqGens σ k 2)) :
    booleanNF p ∈ V (F ∪ fieldEqGens σ k 2) D := by
  let W := V (F ∪ fieldEqGens σ k 2) D
  have hX : ∀ q : MvPolynomial σ k, booleanNF q ∈ W →
      ∀ i : σ, booleanNF (booleanNF q * X i) ∈ W := by
    intro q hq i
    have hdeg : (booleanNF q).totalDegree + (X i : MvPolynomial σ k).totalDegree ≤ D := by
      rw [totalDegree_X]
      exact (Nat.add_le_add_right (totalDegree_booleanNF_le_card q) 1).trans hcap
    have hm : booleanNF q * X i ∈ W := mul_mem_V hq hdeg
    exact (mem_V_iff_booleanNF_mem_V ((totalDegree_mul _ _).trans hdeg)).mp hm
  let I : Ideal (MvPolynomial σ k) := {
    carrier := {q | booleanNF q ∈ W}
    zero_mem' := by simpa only [Set.mem_ofPred_eq, map_zero] using W.zero_mem
    add_mem' := by
      intro q r hq hr
      change booleanNF (q + r) ∈ W
      simpa only [map_add] using W.add_mem hq hr
    smul_mem' := by
      intro q r hr
      change booleanNF (q * r) ∈ W
      simpa only [mul_comm] using booleanNF_mul_mem_of_variable_closed W hX hr q }
  have hinput : F ∪ fieldEqGens σ k 2 ⊆ I := by
    intro q hq
    change booleanNF q ∈ W
    rcases hq with hq | ⟨i, rfl⟩
    · exact (mem_V_iff_booleanNF_mem_V (hgen q hq)).mp
        (mem_V_of_mem_of_totalDegree_le (Set.mem_union_left _ hq) (hgen q hq))
    · simpa only [booleanNF_bit_equation] using W.zero_mem
  exact (Ideal.span_le.mpr hinput) hp

/-- **Generic Boolean upper bound.** If all raw generators are eligible at
`D ≥ N+1`, every ideal consequence is available at `max D (deg p)`.
This is an upper bound only, uniform over every system on these `N` variables. -/
theorem lastFallSet_boolean_system [Fintype σ]
    {F : Set (MvPolynomial σ k)} {D : ℕ}
    (hcap : Fintype.card σ + 1 ≤ D)
    (hgen : ∀ f ∈ F, f.totalDegree ≤ D) :
    D ∈ lastFallSet (F ∪ fieldEqGens σ k 2) := by
  intro p hp
  have hn := booleanNF_mem_V_of_mem_ideal_span hcap hgen hp
  exact (mem_V_iff_booleanNF_mem_V (le_max_right D p.totalDegree)).mpr
    (V_mono _ (le_max_left D p.totalDegree) hn)

theorem lastFallDegree_boolean_system_le [Fintype σ]
    {F : Set (MvPolynomial σ k)} {D : ℕ}
    (hcap : Fintype.card σ + 1 ≤ D)
    (hgen : ∀ f ∈ F, f.totalDegree ≤ D) :
    lastFallDegree (F ∪ fieldEqGens σ k 2) ≤ D :=
  Nat.sInf_le (lastFallSet_boolean_system hcap hgen)

/-- For multilinear input generators, `N+1` is an unconditional upper bound
on the ordinary last fall degree with the bit equations adjoined. -/
theorem lastFallDegree_boolean_system_le_card_succ [Fintype σ]
    {F : Set (MvPolynomial σ k)}
    (hgen : ∀ f ∈ F, booleanNF f = f) :
    lastFallDegree (F ∪ fieldEqGens σ k 2) ≤ Fintype.card σ + 1 := by
  apply lastFallDegree_boolean_system_le le_rfl
  intro f hf
  rw [← hgen f hf]
  exact (totalDegree_booleanNF_le_card f).trans (Nat.le_succ _)

/-- The usual coordinate-degree criterion implies that a polynomial is already
in the stated multilinear normal form. -/
theorem booleanNF_eq_self_of_degreeOf_le_one (p : MvPolynomial σ k)
    (hmulti : ∀ i : σ, p.degreeOf i ≤ 1) : booleanNF p = p := by
  classical
  rw [booleanNF_as_sum]
  conv_rhs => rw [p.as_sum]
  refine Finset.sum_congr rfl fun s hs => ?_
  have he : booleanExponent s = s := by
    ext i
    exact min_eq_left ((le_degreeOf_of_mem_support i hs).trans (hmulti i))
  rw [he]

/-- Raw inputs of degree at most `B` give the explicit presentation-aware
bound `max (N+1) B`. -/
theorem lastFallDegree_boolean_system_le_max_card_degree [Fintype σ]
    {F : Set (MvPolynomial σ k)} {B : ℕ}
    (hgen : ∀ f ∈ F, f.totalDegree ≤ B) :
    lastFallDegree (F ∪ fieldEqGens σ k 2) ≤ max (Fintype.card σ + 1) B :=
  lastFallDegree_boolean_system_le (le_max_left _ _)
    (fun f hf => (hgen f hf).trans (le_max_right _ _))

/-- The `N+1` bound with coordinate-wise multilinearity as the hypothesis. -/
theorem lastFallDegree_multilinear_system_le_card_succ [Fintype σ]
    {F : Set (MvPolynomial σ k)}
    (hgen : ∀ f ∈ F, ∀ i : σ, f.degreeOf i ≤ 1) :
    lastFallDegree (F ∪ fieldEqGens σ k 2) ≤ Fintype.card σ + 1 :=
  lastFallDegree_boolean_system_le_card_succ
    (fun f hf => booleanNF_eq_self_of_degreeOf_le_one f (hgen f hf))

/-- The bit-equation ideal is annihilated by normal form; this uses actual
polynomial ideal closure, rather than equality of evaluations. -/
theorem booleanNF_eq_zero_of_mem_bit_ideal {p : MvPolynomial σ k}
    (hp : p ∈ Ideal.span (fieldEqGens σ k 2)) : booleanNF p = 0 := by
  let I : Ideal (MvPolynomial σ k) := {
    carrier := {q | booleanNF q = 0}
    zero_mem' := map_zero _
    add_mem' := by
      intro q r hq hr
      change booleanNF (q + r) = 0
      rw [map_add, hq, hr, add_zero]
    smul_mem' := by
      intro q r hr
      change booleanNF (q * r) = 0
      rw [← booleanNF_mul_right, hr, mul_zero, map_zero] }
  have hinput : fieldEqGens σ k 2 ⊆ I := by
    rintro _ ⟨i, rfl⟩
    exact booleanNF_bit_equation i
  exact (Ideal.span_le.mpr hinput) hp

/-- **Exact bounded kernel identity.** At every cap, including zero and one,
the bit-equation closure consists exactly of bounded-degree polynomials
whose multilinear normal form is zero. -/
theorem mem_V_bit_iff_degree_and_booleanNF_eq_zero
    {p : MvPolynomial σ k} {D : ℕ} :
    p ∈ V (fieldEqGens σ k 2) D ↔
      p.totalDegree ≤ D ∧ booleanNF p = 0 := by
  constructor
  · intro hp
    exact ⟨totalDegree_le_of_mem_V hp,
      booleanNF_eq_zero_of_mem_bit_ideal (V_le_ideal_span _ _ hp)⟩
  · rintro ⟨hdeg, hnf⟩
    simpa only [hnf, sub_zero] using V_mono _ hdeg (boolean_repair_mem_V p)

/-- Normal form has exactly the Boolean ideal as its kernel. -/
theorem booleanNF_eq_zero_iff_mem_bit_ideal (p : MvPolynomial σ k) :
    booleanNF p = 0 ↔ p ∈ Ideal.span (fieldEqGens σ k 2) := by
  constructor
  · intro hp
    exact V_le_ideal_span _ _
      (mem_V_bit_iff_degree_and_booleanNF_eq_zero.mpr ⟨le_rfl, hp⟩)
  · exact booleanNF_eq_zero_of_mem_bit_ideal

end CryptoResearch.FallDegree
