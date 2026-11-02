/-
Adaptive cancellation and the fixed-error cardinality repair for a scalar
random linear combination.  This theorem has no transcript, commitment,
sampling, or protocol-security semantics.

Source: research/cryptographic_assumption_attack_corpus_20261101/README.md
Target: formal/targets/attack-batch-rlc-adaptive.yaml
Claim:  ATTACK-BATCH-RLC-ADAPTIVE-CANCELLATION
-/
import Mathlib.Algebra.Field.Basic
import Mathlib.Data.Finset.Card

namespace CryptoResearch.AttackCorpus.AdaptiveBatching

universe u

/-- Challenge-dependent errors always cancel. For errors fixed before the
challenge, a nonzero pair has at most one cancelling challenge in a finite
field. The quantifier order keeps these two timing models separate. -/
theorem adaptive_rlc_cancellation :
    (∀ (F : Type u) [Field F] (ρ : F),
      (-ρ) + ρ * (1 : F) = 0 ∧ (1 : F) ≠ 0) ∧
    (∀ (F : Type u) [Field F] [Fintype F] (a b : F),
      ¬ (a = 0 ∧ b = 0) →
        (Finset.univ.filter (fun ρ : F => a + ρ * b = 0)).card ≤ 1) := by
  constructor
  · intro F _ ρ
    simp
  · intro F _ _ a b hab
    classical
    apply Finset.card_le_one.mpr
    intro ρ hρ σ hσ
    simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hρ hσ
    by_cases hb : b = 0
    · have ha : a = 0 := by simpa [hb] using hρ
      exact (hab ⟨ha, hb⟩).elim
    · have hmul : ρ * b = σ * b :=
        add_left_cancel (hρ.trans hσ.symm)
      have hsub : (ρ - σ) * b = 0 := by
        rw [sub_mul, hmul, sub_self]
      rcases mul_eq_zero.mp hsub with hdiff | hbzero
      · exact sub_eq_zero.mp hdiff
      · exact (hb hbzero).elim

end CryptoResearch.AttackCorpus.AdaptiveBatching
