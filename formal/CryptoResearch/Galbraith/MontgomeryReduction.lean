/-
The integer core of Galbraith, Mathematics of Public Key Cryptography v2,
Lemma 2.5.3 (Montgomery reduction).

Source and statement-fidelity boundary:
  research/galbraith_mpkc_formalization_20261101/theory.md
Target:
  formal/targets/galbraith-montgomery-reduction-20261101.yaml

WHAT IS PROVED. Explicit congruence witnesses imply that `a + u*n` is an
integer multiple `R*w`; canonical representative bounds imply `0 <= w < n`;
and `R*w` is congruent to `a` modulo `n`.

WHAT IS NOT PROVED. The existence or computation of the modular inverse, the
power-of-two implementation, constant-time behavior, or any complexity claim.
The final congruence is in multiplication form; the source's inverse form is
equivalent under its original odd-`n`, power-of-two-`R` assumptions.
-/
import Mathlib.Tactic

namespace CryptoResearch.Galbraith

/-- The integer/divisibility core of Montgomery reduction (Galbraith v2,
Lemma 2.5.3).

`hnegInv` is the witness form of `n * n' = -1 (mod R)`, and `hu` is the
witness form of `u = a * n' (mod R)`. -/
theorem montgomery_reduction
    {n R n' a u : Int}
    (hnpos : 0 < n)
    (hnR : n < R)
    (ha0 : 0 <= a)
    (han : a < n)
    (hu0 : 0 <= u)
    (huR : u < R)
    (hnegInv : Exists fun k : Int => n * n' + 1 = k * R)
    (hu : Exists fun ell : Int => u = a * n' + ell * R) :
    Exists fun w : Int =>
      a + u * n = R * w /\
      0 <= w /\
      w < n /\
      n ∣ R * w - a := by
  rcases hnegInv with ⟨k, hk⟩
  rcases hu with ⟨ell, hell⟩
  let w : Int := a * k + ell * n
  have hRw : a + u * n = R * w := by
    dsimp [w]
    calc
      a + u * n = a + (a * n' + ell * R) * n := by rw [hell]
      _ = a * (n * n' + 1) + ell * n * R := by ring
      _ = a * (k * R) + ell * n * R := by rw [hk]
      _ = R * (a * k + ell * n) := by ring
  have hRpos : 0 < R := lt_trans hnpos hnR
  have hunonneg : 0 <= u * n := mul_nonneg hu0 (le_of_lt hnpos)
  have hsumnonneg : 0 <= a + u * n := add_nonneg ha0 hunonneg
  have hw0 : 0 <= w := by
    by_contra hw
    have hwneg : w < 0 := lt_of_not_ge hw
    have hprodneg : R * w < 0 := mul_neg_of_pos_of_neg hRpos hwneg
    rw [← hRw] at hprodneg
    exact (not_lt_of_ge hsumnonneg) hprodneg
  have hale : a <= n - 1 := by omega
  have hule : u <= R - 1 := by omega
  have humul : u * n <= (R - 1) * n :=
    mul_le_mul_of_nonneg_right hule (le_of_lt hnpos)
  have hsumlt : a + u * n < R * n := by
    nlinarith [add_le_add hale humul]
  have hwn : w < n := by
    by_contra hwnot
    have hnle : n <= w := le_of_not_gt hwnot
    have hmul : R * n <= R * w :=
      mul_le_mul_of_nonneg_left hnle (le_of_lt hRpos)
    rw [← hRw] at hmul
    exact (not_le_of_gt hsumlt) hmul
  refine ⟨w, hRw, hw0, hwn, ?_⟩
  refine ⟨u, ?_⟩
  rw [← hRw]
  ring

end CryptoResearch.Galbraith
