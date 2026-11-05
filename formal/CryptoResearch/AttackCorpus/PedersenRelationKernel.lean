/-
The algebraic relation kernel in a two-generator Pedersen commitment.

Source:
`research/cryptographic_assumption_attack_corpus_tranche2_20261102/README.md`.
Target: `formal/targets/attack-pedersen-relation-kernel.yaml`.

Pedersen's primary theorem assumes that the discrete-log relation between the
two generators is unknown and shows that a different-message collision reveals
that relation.  This module formalizes exactly that algebraic boundary.  It
does not model an adversary, computational binding, DLP hardness, generator
derivation, subgroup decoding, or commitment serialization.
-/
import Mathlib.Algebra.Field.ZMod
import Mathlib.Algebra.Module.LinearMap.Basic
import Mathlib.Algebra.Module.Prod
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Module
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

set_option autoImplicit false

namespace CryptoResearch.AttackCorpus.PedersenRelationKernel

variable {F V : Type*} [Field F] [AddCommGroup V] [Module F V]

/-- The additive form of a two-generator Pedersen commitment. -/
def commitmentMap (G H : V) : (F × F) →ₗ[F] V where
  toFun z := z.1 • G + z.2 • H
  map_add' x y := by
    dsimp
    module
  map_smul' c x := by
    dsimp
    module

/-- Pointwise notation for the commitment map. -/
def commit (G H : V) (m r : F) : V := commitmentMap G H (m, r)

@[simp]
theorem commitmentMap_apply (G H : V) (z : F × F) :
    commitmentMap G H z = z.1 • G + z.2 • H := rfl

@[simp]
theorem commit_apply (G H : V) (m r : F) :
    commit G H m r = m • G + r • H := rfl

/-- Once `H = alpha • G`, a commitment is the scalar
`m + r * alpha` applied to `G`. -/
private theorem commit_eq_single_smul
    (G H : V) (alpha m r : F) (hH : H = alpha • G) :
    commit G H m r = (m + r * alpha) • G := by
  simp [commit, hH, add_smul, smul_smul]

/-- The complete kernel equation, conditional on faithful scalar encoding by
`G`.  This is the exact-order-generator premise in abstract form. -/
theorem mem_kernel_iff
    (G H : V) (alpha : F)
    (hH : H = alpha • G)
    (hG : Function.Injective (fun a : F => a • G))
    (z : F × F) :
    z ∈ LinearMap.ker (commitmentMap G H) ↔ z.1 + z.2 * alpha = 0 := by
  rw [LinearMap.mem_ker]
  rw [show commitmentMap G H z = (z.1 + z.2 * alpha) • G by
    simpa [commit] using commit_eq_single_smul G H alpha z.1 z.2 hH]
  constructor
  · intro hz
    apply hG
    simpa using hz
  · intro hz
    simp [hz]

/-- Knowledge of a nonzero relation permits changing an opening to any chosen
message.  The new blinder is the usual Pedersen equivocation formula. -/
theorem equivocate_to_message
    (G H : V) (alpha : F) (hH : H = alpha • G) (hAlpha : alpha ≠ 0)
    (m r m' : F) :
    commit G H m r = commit G H m' (r + (m - m') / alpha) := by
  rw [commit_eq_single_smul G H alpha m r hH,
    commit_eq_single_smul G H alpha m' (r + (m - m') / alpha) hH]
  congr 1
  field_simp [hAlpha]
  <;> ring

/-- Conversely, two openings with different messages have different blinders
and reveal the generator relation.  This is the algebraic reduction in
Pedersen's Theorem 3.1, not a computational binding theorem. -/
theorem collision_recovers_relation
    (G H : V) (alpha : F)
    (hH : H = alpha • G)
    (hG : Function.Injective (fun a : F => a • G))
    (m r m' r' : F) (hm : m ≠ m')
    (hcollision : commit G H m r = commit G H m' r') :
    r' ≠ r ∧ alpha = (m - m') / (r' - r) := by
  have hexponents : m + r * alpha = m' + r' * alpha := by
    apply hG
    calc
      (m + r * alpha) • G = commit G H m r :=
        (commit_eq_single_smul G H alpha m r hH).symm
      _ = commit G H m' r' := hcollision
      _ = (m' + r' * alpha) • G := commit_eq_single_smul G H alpha m' r' hH
  have hr : r' ≠ r := by
    intro hrr
    apply hm
    rw [hrr] at hexponents
    exact add_right_cancel hexponents
  refine ⟨hr, ?_⟩
  apply (eq_div_iff (sub_ne_zero.mpr hr)).2
  calc
    alpha * (r' - r) = r' * alpha - r * alpha := by ring
    _ = m - m' := by linear_combination -hexponents

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩

/-- A concrete nonvacuity control: over `ZMod 5`, `G = 1`, `H = 2`, and
`alpha = 2`, the distinct openings `(0,0)` and `(2,4)` both commit to zero. -/
def concreteZModFiveControl : Prop :=
  let G : ZMod 5 := 1
  let H : ZMod 5 := 2
  let alpha : ZMod 5 := 2
  alpha ≠ 0 ∧ H = alpha • G ∧
    ((0, 0) : ZMod 5 × ZMod 5) ≠ (2, 4) ∧
    commitmentMap G H ((0, 0) : ZMod 5 × ZMod 5) =
      commitmentMap G H ((2, 4) : ZMod 5 × ZMod 5)

theorem concrete_zmod_five_control : concreteZModFiveControl := by
  norm_num [concreteZModFiveControl, commitmentMap] <;> decide

/-- A known relation gives a nonzero kernel vector and arbitrary-message
alternate openings; faithful scalar encoding characterizes the entire kernel,
and a different-message collision recovers the relation.  The final conjunct
keeps a concrete finite control in the exact audited declaration.

This theorem says nothing about whether an outsider can compute `alpha`.
Computational binding requires an adversary/game reduction to DLP outside this
algebraic target. -/
theorem known_relation_kernel_and_alternate_openings
    (G H : V) (alpha : F) (hAlpha : alpha ≠ 0)
    (hH : H = alpha • G)
    (hG : Function.Injective (fun a : F => a • G)) :
    ((alpha, -1) : F × F) ≠ 0 ∧
      (alpha, -1) ∈ LinearMap.ker (commitmentMap G H) ∧
      (∀ z : F × F,
        z ∈ LinearMap.ker (commitmentMap G H) ↔ z.1 + z.2 * alpha = 0) ∧
      (∀ m r m' : F,
        commit G H m r = commit G H m' (r + (m - m') / alpha)) ∧
      (∀ m r m' r' : F, m ≠ m' →
        commit G H m r = commit G H m' r' →
          r' ≠ r ∧ alpha = (m - m') / (r' - r)) ∧
      concreteZModFiveControl := by
  refine ⟨?_, ?_, ?_, ?_, ?_, concrete_zmod_five_control⟩
  · intro hzero
    have halpha : alpha = 0 := congrArg Prod.fst hzero
    exact hAlpha halpha
  · exact (mem_kernel_iff G H alpha hH hG (alpha, -1)).2 (by ring)
  · exact fun z => mem_kernel_iff G H alpha hH hG z
  · exact fun m r m' => equivocate_to_message G H alpha hH hAlpha m r m'
  · intro m r m' r' hm hcollision
    exact collision_recovers_relation G H alpha hH hG m r m' r' hm hcollision

end CryptoResearch.AttackCorpus.PedersenRelationKernel
