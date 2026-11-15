---
id: SA-23c
campaign: semaev-alternatives-20261105
round: 6
parent: SA-23b (verdict INCONCLUSIVE: mechanism confirmed, frozen law class failed; main-session audit results/SA-23b/audit/AUDIT.md)
title: "Held-out test of the post-hoc Frobenius law for y^2 = x^3 + t^12 + 1, and enumeration at p = 229"
status: preregistered
frozen_on: 2026-11-12
executor_tier: sonnet
results_path: experiments/semaev-alternatives-20261105/results/SA-23c/
---

# SA-23c

**Why.** SA-23b confirmed the Jacobi-sum mechanism. At p = 157, 181 and 193 the Gram rank was in {R_J - 1, R_J}, with 1784 sections and rank 16 at p = 157. The (73, 12) control passed. But no rule in the frozen class (one quartic symbol of u and one cubic symbol of v, u and v small integers) predicted the exponents: the best was 50.8% held-out. The main-session audit then found two rules post hoc, on all 2374 primes p = 1 (mod 12) below 1e5. A post-hoc rule counts for nothing until it is tested on data it has not seen. This experiment is that test. It adds one direct enumeration, which tests whether the section count depends only on the rank.

**Rules under test (frozen; found after seeing the data for p < 1e5).** Convention: the SA-23b executor's canonical one. π = a + bi is primary (a odd, b even, a + b = 1 mod 4, b > 0). ρ is in Z[ω] (a' = 2, b' = 0 mod 3, b' > 0). χ is the 12th-power residue symbol at the prime of Z[ζ12] above (π, ρ).
- **L48.** The 20-exponent string e_α(p) is the value of the frozen table `verify/sa23c_table48.json` at the cell (a mod 3, b mod 3, (2/p)_3, (2/p)_4). The table has 48 cells, built by `verify/law48.py` from SA-23b `results/jacobi.jsonl`, with SHA-256 d73913762de51a0e9b70c370f3892684c73dabc1c852a186de5d2bdad69e888a. The symbols are the exponent of χ³(2) mod 4 and of χ⁴(2) mod 3, as in SA-23b.
- **RJ.** R_J(p) = 4 + 4·[2 is a cubic residue mod p] + 8·[3 | b and ((a ≡ 1 mod 3) ≠ (p ≡ 5 mod 8))].

**Protocol.**
1. **Held-out primes.** All primes p = 1 (mod 12) with 1e5 < p < 1e6. Compute the 20 Jacobi sums exactly in Z[ζ12] with the SA-23b code (`src/jac.py`, canonical mode), not refitted. Re-run p < 1e5 first and check that it reproduces SA-23b's `jacobi.jsonl` byte for byte. For each held-out prime record: |J|^2 = p^2 for all 20 pieces, the number of root-of-unity pieces, the exponent string, R_J, the L48 prediction and the RJ prediction.
2. **Enumeration at p = 229.** RJ predicts R_J = 8, and the Jacobi sum must agree. Use the SA-23b chunked enumerator (`enum_r.c`, unchanged), at most two chunks at a time, each under 2 hours. Report S, Gram rank, lattice determinant and minimum height. Verify every section independently with `results/SA-23b/audit/verify_sections.py`.
3. **Frequencies.** Report R_J frequencies over 1e5 < p < 1e6 with bootstrap CIs (2,000 resamples, seed 23). RJ implies 1/2, 1/4, 1/6 and 1/12 for ranks 4, 8, 12 and 16, by Chebotarev in the cells.

**Predictions (frozen).**
- L48 gives the exact string at every held-out prime, and RJ gives R_J at every held-out prime.
- Exactly 16 root-of-unity pieces at every held-out prime.
- R_J frequencies within their CIs of 1/2, 1/4, 1/6 and 1/12.
- At p = 229: Gram rank 8, S = 224 and determinant 256, as at p = 109, the only other enumerated R_J = 8 cell. In other words, S depends only on R_J.

**Criteria (frozen).**
- SUCCESS: zero held-out exceptions to RJ, at most 0.1% held-out exceptions to L48, and at p = 229 a Gram rank in {7, 8} with S = 224.
- KILL: any held-out exception to RJ, or a Gram rank outside {R_J - 1, R_J} at p = 229.
- INCONCLUSIVE: otherwise. Examples: S ≠ 224 at p = 229 with the rank in range (the count is not a function of R_J alone), or L48 exceptions above 0.1% with RJ exact.

**Interpretation stated in advance.** If RJ holds, then for p = 1 (mod 12) the Mordell–Weil rank of y^2 = x^3 + t^12 + 1 over F_p(t) is fixed by π mod 3, p mod 8, and whether 2 is a cube. These are residues at 2 and 3, the bad primes of Z[ζ12]. The frozen SA-23b class could not express them, because the sign of π mod 3 is not a residue symbol of any rational integer. This concerns the surface only. SA-23's ECDLP verdict covers every prime and does not depend on it.

**Cost and tier.** Sonnet executor (resume of the SA-23b executor, which owns the code). Jacobi sums: about 17,000 primes, under 1 core-hour. Enumeration at p = 229: about 8 core-hours (p^5 scaling from 109 and 193), two chunks at a time.
