import Mathlib.Data.Fintype.Card
import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic

/-!
# Cofactor clearing needs a decomposition and an invertible target action

This module separates three finite statements that are often conflated:

* a scalar can collapse both factors when it shares a divisor with the
  intended subgroup order;
* in the product `ZMod 2 × ZMod 3`, multiplication by two has exactly two
  preimages above every point of the second factor; and
* the corresponding constant-fibre statement holds for an arbitrary supplied
  product `K × S` only when the scalar annihilates `K` and permutes `S`.

Equal finite fibre counts are the exact pushforward statement here.  Nothing
in this file constructs an elliptic-curve decomposition or proves uniformity
of a concrete hash-to-curve encoder.
-/

namespace CryptoResearch.AttackCorpus.CofactorPushforward

/-- The number of inputs mapping to a specified output. -/
def fiberCount {A B : Type*} [Fintype A] [DecidableEq B]
    (f : A → B) (y : B) : ℕ :=
  (Finset.univ.filter fun x => f x = y).card

/-- Multiplication by the candidate clearing scalar on a supplied product. -/
def productClear {K S : Type*} [AddMonoid K] [AddMonoid S]
    (h : ℕ) (P : K × S) : K × S :=
  h • P

/-- The intended copy of the target factor inside the supplied product. -/
def productTarget {K S : Type*} [Zero K] (s : S) : K × S :=
  (0, s)

private noncomputable def productFiberEquiv
    {K S : Type*} [AddCommGroup K] [AddCommGroup S]
    (h : ℕ) (hkill : ∀ k : K, h • k = 0)
    (hperm : Function.Bijective fun s : S => h • s) (t : S) :
    {P : K × S // productClear h P = productTarget t} ≃ K := by
  let e : S ≃ S := Equiv.ofBijective (fun s : S => h • s) hperm
  refine
    { toFun := fun P => P.1.1
      invFun := fun k => ⟨(k, e.symm t), ?_⟩
      left_inv := ?_
      right_inv := ?_ }
  · apply Prod.ext
    · exact hkill k
    · exact e.apply_symm_apply t
  · rintro ⟨⟨k, s⟩, hs⟩
    apply Subtype.ext
    apply Prod.ext
    · rfl
    · apply e.injective
      rw [e.apply_symm_apply]
      exact (congrArg Prod.snd hs).symm
  · intro k
    rfl

/-- Under the explicit product hypotheses, multiplication by `h` has image
exactly the supplied target factor, every target has `|K|` preimages, and the
cross-multiplied uniform-pushforward identity is exact. -/
theorem product_image_and_fiber_repair
    {K S : Type*} [AddCommGroup K] [AddCommGroup S]
    [Fintype K] [Fintype S] [DecidableEq K] [DecidableEq S]
    (h : ℕ) (hkill : ∀ k : K, h • k = 0)
    (hperm : Function.Bijective fun s : S => h • s) :
    Set.range (productClear (K := K) (S := S) h) =
        Set.range (productTarget (K := K) (S := S)) ∧
      (∀ t : S,
        fiberCount (productClear (K := K) (S := S) h) (productTarget t) =
          Fintype.card K) ∧
      (∀ t : S,
        fiberCount (productClear (K := K) (S := S) h) (productTarget t) *
            Fintype.card S =
          Fintype.card (K × S)) := by
  have himage :
      Set.range (productClear (K := K) (S := S) h) =
        Set.range (productTarget (K := K) (S := S)) := by
    apply Set.Subset.antisymm
    · rintro _ ⟨⟨k, s⟩, rfl⟩
      refine ⟨h • s, ?_⟩
      apply Prod.ext
      · exact (hkill k).symm
      · rfl
    · rintro _ ⟨s, rfl⟩
      let e : S ≃ S := Equiv.ofBijective (fun x : S => h • x) hperm
      refine ⟨(0, e.symm s), ?_⟩
      apply Prod.ext
      · exact hkill 0
      · exact e.apply_symm_apply s
  have hfiber : ∀ t : S,
      fiberCount (productClear (K := K) (S := S) h) (productTarget t) =
        Fintype.card K := by
    intro t
    rw [fiberCount, ← Fintype.card_subtype]
    exact Fintype.card_congr (productFiberEquiv h hkill hperm t)
  refine ⟨himage, hfiber, ?_⟩
  intro t
  rw [hfiber t, Fintype.card_prod]

/-- The bad control: the candidate scalar shares a factor with both product
components and therefore collapses the entire ambient group. -/
abbrev BadAmbient := ZMod 2 × ZMod 2

def badClear (P : BadAmbient) : BadAmbient :=
  (2 : ℕ) • P

/-- The good finite control: two kills the first factor and permutes the
order-three target factor. -/
abbrev GoodAmbient := ZMod 2 × ZMod 3

def goodClear (P : GoodAmbient) : GoodAmbient :=
  (2 : ℕ) • P

def goodTarget (s : ZMod 3) : GoodAmbient :=
  (0, s)

private theorem badClear_eq_zero (P : BadAmbient) : badClear P = 0 := by
  apply Prod.ext
  · change (2 : ℕ) • P.1 = 0
    rw [nsmul_eq_mul, ZMod.natCast_self, zero_mul]
  · change (2 : ℕ) • P.2 = 0
    rw [nsmul_eq_mul, ZMod.natCast_self, zero_mul]

private theorem two_annihilates_zmod_two (k : ZMod 2) : (2 : ℕ) • k = 0 := by
  rw [nsmul_eq_mul, ZMod.natCast_self, zero_mul]

private theorem two_permutes_zmod_three :
    Function.Bijective (fun s : ZMod 3 => (2 : ℕ) • s) := by
  constructor
  · intro a b hab
    change (2 : ℕ) • a = (2 : ℕ) • b at hab
    have hab' :
        ((2 : ℕ) : ZMod 3) * a = ((2 : ℕ) : ZMod 3) * b := by
      simpa only [nsmul_eq_mul] using hab
    exact mul_left_cancel₀ (by decide : ((2 : ℕ) : ZMod 3) ≠ 0) hab'
  · intro t
    refine ⟨(2 : ℕ) • t, ?_⟩
    simp only [nsmul_eq_mul]
    rw [← mul_assoc]
    have htwo_sq :
        ((2 : ℕ) : ZMod 3) * ((2 : ℕ) : ZMod 3) = 1 := by decide
    rw [htwo_sq, one_mul]

/-- The exact audited declaration contains both failure controls and the
generic repair.  Thus checking this name cannot silently verify only the
convenient counterexample or only the conditional theorem. -/
theorem cofactor_failure_and_product_fiber_repair
    {K S : Type*} [AddCommGroup K] [AddCommGroup S]
    [Fintype K] [Fintype S] [DecidableEq K] [DecidableEq S]
    (h : ℕ) (hkill : ∀ k : K, h • k = 0)
    (hperm : Function.Bijective fun s : S => h • s) :
    ((∀ P : BadAmbient, badClear P = 0) ∧
      fiberCount badClear (0, 0) = 4 ∧
      fiberCount badClear (0, 1) = 0) ∧
    (Set.range goodClear = Set.range goodTarget ∧
      (∀ t : ZMod 3, fiberCount goodClear (goodTarget t) = 2) ∧
      (∀ t : ZMod 3,
        fiberCount goodClear (goodTarget t) * Fintype.card (ZMod 3) =
          Fintype.card GoodAmbient)) ∧
    (Set.range (productClear (K := K) (S := S) h) =
        Set.range (productTarget (K := K) (S := S)) ∧
      (∀ t : S,
        fiberCount (productClear (K := K) (S := S) h) (productTarget t) =
          Fintype.card K) ∧
      (∀ t : S,
        fiberCount (productClear (K := K) (S := S) h) (productTarget t) *
            Fintype.card S =
          Fintype.card (K × S))) := by
  have hbad :
      (∀ P : BadAmbient, badClear P = 0) ∧
        fiberCount badClear (0, 0) = 4 ∧
        fiberCount badClear (0, 1) = 0 := by
    refine ⟨badClear_eq_zero, ?_, ?_⟩
    · rw [fiberCount]
      have hall :
          Finset.univ.filter (fun P : BadAmbient => badClear P = (0, 0)) =
            Finset.univ := by
        apply Finset.filter_eq_self.2
        intro P _
        rw [badClear_eq_zero]
        rfl
      rw [hall, Finset.card_univ, Fintype.card_prod, ZMod.card]
    · rw [fiberCount]
      have hempty :
          Finset.univ.filter (fun P : BadAmbient => badClear P = (0, 1)) =
            ∅ := by
        apply Finset.filter_eq_empty_iff.2
        intro P _
        rw [badClear_eq_zero]
        intro hzero
        have hone : (0 : ZMod 2) = 1 := congrArg Prod.snd hzero
        norm_num at hone
      rw [hempty, Finset.card_empty]
  have hgood_raw := product_image_and_fiber_repair
    (K := ZMod 2) (S := ZMod 3) 2 two_annihilates_zmod_two two_permutes_zmod_three
  have hclear :
      goodClear = productClear (K := ZMod 2) (S := ZMod 3) 2 := by
    funext P
    rfl
  have htarget :
      goodTarget = productTarget (K := ZMod 2) (S := ZMod 3) := by
    funext t
    rfl
  have hgood :
      Set.range goodClear = Set.range goodTarget ∧
        (∀ t : ZMod 3, fiberCount goodClear (goodTarget t) = 2) ∧
        (∀ t : ZMod 3,
          fiberCount goodClear (goodTarget t) * Fintype.card (ZMod 3) =
            Fintype.card GoodAmbient) := by
    rw [hclear, htarget]
    simpa only [ZMod.card] using hgood_raw
  have hgeneric := product_image_and_fiber_repair h hkill hperm
  exact And.intro hbad (And.intro hgood hgeneric)

end CryptoResearch.AttackCorpus.CofactorPushforward
