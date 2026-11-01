import Mathlib.Algebra.MvPolynomial.Degrees
import Mathlib.Algebra.MvPolynomial.CommRing
import Mathlib.Algebra.BigOperators.Fin

/-!
# Instance-wise recovery of the fake-degree inference (Proposition 6)

Source: `knowledge/findings/KN-FIND-936151.md` section 4 (the recovery rule, there
called `U-3` and `U-4`), stated and proved on paper as Proposition 6 of
`papers/first-fall-lean/paper.tex`.

Lemma 4 of Nagao 2015/984 (`d_F <= d'_F`) is false (`Lemma4Witness.lean`,
`Lemma4Outside.lean`). This module proves the repair: a fake fall gives a true fall
at the same degree when (U-3) the field equations are generators of the true
system and (U-4) every product of the fake witness keeps its degree before
reduction.

## Setting

Mathlib's `MvPolynomial σ R` over any commutative ring `R`, with finitely many
variables. The field equations are `fe j = X j ^ 2 - X j` (over `F_2`, the field
equations of the paper). Reduction `red` clamps every exponent to at most one,
which is reduction modulo the `fe j`. A fall at degree `D` of a finite family of
generators is a cofactor family with every product of total degree `<= D`, one of
degree exactly `D`, and a nonzero sum of total degree `< D` (the equality reading
of condition (1)). A fake fall takes every product and the sum after `red`.

## What is proved

`recovery`: if `g` is a fake fall at degree `v` for generators `fs`, and every
unreduced product `g i * fs i` has total degree `<= v`, then `fs` together with
the field equations has a true fall at degree `v`.

## What is NOT proved

That this `MvPolynomial` setting is the list-of-exponent-vectors model of
`Lemma4Witness.lean`; the fake sum is taken here as `red` of the unreduced sum,
which equals the model's reduction of the sum of reduced products because `red`
is linear and idempotent (not proved here). Nothing about first fall degree as a
minimum beyond the existence of a fall at `v`, the `>=` reading, Proposition 5,
or any elliptic curve.
-/

namespace CryptoResearch.Nagao.RecoveryRule

open MvPolynomial Finset

variable {σ R : Type*} [CommRing R] [DecidableEq σ] [Fintype σ]

/-- Total degree of an exponent vector. -/
def deg (a : σ →₀ ℕ) : ℕ := ∑ i, a i

omit [DecidableEq σ] in
theorem sum_eq_deg (a : σ →₀ ℕ) (g : σ → ℕ → ℕ) (hg : ∀ i n, g i n = n) :
    a.sum g = deg a := by
  rw [Finsupp.sum_fintype _ _ (by intro i; rw [hg])]
  simp [deg, hg]

/-- Clamp every exponent to at most one. -/
noncomputable def clamp (a : σ →₀ ℕ) : σ →₀ ℕ :=
  Finsupp.mapRange (fun n => min n 1) (by simp) a

/-- Reduction modulo the field equations `X j ^ 2 - X j`. -/
noncomputable def red (p : MvPolynomial σ R) : MvPolynomial σ R :=
  ∑ a ∈ p.support, monomial (clamp a) (p.coeff a)

/-- The field equation of variable `j`. -/
noncomputable def fe (j : σ) : MvPolynomial σ R := X j ^ 2 - X j

/-- A fall at degree `D` (equality reading). -/
def IsFall {ι : Type*} [Fintype ι] (fs g : ι → MvPolynomial σ R) (D : ℕ) : Prop :=
  (∀ i, (g i * fs i).totalDegree ≤ D) ∧ (∃ i, (g i * fs i).totalDegree = D) ∧
    (∑ i, g i * fs i) ≠ 0 ∧ (∑ i, g i * fs i).totalDegree < D

/-- A fake fall at degree `D`: products and sum taken after reduction. -/
def IsFakeFall {ι : Type*} [Fintype ι] (fs g : ι → MvPolynomial σ R) (D : ℕ) : Prop :=
  (∀ i, (red (g i * fs i)).totalDegree ≤ D) ∧ (∃ i, (red (g i * fs i)).totalDegree = D) ∧
    red (∑ i, g i * fs i) ≠ 0 ∧ (red (∑ i, g i * fs i)).totalDegree < D

/-- The generators `fs` together with the field equations. -/
noncomputable def withFe {ι : Type*} (fs : ι → MvPolynomial σ R) :
    ι ⊕ σ → MvPolynomial σ R :=
  Sum.elim fs fe

/-! ### Degrees -/

omit [DecidableEq σ] in
theorem deg_clamp_le (a : σ →₀ ℕ) : deg (clamp a) ≤ deg a :=
  Finset.sum_le_sum fun i _ => by simp [clamp]

omit [DecidableEq σ] in
theorem deg_add (a b : σ →₀ ℕ) : deg (a + b) = deg a + deg b := by
  simp [deg, Finset.sum_add_distrib]

theorem deg_single (j : σ) (k : ℕ) : deg (Finsupp.single j k) = k := by
  simp [deg, Finsupp.single_apply]

omit [DecidableEq σ] in
theorem totalDegree_monomial_le' (a : σ →₀ ℕ) (c : R) :
    (monomial a c).totalDegree ≤ deg a := by
  have := totalDegree_monomial_le (R := R) a c
  rwa [sum_eq_deg a (fun _ => id) (fun _ _ => rfl)] at this

omit [DecidableEq σ] in
theorem deg_le_totalDegree {p : MvPolynomial σ R} {a : σ →₀ ℕ} (ha : a ∈ p.support) :
    deg a ≤ p.totalDegree := by
  have := le_totalDegree ha
  rwa [sum_eq_deg a _ (fun _ _ => rfl)] at this

omit [DecidableEq σ] in
theorem totalDegree_red_le (p : MvPolynomial σ R) : (red p).totalDegree ≤ p.totalDegree := by
  unfold red
  refine (totalDegree_finsetSum _ _).trans ?_
  refine Finset.sup_le fun a ha => ?_
  exact (totalDegree_monomial_le' _ _).trans ((deg_clamp_le a).trans (deg_le_totalDegree ha))

/-! ### Combinations of field equations with bounded products -/

/-- Sums `∑ j, h j * fe j` with every product of total degree `≤ D`. -/
noncomputable def feSpan (D : ℕ) : Submodule R (MvPolynomial σ R) where
  carrier := {q | ∃ h : σ → MvPolynomial σ R, q = ∑ j, h j * fe j ∧
    ∀ j, (h j * fe j).totalDegree ≤ D}
  zero_mem' := ⟨0, by simp, fun j => by simp⟩
  add_mem' := by
    rintro q q' ⟨h, rfl, hh⟩ ⟨h', rfl, hh'⟩
    refine ⟨h + h', ?_, fun j => ?_⟩
    · simp [add_mul, Finset.sum_add_distrib]
    · rw [Pi.add_apply, add_mul]
      exact (totalDegree_add _ _).trans (max_le (hh j) (hh' j))
  smul_mem' := by
    rintro c q ⟨h, rfl, hh⟩
    refine ⟨c • h, ?_, fun j => ?_⟩
    · simp [Finset.smul_sum]
    · rw [Pi.smul_apply, smul_mul_assoc]
      exact (totalDegree_smul_le _ _).trans (hh j)

theorem totalDegree_fe_le (j : σ) : (fe j : MvPolynomial σ R).totalDegree ≤ 2 := by
  unfold fe
  rw [X_pow_eq_monomial, X]
  refine (totalDegree_sub _ _).trans (max_le ?_ ?_)
  · exact (totalDegree_monomial_le' _ _).trans (by rw [deg_single])
  · exact (totalDegree_monomial_le' _ _).trans (by rw [deg_single]; omega)

/-- One reduction step: `X^a - X^{clamp a}` lies in `feSpan D` when `deg a ≤ D`. -/
theorem monomial_sub_clamp_mem (D : ℕ) :
    ∀ (n : ℕ) (a : σ →₀ ℕ), deg a = n → deg a ≤ D → ∀ c : R,
      monomial a c - monomial (clamp a) c ∈ (feSpan D : Submodule R (MvPolynomial σ R)) := by
  intro n
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    intro a ha haD c
    by_cases hall : ∀ j, a j ≤ 1
    · have : clamp a = a := by
        ext j
        simp [clamp, hall j]
      rw [this, sub_self]
      exact Submodule.zero_mem _
    · simp only [not_forall, not_le] at hall
      obtain ⟨j, hj⟩ := hall
      set b' := a - Finsupp.single j 2 with hb'
      have hle : Finsupp.single j 2 ≤ a := by
        rw [Finsupp.single_le_iff]
        omega
      have ha_eq : a = b' + Finsupp.single j 2 := (tsub_add_cancel_of_le hle).symm
      set b := b' + Finsupp.single j 1 with hb
      have hdeg_a : deg a = deg b' + 2 := by
        rw [ha_eq, deg_add, deg_single]
      have hdeg_b : deg b = deg b' + 1 := by
        rw [hb, deg_add, deg_single]
      have hclamp : clamp b = clamp a := by
        ext i
        by_cases hi : i = j
        · subst hi
          rw [ha_eq]
          simp [clamp, hb]
        · rw [ha_eq]
          simp [clamp, hb, Ne.symm hi]
      have hstep : monomial a c - monomial b c = monomial b' c * fe j := by
        unfold fe
        rw [mul_sub, X_pow_eq_monomial, X, monomial_mul_monomial, monomial_mul_monomial,
          mul_one, ← ha_eq]
      have hmem1 : monomial a c - monomial b c ∈ (feSpan D : Submodule R (MvPolynomial σ R)) := by
        rw [hstep]
        refine ⟨Pi.single j (monomial b' c), ?_, fun i => ?_⟩
        · rw [Finset.sum_eq_single j]
          · simp
          · intro i _ hi
            simp [hi]
          · simp
        · by_cases hi : i = j
          · subst hi
            simp only [Pi.single_eq_same]
            refine (totalDegree_mul _ _).trans ?_
            have h1 := totalDegree_monomial_le' (R := R) b' c
            have h2 := totalDegree_fe_le (R := R) (σ := σ) i
            omega
          · simp [hi]
      have hmem2 := ih (deg b) (by omega) b rfl (by omega) c
      rw [hclamp] at hmem2
      have := Submodule.add_mem _ hmem1 hmem2
      rwa [sub_add_sub_cancel] at this

/-- `p - red p` is a combination of field equations with products of degree `≤ deg p`. -/
theorem sub_red_mem (p : MvPolynomial σ R) :
    p - red p ∈ (feSpan p.totalDegree : Submodule R (MvPolynomial σ R)) := by
  have hsplit : p - red p =
      ∑ a ∈ p.support, (monomial a (p.coeff a) - monomial (clamp a) (p.coeff a)) := by
    rw [Finset.sum_sub_distrib, ← p.as_sum]
    rfl
  rw [hsplit]
  refine Submodule.sum_mem _ fun a ha => ?_
  exact monomial_sub_clamp_mem _ _ a rfl (deg_le_totalDegree ha) _

/-! ### Proposition 6 -/

/-- **Proposition 6 (instance-wise recovery).** A fake fall at degree `v` whose
unreduced products all have total degree `≤ v` yields a true fall at degree `v` of
the generators together with the field equations. -/
theorem recovery {ι : Type*} [Fintype ι] (fs g : ι → MvPolynomial σ R) (v : ℕ)
    (hfake : IsFakeFall fs g v) (hU4 : ∀ i, (g i * fs i).totalDegree ≤ v) :
    ∃ G : ι ⊕ σ → MvPolynomial σ R, IsFall (withFe fs) G v := by
  obtain ⟨_, ⟨i₀, hi₀⟩, hne, hlt⟩ := hfake
  set s := ∑ i, g i * fs i with hs
  have hsdeg : s.totalDegree ≤ v :=
    (totalDegree_finsetSum _ _).trans (Finset.sup_le fun i _ => hU4 i)
  obtain ⟨h, hsum, hh⟩ := sub_red_mem s
  refine ⟨Sum.elim g (fun j => -h j), ?_⟩
  have hG : ∑ k, Sum.elim g (fun j => -h j) k * withFe fs k = red s := by
    rw [Fintype.sum_sum_type]
    simp only [withFe, Sum.elim_inl, Sum.elim_inr, neg_mul, Finset.sum_neg_distrib]
    rw [← hs, ← hsum]
    ring
  refine ⟨fun k => ?_, ⟨Sum.inl i₀, ?_⟩, ?_, ?_⟩
  · rcases k with i | j
    · exact hU4 i
    · simp only [withFe, Sum.elim_inr, neg_mul, totalDegree_neg]
      exact (hh j).trans hsdeg
  · simp only [withFe, Sum.elim_inl]
    exact le_antisymm (hU4 i₀) (hi₀ ▸ totalDegree_red_le _)
  · rw [hG]; exact hne
  · rw [hG]; exact hlt

end CryptoResearch.Nagao.RecoveryRule
