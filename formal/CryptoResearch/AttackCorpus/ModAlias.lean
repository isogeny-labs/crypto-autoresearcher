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

/-- The modulus aliases zero in `ZMod q`, even though `0` and `q` are
different natural numbers when `2 ≤ q`; bounded canonical representatives
restore injectivity.

This declaration contains both the counterexample and its conditional repair,
as required by the frozen target. -/
theorem modulus_alias_and_bounded_repair (q : ℕ) (hq : 2 ≤ q) :
    (0 : ℕ) ≠ q ∧
      (0 : ZMod q) = (q : ZMod q) ∧
      ∀ x y : ℕ,
        x < q → y < q → (x : ZMod q) = (y : ZMod q) → x = y := by
  refine ⟨by omega, ?_, ?_⟩
  · exact (ZMod.natCast_self q).symm
  · intro x y hx hy hxy
    exact bounded_natCast_injective hx hy hxy

end CryptoResearch.AttackCorpus.ModAlias
