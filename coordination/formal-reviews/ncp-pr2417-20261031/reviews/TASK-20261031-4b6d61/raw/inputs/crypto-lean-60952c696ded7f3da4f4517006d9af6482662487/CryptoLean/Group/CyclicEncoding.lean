import Mathlib.GroupTheory.SpecificGroups.Cyclic
import Mathlib.Algebra.Field.ZMod
import Mathlib.Tactic.Ring

set_option autoImplicit false

namespace CryptoLean.Cyclic
variable {A : Type*} [AddCommGroup A] {n : ℕ}

def encode (P : A) (hn : n • P = 0) : ZMod n →+ A :=
  ZMod.lift n ⟨zmultiplesHom A P, by simpa using hn⟩

@[simp] theorem encode_intCast (P : A) (hn : n • P = 0) (z : ℤ) :
    encode P hn (z : ZMod n) = z • P := by
  simp [encode]

theorem encode_natCast (P : A) (hn : n • P = 0) (m : ℕ) :
    encode P hn (m : ZMod n) = m • P := by
  simpa using encode_intCast P hn (m : ℤ)

theorem encode_val [NeZero n] (P : A) (hn : n • P = 0) (a : ZMod n) :
    encode P hn a = a.val • P := by
  simpa using encode_natCast P hn a.val

theorem encode_injective (P : A) (horder : addOrderOf P = n) :
    Function.Injective (encode (n := n) P (by rw [← horder]; exact addOrderOf_nsmul_eq_zero P)) := by
  apply (ZMod.lift_injective n).2
  intro m hm
  apply (ZMod.intCast_zmod_eq_zero_iff_dvd m n).2
  rw [← horder]
  exact addOrderOf_dvd_iff_zsmul_eq_zero.mpr hm

theorem encode_range (P : A) (hn : n • P = 0) :
    (encode P hn).range = AddSubgroup.zmultiples P := by
  ext Q
  constructor
  · rintro ⟨a, rfl⟩
    obtain ⟨z, rfl⟩ := ZMod.intCast_surjective a
    rw [encode_intCast]
    exact AddSubgroup.zsmul_mem_zmultiples P z
  · intro hQ
    obtain ⟨z, rfl⟩ := AddSubgroup.mem_zmultiples_iff.mp hQ
    exact ⟨(z : ZMod n), encode_intCast P hn z⟩

def walkPoint [NeZero n] (P Q : A) (a b : ZMod n) : A :=
  a.val • P + b.val • Q

theorem walkPoint_eq_encode [NeZero n] (P : A) (hn : n • P = 0)
    (a b x : ZMod n) :
    walkPoint P (encode P hn x) a b = encode P hn (a + b*x) := by
  unfold walkPoint
  rw [map_add, ← encode_val P hn a]
  congr 1
  rw [← map_nsmul]
  congr 1
  simp [nsmul_eq_mul]

end CryptoLean.Cyclic
