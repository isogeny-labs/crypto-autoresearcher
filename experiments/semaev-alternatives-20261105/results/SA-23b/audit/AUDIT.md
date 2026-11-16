# SA-23b audit (main session, 2026-11-12)

An independent check of the executor's SA-23b report. **Verdict under the frozen criteria: INCONCLUSIVE, as the executor states.** The mechanism is confirmed at every new prime. The frozen law class fails, and the audit shows the failure is structural. Two post-hoc rules fit all 2374 primes below 1e5. They are registered for a held-out test as SA-23c (`prereg/round6/SA-23c.md`) and count for nothing until then.

## 1. Enumeration: verified with main-session code

`verify_sections.py` is written here. It shares no code with the executor's `cellb.py`. It checks Y^2 = X^3 + t^12 + 1 and the degree bounds for every listed section, forms all signed sections, builds the Gram matrix <P,Q> = chi - P.Q (chi = 2) with its own intersection routine, and takes its rank mod 2^61 - 1.

| p | listed | equation or degree failures | distinct signed | Gram rank | executor |
|---|---|---|---|---|---|
| 157 | 892 | 0 | 1784 | 16 | 1784, 16 |
| 181 | 4 | 0 | 8 | 3 | 8, 3 |
| 193 | 4 | 0 | 8 | 3 | 8, 3 |

The criteria's enumeration part holds. The rank is in {R_J - 1, R_J} at all three new primes: 16 against 16, 3 against 4, 3 against 4. S is 1784 (> 704) at p = 157 and 8 (<= 64) at p = 181 and 193. The (73, 12) control reproduced 8. The separator "7 is a square" is refuted at both 157 and 193.

## 2. Jacobi sums and conventions

- The executor's character is the 12th-power residue symbol at one prime 𝔓 of Z[ζ12] above p, fixed by π = a + bi and ρ. It reduces ζ12 to i0^3·w0 mod p. The quartic and cubic symbols in the law test are m mod 4 and m mod 3 of the same exponent m. So the character and the symbols are coupled consistently, and the failure of the law is not a labelling artefact. The audit checked this specifically before reading anything into the 50.8%.
- Exact Z[ζ12] arithmetic. |J|^2 = p^2 and exactly 16 root-of-unity pieces at all 2374 primes. The pre-freeze strings are reproduced.

## 3. Why the frozen law class fails (post-hoc analysis, `law48.py`)

- **The exponent string is a function of four residues:** (a mod 3, b mod 3, (2/p)_3, (2/p)_4). There are 48 cells, holding 35 to 59 primes each, and the rule is functional at all 2374 primes.
- **No smaller set works.** The audit tried each feature alone and in combination (majority accuracy):
  - π mod 3 alone: 18%;
  - (2/p)_3 alone: 26%;
  - (3/p)_4 and (2/p)_3 together: 27%;
  - π mod 3 and (2/p)_3 together: 52%.
  
  π mod 3, (2/p)_3, plus any one quartic symbol of 2, 6, 8, 18 or 24 (or b mod 8): 100%.
- **The obstruction is the sign of π mod 3.** A quartic symbol of a rational integer sees π mod 3 only through π^2 mod 3, by quartic reciprocity at 3. Cubic symbols see ρ, not π. So no rule built from χ at rational integers can be exact. That covers the frozen class (best 50.8%) and the executor's 72-cell joint test (55.4%). The residues that matter, π mod 3, π mod 8 and ρ mod 2, are the normalisations of the Gaussian and Eisenstein primes at 2 and 3, the bad primes of Z[ζ12].
- **Closed form for the rank (post hoc, 0 exceptions in 2374 primes).** It reproduces all nine enumerated cells, and its implied frequencies 1/2, 1/4, 1/6, 1/12 match the measured 0.508, 0.244, 0.168, 0.079.

      R_J = 4 + 4·[2 is a cubic residue mod p] + 8·[3 | b and ((a ≡ 1 mod 3) ≠ (p ≡ 5 mod 8))]

  The executor's own post-hoc rule (π mod 3 with the symbols of -1, 2 and 3, 144 cells) is a refinement of the same partition.

## 4. What this means

- The rich cells are explained. p = 37 has R_J = 12, p = 109 has 8 and p = 157 has 16. All three are primes where 2 is a cube or 3 | b in the right class. "7 is a square" had no role.
- For SA-23's ECDLP question nothing changes. Even the richest cell, 1784 sections at rank 16 with all geometric sections over F_p, sits under the kissing cap that gives the corrected bound (ERRATA 8).
- **Open (SA-23c).** A held-out test of L48 and RJ on all p = 1 (mod 12) with 1e5 < p < 1e6, using the frozen table (SHA-256 d7391376...). It adds one enumeration at p = 229, where R_J = 8 and S = 224 is predicted, as at p = 109.
