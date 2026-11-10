# Exact source for the primary n=13 toy-curve target

Cryptanalysis `experiments/ic-bench/README.md` describes the primary suite as
nine complete, verified index-calculus DLP runs on the binary Koblitz curve
`y² + xy = x³ + 1`, using three frozen public targets with three factor-base
configurations each. A complete receipt records a recovered scalar and checks
`[scalar]G = Q`. The source tree inspected here is cryptanalysis commit
`612427ead3d47565b92da3e663739d5c17ce71ed`.

The exact committed source bytes used for the finite Lean certificate are:

| path under cryptanalysis | SHA-256 |
| --- | --- |
| `experiments/ic-bench/baseline/primary.jsonl` | `3886d486bf05ba476c00a67c9d7b20ed07250862273019a3b59195a22d60b973` |
| `experiments/ic-bench/workloads/026858681e66.json` | `17195695053cd3f925106b06b8a5db0e7c8b9b981416e769f31c0e774b024908` |
| `experiments/ic-bench/workloads/398002869ca3.json` | `e87fc86e41b3a4c10e6213b8a3310f09b3bf64a8e442ced6c22e1894fa2a5714` |
| `experiments/ic-bench/workloads/aa4b90819f2f.json` | `302aeb0cfebef04842813ec4be8cbd509d3c93624cb7419642c6b7276e40979d` |

The candidate manifests in those receipts all specify polynomial-basis
`F₂[z]/(z¹³ + z⁵ + z² + z + 1)`, the curve `y² + xy = x³ + 1`, generator
`G=(2995,1571)`, and subgroup order `2003`. Each workload contains one target:

| workload | scalar `s` | encoded point `Q` |
| --- | ---: | --- |
| `026858681e66` | 1046 | (2659, 1282) |
| `398002869ca3` | 606 | (6749, 6034) |
| `aa4b90819f2f` | 861 | (4412, 6211) |

The Lean target states exact equalities in a separately written bitmask field
and affine point implementation. It checks the generator and points against
the encoded curve equation, `[2003]G = O`, and the three `[s]G = Q` values.
Nearby scalar and coordinate controls fail. The statement is limited to these
encoded computations. It is not a theorem that the historical processes ran,
that the recorded wall times are reproducible, or that this implementation
models every point of an abstract elliptic-curve group.
