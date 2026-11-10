import CryptoResearch.Quotient.TranslationDescent
import Mathlib.Data.ZMod.Basic
#print axioms CryptoResearch.Quotient.translation_commutes_iff_two_torsion
-- witness: hypotheses are satisfiable and the iff is non-vacuous on ZMod 4
example : (∀ P : ZMod 4, -(P + 1) + 2 = -(P + 2 + 1)) := by decide
example : ¬ (∀ P : ZMod 4, -(P + 1) + 1 = -(P + 1 + 1)) := by decide
