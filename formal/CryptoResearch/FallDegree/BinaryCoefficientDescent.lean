import CryptoResearch.FallDegree.BinaryLocalization
import CryptoResearch.FallDegree.BinarySemaevShape

namespace CryptoResearch.FallDegree
open MvPolynomial
open scoped BigOperators
open BinaryLocalization
variable {σ β τ K k : Type*} [Field K] [Field k]

/-- Additive coefficient projection. It need not be a ring homomorphism. -/
noncomputable def coefficientProjection (φ : K →+ k) :
    MvPolynomial σ K →+ MvPolynomial σ k :=
  AddMonoidHom.comp AddMonoidAlgebra.coeffAddEquiv.symm.toAddMonoidHom
    ((Finsupp.mapRange.addMonoidHom φ).comp AddMonoidAlgebra.coeffAddEquiv.toAddMonoidHom)

@[simp] theorem coefficientProjection_monomial (φ : K →+ k) (d : σ →₀ ℕ) (c : K) :
    coefficientProjection φ (monomial d c) = monomial d (φ c) := by
  simp [coefficientProjection, monomial]

theorem coefficientProjection_booleanNF (φ : K →+ k) (p : MvPolynomial σ K) :
    coefficientProjection φ (booleanNF p) = booleanNF (coefficientProjection φ p) := by
  induction p using MvPolynomial.induction_on' with
  | monomial d c => simp
  | add p q hp hq => simp only [map_add, hp, hq]

theorem coefficientProjection_degree (φ : K →+ k) (p : MvPolynomial σ K) :
    (coefficientProjection φ p).totalDegree ≤ p.totalDegree := by
  have h : coefficientProjection φ p =
      ∑ d ∈ p.support, monomial d (φ (p.coeff d)) := by
    conv_lhs => rw [p.as_sum, map_sum]
    simp
  rw [h]
  exact totalDegree_finsetSum_le fun d hd =>
    (totalDegree_monomial_le _ _).trans (le_totalDegree hd)

/-- Projection preserves supported affine shape, including all scalar
combinations over the extension coefficient field. -/
theorem coefficientProjection_localAffine [DecidableEq β] (φ : K →+ k)
    {A : Finset β} {p : MvPolynomial (β ⊕ τ) K}
    (hp : p ∈ localAffine A) : coefficientProjection φ p ∈ localAffine A := by
  classical
  have h : ∀ c : K, coefficientProjection φ (c • p) ∈ localAffine A := by
    induction hp using Submodule.span_induction with
    | mem p hp =>
      rcases hp with ⟨T, hT, j, rfl⟩
      intro c
      have hm := (localAffine (τ := τ) (k := k) A).smul_mem (φ c)
        (basis_mem_localAffine hT j)
      simpa only [basisMonomial, smul_monomial, smul_eq_mul, mul_one,
        coefficientProjection_monomial] using hm
    | zero => intro c; simp
    | add p q _ _ hp hq =>
      intro c
      simpa only [smul_add, map_add] using (localAffine A).add_mem (hp c) (hq c)
    | smul a p _ hp =>
      intro c
      simpa only [smul_smul] using hp (c*a)
  simpa only [one_smul] using h 1

/-- Evaluation on bit assignments is invariant under normalization. -/
theorem booleanNF_eval_of_bits (p : MvPolynomial σ k) (t : σ → k)
    (ht : ∀ i, t i = 0 ∨ t i = 1) : eval t (booleanNF p) = eval t p := by
  have hker : Ideal.span (fieldEqGens σ k 2) ≤ RingHom.ker (eval t) := by
    apply Ideal.span_le.mpr
    rintro _ ⟨i,rfl⟩
    change eval t ((X i)^2-X i) = 0
    rcases ht i with hi | hi <;> simp [hi]
  have hm := hker (V_le_ideal_span _ _ (boolean_repair_mem_V p))
  change eval t (p-booleanNF p) = 0 at hm
  rw [map_sub, sub_eq_zero] at hm
  exact hm.symm

/-- A raw coefficientwise-descended system inherits the exact support-aware
bound. Raw eligibility, normalization, and evaluation are all derived. -/
theorem lastFallDegree_raw_projected_supported_affine_le
    [DecidableEq β] {ι : Type*} [Fintype ι]
    (B : Finset β) (raw : ι → MvPolynomial (β ⊕ τ) K)
    (φ : ι → K →+ ZMod 2) (A : ι → Finset β) (r d : ℕ)
    (haff : ∀ i, booleanNF (raw i) ∈ localAffine (A i))
    (hsupport : ∀ i, A i ⊆ B) (hsize : ∀ i, (A i).card ≤ r)
    (hdegree : ∀ i, (raw i).totalDegree ≤ d)
    (hunsat : ¬ ∃ a : β → Bool, ∃ t : τ → Bool,
      ∀ i, eval (Sum.elim (fun j => bitValue (k := ZMod 2) (a j))
        (fun j => bitValue (k := ZMod 2) (t j)))
        (coefficientProjection (φ i) (raw i)) = 0) :
    lastFallDegree (Set.range (fun i => coefficientProjection (φ i) (raw i)) ∪
      fieldEqGens (β ⊕ τ) (ZMod 2) 2) ≤ max d (max (B.card+1) (r+2)) := by
  classical
  let F := Set.range (fun i => coefficientProjection (φ i) (raw i))
  let D := max d (max (B.card+1) (r+2))
  let q := fun i => booleanNF (coefficientProjection (φ i) (raw i))
  have hlocal : ∀ i, (A i).card + 2 ≤ D := by
    intro i
    exact (Nat.add_le_add_right (hsize i) 2).trans
      ((le_max_right _ _).trans (le_max_right _ _))
  have hfull : B.card+1 ≤ D := (le_max_left _ _).trans (le_max_right _ _)
  have hrows : ∀ i, q i ∈ V (F ∪ fieldEqGens (β ⊕ τ) (ZMod 2) 2) D := by
    intro i
    have hd : (coefficientProjection (φ i) (raw i)).totalDegree ≤ D :=
      (coefficientProjection_degree _ _).trans ((hdegree i).trans (le_max_left _ _))
    exact (mem_V_iff_booleanNF_mem_V hd).mp
      (mem_V_of_mem_of_totalDegree_le (Or.inl ⟨i,rfl⟩) hd)
  have hqa : ∀ i, q i ∈ localAffine (A i) := by
    intro i
    change booleanNF (coefficientProjection (φ i) (raw i)) ∈ _
    rw [← coefficientProjection_booleanNF]
    exact coefficientProjection_localAffine _ (haff i)
  have hno : ¬ ∃ a : β → Bool, ∃ t : τ → Bool,
      ∀ i, eval (Sum.elim (fun j => bitValue (k := ZMod 2) (a j))
        (fun j => bitValue (k := ZMod 2) (t j))) (q i) = 0 := by
    rintro ⟨a,t,ht⟩
    apply hunsat
    refine ⟨a,t,fun i => ?_⟩
    have hb : ∀ x : β ⊕ τ,
        Sum.elim (fun j => bitValue (k := ZMod 2) (a j))
          (fun j => bitValue (k := ZMod 2) (t j)) x = 0 ∨
        Sum.elim (fun j => bitValue (k := ZMod 2) (a j))
          (fun j => bitValue (k := ZMod 2) (t j)) x = 1 := by
      intro x
      exact zmod_two_is_bit _
    have he := booleanNF_eval_of_bits (coefficientProjection (φ i) (raw i)) _ hb
    rw [← he]
    exact ht i
  have hu := refutation_of_supported_affine_boolean_unsat B q A hrows hqa hsupport
    hlocal hfull zmod_two_is_bit hno
  exact Nat.sInf_le (lastFallSet_of_refutation hu)


noncomputable def binaryBaseForm (S : Finset β) (c₀ : K) (c : β → K) :
    MvPolynomial (β ⊕ τ) K := C c₀ + ∑ i ∈ S, C (c i) * X (Sum.inl i)

noncomputable def binaryAuxForm (T : Finset τ) (c₀ : K) (c : τ → K) :
    MvPolynomial (β ⊕ τ) K := C c₀ + ∑ j ∈ T, C (c j) * X (Sum.inr j)

theorem one_mem_localAffine [DecidableEq β] (A : Finset β) :
    (1 : MvPolynomial (β ⊕ τ) K) ∈ localAffine A := by
  classical
  simpa [basis_eq_prod, auxPolynomial] using
    (basis_mem_localAffine (τ := τ) (k := K) (Finset.empty_subset A) none)

theorem C_mem_localAffine [DecidableEq β] (A : Finset β) (c : K) :
    (C c : MvPolynomial (β ⊕ τ) K) ∈ localAffine A := by
  simpa only [smul_eq_C_mul, mul_one] using
    (localAffine A).smul_mem c (one_mem_localAffine (τ := τ) A)

theorem aux_X_mem_localAffine [DecidableEq β] (A : Finset β) (j : τ) :
    (X (Sum.inr j) : MvPolynomial (β ⊕ τ) K) ∈ localAffine A := by
  classical
  simpa [basis_eq_prod, auxPolynomial] using
    (basis_mem_localAffine (k := K) (Finset.empty_subset A) (some j))

theorem binaryAuxForm_mem_localAffine [DecidableEq β] (A : Finset β)
    (T : Finset τ) (c₀ : K) (c : τ → K) :
    binaryAuxForm T c₀ c ∈ localAffine A := by
  unfold binaryAuxForm
  refine (localAffine A).add_mem (C_mem_localAffine A c₀) ?_
  exact (localAffine A).sum_mem fun j _ => by
    simpa only [smul_eq_C_mul] using
      (localAffine A).smul_mem (c j) (aux_X_mem_localAffine A j)

theorem binaryBaseForm_nf_mul_mem_localAffine [DecidableEq β]
    {A S : Finset β} (hS : S ⊆ A) (c₀ : K) (c : β → K)
    {p : MvPolynomial (β ⊕ τ) K} (hp : p ∈ localAffine A) :
    booleanNF (binaryBaseForm S c₀ c * p) ∈ localAffine A := by
  classical
  unfold binaryBaseForm
  rw [add_mul, map_add]
  refine (localAffine A).add_mem ?_ ?_
  · rw [C_mul', map_smul, localAffine_normal hp]
    exact (localAffine A).smul_mem c₀ hp
  · rw [Finset.sum_mul, map_sum]
    exact (localAffine A).sum_mem fun i hi => by
      rw [mul_assoc, C_mul', map_smul]
      exact (localAffine A).smul_mem (c i) (localAffine_normal_mul_base hp (hS hi))

theorem binaryBaseForm_degree (S : Finset β) (c₀ : K) (c : β → K) :
    (binaryBaseForm (τ := τ) S c₀ c).totalDegree ≤ 1 := by
  unfold binaryBaseForm
  exact (totalDegree_add _ _).trans (max_le (by simp)
    (totalDegree_finsetSum_le fun i _ =>
      (totalDegree_mul _ _).trans (by simp)))

theorem binaryAuxForm_degree (T : Finset τ) (c₀ : K) (c : τ → K) :
    (binaryAuxForm (β := β) T c₀ c).totalDegree ≤ 1 := by
  unfold binaryAuxForm
  exact (totalDegree_add _ _).trans (max_le (by simp)
    (totalDegree_finsetSum_le fun j _ =>
      (totalDegree_mul _ _).trans (by simp)))

theorem binaryTwist_baseForm [ExpChar K 2]
    (S : Finset β) (c₀ : K) (c : β → K) :
    binaryTwist (binaryBaseForm (τ := τ) S c₀ c) =
      binaryBaseForm S (c₀^2) (fun i => (c i)^2) := by
  simp [binaryTwist, binaryBaseForm, frobenius_def]

theorem binaryTwist_auxForm [ExpChar K 2]
    (T : Finset τ) (c₀ : K) (c : τ → K) :
    binaryTwist (binaryAuxForm (β := β) T c₀ c) =
      binaryAuxForm T (c₀^2) (fun j => (c j)^2) := by
  simp [binaryTwist, binaryAuxForm, frobenius_def]


@[simp] theorem booleanNF_C' (c : k) : booleanNF (C c : MvPolynomial σ k) = C c := by
  change booleanNF (monomial 0 c) = monomial 0 c
  rw [booleanNF_monomial, booleanExponent_zero]

theorem base_X_mem_localAffine [DecidableEq β] {A : Finset β} {i : β} (hi : i ∈ A) :
    (X (Sum.inl i) : MvPolynomial (β ⊕ τ) K) ∈ localAffine A := by
  classical
  simpa [basis_eq_prod, auxPolynomial] using
    (basis_mem_localAffine (τ := τ) (k := K) (Finset.singleton_subset_iff.mpr hi) none)

theorem binaryBaseForm_mem_localAffine [DecidableEq β] {A S : Finset β}
    (hS : S ⊆ A) (c₀ : K) (c : β → K) :
    binaryBaseForm (τ := τ) S c₀ c ∈ localAffine A := by
  unfold binaryBaseForm
  refine (localAffine A).add_mem (C_mem_localAffine A c₀) ?_
  exact (localAffine A).sum_mem fun i hi => by
    simpa only [smul_eq_C_mul] using
      (localAffine A).smul_mem (c i) (base_X_mem_localAffine (hS hi))

theorem binaryS3_normal_support [DecidableEq β] [ExpChar K 2]
    {A Sx Sy : Finset β} (hx : Sx ⊆ A) (hy : Sy ⊆ A)
    (cx₀ cy₀ cu₀ a : K) (cx cy : β → K) (cu : τ → K) (T : Finset τ) :
    booleanNF (binaryS3 (binaryBaseForm Sx cx₀ cx) (binaryBaseForm Sy cy₀ cy)
      (binaryAuxForm T cu₀ cu) (C a)) ∈ localAffine A := by
  let x := binaryBaseForm (τ := τ) Sx cx₀ cx
  let y := binaryBaseForm (τ := τ) Sy cy₀ cy
  let u := binaryAuxForm (β := β) T cu₀ cu
  have htx : binaryTwist x = binaryBaseForm Sx (cx₀^2) (fun i => (cx i)^2) :=
    binaryTwist_baseForm Sx cx₀ cx
  have hty : binaryTwist y = binaryBaseForm Sy (cy₀^2) (fun i => (cy i)^2) :=
    binaryTwist_baseForm Sy cy₀ cy
  have htu : binaryTwist u ∈ localAffine A := by
    rw [show binaryTwist u = binaryAuxForm T (cu₀^2) (fun j => (cu j)^2) from
      binaryTwist_auxForm T cu₀ cu]
    exact binaryAuxForm_mem_localAffine A T _ _
  have hu : u ∈ localAffine A := binaryAuxForm_mem_localAffine A T cu₀ cu
  have h1 : booleanNF (binaryTwist x * binaryTwist y) ∈ localAffine A := by
    rw [htx, hty]
    exact binaryBaseForm_nf_mul_mem_localAffine hx _ _ (binaryBaseForm_mem_localAffine hy _ _)
  have h2 : booleanNF ((binaryTwist x+binaryTwist y)*binaryTwist u) ∈ localAffine A := by
    rw [add_mul, map_add, htx, hty]
    exact (localAffine A).add_mem
      (binaryBaseForm_nf_mul_mem_localAffine hx _ _ htu)
      (binaryBaseForm_nf_mul_mem_localAffine hy _ _ htu)
  have h3 : booleanNF (x*y*u) ∈ localAffine A := by
    have h := binaryBaseForm_nf_mul_mem_localAffine hx cx₀ cx
      (binaryBaseForm_nf_mul_mem_localAffine hy cy₀ cy hu)
    simpa only [booleanNF_mul_right, ← mul_assoc] using h
  have hr : booleanNF (binaryS3Reduced x y u (C a)) ∈ localAffine A := by
    simp only [binaryS3Reduced, map_add, booleanNF_C']
    exact (localAffine A).add_mem ((localAffine A).add_mem
      ((localAffine A).add_mem h1 h2) h3) (C_mem_localAffine A a)
  have hrepair := binaryS3_repair x y u (C a)
    (binaryBaseForm_degree Sx cx₀ cx) (binaryBaseForm_degree Sy cy₀ cy)
    (binaryAuxForm_degree T cu₀ cu)
  have hn := booleanNF_eq_zero_of_mem_bit_ideal (V_le_ideal_span _ _ hrepair)
  rw [map_sub, sub_eq_zero] at hn
  rw [hn]
  exact hr


theorem binaryS3_degree (x y u : MvPolynomial σ K) (a : K)
    (hx : x.totalDegree ≤ 1) (hy : y.totalDegree ≤ 1) (hu : u.totalDegree ≤ 1) :
    (binaryS3 x y u (C a)).totalDegree ≤ 4 := by
  have hxy : (x*y).totalDegree ≤ 2 := (totalDegree_mul _ _).trans (by omega)
  have hxu : (x*u).totalDegree ≤ 2 := (totalDegree_mul _ _).trans (by omega)
  have hyu : (y*u).totalDegree ≤ 2 := (totalDegree_mul _ _).trans (by omega)
  have hq : (x*y+x*u+y*u).totalDegree ≤ 2 :=
    (totalDegree_add _ _).trans (max_le
      ((totalDegree_add _ _).trans (max_le hxy hxu)) hyu)
  have hs : ((x*y+x*u+y*u)^2).totalDegree ≤ 4 :=
    (totalDegree_pow _ _).trans (by omega)
  have ht : (x*y*u).totalDegree ≤ 3 := (totalDegree_mul _ _).trans (by omega)
  unfold binaryS3
  exact (totalDegree_add _ _).trans (max_le
    ((totalDegree_add _ _).trans (by omega)) (by simp))

theorem binaryGuard_normal_support [DecidableEq β]
    {A Sx Sy : Finset β} (hx : Sx ⊆ A) (hy : Sy ⊆ A)
    (cx cy : β → K) (cv : τ → K) (T : Finset τ) :
    booleanNF (binaryAuxForm T 0 cv *
      (binaryBaseForm Sx 0 cx + binaryBaseForm Sy 0 cy) + 1) ∈ localAffine A := by
  have hv := binaryAuxForm_mem_localAffine (K := K) A T 0 cv
  have hxv := binaryBaseForm_nf_mul_mem_localAffine hx 0 cx hv
  have hyv := binaryBaseForm_nf_mul_mem_localAffine hy 0 cy hv
  have he : binaryAuxForm (β := β) T 0 cv *
      (binaryBaseForm Sx 0 cx + binaryBaseForm Sy 0 cy) + 1 =
      binaryBaseForm Sx 0 cx * binaryAuxForm T 0 cv +
      binaryBaseForm Sy 0 cy * binaryAuxForm T 0 cv + 1 := by ring
  rw [he, map_add, map_add]
  have h1 : booleanNF (1 : MvPolynomial (β ⊕ τ) K) = 1 := by
    simpa only [map_one] using (booleanNF_C' (σ := β ⊕ τ) (1 : K))
  rw [h1]
  exact (localAffine A).add_mem ((localAffine A).add_mem hxv hyv) (one_mem_localAffine A)

/-- Index zero selects the first S3, one the second, and two the optional
guard. Rows/projections may be selected with or without that guard. -/
noncomputable def binaryChainRaw (j : Fin 3) (x y z u v : MvPolynomial σ K) (r a : K) :
    MvPolynomial σ K :=
  if j = 0 then binaryS3 x y u (C a)
  else if j = 1 then binaryS3 z (C r) u (C a)
  else v*(x+y)+1

/-- The second displayed S3 is exactly the conventional cyclic permutation. -/
theorem binaryS3_cycle (x y z a : MvPolynomial σ K) :
    binaryS3 x y z a = binaryS3 z x y a := by
  unfold binaryS3
  ring

/-- Raw F2-coefficient descent of the actual two-S3 chain, including optional
inverse-guard projections, has last fall at most 3ell+1 on Boolean UNSAT.
No projection is assumed multiplicative and no localized row is assumed. -/
theorem lastFallDegree_binary_two_S3_chain_le
    [DecidableEq β] [ExpChar K 2] {ι : Type*} [Fintype ι]
    (ell : ℕ) (hell : 1 ≤ ell) (Sx Sy Sz : Finset β) (Tu Tv : Finset τ)
    (hx : Sx.card ≤ ell) (hy : Sy.card ≤ ell) (hz : Sz.card ≤ ell)
    (cx cy cz : β → K) (cu cv : τ → K) (r a : K)
    (which : ι → Fin 3) (φ : ι → K →+ ZMod 2)
    (hunsat : ¬ ∃ b : β → Bool, ∃ t : τ → Bool,
      ∀ i, eval (Sum.elim (fun j => bitValue (k := ZMod 2) (b j))
        (fun j => bitValue (k := ZMod 2) (t j)))
        (coefficientProjection (φ i) (binaryChainRaw (which i)
          (binaryBaseForm Sx 0 cx) (binaryBaseForm Sy 0 cy) (binaryBaseForm Sz 0 cz)
          (binaryAuxForm Tu 0 cu) (binaryAuxForm Tv 0 cv) r a)) = 0) :
    lastFallDegree (Set.range (fun i => coefficientProjection (φ i) (binaryChainRaw (which i)
      (binaryBaseForm Sx 0 cx) (binaryBaseForm Sy 0 cy) (binaryBaseForm Sz 0 cz)
      (binaryAuxForm Tu 0 cu) (binaryAuxForm Tv 0 cv) r a)) ∪
      fieldEqGens (β ⊕ τ) (ZMod 2) 2) ≤ 3*ell+1 := by
  classical
  let B := Sx ∪ Sy ∪ Sz
  let A := fun i => if which i = 1 then Sz else Sx ∪ Sy
  let raw := fun i => binaryChainRaw (which i)
      (binaryBaseForm Sx 0 cx) (binaryBaseForm Sy 0 cy) (binaryBaseForm Sz 0 cz)
      (binaryAuxForm Tu 0 cu) (binaryAuxForm Tv 0 cv) r a
  have haff : ∀ i, booleanNF (raw i) ∈ localAffine (A i) := by
    intro i
    by_cases h0 : which i = 0
    · simp only [raw, binaryChainRaw, h0, ↓reduceIte, A]
      exact binaryS3_normal_support Finset.subset_union_left Finset.subset_union_right
        0 0 0 a cx cy cu Tu
    · by_cases h1 : which i = 1
      · simp only [raw, binaryChainRaw, h1, ↓reduceIte, A]
        simpa [binaryBaseForm] using
          (binaryS3_normal_support (A := Sz) (Sx := Sz) (Sy := ∅)
            (Finset.Subset.refl _) (Finset.empty_subset _) 0 r 0 a cz (fun _ => 0) cu Tu)
      · simp only [raw, binaryChainRaw, h0, h1, ↓reduceIte, A]
        exact binaryGuard_normal_support Finset.subset_union_left Finset.subset_union_right cx cy cv Tv
  have hsupport : ∀ i, A i ⊆ B := by
    intro i
    dsimp [A, B]
    split_ifs
    · exact Finset.subset_union_right
    · exact Finset.subset_union_left
  have hsize : ∀ i, (A i).card ≤ 2*ell := by
    intro i
    dsimp [A]
    split_ifs
    · omega
    · have h := Finset.card_union_le Sx Sy
      omega
  have hdeg : ∀ i, (raw i).totalDegree ≤ 4 := by
    intro i
    dsimp [raw, binaryChainRaw]
    split_ifs
    · exact binaryS3_degree _ _ _ a (binaryBaseForm_degree Sx 0 cx)
        (binaryBaseForm_degree Sy 0 cy) (binaryAuxForm_degree Tu 0 cu)
    · exact binaryS3_degree _ _ _ a (binaryBaseForm_degree Sz 0 cz)
        (by simp) (binaryAuxForm_degree Tu 0 cu)
    · have hv := binaryAuxForm_degree (β := β) Tv 0 cv
      have hx' := binaryBaseForm_degree (τ := τ) Sx 0 cx
      have hy' := binaryBaseForm_degree (τ := τ) Sy 0 cy
      have hs : ((binaryBaseForm (τ := τ) Sx 0 cx)+(binaryBaseForm Sy 0 cy)).totalDegree ≤ 1 :=
        (totalDegree_add _ _).trans (max_le hx' hy')
      exact (totalDegree_add _ _).trans (max_le
        ((totalDegree_mul _ _).trans (by omega)) (by simp))
  have h := lastFallDegree_raw_projected_supported_affine_le B raw φ A (2*ell) 4
    haff hsupport hsize hdeg hunsat
  have hcard : B.card ≤ 3*ell := by
    have h1 := Finset.card_union_le Sx Sy
    have h2 := Finset.card_union_le (Sx ∪ Sy) Sz
    dsimp [B]
    omega
  exact h.trans (max_le (by omega) (max_le (by omega) (by omega)))

end CryptoResearch.FallDegree
#print axioms CryptoResearch.FallDegree.coefficientProjection_localAffine
#print axioms CryptoResearch.FallDegree.booleanNF_eval_of_bits
#print axioms CryptoResearch.FallDegree.lastFallDegree_raw_projected_supported_affine_le
#print axioms CryptoResearch.FallDegree.lastFallDegree_binary_two_S3_chain_le
