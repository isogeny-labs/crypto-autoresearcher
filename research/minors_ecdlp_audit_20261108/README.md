# Audit of the "minors solve the ECDLP" line, 2026-11-08

Lead: `LEAD-EXO-minors-guess-and-determine`. Status: audit and one reproduced
toy check. Every number is `[pcc:unverified]`. The reading of the four papers
was done by a delegated reader from the arXiv PDFs; the toy table below was
re-run by the session that filed this note and reproduces exactly
(`toy_minors.out.txt`, produced by `python3 -I toy_minors.py`).

## Papers (all four ids resolve as the lead says)

| id | title | notes |
|---|---|---|
| 1703.07544 v3 | A Las Vegas algorithm to solve the ECDLP (Mahalanobis, Mallick) | success probability 0.6 (log p)^2 / p per pass; its section 5.2 calls the cost "only little better than exhaustive search" |
| 2005.05039 v3 | A new method for solving the ECDLP (Abdullah, Mahalanobis, Mallick) | J. Groups Complex. Cryptol. 12(2), 2021; states Conjecture A (sub-exponentially many initial minors suffice), no theorem on cost; its own text says iteration counts approximately double per bit |
| 2310.04132 v1 | Minors solve the ECDLP (Abdullah, Mahalanobis) | repeats the conjecture; "polynomial time" might follow from data; data are binary fields up to 45 bits |
| 2607.09814 v2 | A Guess and Determine Attack on the ECDLP (Mahalanobis) | states a cost per parameter choice; its introduction says the attack is "no better than the exhaustive search"; no timings |

Corrections to the lead: the "order 2^50" experiments in 2005 and 2310 are over the
binary field F_{2^50}, not prime fields. The papers do state a cost and it is
about p. The internal draft design is not the papers' algorithm.

## Algorithm (read from the text)

1. l = 3 n' with n' about log2 p. Take 2l points n_i P and -n_j Q.
2. Matrix M, 2l rows, C(n'+2, 2) columns (monomials of degree n'). Its left
   kernel K has dimension l; reduce to [A | antidiagonal identity].
3. 3 n' points on E sum to O iff a degree-n' curve not containing E passes
   through them. A kernel vector with l zeros marks l points summing to O,
   which gives a linear relation in the scalar.
4. Such a vector exists iff the l x l block A has a zero minor of some size.
   The search sets are 2x2 minors, Schur complements, almost-principal minors.

## Where it fails

A zero minor of A is an essentially random event of probability about 1/p.
The method examines a polynomial-in-l number of minors per kernel. Expected
work is therefore p divided by a polynomial in log p, not sqrt(p). Inference
from the papers' own tables: a random-zero model predicts their iteration
counts without hidden structure (2005 Table 1 model 263 / 1577 / 9628 against
observed 113 / 716 / 4406; Schur at 2^50 model 1273 against observed 888; 2310
zero-minor counts at F_{2^25} model 0.2 / 136 / 44,000 against observed 1 / 230
/ 70,498). Observed growth 2^40 to 2^50 is 317x, an exponent of about 0.83 in q.

Cost of the 2607 formulas at l = 3 log2 p (parameters inferred from its tables,
not stated):

| group order | K | kernels | sqrt(n) | gap |
|---|---|---|---|---|
| 2^20 | 30 x 60 | about 2^21 | 2^10 | about 2^11 |
| 2^64 | 192 x 384 | about 2^63 to 2^64 | 2^32 | about 2^31 |
| 2^256 | 768 x 1536 | about 2^258 | 2^128 | about 2^130 |

## Toy check (re-run; `toy_minors.py`, 57 lines, stdlib only)

For prime-order curves it builds M and K, counts zero 2x2 minors of A, and
checks that each hit recovers the scalar m.

| p | N | l | minors tested | zero minors | random model | correct m | minors per hit | sqrt(N) |
|---|---|---|---|---|---|---|---|---|
| 1031 | 1033 | 12 | 52,272 | 52 | 50.6 | 52 | 1005 | 32 |
| 4099 | 4021 | 15 | 99,225 | 21 | 24.7 | 21 | 4725 | 63 |
| 16411 | 16273 | 18 | 257,499 | 16 | 15.8 | 16 | 16,094 | 128 |

Kernels with accidentally repeated points (a collision that fixes the scalar by
itself, ordinary birthday) are filtered out; without the filter the count
shows an excess caused by that, not by structure. The method is correct and
every hit recovers m, and it costs about N minors per hit.

## Verdict and limits

About 85 percent confidence, the reader's estimate, that the line gives no
sub-sqrt cost on generic prime-field curves. The honest summary is that the
authors' latest paper concedes it. What would change this: data that zero
minors cluster above the 1/p density at 40 bits or more, a birthday variant
that collides without the p-sized candidate pool (the 2607 "rho on penultimate
intersections" is unimplemented and the paper could not define the collision),
or prime-field data at all, since every dataset in 2005 and 2310 is binary.
Not run: a 20 to 40 bit hash scan with every operation charged and a fitted
exponent against matched rho.

This note changes no lead disposition.
