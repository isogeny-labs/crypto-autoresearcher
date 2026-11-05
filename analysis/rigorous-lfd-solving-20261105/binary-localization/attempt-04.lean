import CryptoResearch.FallDegree.BooleanNormalization

namespace CryptoResearch.FallDegree
namespace BinaryLocalization

open MvPolynomial
open scoped BigOperators

variable {β τ k : Type*} [Field k] [DecidableEq β]

noncomputable def baseExponent (T : Finset β) : (β ⊕ τ) →₀ ℕ :=
  ∑ i ∈ T, Finsupp.single (Sum.inl i) 1

noncomputable def auxExponent : Option τ → (β ⊕ τ) →₀ ℕ
  | none => 0
  | some j => Finsupp.single (Sum.inr j) 1

noncomputable def basisExponent (T : Finset β) (j : Option τ) : (β ⊕ τ) →₀ ℕ :=
  baseExponent T + auxExponent j

noncomputable def basisMonomial (T : Finset β) (j : Option τ) : MvPolynomial (β ⊕ τ) k :=
  monomial (basisExponent T j) 1

@[simp] theorem baseExponent_inl (T : Finset β) (i : β) :
    (baseExponent (τ := τ) T) (Sum.inl i) = if i ∈ T then 1 else 0 := by
  classical
  simp [baseExponent, Finsupp.finsetSum_apply, Finsupp.single_apply, eq_comm]

@[simp] theorem baseExponent_inr (T : Finset β) (j : τ) :
    (baseExponent T) (Sum.inr j) = 0 := by
  classical
  simp [baseExponent, Finsupp.finsetSum_apply, Finsupp.single_apply]

@[simp] theorem booleanExponent_basis (T : Finset β) (j : Option τ) :
    booleanExponent (basisExponent T j) = basisExponent T j := by
  classical
  ext x
  rcases x with i | i <;> cases j <;>
    simp [basisExponent, auxExponent, Finsupp.single_apply]
  all_goals split_ifs <;> simp_all

@[simp] theorem booleanNF_basis (T : Finset β) (j : Option τ) :
    booleanNF (basisMonomial (k := k) T j) = basisMonomial T j := by
  simp [basisMonomial]

theorem wt_baseExponent (T : Finset β) : wt (baseExponent (τ := τ) T) = T.card := by
  classical
  induction T using Finset.induction_on with
  | empty => simp [baseExponent, wt_zero]
  | @insert i T hi ih =>
    rw [baseExponent, Finset.sum_insert hi, wt_single_add]
    rw [Finset.card_insert_of_notMem hi]
    change 1 + wt (baseExponent (τ := τ) T) = T.card + 1
    omega

theorem basisMonomial_degree (T : Finset β) (j : Option τ) :
    (basisMonomial (k := k) T j).totalDegree ≤ T.card + 1 := by
  rw [basisMonomial, totalDegree_monomial_one]
  cases j with
  | none => simp [basisExponent, auxExponent, wt_baseExponent]
  | some j =>
    rw [basisExponent, auxExponent, add_comm, wt_single_add, wt_baseExponent]
    omega

theorem capped_basis_add_base (T : Finset β) (j : Option τ) (i : β) :
    booleanExponent (basisExponent T j + Finsupp.single (Sum.inl i) 1) =
      basisExponent (insert i T) j := by
  classical
  ext x
  rcases x with b | u
  · by_cases hbi : b = i <;> by_cases hbT : b ∈ T <;> cases j <;>
      simp [basisExponent, auxExponent, Finsupp.single_apply, hbi, eq_comm, hbT]
  · cases j <;> simp [basisExponent, auxExponent, Finsupp.single_apply]
    split_ifs <;> simp_all

@[simp] theorem booleanNF_basis_mul_base (T : Finset β) (j : Option τ) (i : β) :
    booleanNF (basisMonomial (k := k) T j * X (Sum.inl i)) =
      basisMonomial (insert i T) j := by
  change booleanNF (monomial (basisExponent T j) (1 : k) *
    monomial (Finsupp.single (Sum.inl i) 1) 1) = _
  simp [basisMonomial, capped_basis_add_base]

/-- Exact span of multilinear monomials supported on `A` in the base block,
and with at most one variable from the entire auxiliary block. -/
noncomputable def localAffine (A : Finset β) : Submodule k (MvPolynomial (β ⊕ τ) k) :=
  Submodule.span k {p | ∃ T : Finset β, T ⊆ A ∧ ∃ j : Option τ, p = basisMonomial T j}

theorem basis_mem_localAffine {A T : Finset β} (hT : T ⊆ A) (j : Option τ) :
    basisMonomial (k := k) T j ∈ localAffine (τ := τ) A :=
  Submodule.subset_span ⟨T, hT, j, rfl⟩

theorem localAffine_degree {A : Finset β} {p : MvPolynomial (β ⊕ τ) k}
    (hp : p ∈ localAffine A) : p.totalDegree ≤ A.card + 1 := by
  have hle : localAffine (τ := τ) (k := k) A ≤ restrictTotalDegree (β ⊕ τ) k (A.card + 1) := by
    apply Submodule.span_le.mpr
    rintro p ⟨T, hT, j, rfl⟩
    exact (mem_restrictTotalDegree ..).mpr
      ((basisMonomial_degree T j).trans (Nat.add_le_add_right (Finset.card_le_card hT) 1))
  exact (mem_restrictTotalDegree ..).mp (hle hp)

theorem localAffine_normal {A : Finset β} {p : MvPolynomial (β ⊕ τ) k}
    (hp : p ∈ localAffine A) : booleanNF p = p := by
  induction hp using Submodule.span_induction with
  | mem p hp => rcases hp with ⟨T, _, j, rfl⟩; exact booleanNF_basis T j
  | zero => exact map_zero _
  | add p q _ _ hp hq => simp only [map_add, hp, hq]
  | smul c p _ hp => simp only [map_smul, hp]

noncomputable def bitFactor (a : β → Bool) (i : β) : MvPolynomial (β ⊕ τ) k :=
  if a i then X (Sum.inl i) else 1 - X (Sum.inl i)

noncomputable def indicator (A : Finset β) (a : β → Bool) : MvPolynomial (β ⊕ τ) k :=
  ∏ i ∈ A, bitFactor a i

theorem bitFactor_degree (a : β → Bool) (i : β) :
    (bitFactor (τ := τ) (k := k) a i).totalDegree ≤ 1 := by
  unfold bitFactor
  split
  · simp
  · exact (totalDegree_sub _ _).trans (by simp)

theorem indicator_degree (A : Finset β) (a : β → Bool) :
    (indicator (τ := τ) (k := k) A a).totalDegree ≤ A.card := by
  exact (totalDegree_finsetProd A _).trans
    ((Finset.sum_le_sum fun i _ => bitFactor_degree a i).trans (by simp))

theorem localAffine_normal_factor {A : Finset β} {p : MvPolynomial (β ⊕ τ) k}
    (hp : p ∈ localAffine A) {i : β} (hi : i ∈ A) (a : β → Bool) :
    booleanNF (p * bitFactor a i) ∈ localAffine A := by
  induction hp using Submodule.span_induction with
  | mem p hp =>
    rcases hp with ⟨T, hT, j, rfl⟩
    unfold bitFactor
    split
    · simpa using basis_mem_localAffine (Finset.insert_subset hi hT) j
    · rw [mul_sub, mul_one, map_sub, booleanNF_basis, booleanNF_basis_mul_base]
      exact Submodule.sub_mem _ (basis_mem_localAffine hT j)
        (basis_mem_localAffine (Finset.insert_subset hi hT) j)
  | zero => simp
  | add p q _ _ hp hq =>
    simpa only [add_mul, map_add] using Submodule.add_mem _ hp hq
  | smul c p _ hp =>
    simpa only [smul_mul_assoc, map_smul] using Submodule.smul_mem _ c hp

/-- Actual staged derivation: multiply one supported indicator factor, then
repair to normal form at each step. Localized row derivability is concluded. -/
theorem staged_indicator_mem_V
    {F : Set (MvPolynomial (β ⊕ τ) k)} {D : ℕ} {A B : Finset β}
    {p : MvPolynomial (β ⊕ τ) k}
    (hp : p ∈ V (F ∪ fieldEqGens (β ⊕ τ) k 2) D)
    (haff : p ∈ localAffine A) (hB : B ⊆ A) (hcap : A.card + 2 ≤ D)
    (a : β → Bool) :
    booleanNF (indicator B a * p) ∈ V (F ∪ fieldEqGens (β ⊕ τ) k 2) D ∧
      booleanNF (indicator B a * p) ∈ localAffine A := by
  classical
  induction B using Finset.induction_on with
  | empty => simpa [indicator, localAffine_normal haff] using And.intro hp haff
  | @insert i B hi ih =>
    have hBi : B ⊆ A := (Finset.subset_insert i B).trans hB
    have hiA : i ∈ A := hB (Finset.mem_insert_self i B)
    obtain ⟨hmem, hlocal⟩ := ih hBi
    have hprod : booleanNF (indicator B a * p) * bitFactor a i ∈
        V (F ∪ fieldEqGens (β ⊕ τ) k 2) D := by
      refine mul_mem_V hmem ?_
      exact (Nat.add_le_add (localAffine_degree hlocal) (bitFactor_degree a i)).trans hcap
    have hnew := (mem_V_iff_booleanNF_mem_V
      ((totalDegree_mul _ _).trans
        ((Nat.add_le_add (localAffine_degree hlocal) (bitFactor_degree a i)).trans hcap))).mp hprod
    have hnewlocal := localAffine_normal_factor hlocal hiA a
    have hid : booleanNF (indicator (insert i B) a * p) =
        booleanNF (booleanNF (indicator B a * p) * bitFactor a i) := by
      rw [booleanNF_mul_left]
      congr 1
      simp [indicator, Finset.prod_insert hi]
      ring
    rw [hid]
    exact ⟨hnew, hnewlocal⟩

noncomputable def auxPolynomial : Option τ → MvPolynomial (β ⊕ τ) k
  | none => 1
  | some j => X (Sum.inr j)

theorem basis_eq_prod (T : Finset β) (j : Option τ) :
    basisMonomial (k := k) T j =
      (∏ i ∈ T, X (Sum.inl i)) * auxPolynomial j := by
  have hbase : monomial (baseExponent (τ := τ) T) (1 : k) =
      ∏ i ∈ T, X (Sum.inl i) := by
    rw [baseExponent, monomial_sum_one]
    rfl
  cases j with
  | none => simpa [basisMonomial, basisExponent, auxExponent, auxPolynomial] using hbase
  | some j =>
    have hmul := monomial_mul_monomial (s := baseExponent (τ := τ) T)
      (s' := Finsupp.single (Sum.inr j) 1) (a := (1 : k)) (b := 1)
    simpa only [basisMonomial, basisExponent, auxExponent, auxPolynomial, hbase, one_mul, X]
      using hmul.symm

theorem bitFactor_degreeOf (a : β → Bool) (i : β) (x : β ⊕ τ) :
    (bitFactor (k := k) a i).degreeOf x ≤ if x = Sum.inl i then 1 else 0 := by
  classical
  unfold bitFactor
  split
  · simp [degreeOf_X]
  · exact (degreeOf_sub_le x 1 (X (Sum.inl i))).trans (by simp [degreeOf_X])

theorem indicator_degreeOf_le (A : Finset β) (a : β → Bool) (x : β ⊕ τ) :
    (indicator (k := k) A a).degreeOf x ≤ ∑ i ∈ A, if x = Sum.inl i then 1 else 0 := by
  exact (degreeOf_prod_le x A _).trans
    (Finset.sum_le_sum fun i _ => bitFactor_degreeOf a i x)

theorem indicator_aux_degreeOf (A : Finset β) (a : β → Bool) (j : τ) :
    (indicator (k := k) A a).degreeOf (Sum.inr j) = 0 := by
  have h := indicator_degreeOf_le (k := k) A a (Sum.inr j)
  simpa using h

theorem indicator_normal (A : Finset β) (a : β → Bool) :
    booleanNF (indicator (τ := τ) (k := k) A a) = indicator A a := by
  classical
  apply booleanNF_eq_self_of_degreeOf_le_one
  intro x
  refine (indicator_degreeOf_le A a x).trans ?_
  rcases x with i | j
  · simp only [Sum.inl.injEq]
    by_cases hi : i ∈ A <;> simp [hi, eq_comm]
  · simp

theorem indicator_aux_normal (A : Finset β) (a : β → Bool) (j : Option τ) :
    booleanNF (indicator (k := k) A a * auxPolynomial j) =
      indicator A a * auxPolynomial j := by
  classical
  cases j with
  | none => simpa [auxPolynomial] using indicator_normal (τ := τ) (k := k) A a
  | some j =>
    apply booleanNF_eq_self_of_degreeOf_le_one
    intro x
    have h := degreeOf_mul_le x (indicator (τ := τ) (k := k) A a) (X (Sum.inr j))
    rcases x with i | u
    · have hi : (indicator (τ := τ) (k := k) A a).degreeOf (Sum.inl i) ≤ 1 := by
        have hi := indicator_degreeOf_le (τ := τ) (k := k) A a (Sum.inl i)
        by_cases hm : i ∈ A <;> simpa [eq_comm, hm] using hi
      exact h.trans (by simpa [degreeOf_X] using hi)
    · rw [indicator_aux_degreeOf, zero_add] at h
      exact h.trans (by simp [degreeOf_X]; split_ifs <;> omega)

def bitValue (b : Bool) : k := if b then 1 else 0

theorem indicator_mul_base (A : Finset β) (a : β → Bool) {i : β} (hi : i ∈ A) :
    booleanNF (indicator (τ := τ) (k := k) A a * X (Sum.inl i)) =
      bitValue (a i) • indicator A a := by
  classical
  have hsplit : indicator (τ := τ) (k := k) A a =
      indicator (A.erase i) a * bitFactor a i :=
    (Finset.prod_erase_mul A (bitFactor (τ := τ) (k := k) a) hi).symm
  have hkey : booleanNF (indicator (τ := τ) (k := k) A a * X (Sum.inl i)) =
      booleanNF (indicator (A.erase i) a * booleanNF (bitFactor a i * X (Sum.inl i))) := by
    rw [booleanNF_mul_right, hsplit, mul_assoc]
  rw [hkey]
  cases hai : a i with
  | false =>
    have hz : booleanNF (bitFactor (τ := τ) (k := k) a i * X (Sum.inl i)) = 0 := by
      have he : bitFactor (τ := τ) (k := k) a i * X (Sum.inl i) =
          -((X (Sum.inl i) : MvPolynomial (β ⊕ τ) k)^2 - X (Sum.inl i)) := by
        simp only [bitFactor, hai, Bool.false_eq_true, ↓reduceIte]
        ring
      rw [he, map_neg, booleanNF_bit_equation, neg_zero]
    simp [hz, bitValue, hai]
  | true =>
    have hx : booleanNF (bitFactor (τ := τ) (k := k) a i * X (Sum.inl i)) = X (Sum.inl i) := by
      simp only [bitFactor, hai, ↓reduceIte]
      rw [← pow_two, X_pow_eq_monomial]
      simp [X]
    rw [hx]
    have he : indicator (τ := τ) (k := k) (A.erase i) a * X (Sum.inl i) = indicator A a := by
      simpa [bitFactor, hai] using hsplit.symm
    rw [he, indicator_normal]
    simp [bitValue, hai]

/-- Assign only base variables; auxiliary variables remain indeterminates. -/
noncomputable def specializeBase (a : β → Bool) :
    MvPolynomial (β ⊕ τ) k →ₐ[k] MvPolynomial (β ⊕ τ) k :=
  aeval fun x => match x with
    | Sum.inl i => C (bitValue (a i))
    | Sum.inr j => X (Sum.inr j)

@[simp] theorem specializeBase_base (a : β → Bool) (i : β) :
    specializeBase (τ := τ) (k := k) a (X (Sum.inl i)) = C (bitValue (a i)) := by
  simp [specializeBase]

@[simp] theorem specializeBase_aux (a : β → Bool) (j : Option τ) :
    specializeBase (k := k) a (auxPolynomial j) = auxPolynomial j := by
  cases j <;> simp [auxPolynomial, specializeBase]

/-- Exact polynomial interpolation identity on each supported affine monomial. -/
theorem indicator_basis_interpolation {A T : Finset β} (hT : T ⊆ A)
    (a : β → Bool) (j : Option τ) :
    booleanNF (indicator A a * basisMonomial (k := k) T j) =
      indicator A a * specializeBase a (basisMonomial T j) := by
  classical
  induction T using Finset.induction_on with
  | empty => simpa [basis_eq_prod] using indicator_aux_normal (k := k) A a j
  | @insert i T hi ih =>
    have hiA : i ∈ A := hT (Finset.mem_insert_self i T)
    have hTA : T ⊆ A := (Finset.subset_insert i T).trans hT
    have hb : basisMonomial (k := k) (insert i T) j = X (Sum.inl i) * basisMonomial T j := by
      simp only [basis_eq_prod, Finset.prod_insert hi]
      ring
    rw [hb, map_mul, specializeBase_base]
    have hkey : booleanNF (indicator A a * (X (Sum.inl i) * basisMonomial (k := k) T j)) =
        booleanNF (booleanNF (indicator A a * X (Sum.inl i)) * basisMonomial T j) := by
      rw [booleanNF_mul_left, mul_assoc]
    rw [hkey, indicator_mul_base A a hiA, smul_mul_assoc, map_smul, ih hTA, C_mul']
    simp only [mul_smul_comm]

/-- Interpolation is proved as an identity of polynomials in the unassigned
auxiliary variables. No localized derivability premise is used. -/
theorem indicator_interpolation {A : Finset β} {p : MvPolynomial (β ⊕ τ) k}
    (hp : p ∈ localAffine A) (a : β → Bool) :
    booleanNF (indicator A a * p) = indicator A a * specializeBase a p := by
  induction hp using Submodule.span_induction with
  | mem p hp =>
    rcases hp with ⟨T, hT, j, rfl⟩
    exact indicator_basis_interpolation hT a j
  | zero => simp
  | add p q _ _ hp hq => simp only [mul_add, map_add, hp, hq]
  | smul c p _ hp => simp only [mul_smul_comm, map_smul, hp]

/-- Supported localization followed by multiplication by the complementary
base indicator, with total cost at most `all bases + 1`. -/
theorem full_localized_row_mem_V
    {F : Set (MvPolynomial (β ⊕ τ) k)} {D : ℕ} {A B : Finset β}
    {p : MvPolynomial (β ⊕ τ) k}
    (hp : p ∈ V (F ∪ fieldEqGens (β ⊕ τ) k 2) D)
    (haff : p ∈ localAffine A) (hAB : A ⊆ B)
    (hlocal : A.card + 2 ≤ D) (hfull : B.card + 1 ≤ D) (a : β → Bool) :
    indicator B a * specializeBase a p ∈ V (F ∪ fieldEqGens (β ⊕ τ) k 2) D := by
  classical
  obtain ⟨hmem, hspace⟩ := staged_indicator_mem_V hp haff (Finset.Subset.refl A) hlocal a
  have hdegree : (booleanNF (indicator A a * p)).totalDegree +
      (indicator (τ := τ) (k := k) (B \ A) a).totalDegree ≤ D := by
    have hcard : (B \ A).card + A.card = B.card := Finset.card_sdiff_add_card_eq_card hAB
    have h1 := localAffine_degree hspace
    have h2 := indicator_degree (τ := τ) (k := k) (B \ A) a
    omega
  have hm := mul_mem_V hmem hdegree
  rw [indicator_interpolation haff a] at hm
  have hid : indicator (τ := τ) (k := k) (B \ A) a * indicator A a = indicator B a :=
    Finset.prod_sdiff hAB
  convert hm using 1
  rw [← hid]
  ring

end BinaryLocalization
end CryptoResearch.FallDegree
