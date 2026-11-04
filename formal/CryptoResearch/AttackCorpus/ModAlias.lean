import Mathlib.Data.ZMod.Basic

/-!
Finite-ring boundary for the modular-alias target.

Source: `research/cryptographic_assumption_attack_corpus_20261101/README.md`.
Target: `formal/targets/attack-mod-alias.yaml`.

This module proves only an arithmetic statement about canonical natural-number
representatives in `ZMod q`.  It does not assert that a circuit, compiler, or
serialization layer omitted the range constraints needed to use the repair.
-/

namespace CryptoResearch.AttackCorpus.ModAlias

/-- Natural-number casts into `ZMod q` are injective on the canonical
half-open interval `[0, q)`.

The interval hypotheses are intentionally explicit: they are the exact repair
for the modular alias and are not hidden behind a “well formed” predicate. -/
theorem bounded_natCast_injective {q x y : ℕ}
    (hx : x < q) (hy : y < q)
    (hxy : (x : ZMod q) = (y : ZMod q)) :
    x = y := by
  have hval := congrArg ZMod.val hxy
  simpa [ZMod.val_natCast_of_lt hx, ZMod.val_natCast_of_lt hy] using hval

/-- The sharp natural-number boundary for the alias witness is `0 < q`.

At `q = 1` the naturals `0` and `q` are still distinct and have equal casts,
and the bounded repair remains valid.  Thus the frozen target's `2 ≤ q`
premise is sufficient but is not needed for this elementary statement. -/
theorem modulus_alias_and_positive_bounded_repair (q : ℕ) (hq : 0 < q) :
    (0 : ℕ) ≠ q ∧
      (0 : ZMod q) = (q : ZMod q) ∧
      ∀ x y : ℕ,
        x < q → y < q → (x : ZMod q) = (y : ZMod q) → x = y := by
  have hqne : q ≠ 0 := Nat.ne_of_gt hq
  refine ⟨Ne.symm hqne, (ZMod.natCast_self q).symm, ?_⟩
  intro x y hx hy hxy
  exact bounded_natCast_injective hx hy hxy

/-- At modulus zero, the proposed natural witnesses `0` and `q` coincide, so
the distinct-witness half of the alias counterexample cannot hold. -/
theorem zero_modulus_witness_not_distinct :
    ¬ ((0 : ℕ) ≠ (0 : ℕ)) := by
  simp

/-- The modulus aliases zero in `ZMod q`, even though `0` and `q` are
different natural numbers when `2 ≤ q`; bounded canonical representatives
restore injectivity.

This declaration contains both the counterexample and its conditional repair,
as required by the frozen target. -/
theorem modulus_alias_and_bounded_repair (q : ℕ) (hq : 2 ≤ q) :
    (0 : ℕ) ≠ q ∧
      (0 : ZMod q) = (q : ZMod q) ∧
      ∀ x y : ℕ,
        x < q → y < q → (x : ZMod q) = (y : ZMod q) → x = y :=
  modulus_alias_and_positive_bounded_repair q
    (lt_of_lt_of_le (by decide : 0 < 2) hq)

end CryptoResearch.AttackCorpus.ModAlias
