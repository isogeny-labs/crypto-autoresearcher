import CryptoResearch.Nagao.Lemma4Witness
import CryptoResearch.Nagao.Lemma4Outside
import CryptoResearch.Nagao.RecoveryRule
import CryptoResearch.Nagao.Bridge
import CryptoResearch.Nagao.BridgeB

/-! Reviewer-written controls for J3 (TASK-20261101-cd72e8). Not producer evidence. -/

namespace J3Controls

open MvPolynomial CryptoResearch.Nagao CryptoResearch.Nagao.RecoveryRule

/-! ### D7/D8: degree 0 never carries a fall (so `1 ≤ D'` loses nothing) -/

theorem no_fall_zero {σ R ι : Type*} [CommRing R] [Fintype ι]
    (fs g : ι → MvPolynomial σ R) : ¬ IsFall fs g 0 := fun h => by
  have := h.2.2.2; omega

theorem no_fakefall_zero {σ R ι : Type*} [CommRing R] [Fintype ι]
    (fs g : ι → MvPolynomial σ R) : ¬ IsFakeFall fs g 0 := fun h => by
  have := h.2.2.2; omega

theorem list_no_fall_zero (n : Nat) (fake : Bool) (S : List Lemma4Witness.Poly) :
    ¬ Lemma4Witness.FallAt n fake S 0 := by
  rintro ⟨gs, -, hc⟩
  dsimp only [Lemma4Witness.Cond] at hc
  obtain ⟨-, -, hne, hlt⟩ := hc
  obtain ⟨m, hm⟩ := List.exists_mem_of_ne_nil _ hne
  exact absurd (hlt m hm) (Nat.not_lt_zero _)

/-! ### Proves-too-much control: `hU4` is load-bearing in `recovery` -/

theorem gFake_violates_U4 : ¬ ∀ i, (Bridge.gFake i * Bridge.mFA i).totalDegree ≤ 2 := by
  intro h
  have := h 0
  simp [Bridge.gFake, Bridge.mFA, Bridge.totalDegree_mA₁] at this

theorem recovery_without_U4_false :
    ¬ (∀ (fs g : Fin 2 → Bridge.P) (v : ℕ), IsFakeFall fs g v →
        ∃ G : Fin 2 ⊕ Fin 2 → Bridge.P, IsFall (withFe fs) G v) := fun h =>
  Bridge.in_no_fall_two (h Bridge.mFA Bridge.gFake 2 Bridge.fake_fall_two)

/-! ### Non-vacuity: `Lemma4Mv` is not false for free -/

theorem single_no_fall (D : ℕ) : ¬ ∃ G, IsFall (![X 0] : Fin 1 → Bridge.P) G D := by
  rintro ⟨G, -, ⟨i, hi⟩, -, hlt⟩
  fin_cases i
  simp only [Fin.sum_univ_one] at hlt
  simp at hi hlt
  omega

theorem lemma4Mv_holds_somewhere : Bridge.Lemma4Mv (![X 0] : Fin 1 → Bridge.P) Bridge.mFA :=
  fun d hd => absurd hd.1 (single_no_fall d)

/-! ### C4 gap: no fake fall at degree 1 with unrestricted cofactors (so d'_F = 2 exactly) -/

theorem clamp_eq_zero_iff {σ : Type*} (a : σ →₀ ℕ) : clamp a = 0 ↔ a = 0 := by
  constructor
  · intro h
    ext i
    have := DFunLike.congr_fun h i
    simp only [clamp, Finsupp.mapRange_apply, Finsupp.coe_zero, Pi.zero_apply] at this
    simp only [Finsupp.coe_zero, Pi.zero_apply]
    omega
  · rintro rfl
    ext i
    simp [clamp]

theorem constantCoeff_red {σ R : Type*} [CommRing R] (p : MvPolynomial σ R) :
    constantCoeff (red p) = constantCoeff p := by
  classical
  unfold red
  rw [map_sum]
  simp only [constantCoeff_monomial, clamp_eq_zero_iff]
  rw [Finset.sum_ite_eq']
  split_ifs with h
  · rw [constantCoeff_eq]
  · rw [constantCoeff_eq]
    exact (notMem_support_iff.mp h).symm

theorem no_fakefall_one {σ ι : Type*} [Fintype ι]
    (fs : ι → MvPolynomial σ (ZMod 2)) (h0 : ∀ i, constantCoeff (fs i) = 0)
    (g : ι → MvPolynomial σ (ZMod 2)) : ¬ IsFakeFall fs g 1 := by
  rintro ⟨-, -, hne, hlt⟩
  have hc : (red (∑ i, g i * fs i)).totalDegree = 0 := by omega
  rw [totalDegree_eq_zero_iff_eq_C] at hc
  apply hne
  rw [hc, ← constantCoeff_eq, constantCoeff_red, map_sum]
  simp [h0]

theorem fe_cc {σ : Type*} (j : σ) : constantCoeff (fe j : MvPolynomial σ (ZMod 2)) = 0 := by
  simp [fe]

theorem withFe_cc {σ ι : Type*} (fs : ι → MvPolynomial σ (ZMod 2))
    (h : ∀ i, constantCoeff (fs i) = 0) : ∀ k, constantCoeff (withFe fs k) = 0 := by
  rintro (i | j)
  · exact h i
  · exact fe_cc j

theorem mFA_cc : ∀ i, constantCoeff (Bridge.mFA i) = 0 := by
  intro i; fin_cases i <;> simp [Bridge.mFA, Bridge.mA₁, Bridge.mA₂]

theorem mFB_cc : ∀ i, constantCoeff (BridgeB.mFB i) = 0 := by
  intro i; fin_cases i <;> simp [BridgeB.mFB, BridgeB.mB₁, BridgeB.mB₂]

/-- "d'_F = 2": a fake fall at 2 and none at any `1 ≤ D < 2`, for arbitrary cofactors. -/
def FakeFirstFallIs {σ ι : Type*} [Fintype ι] (fs : ι → MvPolynomial σ (ZMod 2)) (d : ℕ) : Prop :=
  (∃ g, IsFakeFall fs g d) ∧ ∀ D, 1 ≤ D → D < d → ¬ ∃ g, IsFakeFall fs g D

theorem fake_first_two {σ ι : Type*} [Fintype ι] (fs : ι → MvPolynomial σ (ZMod 2))
    (h0 : ∀ i, constantCoeff (fs i) = 0) (hf : ∃ g, IsFakeFall fs g 2) :
    FakeFirstFallIs fs 2 :=
  ⟨hf, fun D h1 h2 => by
    obtain rfl : D = 1 := by omega
    rintro ⟨g, hg⟩
    exact no_fakefall_one fs h0 g hg⟩

theorem C4_fake_side :
    FakeFirstFallIs Bridge.mFA 2 ∧ FakeFirstFallIs (withFe Bridge.mFA) 2 ∧
    FakeFirstFallIs BridgeB.mFB 2 ∧ FakeFirstFallIs (withFe BridgeB.mFB) 2 :=
  ⟨fake_first_two _ mFA_cc ⟨_, Bridge.fake_fall_two⟩,
   fake_first_two _ (withFe_cc _ mFA_cc) ⟨_, Bridge.fake_fall_two_fe⟩,
   fake_first_two _ mFB_cc ⟨_, BridgeB.fake_fall_twoB⟩,
   fake_first_two _ (withFe_cc _ mFB_cc) ⟨_, BridgeB.fake_fall_two_feB⟩⟩

/-! ### D5: `red_sum_red` covers the fake sum of `IsFakeFall` for any finite index -/
example {σ R ι : Type*} [CommRing R] [DecidableEq σ] [Fintype ι] (g fs : ι → MvPolynomial σ R) :
    red (∑ i, red (g i * fs i)) = red (∑ i, g i * fs i) :=
  Bridge.red_sum_red (fun i => g i * fs i)

/-! ### D6 sharpness: no fake fall at 2 whose unreduced products have degree `≤ 2` -/

theorem A_no_U4_fakefall_two :
    ¬ ∃ g, IsFakeFall Bridge.mFA g 2 ∧ ∀ i, (g i * Bridge.mFA i).totalDegree ≤ 2 := by
  rintro ⟨g, hf, hu⟩
  exact Bridge.in_no_fall_two (recovery Bridge.mFA g 2 hf hu)

theorem B_no_U4_fakefall_two :
    ¬ ∃ g, IsFakeFall BridgeB.mFB g 2 ∧ ∀ i, (g i * BridgeB.mFB i).totalDegree ≤ 2 := by
  rintro ⟨g, hf, hu⟩
  exact BridgeB.in_no_fall_twoB (recovery BridgeB.mFB g 2 hf hu)

end J3Controls

#print axioms J3Controls.no_fall_zero
#print axioms J3Controls.no_fakefall_zero
#print axioms J3Controls.list_no_fall_zero
#print axioms J3Controls.gFake_violates_U4
#print axioms J3Controls.recovery_without_U4_false
#print axioms J3Controls.lemma4Mv_holds_somewhere
#print axioms J3Controls.constantCoeff_red
#print axioms J3Controls.C4_fake_side
#print axioms J3Controls.A_no_U4_fakefall_two
#print axioms J3Controls.B_no_U4_fakefall_two

/-! ### List-model certificates, evaluated (products, then sum) -/
open CryptoResearch.Nagao.Lemma4Witness in
def showCert (fake : Bool) (gs S : List Poly) : List Poly × Poly :=
  let gS := gens fake S
  let P := List.zipWith (fun g s => prep fake (mul g s)) gs gS
  (P, prep fake (norm P.flatten))
open CryptoResearch.Nagao.Lemma4Witness CryptoResearch.Nagao.Lemma4Outside in
#eval [("gA_true/SA", showCert false gA_true SA), ("gA_fake/SA", showCert true gA_fake SA),
       ("gB_true/SB", showCert false gB_true SB), ("gB_fake/SB", showCert true gB_fake SB),
       ("gA_out/FA", showCert false gA_out FA), ("gA_fake/FA", showCert true gA_fake FA),
       ("gB_out/FB", showCert false gB_out FB), ("gB_fake/FB", showCert true gB_fake FB)]
