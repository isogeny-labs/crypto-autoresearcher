/-
  PlantedLeak.lean -- arithmetic behind notes/planted_leak.md (companion to
  IcTensorRoute.ladder_rule; that file is untouched).

  Build:
    cd /Volumes/SSD990-2/crypto-autoresearcher/formal && lake env lean <this file>

  Fact 1.  A group homomorphism ZMod N ->+ ZMod M is trivial when gcd(N, M) = 1.
           So on a cyclic group of PRIME order N, a nonzero "character" into Z/M exists
           only if N divides M, i.e. only a full discrete log mod N.  Any proper
           character (M a proper divisor, or coprime) is zero; there is no nontrivial
           "cheap" sum-compatible filter that is not a discrete-log reduction.
           (The group-order-N = #E(F_p) identification is the note's, not Lean's.)
  Fact 2.  Binary-tree node count: a tree on 2^t leaves has 2^t - 1 internal nodes,
           and 2^(t+1) = 2 * 2^t: the exponent 2^(t+1) counts the 2^t twice.
-/
import Mathlib.Tactic
import Mathlib.Data.ZMod.Basic
import Mathlib.GroupTheory.OrderOfElement

namespace PlantedLeak

/-- A homomorphism from Z/N to Z/M is zero when gcd(N, M) = 1. -/
theorem hom_zero_of_coprime (N M : ℕ) [NeZero N] [NeZero M] (hcop : Nat.Coprime N M)
    (φ : ZMod N →+ ZMod M) : φ = 0 := by
  ext x
  have h1 : N • φ x = 0 := by
    rw [← map_nsmul]
    have : N • x = 0 := by simp
    rw [this, map_zero]
  have h2 : M • φ x = 0 := by
    rw [nsmul_eq_mul]; simp
  have h3 : addOrderOf (φ x) ∣ Nat.gcd N M :=
    Nat.dvd_gcd (addOrderOf_dvd_of_nsmul_eq_zero h1) (addOrderOf_dvd_of_nsmul_eq_zero h2)
  rw [hcop] at h3
  have : addOrderOf (φ x) = 1 := Nat.dvd_one.mp h3
  simpa using this

/-- Prime order N: a nonzero character into Z/M forces N ∣ M (a full dlog mod N). -/
theorem nonzero_char_prime_dvd (N M : ℕ) [NeZero M] (hN : N.Prime)
    (φ : ZMod N →+ ZMod M) (hφ : φ ≠ 0) : N ∣ M := by
  have : NeZero N := ⟨hN.ne_zero⟩
  by_contra hnd
  exact hφ (hom_zero_of_coprime N M ((Nat.Prime.coprime_iff_not_dvd hN).mpr hnd) φ)

/-- A full binary tree on 2^t leaves has 2^t - 1 internal nodes (stated additively). -/
theorem tree_internal_nodes (t : ℕ) : (∑ j ∈ Finset.range t, 2 ^ j) + 1 = 2 ^ t := by
  induction t with
  | zero => simp
  | succ n ih => rw [Finset.sum_range_succ, pow_succ]; omega

/-- The exponent 2^(t+1) is twice the leaf count, i.e. strictly more than the internal
    node count 2^t - 1 plus the 2^t leaves it would be charged against once. -/
theorem double_count_gap (t : ℕ) :
    2 ^ (t + 1) = ((∑ j ∈ Finset.range t, 2 ^ j) + 1) + 2 ^ t := by
  rw [tree_internal_nodes, pow_succ]; ring

end PlantedLeak

#print axioms PlantedLeak.hom_zero_of_coprime
#print axioms PlantedLeak.nonzero_char_prime_dvd
#print axioms PlantedLeak.tree_internal_nodes
#print axioms PlantedLeak.double_count_gap
