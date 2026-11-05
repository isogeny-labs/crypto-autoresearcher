# Semaev Frobenius-collapse theorem: semantic review

**Review date:** 2026-11-01 UTC
**Claim:** `THM-SEMAEV-FALL1-LEMMA-1`
**Named Lean theorem:** `CryptoResearch.Semaev.pow_q_eq_frobeniusTwist_mod_fieldEquations`
**Archive task:** `TASK-20261101-f62009`

## Result at the stated scope

For a characteristic-`p` commutative ring and `q=p^e`, the Lean theorem proves that `g^q` and the coefficientwise `q`-Frobenius twist of `g` have the same image in the quotient by `(x_i^q-x_i)`. The source claim's field/prime assumptions are instances of the Lean hypotheses. Two independent reviews agree on the identity: one rederived it from the statement without reading the proof or source note; the other checked the Lean induction and source crosswalk. The [hosted formal run](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41282682489) records `machine_verified`, `build_passed: true`, `axiom_audit_passed: true`, and no forbidden constructs for the named target.

The theorem's type does not state non-semi-regularity, a Semaev-specific system result, a first/last-fall-degree bound, or solver complexity. The source note's section 0a corrects an older literature-bound attribution. Corollary 1's membership and degree arithmetic are separate Lean declarations outside this named target. These boundaries are material when citing the result.

## Machine evidence and pinning

| Item | Checked value |
| --- | --- |
| Hosted source commit | `6475884a98b4a0fd0f50ddc7d8b0c82855b74531` |
| Target YAML SHA-256 | `e2b083a617fadec962d855e8dde425fef1fe010a15ea1652098ae4e57096ce7c` |
| Lean theorem file SHA-256 | `f408877908fc156006c2b24cb38b26610461e03093ff88aadbf11d4bc2c2e398` |
| Source note SHA-256 | `11b61f4f4bdaed0c323ec852f19fc4c0a7ff3972715bfe637604fb675db7fee4` |
| Target receipt | `formal-verification-receipts/semaev-frobenius-collapse.json` from run `41282682489` |
| Target axiom audit | Standard `propext`, `Classical.choice`, `Quot.sound`; no extra axiom or `sorry` reported |

The three file hashes were recomputed in this worktree. `git diff` found no change to those paths between the hosted source commit and this review branch's base. The hosted receipt still marks `semantic_review.status: pending`; this packet documents an independent review and does not rewrite that machine field or make an official experiment-status decision. A future formal workflow at the PR head is a distinct current-head gate.

## Review composition

| Joint | Owner | Result |
| --- | --- | --- |
| Quotient proof: constants, sums, variable multiplication | `TASK-20261101-8995a6` | Holds by source inspection; hosted kernel/axiom audit supplies machine check. |
| Named theorem versus producer's Lemma 1 | `TASK-20261101-8995a6` | Holds for the congruence; later interpretation is outside the type. |
| Blind finite-support rederivation | `TASK-20261101-df39aa` | Holds; checked mixed monomials, extension coefficients, and `q=1`. |

The blind reviewer read only the blind handoff. Neither reviewer read the other's report. The false controls fail as required: in characteristic zero, `(x+y)^2-(x^2+y^2)=2xy` is nonzero modulo `(x^2-x,y^2-y)`; without field equations, `x^2≠x` in `F₂[x]`. The repository's `check_review_independence.py` passed with two YAML attestations, every joint owned, blindness respected, and controls declared.

## Proof and dependency diagram

```mermaid
flowchart LR
  A[Finite-support polynomial g] --> B[Characteristic p: g^q = sum c_a^q x^(q a)]
  B --> C[Quotient by I_q: x_i^q = x_i]
  C --> D[g^q congruent to coefficientwise Frobenius twist]
  D --> E[Named Lean theorem and hosted axiom audit]
  D -. separate argument needed .-> F[Semaev system regularity and solving-degree claims]
```

The dashed edge is a research dependency, not a proved implication. No performance measurement is claimed by this packet, so a performance graph would have no measured axes or data.

## Reproduction

1. Fetch hosted run `41282682489` and its `formal-verification-receipts` artifact; inspect `semaev-frobenius-collapse.json` for the named theorem, source hashes, build status, and axiom audit.
2. From this branch, run `python3 tools/check_review_independence.py --plan coordination/formal-reviews/semaev-frobenius-collapse-20261101/source-handoff.yaml --reports coordination/formal-reviews/semaev-frobenius-collapse-20261101/blind-attestation.yaml coordination/formal-reviews/semaev-frobenius-collapse-20261101/source-attestation.yaml`.
3. Read `blind-report.md` and `source-report.md` separately, then compare their attestation blocks to the corresponding YAML files.

The report PDF is a compact shareable rendering of this packet; the Markdown and two reviewer reports remain the source of technical detail.
