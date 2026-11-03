/- Independent, Mathlib-free re-check of the PR's Lemma 2.5.3 statement
   (Lean core only: grind's ring/linear solver). -/

-- The PR's exact proposition (same binders and hypotheses).
theorem montgomery_reduction_core
    {n R n' a u : Int}
    (hnpos : 0 < n) (hnR : n < R) (ha0 : 0 <= a) (han : a < n)
    (hu0 : 0 <= u) (huR : u < R)
    (hnegInv : Exists fun k : Int => n * n' + 1 = k * R)
    (hu : Exists fun ell : Int => u = a * n' + ell * R) :
    Exists fun w : Int => a + u * n = R * w /\ 0 <= w /\ w < n /\ n ∣ R * w - a := by
  obtain ⟨k, hk⟩ := hnegInv
  obtain ⟨l, hl⟩ := hu
  have hRw : a + u * n = R * (a * k + l * n) := by subst hl; grind
  refine ⟨a * k + l * n, hRw, ?_, ?_, ⟨u, by grind⟩⟩
  · have : 0 <= u * n := Int.mul_nonneg hu0 (Int.le_of_lt hnpos)
    have hR : 0 < R := by omega
    exact Int.le_of_mul_le_mul_left (by grind) hR
  · have h1 : u * n <= (R - 1) * n := Int.mul_le_mul_of_nonneg_right (by omega) (Int.le_of_lt hnpos)
    have hR : 0 < R := by omega
    exact Int.lt_of_mul_lt_mul_left (a := R) (by grind) (Int.le_of_lt hR)

-- Strengthening: `hnpos` and `hnR` are redundant (n > a >= 0, R > u >= 0);
-- in particular R > n is not used by the integer core.
theorem montgomery_reduction_core_min
    {n R n' a u : Int}
    (ha0 : 0 <= a) (han : a < n) (hu0 : 0 <= u) (huR : u < R)
    (hnegInv : Exists fun k : Int => n * n' + 1 = k * R)
    (hu : Exists fun ell : Int => u = a * n' + ell * R) :
    Exists fun w : Int => a + u * n = R * w /\ 0 <= w /\ w < n /\ n ∣ R * w - a := by
  have hnpos : 0 < n := by omega
  obtain ⟨k, hk⟩ := hnegInv
  obtain ⟨l, hl⟩ := hu
  have hRw : a + u * n = R * (a * k + l * n) := by subst hl; grind
  refine ⟨a * k + l * n, hRw, ?_, ?_, ⟨u, by grind⟩⟩
  · have : 0 <= u * n := Int.mul_nonneg hu0 (Int.le_of_lt hnpos)
    exact Int.le_of_mul_le_mul_left (by grind) (by omega : (0:Int) < R)
  · have h1 : u * n <= (R - 1) * n := Int.mul_le_mul_of_nonneg_right (by omega) (Int.le_of_lt hnpos)
    exact Int.lt_of_mul_lt_mul_left (a := R) (by grind) (by omega)

-- The book's inverse form: the negative-inverse hypothesis alone gives
-- an inverse of R mod n, so  R*w ≡ a  upgrades to  w ≡ a * Rinv (mod n).
theorem montgomery_inverse_form
    {n R n' a w k : Int} (hk : n * n' + 1 = k * R) (hw : n ∣ R * w - a) :
    n ∣ w - a * k := by
  obtain ⟨c, hc⟩ := hw
  -- k*R ≡ 1 (mod n), so w = k*R*w - n*n'*w ≡ k*a.
  exact ⟨k * c - n' * w, by grind⟩

-- Control: the bound w < n FAILS for Montgomery-multiplication inputs a < nR
-- (book's own sketch says w < 2n): n=3, R=4, n'=1, a=11, u=3, w=5.
example : (11:Int) + 3 * 3 = 4 * 5 ∧ ¬ ((5:Int) < 3) := by decide

#print axioms montgomery_reduction_core
#print axioms montgomery_reduction_core_min
#print axioms montgomery_inverse_form
