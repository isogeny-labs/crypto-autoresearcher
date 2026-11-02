/-
A residue equality need not identify the natural numbers represented by the
residues.  The bounded repair states the canonical interval explicitly.

Source: research/cryptographic_assumption_attack_corpus_20261101/README.md
Target: formal/targets/attack-mod-alias.yaml
Claim:  ATTACK-MOD-ALIAS-BOUNDED-REPAIR

This is an equality statement about natural casts into ZMod. It contains no
circuit semantics, encoding theorem, or proof-system soundness result.
-/
import Mathlib.Data.ZMod.Basic

namespace CryptoResearch.AttackCorpus.ModAlias

/-- `0` and `q` are distinct natural numbers with the same residue, while
casting becomes injective when both representatives lie in `[0,q)`. -/
theorem modulus_alias_and_bounded_repair (q : ℕ) (hq : 2 ≤ q) :
    (0 : ℕ) ≠ q ∧
      (0 : ZMod q) = (q : ZMod q) ∧
      ∀ x y : ℕ, x < q → y < q →
        (x : ZMod q) = (y : ZMod q) → x = y := by
  have hq0 : 0 < q := lt_of_lt_of_le (by decide : 0 < 2) hq
  have hqne : q ≠ 0 := Nat.ne_of_gt hq0
  haveI : NeZero q := ⟨hqne⟩
  refine ⟨Ne.symm hqne, ?_, ?_⟩
  · exact (ZMod.natCast_self q).symm
  · intro x y hx hy hxy
    have hv : (x : ZMod q).val = (y : ZMod q).val :=
      congrArg (fun z : ZMod q => z.val) hxy
    simpa only [ZMod.val_natCast_of_lt hx, ZMod.val_natCast_of_lt hy] using hv

end CryptoResearch.AttackCorpus.ModAlias
