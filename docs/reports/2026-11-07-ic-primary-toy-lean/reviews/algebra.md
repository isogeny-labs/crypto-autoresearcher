# Blind algebra review: primary n=13 toy curve

**Verdict: holds** for the archived finite field and point arithmetic claims. This is an independent algebraic re-derivation only; I did not inspect the Lean declaration or establish that its encoded operations implement these formulas.

## Source identity and scope

- Cryptanalysis source checkout HEAD: `612427ead3d47565b92da3e663739d5c17ce71ed`.
- Assigned proof-input commit: `83d750c7a0` (task identifier supplied by Coordinator; its contents were not read).
- Archive: `baseline/primary.jsonl`, SHA-256 `3886d486bf05ba476c00a67c9d7b20ed07250862273019a3b59195a22d60b973`. Its nine rows repeat scalars 1046, 606, 861 across the three named candidate families. I used it only to identify those families and archived scalar values; it is not independent evidence of their correctness.
- Workloads and SHA-256: `026858681e66.json` `17195695053cd3f925106b06b8a5db0e7c8b9b981416e769f31c0e774b024908`; `398002869ca3.json` `e87fc86e41b3a4c10e6213b8a3310f09b3bf64a8e442ced6c22e1894fa2a5714`; `aa4b90819f2f.json` `302aeb0cfebef04842813ec4be8cbd509d3c93624cb7419642c6b7276e40979d`.
- Candidate manifests and SHA-256: `IC1N13Ckb1fb8PDP3xlRCsampleLAgaussTDpdpISO0hb34ead1a1d66.json` `08e925fb729990a73a2f738ddbd29dc74bceea09aad0c4e05080891d5da77083`; `IC1N13Ckb1fb8PDP3xlRCsampleLAgaussTDpdpISO0h9cd5348f2b43.json` `3a2b0fd1d83ce977a4e47f6e12f894aca222f4ad954006fc93ae6b8f7c16d9da`; `IC1N13Ckb1fb4PDP3xlRCsampleLAgaussTDpdpISO0h7e9e3a2574ab.json` `62c9e48895d8621c86e9085588ee443fb9c8a1bfe3c46e861ebe630f2c078f0f`. All three declare the same field, curve, generator, and subgroup order.

## Independent method

The manifest defines bit `i` as the coefficient of `z^i` and modulus `f=z^13+z^5+z^2+z+1`, bitmask `8231` (`0x2027`). I wrote a fresh, ephemeral Python 3 calculation in the shell; no producer code or proof file was imported. Field addition was integer XOR. Multiplication was binary shift/XOR with reduction by `8231` whenever bit 13 appeared. Nonzero inversion used `a^8190` by repeated squaring. Exhaustively, `a * a^8190 = 1` for every integer `a` from 1 through 8191, so all nonzero encoded residues have inverses under this multiplication. Also `z^8192 = z`.

For `E: y²+xy=x³+1`, I used infinity as `None`, inverse `-(x,y)=(x,x+y)`, and, for `x1 != x2`,

`lambda=(y1+y2)/(x1+x2)`, `x3=lambda²+lambda+x1+x2`, `y3=lambda*(x1+x3)+x3+y1`.

For doubling at `x != 0`, I used `lambda=x+y/x`, `x3=lambda²+lambda`, `y3=x²+(lambda+1)*x3`. Equal x coordinates with `y1+y2=x1` return infinity. I applied binary double-and-add to `G=(2995,1571)` without reducing the scalar modulo 2003. The curve residual was computed independently as `y²+xy+x³+1`; zero means on curve.

## Results

| Scalar | Computed `[scalar]G` | Check |
| ---: | --- | --- |
| 2003 | infinity | subgroup-order claim holds for G |
| 1045 | (1082, 7387) | differs from first target |
| 1046 | (2659, 1282) | equals workload `026858681e66` target |
| 1047 | (7851, 3095) | differs from first target |
| 605 | (560, 1201) | differs from second target |
| 606 | (6749, 6034) | equals workload `398002869ca3` target |
| 607 | (6721, 2942) | differs from second target |
| 860 | (3537, 3092) | differs from third target |
| 861 | (4412, 6211) | equals workload `aa4b90819f2f` target |
| 862 | (5120, 5987) | differs from third target |

The residual is zero for G and all three recorded targets. The altered first coordinate pair `(2659,1283)` has residual `2658`, so it fails the curve equation and differs from `[1046]G`. The negative controls specified in the review plan were 1045, 605, 860, and this altered pair; I additionally checked the following adjacent scalars.

## Limits and attestation

`joints_owned`: algebraic re-derivation of the source constants, three scalar multiples, `[2003]G`, adjacent scalar controls, and altered coordinate. The calculation checks the finite model specified by the manifests. It does not audit the producer's Lean statement, kernel proof, implementation bridge, benchmark execution, or archived run provenance. In particular, the claim that a Lean-encoded multiplication and point law coincide with the polynomial field and curve law above remains a separate review obligation.

`sources_read` (complete task source list): `/var/tmp/crypto-auto-ic-primary-lean-20261107/docs/reports/2026-11-07-ic-primary-toy-lean/review_plan.md`; `/var/tmp/cryptanalysis-dashboard-source-20261107/experiments/ic-bench/baseline/primary.jsonl`; the three workload JSON files and three candidate JSON files named with hashes above, all under that checkout's `experiments/ic-bench/` directory. I read the full review plan, including its review boundaries and specified controls. I did not read the producer Lean file, `source.md`, `machine-check.json`, dashboard audit, sibling report, or any other proof file. No sibling review output was accessed before filing this verdict.
