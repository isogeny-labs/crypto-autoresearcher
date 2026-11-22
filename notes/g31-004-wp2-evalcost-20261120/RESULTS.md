# G31-004 / WP2 — Per-candidate evaluation cost of Semaev summation polynomials over a ~31-bit prime field

**Question.** If a cost ledger charges relation search per candidate tuple, what does one
`S_3` / `S_4` evaluation actually cost at `p ≈ 2^31`, and how much does the answer depend on
the assumed evaluation mode?

**Answer in one line.** At `p = 2^31−1`, `y² = x³+7`: a sieve-style `S_3` candidate costs
**245 ns**, a sieve-style `S_4` candidate **433 ns** (`362 ns` once coefficients are fully
amortised), a vectorised batched `S_4` candidate **12 ns**, and a reuse-free one-shot `S_4`
**54 µs** — a 4500× spread across modes. The ledger must record the mode, or it is
meaningless. Ratios to a Python group addition: 0.25 (`S_3`) and 0.45 (`S_4`, W=384).

---

## 1. Machine, versions, and timing method

| item | value |
|---|---|
| CPU | Apple M4 Pro (14 cores), macOS 27.2 arm64 |
| Python | CPython 3.12.8, `sys.int_info.bits_per_digit = 30` ← matters, see §8 |
| numpy | 2.4.4 (mode C only) |
| curve | `y² = x³ + 7` (`a=0`, `b=7`); `4a³+27b² = 1323 ≠ 0` mod both primes (asserted) |
| p ≈ 2^20 | `1048573` — largest prime < 2^20 |
| p ≈ 2^31 | `2147483647 = 2^31−1` — Mersenne prime, largest prime < 2^31 |
| reps | **5** per (mode, m, p) for every headline number; 3 for the §8 probe (flagged there) |
| clock | `time.perf_counter`, single-threaded, batch sized ≈0.2–0.5 s per rep |
| seed | 31004 (all RNG streams; data generated *outside* the timed region) |
| peak RSS | 230 MB (process), wall 69 s for the full benchmark |
| raw data | `results_wp2.json`, `results_crosscheck.json` |

**CPU pinning — honest status.** macOS has no `sched_setaffinity`; there is no way for a user
process to pin to a core. I made the best available attempt, Mach `thread_policy_set` with
`THREAD_AFFINITY_POLICY`, and the kernel **refused**: `kern_return = 46 = KERN_NOT_SUPPORTED`
(`<mach/kern_return.h>`), because the affinity policy is a hint that Apple Silicon does not
implement. So: **the numbers below are *not* from a pinned CPU.** Compensation: single-threaded
runs, nothing else running, 5 repetitions, median **and** IQR reported. Observed **within-run**
IQRs are 0.1–2 % of the median for mode B, up to ~6 % for the batched mode C, and 1–12 % for the
one-shot modes A/A2 (which allocate power tables per call, so the allocator adds variance).

**Reproducibility across independent runs.** The whole benchmark was executed twice (same code,
same machine, ~70 s each) so that within-run IQR is not mistaken for total error. Run 2 vs run 1:
mode B within **1.5–5.4 %** (`S_3` +2.5 %, `S_4` W=384 +3.9 %), mode C within 6 %, `ref_group_add`
+3.7 %, but the one-shot modes up to **16 %** (`A2 S_3` at p=2^20) and the `p=2^20` mulmod
calibration 14 %. **Quote mode-B numbers to two significant figures, and treat the one-shot rows
as order-of-magnitude.** The tables below are run 1, the run shipped in `results_wp2.json`.

---

## 2. Polynomials (task 1) — parsed from the WP1 census, not recomputed

The stored universal polynomials `s3_universal_Z.json` / `s4_universal_Z.json` (schema
`{gens, terms:[{exp, coeff}]}`, gens `[x1..xm, a, b]`) were specialised by
`semaev_eval.specialize`. No resultant was recomputed anywhere in this WP.

| object | gens | monomials over Z | check |
|---|---|---|---|
| `S_3` universal | x1,x2,x3,a,b | **13** | matches census |
| `S_4` universal | x1..x4,a,b | **540** | matches census |
| `S_3` at a=b=1, mod p | — | **13** | term-for-term `==` `harness.semaev.s3_expr(1,1)` mod p |
| `S_4` at a=b=1, mod p | — | **439** | term-for-term `==` `harness.semaev.s4_expr(1,1)` mod p, **at p=2^20 and p=2^31** |
| `S_3` at a=0,b=7 (benchmark curve) | — | 9 | 4 terms die with `a=0` |
| `S_4` at a=0,b=7 | — | 191 | 349 terms die with `a=0`; support by x4-degree: 37,39,42,40,33 |
| degrees | — | `deg_{x_i} S_3 = 2`, `deg_{x_i} S_4 = 4` | asserted from supports |

So the benchmark curve is *smaller* than the census curve at `a=b=1`. Both constants are
reported (the a=b=1 one-shot figures are at the end of §5) so the ledger can pick the right one:
**191 terms** for `b=7, a=0`, **439 terms** for `a=b=1`.

## 3. Correctness gates run *before* any timing

An optimised loop that computes the wrong thing has zero value, so every timed loop is checked
value-for-value against the reference evaluator (`bench_wp2.verify_loops`), and the
specialisations are separately cross-checked at the benchmark primes:

- `S_4` (from the stored universal JSON) **==** the repo's `s4_expr(1,1)` reduced mod p,
  term-for-term, at `p = 2^20` and `p = 2^31` (`results_crosscheck.json`).
- `S_4` values **==** the independent quadratic-resultant closed form
  `(AF−CD)² − (AE−BD)(BF−CE)` on 4 000 random tuples at both primes: 0 mismatches.
- 2 000 **constructive positive controls** per prime per m: build `P_3 = −(P_1+P_2)` from real
  `F_p` points, set `x_3 = x(P_3)` → `S_3 = 0` exactly; likewise `P_4 = −(P_1+P_2+P_3)` → `S_4 = 0`.
  Result `2000/2000` for both, both primes. Perturbation control (`x_3+1`) never vanishes.
- `S_3` diagonal `S_3(x,x,t)`: linear, root `== x([2]P)`, `2000/2000` at both primes.
- `p=101` self-test in `semaev_eval.selftest()`: 13/540 universal support, 13/439 at a=b=1,
  term-for-term `==` `s3_mod101.json` / `s4_mod101.json`, zero sets `==` `F_{p²}` group-law truth.
- Modes A and A2 need no separate loop-level check: A *calls* the reference evaluator from
  `semaev_eval`, and A2's pre-tabulated accumulation pattern is itself checked against the
  reference on sample tuples inside `verify_loops` (as are mode B's reduced and unreduced
  variants and every cell of mode C's matrices).

Random-sample zero-rate at `p ~ 2^31` is deliberately **not** used as a check: `1/p ≈ 5·10⁻¹⁰`
against `N = 4·10⁵` samples gives an uninformative expected count of ~2·10⁻⁴. The constructive
controls replace it.

---

## 4. The four modes

| id | mode | what it models |
|---|---|---|
| **A** | one-shot sparse | one isolated evaluation: power tables rebuilt inside the call, `n` monomials accumulated. Worst case, no reuse. |
| **A2** | pre-tabulated powers | power table per field element built **once per batch**, then a pure per-monomial multiply-accumulate. **Reported separately — this is the variant that hides memory traffic; it is not the headline.** |
| **B** | **sieve sweep (headline)** | nested grid sweep with powers updated incrementally at each loop level; all operands are full-size field elements (offsets `p/2, p/3, p/5`, `x_max = p−W−1`); three reductions per candidate at `m=3` (one for the value, two for the incremental square update). For `m=4`: the 5 coefficients of `S_4` in `x4` are computed once per `(x1,x2,x3)` triple, then a degree-4 Horner (4 mulmods, 5 reductions) over a window of `W` values of `x4`. |
| **C** | batched / multipoint-style | numpy `int64` coefficient arrays per triple, reused across the `x4` window; `S_3` analogue broadcast over the `x3` window. Cache-resident; see caveats. |

Design notes worth recording:
- True subproduct-tree multipoint evaluation is pointless here: the "polynomial in one variable"
  is degree **2** (`m=3`) and **4** (`m=4`). Direct Horner is already optimal; what actually
  matters is **coefficient reuse across a window**, which is what B and C implement.
- Mode B keeps the running square reduced (`X²⁼¹ = X² + 2X+1`, with `% p` on both the square and
  the step). A variant that leaves the running square unreduced (safe: it is bounded by
  `p + 2W²`) is also measured: it is **26 % faster** (`181` vs `245 ns` at `m=3, p=2^31`, i.e.
  1.35×). The reduced version is the headline because it is the conservative, straightforwardly
  portable one.

## 5. Results — ns per candidate (median [IQR]), 5 reps

`m=3` panels are `S_3`; `m=4` panels are `S_4`. Term counts: 9 / 191 on this curve.

| mode | m | p=1048573 | p=2147483647 |
|---|---|---|---|
| A one-shot | 3 | 2 575 [130] | 3 222 [13] |
| A one-shot | 4 | 50 089 [6 180] | 54 445 [66] |
| A2 pre-tabulated | 3 | 2 064 [161] | 1 960 [14] |
| A2 pre-tabulated | 4 | 23 492 [207] | 31 084 [293] |
| **B sweep** | **3** | **154.7 [0.3]** | **245.3 [2.6]** |
| **B sweep, W=32** | 4 | 719.1 [14.9] | 1 106.6 [3.8] |
| **B sweep, W=96** | 4 | 368.1 [4.4] | 611.6 [1.4] |
| **B sweep, W=384** | 4 | **230.8 [3.9]** | **433.2 [2.9]** |
| B Horner-only (W→∞) | 4 | 180.0 [2.9] | 362.2 [0.5] |
| C batched, W=128 | 4 | 23.5 [1.5] | 22.6 [1.2] |
| C batched, W=512 | 4 | 12.6 [0.3] | 12.0 [1.0] |
| C batched | 3 | 3.8 [0.3] | 3.6 [0.04] |
| C no-reuse baseline | 4 | 1 202 [0.7] | 1 162 [13] |

**Amortisation structure of mode B for `m=4`** (`p=2^31`): coefficient block costs
**23 517 ns per `(x1,x2,x3)` triple**, so the coefficient share per candidate is `23517/W` ns:

| W | coef share | + Horner | measured |
|---|---|---|---|
| 32 | 735 | 362 | 1 107 |
| 96 | 245 | 362 | 612 |
| 384 | 61 | 362 | 433 |
| ∞ | 0 | 362 | 362 |

So the per-candidate charge for `m=4` is `362 + 23517/W` ns, and a real sieve wants a large
window (or `x4`-root-finding instead of a scan). At `m=3` there is no coefficient block to
amortise: the candidate itself is the whole cost, 245 ns.

(The W-sweep holds `x2, x3` fixed and strides `x1`, to isolate `W`; every operand is a full-size
field element either way, so the coefficient cost — and hence the row structure — does not depend
on which corner of the grid is used.)

**Charge ladder at `p=2^31` (`S_4`, 191 terms).** The same candidate costs:

`54 445 ns` (one-shot) → `31 084` (pre-tabulated) → `1 162` (vectorised, no reuse) →
`433` (sieve sweep, W=384) → `362` (sweep, coefficients amortised) → `12` (batched arrays).

A 4 500× spread. **Charging a relation search at one-shot cost overstates it by 126× relative to
the sieve loop and by ~4 500× relative to the batched loop.** This is the single most important
finding for the ledger.

**Census-comparable `a=b=1` constants at `p=2^31`** (13 / 439 terms): one-shot `S_3` 3 934 ns,
one-shot `S_4` 116 359 ns, pre-tabulated `S_4` 67 693 ns — i.e. 2.1× the `a=0,b=7` figures,
tracking the 439/191 = 2.3× support ratio. Sweep numbers were not re-measured for `a=b=1`; scale
the `m=4` coefficient block by the term ratio (23 517 ns × 2.3 ≈ 54 µs per triple) if that curve
is needed.

## 6. Normalisation to a reference group operation (task 3)

Reference = affine point addition on the *same* curve in the *same* Python implementation
(`Curve.add`: one `pow(x,−1,p)` inversion, 3 mulmods), and doubling separately:

| reference | p=2^20 | p=2^31 |
|---|---|---|
| point addition | 609 [23] ns | 968 [30] ns |
| point doubling | 682 [16] ns | 1 090 [10] ns |
| calibration mulmod `(a·b) % p`, full-size | 61.8 [1.0] ns | 97.6 [0.8] ns |

| ratio | p=2^20 | p=2^31 |
|---|---|---|
| `S_3` sweep / Python add | 0.254 | 0.254 |
| `S_4` sweep (W=96) / Python add | 0.605 | 0.632 |
| `S_4` sweep (W=384) / Python add | 0.379 | 0.448 |
| `S_4` Horner-only / Python add | 0.296 | 0.374 |
| `S_4` batched (W=512) / Python add | 0.021 | 0.012 |
| `S_3` / `S_4` in calibration-mulmods | 2.5 / 6.0 (W=96) | 2.5 / 6.3 (W=96); 4.4 at W=384; 3.7 for the bare Horner |

**Read this as a dimensionless shape, never as a conversion factor.** The ratio is
`(arithmetic in the evaluator) / (arithmetic + a modular inverse + interpreter overhead in a
Python affine add)`. A harness with a C group law (≈ tens of ns, inversion via a batch trick or
projective coordinates) and a C evaluator (≈ few ns per candidate) will land somewhere else
entirely; the ratio can move by 1–2 orders of magnitude in either direction. **Re-measure both
sides in the harness's own units before any GOE-style conversion.** What *is* portable is the
*structure*: `S_3` costs ≈ 2.5 mulmod-equivalents, `S_4` ≈ 6.3 at `W=96` (4.4 at `W=384`, 3.7 for
the amortised Horner alone), i.e. an `S_4` candidate is ~2.5× an `S_3` candidate, and both are
well under one affine group addition *in Python*.

## 7. Scaling sanity (task 4): 2^20 → 2^31

| quantity | p=2^20 | p=2^31 | growth |
|---|---|---|---|
| `S_3` sweep | 154.7 ns | 245.3 ns | 1.59× |
| `S_4` Horner-only | 180.0 ns | 362.2 ns | 2.01× |
| `S_4` W=384 | 230.8 ns | 433.2 ns | 1.88× |
| calibration mulmod | 61.8 ns | 97.6 ns | 1.58× |
| Python point add | 609 ns | 968 ns | 1.59× |

Growth is **not** the ~1.0× that "multiplications are linear in log p at fixed word size"
predicts in C. It is 1.6–2.0×, and §8 shows the cause is a **CPython bignum artefact, not
mathematics**.

## 8. Where the growth comes from — the 30-bit digit boundary

CPython stores integers in 30-bit digits. `1048573 < 2^30` is one digit; `2147483647` is two,
and its *products* are three. Probing four primes straddling the boundary (3 reps each — the
only place reps < 5, flagged):

| p | operand digits | mulmod | `S_3` sweep | `S_4` Horner |
|---|---|---|---|---|
| 1 048 573 (< 2^20) | 1 | 57.9 ns | 151.1 ns | 167.6 ns |
| 1 073 741 789 (< 2^30) | 1 | 53.0 ns | 145.6 ns | 172.2 ns |
| 1 073 741 827 (> 2^30) | 2 | 77.2 ns | 201.4 ns | 299.9 ns |
| 2 147 483 647 (< 2^31) | 2 | 95.5 ns | 247.9 ns | 364.8 ns |

(A second run reproduced the pattern with different absolute values — `S_3`: 153, 148, 206, 272 ns;
Horner: 182, 172, 305, 401 ns — which is why only the *shape* is claimed here.)

Within one digit class the cost is essentially **flat** (151 vs 146 ns; 168 vs 172 ns) — which is
exactly the "constant per candidate at fixed word size" prediction. The jump sits at 2^30, i.e.
at the CPython representation. The further ~1.2× from 2^30 to 2^31 is *not* a change in digit
count (operands are two digits, products three, in both cases); it is that the *typical product*
is ~4× larger in absolute value (mean `p²/4` ≈ 2^58 vs 2^60), so a much larger fraction of
products occupy the full third digit. **In C/Rust with 64-bit words both primes are one word, and
per-candidate cost should be essentially constant; the measured 1.6–2.0× should not be
extrapolated as if it were a log p law.** Conversely, do not use these numbers to argue anything
about asymptotic complexity.

## 9. What a relation-search inner loop costs at these sizes

`p=2^31`, mode B, pure evaluation only (no `y` handling, no memory traffic, no factoring, no
relation bookkeeping). Full enumeration of a factor base of size `B`:

| m | B | candidates | wall clock | in Python group adds |
|---|---|---|---|---|
| 3 | 1 024 | 1.07·10⁹ | 4.4 min | 2.7·10⁸ |
| 3 | 4 096 | 6.87·10¹⁰ | 4.7 h | 1.7·10¹⁰ |
| 4 | 1 024 | 1.10·10¹² | 5.5 d | 4.9·10¹¹ |
| 4 | 4 096 | 2.82·10¹⁴ | 3.9 yr | 1.3·10¹⁴ |

Using the batched (mode C) rate instead divides these by ~36. Using the one-shot rate multiplies
them by ~126. **This is precisely why the mode must be part of the charge**, and it is the
practical form of the "honest charging" requirement: quoting a single ns/candidate without the
mode is a 3-orders-of-magnitude error bar.

These are per-candidate costs only: a real `m=4` relation search does not enumerate `B⁴`; it uses
sieving, pair-sums, or root-finding in `x4` precisely to avoid it. Nothing here says anything
about the cost of *finding relations*.

---

## 10. What this does and does not establish

**Does establish**
1. The stored universal `S_3` (13 monomials) / `S_4` (540 over Z, 439 at a=b=1) specialise
   correctly at `p = 2^31−1`, **term-for-term identical to the repo's own construction**, and
   value-for-value identical to the independent resultant closed form on 4 000 random tuples at
   each prime.
2. Concrete per-candidate numbers in a specified implementation (CPython 3.12.8, M4 Pro), with
   IQRs, for four evaluation modes at two primes, plus the amortisation law
   `362 + 23517/W` ns for `S_4`.
3. An existence proof that the *mode* dominates the cost by ~4 500× at `m=4`, and a reproducible
   harness (`bench_wp2.py`) in which any ledger can re-measure in its own units.
4. That the ~1.6–2.0× growth from 2^20 to 2^31 is a CPython 30-bit-digit effect, demonstrated by
   a probe straddling 2^30 (flat within a digit class, step at the boundary).

**Does not establish**
1. **No GOE claim, no crypto-scale extrapolation.** 2^31 is a toy scale; the curve `y²=x³+7` was
   chosen by the brief, not by any attack model. Nothing here bounds what a real relation search
   costs at 256 bits, and no GOE / complexity exponent is derived or implied.
2. **No portable constant.** The ns/candidate and the group-op ratio are properties of *this*
   interpreter and *this* CPU. In C, both sides drop by 1–2 orders of magnitude and the ratio can
   move either way; in a GPU harness with batch inversion it moves further. Only the *shape*
   (≈2.5 / 6.3 mulmods; `S_4 ≈ 2.5× S_3`) is plausibly portable.
3. **No pinned CPU.** Affinity was refused by the kernel (`KERN_NOT_SUPPORTED`); this is
   single-threaded, uncontended, 5-rep median with IQR, not a hard-pinned measurement. Within-run
   IQR is small for mode B (≤2 %), but between-run drift reaches 5.4 % for mode B and 16 % for the
   one-shot modes (§1), so two significant figures is the honest precision.
4. **Mode C excludes its own memory traffic.** The batched numbers assume cache-resident
   `int64` arrays and do not include writing/streaming a real sieve grid, which is what §4's
   warning about mode A2 is about. A production sieve's per-candidate cost sits between B and C.
5. **`a=0` shrinks the polynomial.** On a `j=0` curve (`y² = x³ + b`) every monomial carrying an
   `a` factor dies: 191 terms instead of 540. That support is *not* the generic curve's; a ledger
   must use the support of the curve it actually searches over. Coefficient heights and supports
   were not re-censused here — they are read from WP1's stored universal polynomials and
   specialised, not re-derived.
6. **Only `m = 3, 4`.** `deg_{x_i} S_m = 2^{m−2}`, so `S_5` is already degree 8 per variable;
   nothing above `m=4` is measured, and the `m`-scaling of evaluation cost is not characterised
   beyond "`S_4` costs ~2.5× `S_3` at these supports", which is not a law.
7. **No claim about which mode a real sieve uses.** B and C are two plausible inner loops, not a
   survey of them; a `y`-side search or a `x4`-root-finding loop has yet another cost profile.

---

## 11. Files and reproduction

```
/Volumes/SSD990/llm/tmp/opencode/g31-004-wp2/
  semaev_eval.py        importable module (stdlib only): load/specialise/evaluate S_3,S_4,
                        F_p and F_{p^2} curve, group-law truth, p=101 self-test
  bench_wp2.py          all timings (modes A/A2/B/C, group-op reference, W sweep,
                        digit-boundary probe); writes results_wp2.json; verifies every loop
  crosscheck_wp2.py     independent validation at p=2^20 and p=2^31 (repo term-for-term,
                        resultant values, group-law positive controls, diagonal identity)
  results_wp2.json      raw medians/IQR/all reps (run 1 — the run quoted everywhere)
  results_wp2.run2.json independent second run, evidence for the §1 reproducibility claim
  results_crosscheck.json
```

```
python3 -B semaev_eval.py        # ~1 s, p=101 self-test
python3 -B crosscheck_wp2.py     # ~1 s, p=2^20/2^31 cross-checks
python3 -B bench_wp2.py          # ~70 s, writes results_wp2.json
```

Read-only inputs: `/Volumes/SSD990-2/crypto-autoresearcher/notes/g31-004-odd-char-census-20261120/`
(`polynomials/*.json`, `census.py`, `validate.py`, `ecfield.py`; repo `harness/semaev.py` imported
under `python -B`). Nothing in that tree was modified. Determinism: seed 31004; the timing
measurements reproduce within a few percent for the headline modes — see §1 for the full
between-run figures.
