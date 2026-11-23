# PKM P-192 auxiliary curves and F4 degree of regularity

Date: 2026-11-22. Rust implementation and measurements.

This directory contains two self-contained Rust experiments:

1. `pkm-p192-test/` — constructs the Petit–Kosters–Messeng (PKM) `p+1`
   supersingular auxiliary curve over the actual NIST P-192 prime
   `p = 2^192 - 2^64 - 1`, verifies the full 64-step 2-isogeny chain, and
   censuses the chain-mapped factor base on the NIST P-192 target curve.
2. `dreg-pkm/` — generates the same PKM factor base in the chain encoding and
   the dense minimal-polynomial encoding, then runs msolve 0.11.0 F4 and
   parses its per-round degree table to compare the degree of regularity.

These are observations and tooling. They create no hypothesis, experiment,
approval, ledger, goal or queue record, and they change no official status.

## Key results

### P-192 construction

- `p mod 4 = 3`, `v2(p+1) = 64`.
- `E0: y^2 = x^3 + x` has `j = 1728`, is supersingular, and has `#E0 = p+1`.
- The full 64-step Velu 2-isogeny chain verifies; with `L = 64` the kernel
  generator `R` maps to infinity and the x-set collapses to `2^63` values.
- For `L = 4, 8, 12, 16`: `|V| = 2^L`, chain-map verification passes, the
  P-192 target factor-base density is ~1/2, and every planted `P+Q` pair is
  recovered with the Semaev `S3` relation equal to zero.

### F4 degree of regularity

Same factor base `V = x(R + <K>)`, same target, same `S_{m+1}` equation,
msolve 0.11.0 F4, DRL order, three seeds per cell.

| m | L | chain d_reg | dense d_reg |
|---|---:|---:|---:|
| 2 | 3 | 5 | 10 |
| 2 | 4 | 5 | 18 |
| 2 | 5 | 5 | 34 |
| 2 | 6 | 5 | 66 |
| 2 | 7 | 5 | 130 |
| 2 | 8 | 5* | 258 |
| 3 | 3 | 6 | 12 |
| 3 | 4 | 6* | 20 |
| 3 | 5 | 6* | 36* |

`*` marks a 60 s per-solve cap; the value is a lower bound. The chain
encoding holds a constant degree of regularity while the dense encoding grows
as `2^L + 2` (m=2) or `2^L + 4` (m=3).

**Scope:** this is a degree-of-regularity advantage, not a total F4 wall-clock
or index-calculus advantage. At these toy sizes the chain system has more
variables and is often slower because the dense system is univariate and
msolve exploits that structure.

## Reproduce

```sh
cd pkm-p192-test
cargo build --release --offline
./target/release/pkm-p192-test > ../results/pkm-p192-results.json

cd ../dreg-pkm
cargo build --release --offline
./target/release/dreg-pkm > ../results/dreg-results.jsonl
```

`dreg-pkm` invokes `msolve` from `PATH`; the measurements above used msolve
0.11.0. Rust toolchain: 1.93.1.

## Files

- `pkm-p192-test/src/main.rs` — BigUint P-192 field/curve/chain/census code.
- `dreg-pkm/src/main.rs` — small-field chain generator, flat polynomial
  expansion, msolve driver and F4 round parser.
- `results/pkm-p192-results.json` — raw construction/census output.
- `results/dreg-results.jsonl` — one JSON row per (m, L, seed) cell.
- `reports/PKM-P192.md`, `reports/DREG.md` — detailed tables and limits.
- `cases/m2L3/A.ms`, `cases/m2L3/B.ms` — one representative pair of inputs.

## Limitations

- Toy fields and `L <= 8` (m=2), `L <= 5` (m=3); not a P-192-scale solve.
- `d_reg` is the maximum F4 selected round degree parsed from msolve, not an
  independently proved regularity bound.
- The d_reg advantage did not translate into lower wall time at these sizes.
- The P-192 construction test does not recompute `#E0` by SEA;
  supersingularity follows from `j=1728` with `p = 3 mod 4`, and `#E0 = p+1`
  from trace zero.
