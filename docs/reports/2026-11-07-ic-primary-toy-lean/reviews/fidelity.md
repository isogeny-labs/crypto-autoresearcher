# Independent source-fidelity review: primary n=13 encoded certificate

## Scope and input identity

Owned joint: source identity and statement fidelity for Conductor T-1866. I reviewed crypto-autoresearcher proof-input commit `83d750c7a03bac3abc73800740d39944e526decc` against cryptanalysis commit `612427ead3d47565b92da3e663739d5c17ce71ed`. The cited declaration is `CryptoResearch.IC.PrimaryToyCurve.primary_archive_certificate` in `formal/CryptoResearch/IC/PrimaryToyCurve.lean`; the target is `formal/targets/ic-primary-toy-curve-20261107.yaml` (task `T-1863`, claim `IC-PRIMARY-N13-ENCODED-SCALARS-20261107`).

| Input at the above revisions | SHA-256 |
| --- | --- |
| crypto-autoresearcher `formal/CryptoResearch/IC/PrimaryToyCurve.lean` | `a03b27a49db206f14dc6be74b0624ebb48e9270c6708b8cd70452d82bf5cd187` |
| crypto-autoresearcher `formal/targets/ic-primary-toy-curve-20261107.yaml` | `6bad93d3952b537f7d53faca796ee4ea2c12310ef18781d5aa5d823eb37c9137` |
| crypto-autoresearcher `docs/reports/2026-11-07-ic-primary-toy-lean/source.md` | `4a216bb6656b11eeeb21f9e40df5c661f044a981a1025669aad6cd295a030675` |
| crypto-autoresearcher `docs/reports/2026-11-07-ic-primary-toy-lean/review_plan.md` | `8b7c8c7b7d4fca88ab75762111afe72f9af6eec6ae77042e98114a72259896bd` |
| cryptanalysis `experiments/ic-bench/baseline/primary.jsonl` | `3886d486bf05ba476c00a67c9d7b20ed07250862273019a3b59195a22d60b973` |
| cryptanalysis `experiments/ic-bench/workloads/026858681e66.json` | `17195695053cd3f925106b06b8a5db0e7c8b9b981416e769f31c0e774b024908` |
| cryptanalysis `experiments/ic-bench/workloads/398002869ca3.json` | `e87fc86e41b3a4c10e6213b8a3310f09b3bf64a8e442ced6c22e1894fa2a5714` |
| cryptanalysis `experiments/ic-bench/workloads/aa4b90819f2f.json` | `302aeb0cfebef04842813ec4be8cbd509d3c93624cb7419642c6b7276e40979d` |
| cryptanalysis `experiments/ic-bench/candidates/IC1N13Ckb1fb8PDP3xlRCsampleLAgaussTDpdpISO0hb34ead1a1d66.json` | `08e925fb729990a73a2f738ddbd29dc74bceea09aad0c4e05080891d5da77083` |
| cryptanalysis `experiments/ic-bench/candidates/IC1N13Ckb1fb8PDP3xlRCsampleLAgaussTDpdpISO0h9cd5348f2b43.json` | `3a2b0fd1d83ce977a4e47f6e12f894aca222f4ad954006fc93ae6b8f7c16d9da` |
| cryptanalysis `experiments/ic-bench/candidates/IC1N13Ckb1fb4PDP3xlRCsampleLAgaussTDpdpISO0h7e9e3a2574ab.json` | `62c9e48895d8621c86e9085588ee443fb9c8a1bfe3c46e861ebe630f2c078f0f` |

The archive contains nine JSONL rows, one for each pairing of three workload IDs and three candidate IDs. Each row says `status=complete`, `verified_scalar=true`, `subgroup_order="2003"`, and records the corresponding workload scalar in its verified descent. These are source records, not a Lean proof of their historical execution.

## Statement and definition comparison

All three candidate manifests agree on characteristic 2, degree 13, polynomial basis with bit `i` encoding coefficient of `z^i`, modulus exponents `[13,5,2,1,0]`, curve model `y^2+x*y=x^3+a2*x^2+a6` with `a2=0, a6=1`, generator `(2995,1571)`, and subgroup scalar `2003`. The Lean `modulus` is `2^13+2^5+2^2+2+1=8231`, exactly the candidate polynomial's bitmask. Its `onCurve` checks `y²+xy=x³+1` using XOR as addition and its encoded `fm` multiplication. The Lean `generator` is `some (2995,1571)`.

| Workload ID | Workload target `(s,x,y)` | Archive rows | Lean target equality |
| --- | --- | ---: | --- |
| `026858681e66` | `(1046,2659,1282)` | 3 | `scale 1046 generator = some (2659,1282)` |
| `398002869ca3` | `(606,6749,6034)` | 3 | `scale 606 generator = some (6749,6034)` |
| `aa4b90819f2f` | `(861,4412,6211)` | 3 | `scale 861 generator = some (4412,6211)` |

The target spec and cited theorem are closed conjunctions of equalities and inequalities about those fixed encodings. They have **no free variables, hypotheses, or universal quantifiers**. `scale` uses twelve bits of scalar fuel, enough for all four stated scalars, including 2003. `none` represents infinity. The statement checks `scale 2003 generator = none`; it does not state exact order 2003. The three target coordinates are conclusions, not definitions of `scale`, and none of the asserted equalities appears as an assumption. `archived_points_on_curve` also checks all three target points on the encoded curve, but the cited `primary_archive_certificate` includes only the generator's `onCurve` conjunct; target curve membership is available from that separate theorem rather than the cited declaration.

The Lean definitions implement the standard binary affine cases on `Option (Nat × Nat)`: identity at `none`; equal-`x` inverse test `y1 XOR y2 = x1`; doubling slope `x+y/x`; distinct-`x` slope `(y1+y2)/(x1+x2)`; and the corresponding `a2=0` result-coordinate formulas. `inv` uses exponent `2^13-2` in the same encoded multiplication. The finite theorem checks particular evaluations of these definitions. It does not establish that the modulus is irreducible, that `inv` is correct for all nonzero 13-bit elements, that these formulas form a group law on the curve, or that this separate Lean implementation is extensionally identical to the cryptanalysis program. Those bridges are necessary for a generic field, exact subgroup-order, or implementation-correctness claim; the target spec explicitly limits itself to encoded computations.

## Worked attacks and controls

1. **Transcription attack.** I compared each of the five modulus exponents, both curve coefficients, both generator coordinates, subgroup scalar, and all nine scalar/target coordinates against the committed candidate and workload files. No mismatch was found. In particular the scalar `606` belongs to workload `398002869ca3`, while `861` belongs to `aa4b90819f2f`; the archive repeats each in exactly three candidate rows.
2. **Circularity and quantifier attack.** The target coordinates occur on the right side of closed equality propositions; `scale`, `add`, `fm`, and `inv` do not read a target table. There is no hypothesis that grants `[s]G=Q`, no universal point claim, and no generic order assertion. Thus the encoded equalities are not won by an assumed conclusion. The bare claim `scale 2003 generator = none` would also hold in a degenerate stipulated operation; the missing field and group-law bridges prevent interpreting this conjunct alone as exact subgroup-order evidence.
3. **Known-false neighboring cases.** The source proves `scale 1045 generator ≠ (2659,1282)`, `scale 605 generator ≠ (6749,6034)`, `scale 860 generator ≠ (4412,6211)`, and `onCurve (2659,1283)=false` in `nearby_controls_rejected`, and the cited certificate includes all four. These test that the fixed statement does not accept adjacent scalars or the altered first target coordinate. They do not test every scalar or every malformed point.

The proof has no claim about wall time, operation counts, nine historical process executions, factor-base quality, index-calculus success, or comparative speed. The archive records some of these observations, but the Lean theorem does not validate their provenance or measurement.

## Pinned Lean inspection

Toolchain pin: `formal/lean-toolchain` specifies `leanprover/lean4:v4.35.0`. I used `/var/tmp/binstd-elan/toolchains/leanprover--lean4---v4.35.0/bin/lean`, which reports Lean 4.35.0, release commit `eb6cafb7290e8bd5f2937522d8d804f58f02bafc`. I piped the exact source file followed by `#print CryptoResearch.IC.PrimaryToyCurve.primary_archive_certificate` and `#print axioms` for that declaration and each of its four helper theorems into `lean --stdin` with `LEAN_PATH=/var/tmp/binstd-elan/toolchains/leanprover--lean4---v4.35.0/lib/lean`. Both runs exited 0. The elaborated type is exactly the closed ten-conjunct type described above: modulus equality, generator curve test, 2003-to-infinity equality, three target equalities, three adjacent-scalar inequalities, and the altered-coordinate false test. Its printed proof references `archived_points_on_curve`, `generator_2003_to_infinity`, `archived_primary_targets`, and `nearby_controls_rejected`. All five `#print axioms` outputs report `[propext]` only, a Lean standard axiom; no custom axiom appears. This source-fidelity check does not replace the Coordinator's kernel and controls joint.

## Review attestation

- `joints_owned`: source identity and statement fidelity only.
- `sources_read`: `/var/lib/spot-codex/home/skills/review-evidence/SKILL.md`; `/var/lib/spot-codex/home/skills/review-evidence/references/lean-review.md`; `/var/lib/spot-codex/home/memories/MEMORY.md` (targeted search returned no relevant match); crypto-autoresearcher `formal/CryptoResearch/IC/PrimaryToyCurve.lean`, `formal/targets/ic-primary-toy-curve-20261107.yaml`, `docs/reports/2026-11-07-ic-primary-toy-lean/source.md`, `docs/reports/2026-11-07-ic-primary-toy-lean/review_plan.md`, `formal/lean-toolchain`, `formal/lakefile.toml` and `formal/lake-manifest.json` (pin search only); cryptanalysis `experiments/ic-bench/baseline/primary.jsonl`, the three exact `workloads/*.json` and three exact `candidates/*.json` listed above, and `experiments/ic-bench/README.md` (targeted search only).
- `sibling_report_access`: none. I did not open or search the blind algebra review, its path, or any sibling verdict.
- `blind_rederivation_compliance`: not applicable to this assigned joint; the blind algebra reviewer owns independent recomputation. I read the producer Lean file as expressly allowed by the plan.
- `verdict`: **holds** for source fidelity of the finite, encoded target claim. The field, group-law, and program-equivalence bridges remain outside this claim and are not certified by this verdict.
