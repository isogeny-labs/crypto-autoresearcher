/-
Source: research/cryptographic_assumption_attack_corpus_20261101/README.md
Target: formal/targets/attack-batch-rlc-adaptive.yaml

This module isolates the challenge-timing boundary in a scalar random-linear-
combination check.  The first theorem permits the alleged errors to depend on
the challenge and gives a cancellation for every challenge.  The repair keeps
`a` and `b` outside the challenge quantifier and counts accepting challenges.

No transcript, group equation, sampler, Fiat--Shamir transform, or protocol
security game is modeled here.
-/
import Mathlib.Algebra.Field.Basic
import Mathlib.Data.Set.Card
import Mathlib.Tactic.Ring

set_option autoImplicit false

namespace CryptoResearch.AttackCorpus.AdaptiveBatching

variable {F : Type*} [Field F]

/-- An error chosen after seeing the challenge. -/
def adaptiveError0 (rho : F) : F := -rho

/-- The second adaptive error is nonzero, independently of the challenge. -/
def adaptiveError1 (_rho : F) : F := 1

/-- Adaptive errors can cancel every random-linear-combination challenge.

The dependency on `rho` is explicit in both errors.  Consequently this theorem
is not an instance of a fixed nonzero polynomial evaluated at a later random
challenge. -/
theorem adaptive_rlc_cancellation :
    ∀ rho : F,
      adaptiveError0 rho + rho * adaptiveError1 rho = 0 ∧
        adaptiveError1 rho ≠ 0 := by
  intro rho
  simp [adaptiveError0, adaptiveError1]

/-- Fixed nonzero errors accept at no more than one field challenge.

The placement of `a` and `b` before the filtered `rho` is the entire timing
model supplied by this theorem.  Uniform sampling would turn this cardinality
bound into probability at most `1 / |F|`; that probability statement is not
part of this target. -/
theorem fixed_error_acceptance_card_le_one [Fintype F] (a b : F)
    (hfixed : ¬ (a = 0 ∧ b = 0)) :
    ({rho : F | a + rho * b = 0} : Set F).ncard ≤ 1 := by
  rw [Set.ncard_le_one_iff_subsingleton]
  intro rho hrho sigma hsigma
  change a + rho * b = 0 at hrho
  change a + sigma * b = 0 at hsigma
  by_cases hb : b = 0
  · have ha : a = 0 := by simpa [hb] using hrho
    exact (hfixed ⟨ha, hb⟩).elim
  · have hdiff : (rho - sigma) * b = 0 := by
      calc
        (rho - sigma) * b = (a + rho * b) - (a + sigma * b) := by ring
        _ = 0 := by rw [hrho, hsigma]; simp
    rcases mul_eq_zero.mp hdiff with hrs | hb'
    · exact sub_eq_zero.mp hrs
    · exact (hb hb').elim

end CryptoResearch.AttackCorpus.AdaptiveBatching
