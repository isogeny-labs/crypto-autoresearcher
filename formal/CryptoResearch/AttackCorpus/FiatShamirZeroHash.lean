/-
Finite algebraic controls for a constant-challenge Fiat--Shamir transform.

Source:
`research/cryptographic_assumption_attack_corpus_tranche2_20261102/README.md`.
Target: `formal/targets/attack-fs-zero-hash.yaml`.

The verifier below is only the abstract module equation

  s • G = R + H(m, R) • X.

It does not model transcript encodings, a random oracle, rewinding, query
bounds, an extractor, or a proof of knowledge.  In particular, the constant
hashes used for the countermodels are outside the random-oracle model.
-/
import Mathlib.Algebra.Field.ZMod
import Mathlib.Algebra.Module.Basic
import Mathlib.Tactic.NormNum

namespace CryptoResearch.AttackCorpus.FiatShamirZeroHash

/-- The single Schnorr-style module equation checked by this finite model. -/
def Accepts
    {Message F A : Type*} [Field F] [AddCommGroup A] [Module F A]
    (H : Message → A → F) (m : Message)
    (generator publicKey commitment : A) (response : F) : Prop :=
  response • generator = commitment + H m commitment • publicKey

/-- A deliberately non-random challenge function. -/
def constantHash
    {Message F A : Type*} [Zero F] (challenge : F) : Message → A → F :=
  fun _ _ ⇒ challenge

/-- Challenge zero makes `R = s • G` accept for every public key.  The
construction has no witness input. -/
theorem zero_hash_accepts_every_public_key
    {Message F A : Type*} [Field F] [AddCommGroup A] [Module F A]
    (m : Message) (generator publicKey : A) (response : F) :
    Accepts (constantHash (0 : F)) m generator publicKey
      (response • generator) response := by
  simp [Accepts, constantHash]

/-- More generally, if a constant challenge is known before the commitment is
chosen, `R = s • G - c • X` is accepting.  Nonzero alone is therefore not a
Fiat--Shamir security premise. -/
theorem known_constant_hash_accepts
    {Message F A : Type*} [Field F] [AddCommGroup A] [Module F A]
    (challenge response : F) (m : Message) (generator publicKey : A) :
    Accepts (constantHash challenge) m generator publicKey
      (response • generator - challenge • publicKey) response := by
  simp [Accepts, constantHash]

/-- The same zero-hash transcript accepts two distinct public keys in a
concrete prime-field module. -/
theorem zmod_five_zero_hash_accepts_distinct_public_keys :
    let message : Unit := ()
    let generator : ZMod 5 := 1
    let response : ZMod 5 := 3
    let commitment : ZMod 5 := 3
    let publicKey₀ : ZMod 5 := 0
    let publicKey₁ : ZMod 5 := 1
    publicKey₀ ≠ publicKey₁ ∧
      Accepts (constantHash (0 : ZMod 5)) message generator publicKey₀
        commitment response ∧
      Accepts (constantHash (0 : ZMod 5)) message generator publicKey₁
        commitment response := by
  norm_num [Accepts, constantHash]

/-- Honest algebraic control: for one fixed transcript, a nonzero challenge
determines at most one public group element.  This fixes the transcript and
does not supply a fork or a Fiat--Shamir security theorem. -/
theorem fixed_transcript_nonzero_challenge_unique_public_key
    {Message F A : Type*} [Field F] [AddCommGroup A] [Module F A]
    (H : Message → A → F) (m : Message)
    (generator commitment publicKey₀ publicKey₁ : A) (response : F)
    (hchallenge : H m commitment ≠ 0)
    (h₀ : Accepts H m generator publicKey₀ commitment response)
    (h₁ : Accepts H m generator publicKey₁ commitment response) :
    publicKey₀ = publicKey₁ := by
  have hsmul :
      H m commitment • publicKey₀ = H m commitment • publicKey₁ := by
    apply add_left_cancel (a := commitment)
    exact h₀.symm.trans h₁
  exact (isUnit_iff_ne_zero.mpr hchallenge).smul_left_cancel.mp hsmul

/-- Exact audited declaration.  It keeps the zero-challenge construction, the
stronger arbitrary-known-constant construction, a concrete distinct-key
control, and the fixed-transcript nonzero uniqueness statement in one type. -/
theorem zero_hash_acceptance_and_nonzero_control
    {Message F A : Type*} [Field F] [AddCommGroup A] [Module F A]
    (H : Message → A → F) (m : Message)
    (generator commitment publicKey₀ publicKey₁ : A)
    (response challenge : F) :
    Accepts (constantHash (0 : F)) m generator publicKey₀
        (response • generator) response ∧
      Accepts (constantHash challenge) m generator publicKey₀
        (response • generator - challenge • publicKey₀) response ∧
      ((0 : ZMod 5) ≠ 1 ∧
        Accepts (constantHash (0 : ZMod 5)) ()
          (1 : ZMod 5) (0 : ZMod 5) (3 : ZMod 5) (3 : ZMod 5) ∧
        Accepts (constantHash (0 : ZMod 5)) ()
          (1 : ZMod 5) (1 : ZMod 5) (3 : ZMod 5) (3 : ZMod 5)) ∧
      (H m commitment ≠ 0 →
        Accepts H m generator publicKey₀ commitment response →
        Accepts H m generator publicKey₁ commitment response →
        publicKey₀ = publicKey₁) := by
  refine ⟨zero_hash_accepts_every_public_key m generator publicKey₀ response,
    known_constant_hash_accepts challenge response m generator publicKey₀,
    ?_, ?_⟩
  · simpa using zmod_five_zero_hash_accepts_distinct_public_keys
  · intro hchallenge h₀ h₁
    exact fixed_transcript_nonzero_challenge_unique_public_key
      H m generator commitment publicKey₀ publicKey₁ response
      hchallenge h₀ h₁

end CryptoResearch.AttackCorpus.FiatShamirZeroHash
