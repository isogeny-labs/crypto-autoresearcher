# Endosweep batch 7: discriminant certificate fidelity review

Reviewed commit: `23c5aeca09f8f512d90755193660c1b2aa509714`; preregistered plan: `d549627b2737cd94bbd8a9ab26c248a66319d94b`; archival task: T-1739. This technical packet changes no hypothesis, evidence, or scientific decision record. Its source, blind, and machine inputs remain separate.

## Checked result

The exact recorded integers for brainpool/brainpoolP512r1 satisfy `q + 1 - t = h*n` and `4q - t² = 557*p54*p98`. The blind calculation independently obtained the candidate `D_K = -(4q-t²)`, `f = 1`, `L = 512`, and `min_nonscalar_degree(D_K) = (|D_K|+1)/4 >= 2^510`. Its one-digit mutation breaks multiplication; its composite-base counterexample shows that multiplication alone does not establish a fundamental discriminant. The source reviewer found byte-identical Lean generation, 13 passing source-manifest hashes, and 53 passing source checks, including the frozen factor/snapshot chain and external parameter comparison.

| Subclaim | Machine status | Fidelity / review outcome | Evidence |
| --- | --- | --- | --- |
| Recorded integer identities, factor product, candidate discriminant and degree bounds | Passed in named hosted Lean receipt; independent exact arithmetic holds | Faithful to the numeric target at its stated recorded-integer scope; independently corroborated | [Machine evidence](machine-evidence.md), [blind report](reviews/blind/report.md), [source report](reviews/source/report.md) |
| `D_K` fundamental if both listed large bases are prime | Passed as an **implication** whose premise is explicit in `DkCert.Statement` | Conditional statement is faithful; premise was not independently discharged in this review | [Lean target](../../../formal/targets/endosweep-dk-exact-batch7-discriminants.yaml), source report, blind composite counterexample |
| `t` is the actual trace of the named curve; `End(E)` has the asserted order and degree equals norm | Not a declaration in this target | Open bridge; the source parameter match is useful but does not prove these mathematical links | Source report, [review plan](review-plan.md) |
| Historical PARI primality run and exact source-checkout custody | Not certified by the named Lean theorem | Inconclusive: retained metadata/prose, no archived primality proof or authenticated run receipt; builder records but does not enforce the std-curves pin or clean input bytes | Source report |

The top-level review outcome is **inconclusive for the named-curve interpretation and unconditional fundamental-discriminant claim**. The arithmetic subclaim holds at its recorded-integer scope. The named Lean theorem itself states the primality implication, not an unconditional proof of the two large factors. No full end-to-end curve or cryptanalytic conclusion is inferred from it.

## Specific corrections and next checks

1. `formal/targets/endosweep-dk-exact-batch7-discriminants.yaml` notes call the odd-exponent product a “squarefree part” in an unconditional list. The generated Lean header and target `claim` field correctly make squarefreeness conditional. Add a new corrected target/version and fresh receipt rather than silently changing the frozen target.
2. Bind the actual `std-curves` input bytes and enforce the declared revision and clean tree in `research/endosweep_dk_exact_20261016/build_dk_exact.py`. Rerun its focused source tests after that code change; historical records remain immutable.
3. Retain or independently regenerate checkable certificates for the two large factors, then assess the curve trace and endomorphism bridge separately. A new proof must bind these inputs to the named curve rather than only reprove the integer equalities.

The review plan was committed before reviewer dispatch. Reviewer reports contain paths read, joint verdicts and isolation attestations. The automated `check_review_independence.py` expects a structured plan; this round's committed Markdown plan cannot be passed to it as a green check. Manual attestation review found no declared cross-reading, but that procedural limitation prevents a `validated_scoped` outcome. The [diagram](review-boundary.svg) and [inspected PDF](report.pdf) show the claim boundary. No canonical performance graph changes: this review makes no measurement or speed claim, and the batch 7 `dk_exact.svg` / `ecm_effort.svg` graph sources were checked as historical research visuals, not altered by this arithmetic review.
