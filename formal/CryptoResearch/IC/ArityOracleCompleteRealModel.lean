/-
Additive complete-real-model correction for the IC arity/oracle envelope.

This file deliberately imports, but does not modify, the historical target
`ArityOracleThreshold.lean`.  It proves only real-number cost-model algebra.
No curve, oracle implementation, probability/rank statement, or ECDLP/PFSE
bridge occurs in any theorem type.
-/
import CryptoResearch.IC.ArityOracleThreshold

set_option autoImplicit false

namespace CryptoResearch.IC.ArityOracleCompleteRealModel

open CryptoResearch.IC.ArityOracleThreshold

/-- The two-affine-piece envelope used by both oracle conventions. -/
noncomputable def envelope (d q β : ℝ) : ℝ := max (1 - d * β) (q * β)

/-- A lower bound together with arbitrarily close positive-domain witnesses.
This is an explicit infimum certificate over the open domain `β > 0`; unlike
a minimum statement it also covers an unattained infimum. -/
def IsPositiveInfimum (f : ℝ → ℝ) (a : ℝ) : Prop :=
  (∀ β, 0 < β → a ≤ f β) ∧
    ∀ ε, 0 < ε → ∃ β, 0 < β ∧ f β < a + ε

/-- Exact optimized value of the envelope on the positive `β`-domain. -/
noncomputable def envelopeInf (d q : ℝ) : ℝ :=
  if 0 < d then q / (d + q) else 1

/-- The two oracle coefficients after collecting affine terms. -/
noncomputable def qF (k : ℝ) : ℝ := max k 2
noncomputable def qG (k : ℝ) : ℝ := max (k + 1) 2
noncomputable def dParam (m k : ℝ) : ℝ := m - 1 - k

/-- Optimized all-decompositions envelope. -/
noncomputable def infF (m k : ℝ) : ℝ := envelopeInf (dParam m k) (qF k)

/-- Optimized one-decomposition envelope. -/
noncomputable def infG (m k : ℝ) : ℝ := envelopeInf (dParam m k) (qG k)

lemma envelope_at_crossing (d q : ℝ) (hd : 0 < d) (hq : 0 < q) :
    envelope d q (1 / (d + q)) = q / (d + q) := by
  unfold envelope
  have hp : 0 < d + q := by linarith
  have hn : d + q ≠ 0 := ne_of_gt hp
  have hleft : 1 - d * (1 / (d + q)) = q / (d + q) := by
    field_simp
    ring
  have hright : q * (1 / (d + q)) = q / (d + q) := by ring
  rw [hleft, hright, max_self]

lemma envelope_lower_pos (d q β : ℝ) (hd : 0 < d) (hq : 0 < q) (hβ : 0 < β) :
    q / (d + q) ≤ envelope d q β := by
  unfold envelope
  have hp : 0 < d + q := by linarith
  by_cases h : β ≤ 1 / (d + q)
  · have hc : β * (d + q) ≤ 1 := (le_div_iff₀ hp).mp h
    have hl : q / (d + q) ≤ 1 - d * β := by
      rw [div_le_iff₀ hp]
      nlinarith
    exact hl.trans (le_max_left _ _)
  · push Not at h
    have hc : 1 < β * (d + q) := (div_lt_iff₀ hp).mp h
    have hr : q / (d + q) ≤ q * β := by
      rw [div_le_iff₀ hp]
      nlinarith
    exact hr.trans (le_max_right _ _)

theorem envelope_infimum_pos (d q : ℝ) (hd : 0 < d) (hq : 0 < q) :
    IsPositiveInfimum (envelope d q) (q / (d + q)) := by
  constructor
  · intro β hβ
    exact envelope_lower_pos d q β hd hq hβ
  · intro ε hε
    refine ⟨1 / (d + q), by positivity, ?_⟩
    rw [envelope_at_crossing d q hd hq]
    linarith

theorem envelope_minimizer_pos (d q β : ℝ) (hd : 0 < d) (hq : 0 < q)
    (hβ : 0 < β) :
    envelope d q β = q / (d + q) ↔ β = 1 / (d + q) := by
  have hp : 0 < d + q := by linarith
  constructor
  · intro he
    rcases lt_trichotomy β (1 / (d + q)) with hlt | heq | hgt
    · have hc : β * (d + q) < 1 := (lt_div_iff₀ hp).mp hlt
      have hs : q / (d + q) < 1 - d * β := by
        rw [div_lt_iff₀ hp]
        nlinarith
      have := le_max_left (1 - d * β) (q * β)
      unfold envelope at he
      linarith
    · exact heq
    · have hc : 1 < β * (d + q) := (div_lt_iff₀ hp).mp hgt
      have hs : q / (d + q) < q * β := by
        rw [div_lt_iff₀ hp]
        nlinarith
      have := le_max_right (1 - d * β) (q * β)
      unfold envelope at he
      linarith
  · rintro rfl
    exact envelope_at_crossing d q hd hq

lemma envelope_zero (q β : ℝ) : envelope 0 q β = max 1 (q * β) := by
  simp [envelope]

theorem envelope_infimum_zero (q : ℝ) (hq : 0 < q) :
    IsPositiveInfimum (envelope 0 q) 1 := by
  constructor
  · intro β hβ
    rw [envelope_zero]
    exact le_max_left _ _
  · intro ε hε
    refine ⟨1 / (2 * q), by positivity, ?_⟩
    rw [envelope_zero]
    have hq2 : q * (1 / (2 * q)) = 1 / 2 := by field_simp
    rw [hq2, max_eq_left (by norm_num : (1 / 2 : ℝ) ≤ 1)]
    linarith

theorem envelope_minimizer_zero (q β : ℝ) (hq : 0 < q) (hβ : 0 < β) :
    envelope 0 q β = 1 ↔ β ≤ 1 / q := by
  rw [envelope_zero, max_eq_left_iff]
  rw [le_div_iff₀ hq]
  constructor <;> intro h <;> nlinarith

theorem envelope_infimum_neg (d q : ℝ) (hd : d < 0) (hq : 0 < q) :
    IsPositiveInfimum (envelope d q) 1 := by
  constructor
  · intro β hβ
    unfold envelope
    have : 1 < 1 - d * β := by nlinarith
    exact this.le.trans (le_max_left _ _)
  · intro ε hε
    let c : ℝ := q - d + 1
    have hc : 0 < c := by dsimp [c]; linarith
    refine ⟨ε / c, div_pos hε hc, ?_⟩
    unfold envelope
    rw [max_lt_iff]
    constructor
    · rw [sub_lt_iff_lt_add]
      have hdc : -d < c := by dsimp [c]; linarith
      have := (div_lt_iff₀ hc).mpr (mul_lt_mul_of_pos_left hdc hε)
      have ht : -d * (ε / c) < ε := by
        calc
          -d * (ε / c) = ε * -d / c := by ring
          _ < ε := this
      nlinarith
    · have hqc : q < c := by dsimp [c]; linarith
      have := (div_lt_iff₀ hc).mpr (mul_lt_mul_of_pos_left hqc hε)
      have ht : q * (ε / c) < ε := by
        calc
          q * (ε / c) = ε * q / c := by ring
          _ < ε := this
      linarith

theorem envelope_no_minimizer_neg (d q β : ℝ) (hd : d < 0) (hq : 0 < q)
    (hβ : 0 < β) : 1 < envelope d q β := by
  unfold envelope
  have : 1 < 1 - d * β := by nlinarith
  exact this.trans_le (le_max_left _ _)

theorem envelope_infimum (d q : ℝ) (hq : 0 < q) :
    IsPositiveInfimum (envelope d q) (envelopeInf d q) := by
  by_cases hd : 0 < d
  · simp only [envelopeInf, if_pos hd]
    exact envelope_infimum_pos d q hd hq
  · have hdn : d ≤ 0 := le_of_not_gt hd
    rcases hdn.eq_or_lt with rfl | hlt
    · simp only [envelopeInf, lt_self_iff_false, if_false]
      exact envelope_infimum_zero q hq
    · simp only [envelopeInf, if_neg (not_lt_of_ge hlt.le)]
      exact envelope_infimum_neg d q hlt hq

lemma max_zero_add (a b : ℝ) (hb : 0 ≤ b) : max 0 a + b = max b (a + b) := by
  by_cases ha : 0 ≤ a
  · rw [max_eq_right ha, max_eq_right]
    linarith
  · push Not at ha
    rw [max_eq_left ha.le, zero_add, max_eq_left]
    linarith

lemma max_mul_nonneg (a b β : ℝ) (hβ : 0 ≤ β) :
    max a b * β = max (a * β) (b * β) := by
  rcases le_total a b with hab | hba
  · rw [max_eq_right hab, max_eq_right (mul_le_mul_of_nonneg_right hab hβ)]
  · rw [max_eq_left hba, max_eq_left (mul_le_mul_of_nonneg_right hba hβ)]

theorem costAll_eq_envelope (m β k : ℝ) (hβ : 0 < β) (hk : 0 ≤ k) :
    costAll m β k = envelope (dParam m k) (qF k) β := by
  unfold costAll attemptsAll envelope dParam qF
  rw [max_zero_add (1 - β * (m - 1)) (k * β) (mul_nonneg hk hβ.le)]
  have hline : 1 - β * (m - 1) + k * β = 1 - (m - 1 - k) * β := by ring
  rw [hline, max_mul_nonneg k 2 β hβ.le]
  ac_rfl

theorem costOne_eq_envelope (m β k : ℝ) (hβ : 0 < β) (hk : 0 ≤ k) :
    costOne m β k = envelope (dParam m k) (qG k) β := by
  unfold costOne attemptsOne envelope dParam qG
  have hb : 0 ≤ (k + 1) * β := mul_nonneg (by linarith) hβ.le
  have hsum : max 0 (1 - β * m) + β + k * β =
      max 0 (1 - β * m) + (k + 1) * β := by ring
  rw [hsum, max_zero_add (1 - β * m) ((k + 1) * β) hb]
  have hline : 1 - β * m + (k + 1) * β = 1 - (m - 1 - k) * β := by ring
  rw [hline, max_mul_nonneg (k + 1) 2 β hβ.le]
  ac_rfl

/-! ## Optimized and pointwise half thresholds -/

theorem envelopeInf_lt_half_iff (d q : ℝ) (hq : 0 < q) :
    envelopeInf d q < 1 / 2 ↔ q < d := by
  by_cases hd : 0 < d
  · have hp : 0 < d + q := by linarith
    rw [envelopeInf, if_pos hd, div_lt_iff₀ hp]
    constructor <;> intro h <;> nlinarith
  · have hdn : d ≤ 0 := le_of_not_gt hd
    rw [envelopeInf, if_neg hd]
    constructor <;> intro h <;> linarith

theorem envelopeInf_eq_half_iff (d q : ℝ) (hq : 0 < q) :
    envelopeInf d q = 1 / 2 ↔ d = q := by
  by_cases hd : 0 < d
  · have hp : 0 < d + q := by linarith
    rw [envelopeInf, if_pos hd]
    constructor
    · intro h
      field_simp at h
      nlinarith
    · rintro rfl
      field_simp
      ring
  · have hdn : d ≤ 0 := le_of_not_gt hd
    rw [envelopeInf, if_neg hd]
    constructor <;> intro h <;> linarith

theorem half_lt_envelopeInf_iff (d q : ℝ) (hq : 0 < q) :
    1 / 2 < envelopeInf d q ↔ d < q := by
  by_cases hd : 0 < d
  · have hp : 0 < d + q := by linarith
    rw [envelopeInf, if_pos hd, lt_div_iff₀ hp]
    constructor <;> intro h <;> nlinarith
  · have hdn : d ≤ 0 := le_of_not_gt hd
    rw [envelopeInf, if_neg hd]
    constructor <;> intro h <;> linarith

theorem envelope_lt_half_iff (d q β : ℝ) (hdq : q < d) (hq : 0 < q)
    (hβ : 0 < β) :
    envelope d q β < 1 / 2 ↔ 1 / (2 * d) < β ∧ β < 1 / (2 * q) := by
  have hd : 0 < d := by linarith
  have h2d : 0 < 2 * d := by positivity
  have h2q : 0 < 2 * q := by positivity
  unfold envelope
  rw [max_lt_iff]
  constructor
  · rintro ⟨hl, hr⟩
    constructor
    · rw [div_lt_iff₀ h2d]
      nlinarith
    · rw [lt_div_iff₀ h2q]
      nlinarith
  · rintro ⟨hl, hr⟩
    constructor
    · have := (div_lt_iff₀ h2d).mp hl
      nlinarith
    · have := (lt_div_iff₀ h2q).mp hr
      nlinarith

theorem envelope_eq_half_of_d_gt_q (d q β : ℝ) (hdq : q < d) (hq : 0 < q)
    (hβ : 0 < β) :
    envelope d q β = 1 / 2 ↔
      β = 1 / (2 * d) ∨ β = 1 / (2 * q) := by
  have hd : 0 < d := by linarith
  have h2d : 0 < 2 * d := by positivity
  have h2q : 0 < 2 * q := by positivity
  constructor
  · intro he
    have hl : 1 - d * β ≤ 1 / 2 := by
      have := le_max_left (1 - d * β) (q * β)
      unfold envelope at he
      linarith
    have hr : q * β ≤ 1 / 2 := by
      have := le_max_right (1 - d * β) (q * β)
      unfold envelope at he
      linarith
    have hor : 1 - d * β = 1 / 2 ∨ q * β = 1 / 2 := by
      by_contra hn
      push Not at hn
      have hll : 1 - d * β < 1 / 2 := lt_of_le_of_ne hl hn.1
      have hrr : q * β < 1 / 2 := lt_of_le_of_ne hr hn.2
      have hm := max_lt hll hrr
      unfold envelope at he
      linarith
    rcases hor with hor | hor
    · left
      rw [eq_div_iff (ne_of_gt h2d)]
      nlinarith
    · right
      rw [eq_div_iff (ne_of_gt h2q)]
      nlinarith
  · rintro (rfl | rfl)
    · unfold envelope
      have hl : 1 - d * (1 / (2 * d)) = 1 / 2 := by
        field_simp
        ring
      have hr : q * (1 / (2 * d)) < 1 / 2 := by
        rw [mul_one_div, div_lt_iff₀ h2d]
        nlinarith
      rw [hl, max_eq_left hr.le]
    · unfold envelope
      have hr : q * (1 / (2 * q)) = 1 / 2 := by
        field_simp
      have hl : 1 - d * (1 / (2 * q)) < 1 / 2 := by
        rw [mul_one_div]
        have hratio : (1 / 2 : ℝ) < d / (2 * q) := by
          rw [div_lt_div_iff₀ (by norm_num : (0 : ℝ) < 2) h2q]
          nlinarith
        linarith
      rw [hr, max_eq_right hl.le]

theorem envelope_eq_half_of_d_eq_q (d q β : ℝ) (hdq : d = q) (hq : 0 < q)
    (hβ : 0 < β) :
    envelope d q β = 1 / 2 ↔ β = 1 / (2 * q) := by
  subst d
  have hm := envelope_minimizer_pos q q β hq hq hβ
  have hv : q / (q + q) = (1 / 2 : ℝ) := by
    field_simp
    ring
  have hb : 1 / (q + q) = 1 / (2 * q) := by ring_nf
  rw [← hv, hm, hb]

theorem envelope_gt_half_of_d_lt_q (d q β : ℝ) (hdq : d < q) (hq : 0 < q)
    (hβ : 0 < β) : 1 / 2 < envelope d q β := by
  have hi := (envelope_infimum d q hq).1 β hβ
  have hs := (half_lt_envelopeInf_iff d q hq).2 hdq
  linarith

lemma qF_pos (k : ℝ) : 0 < qF k := by
  unfold qF
  exact lt_of_lt_of_le (by norm_num) (le_max_right k 2)

lemma qG_pos (k : ℝ) : 0 < qG k := by
  unfold qG
  exact lt_of_lt_of_le (by norm_num) (le_max_right (k + 1) 2)

/-! ## Comparing the two oracle conventions -/

theorem qF_eq_qG_iff (k : ℝ) : qF k = qG k ↔ k ≤ 1 := by
  unfold qF qG
  constructor
  · intro he
    by_contra hn
    push Not at hn
    by_cases hk : k ≤ 2
    · rw [max_eq_right hk, max_eq_left (by linarith : 2 ≤ k + 1)] at he
      linarith
    · push Not at hk
      rw [max_eq_left hk.le, max_eq_left (by linarith : 2 ≤ k + 1)] at he
      linarith
  · intro hk
    rw [max_eq_right (by linarith : k ≤ 2),
      max_eq_right (by linarith : k + 1 ≤ 2)]

theorem qF_lt_qG_iff (k : ℝ) : qF k < qG k ↔ 1 < k := by
  constructor
  · intro h
    by_contra hn
    have he := (qF_eq_qG_iff k).2 (le_of_not_gt hn)
    rw [he] at h
    exact (lt_irrefl _ h)
  · intro hk
    unfold qF qG
    by_cases hk2 : k ≤ 2
    · rw [max_eq_right hk2, max_eq_left (by linarith : 2 ≤ k + 1)]
      linarith
    · push Not at hk2
      rw [max_eq_left hk2.le, max_eq_left (by linarith : 2 ≤ k + 1)]
      linarith

theorem qF_le_qG (k : ℝ) : qF k ≤ qG k := by
  unfold qF qG
  exact max_le_max (by linarith) le_rfl

theorem costAll_le_costOne_exact (m β k : ℝ) (hm : 2 ≤ m) (hβ : 0 < β)
    (hk : 0 ≤ k) :
    costAll m β k ≤ costOne m β k ∧
      (costAll m β k = costOne m β k ↔ k ≤ 1 ∨ β ≤ 1 / m) := by
  rw [costAll_eq_envelope m β k hβ hk, costOne_eq_envelope m β k hβ hk]
  constructor
  · unfold envelope
    exact max_le_max le_rfl (mul_le_mul_of_nonneg_right (qF_le_qG k) hβ.le)
  · constructor
    · intro he
      by_contra hn
      push Not at hn
      have hk1 : 1 < k := hn.1
      have hbm : 1 / m < β := hn.2
      have hm0 : 0 < m := by linarith
      have hmb' : 1 < β * m := (div_lt_iff₀ hm0).mp hbm
      have hmb : 1 < m * β := by nlinarith
      have hq : qF k < qG k := (qF_lt_qG_iff k).2 hk1
      have hqG : qG k = k + 1 := by
        unfold qG
        rw [max_eq_left (by linarith : 2 ≤ k + 1)]
      have hline : 1 - dParam m k * β < qG k * β := by
        rw [hqG]
        unfold dParam
        nlinarith
      have hright : qF k * β < qG k * β :=
        mul_lt_mul_of_pos_right hq hβ
      unfold envelope at he
      have hs : max (1 - dParam m k * β) (qF k * β) < qG k * β :=
        max_lt hline hright
      have hle := le_max_right (1 - dParam m k * β) (qG k * β)
      linarith
    · rintro (hk1 | hbm)
      · rw [(qF_eq_qG_iff k).2 hk1]
      · by_cases hk1 : k ≤ 1
        · rw [(qF_eq_qG_iff k).2 hk1]
        · have hk1' : 1 < k := lt_of_not_ge hk1
          have hqF : qF k = max k 2 := rfl
          have hqG : qG k = k + 1 := by
            unfold qG
            rw [max_eq_left (by linarith : 2 ≤ k + 1)]
          have hm0 : 0 < m := by linarith
          have hmb : m * β ≤ 1 := by
            have := (le_div_iff₀ hm0).mp hbm
            nlinarith
          have hlineG : qG k * β ≤ 1 - dParam m k * β := by
            rw [hqG]
            unfold dParam
            nlinarith
          have hlineF : qF k * β ≤ 1 - dParam m k * β := by
            exact (mul_le_mul_of_nonneg_right (qF_le_qG k) hβ.le).trans hlineG
          unfold envelope
          rw [max_eq_left hlineF, max_eq_left hlineG]

theorem envelopeInf_strict_mono_q (d q r : ℝ) (hd : 0 < d) (hq : 0 < q)
    (hqr : q < r) : envelopeInf d q < envelopeInf d r := by
  have hr : 0 < r := by linarith
  have hpq : 0 < d + q := by linarith
  have hpr : 0 < d + r := by linarith
  rw [envelopeInf, if_pos hd, envelopeInf, if_pos hd]
  rw [div_lt_div_iff₀ hpq hpr]
  nlinarith

theorem infF_eq_infG_iff (m k : ℝ) (hm : 2 ≤ m) (hk : 0 ≤ k) :
    infF m k = infG m k ↔ k ≤ 1 ∨ m - 1 ≤ k := by
  unfold infF infG
  by_cases hkm : k < m - 1
  · have hd : 0 < dParam m k := by unfold dParam; linarith
    constructor
    · intro he
      left
      by_contra hn
      have hq := (qF_lt_qG_iff k).2 (lt_of_not_ge hn)
      exact (ne_of_lt (envelopeInf_strict_mono_q (dParam m k) (qF k) (qG k)
        hd (qF_pos k) hq)) he
    · rintro (hk1 | hbad)
      · rw [(qF_eq_qG_iff k).2 hk1]
      · linarith
  · have hd : ¬ 0 < dParam m k := by unfold dParam; linarith
    rw [envelopeInf, if_neg hd, envelopeInf, if_neg hd]
    constructor
    · intro h
      exact Or.inr (le_of_not_gt hkm)
    · intro h
      rfl

theorem infF_lt_infG_iff (m k : ℝ) (hm : 2 ≤ m) (hk : 0 ≤ k) :
    infF m k < infG m k ↔ 1 < k ∧ k < m - 1 := by
  constructor
  · intro h
    constructor
    · by_contra hn
      have he := (infF_eq_infG_iff m k hm hk).2 (Or.inl (le_of_not_gt hn))
      linarith
    · by_contra hn
      have he := (infF_eq_infG_iff m k hm hk).2 (Or.inr (le_of_not_gt hn))
      linarith
  · rintro ⟨hk1, hkm⟩
    unfold infF infG
    have hd : 0 < dParam m k := by unfold dParam; linarith
    exact envelopeInf_strict_mono_q (dParam m k) (qF k) (qG k) hd
      (qF_pos k) ((qF_lt_qG_iff k).2 hk1)

/-! ## Sharp meet-in-the-middle class envelopes -/

lemma qF_eq_two (k : ℝ) (hk : k ≤ 2) : qF k = 2 := by
  exact max_eq_right hk

lemma qF_eq_self (k : ℝ) (hk : 2 ≤ k) : qF k = k := by
  exact max_eq_left hk

lemma qG_eq_succ (k : ℝ) (hk : 1 ≤ k) : qG k = k + 1 := by
  exact max_eq_left (by linarith)

theorem mitm_infF_small_bound (m k : ℝ) (hm2 : 2 ≤ m) (hm4 : m ≤ 4)
    (hk : m / 2 ≤ k) : 4 / (m + 2) ≤ infF m k := by
  have hk0 : 0 ≤ k := by linarith
  have hmp2 : 0 < m + 2 := by linarith
  by_cases hkm : k < m - 1
  · have hd : 0 < dParam m k := by unfold dParam; linarith
    unfold infF envelopeInf
    rw [if_pos hd]
    by_cases hk2 : k ≤ 2
    · rw [qF_eq_two k hk2]
      have hden : 0 < dParam m k + 2 := by unfold dParam; linarith
      rw [div_le_div_iff₀ hmp2 hden]
      unfold dParam
      nlinarith
    · have hk2' : 2 < k := lt_of_not_ge hk2
      rw [qF_eq_self k hk2'.le]
      have hden : 0 < dParam m k + k := by unfold dParam; linarith
      rw [div_le_div_iff₀ hmp2 hden]
      unfold dParam
      nlinarith
  · have hd : ¬ 0 < dParam m k := by unfold dParam; linarith
    unfold infF envelopeInf
    rw [if_neg hd]
    rw [div_le_iff₀ hmp2]
    nlinarith

theorem mitm_infF_large_bound (m k : ℝ) (hm : 4 ≤ m) (hk : m / 2 ≤ k) :
    m / (2 * (m - 1)) ≤ infF m k := by
  have hk2 : 2 ≤ k := by linarith
  have hm1 : 0 < m - 1 := by linarith
  have hden : 0 < 2 * (m - 1) := by positivity
  by_cases hkm : k < m - 1
  · have hd : 0 < dParam m k := by unfold dParam; linarith
    unfold infF envelopeInf
    rw [if_pos hd, qF_eq_self k hk2]
    have he : dParam m k + k = m - 1 := by unfold dParam; ring
    rw [he]
    rw [div_le_div_iff₀ hden hm1]
    nlinarith
  · have hd : ¬ 0 < dParam m k := by unfold dParam; linarith
    unfold infF envelopeInf
    rw [if_neg hd]
    rw [div_le_iff₀ hden]
    nlinarith

theorem mitm_infG_bound (m k : ℝ) (hm : 2 ≤ m) (hk : m / 2 ≤ k) :
    1 / 2 + 1 / m ≤ infG m k := by
  have hk1 : 1 ≤ k := by linarith
  have hm0 : 0 < m := by linarith
  by_cases hkm : k < m - 1
  · have hd : 0 < dParam m k := by unfold dParam; linarith
    unfold infG envelopeInf
    rw [if_pos hd, qG_eq_succ k hk1]
    have he : dParam m k + (k + 1) = m := by unfold dParam; ring
    rw [he]
    rw [le_div_iff₀ hm0]
    field_simp [ne_of_gt hm0]
    nlinarith
  · have hd : ¬ 0 < dParam m k := by unfold dParam; linarith
    unfold infG envelopeInf
    rw [if_neg hd]
    have hinv : 1 / m ≤ (1 / 2 : ℝ) := by
      rw [div_le_iff₀ hm0]
      nlinarith
    linarith

theorem mitm_infF_small_witness (m : ℝ) (hm2 : 2 ≤ m) (hm4 : m ≤ 4) :
    infF m (m / 2) = 4 / (m + 2) := by
  by_cases he : m = 2
  · subst m
    norm_num [infF, envelopeInf, dParam, qF]
  · have hm : 2 < m := lt_of_le_of_ne hm2 (Ne.symm he)
    have hd : 0 < dParam m (m / 2) := by unfold dParam; linarith
    have hq : qF (m / 2) = 2 := qF_eq_two _ (by linarith)
    unfold infF envelopeInf
    rw [if_pos hd, hq]
    have hden : dParam m (m / 2) + 2 = (m + 2) / 2 := by
      unfold dParam
      ring
    rw [hden]
    have hp : 0 < m + 2 := by linarith
    field_simp [ne_of_gt hp]
    ring

theorem mitm_infF_large_witness (m : ℝ) (hm : 4 ≤ m) :
    infF m (m / 2) = m / (2 * (m - 1)) := by
  have hd : 0 < dParam m (m / 2) := by unfold dParam; linarith
  have hq : qF (m / 2) = m / 2 := qF_eq_self _ (by linarith)
  unfold infF envelopeInf
  rw [if_pos hd, hq]
  have hden : dParam m (m / 2) + m / 2 = m - 1 := by
    unfold dParam
    ring
  rw [hden]
  have hm1 : 0 < m - 1 := by linarith
  field_simp [ne_of_gt hm1]

theorem mitm_infG_witness (m : ℝ) (hm : 2 ≤ m) :
    infG m (m / 2) = 1 / 2 + 1 / m := by
  by_cases he : m = 2
  · subst m
    norm_num [infG, envelopeInf, dParam, qG]
  · have hm' : 2 < m := lt_of_le_of_ne hm (Ne.symm he)
    have hd : 0 < dParam m (m / 2) := by unfold dParam; linarith
    have hq : qG (m / 2) = m / 2 + 1 := qG_eq_succ _ (by linarith)
    unfold infG envelopeInf
    rw [if_pos hd, hq]
    have hden : dParam m (m / 2) + (m / 2 + 1) = m := by
      unfold dParam
      ring
    rw [hden]
    have hm0 : 0 < m := by linarith
    field_simp [ne_of_gt hm0]

theorem mitm_no_uniform_positive_gap :
    ∀ ε : ℝ, 0 < ε → ∃ m k : ℝ,
      4 ≤ m ∧ m / 2 ≤ k ∧ infF m k < 1 / 2 + ε := by
  intro ε hε
  let m : ℝ := 4 + 1 / ε
  let k : ℝ := m / 2
  have hm : 4 ≤ m := by
    dsimp [m]
    have : 0 < 1 / ε := one_div_pos.mpr hε
    linarith
  refine ⟨m, k, hm, le_rfl, ?_⟩
  rw [mitm_infF_large_witness m hm]
  have hm1 : 0 < m - 1 := by linarith
  have hden : 0 < 2 * (m - 1) := by positivity
  have he : m / (2 * (m - 1)) = 1 / 2 + 1 / (2 * (m - 1)) := by
    field_simp
    ring
  rw [he]
  have hprod : 1 < ε * (2 * (m - 1)) := by
    dsimp [m]
    field_simp
    nlinarith
  have hgap : 1 / (2 * (m - 1)) < ε := by
    rw [div_lt_iff₀ hden]
    nlinarith
  linarith

/-! ## Specialization to `F` and `G`, and exact controls -/

theorem dq_positive (m k : ℝ) (hm : 2 ≤ m) :
    0 < dParam m k + qF k ∧ 0 < dParam m k + qG k := by
  have hfk : k ≤ qF k := le_max_left _ _
  have hgk : k + 1 ≤ qG k := le_max_left _ _
  unfold dParam
  constructor <;> linarith

theorem cost_infima (m k : ℝ) (hm : 2 ≤ m) (hk : 0 ≤ k) :
    IsPositiveInfimum (fun β ↦ costAll m β k) (infF m k) ∧
      IsPositiveInfimum (fun β ↦ costOne m β k) (infG m k) := by
  have hF := envelope_infimum (dParam m k) (qF k) (qF_pos k)
  have hG := envelope_infimum (dParam m k) (qG k) (qG_pos k)
  constructor
  · unfold IsPositiveInfimum at hF ⊢
    unfold infF
    constructor
    · intro β hβ
      change envelopeInf (dParam m k) (qF k) ≤ costAll m β k
      rw [costAll_eq_envelope m β k hβ hk]
      exact hF.1 β hβ
    · intro ε hε
      rcases hF.2 ε hε with ⟨β, hβ, hb⟩
      refine ⟨β, hβ, ?_⟩
      change costAll m β k < envelopeInf (dParam m k) (qF k) + ε
      rw [costAll_eq_envelope m β k hβ hk]
      exact hb
  · unfold IsPositiveInfimum at hG ⊢
    unfold infG
    constructor
    · intro β hβ
      change envelopeInf (dParam m k) (qG k) ≤ costOne m β k
      rw [costOne_eq_envelope m β k hβ hk]
      exact hG.1 β hβ
    · intro ε hε
      rcases hG.2 ε hε with ⟨β, hβ, hb⟩
      refine ⟨β, hβ, ?_⟩
      change costOne m β k < envelopeInf (dParam m k) (qG k) + ε
      rw [costOne_eq_envelope m β k hβ hk]
      exact hb

theorem optimized_equal_but_unattained (m k : ℝ) (hm : 2 ≤ m) (hk : 0 ≤ k)
    (hkm : m - 1 < k) :
    infF m k = infG m k ∧
      ¬ (∃ β, 0 < β ∧ costAll m β k = infF m k) ∧
      ¬ (∃ β, 0 < β ∧ costOne m β k = infG m k) := by
  have hd : dParam m k < 0 := by unfold dParam; linarith
  have hdn : ¬ 0 < dParam m k := not_lt_of_ge hd.le
  have hiF : infF m k = 1 := by unfold infF envelopeInf; rw [if_neg hdn]
  have hiG : infG m k = 1 := by unfold infG envelopeInf; rw [if_neg hdn]
  refine ⟨hiF.trans hiG.symm, ?_, ?_⟩
  · rintro ⟨β, hβ, he⟩
    rw [costAll_eq_envelope m β k hβ hk, hiF] at he
    have hs := envelope_no_minimizer_neg (dParam m k) (qF k) β hd (qF_pos k) hβ
    linarith
  · rintro ⟨β, hβ, he⟩
    rw [costOne_eq_envelope m β k hβ hk, hiG] at he
    have hs := envelope_no_minimizer_neg (dParam m k) (qG k) β hd (qG_pos k) hβ
    linarith

theorem F1_nonattainment :
    infF 2 2 = 1 ∧ infG 2 2 = 1 ∧
      (∀ β : ℝ, 0 < β → 1 < costAll 2 β 2) ∧
      (∀ β : ℝ, 0 < β → 1 < costOne 2 β 2) := by
  constructor
  · norm_num [infF, envelopeInf, dParam, qF]
  constructor
  · norm_num [infG, envelopeInf, dParam, qG]
  constructor
  · intro β hβ
    rw [costAll_eq_envelope 2 β 2 hβ (by norm_num)]
    apply lt_of_lt_of_le (show (1 : ℝ) < 1 + β by linarith)
    unfold envelope dParam qF
    norm_num
  · intro β hβ
    rw [costOne_eq_envelope 2 β 2 hβ (by norm_num)]
    apply lt_of_lt_of_le (show (1 : ℝ) < 1 + β by linarith)
    unfold envelope dParam qG
    norm_num

theorem F2_invalid_middle_bound :
    (0 : ℝ) / (5 - 1) = 0 ∧ infF 5 0 = 1 / 3 ∧
      costAll 5 (1 / 6) 0 = 1 / 3 := by
  norm_num [infF, envelopeInf, dParam, qF, costAll, attemptsAll]

theorem F3_pointwise_not_optimized :
    infF 5 1 = 2 / 5 ∧ costAll 5 1 1 = 2 ∧
      infF 7 2 = 1 / 3 ∧ costAll 7 1 2 = 2 := by
  norm_num [infF, envelopeInf, dParam, qF, costAll, attemptsAll]

theorem F4_strictness_boundaries :
    infF 3 2 = 1 ∧ infG 3 2 = 1 ∧
      costAll 5 (1 / 4) 2 = 1 / 2 := by
  norm_num [infF, infG, envelopeInf, dParam, qF, qG, costAll, attemptsAll]

theorem F5_unrestricted_branch_control :
    2 / ((2 : ℝ) + 1 - 3 / 2) = 4 / 3 ∧ infF 2 (3 / 2) = 1 ∧
      (∀ β : ℝ, 0 < β → 1 < costAll 2 β (3 / 2)) := by
  constructor
  · norm_num
  constructor
  · norm_num [infF, envelopeInf, dParam, qF]
  · intro β hβ
    rw [costAll_eq_envelope 2 β (3 / 2) hβ (by norm_num)]
    apply lt_of_lt_of_le (show (1 : ℝ) < 1 + β / 2 by linarith)
    unfold envelope dParam qF
    rw [max_eq_right (by norm_num : (3 / 2 : ℝ) ≤ 2)]
    convert le_max_left (1 + β / 2) (2 * β) using 1 <;> ring

theorem positive_exact_controls :
    costAll 5 (1 / 5) 1 = 2 / 5 ∧ costAll 3 (1 / 4) 0 = 1 / 2 := by
  norm_num [costAll, attemptsAll]

theorem blanket_attainment_control :
    ¬ ∃ β : ℝ, 0 < β ∧ costAll 2 β 2 = infF 2 2 := by
  rintro ⟨β, hβ, he⟩
  have hf := F1_nonattainment
  rw [hf.1] at he
  have := hf.2.2.1 β hβ
  linarith

/-- Every clause required by the dated complete-real-model correction.  The
aggregate target below returns this proposition, so the coverage is carried by
its elaborated type rather than by adjacent comments. -/
structure CompleteRealModel : Prop where
  normal_forms : ∀ m β k : ℝ, 2 ≤ m → 0 < β → 0 ≤ k →
    costAll m β k = envelope (dParam m k) (qF k) β ∧
      costOne m β k = envelope (dParam m k) (qG k) β
  denominator_positive : ∀ m k : ℝ, 2 ≤ m → 0 ≤ k →
    0 < dParam m k + qF k ∧ 0 < dParam m k + qG k
  exact_cost_infima : ∀ m k : ℝ, 2 ≤ m → 0 ≤ k →
    IsPositiveInfimum (fun β ↦ costAll m β k) (infF m k) ∧
      IsPositiveInfimum (fun β ↦ costOne m β k) (infG m k)
  infimum_positive : ∀ d q : ℝ, 0 < d → 0 < q →
    IsPositiveInfimum (envelope d q) (q / (d + q))
  minimizer_positive : ∀ d q β : ℝ, 0 < d → 0 < q → 0 < β →
    (envelope d q β = q / (d + q) ↔ β = 1 / (d + q))
  infimum_zero : ∀ q : ℝ, 0 < q → IsPositiveInfimum (envelope 0 q) 1
  minimizer_zero : ∀ q β : ℝ, 0 < q → 0 < β →
    (envelope 0 q β = 1 ↔ β ≤ 1 / q)
  infimum_negative : ∀ d q : ℝ, d < 0 → 0 < q →
    IsPositiveInfimum (envelope d q) 1
  no_minimizer_negative : ∀ d q β : ℝ, d < 0 → 0 < q → 0 < β →
    1 < envelope d q β
  optimized_half : ∀ d q : ℝ, 0 < q →
    (envelopeInf d q < 1 / 2 ↔ q < d) ∧
      (envelopeInf d q = 1 / 2 ↔ d = q) ∧
      (1 / 2 < envelopeInf d q ↔ d < q)
  pointwise_below : ∀ d q β : ℝ, q < d → 0 < q → 0 < β →
    (envelope d q β < 1 / 2 ↔ 1 / (2 * d) < β ∧ β < 1 / (2 * q))
  pointwise_endpoints : ∀ d q β : ℝ, q < d → 0 < q → 0 < β →
    (envelope d q β = 1 / 2 ↔ β = 1 / (2 * d) ∨ β = 1 / (2 * q))
  pointwise_equal : ∀ d q β : ℝ, d = q → 0 < q → 0 < β →
    (envelope d q β = 1 / 2 ↔ β = 1 / (2 * q))
  pointwise_above : ∀ d q β : ℝ, d < q → 0 < q → 0 < β →
    1 / 2 < envelope d q β
  convention_comparison : ∀ m β k : ℝ, 2 ≤ m → 0 < β → 0 ≤ k →
    costAll m β k ≤ costOne m β k ∧
      (costAll m β k = costOne m β k ↔ k ≤ 1 ∨ β ≤ 1 / m)
  optimized_comparison : ∀ m k : ℝ, 2 ≤ m → 0 ≤ k →
    (infF m k = infG m k ↔ k ≤ 1 ∨ m - 1 ≤ k) ∧
      (infF m k < infG m k ↔ 1 < k ∧ k < m - 1)
  equal_unattained : ∀ m k : ℝ, 2 ≤ m → 0 ≤ k → m - 1 < k →
    infF m k = infG m k ∧
      ¬ (∃ β, 0 < β ∧ costAll m β k = infF m k) ∧
      ¬ (∃ β, 0 < β ∧ costOne m β k = infG m k)
  mitm_pointwise : ∀ m β k : ℝ, 2 ≤ m → 0 < β → m / 2 ≤ k →
    1 / 2 < costAll m β k
  mitm_small : ∀ m k : ℝ, 2 ≤ m → m ≤ 4 → m / 2 ≤ k →
    4 / (m + 2) ≤ infF m k
  mitm_large : ∀ m k : ℝ, 4 ≤ m → m / 2 ≤ k →
    m / (2 * (m - 1)) ≤ infF m k
  mitm_one : ∀ m k : ℝ, 2 ≤ m → m / 2 ≤ k →
    1 / 2 + 1 / m ≤ infG m k
  mitm_sharp_small : ∀ m : ℝ, 2 ≤ m → m ≤ 4 →
    infF m (m / 2) = 4 / (m + 2)
  mitm_sharp_large : ∀ m : ℝ, 4 ≤ m →
    infF m (m / 2) = m / (2 * (m - 1))
  mitm_sharp_one : ∀ m : ℝ, 2 ≤ m →
    infG m (m / 2) = 1 / 2 + 1 / m
  no_uniform_gap : ∀ ε : ℝ, 0 < ε → ∃ m k : ℝ,
    4 ≤ m ∧ m / 2 ≤ k ∧ infF m k < 1 / 2 + ε
  failure_F1 : infF 2 2 = 1 ∧ infG 2 2 = 1 ∧
    (∀ β : ℝ, 0 < β → 1 < costAll 2 β 2) ∧
    (∀ β : ℝ, 0 < β → 1 < costOne 2 β 2)
  failure_F2 : (0 : ℝ) / (5 - 1) = 0 ∧ infF 5 0 = 1 / 3 ∧
    costAll 5 (1 / 6) 0 = 1 / 3
  failure_F3 : infF 5 1 = 2 / 5 ∧ costAll 5 1 1 = 2 ∧
    infF 7 2 = 1 / 3 ∧ costAll 7 1 2 = 2
  failure_F4 : infF 3 2 = 1 ∧ infG 3 2 = 1 ∧ costAll 5 (1 / 4) 2 = 1 / 2
  failure_F5 : 2 / ((2 : ℝ) + 1 - 3 / 2) = 4 / 3 ∧ infF 2 (3 / 2) = 1 ∧
    (∀ β : ℝ, 0 < β → 1 < costAll 2 β (3 / 2))
  positives : costAll 5 (1 / 5) 1 = 2 / 5 ∧ costAll 3 (1 / 4) 0 = 1 / 2
  known_false_control : ¬ ∃ β : ℝ, 0 < β ∧ costAll 2 β 2 = infF 2 2

/-- Complete real-domain correction for the two IC oracle envelopes. -/
theorem complete_real_model : CompleteRealModel := by
  constructor
  · intro m β k hm hβ hk
    exact ⟨costAll_eq_envelope m β k hβ hk, costOne_eq_envelope m β k hβ hk⟩
  · intro m k hm hk
    exact dq_positive m k hm
  · intro m k hm hk
    exact cost_infima m k hm hk
  · exact envelope_infimum_pos
  · exact envelope_minimizer_pos
  · exact envelope_infimum_zero
  · exact envelope_minimizer_zero
  · exact envelope_infimum_neg
  · exact envelope_no_minimizer_neg
  · intro d q hq
    exact ⟨envelopeInf_lt_half_iff d q hq, envelopeInf_eq_half_iff d q hq,
      half_lt_envelopeInf_iff d q hq⟩
  · exact envelope_lt_half_iff
  · exact envelope_eq_half_of_d_gt_q
  · exact envelope_eq_half_of_d_eq_q
  · exact envelope_gt_half_of_d_lt_q
  · exact costAll_le_costOne_exact
  · intro m k hm hk
    exact ⟨infF_eq_infG_iff m k hm hk, infF_lt_infG_iff m k hm hk⟩
  · exact optimized_equal_but_unattained
  · exact mitm_never_sub_generic
  · exact mitm_infF_small_bound
  · exact mitm_infF_large_bound
  · exact mitm_infG_bound
  · exact mitm_infF_small_witness
  · exact mitm_infF_large_witness
  · exact mitm_infG_witness
  · exact mitm_no_uniform_positive_gap
  · exact F1_nonattainment
  · exact F2_invalid_middle_bound
  · exact F3_pointwise_not_optimized
  · exact F4_strictness_boundaries
  · exact F5_unrestricted_branch_control
  · exact positive_exact_controls
  · exact blanket_attainment_control

end CryptoResearch.IC.ArityOracleCompleteRealModel
