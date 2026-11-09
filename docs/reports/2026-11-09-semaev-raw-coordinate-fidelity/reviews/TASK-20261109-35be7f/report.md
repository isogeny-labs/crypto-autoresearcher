# J2 source-to-Lean statement fidelity review

**Task:** TASK-20261109-35be7f (Conductor T-2006)  
**Joint owned:** J2 producer-to-Lean statement fidelity  
**Verdict:** **holds**, for the typed raw-pair predicate and its stated iff.  
**Pinned source:** Git commit `3f7e3e4d0d049256e0ae23571553e806aab230ab` in `/var/tmp/semaev-frobenius-fidelity-20261109`.  
**Plan:** `review-plan.yaml`, SHA-256 `0cbbc5e36a720afa830e67211da86062bbf62fc501b8da31e13e79e96e7fc16a`.

This is a source/type comparison, not a Lean build or hosted-run audit. I read no J1 or J3 report or output. Each of the five reviewed Git blobs matches the SHA-256 value pinned in the plan.

## Exact correspondence

The source Lemma 3 (`research/THM_SEMAEV_FALL1.md:105-113`) describes a finite tuple of affine curve points with three checks: each point satisfies the curve equation, each x-coordinate belongs to the declared subspace, and their curve-group sum equals the target. It claims the predicate is total and decidable. The raw-coordinate target (`formal/targets/semaev-raw-coordinate-certificate.yaml:20-28`) explicitly narrows the object under review to already typed `K × K` pairs and `R : W.Point`, and states an iff for those three conditions.

| Joint | Pinned Lean text | Fidelity finding |
| --- | --- | --- |
| Quantifiers and fields | `Certificate.lean:16-18,160-165` has arbitrary `b m : Nat`, `F K : Type*`, `[Field F] [Fintype F] [DecidableEq F]`, `[Field K] [DecidableEq K]`, `[Algebra F K]`. | Uniform over every tuple length and declared family. Finite `F` supplies the finite coefficient search. The source setup has a finite extension `K = F_{q^n}`; the theorem is more general in `K` and covers that case when its instances are supplied. It does not instantiate a concrete extension or embedding. |
| Curve and target | `Certificate.lean:147-148,160-162` requires `W : WeierstrassCurve.Affine K`, `[W.IsElliptic]`, and `R : W.Point`. | The explicit ellipticity assumption meets the target's nonsingularity condition. `R` is already a typed curve point, possibly infinity; target decoding and target validity from bytes are outside the statement. No hypothesis asserts the desired equality. |
| Family and span | `Certificate.lean:20-32,149-150,163-164` uses `basis : Fin b → K`, searches `Fin b → F`, and equates this with `Submodule.span F (Set.range basis)`. | The iff checks membership in exactly the supplied family's span. Neither linear independence nor an externally intended `V` is established. The source calls the family a fixed basis; the target deliberately permits a finite spanning family. A concrete basis/dimension claim needs a separate binding. |
| Equation and invalid pairs | `Certificate.lean:37-49,131-136,147-151,163-164` tests the explicit Weierstrass equation. `pointOfRaw` maps a pair failing that test to `.zero`. | The first conjunct of `validRawDecomposition` rejects every such pair, including one whose identity image could otherwise make the sum match. The equation equivalence connects the arithmetic check to `W.Equation`. The named iff keeps the equation conjunct; it does not accept an invalid pair via the fallback. |
| Group sum | `Certificate.lean:131-151,160-177` reifies accepted pairs as `W.Point` and compares `∑ i, pointOfRaw W (xy i)` with `R`. | The equality is a sum in Mathlib's point type. The named theorem preserves this sum exactly on both sides; it does not prove a producer's independently encoded group operation agrees with it. `pointOfRaw_eq_mk` (`:138-142`) states the valid-pair constructor identity. |
| Decidability | `Certificate.lean:24-27,41-44,153-157` provides `Decidable` instances for the finite span, equation, and raw predicate. | The named declaration is an iff of propositions, not itself a `decide = true` theorem. The accompanying instance provides the total decision procedure in Lean. It specifies no time bound or particular linear-system algorithm; the membership implementation enumerates finite coefficients. |

The named proof (`Certificate.lean:166-177`) unfolds `validRawDecomposition`, converts the equation and span conjuncts via established equivalences, and passes the same group-sum equality through in both directions. It assumes no valid decomposition as a theorem hypothesis. This is a direct fidelity match for the target's typed pair-level iff. The empty cases remain meaningful: `m = 0` leaves the pair condition vacuous and requires `R` to equal the empty sum; `b = 0` uses the span of the empty family. These are generalizations of the usual positive-size application, not hidden acceptance paths.

## Boundary of the verdict

The October 21 producer report (`docs/reports/2026-10-21-semaev-certificate/report.md:12-36,59-69`) describes the typed-point theorem and the supplemental raw-coordinate iff. Its phrase “untrusted-input path” applies to raw **field-element pairs**; it cannot be read as a verified byte parser. The raw target itself says this explicitly (`formal/targets/semaev-raw-coordinate-certificate.yaml:11-19`). The open bridge record (`problems/semaev-certificate-serialized-record-bridge.md:20-29`) lists six missing obligations:

1. **B1:** an unambiguous bytes-to-coordinate decoder that rejects malformed, ambiguous, and out-of-range encodings.
2. **B2:** concrete modulus, extension representation, arithmetic, byte order, and `F`-to-`K` embedding bound to the Lean instances.
3. **B3:** recorded curve coefficients bound to `W`, with `W.IsElliptic` established.
4. **B4:** the recorded family bound to the checker input and its span to the intended `V`; independence only where a basis or dimension claim needs it.
5. **B5:** tuple length, every summand, challenge association, target, and any infinity tag bound to the typed arguments.
6. **B6:** authenticated execution of the instantiated Lean checker or a checked native-verifier refinement, with evaluation trust stated.

Consequently, this J2 verdict does not authenticate a serialized certificate, any specific experiment result, a relation or syzygy attributed elsewhere in the research note, decomposition existence/probability, or runtime. The source Lemma's broader explanatory Remark 3 (`research/THM_SEMAEV_FALL1.md:115-117`) calls for independent run-wrapper re-verification; this theorem supplies a mathematical checker predicate, while B1–B6 and execution evidence are required to show that a run wrapper used it on the intended record. The October 21 report likewise makes no rate or runtime claim (`:59-69`).

**J2 conclusion:** `holds` for source-to-Lean fidelity of the typed raw-pair iff and accompanying decidability construction. Serialized-record and runtime interpretations remain separate, open obligations. Machine validity and controls belong to the independently assigned J3 and J1 joints; I did not inspect their reports, run Lean, or infer their outcomes.

## Input digests

| Pinned Git path | SHA-256 |
| --- | --- |
| `research/THM_SEMAEV_FALL1.md` | `11b61f4f4bdaed0c323ec852f19fc4c0a7ff3972715bfe637604fb675db7fee4` |
| `formal/targets/semaev-raw-coordinate-certificate.yaml` | `e813668ff35099270312e4138f52e01c20673084ca11c9c822c6077018e4ebc5` |
| `formal/CryptoResearch/Semaev/Certificate.lean` | `aa022e4829eefc2cbe9ac05cbeb39f81e9e3eaa8147e2e41e9d718f11976bd89` |
| `docs/reports/2026-10-21-semaev-certificate/report.md` | `d060ca4237190ef4b742b08797273da39e26eab39ed968bc6f0101a0ee18b68c` |
| `problems/semaev-certificate-serialized-record-bridge.md` | `22004a6348c822371e265c174bd7e98bf5d65119a3ce74ba116548da04d6b0e9` |
