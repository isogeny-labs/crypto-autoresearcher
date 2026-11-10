/-
Sheriff SHF-20261106-a114e7, reader `lean` (LNX): statement-fidelity checks of
CryptoResearch.Quotient.translation_commutes_iff_two_torsion.

Run from /home/user/crypto-autoresearcher/formal:
  PATH=$HOME/.elan/bin:$PATH CHECKPOINT_SKIP=audit BENCHREC_SKIP=audit \
    lake env lean ../research/sheriff/SHF-20261106-a114e7/scripts/readers/lean/fidelity.lean
Everything here must elaborate with no error. Expected failures live in
ptm_*.lean in the same directory.
-/
import CryptoResearch.Quotient.TranslationDescent
import Mathlib.Data.ZMod.Basic
import Mathlib.GroupTheory.Perm.Basic
import Mathlib.AlgebraicGeometry.EllipticCurve.Affine.Point

open CryptoResearch.Quotient

-- K-a1: the exact elaborated statement and its axioms.
#check @translation_commutes_iff_two_torsion
#print axioms translation_commutes_iff_two_torsion

/- K-blind: blind restatement written from research/THM_QUOTIENT_DESCENT1.md
"Setting" and "Proof" only (iota_S(P) = -P - S, tau_T(P) = P + T, commuting maps
as an equality of functions, and 2T = O written as T + T = 0), then shown to be
the producer's proposition. -/
namespace LNXBlind
variable {E : Type*} [AddCommGroup E]

def iota (S : E) (P : E) : E := -P - S
def tau (T : E) (P : E) : E := P + T

theorem blind_lemma (S T : E) :
    (tau T ∘ iota S = iota S ∘ tau T) ↔ T + T = 0 := by
  have h := translation_commutes_iff_two_torsion S T
  rw [two_nsmul] at h
  rw [← h, funext_iff]
  apply forall_congr'
  intro P
  have a : -P - S + T = -(P + S) + T := by abel
  have b : -(P + T) - S = -(P + T + S) := by abel
  simp only [Function.comp_apply, tau, iota, a, b]

-- the blind statement and the producer's are the same proposition (both directions)
theorem producer_of_blind (S T : E) :
    (∀ P : E, -(P + S) + T = -(P + T + S)) ↔ (2 : ℕ) • T = 0 := by
  rw [two_nsmul, ← blind_lemma S T, funext_iff]
  apply forall_congr'
  intro P
  have a : -P - S + T = -(P + S) + T := by abel
  have b : -(P + T) - S = -(P + T + S) := by abel
  simp only [Function.comp_apply, tau, iota, a, b]

/- iota_S is an involution for every S (the note's "whatever the order of S"),
and the formal theorem places no hypothesis on S. -/
theorem iota_involutive (S : E) : Function.Involutive (iota S) := by
  intro P; simp only [iota]; abel

end LNXBlind

/- K-b: hypotheses are only [AddCommGroup E]; discharge them on concrete
witnesses, including the Mathlib elliptic-curve point group. -/
example : (∀ P : ZMod 4, -(P + 1) + 2 = -(P + 2 + 1)) ↔ (2 : ℕ) • (2 : ZMod 4) = 0 :=
  translation_commutes_iff_two_torsion (1 : ZMod 4) 2
example {F : Type} [Field F] [DecidableEq F] (W : WeierstrassCurve.Affine F) (S T : W.Point) :
    (∀ P : W.Point, -(P + S) + T = -(P + T + S)) ↔ (2 : ℕ) • T = 0 :=
  translation_commutes_iff_two_torsion S T

/- K-c: kernel-checked differential tests on small groups (decide), computed
independently of the producer's proof. -/
-- ZMod 4: both sides, every S and T
example : ∀ S T : ZMod 4, ((∀ P : ZMod 4, -(P + S) + T = -(P + T + S)) ↔ (2 : ℕ) • T = 0) := by
  decide
-- ZMod 2 × ZMod 4 (E[2] has 4 elements): both sides, every S and T
example : ∀ S T : ZMod 2 × ZMod 4,
    ((∀ P : ZMod 2 × ZMod 4, -(P + S) + T = -(P + T + S)) ↔ (2 : ℕ) • T = 0) := by
  decide
-- an order-4 translation does not commute, an order-2 one does (S of order 4)
example : ¬ (∀ P : ZMod 4, -(P + 1) + 1 = -(P + 1 + 1)) := by decide
example : (∀ P : ZMod 4, -(P + 1) + 2 = -(P + 2 + 1)) := by decide

/- K-c (#eval): count commuting T vs 2-torsion T, per S, on several groups.
Prints (name, #group, #T commuting for all S, #T with 2•T = 0, agree for every S). -/
def lnxCheck (name : String) (G : List α) [Add α] [Neg α] [Zero α] [DecidableEq α]
    (two : α → α) : String :=
  let comm (S T : α) : Bool := G.all fun P => decide (-(P + S) + T = -(P + T + S))
  let tors (T : α) : Bool := decide (two T = 0)
  let agree := G.all fun S => G.all fun T => comm S T == tors T
  let nComm := (G.filter fun T => G.all fun S => comm S T).length
  let nTors := (G.filter tors).length
  s!"{name}: |G|={G.length} commuting={nComm} two_torsion={nTors} agree_all_S={agree}"

def zmodList (n : ℕ) [NeZero n] : List (ZMod n) := (List.range n).map (fun k => (k : ZMod n))

#eval lnxCheck "ZMod 1" (zmodList 1) (fun T => (2 : ℕ) • T)
#eval lnxCheck "ZMod 2" (zmodList 2) (fun T => (2 : ℕ) • T)
#eval lnxCheck "ZMod 3" (zmodList 3) (fun T => (2 : ℕ) • T)
#eval lnxCheck "ZMod 4" (zmodList 4) (fun T => (2 : ℕ) • T)
#eval lnxCheck "ZMod 6" (zmodList 6) (fun T => (2 : ℕ) • T)
#eval lnxCheck "ZMod 12" (zmodList 12) (fun T => (2 : ℕ) • T)
#eval lnxCheck "ZMod 2 x ZMod 2" ((zmodList 2).flatMap fun a => (zmodList 2).map fun b => (a, b))
  (fun T => (2 : ℕ) • T)
#eval lnxCheck "ZMod 2 x ZMod 4" ((zmodList 2).flatMap fun a => (zmodList 4).map fun b => (a, b))
  (fun T => (2 : ℕ) • T)
#eval lnxCheck "ZMod 4 x ZMod 6" ((zmodList 4).flatMap fun a => (zmodList 6).map fun b => (a, b))
  (fun T => (2 : ℕ) • T)

/- Commutativity is load-bearing: in the non-abelian Additive (Perm (Fin 3)) the
2-torsion set has 4 elements, but only T = 0 commutes with every iota_S. -/
def s3 : List (Additive (Equiv.Perm (Fin 3))) :=
  [1, Equiv.swap 0 1, Equiv.swap 0 2, Equiv.swap 1 2,
   Equiv.swap 0 1 * Equiv.swap 0 2, Equiv.swap 0 2 * Equiv.swap 0 1].map Additive.ofMul

#eval s!"distinct elements of s3: {(s3.dedup).length}"
#eval lnxCheck "Additive (Perm (Fin 3))" s3 (fun T => T + T)
