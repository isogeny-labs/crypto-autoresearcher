import Mathlib.Data.ZMod.Basic
import Mathlib.GroupTheory.OrderOfElement
import Mathlib.Tactic

/-!
# Ambient membership is not designated-subgroup membership

This module checks the smallest product-group countermodel from the frozen
attack-corpus target.  It deliberately models only an ambient finite additive
group and one designated subgroup; it does not model elliptic-curve decoding.
-/

namespace CryptoResearch.AttackCorpus.SubgroupMembership

/-- The transparent ambient group with cofactor two and designated order three. -/
abbrev Ambient := ZMod 2 × ZMod 3

/-- The designated order-three factor. -/
def scalarEmbedding (s : ZMod 3) : Ambient := (0, s)

/-- Membership in the intended subgroup is membership in the image of its
scalar encoding. -/
def designatedSubgroup : Set Ambient := Set.range scalarEmbedding

/-- A valid ambient element in the other direct factor. -/
def outsidePoint : Ambient := (1, 0)

private theorem outsidePoint_order : addOrderOf outsidePoint = 2 := by
  apply (addOrderOf_eq_iff (by decide : 0 < 2)).2
  constructor
  · decide
  · intro m hm hpos
    have hm_one : m = 1 := by omega
    subst m
    simp [outsidePoint]

private theorem nonzero_designated_order (s : ZMod 3)
    (hs : scalarEmbedding s ≠ 0) : addOrderOf (scalarEmbedding s) = 3 := by
  apply (addOrderOf_eq_iff (by decide : 0 < 3)).2
  constructor
  · apply Prod.ext
    · simp [scalarEmbedding]
    · change (3 : ℕ) • s = 0
      rw [nsmul_eq_mul, ZMod.natCast_self, zero_mul]
  · intro m hm hpos
    have hm_cases : m = 1 ∨ m = 2 := by omega
    rcases hm_cases with rfl | rfl
    · simpa only [one_nsmul] using hs
    · intro htwo
      have hs2 : (2 : ℕ) • s = 0 := congrArg Prod.snd htwo
      rw [nsmul_eq_mul] at hs2
      have htwo_ne : (2 : ZMod 3) ≠ 0 := by decide
      have hs_zero : s = 0 := (mul_eq_zero.mp hs2).resolve_left htwo_ne
      apply hs
      ext <;> simp [scalarEmbedding, hs_zero]

/-- Ambient acceptance alone does not imply membership in the designated
order-three subgroup.  Conversely, actual membership supplies a scalar, and
every nonzero member of that image has additive order three. -/
theorem ambient_membership_does_not_imply_designated_subgroup :
    outsidePoint ∉ designatedSubgroup ∧
      addOrderOf outsidePoint = 2 ∧
      ∀ Q : Ambient, Q ∈ designatedSubgroup →
        (∃ s : ZMod 3, Q = scalarEmbedding s) ∧
          (Q ≠ 0 → addOrderOf Q = 3) := by
  refine ⟨?_, outsidePoint_order, ?_⟩
  · rintro ⟨s, hs⟩
    have hfirst : (0 : ZMod 2) = 1 := congrArg Prod.fst hs
    norm_num at hfirst
  · rintro Q ⟨s, rfl⟩
    exact ⟨⟨s, rfl⟩, nonzero_designated_order s⟩

end CryptoResearch.AttackCorpus.SubgroupMembership
