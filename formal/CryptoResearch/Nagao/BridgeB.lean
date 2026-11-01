import CryptoResearch.Nagao.Bridge

/-!
# Bridge, witness B: the Lemma 4 counterexample in `MvPolynomial (Fin 3) (ZMod 2)`

`Bridge.lean` restates witness A of `Lemma4Witness.lean` in Mathlib `MvPolynomial`.
This module does the same for witness B, `F = {X₀X₁ + X₂, X₀X₂ + X₁}` over
`F_2[X₀, X₁, X₂]`, with **unrestricted** cofactors and the fall definitions of
`RecoveryRule.lean`:

* `toMv_fB₁`, `toMv_fB₂` identify the list data of witness B with these polynomials.
* With or without the field equations among the generators of the true system, there
  is no fall at degree 1 or 2 for any cofactors (`F_2[X₀, X₁, X₂]` is a domain, so
  every cofactor of a quadratic generator in a product of degree `≤ 2` is constant;
  the coefficients of `X₀X₁`, `X₀X₂`, `X₀²`, `X₁²`, `X₂²` force the constants to
  zero), and there is a fall at degree 3: `X₂ f₁ + X₁ f₂ = X₁² + X₂²`.
* There is a fake fall at degree 2: `red (f₁ + (X₀ + 1) f₂) = X₁ + X₂`.
* Hence `d_F ≤ d'_F` fails in the printed and inside placements (`lemma4_mvB_false`).

Not proved: that the `MvPolynomial` fall definitions transcribe Nagao's Definitions 5
and 6 (equality reading); anything for the literal `≥` reading, Proposition 5, or
elliptic curves.
-/

namespace CryptoResearch.Nagao.BridgeB

open MvPolynomial Finset CryptoResearch.Nagao.RecoveryRule CryptoResearch.Nagao.Bridge

abbrev Q := MvPolynomial (Fin 3) (ZMod 2)

/-! ### Fall statements over any finite variable type -/

/-- `d` is the first fall degree of `fs`: a fall at `d`, none at `1 ≤ D < d`. -/
def FirstFallIs' {σ ι : Type*} [DecidableEq σ] [Fintype σ] [Fintype ι]
    (fs : ι → MvPolynomial σ (ZMod 2)) (d : ℕ) : Prop :=
  (∃ G, IsFall fs G d) ∧ ∀ D, 1 ≤ D → D < d → ¬ ∃ G, IsFall fs G D

/-- Lemma 4 for one system, `d_F ≤ d'_F`, as in `Bridge.Lemma4Mv`. -/
def Lemma4Mv' {σ ι κ : Type*} [DecidableEq σ] [Fintype σ] [Fintype ι] [Fintype κ]
    (fsTrue : ι → MvPolynomial σ (ZMod 2)) (fsFake : κ → MvPolynomial σ (ZMod 2)) : Prop :=
  ∀ d, FirstFallIs' fsTrue d → ∀ D, (∃ g, IsFakeFall fsFake g D) → d ≤ D

/-! ### Exponent vectors and polynomials -/

theorem fin3_ext (a b : Fin 3 →₀ ℕ) : a = b ↔ a 0 = b 0 ∧ a 1 = b 1 ∧ a 2 = b 2 := by
  constructor
  · rintro rfl; exact ⟨rfl, rfl, rfl⟩
  · rintro ⟨h0, h1, h2⟩
    ext i; fin_cases i
    · exact h0
    · exact h1
    · exact h2

noncomputable abbrev e0 : Fin 3 →₀ ℕ := Finsupp.single 0 1
noncomputable abbrev e1 : Fin 3 →₀ ℕ := Finsupp.single 1 1
noncomputable abbrev e2 : Fin 3 →₀ ℕ := Finsupp.single 2 1
noncomputable abbrev e01 : Fin 3 →₀ ℕ := Finsupp.single 0 1 + Finsupp.single 1 1
noncomputable abbrev e02 : Fin 3 →₀ ℕ := Finsupp.single 0 1 + Finsupp.single 2 1
noncomputable abbrev e002 : Fin 3 →₀ ℕ := Finsupp.single 0 2 + Finsupp.single 2 1

/-- `f_1 = X₀X₁ + X₂`. -/
noncomputable def mB₁ : Q := X 0 * X 1 + X 2
/-- `f_2 = X₀X₂ + X₁`. -/
noncomputable def mB₂ : Q := X 0 * X 2 + X 1

noncomputable def mFB : Fin 2 → Q := ![mB₁, mB₂]

theorem mB₁_eq : mB₁ = monomial e01 1 + monomial e2 1 := by
  simp [mB₁, X, monomial_mul_monomial]

theorem mB₂_eq : mB₂ = monomial e02 1 + monomial e1 1 := by
  simp [mB₂, X, monomial_mul_monomial]

theorem expOf_110 : expOf 3 [1, 1, 0] = e01 := by
  rw [fin3_ext]; simp [expOf]

theorem expOf_001 : expOf 3 [0, 0, 1] = e2 := by
  rw [fin3_ext]; simp [expOf]

theorem expOf_101 : expOf 3 [1, 0, 1] = e02 := by
  rw [fin3_ext]; simp [expOf]

theorem expOf_010 : expOf 3 [0, 1, 0] = e1 := by
  rw [fin3_ext]; simp [expOf]

theorem toMv_fB₁ : toMv 3 Lemma4Witness.fB₁ = mB₁ := by
  simp [toMv, Lemma4Witness.fB₁, expOf_110, expOf_001, mB₁_eq]

theorem toMv_fB₂ : toMv 3 Lemma4Witness.fB₂ = mB₂ := by
  simp [toMv, Lemma4Witness.fB₂, expOf_101, expOf_010, mB₂_eq]

/-! ### Degrees and cofactors -/

theorem deg_fin3 (a : Fin 3 →₀ ℕ) : deg a = a 0 + a 1 + a 2 := by
  simp [deg, Fin.sum_univ_three]

theorem totalDegree_monomial_one3 (a : Fin 3 →₀ ℕ) :
    (monomial a (1 : ZMod 2)).totalDegree = deg a := by
  rw [totalDegree_monomial _ one_ne_zero, sum_eq_deg a (fun _ e => e) (fun _ _ => rfl)]

theorem le_totalDegree_of_coeff3 {p : Q} {m : Fin 3 →₀ ℕ} (h : p.coeff m ≠ 0) :
    deg m ≤ p.totalDegree :=
  deg_le_totalDegree (mem_support_iff.mpr h)

theorem coeff_zero_of_lt3 {p : Q} {m : Fin 3 →₀ ℕ} (h : p.totalDegree < deg m) :
    p.coeff m = 0 := by
  by_contra hc
  have := le_totalDegree_of_coeff3 hc
  omega

theorem totalDegree_two_of {p : Q} (a b : Fin 3 →₀ ℕ) (hp : p = monomial a 1 + monomial b 1)
    (ha : deg a = 2) (hb : deg b ≤ 2) (hab : a ≠ b) : p.totalDegree = 2 := by
  refine le_antisymm ?_ ?_
  · rw [hp]
    refine (totalDegree_add _ _).trans (max_le ?_ ?_)
    · rw [totalDegree_monomial_one3]; omega
    · rw [totalDegree_monomial_one3]; omega
  · have h := le_totalDegree_of_coeff3 (p := p) (m := a) (by
      rw [hp]; simp [coeff_monomial, hab.symm])
    omega

theorem totalDegree_mB₁ : mB₁.totalDegree = 2 :=
  totalDegree_two_of e01 e2 mB₁_eq (by rw [deg_fin3]; simp) (by rw [deg_fin3]; simp)
    (by rw [Ne, fin3_ext]; simp)

theorem totalDegree_mB₂ : mB₂.totalDegree = 2 :=
  totalDegree_two_of e02 e1 mB₂_eq (by rw [deg_fin3]; simp) (by rw [deg_fin3]; simp)
    (by rw [Ne, fin3_ext]; simp)

theorem fe_eq3 (j : Fin 3) : (fe j : Q) = monomial (Finsupp.single j 2) 1 -
    monomial (Finsupp.single j 1) 1 := by
  simp [fe, X, monomial_pow]

theorem totalDegree_fe3 (j : Fin 3) : (fe j : Q).totalDegree = 2 := by
  refine le_antisymm ?_ ?_
  · rw [fe_eq3]
    refine (totalDegree_sub _ _).trans (max_le ?_ ?_)
    · rw [totalDegree_monomial_one3, deg_fin3]; fin_cases j <;> simp
    · rw [totalDegree_monomial_one3, deg_fin3]; fin_cases j <;> simp
  · have h := le_totalDegree_of_coeff3 (p := fe j) (m := Finsupp.single j 2) (by
      rw [fe_eq3]; fin_cases j <;> simp [coeff_monomial, fin3_ext])
    rw [deg_fin3] at h
    fin_cases j <;> simpa using h

theorem two_eq_zero3 : (2 : Q) = 0 := by
  have h : (2 : Q) = C (2 : ZMod 2) := by rw [map_ofNat]
  rw [h, show (2 : ZMod 2) = 0 by decide, map_zero]

theorem ne_zero_of_totalDegree_pos3 {p : Q} (h : 0 < p.totalDegree) : p ≠ 0 := by
  rintro rfl; simp at h

theorem cof_zero3 {g s : Q} {D : ℕ} (hs : s ≠ 0) (h : (g * s).totalDegree ≤ D)
    (hD : D < s.totalDegree) : g = 0 := by
  by_contra hg
  rw [totalDegree_mul_of_isDomain hg hs] at h
  omega

theorem cof_const3 {g s : Q} (hs : s ≠ 0) (h : (g * s).totalDegree ≤ s.totalDegree) :
    g = C (g.coeff 0) := by
  by_cases hg : g = 0
  · simp [hg]
  rw [totalDegree_mul_of_isDomain hg hs] at h
  exact totalDegree_eq_zero_iff_eq_C.mp (by omega)

theorem mFB_deg (i : Fin 2) : (mFB i).totalDegree = 2 := by
  fin_cases i
  · exact totalDegree_mB₁
  · exact totalDegree_mB₂

theorem withFeB_deg (k : Fin 2 ⊕ Fin 3) : (withFe mFB k).totalDegree = 2 := by
  rcases k with i | j
  · exact mFB_deg i
  · exact totalDegree_fe3 j

/-- Generators of total degree exactly two: no fall at degree one. -/
theorem no_fall_one3 {ι : Type*} [Fintype ι] (fs : ι → Q) (hfs : ∀ i, (fs i).totalDegree = 2) :
    ¬ ∃ G, IsFall fs G 1 := by
  rintro ⟨G, hle, ⟨i, hi⟩, -, -⟩
  have hz : G i = 0 :=
    cof_zero3 (ne_zero_of_totalDegree_pos3 (by rw [hfs i]; norm_num)) (hle i) (by rw [hfs i]; norm_num)
  rw [hz, zero_mul] at hi
  simp at hi

/-- Every cofactor of a degree-two generator in a product of degree `≤ 2` is constant. -/
theorem cofactors_const {ι : Type*} [Fintype ι] (fs : ι → Q) (hfs : ∀ i, (fs i).totalDegree = 2)
    (G : ι → Q) (hle : ∀ i, (G i * fs i).totalDegree ≤ 2) (i : ι) :
    G i = C ((G i).coeff 0) :=
  cof_const3 (ne_zero_of_totalDegree_pos3 (by rw [hfs i]; norm_num)) (by rw [hfs i]; exact hle i)

/-! ### No fall at degree 2 -/

theorem out_no_fall_twoB : ¬ ∃ G, IsFall mFB G 2 := by
  rintro ⟨G, hle, -, hne, hlt⟩
  have hc := cofactors_const mFB mFB_deg G hle
  set c₁ := (G 0).coeff 0
  set c₂ := (G 1).coeff 0
  have hsum : ∑ i, G i * mFB i = C c₁ * mB₁ + C c₂ * mB₂ := by
    rw [Fin.sum_univ_two, hc 0, hc 1]; simp [mFB]; rfl
  rw [hsum] at hne hlt
  have hz : ∀ m : Fin 3 →₀ ℕ, deg m = 2 → (C c₁ * mB₁ + C c₂ * mB₂).coeff m = 0 :=
    fun m hm => coeff_zero_of_lt3 (by omega)
  have h₁ : c₁ = 0 := by
    have := hz e01 (by rw [deg_fin3]; simp)
    rw [mB₁_eq, mB₂_eq] at this
    simpa [AddMonoidAlgebra.coeff_add, coeff_C_mul, coeff_monomial, fin3_ext] using this
  have h₂ : c₂ = 0 := by
    have := hz e02 (by rw [deg_fin3]; simp)
    rw [mB₁_eq, mB₂_eq] at this
    simpa [AddMonoidAlgebra.coeff_add, coeff_C_mul, coeff_monomial, fin3_ext] using this
  exact hne (by rw [h₁, h₂]; simp)

theorem in_no_fall_twoB : ¬ ∃ G, IsFall (withFe mFB) G 2 := by
  rintro ⟨G, hle, -, hne, hlt⟩
  have hc := cofactors_const (withFe mFB) withFeB_deg G hle
  set c₁ := (G (Sum.inl 0)).coeff 0
  set c₂ := (G (Sum.inl 1)).coeff 0
  set c₃ := (G (Sum.inr 0)).coeff 0
  set c₄ := (G (Sum.inr 1)).coeff 0
  set c₅ := (G (Sum.inr 2)).coeff 0
  have hsum : ∑ k, G k * withFe mFB k =
      C c₁ * mB₁ + C c₂ * mB₂ + (C c₃ * fe 0 + C c₄ * fe 1 + C c₅ * fe 2) := by
    rw [Fintype.sum_sum_type, Fin.sum_univ_two, Fin.sum_univ_three, hc (Sum.inl 0),
      hc (Sum.inl 1), hc (Sum.inr 0), hc (Sum.inr 1), hc (Sum.inr 2)]
    simp [withFe, mFB]
    rfl
  rw [hsum] at hne hlt
  have hz : ∀ m : Fin 3 →₀ ℕ, deg m = 2 →
      (C c₁ * mB₁ + C c₂ * mB₂ + (C c₃ * fe 0 + C c₄ * fe 1 + C c₅ * fe 2)).coeff m = 0 :=
    fun m hm => coeff_zero_of_lt3 (by omega)
  have key : ∀ m : Fin 3 →₀ ℕ, deg m = 2 → _ := fun m hm => by
    have := hz m hm
    rw [mB₁_eq, mB₂_eq, fe_eq3, fe_eq3, fe_eq3] at this
    exact this
  have h₁ : c₁ = 0 := by
    have := key e01 (by rw [deg_fin3]; simp)
    simpa [AddMonoidAlgebra.coeff_add, coeff_sub, coeff_C_mul, coeff_monomial, fin3_ext] using this
  have h₂ : c₂ = 0 := by
    have := key e02 (by rw [deg_fin3]; simp)
    simpa [AddMonoidAlgebra.coeff_add, coeff_sub, coeff_C_mul, coeff_monomial, fin3_ext] using this
  have h₃ : c₃ = 0 := by
    have := key (Finsupp.single 0 2) (by rw [deg_fin3]; simp)
    simpa [AddMonoidAlgebra.coeff_add, coeff_sub, coeff_C_mul, coeff_monomial, fin3_ext] using this
  have h₄ : c₄ = 0 := by
    have := key (Finsupp.single 1 2) (by rw [deg_fin3]; simp)
    simpa [AddMonoidAlgebra.coeff_add, coeff_sub, coeff_C_mul, coeff_monomial, fin3_ext] using this
  have h₅ : c₅ = 0 := by
    have := key (Finsupp.single 2 2) (by rw [deg_fin3]; simp)
    simpa [AddMonoidAlgebra.coeff_add, coeff_sub, coeff_C_mul, coeff_monomial, fin3_ext] using this
  exact hne (by rw [h₁, h₂, h₃, h₄, h₅]; simp)

/-! ### Fall at degree 3 -/

/-- `X₂ f₁ + X₁ f₂ = X₁² + X₂²`. -/
noncomputable def GoutB : Fin 2 → Q := ![X 2, X 1]

theorem sum_GoutB : ∑ i, GoutB i * mFB i = X 1 ^ 2 + X 2 ^ 2 := by
  rw [Fin.sum_univ_two]
  simp only [GoutB, mFB, mB₁, mB₂, Matrix.cons_val_zero, Matrix.cons_val_one]
  have : (X 2 : Q) * (X 0 * X 1 + X 2) + X 1 * (X 0 * X 2 + X 1) =
      2 * (X 0 * X 1 * X 2) + (X 1 ^ 2 + X 2 ^ 2) := by ring
  rw [this, two_eq_zero3, zero_mul, zero_add]

theorem sum_GoutB_eq : (X 1 ^ 2 + X 2 ^ 2 : Q) =
    monomial (Finsupp.single 1 2) 1 + monomial (Finsupp.single 2 2) 1 := by
  simp [X, monomial_pow]

theorem sum_GoutB_ne : (X 1 ^ 2 + X 2 ^ 2 : Q) ≠ 0 := by
  intro h
  have := congrArg (fun p : Q => p.coeff (Finsupp.single 1 2)) h
  rw [sum_GoutB_eq] at this
  simp [AddMonoidAlgebra.coeff_add, coeff_monomial, fin3_ext] at this

theorem sum_GoutB_deg : (X 1 ^ 2 + X 2 ^ 2 : Q).totalDegree < 3 := by
  rw [sum_GoutB_eq]
  refine lt_of_le_of_lt ((totalDegree_add _ _).trans (max_le ?_ ?_)) (by norm_num : 2 < 3)
  · rw [totalDegree_monomial_one3, deg_fin3]; simp
  · rw [totalDegree_monomial_one3, deg_fin3]; simp

theorem X_mul_deg (j : Fin 3) {s : Q} (hs : s.totalDegree = 2) : (X j * s).totalDegree = 3 := by
  rw [totalDegree_mul_of_isDomain (X_ne_zero j) (ne_zero_of_totalDegree_pos3 (by omega)),
    totalDegree_X, hs]

theorem out_fall_threeB : IsFall mFB GoutB 3 := by
  refine ⟨fun i => ?_, ⟨0, ?_⟩, ?_, ?_⟩
  · fin_cases i
    · exact (X_mul_deg 2 totalDegree_mB₁).le
    · exact (X_mul_deg 1 totalDegree_mB₂).le
  · exact X_mul_deg 2 totalDegree_mB₁
  · rw [sum_GoutB]; exact sum_GoutB_ne
  · rw [sum_GoutB]; exact sum_GoutB_deg

noncomputable def GinB : Fin 2 ⊕ Fin 3 → Q := Sum.elim GoutB 0

theorem sum_GinB : ∑ k, GinB k * withFe mFB k = X 1 ^ 2 + X 2 ^ 2 := by
  rw [Fintype.sum_sum_type]
  simp only [GinB, withFe, Sum.elim_inl, Sum.elim_inr, Pi.zero_apply, zero_mul,
    Finset.sum_const_zero, add_zero]
  exact sum_GoutB

theorem in_fall_threeB : IsFall (withFe mFB) GinB 3 := by
  obtain ⟨hle, ⟨i, hi⟩, -, -⟩ := out_fall_threeB
  refine ⟨fun k => ?_, ⟨Sum.inl i, ?_⟩, ?_, ?_⟩
  · rcases k with i | j
    · exact hle i
    · simp [GinB, withFe]
  · simpa [GinB, withFe] using hi
  · rw [sum_GinB]; exact sum_GoutB_ne
  · rw [sum_GinB]; exact sum_GoutB_deg

/-! ### Fake fall at degree 2 -/

theorem clamp_id_of (a : Fin 3 →₀ ℕ) (h : ∀ i, a i ≤ 1) : clamp a = a := by
  ext i; simp [clamp, h i]

theorem clamp_e002 : clamp e002 = e02 := by
  rw [fin3_ext]; simp [clamp]

theorem red_mB₁ : red mB₁ = mB₁ := by
  rw [mB₁_eq, red_add, red_monomial, red_monomial,
    clamp_id_of e01 (by intro i; fin_cases i <;> simp),
    clamp_id_of e2 (by intro i; fin_cases i <;> simp)]

/-- `(X₀ + 1) f₂ = X₀²X₂ + X₀X₁ + X₀X₂ + X₁`. -/
theorem P2_eq : (X 0 + 1 : Q) * mB₂ =
    monomial e002 1 + monomial e01 1 + (monomial e02 1 + monomial e1 1) := by
  rw [mB₂_eq, add_mul, one_mul, mul_add, X, monomial_mul_monomial, monomial_mul_monomial, mul_one]
  have h1 : (Finsupp.single (0 : Fin 3) 1 + e02) = e002 := by rw [fin3_ext]; simp
  have h2 : (Finsupp.single (0 : Fin 3) 1 + e1) = e01 := rfl
  rw [h1, h2]

theorem red_P2 : red ((X 0 + 1 : Q) * mB₂) = monomial e01 1 + monomial e1 1 := by
  rw [P2_eq, red_add, red_add, red_add, red_monomial, red_monomial, red_monomial, red_monomial,
    clamp_e002, clamp_id_of e01 (by intro i; fin_cases i <;> simp),
    clamp_id_of e02 (by intro i; fin_cases i <;> simp),
    clamp_id_of e1 (by intro i; fin_cases i <;> simp)]
  have : (monomial e02 (1 : ZMod 2)) + monomial e01 1 + (monomial e02 1 + monomial e1 1) =
      monomial e02 (1 + 1) + (monomial e01 1 + monomial e1 1) := by
    rw [map_add]; abel
  rw [this, show (1 + 1 : ZMod 2) = 0 by decide, map_zero, zero_add]

noncomputable def gFakeB : Fin 2 → Q := ![1, X 0 + 1]

theorem red_sum_fakeB : red (∑ i, gFakeB i * mFB i) = monomial e1 1 + monomial e2 1 := by
  rw [Fin.sum_univ_two]
  simp only [gFakeB, mFB, Matrix.cons_val_zero, Matrix.cons_val_one, one_mul]
  rw [red_add, red_mB₁, red_P2, mB₁_eq]
  have : (monomial e01 (1 : ZMod 2)) + monomial e2 1 + (monomial e01 1 + monomial e1 1) =
      monomial e01 (1 + 1) + (monomial e1 1 + monomial e2 1) := by
    rw [map_add]; abel
  rw [this, show (1 + 1 : ZMod 2) = 0 by decide, map_zero, zero_add]

theorem fake_fall_twoB : IsFakeFall mFB gFakeB 2 := by
  refine ⟨fun i => ?_, ⟨0, ?_⟩, ?_, ?_⟩
  · fin_cases i
    · change (red (1 * mB₁)).totalDegree ≤ 2
      rw [one_mul, red_mB₁, totalDegree_mB₁]
    · change (red ((X 0 + 1) * mB₂)).totalDegree ≤ 2
      rw [red_P2]
      refine (totalDegree_add _ _).trans (max_le ?_ ?_)
      · rw [totalDegree_monomial_one3, deg_fin3]; simp
      · rw [totalDegree_monomial_one3, deg_fin3]; simp
  · change (red (1 * mB₁)).totalDegree = 2
    rw [one_mul, red_mB₁, totalDegree_mB₁]
  · rw [red_sum_fakeB]
    intro h
    have := congrArg (fun p : Q => p.coeff e1) h
    simp [AddMonoidAlgebra.coeff_add, coeff_monomial, fin3_ext] at this
  · rw [red_sum_fakeB]
    refine lt_of_le_of_lt ((totalDegree_add _ _).trans (max_le ?_ ?_)) (by norm_num : 1 < 2)
    · rw [totalDegree_monomial_one3, deg_fin3]; simp
    · rw [totalDegree_monomial_one3, deg_fin3]; simp

theorem fake_fall_two_feB : IsFakeFall (withFe mFB) (Sum.elim gFakeB 0) 2 := by
  obtain ⟨hle, ⟨i, hi⟩, hne, hlt⟩ := fake_fall_twoB
  have hs : ∑ k, Sum.elim gFakeB 0 k * withFe mFB k = ∑ i, gFakeB i * mFB i := by
    rw [Fintype.sum_sum_type]; simp [withFe]
  refine ⟨fun k => ?_, ⟨Sum.inl i, ?_⟩, ?_, ?_⟩
  · rcases k with i | j
    · exact hle i
    · simp [withFe, red_zero]
  · simpa [withFe] using hi
  · rw [hs]; exact hne
  · rw [hs]; exact hlt

/-! ### Lemma 4 is false at witness B -/

theorem firstFall_outB : FirstFallIs' mFB 3 := by
  refine ⟨⟨GoutB, out_fall_threeB⟩, fun D h1 h3 => ?_⟩
  interval_cases D
  · exact no_fall_one3 mFB mFB_deg
  · exact out_no_fall_twoB

theorem firstFall_inB : FirstFallIs' (withFe mFB) 3 := by
  refine ⟨⟨GinB, in_fall_threeB⟩, fun D h1 h3 => ?_⟩
  interval_cases D
  · exact no_fall_one3 (withFe mFB) withFeB_deg
  · exact in_no_fall_twoB

/-- Witness B: printed placement (fake side from `F` or from `F ∪ S_fe`) and inside
placement, with the list-model data identified. -/
theorem lemma4_mvB_false :
    toMv 3 Lemma4Witness.fB₁ = mB₁ ∧ toMv 3 Lemma4Witness.fB₂ = mB₂ ∧
    ¬ Lemma4Mv' mFB mFB ∧ ¬ Lemma4Mv' mFB (withFe mFB) ∧
    ¬ Lemma4Mv' (withFe mFB) (withFe mFB) :=
  ⟨toMv_fB₁, toMv_fB₂,
    fun h => by have := h 3 firstFall_outB 2 ⟨gFakeB, fake_fall_twoB⟩; omega,
    fun h => by have := h 3 firstFall_outB 2 ⟨_, fake_fall_two_feB⟩; omega,
    fun h => by have := h 3 firstFall_inB 2 ⟨_, fake_fall_two_feB⟩; omega⟩

end CryptoResearch.Nagao.BridgeB
