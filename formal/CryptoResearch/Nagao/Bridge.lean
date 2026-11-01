import CryptoResearch.Nagao.RecoveryRule
import CryptoResearch.Nagao.Lemma4Witness
import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.MvPolynomial.NoZeroDivisors
import Mathlib.Algebra.Field.ZMod
import Mathlib.Tactic.IntervalCases

/-!
# Bridge: the Lemma 4 counterexample in Mathlib `MvPolynomial`

`Lemma4Witness.lean` and `Lemma4Outside.lean` refute Lemma 4 of Nagao 2015/984 in a
list-of-exponent-vectors model, with cofactors restricted to monomials of degree
`<= D`. This module restates witness A in Mathlib's `MvPolynomial (Fin 2) (ZMod 2)`,
with the fall definitions of `RecoveryRule.lean`, and proves it there with
**unrestricted** cofactors:

* `toMv` sends a list-model polynomial to `MvPolynomial`; `toMv_fA₁`, `toMv_fA₂`
  identify the list data of witness A with `X^2 Y` and `X Y + X`.
* Over `F = {X^2 Y, X Y + X}`, with or without the field equations among the
  generators of the true system, there is no fall at degree 1 or 2 for any
  cofactors, and there is a fall at degree 3; so the first fall degree is 3.
* There is a fake fall of `F` at degree 2, so the fake first fall degree is at most 2.
* Hence `d_F <= d'_F` fails (`lemma4_mv_false_inside`, `lemma4_mv_false_outside`).

Also proved: `red` is additive and idempotent (`red_add`, `red_red`), so the fake
sum `red (∑ g_i f_i)` used in `RecoveryRule.lean` equals the reduction of the sum of
reduced products (`red_sum_red`), which is how the list model computes it.

Not proved: that the `MvPolynomial` fall definitions transcribe Nagao's Definitions
5 and 6 (equality reading); witness B in `MvPolynomial`; any statement for the
literal `>=` reading, Proposition 5, or elliptic curves.
-/

namespace CryptoResearch.Nagao.Bridge

open MvPolynomial Finset CryptoResearch.Nagao.RecoveryRule

/-! ### `red` is additive and idempotent -/

section Red

variable {σ R : Type*} [CommRing R] [DecidableEq σ]

omit [DecidableEq σ] in
theorem red_eq_of_subset (p : MvPolynomial σ R) {s : Finset (σ →₀ ℕ)} (hs : p.support ⊆ s) :
    red p = ∑ a ∈ s, monomial (clamp a) (p.coeff a) := by
  unfold red
  refine Finset.sum_subset hs fun a _ ha => ?_
  rw [notMem_support_iff.mp ha, map_zero]

theorem red_add (p q : MvPolynomial σ R) : red (p + q) = red p + red q := by
  classical
  have hp : p.support ⊆ p.support ∪ q.support := Finset.subset_union_left
  have hq : q.support ⊆ p.support ∪ q.support := Finset.subset_union_right
  have hpq : (p + q).support ⊆ p.support ∪ q.support := support_add
  rw [red_eq_of_subset _ hpq, red_eq_of_subset _ hp, red_eq_of_subset _ hq,
    ← Finset.sum_add_distrib]
  simp [AddMonoidAlgebra.coeff_add, map_add]

omit [DecidableEq σ] in
theorem red_zero : red (0 : MvPolynomial σ R) = 0 := by
  simp [red]

theorem red_monomial (a : σ →₀ ℕ) (c : R) : red (monomial a c) = monomial (clamp a) c := by
  classical
  rw [red_eq_of_subset _ (support_monomial_subset (a := c)), Finset.sum_singleton]
  simp [coeff_monomial]

theorem red_sum {ι : Type*} (s : Finset ι) (f : ι → MvPolynomial σ R) :
    red (∑ i ∈ s, f i) = ∑ i ∈ s, red (f i) := by
  classical
  induction s using Finset.induction_on with
  | empty => simp [red_zero]
  | insert i s hi ih => rw [Finset.sum_insert hi, Finset.sum_insert hi, red_add, ih]

omit [DecidableEq σ] in
theorem clamp_clamp (a : σ →₀ ℕ) : clamp (clamp a) = clamp a := by
  ext i
  simp [clamp]

theorem red_red (p : MvPolynomial σ R) : red (red p) = red p := by
  have h : red p = ∑ a ∈ p.support, monomial (clamp a) (p.coeff a) := rfl
  rw [h, red_sum]
  simp only [red_monomial, clamp_clamp]

/-- The fake sum of `RecoveryRule.lean` is the list model's fake sum. -/
theorem red_sum_red {ι : Type*} [Fintype ι] (p : ι → MvPolynomial σ R) :
    red (∑ i, red (p i)) = red (∑ i, p i) := by
  rw [red_sum, red_sum]
  simp only [red_red]

end Red

/-! ### Witness A in `MvPolynomial (Fin 2) (ZMod 2)` -/

abbrev P := MvPolynomial (Fin 2) (ZMod 2)

/-- `f_1 = X^2 Y`. -/
noncomputable def mA₁ : P := X 0 ^ 2 * X 1
/-- `f_2 = X Y + X`. -/
noncomputable def mA₂ : P := X 0 * X 1 + X 0

/-- The generators of witness A. -/
noncomputable def mFA : Fin 2 → P := ![mA₁, mA₂]

/-! #### The list model maps to these polynomials -/

/-- Exponent vector of the list model as a finsupp on `Fin n`. -/
noncomputable def expOf (n : ℕ) (m : List ℕ) : Fin n →₀ ℕ :=
  Finsupp.equivFunOnFinite.symm fun i => m.getD i.val 0

/-- A list-model polynomial over `F_2` (a set of monomials) as an `MvPolynomial`. -/
noncomputable def toMv (n : ℕ) (p : Lemma4Witness.Poly) : MvPolynomial (Fin n) (ZMod 2) :=
  (p.map fun m => monomial (expOf n m) 1).sum

theorem expOf_21 : expOf 2 [2, 1] = Finsupp.single 0 2 + Finsupp.single 1 1 := by
  ext i; fin_cases i <;> simp [expOf]

theorem expOf_11 : expOf 2 [1, 1] = Finsupp.single 0 1 + Finsupp.single 1 1 := by
  ext i; fin_cases i <;> simp [expOf]

theorem expOf_10 : expOf 2 [1, 0] = Finsupp.single 0 1 := by
  ext i; fin_cases i <;> simp [expOf]

theorem fin2_ext (a b : Fin 2 →₀ ℕ) : a = b ↔ a 0 = b 0 ∧ a 1 = b 1 := by
  constructor
  · rintro rfl; exact ⟨rfl, rfl⟩
  · rintro ⟨h0, h1⟩
    ext i; fin_cases i
    · exact h0
    · exact h1

/-- The four exponent vectors used below. -/
noncomputable abbrev eX : Fin 2 →₀ ℕ := Finsupp.single 0 1
noncomputable abbrev eXY : Fin 2 →₀ ℕ := Finsupp.single 0 1 + Finsupp.single 1 1
noncomputable abbrev eXX : Fin 2 →₀ ℕ := Finsupp.single 0 2
noncomputable abbrev eYY : Fin 2 →₀ ℕ := Finsupp.single 1 2
noncomputable abbrev eXXY : Fin 2 →₀ ℕ := Finsupp.single 0 2 + Finsupp.single 1 1

theorem mA₁_eq : mA₁ = monomial eXXY 1 := by
  simp [mA₁, X, monomial_pow, monomial_mul_monomial]

theorem mA₂_eq : mA₂ = monomial eXY 1 + monomial eX 1 := by
  simp [mA₂, X, monomial_mul_monomial]

theorem fe_eq (j : Fin 2) : (fe j : P) = monomial (Finsupp.single j 2) 1 -
    monomial (Finsupp.single j 1) 1 := by
  simp [fe, X, monomial_pow]

theorem toMv_fA₁ : toMv 2 Lemma4Witness.fA₁ = mA₁ := by
  simp [toMv, Lemma4Witness.fA₁, expOf_21, mA₁_eq]

theorem toMv_fA₂ : toMv 2 Lemma4Witness.fA₂ = mA₂ := by
  simp [toMv, Lemma4Witness.fA₂, expOf_11, expOf_10, mA₂_eq]

/-! #### Degrees -/

theorem deg_fin2 (a : Fin 2 →₀ ℕ) : deg a = a 0 + a 1 := by
  simp [deg, Fin.sum_univ_two]

theorem totalDegree_monomial_one (a : Fin 2 →₀ ℕ) : (monomial a (1 : ZMod 2)).totalDegree = deg a := by
  rw [totalDegree_monomial _ one_ne_zero, sum_eq_deg a (fun _ e => e) (fun _ _ => rfl)]

theorem le_totalDegree_of_coeff {p : P} {m : Fin 2 →₀ ℕ} (h : p.coeff m ≠ 0) :
    deg m ≤ p.totalDegree :=
  deg_le_totalDegree (mem_support_iff.mpr h)

theorem coeff_zero_of_lt {p : P} {m : Fin 2 →₀ ℕ} (h : p.totalDegree < deg m) : p.coeff m = 0 := by
  by_contra hc
  have := le_totalDegree_of_coeff hc
  omega

theorem totalDegree_mA₁ : mA₁.totalDegree = 3 := by
  rw [mA₁_eq, totalDegree_monomial_one, deg_fin2]
  simp

theorem totalDegree_mA₂ : mA₂.totalDegree = 2 := by
  refine le_antisymm ?_ ?_
  · rw [mA₂_eq]
    refine (totalDegree_add _ _).trans (max_le ?_ ?_)
    · rw [totalDegree_monomial_one, deg_fin2]; simp
    · rw [totalDegree_monomial_one, deg_fin2]; simp
  · have h := le_totalDegree_of_coeff (p := mA₂) (m := eXY) (by
      rw [mA₂_eq]; simp [AddMonoidAlgebra.coeff_add, coeff_monomial])
    rw [deg_fin2] at h
    simpa using h

theorem totalDegree_fe (j : Fin 2) : (fe j : P).totalDegree = 2 := by
  refine le_antisymm ?_ ?_
  · rw [fe_eq]
    refine (totalDegree_sub _ _).trans (max_le ?_ ?_)
    · rw [totalDegree_monomial_one, deg_fin2]; fin_cases j <;> simp
    · rw [totalDegree_monomial_one, deg_fin2]; fin_cases j <;> simp
  · have h := le_totalDegree_of_coeff (p := fe j) (m := Finsupp.single j 2) (by
      rw [fe_eq]; fin_cases j <;> simp [coeff_monomial, fin2_ext])
    rw [deg_fin2] at h
    fin_cases j <;> simpa using h

theorem two_eq_zero : (2 : P) = 0 := by
  have h : (2 : P) = C (2 : ZMod 2) := by rw [map_ofNat]
  rw [h, show (2 : ZMod 2) = 0 by decide, map_zero]

theorem ne_zero_of_totalDegree_pos {p : P} (h : 0 < p.totalDegree) : p ≠ 0 := by
  rintro rfl; simp at h

/-! #### Cofactors are forced to vanish or be constant -/

theorem cof_zero {g s : P} {D : ℕ} (hs : s ≠ 0) (h : (g * s).totalDegree ≤ D)
    (hD : D < s.totalDegree) : g = 0 := by
  by_contra hg
  rw [totalDegree_mul_of_isDomain hg hs] at h
  omega

theorem cof_const {g s : P} (hs : s ≠ 0) (h : (g * s).totalDegree ≤ s.totalDegree) :
    g = C (g.coeff 0) := by
  by_cases hg : g = 0
  · simp [hg]
  rw [totalDegree_mul_of_isDomain hg hs] at h
  exact totalDegree_eq_zero_iff_eq_C.mp (by omega)

theorem mFA_deg (i : Fin 2) : 2 ≤ (mFA i).totalDegree := by
  fin_cases i <;> simp [mFA, totalDegree_mA₁, totalDegree_mA₂]

theorem withFe_deg (k : Fin 2 ⊕ Fin 2) : 2 ≤ (withFe mFA k).totalDegree := by
  rcases k with i | j
  · exact mFA_deg i
  · simp [withFe, totalDegree_fe]

/-- Generators of degree at least two have no fall at degree one. -/
theorem no_fall_one {ι : Type*} [Fintype ι] (fs : ι → P) (hfs : ∀ i, 2 ≤ (fs i).totalDegree) :
    ¬ ∃ G, IsFall fs G 1 := by
  rintro ⟨G, hle, ⟨i, hi⟩, -, -⟩
  have hz : G i = 0 :=
    cof_zero (ne_zero_of_totalDegree_pos (by have := hfs i; omega)) (hle i) (by have := hfs i; omega)
  rw [hz, zero_mul] at hi
  simp at hi

/-! #### Outside placement: the true system is `F` alone -/

theorem out_no_fall_two : ¬ ∃ G, IsFall mFA G 2 := by
  rintro ⟨G, hle, -, hne, hlt⟩
  have h0 : G 0 = 0 := cof_zero (s := mA₁)
    (ne_zero_of_totalDegree_pos (by rw [totalDegree_mA₁]; norm_num)) (hle 0)
    (by rw [totalDegree_mA₁]; norm_num)
  have h1 : G 1 = C ((G 1).coeff 0) := cof_const (s := mA₂)
    (ne_zero_of_totalDegree_pos (by rw [totalDegree_mA₂]; norm_num))
    (by have := hle 1; simpa [mFA, totalDegree_mA₂] using this)
  set c := (G 1).coeff 0
  have hsum : ∑ i, G i * mFA i = C c * mA₂ := by
    rw [Fin.sum_univ_two, h0, h1]; simp [mFA]
  rw [hsum] at hne hlt
  have hc : c = 0 := by
    have := coeff_zero_of_lt (m := eXY) (by rw [deg_fin2]; simpa using hlt)
    rw [coeff_C_mul, mA₂_eq] at this
    simpa [AddMonoidAlgebra.coeff_add, coeff_monomial, fin2_ext] using this
  exact hne (by rw [hc]; simp)

/-- True fall at 3 without field equations: `1 * X^2 Y + X * (X Y + X) = X^2`. -/
noncomputable def Gout : Fin 2 → P := ![1, X 0]

theorem sum_Gout : ∑ i, Gout i * mFA i = X 0 ^ 2 := by
  rw [Fin.sum_univ_two]
  simp only [Gout, mFA, mA₁, mA₂, Matrix.cons_val_zero, Matrix.cons_val_one]
  have : (1 : P) * (X 0 ^ 2 * X 1) + X 0 * (X 0 * X 1 + X 0) = 2 * (X 0 ^ 2 * X 1) + X 0 ^ 2 := by
    ring
  rw [this, two_eq_zero, zero_mul, zero_add]

theorem totalDegree_X0_sq : (X 0 ^ 2 : P).totalDegree = 2 := totalDegree_X_pow _ _

theorem out_fall_three : IsFall mFA Gout 3 := by
  refine ⟨fun i => ?_, ⟨0, ?_⟩, ?_, ?_⟩
  · fin_cases i
    · simp [Gout, mFA, totalDegree_mA₁]
    · change (X (0 : Fin 2) * mA₂ : P).totalDegree ≤ 3
      refine (totalDegree_mul _ _).trans ?_
      rw [totalDegree_mA₂, totalDegree_X]
  · simp [Gout, mFA, totalDegree_mA₁]
  · rw [sum_Gout]; exact pow_ne_zero _ (X_ne_zero _)
  · rw [sum_Gout, totalDegree_X0_sq]; norm_num

/-! #### Inside placement: the true system is `F ∪ S_fe` -/

theorem in_no_fall_two : ¬ ∃ G, IsFall (withFe mFA) G 2 := by
  rintro ⟨G, hle, -, hne, hlt⟩
  have hfe : ∀ j, G (Sum.inr j) = C ((G (Sum.inr j)).coeff 0) := fun j =>
    cof_const (s := fe j) (ne_zero_of_totalDegree_pos (by rw [totalDegree_fe]; norm_num))
      (by have := hle (Sum.inr j); simpa [withFe, totalDegree_fe] using this)
  have h0 : G (Sum.inl 0) = 0 := cof_zero (s := mA₁)
    (ne_zero_of_totalDegree_pos (by rw [totalDegree_mA₁]; norm_num)) (hle (Sum.inl 0))
    (by rw [totalDegree_mA₁]; norm_num)
  have h1 : G (Sum.inl 1) = C ((G (Sum.inl 1)).coeff 0) := cof_const (s := mA₂)
    (ne_zero_of_totalDegree_pos (by rw [totalDegree_mA₂]; norm_num))
    (by have := hle (Sum.inl 1); simpa [withFe, mFA, totalDegree_mA₂] using this)
  set c₁ := (G (Sum.inl 1)).coeff 0
  set c₂ := (G (Sum.inr 0)).coeff 0
  set c₃ := (G (Sum.inr 1)).coeff 0
  have hsum : ∑ k, G k * withFe mFA k = C c₁ * mA₂ + (C c₂ * fe 0 + C c₃ * fe 1) := by
    rw [Fintype.sum_sum_type, Fin.sum_univ_two, Fin.sum_univ_two, h0, h1, hfe 0, hfe 1]
    simp [withFe, mFA]
    rfl
  rw [hsum] at hne hlt
  have hlt' : ∀ m : Fin 2 →₀ ℕ, deg m = 2 →
      (C c₁ * mA₂ + (C c₂ * fe 0 + C c₃ * fe 1)).coeff m = 0 :=
    fun m hm => coeff_zero_of_lt (by omega)
  have hc₁ : c₁ = 0 := by
    have := hlt' eXY (by rw [deg_fin2]; simp)
    rw [mA₂_eq, fe_eq, fe_eq] at this
    simpa [AddMonoidAlgebra.coeff_add, coeff_sub, coeff_C_mul, coeff_monomial, fin2_ext] using this
  have hc₂ : c₂ = 0 := by
    have := hlt' eXX (by rw [deg_fin2]; simp)
    rw [mA₂_eq, fe_eq, fe_eq] at this
    simpa [AddMonoidAlgebra.coeff_add, coeff_sub, coeff_C_mul, coeff_monomial, fin2_ext] using this
  have hc₃ : c₃ = 0 := by
    have := hlt' eYY (by rw [deg_fin2]; simp)
    rw [mA₂_eq, fe_eq, fe_eq] at this
    simpa [AddMonoidAlgebra.coeff_add, coeff_sub, coeff_C_mul, coeff_monomial, fin2_ext] using this
  exact hne (by rw [hc₁, hc₂, hc₃]; simp)

noncomputable def Gin : Fin 2 ⊕ Fin 2 → P := Sum.elim Gout 0

theorem sum_Gin : ∑ k, Gin k * withFe mFA k = X 0 ^ 2 := by
  rw [Fintype.sum_sum_type]
  simp only [Gin, withFe, Sum.elim_inl, Sum.elim_inr, Pi.zero_apply, zero_mul,
    Finset.sum_const_zero, add_zero]
  exact sum_Gout

theorem in_fall_three : IsFall (withFe mFA) Gin 3 := by
  obtain ⟨hle, ⟨i, hi⟩, -, -⟩ := out_fall_three
  refine ⟨fun k => ?_, ⟨Sum.inl i, ?_⟩, ?_, ?_⟩
  · rcases k with i | j
    · exact hle i
    · simp [Gin, withFe]
  · simpa [Gin, withFe] using hi
  · rw [sum_Gin]; exact pow_ne_zero _ (X_ne_zero _)
  · rw [sum_Gin, totalDegree_X0_sq]; norm_num

/-! #### Fake fall at degree 2 -/

theorem clamp_eXXY : clamp eXXY = eXY := by
  rw [fin2_ext]; simp [clamp]

theorem clamp_eXY : clamp eXY = eXY := by
  rw [fin2_ext]; simp [clamp]

theorem clamp_eX : clamp eX = eX := by
  rw [fin2_ext]; simp [clamp]

theorem red_mA₁ : red mA₁ = monomial eXY 1 := by
  rw [mA₁_eq, red_monomial, clamp_eXXY]

theorem red_mA₂ : red mA₂ = mA₂ := by
  rw [mA₂_eq, red_add, red_monomial, red_monomial, clamp_eXY, clamp_eX]

theorem red_sum_fake : red (mA₁ + mA₂) = monomial eX 1 := by
  rw [red_add, red_mA₁, red_mA₂, mA₂_eq, ← add_assoc, ← map_add,
    show (1 + 1 : ZMod 2) = 0 by decide, map_zero, zero_add]

noncomputable def gFake : Fin 2 → P := ![1, 1]

theorem fake_fall_two : IsFakeFall mFA gFake 2 := by
  have hs : ∑ i, gFake i * mFA i = mA₁ + mA₂ := by
    rw [Fin.sum_univ_two]; simp [gFake, mFA]
  refine ⟨fun i => ?_, ⟨0, ?_⟩, ?_, ?_⟩
  · fin_cases i
    · change (red (1 * mA₁)).totalDegree ≤ 2
      rw [one_mul, red_mA₁, totalDegree_monomial_one, deg_fin2]; simp
    · change (red (1 * mA₂)).totalDegree ≤ 2
      rw [one_mul, red_mA₂, totalDegree_mA₂]
  · change (red (1 * mA₁)).totalDegree = 2
    rw [one_mul, red_mA₁, totalDegree_monomial_one, deg_fin2]; simp
  · rw [hs, red_sum_fake]; simp
  · rw [hs, red_sum_fake, totalDegree_monomial_one, deg_fin2]; simp

/-- Fake side computed from `F ∪ S_fe`: the field equations get the zero cofactor. -/
theorem fake_fall_two_fe : IsFakeFall (withFe mFA) (Sum.elim gFake 0) 2 := by
  obtain ⟨hle, ⟨i, hi⟩, hne, hlt⟩ := fake_fall_two
  have hs : ∑ k, Sum.elim gFake 0 k * withFe mFA k = ∑ i, gFake i * mFA i := by
    rw [Fintype.sum_sum_type]; simp [withFe]
  refine ⟨fun k => ?_, ⟨Sum.inl i, ?_⟩, ?_, ?_⟩
  · rcases k with i | j
    · exact hle i
    · simp [withFe, red_zero]
  · simpa [withFe] using hi
  · rw [hs]; exact hne
  · rw [hs]; exact hlt

/-! #### Lemma 4 is false in `MvPolynomial` -/

/-- `d` is the first fall degree of `fs`: a fall at `d`, none at `1 ≤ D < d`. -/
def FirstFallIs {ι : Type*} [Fintype ι] (fs : ι → P) (d : ℕ) : Prop :=
  (∃ G, IsFall fs G d) ∧ ∀ D, 1 ≤ D → D < d → ¬ ∃ G, IsFall fs G D

/-- Lemma 4 for one system, `d_F ≤ d'_F`, stated without taking a minimum on the fake
side: the first fall degree is at most every degree that has a fake fall. -/
def Lemma4Mv {ι κ : Type*} [Fintype ι] [Fintype κ] (fsTrue : ι → P) (fsFake : κ → P) : Prop :=
  ∀ d, FirstFallIs fsTrue d → ∀ D, (∃ g, IsFakeFall fsFake g D) → d ≤ D

theorem firstFall_out : FirstFallIs mFA 3 := by
  refine ⟨⟨Gout, out_fall_three⟩, fun D h1 h3 => ?_⟩
  interval_cases D
  · exact no_fall_one mFA mFA_deg
  · exact out_no_fall_two

theorem firstFall_in : FirstFallIs (withFe mFA) 3 := by
  refine ⟨⟨Gin, in_fall_three⟩, fun D h1 h3 => ?_⟩
  interval_cases D
  · exact no_fall_one (withFe mFA) withFe_deg
  · exact in_no_fall_two

/-- **Printed placement** (true side `F` alone), fake side from `F`, unrestricted cofactors. -/
theorem lemma4_mv_false_outside : ¬ Lemma4Mv mFA mFA := fun h => by
  have := h 3 firstFall_out 2 ⟨gFake, fake_fall_two⟩
  omega

/-- Printed placement, fake side from `F ∪ S_fe`. -/
theorem lemma4_mv_false_outside_fe : ¬ Lemma4Mv mFA (withFe mFA) := fun h => by
  have := h 3 firstFall_out 2 ⟨_, fake_fall_two_fe⟩
  omega

/-- **Inside placement** (true side `F ∪ S_fe`), unrestricted cofactors. -/
theorem lemma4_mv_false_inside : ¬ Lemma4Mv (withFe mFA) (withFe mFA) := fun h => by
  have := h 3 firstFall_in 2 ⟨_, fake_fall_two_fe⟩
  omega

/-- All three placements at once, with the list-model data identified. -/
theorem lemma4_mv_false :
    toMv 2 Lemma4Witness.fA₁ = mA₁ ∧ toMv 2 Lemma4Witness.fA₂ = mA₂ ∧
    ¬ Lemma4Mv mFA mFA ∧ ¬ Lemma4Mv mFA (withFe mFA) ∧
    ¬ Lemma4Mv (withFe mFA) (withFe mFA) :=
  ⟨toMv_fA₁, toMv_fA₂, lemma4_mv_false_outside, lemma4_mv_false_outside_fe,
    lemma4_mv_false_inside⟩

end CryptoResearch.Nagao.Bridge
