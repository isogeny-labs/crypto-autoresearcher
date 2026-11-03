# J2: source and elaborated-type fidelity

Task: `TASK-20261103-a1d702` / `T-1531`.
Owned joint: **J2 source and elaborated-type fidelity**.
Frozen review revision: `b806841cef6ad73e80c5d49ca9a51845e5cf2eb6`.
Producer input revision: `004355570fa983535696439b1781cb762dae3607`.
Verdict for this joint: **holds**, with the receipt identity and fresh execution limitations below. This is a source/statement correspondence finding, not a whole-review validation or independent authentication of the pinned machine receipt.

## Inputs and method

The primary sources were the exact torsion derivation note, target YAML, Lean declarations, frozen plan and input bindings, plus the model README, dependency pins and linked problem record. The comparison is an elementary statement and type audit; no novelty or external literature conclusion is made. The repository formal-review instructions and attestation schema were checked. No J1 or J3 report was read. This reviewer is not the blind mathematical re-derivation reviewer.

`reproduce.py` checks Git objects at the frozen and producer revisions against the materialized files, preserves the historical printed type and emits `checks.json`. Its default replay performs hashes only. `python3 reproduce.py --lean` opts into bounded direct-source elaboration and should be run only in a fresh copy of this write-once packet. No Lake build, package fetch, cloud submission, repository edit, commit, push or merge was performed.

## Correspondence findings

1. **Universes and quantifiers.** The declaration is uniform in `{A : Type u}`, followed by `M : AdditiveModel A`, `r : Nat` and arbitrary `P T : A`. It then takes the oddness, annihilation, two-torsion and nonzero hypotheses. There is no existential choice of a specially favorable model, no finite-carrier assumption, and no quantifier shift that would weaken the stated result.

2. **Algebraic laws.** `AdditiveModel` has two data fields (`zero`, `add`) and four proof fields (`zero_add`, `add_zero`, `assoc`, `comm`). Their types are the usual universally quantified left identity, right identity, associativity and commutativity equalities. The plan's phrase “all five additive-law fields” is a counting error: there are **four** law fields and **six** fields in total. This discrepancy is recorded; the frozen plan was not edited. The laws required by the prose are all present. No inverse, cancellation, primality or finiteness assumption is hidden in the model.

3. **Scalar multiplication and oddness.** `multiple 0 a = zero` and `multiple (n+1) a = add (multiple n a) a` give the repeated-addition scalar convention in the note. The witness is exactly `∃ k : Nat, r = k + k + 1`. It expresses a positive odd natural scalar, admits `r=1`, and excludes zero and even scalars. No proof of the desired translation conclusion is supplied as a premise.

4. **The two conclusions are distinct declarations.** `odd_translation` proves `M.multiple r (M.add P T) = T` from oddness, `rP=zero`, and `T+T=zero`. `odd_translation_outside_kernel` additionally takes `T_nonzero : T ≠ M.zero` and proves `M.multiple r (M.add P T) ≠ M.zero`. Thus the named target supplies exactly the exclusion predicate; the adjacent equality theorem supplies the target prose's “more precisely” statement. The named theorem does not itself return their conjunction. Both declarations are present in the same exact source.

5. **Meaning of kernel and nonzero.** “Outside the zero-kernel” is precisely failure of the equation defining the zero fiber of multiplication by `r`. The Lean file does not define a subgroup object, but the prose does not require one for this conditional statement. The nonzero premise belongs to the exclusion theorem and is not demanded for the equality theorem. Taking `T=zero` keeps the equality meaningful and destroys the exclusion strengthening.

6. **Satisfiability.** The explicit `xorModel` interprets the data as `Bool`, `false`, and `Bool.xor`, and supplies each law by exhaustive case proof. `positive_control` applies the exact named theorem with `r=3`, `P=false`, `T=true`, and witness `k=1`; the annihilation and two-torsion facts are definitional, and nonzero is decidable. This is a concrete satisfiable set of hypotheses, not a contradictory or empty-carrier construction. `zero : A` also makes the model's carrier inhabited. The source's `even_scalar_control` and the zero-T specialization identify why the two restrictions are material. These source checks are not claimed as new independently completed Lean executions.

## Printed type, hashes and actual execution

The exact source note, target YAML and theorem bytes match all three of: the frozen expected SHA-256, the producer Git object, and the working file. The theorem SHA-256 is `68eb719cc0c34018475a73e00b22a623a8937f66f471be407dc4015c51020e8b`. Toolchain and manifest bytes also match the historical receipt's declared digests. The workspace manifest has an empty package list and pins Lean 4.22.0.

The pre-existing receipt read through `git show` was:

`docs/reports/2026-10-31-hosted-formal-receipts/receipts/scoped-odd-torsion-translation.json`.

Its actual digest is `c4ae843196160e477aa13de229c825ca3cf15452baa02c3db1019c3f20adfb52`, whereas the frozen bindings name `63419f85fb756ca00a9772fb5c7454a605aed73f53b1fad2b355de3c7ba15403` for run `41494797344`. Its recorded source revision is `232f4e78abe6cd8eca285fb2be075d3fdd40ee33`. This is a **different historical receipt**, not the frozen run's receipt. The mismatch remains a failed check in `checks.json`; it was not normalized away. Its recorded theorem and task-spec hashes nevertheless match the exact reviewed source and target. Its printed named type is:

```lean
ScopedObstructions.AdditiveModel.odd_translation_outside_kernel.{u} {A : Type u}
  (M : ScopedObstructions.AdditiveModel A) (r : Nat) (P T : A)
  (odd_r : ∃ k, r = k + k + 1)
  (annihilates_P : M.multiple r P = M.zero)
  (two_T : M.add T T = M.zero) (T_nonzero : T ≠ M.zero) :
  M.multiple r (M.add P T) ≠ M.zero
```

This observed printed type matches the source's binders and conclusion exactly. The historical log also reports zero-axiom checks, but reading the log does not independently authenticate its execution. J3 owns the pinned receipt and machine boundary; this reviewer did not read J3's output.

Fresh local execution was attempted only with the already installed Lean 4.22.0 and a copy of the exact source. `lean +leanprover/lean4:v4.22.0 --version` passed. Direct `lean +leanprover/lean4:v4.22.0 Torsion.lean` exceeded its 45-second timeout, and the wrapper exited before saving source compiler logs. `TypeAudit.lean` was created but never run. This attempt is **infrastructure_error**, with no compiler diagnostic and no mathematical refutation. `initial-attempt.json`, `initial-attempt.failure.txt`, and `reproduce-attempt1.py` preserve it. No second Lean run was attempted. Fresh machine verification remains unestablished by this J2 packet.

## Concrete application bridges still absent

The source does not establish any of the following application-specific obligations:

- A named field and nonsingular elliptic curve, a rational-point carrier, its identity/infinity value, and concrete point addition/equality representations.
- A checked interpretation of those point operations as this `AdditiveModel`, including all four laws and a proof that the implementation's scalar operation agrees with `multiple`.
- A concrete scalar `r` with its odd witness and a concrete point `P` with `[r]P=O`. The premise does not assert that `P` has exact order `r` or that `r` is prime.
- A rational point `T` on that same curve/domain, a certificate for `[2]T=O`, and a certificate that `T≠O`. The existence of such a point on an intended curve is not supplied by this abstract theorem.
- An identified target subgroup or factor base and a proof that each of its members belongs to the zero-kernel of `[r]`. That containment is needed to turn zero-kernel exclusion into exclusion from a particular factor base. No membership checker or certificate is imported.
- A definition of tuple translation or relation preservation, or an argument excluding even numbers of translations whose torsion contributions cancel. The single-point result supplies no blanket exclusion of T-closed mixed-domain factor bases.
- A refinement from serialized coordinates or executable point arithmetic to the mathematical objects and equality used in a claimed implementation.

These bridges are already named as separate obligations in the source note and linked problem record. Their absence does not change the faithful scope of the conditional additive statement.

## Disposition

Source/statement fidelity: **faithful_scoped**. J2 joint verdict: **holds**. Current-source fresh machine status in this packet: **infrastructure_error** from the bounded timeout. Pinned receipt authentication: **not performed by J2**; the historical receipt identity mismatch is preserved. No official research status was changed.
