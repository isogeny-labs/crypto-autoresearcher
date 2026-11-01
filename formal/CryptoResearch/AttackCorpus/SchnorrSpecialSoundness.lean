/-
Scalar controls for Schnorr two-transcript extraction.

Source: `research/cryptographic_assumption_attack_corpus_20261101/README.md`.
Target: `formal/targets/attack-schnorr-special-soundness.yaml`.

This module proves only the scalar identity obtained after two accepting
transcripts have already been reduced to equations in the same prime field.
It does not construct forks, model a transcript parser or random oracle, or
prove proof-of-knowledge security.
-/
import Mathlib.Algebra.Field.ZMod
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

namespace CryptoResearch.AttackCorpus.SchnorrSpecialSoundness

/-- Two scalar transcript equations with the same commitment and distinct
challenges determine the witness over a prime field.  The unit conclusion
makes the division premise visible rather than hiding it in notation. -/
theorem extract_of_distinct_challenges
    {q : ℕ} [Fact q.Prime]
    (r s1 s2 c1 c2 x : ZMod q)
    (h1 : s1 = r + c1 * x)
    (h2 : s2 = r + c2 * x)
    (hc : c1 ≠ c2) :
    IsUnit (c1 - c2) ∧ x = (s1 - s2) / (c1 - c2) := by
  have hdiff : c1 - c2 ≠ 0 := sub_ne_zero.mpr hc
  have hunit : IsUnit (c1 - c2) := isUnit_iff_ne_zero.mpr hdiff
  refine ⟨hunit, ?_⟩
  symm
  apply (div_eq_iff hdiff).2
  calc
    s1 - s2 = (c1 - c2) * x := by rw [h1, h2]; ring
    _ = x * (c1 - c2) := mul_comm _ _

/-- With challenge zero, the same commitment and response accept two distinct
witness values.  Thus equal challenges supply no extraction equation. -/
theorem equal_zero_challenge_nonunique {F : Type*} [Field F] :
    ∃ (x y r s1 s2 : F), x ≠ y ∧
      s1 = r + 0 * x ∧ s2 = r + 0 * x ∧
      s1 = r + 0 * y ∧ s2 = r + 0 * y := by
  refine ⟨0, 1, 0, 0, 0, zero_ne_one, ?_, ?_, ?_, ?_⟩ <;> simp

/-- Distinct challenges are insufficient over a composite scalar ring.
In `ZMod 4`, challenges `2` and `0` differ by the nonunit `2`; with zero
commitment and responses, both witnesses `0` and `2` satisfy both equations. -/
theorem zmod_four_distinct_challenges_nonunique :
    let r : ZMod 4 := 0
    let s1 : ZMod 4 := 0
    let s2 : ZMod 4 := 0
    let c1 : ZMod 4 := 2
    let c2 : ZMod 4 := 0
    c1 ≠ c2 ∧ ¬ IsUnit (c1 - c2) ∧
      s1 = r + c1 * 0 ∧ s2 = r + c2 * 0 ∧
      s1 = r + c1 * 2 ∧ s2 = r + c2 * 2 := by
  dsimp
  refine ⟨by decide, ?_, by norm_num, by norm_num, ?_, by norm_num⟩
  · rw [sub_zero]
    change ¬ IsUnit ((2 : ℕ) : ZMod 4)
    rw [ZMod.isUnit_iff_coprime]
    decide
  · calc
      (0 : ZMod 4) = 4 := (ZMod.natCast_self 4).symm
      _ = 0 + 2 * 2 := by norm_num

end CryptoResearch.AttackCorpus.SchnorrSpecialSoundness
