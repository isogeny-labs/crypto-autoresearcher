import CryptoResearch.Nagao.Bridge
import CryptoResearch.Nagao.BridgeB

/-!
# Exact first fall degrees of both witnesses in `MvPolynomial`

Adopted, on the Coordinator's decision for item F2 of formal-review batch
BATCH-4c1c67, from the reviewer control `J3Controls.C4_fake_side` written by
TASK-20261101-cd72e8 (J3) in
`coordination/formal-reviews/BATCH-4c1c67/reviews/TASK-20261101-cd72e8/raw/J3/Controls.lean`.
The proof below is J3's, moved into the workspace namespace; only names and this
header changed.

`Bridge.lean` and `BridgeB.lean` prove that the true first fall degree is 3 and
exhibit a fake fall at degree 2, so `d'_F ≤ 2`. This module closes the gap to
`d'_F = 2`: with arbitrary cofactors there is no fake fall at degree 1 for any
family of generators without constant terms, because `red` preserves the
constant coefficient and a fake fall at 1 would need a nonzero constant reduced
sum. Both witnesses, with or without the field equations, qualify.

`exact_first_fall_degrees` states, for witnesses A and B in both placements,
`d_F = 3` and `d'_F = 2` exactly.

Not proved: that the `MvPolynomial` fall definitions transcribe Nagao's
Definitions 5 and 6 (equality reading); anything for the `≥` reading.
-/

namespace CryptoResearch.Nagao.FakeExact

open MvPolynomial CryptoResearch.Nagao.RecoveryRule

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

/-- Reduction modulo the field equations keeps the constant coefficient. -/
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

/-- Generators without constant terms have no fake fall at degree 1, for any cofactors. -/
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

/-- `d` is the fake first fall degree of `fs`: a fake fall at `d`, none at `1 ≤ D < d`. -/
def FakeFirstFallIs {σ ι : Type*} [Fintype ι] (fs : ι → MvPolynomial σ (ZMod 2)) (d : ℕ) : Prop :=
  (∃ g, IsFakeFall fs g d) ∧ ∀ D, 1 ≤ D → D < d → ¬ ∃ g, IsFakeFall fs g D

theorem fake_first_two {σ ι : Type*} [Fintype ι] (fs : ι → MvPolynomial σ (ZMod 2))
    (h0 : ∀ i, constantCoeff (fs i) = 0) (hf : ∃ g, IsFakeFall fs g 2) :
    FakeFirstFallIs fs 2 :=
  ⟨hf, fun D h1 h2 => by
    obtain rfl : D = 1 := by omega
    rintro ⟨g, hg⟩
    exact no_fakefall_one fs h0 g hg⟩

/-- `d'_F = 2` exactly for both witnesses, with or without the field equations. -/
theorem fake_first_fall_two :
    FakeFirstFallIs Bridge.mFA 2 ∧ FakeFirstFallIs (withFe Bridge.mFA) 2 ∧
    FakeFirstFallIs BridgeB.mFB 2 ∧ FakeFirstFallIs (withFe BridgeB.mFB) 2 :=
  ⟨fake_first_two _ mFA_cc ⟨_, Bridge.fake_fall_two⟩,
   fake_first_two _ (withFe_cc _ mFA_cc) ⟨_, Bridge.fake_fall_two_fe⟩,
   fake_first_two _ mFB_cc ⟨_, BridgeB.fake_fall_twoB⟩,
   fake_first_two _ (withFe_cc _ mFB_cc) ⟨_, BridgeB.fake_fall_two_feB⟩⟩

/-- **Exact degrees.** For witnesses A and B, printed (`F`) and inside (`F ∪ S_fe`)
placements: true first fall degree 3, fake first fall degree 2 (fake side from `F`
and from `F ∪ S_fe`), arbitrary cofactors. -/
theorem exact_first_fall_degrees :
    Bridge.FirstFallIs Bridge.mFA 3 ∧ Bridge.FirstFallIs (withFe Bridge.mFA) 3 ∧
    BridgeB.FirstFallIs' BridgeB.mFB 3 ∧ BridgeB.FirstFallIs' (withFe BridgeB.mFB) 3 ∧
    FakeFirstFallIs Bridge.mFA 2 ∧ FakeFirstFallIs (withFe Bridge.mFA) 2 ∧
    FakeFirstFallIs BridgeB.mFB 2 ∧ FakeFirstFallIs (withFe BridgeB.mFB) 2 :=
  ⟨Bridge.firstFall_out, Bridge.firstFall_in, BridgeB.firstFall_outB, BridgeB.firstFall_inB,
   fake_first_fall_two⟩

end CryptoResearch.Nagao.FakeExact
