# Frobenius congruence: independent proof and claim-fidelity review

**Claim:** `THM-SEMAEV-FALL1-LEMMA-1` at source commit `36ee18fa3d0e6d527e1b36e3e2a09180c5fcf055`. **Review plan:** SHA-256 `86d181656375f95f5aa53df01219acf91d6ff4402225c114f264e74d628db735`. **Named Lean declaration:** `CryptoResearch.Semaev.pow_q_eq_frobeniusTwist_mod_fieldEquations`.

The polynomial congruence holds for the stated characteristic-power exponent, the named Lean statement matches the source lemma, and the exact hosted build and axiom audit pass on pinned inputs. Three independently sealed review joints cover those distinct facts. `tools/check_review_independence.py` reports `PASS: 3 report(s), every joint owned and attested, blindness respected, controls declared` against the unmodified prospective plan.

![Three-joint evidence map](evidence-map.svg)

## Claim-level findings

| Claim or control | Evidence | Judgment |
| --- | --- | --- |
| For `q=p^e`, `g^q-g^phi` lies in `(X_i^q-X_i)` over a characteristic-`p` coefficient ring | J1 blind finite-support derivation; J2 statement comparison; J3 named Lean receipt | **Holds** at the polynomial congruence scope. |
| Named Lean declaration expresses source Lemma 1 | J2 pinned source/target/type comparison; J3 exact input hashes | **Holds** for Lemma 1 statement fidelity. Lean is slightly more general in coefficient ring and admits harmless `e=0`/empty-variable cases. |
| Exact named Lean proof was built and audited | GitHub run [42665763089](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/42665763089), artifact 13699385811, published/downloaded ZIP SHA-256 `e081ab350fecd5394080b89f8d09a570a2a7c031e344d3b94a08195eb08faf81`; J3 receipt replay | **Holds** on synthetic merge tree `3abcd77ef51d63a79fcf02fcfd172d7d283babc3`, whose relevant inputs equal head `d25ed16abcaaa942857e5e3a6d72637aaf8aa5c5`. Audit reports 1,313 theorems with only `propext`, `Classical.choice`, `Quot.sound`. |
| Literal equality in `K[X]` without quotienting | J1 `F_2[x]`, `g=x`, `q=2` | **False:** `x²-x` is nonzero as a polynomial and is an ideal generator. |
| Same congruence for a `q` unrelated to characteristic | J1 additive correction, `F_2[u]/(u²)` witness for `q=3` and `g=x+y` | **False:** generators vanish under `x=1+u,y=1`, while the cross-term residue maps to `u ≠ 0`. The original sealed J1 report's `F_4` witness was invalid; its separate correction is the operative finite witness. |
| Concrete descended-Semaev redundancy, fall-degree, semi-regularity, or solver complexity | J2 scope inspection; no instantiation or propagation theorem in this named declaration | **Open at this joint.** A system-level descent bridge and separately reviewed degree/complexity statements are required. |

## Provenance and limits

The research source, target specification, Lean file, toolchain file and Lake manifest hashes in the plan match the authenticated J3 receipt. Its 106 workspace inputs match 105 tracked files plus the deterministically generated root module; 10 verifier inputs match the archived merge tree. Before/after dependency pin records agree on 10 clean Git revisions. J3's wrong-name, changed-hash, and missing-audit controls reject. A synthetic self-consistent success JSON passes the consistency checker, so the GitHub run and artifact digest are essential provenance; the checker alone does not authenticate execution.

The source's Corollary 1 membership and degree statements have separate Lean declarations and were outside this named-theorem review. The present review neither changes a research ledger decision nor certifies a descended Semaev system's solving degree. The next proof obligation is to bind an explicit descended-system construction to the coefficientwise Frobenius equations, then review any degree statement on that construction separately.

## Records

- Prospective [review plan](../review-plan.yaml) and [blind card](../blind-card.md).
- Sealed [J1 algebra review](../reviews/TASK-20261109-b2993e/report.md) with [operative correction](../reviews/TASK-20261109-b2993e/correction-1.md), [J2 source/type review](../reviews/TASK-20261109-ca597b/report.md), and [J3 hosted machine review](../reviews/TASK-20261109-115f30/report.md).
- Original sealed source packets and chronology corrections remain under `../review-source-packets/`; the hosted ZIP is available from artifact 13699385811 and locally in J3's SHA-verified packet. No new Lean or cloud job was launched for synthesis.
