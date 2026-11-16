---
id: SA-23b
campaign: semaev-alternatives-20261105
round: 6
parent: SA-23 (audit section 3: the rich-cell anomaly)
title: "Why some primes give many sections: Jacobi-sum ranks of y^2 = x^3 + t^12 + 1 against exhaustive enumeration"
status: preregistered
frozen_on: 2026-11-12
executor_tier: sonnet
results_path: experiments/semaev-alternatives-20261105/results/SA-23b/
---

# SA-23b

**Why.** The SA-23 audit found two ordinary cells at d = 12 with far more integral sections than any other: p = 37 (704 sections, Gram rank 12) and p = 109 (224, rank 8), against 8 sections (rank 3) at p = 13, 61, 73, 97. A scan of about 20 residue characters left one separator, "7 is a square mod p", flagged as having no evidential weight. This experiment tests a mechanism instead of a scanned separator. The verdict words below refer to that mechanism, not to an ECDLP speed-up. SA-23's verdict does not depend on the outcome (its corrected bound covers every prime).

**Mechanism (stated before the run).** For p = 1 (mod 12) the essential part of H^2 of S_12: y^2 = x^3 + t^12 + 1 splits into 2d - 4 = 20 one-dimensional pieces indexed by alpha = (chi^6, chi^b, chi^k), with b in {4, 8}, k in 1..11, and 6 + b + k not 0 mod 12 (chi of order 12 on F_p^*). The Frobenius eigenvalue on a piece is J(alpha) = chi^b(-1) chi^k(-1) J(chi^6, chi^b) J(chi^{6+b}, chi^k). By the Tate conjecture (proved for K3 surfaces; S_12 has chi = 2, so it is K3) and Shioda-Tate with all fibres irreducible: rank MW(F_p(t)) = R_J(p) := #{alpha : J(alpha) = p}.

**Pre-freeze computation (2026-11-12, `prereg/round6/verify/jacobi_rank.py`, `jacobi_roots.py`; outputs stored).**
- All 20 pieces have |J| = p at 9 primes. R_J = 4, 12, 4, 4, 4, 8, 16, 4, 4 at p = 13, 37, 61, 73, 97, 109, 157, 181, 193.
- Agreement with enumeration: R_J equals the Gram rank at p = 37 (12) and 109 (8). It is one more than the Gram rank at p = 13 and 61 (4 vs 3), consistent with an MW generator that is not integral.
- At 12 primes, exactly 16 of the 20 pieces have J/p a root of unity (always cube or fourth roots). R_J(p) is the number of these roots that equal 1.
- R_J contradicts the scanned separator: it predicts p = 157 rich (rank 16, 7 not a square) and p = 193 poor (rank 4, 7 a square).

**Protocol.**
1. Enumeration (direct test). Run the SA-23 C enumerator, unchanged in its square test, at (157, 12), (181, 12) and (193, 12). Each cell is split into chunks by the value of the leading coefficient of X, so that every chunk finishes inside one 2-hour background job. At most two chunks run at a time. Output per cell: S, Gram rank, lattice determinant, minimum height. Reproduce one earlier cell, (73, 12), chunked the same way, as a control (expect 8 sections).
2. Jacobi ranks at scale. Compute R_J(p) for every prime p = 1 (mod 12), p < 10^5. Use Gauss sums or vectorised Jacobi sums. Exact cyclotomic arithmetic is preferred; floating point is acceptable if every |J| = p check passes to 1e-9 relative. Record each piece's root-of-unity exponent e_alpha(p), or "none" when J/p is not a root of unity.
3. Validation. Compare R_J with the Gram rank at all 9 enumerated cells (13, 37, 61, 73, 97, 109, 157, 181, 193). Gram ranks for 73 and 97 come from the existing section files.
4. Law. Find a rule giving e_alpha(p) from a quartic residue symbol (u/p)_4 and a cubic residue symbol (v/p)_3. Search u and v over the frozen candidate set {+-1, +-2, +-3, +-4, +-6, +-8, +-9, +-12, +-18, +-24, +-27, +-36} (cubic and quartic symbols computed in Z[i] and Z[omega] with the standard primary normalisation, or equivalently through p = a^2 + b^2 and 4p = L^2 + 27M^2 representations). Fit on p < 10^4; test on 10^4 < p < 10^5 without refitting.
5. Report the frequencies of R_J in {4, 8, 12, 16} (and anything else) over p < 10^5, and the fraction with rank 16.

**Predictions (frozen).** Enumeration: the Gram rank equals R_J or R_J - 1 at all three new primes. That gives rank 15-16 and S > 704 at p = 157, and rank <= 4 with S <= 64 at p = 181 and 193. The geometric count of algebraic pieces is 16 at every p = 1 (mod 12) < 10^5. A residue-symbol rule with one quartic and one cubic symbol predicts e_alpha(p) at >= 99% of held-out primes. The scanned separator "7 is a square" is refuted.

**Criteria (frozen; about the mechanism).**
- SUCCESS (mechanism confirmed): at each of the three new primes, the Gram rank is in {R_J - 1, R_J}, and S is above 704 at p = 157 and at most 64 at p = 181 and 193. In addition, a residue-symbol rule from the frozen candidate set predicts all 20 exponents at >= 99% of held-out primes.
- KILL (mechanism refuted): the Gram rank at any new prime lies outside {R_J - 1, R_J}, or the (73, 12) control fails.
- INCONCLUSIVE: otherwise, for example enumeration confirms the ranks but no rule in the candidate set reaches 99%.
- The separator "7 is a square" is reported as refuted or surviving by direct comparison at the three new primes.

**Cost and tier.** Sonnet executor. Enumeration about 7 core-hours (1.2, 2.4 and 3.4 h single-thread at 157, 181 and 193, extrapolated from 697 s at p = 109 and scaling about p^5). Jacobi sums under 1 core-hour. Python with numpy, gcc, and PARI through cypari2 or Sage for residue symbols.
