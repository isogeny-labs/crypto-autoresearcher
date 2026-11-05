# Independent review B: cubic evaluation rank

## Result

**Joint B verdict: `holds`, at the exact finite linear-algebra scope of the frozen target.** The concrete ten-point evaluation matrix has the stated nonzero right-kernel vector and determinant zero, and the determinant-nonzero repair is valid over every field. The source and theorem correctly keep projective quotienting, nonsingular-cubic construction, and JKSST's actual `2 <= r <= 9` families outside the result.

This is a semantic verdict, not a machine-verification verdict. Exact Lean 4.35 run `41503944712` was pending when this review was assigned. After the semantic audit, the Coordinator reported that `CubicEvalRank` built successfully while the overall run failed in other modules. I did not inspect the run log, a target receipt, or the named axiom audit and did not rerun it. Machine status therefore remains **`pending`** for this attestation; the reported module build is recorded narrowly and this report does not call the exact run or full gate passed.

| Review dimension | Result |
| --- | --- |
| Joint | B — cubic evaluation rank countermodel and determinant repair |
| Semantic fidelity | `faithful_scoped` |
| Joint verdict | `holds` |
| Machine status | `pending` (Coordinator-reported module build success; target receipt/named audit unread) |
| Formal-review outcome while the machine gate is pending | `inconclusive` |

## Bound inputs

- Review head: `fbb6c5d6f8bbae160e51404172996c837efb0a07`.
- Producer snapshot: `674b3248a8b007748a2cf4f10e5063e7de123be4`. The only files added between that snapshot and the review head are the precommitted review plan and blind input; the reviewed target, theorem source, and research note are unchanged.
- Review plan: `docs/reports/2026-11-02-attack-corpus-next-five-lean/review-plan.yaml`, SHA-256 `7a55598bad9dddb2f6b462fa981d6f4afb7e17871c417174692f1c3201f1f77f`.
- Target: `formal/targets/attack-cubic-eval-rank.yaml`, SHA-256 `23f3b80c1fce11658c833cc612620c35ea8ca65323d29e1022855344ba4acd3c`.
- Lean source: `formal/CryptoResearch/AttackCorpus/CubicEvalRank.lean`, SHA-256 `ed62caa522eb7820784ed2674cb1d088a7581a6205f26b8e160292ef2dc56464`.
- Source note: `research/cryptographic_assumption_attack_corpus_tranche2_20261102/README.md`, SHA-256 `4834787c796eec875c33ca16ad75801c99102b31bbc565e0694311cc63b70a68`.
- Pinned toolchain: Lean `4.35.0`; `mathlib` revision `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`; `CryptoLean` revision `60952c696ded7f3da4f4517006d9af6482662487`.

The exact audited declaration is `CryptoResearch.AttackCorpus.CubicEvalRank.collinear_kernel_and_injective_repair` at source lines 115–131.

## Clause mapping

| Frozen claim clause | Lean encoding | Independent audit |
| --- | --- | --- |
| Ten rational representatives `P_i=(i,0,1)` are distinct | `collinearPoints` (lines 61–73), first conjunct at line 116 | Holds for literal triples. It also implies distinct projective classes for these normalized representatives because the `z=1` coordinate forces any projective scaling between two of them to equal 1. |
| `Y Z^2` is a nonzero coefficient vector | `lineCubic` has coordinate 8 equal to 1 (lines 65–78), second conjunct at line 117 | Holds. Index 8 is exactly `Y*Z^2` in the declared zero-based monomial order. |
| It vanishes at all ten points | `lineCubic_value` and `lineCubic_vanishes` (lines 80–87), third conjunct at line 118 | Holds: every point has `y=0`, `z=1`, so every one of the ten evaluations is 0. |
| The evaluation matrix has a nontrivial coefficient kernel | row-oriented `evaluationMatrix`, `evaluationMatrix_mulVec_apply`, and `lineCubic_in_kernel` (lines 52–59 and 89–92), existential at lines 119–120 | Holds. Matrix rows are points and columns are coefficients, so `A *ᵥ c` is exactly the vector of cubic evaluations. |
| The square matrix has determinant zero | `collinear_evaluation_det_zero` (lines 105–110), fifth conjunct at line 121 | Holds, both from the nonzero kernel and directly from its six identically zero columns. |
| Nonzero determinant repairs injectivity over any field | `coefficients_eq_zero_of_det_ne_zero` (lines 94–103), universal final conjunct at lines 122–126 | Holds. For a square matrix over a field, `det A != 0` makes `A` invertible, and `A c=0` therefore gives `c=0`. No characteristic restriction is used. |

## Independent matrix and kernel computation

The Lean monomial order is

```text
[X^3, X^2Y, X^2Z, XY^2, XYZ, XZ^2, Y^3, Y^2Z, YZ^2, Z^3].
```

For `P_i=(i,0,1)`, direct substitution gives row

```text
A_i = [i^3, 0, i^2, 0, 0, i, 0, 0, 0, 1].
```

Thus columns 1, 3, 4, 6, 7, and 8 are zero. The requested witness is `e_8`, the coefficient vector with its only 1 at zero-based coordinate 8. The ten evaluations were recomputed individually:

| `i` | `i^3` | `i^2` | `i` | `1` | `A_i e_8` |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 0 | 0 | 1 | 0 |
| 1 | 1 | 1 | 1 | 1 | 0 |
| 2 | 8 | 4 | 2 | 1 | 0 |
| 3 | 27 | 9 | 3 | 1 | 0 |
| 4 | 64 | 16 | 4 | 1 | 0 |
| 5 | 125 | 25 | 5 | 1 | 0 |
| 6 | 216 | 36 | 6 | 1 | 0 |
| 7 | 343 | 49 | 7 | 1 | 0 |
| 8 | 512 | 64 | 8 | 1 | 0 |
| 9 | 729 | 81 | 9 | 1 | 0 |

The only potentially nonzero columns are 0, 2, 5, and 9. Rows 0–3 restricted to columns `[9,5,2,0]` form

```text
[[1,0,0,0],
 [1,1,1,1],
 [1,2,4,8],
 [1,3,9,27]],
```

whose Vandermonde determinant is `12`. Therefore the exact rational rank is 4, the kernel dimension is 6, `e_8` is a nonzero kernel element, and the 10-by-10 determinant is zero. A deterministic exact-integer/Fraction calculation independently returned rank 4 with pivot columns `[0,2,5,9]`, minor determinant 12, all ten dot products 0, and full determinant 0. This was an arithmetic check, not a Lean build or scientific trial.

## Matrix orientation and determinant repair

The orientation is correct and load-bearing. `evaluationMatrix points i j` is monomial `j` at point `i`; Mathlib's `mulVec` therefore computes

```text
(A *ᵥ c)_i = sum_j A_ij c_j = cubicValue c (points i).
```

The witness is consequently a **right** kernel vector. Transposing the matrix without also changing the multiplication convention would not encode coefficient evaluation, even though singularity itself would survive transposition. The theorem does not make that mistake.

For the repair, let `A=evaluationMatrix points`. The vanishing premise is exactly `A c=0`. Over any field, `det A != 0` gives `A^-1`, hence

```text
c = A^-1 (A c) = A^-1 0 = 0.
```

This works in every characteristic. The concrete numeral points are asserted only over `Q`; the source does not incorrectly claim that `0,...,9` remain distinct in small characteristic. The generic repair does not require a separate distinctness hypothesis because nonzero determinant already excludes repeated or zero rows.

## Projective-scaling boundary

`Point3` is a raw triple, not a projective quotient, exactly as the target's proof map says. For a valid nonzero scaling `lambda`, every monomial has total degree 3, so

```text
cubicMonomials (lambda p) = lambda^3 * cubicMonomials p.
```

Scaling each representative by nonzero `lambda_i` left-multiplies the evaluation matrix by a diagonal matrix with entries `lambda_i^3`. Its determinant is multiplied by `product_i lambda_i^3`, a nonzero scalar, and its right kernel is unchanged. Vanishing and the determinant zero/nonzero boundary are therefore invariant under valid projective rescaling.

Scaling by zero is not a projective equivalence. The raw `Point3` type permits the zero triple, but any evaluation matrix containing it has a zero row and cannot satisfy the repair's nonzero-determinant premise. No false projective conclusion follows. Formal quotient construction and well-definedness on projective classes remain deliberately unproved.

## Reducible and singular witness

The witness is

```text
F(X,Y,Z) = Y Z^2 = Y * Z * Z.
```

It is reducible and nonreduced. Its gradient over `Q` is

```text
(dF/dX, dF/dY, dF/dZ) = (0, Z^2, 2 Y Z),
```

which vanishes with `F` at the projective point `[1:0:0]`; hence the cubic is singular and not an elliptic cubic. The Lean declaration does not formalize reducibility, derivatives, discriminants, or nonsingularity. That omission is an explicit scope boundary, not support for a nonsingular witness.

## Narrow JKSST comparison

Primary source checked: Jacobson–Koblitz–Silverman–Stein–Teske, *Analysis of the Xedni Calculus Attack*, author-hosted PDF, especially Section 3.2, SHA-256 `981bf955f7aecc5df4f271837f6653bd7666e5026f59df44196609d4a1dd6bc7`.

Section 3.2 says:

- Step 1 fixes `2 <= r <= 9` and defines an `r`-by-10 matrix whose rows evaluate the ten general cubic monomials at the `r` points.
- Its displayed column order is a permutation of the Lean order. Column permutation preserves rank and determinant zero/nonzero (up to determinant sign in the square case), so this causes no semantic mismatch.
- Step 2 explicitly requires the chosen points to make that matrix have rank `r`.
- Remark 2 uses the one-way implication **rank `r` implies the points are distinct**. It does not use, state, or suggest the converse.
- Remark 4 explains why the rank-`r` premise is needed for the later coefficient lifting.
- The paper separately requires a kernel coefficient vector that defines an elliptic curve with nonzero discriminant over each small field.

The reviewed source note is therefore accurate: JKSST never infers rank from distinctness. Any later description saying that this countermodel corrects such an inference in JKSST would be false and should be rejected. The Lean example has `r=10` and rank 4. In JKSST's actual range, full row rank `r<=9` still leaves a nonzero coefficient kernel of dimension at least `10-r`; in the Lean square repair, nonzero determinant instead makes the coefficient kernel trivial. The result is a nearby guardrail, not a model, erratum, or refutation of JKSST's rank-tested families.

## Hypothesis delta and missing bridges

Relative to the frozen target claim, the hypothesis-delta table is empty: every binder and load-bearing premise in the declaration is stated by the target—`Fin 10`, rational concrete representatives, an arbitrary field `K`, ten raw coordinate triples, a coefficient vector, nonzero determinant, and ten vanishing equations. There is no added `Fact`, characteristic assumption, finiteness assumption, distinctness premise for the generic repair, or assumed conclusion.

The following are explicit model boundaries rather than hidden hypotheses:

| Boundary | Status |
| --- | --- |
| Raw triples to genuine projective points | Not formalized; nonzero-rescaling invariance checked algebraically above. |
| Kernel cubic to nonsingular elliptic cubic | Not formalized; the concrete witness is reducible and singular. |
| Square ten-point condition to JKSST's rectangular `r<=9` condition | Not claimed; only the linear-algebra analogy is valid. |
| A finite rank fact to an ECDLP attack, probability, or implementation claim | No bridge exists in this target and none is inferred. |

## Controls

1. **Drop determinant nonzero.** The concrete matrix itself is the countercontrol: ten distinct normalized representatives, rank 4, six-dimensional kernel, determinant zero.
2. **Replace rank with distinctness.** The same example disproves the replacement; literal and projective distinctness do not remove `e_8` from the kernel.
3. **Change representative by nonzero scaling.** Rows scale by nonzero cubes, preserving rank and the right kernel.
4. **Allow zero scaling/zero triple.** This is not projective scaling and forces a zero row; it cannot satisfy the repair premise.
5. **Demand a nonsingular cubic.** The supplied witness fails that stronger premise at `[1:0:0]`, so the target cannot prove too much about elliptic cubics.
6. **Change field characteristic.** The determinant implication remains valid, but the concrete rational distinctness witness is not silently transferred to small characteristic.

Static inspection found no `sorry`, `admit`, custom `axiom`, `unsafe`, or `native_decide` token in the theorem source. The configured project audit is fail-closed over nonstandard axioms, but neither static inspection nor configuration is an executed target audit. The later Coordinator report establishes only that this module built in the exact run; the generated named-declaration audit remains uninspected and the overall run failed elsewhere.

## Unresolved items

- For exact Lean run `41503944712`, module build success is Coordinator-reported, while the overall run failed in other modules. Its source binding, named-declaration audit, and axiom evidence remain unread; no exact-run or full-gate pass is claimed.
- No independent binary/kernel rechecker was run.
- Projective quotienting and nonsingularity/discriminant facts are outside Lean here.
- No result about JKSST's actual selected points, coefficient-lifting interface, elliptic curves, success probability, ECDLP complexity, or an implementation follows from this target.

Subject to those stated boundaries, joint B holds.
