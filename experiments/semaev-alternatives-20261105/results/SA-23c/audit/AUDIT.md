# SA-23c audit (main session, 2026-11-12)

**Verdict: SUCCESS, as the executor states.** The audit checks below use main-session code throughout.

| check | method | result |
|---|---|---|
| frozen inputs | SHA-256 of `SA-23c.md` and `verify/sa23c_table48.json` | 5aa86e98..., d7391376...: match the registry |
| held-out set | sympy list of primes p = 1 (mod 12), 1e5 < p < 1e6, against the executor's rows | 17,190 = 17,190, identical sets |
| representation | every row has a odd, b even, a + b = 1 mod 4, b > 0, a^2 + b^2 = p | 0 violations |
| L48 | own scoring against the frozen table | 0 exceptions |
| RJ | own scoring of the closed form (cube test by 2^((p-1)/3) mod p) | 0 exceptions |
| R_J by independent code | `audit_rj_float.py`: the pre-freeze algorithm (primitive-root character, complex floating point), vectorised, at the smallest and largest held-out prime of each rank class | 8 / 8 match (4, 4, 8, 8, 12, 12, 16, 16) |
| p = 229 sections | `SA-23b/audit/verify_sections.py`, re-run by the main session | 112 listed, 0 failures, 224 distinct signed, Gram rank 8 |

**Scope.** The laws are verified numerically up to 1e6 and enumeratively at 10 cells, 13 <= p <= 229. They are not proved. The independent Jacobi check covers R_J, which does not depend on the character labelling. The 20-exponent strings rest on the executor's exact code alone, cross-checked against the pre-freeze strings at 12 primes in SA-23b. "S depends only on R_J" rests on two R_J = 8 cells and one cell each at 12 and 16. None of this bears on ECDLP: SA-23's corrected bound covers every prime.
