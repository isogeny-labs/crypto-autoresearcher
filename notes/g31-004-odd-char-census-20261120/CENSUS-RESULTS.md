# G31-004 / WP1 — Semaev summation polynomials over odd-characteristic prime fields: explicit census + brute-force validation

## 1. Provenance

- Work dir: `/Volumes/SSD990/llm/tmp/opencode/g31-004/`
  - `census.py` — task 1 (construction + census), `validate.py` — tasks 2–4, `ecfield.py` — shared F_p / F_{p^2} / curve helpers.
  - Raw outputs: `results/census_stats.json`, `results/validation_stats.json`, `polynomials/{s3_universal_Z,s4_universal_Z,s3_mod101,s4_mod101}.json` (sparse `{exp-vector: coeff}`), logs `census.log`, `validate.log`.
- Environment: Python 3.12.8, sympy 1.14.0, numpy 2.4.4, macOS-27.2-arm64. (A `sage` binary is installed on this machine but was **not used**.)
- Repo reference, **read-only**: `/Volumes/SSD990-2/crypto-autoresearcher` @ `5c186aacf0c2d08d73020c9b411167b0eb42ba78`; files read: `harness/semaev.py`, `harness/toycurve.py`, `tests/test_semaev_s4_exact.py`. Imported under `python -B`; no bytecode or any other file was written into the repo (the pre-existing `harness/__pycache__` entries are dated Nov 6, before this run; none of the `git status` modifications belong to this work).
- Seeds: master seed **31004** (all `random.Random` / `numpy.default_rng` derivations documented in the scripts).
- Curves: `harness/toycurve.py` contains **no fixed toy curve** (instances are seed-generated), so concrete documented choices are used: **(p,a,b) ∈ {(101,1,1), (127,1,1), (1009,1,1)}**, y² = x³+ax+b, discriminant 4a³+27b² = 31 ≠ 0 in every field.
- Repo convention (verified by reading the source, and re-verified empirically here):
  - `S_2(x1,x2) = x1 − x2` (odd characteristic: P1+P2 = O ⟺ equal abscissae);
  - `S_3(x1,x2,x3) = (x1−x2)²x3² − 2((x1+x2)(x1x2+a)+2b)x3 + (x1x2−a)² − 4b(x1+x2)` (Semaev, ePrint 2004/031, cleared-denominator form);
  - `S_4 = Res_t(S_3(x1,x2,t), S_3(x3,x4,t))`.
- **Brief correction:** the WP brief's "S_2 = (f(x1)−f(x2))/(x1−x2), degree 2 in each" does **not** match the repo, Semaev, or the m=2 vanishing condition (that quotient vanishes on an unrelated curve; the m=2 correspondence is the diagonal x1=x2). The census follows the repo/published convention and *validates it against the group law from scratch*, so no conclusion here rests on either the brief's claim or the repo's.

## 2. Semantics used for brute force (matters for the mismatch accounting)

Semaev's equivalence over F̄_p is: `S_m(x1..xm) = 0 ⟺ ∃ y_i ∈ F̄_p on E with ΣPi = O` (signs absorbed in y_i). For x_i ∈ F_p every lift satisfies y_i² = f(x_i) ∈ F_p, so **all relevant y_i live in F_p or F_{p^2}** — the brute force therefore enumerates lifts in F_{p^2} = F_p[w]/(w²−ns) and is *exact* for the algebraic-closure statement on F_p-tuples (no sampling of the closure). The weaker "signs in E(F_p)" statement (what the repo's own test checks, restricted to on-curve x's) is *legitimately false* on tuples with some off-curve x_i: e.g. if f(x1) is a non-square, S_3(x1,x1,x3) vanishes exactly at x3 = x([2](x1,y1)) with y1 ∉ F_p (the doubling abscissa ((3x²+a)²/(4f) − 2x lies in F_p), yet no F_p-signs exist). Validation therefore reports the two statements separately and **both passed** (section 4).

## 3. Task 1 — census

Universal over Z[a,b,x1..x4] (one computation, all primes):

| poly | gens | total deg | deg per var | monomials (Z) | coeff heights Z |
|---|---|---|---|---|---|
| S_3 | x1,x2,x3,a,b | 4 | 2,2,2 (a:2,b:1) | 13 | max abs 4, mean 2.15 |
| S_4 | x1..x4,a,b | 12 | 4,4,4,4 (a:4,b:3) | 540 | max abs 384, mean 23.9 |

Per prime (a=b=1; S_4 computed three independent ways: **A** = Z-resultant then reduce; **B** = own 4×4 Sylvester determinant with F_p polynomial entries; **C** = quadratic-resultant closed form (AF−CD)² − (AE−BD)(BF−CE) over Z then reduce):

| (m,p,curve) | total deg | per-var deg | monomials (dense box, support) | coeff heights mod p | zero rate (200k random sample) | wall time | A=B=C |
|---|---|---|---|---|---|---|---|
| S_3, p=101, (1,1) | 4 | 2,2,2 | 13 (27, 48.1%) | min 1, max 99, mean 68.4 | 0.00956 | expand 0.019 s | n/a (closed form) |
| S_3, p=127 | 4 | 2,2,2 | 13 (27, 48.1%) | max 125, mean 86.4 | 0.00777 | — | — |
| S_3, p=1009 | 4 | 2,2,2 | 13 (27, 48.1%) | max 1007, mean 697.0 | 0.00094 | — | — |
| S_4, p=101 | 12 | 4,4,4,4 | 439 (625, 70.2%) | min 1, max 97, mean 45.8 | 0.00992 | A 0.095 s, B 0.005 s, C 0.105 s | ✓ ✓ |
| S_4, p=127 | 12 | 4,4,4,4 | 439 (625, 70.2%) | max 123, mean 56.1 | 0.00805 | A 0.004 s, B 0.004 s, C 0.009 s | ✓ ✓ |
| S_4, p=1009 | 12 | 4,4,4,4 | 439 (625, 70.2%) | max 1005, mean 441.3 | 0.00097 | A 0.004 s, B 0.003 s, C 0.007 s | ✓ ✓ |

- Universal S_4 (sympy resultant over Z, gens x1..x4,a,b): **0.65 s**, trivially inside the 20-min budget; no subresultant-PRS fallback was needed. Peak RSS 180 MB (census.py) / 426 MB (validate.py) (`ru_maxrss`).
- Consistency of degrees with theory: deg_{x_i} S_m = 2^{m−2} (2, 4); total degrees 4 and 12 (generic bounds 2^{m−1}+… not tight). Zero rates ≈ 1/p as expected for a hypersurface with p^{m−1}-sized zero set (exhaustive at p=101: S_3 has exactly 10109 zeros vs p² = 10201 heuristic).
- Monomial counts are stable 13 / 439 at all three primes (no coefficient collapse; Z-heights ≤ 384).
- Distinct exponent vectors = monomial counts above (sparse support); "dense box" = ∏(deg_i+1).

## 4. Task 2 — brute-force validation vs the group law

`ecfield.py` truth: enumerate F_{p^2} lifts, pair sums, mark attainable abscissae (cross-checked against a naive triple-enumeration oracle at p=11: 0 mismatches; own F_p arithmetic vs `harness.toycurve.EllipticCurve.add`: 0/3000 mismatches).

**S_3** (statement checked: S_3(x)=0 ⟺ ∃ F̄_p-lifts with P1+P2+P3 = O):

| p | mode | tuples | S_3 zeros | ext-truth true | mismatches | vs F_p-only truth on all-on-curve tuples | mixed-tuple zeros (some x off-curve) |
|---|---|---|---|---|---|---|---|
| 101 | **exhaustive** | 1,030,301 | 10,109 | 10,109 | **0** | 0 / 5,356 all-on-curve zeros agree | 4,753 — **all** genuine F̄-solutions; 0 unexplained |
| 127 | **exhaustive** | 2,048,383 | 16,006 | 16,006 | **0** | 0 / 7,750 agree | 8,256 — all explained |
| 1009 | random 20k | 20,000 | 22 | — | **0** | — | — |

The F_p-only ("signs in E(F_p)") statement agrees with the polynomial exactly on tuples whose three x's are all on-curve abscissae, and disagrees only on mixed tuples in the way predicted by theory (section 2) — counted, not patched away.

**S_4** (p = 101, the smallest prime):

| test | tuples | mismatches |
|---|---|---|
| random uniform F_p⁴ vs F̄-truth | 20,000 (220 zeros) | **0** |
| forced diagonal x1=x2 vs F̄-truth | 4,000 | **0** |
| **exhaustive** over all on-curve-x tuples (52 abscissae; mirrors repo test semantics) | 7,311,616 | **0** |
| census polynomial values vs quadratic-resultant formula (ties the two computations) | 2,000 | **0** |

**No mismatches anywhere.** No convention debugging was needed: the group-law ground truth matches the recursion polynomials exactly.

## 5. Task 3 — cross-check vs `harness/semaev.py`

For each of the three curves:

- Coefficient dictionaries `semaev.s3_expr(a,b)` vs ours: **identical mod p** (all 3 primes).
- Coefficient dictionaries `semaev.s4_expr(a,b)` (the repo's own Z-resultant) vs our census S_4: **identical mod p** (all 3 primes, 439 monomials each); and **exact over Z**: our universal S_4 ∈ Z[a,b,x1..x4] specialized at a=b=1 equals `semaev.s4_expr(1,1)` coefficient-for-coefficient.
- Zero-set agreement on 10⁴ random tuples per prime, repo evaluator (`semaev.s3_eval`, repo S_4 expanded) vs ours: **10000/10000 for S_3 and S_4 at p = 101, 127, 1009** (60,000 comparisons total).
- The repo's own `tests/test_semaev_s4_exact.py` encodes the same convention (± signs, pair-sum meet); our exhaustive on-curve test at p=101 is a scaled-up analogue with independent code paths. (We did not execute the repo's pytest to avoid generating bytecode in the read-only tree; our validation covers the same statement at larger p with independent implementations.)

## 6. Task 4 — symmetry and duplication structure

- **Full symmetry, exact over Z:** S_3 invariant under all 6 permutations and S_4 under all 24 permutations of the x-variables (coefficient-dictionary check on the universal polys). Numeric check at p=101: 500 random tuples × all permutations: 0 violations (S_3), 0 violations (S_4).
- **Duplication on the S_3 diagonal, p=101, all x ∈ F_p:** S_3(x,x,t) is always genuinely linear (t²-coefficient vanishes), and its unique root equals x([2](x,y)) = (3x²+a)²/(4f(x)) − 2x for **101/101 x** — including off-curve x (where the doubling uses y ∈ F_{p²}); the truth row {(t)} from the group enumeration matches the single root in 101/101 cases. The 2-torsion special case (f(x)=0 forcing S_3(x,x,·) a nonzero constant) did not occur on this curve — E(F_101) has no point of order 2 — so that branch is implemented and checked in code but exercised zero times here (honest gap).
- **S_4 diagonal, exact value identity** (2000/2000 samples): `S_4(x,x,u,v) = (4f(x))² · (u−v)² · S_3(u, v, x([2]P))`. The extra factor (u−v)² is not an error: the recursion's resultant treats both S_3's as *formal* quadratics in t, and killing the leading coefficient (x1−x2)² on the diagonal leaves the second factor's leading coefficient in the value. Both extra factors are squares, so zero sets — the group-theoretic content — are unaffected (verified by the forced-diagonal brute force). Our first naive prediction without (u−v)² failed 1947/2000, which is what surfaced the formal-degree artifact.
- **Independent re-derivation of S_3** (no closed form): eliminate y3,y2,y1 from collinearity det + three y²=f(x) equations by iterated resultants over Z. Result: degree-20 polynomial in 6 gens (795 monomials) = **S_3² × (extraneous factor of total degree 12)**; numeric maximal power of S_3 dividing it: exactly **2** (matches the 2 generic collinear-lift pairs per correspondence point). Zero-set comparison vs the closed form over F_101 (4000 random points): every extra zero lies on a diagonal x_i = x_j (113 — matching the ~2.8% baseline diagonal rate), **0 off-diagonal mismatches, and 0 points where S_3 vanishes but the elimination does not**. Lesson recorded for later WPs: naive iterated y-elimination produces the summation polynomial squared times discriminant-type junk; the S_3 closed form / Semaev recursion (what the repo uses) avoids that.

## 7. What this does and does not establish

**Does establish**
1. For the three concrete curves, the repo-convention S_3 and S_4 were computed *exactly* (three independent resultant computations agree, and the S_4 matches the repo construction coefficient-for-coefficient over Z), with full census data (degrees, support, heights, zero densities).
2. The Semaev vanishing property over F̄_p for m = 3 is verified **exhaustively** at p = 101 and p = 127 (3.08M tuples) and on 20k random samples at p = 1009 — with exact F_{p^2} ground truth, so this is complete, not sampled, verification at the small primes. For m = 4 it is verified exhaustively on all on-curve-abscissa tuples at p = 101 (7.3M tuples) and on 24k random tuples including off-curve and diagonal cases.
3. Zero agreement with `harness/semaev.py` is 100% on every sample tried, and polynomial-level equality holds outright — so the repo implementation's convention is confirmed, not just imitated.
4. The F_p-only ("signs in E(F_p)") reading of the equivalence holds exactly on all-on-curve tuples and **fails by design** on mixed tuples; both readings are separated cleanly and counted.
5. Full S_m symmetry (exact, over Z) and the duplication structure on the x1=x2 diagonal (exact value identity including the formal-resultant leading-coefficient factor).

**Does not establish**
1. No proof for arbitrary p, m ≥ 5, or arbitrary curves: this is a finite census + brute-force at toy scale; nothing here scales to cryptographic p, and no complexity/cost claims are made.
2. m = 4 was **not** exhaustively validated over all of F_101⁴ (104M tuples) with F̄-truth — only over on-curve tuples exhaustively plus 24k random mixed tuples — nor was any m = 4 validation done at p = 127/1009 (only zero-rate sampling).
3. The recursion polynomials are the *naive* recursion outputs, not proven minimal: we observed (m=3 elimination) that naive y-elimination yields S_3²·junk, and (diagonal S_4) that formal-degree resultants carry leading-coefficient artifacts; we did not attempt radical/saturation computations (e.g. confirming the recursion gives exactly S_m and not a power of it for m ≥ 4 over Z).
4. The 2-torsion diagonal branch (f(x) = 0) was never exercised at p = 101 (curve has no rational 2-torsion); it is covered only by code + reasoning.
5. Irreducibility, squarefreeness, geometric integrality of the S_m, and any statement about factor-base attack viability / degrees of regularity are out of scope and untouched.
6. Coefficient-height statistics are specific to a=1,b=1 (generic-a,b heights are the universal-Z ones in section 3); other (a,b) can change sparse support (e.g. b=0 kills monomials).

## 8. Reproduce

```
cd /Volumes/SSD990/llm/tmp/opencode/g31-004
python3 -B census.py     # ~5 s wall, writes results/census_stats.json, polynomials/*.json
python3 -B validate.py   # ~11 s wall after census, writes results/validation_stats.json
```

(`-B` keeps the imported read-only repo free of `__pycache__`. Both scripts are deterministic given seed 31004.)
