import CryptoResearch.Binstd.Factorization
import Mathlib.Tactic

/-!
Decode the archived BINSTD bitmasks as polynomials over `ZMod 2`.  The
coefficient of `X^i` is bit `i`, with a fixed 18-bit bound covering the
degree-17 field modulus.  This identifies the concrete archived encodings
with the polynomial statements used by the existing factor proofs.  It does
not by itself prove the bitmask remainder algorithm agrees with polynomial
division or that the archived field construction is a field.
-/

namespace CryptoResearch.Binstd

open Polynomial

/-- Decode at most `fuel` low bits of a natural-number polynomial mask. -/
noncomputable def decodeMask : Nat → Nat → F2[X]
  | 0, _ => 0
  | fuel + 1, mask =>
      C ((mask % 2 : Nat) : F2) + X * decodeMask fuel (mask / 2)

/-- The exact archived modulus mask denotes `X^17 + X^3 + 1`. -/
theorem decode_modulus17 :
    decodeMask 18 131081 = X ^ 17 + X ^ 3 + 1 := by
  norm_num [decodeMask]
  ring

/-- The three archived factor masks denote the factors in the source-bound product. -/
theorem decode_factor_masks :
    decodeMask 18 3 = factor1 ∧
    decodeMask 18 313 = factor8a ∧
    decodeMask 18 471 = factor8b := by
  constructor
  · unfold factor1
    norm_num [decodeMask]
    ring
  constructor
  · unfold factor8a
    norm_num [decodeMask]
    ring
  · unfold factor8b
    norm_num [decodeMask]
    ring

/-- Nearby encoded-remainder controls decode to different polynomials. -/
theorem decode_reducible_controls :
    decodeMask 18 131073 = X ^ 17 + 1 ∧
    decodeMask 18 257 = X ^ 8 + 1 := by
  constructor
  · norm_num [decodeMask]
    ring
  · norm_num [decodeMask]
    ring

end CryptoResearch.Binstd
