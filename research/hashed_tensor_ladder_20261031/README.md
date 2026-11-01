# Hashed-factor-base tensor ECDL at 40-80-bit prime fields (observation only)

Single-session analysis dated 2026-10-31. Not independently reviewed. No speedup is claimed.

## What this is

A measurement of the compiled Boolean relation networks from the Bochum hashed-factor-base
ECDL reference (Akshima et al., v0.2) at prime field sizes of 40 to 131 bits and slot counts
m = 2 to 7. The counting algorithm from the ETH-refutation papers runs in time about
2^(N / sqrt(log2 N)) on a network of N Boolean variables, with all hidden constants set to 1.
Beating Pollard rho needs that exponent to fall below (1/2 - 1/m) * ell.

## Result

- The compiled networks have 1.7e5 to 3.1e6 variables.
- The counting exponent is 1,484 to 10,110 times the rho exponent at every size and slot count measured.
- With unit constants the crossover is m = 4 and ell above 2^254 (`crossover.py`).
- The Bochum, Kintali and Anthropic size thresholds are all far above 40-80 bits.
  See `HASHED_TENSOR_REVIEW.md` sections 0, 3 and 4.

## Files

| File | Purpose |
|---|---|
| `compile_stats.py` | Compile relation networks and record variables, edges, degree, exponent |
| `crossover.py`, `test_crossover.py` | Closed-form unit-constant crossover and its 5 tests |
| `plot_exponents.py` | Draws `exponents.svg` from `compile-stats.json` |
| `compile-stats.json` | 42 rows plus fits, one real-compile cross-check at ell=40, m=2 |
| `report.typ`, `report.pdf` | Short report (57 KB) |
| `HASHED_TENSOR_REVIEW.md` | Full review and path analysis for 40-80 bits |
| `KR_DRAFTS.md` | Draft known-result texts. Not filed: IDs are placeholders |
| `ADJACENT_PRIME_SAT_REVIEW.md` | Review of the adjacent prime_sat_* thread |

## Reproduce

```
python3 compile_stats.py --ref <cryptanalysis>/experiments/hashed-ecdl-tensor-reference \
    --ells 40,48,56,64,72,80,131 --slots 2,3,4,5,6,7 --jobs 4 --compile 40:2 --out compile-stats.json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_crossover
python3 plot_exponents.py compile-stats.json exponents.svg
```

Needs Python 3.10+, sympy and PARI/GP (`gp`). The run took about 2 minutes.

## Caveats

- Network size comes from the compiler, but the counting exponent is a formula with constants set to 1. It is a lower bound on cost.
- Only one size was cross-checked with a real compile.
- The ETH-refutation claims are under review and unverified.
