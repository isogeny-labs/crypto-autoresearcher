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
    simpa only [baseExponent, Nat.add_comm] using congrArg (fun n => n + 1) ih

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
  rcases x with b | a <;> cases j <;>
    simp [basisExponent, auxExponent, Finsupp.single_apply]
  all_goals split_ifs <;> omega

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

end BinaryLocalization
end CryptoResearch.FallDegree
