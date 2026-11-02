/-
Source: research/cryptographic_assumption_attack_corpus_tranche2_20261102/README.md
Target: formal/targets/attack-one-shot-history.yaml

This module separates a one-shot success count from the joint law of repeated
trials.  Two processes on the same two-element sample space have identical
one-shot counts but different two-trial survival events.  The repair assumes a
history-uniform survival recurrence directly and derives its geometric and
finite tail-sum consequences.

No xedni sampler, conditional-probability construction, expectation identity,
height comparison, or Lang-type input is modeled here.
-/
import Mathlib.Algebra.Ring.GeomSum
import Mathlib.Data.Real.Basic
import Mathlib.Data.Set.Card
import Mathlib.Tactic.Ring

set_option autoImplicit false

open scoped BigOperators

namespace CryptoResearch.AttackCorpus.OneShotHistory

/-- Every trial consults the same outcome. -/
def correlatedSuccess (_trial outcome : Bool) : Prop := outcome = true

/-- The two trials succeed on complementary outcomes. -/
def complementarySuccess (trial outcome : Bool) : Prop := trial = outcome

/-- The natural-numbered correlated process has the same persistent outcome. -/
def correlatedNatSuccess (_trial : ℕ) (outcome : Bool) : Prop := outcome = true

theorem correlated_success_card (trial : Bool) :
    ({outcome : Bool | correlatedSuccess trial outcome} : Set Bool).ncard = 1 := by
  have hset :
      ({outcome : Bool | correlatedSuccess trial outcome} : Set Bool) = {true} := by
    ext outcome
    simp [correlatedSuccess]
  rw [hset]
  simp

theorem correlated_two_trial_failure_card :
    ({outcome : Bool |
        ¬ correlatedSuccess false outcome ∧
          ¬ correlatedSuccess true outcome} : Set Bool).ncard = 1 := by
  have hset :
      ({outcome : Bool |
          ¬ correlatedSuccess false outcome ∧
            ¬ correlatedSuccess true outcome} : Set Bool) = {false} := by
    ext outcome
    cases outcome <;> simp [correlatedSuccess]
  rw [hset]
  simp

theorem complementary_success_card (trial : Bool) :
    ({outcome : Bool | complementarySuccess trial outcome} : Set Bool).ncard = 1 := by
  have hset :
      ({outcome : Bool | complementarySuccess trial outcome} : Set Bool) = {trial} := by
    ext outcome
    simp [complementarySuccess, eq_comm]
  rw [hset]
  simp

theorem complementary_two_trial_failure_card :
    ({outcome : Bool |
        ¬ complementarySuccess false outcome ∧
          ¬ complementarySuccess true outcome} : Set Bool).ncard = 0 := by
  have hset :
      ({outcome : Bool |
          ¬ complementarySuccess false outcome ∧
            ¬ complementarySuccess true outcome} : Set Bool) = ∅ := by
    ext outcome
    cases outcome <;> simp [complementarySuccess]
  rw [hset]
  simp

theorem correlated_forever_failure :
    ∃ outcome : Bool, ∀ trial : ℕ, ¬ correlatedNatSuccess trial outcome := by
  exact ⟨false, by simp [correlatedNatSuccess]⟩

/-- A history-uniform upper bound on conditional success is represented by the
division-free survival recurrence
`(1 - epsilon) * S n ≤ S (n + 1)`.

The recurrence, not a marginal one-shot bound, supplies the induction step.
The finite tail inequality is the cross-multiplied geometric-series bound; no
identification of that sum with an expected waiting time is made here. -/
theorem survival_lower_bound_and_finite_tail
    (S : ℕ → ℝ) (epsilon : ℝ)
    (hS0 : S 0 = 1)
    (hepsilon_nonneg : 0 ≤ epsilon)
    (hepsilon_le_one : epsilon ≤ 1)
    (_hS_nonneg : ∀ n, 0 ≤ S n)
    (hstep : ∀ n, (1 - epsilon) * S n ≤ S (n + 1)) :
    (∀ n, (1 - epsilon) ^ n ≤ S n) ∧
      ∀ N, 1 - (1 - epsilon) ^ N ≤
        epsilon * ∑ i ∈ Finset.range N, S i := by
  have hfactor_nonneg : 0 ≤ 1 - epsilon := sub_nonneg.mpr hepsilon_le_one
  have hgeometric : ∀ n, (1 - epsilon) ^ n ≤ S n := by
    intro n
    induction n with
    | zero => simpa [hS0]
    | succ n ih =>
        calc
          (1 - epsilon) ^ (n + 1) =
              (1 - epsilon) * (1 - epsilon) ^ n := by
                rw [pow_succ, mul_comm]
          _ ≤ (1 - epsilon) * S n :=
            mul_le_mul_of_nonneg_left ih hfactor_nonneg
          _ ≤ S (n + 1) := hstep n
  refine ⟨hgeometric, ?_⟩
  intro N
  have hsum :
      (∑ i ∈ Finset.range N, (1 - epsilon) ^ i) ≤
        ∑ i ∈ Finset.range N, S i := by
    induction N with
    | zero => simp
    | succ N ih =>
        simpa only [Finset.sum_range_succ] using
          add_le_add ih (hgeometric N)
  have hscaled := mul_le_mul_of_nonneg_left hsum hepsilon_nonneg
  calc
    1 - (1 - epsilon) ^ N =
        (∑ i ∈ Finset.range N, (1 - epsilon) ^ i) *
          (1 - (1 - epsilon)) := by
            symm
            exact geom_sum_mul_neg (1 - epsilon) N
    _ = epsilon * (∑ i ∈ Finset.range N, (1 - epsilon) ^ i) := by ring
    _ ≤ epsilon * ∑ i ∈ Finset.range N, S i := hscaled

/-- Identical one-shot success counts do not determine repeated-trial history.

The first process retains one failing outcome after both trials and forever;
the second has no outcome that fails both trials.  The final conjunct keeps the
history-uniform recurrence repair in this exact audited declaration. -/
theorem correlated_history_and_hazard_repair :
    (∀ trial : Bool,
      ({outcome : Bool | correlatedSuccess trial outcome} : Set Bool).ncard = 1) ∧
    ({outcome : Bool |
        ¬ correlatedSuccess false outcome ∧
          ¬ correlatedSuccess true outcome} : Set Bool).ncard = 1 ∧
    (∀ trial : Bool,
      ({outcome : Bool | complementarySuccess trial outcome} : Set Bool).ncard = 1) ∧
    ({outcome : Bool |
        ¬ complementarySuccess false outcome ∧
          ¬ complementarySuccess true outcome} : Set Bool).ncard = 0 ∧
    (∃ outcome : Bool, ∀ trial : ℕ,
      ¬ correlatedNatSuccess trial outcome) ∧
    ∀ (S : ℕ → ℝ) (epsilon : ℝ),
      S 0 = 1 →
      0 ≤ epsilon →
      epsilon ≤ 1 →
      (∀ n, 0 ≤ S n) →
      (∀ n, (1 - epsilon) * S n ≤ S (n + 1)) →
      ((∀ n, (1 - epsilon) ^ n ≤ S n) ∧
        ∀ N, 1 - (1 - epsilon) ^ N ≤
          epsilon * ∑ i ∈ Finset.range N, S i) := by
  refine ⟨correlated_success_card, correlated_two_trial_failure_card,
    complementary_success_card, complementary_two_trial_failure_card,
    correlated_forever_failure, ?_⟩
  intro S epsilon hS0 hepsilon_nonneg hepsilon_le_one hS_nonneg hstep
  exact survival_lower_bound_and_finite_tail S epsilon hS0 hepsilon_nonneg
    hepsilon_le_one hS_nonneg hstep

end CryptoResearch.AttackCorpus.OneShotHistory
