import CryptoResearch.FallDegree.FirstFallBounded

/-!
Exact raw-to-reduced shape of characteristic-two S3 in ordinary V.
Bounded derivations from explicit bit equations, not a formalization of
coefficient extraction, support localization, or the full last-fall bound.
-/
namespace CryptoResearch.FallDegree
open MvPolynomial
variable {σ k : Type*} [Field k] [ExpChar k 2]

noncomputable def binaryS3 (x y u a : MvPolynomial σ k) : MvPolynomial σ k :=
  (x*y+x*u+y*u)^2+x*y*u+a

noncomputable def binaryTwist (x : MvPolynomial σ k) : MvPolynomial σ k :=
  map (iterateFrobenius k 2 1) x

noncomputable def binaryS3Reduced (x y u a : MvPolynomial σ k) : MvPolynomial σ k :=
  binaryTwist x * binaryTwist y +
    (binaryTwist x + binaryTwist y) * binaryTwist u + x*y*u+a

theorem binaryTwist_totalDegree (x : MvPolynomial σ k) :
    (binaryTwist x).totalDegree = x.totalDegree :=
  totalDegree_frobeniusTwist (p := 2) (e := 1) x

/-- Characteristic-two S3 has a cubic representative derived at cap four. -/
theorem binaryS3_repair (x y u a : MvPolynomial σ k)
    (hx : x.totalDegree ≤ 1) (hy : y.totalDegree ≤ 1)
    (hu : u.totalDegree ≤ 1) :
    binaryS3 x y u a - binaryS3Reduced x y u a
      ∈ V (fieldEqGens σ k 2) 4 := by
  have hxy : (x*y).totalDegree ≤ 2 := (totalDegree_mul x y).trans (by omega)
  have hxu : (x*u).totalDegree ≤ 2 := (totalDegree_mul x u).trans (by omega)
  have hyu : (y*u).totalDegree ≤ 2 := (totalDegree_mul y u).trans (by omega)
  have hq : (x*y+x*u+y*u).totalDegree ≤ 2 :=
    (totalDegree_add _ _).trans (max_le
      ((totalDegree_add _ _).trans (max_le hxy hxu)) hyu)
  have h := V_mono (fieldEqGens σ k 2) (show
      2 * (x*y+x*u+y*u).totalDegree ≤ 4 by omega)
    (frobenius_degree_fall (p := 2) (e := 1) (x*y+x*u+y*u))
  simp only [pow_one] at h
  convert h using 1
  simp only [binaryS3, binaryS3Reduced, binaryTwist, map_add, map_mul]
  ring

/-- Multilinearity additionally requires disjoint coordinate blocks. -/
theorem binaryS3Reduced_degree (x y u a : MvPolynomial σ k)
    (hx : x.totalDegree ≤ 1) (hy : y.totalDegree ≤ 1)
    (hu : u.totalDegree ≤ 1) (ha : a.totalDegree ≤ 3) :
    (binaryS3Reduced x y u a).totalDegree ≤ 3 := by
  have htx := binaryTwist_totalDegree x
  have hty := binaryTwist_totalDegree y
  have htu := binaryTwist_totalDegree u
  have hp : (binaryTwist x * binaryTwist y).totalDegree ≤ 2 :=
    (totalDegree_mul _ _).trans (by omega)
  have hs : (binaryTwist x + binaryTwist y).totalDegree ≤ 1 :=
    (totalDegree_add _ _).trans (by omega)
  have hsu : ((binaryTwist x + binaryTwist y) * binaryTwist u).totalDegree ≤ 2 :=
    (totalDegree_mul _ _).trans (by omega)
  have hxy : (x*y).totalDegree ≤ 2 := (totalDegree_mul _ _).trans (by omega)
  have hxyu : (x*y*u).totalDegree ≤ 3 := (totalDegree_mul _ _).trans (by omega)
  unfold binaryS3Reduced
  exact (totalDegree_add _ _).trans (max_le
    ((totalDegree_add _ _).trans (max_le
      ((totalDegree_add _ _).trans (by omega)) hxyu)) ha)

/-- With one fixed field parameter the reduced second equation is quadratic. -/
theorem binaryS3Reduced_fixed_degree (x y : MvPolynomial σ k) (r a : k)
    (hx : x.totalDegree ≤ 1) (hy : y.totalDegree ≤ 1) :
    (binaryS3Reduced x y (C r) (C a)).totalDegree ≤ 2 := by
  have htx := binaryTwist_totalDegree x
  have hty := binaryTwist_totalDegree y
  have htr := binaryTwist_totalDegree (C r : MvPolynomial σ k)
  have hp : (binaryTwist x * binaryTwist y).totalDegree ≤ 2 :=
    (totalDegree_mul _ _).trans (by omega)
  have hs : (binaryTwist x + binaryTwist y).totalDegree ≤ 1 :=
    (totalDegree_add _ _).trans (by omega)
  have hsu : ((binaryTwist x + binaryTwist y) * binaryTwist (C r)).totalDegree ≤ 1 :=
    (totalDegree_mul _ _).trans (by simp only [totalDegree_C] at htr; omega)
  have hxy : (x*y).totalDegree ≤ 2 := (totalDegree_mul _ _).trans (by omega)
  have hxyu : (x*y*C r).totalDegree ≤ 2 :=
    (totalDegree_mul _ _).trans (by simp only [totalDegree_C]; omega)
  unfold binaryS3Reduced
  exact (totalDegree_add _ _).trans (max_le
    ((totalDegree_add _ _).trans (max_le
      ((totalDegree_add _ _).trans (by omega)) hxyu)) (by simp))
end CryptoResearch.FallDegree
#print axioms CryptoResearch.FallDegree.binaryS3_repair
#print axioms CryptoResearch.FallDegree.binaryS3Reduced_degree
#print axioms CryptoResearch.FallDegree.binaryS3Reduced_fixed_degree
