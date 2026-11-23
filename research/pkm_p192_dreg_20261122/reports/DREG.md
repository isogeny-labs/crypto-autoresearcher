# Groebner/F4 degree-of-regularity advantage: PKM chain vs dense Semaev encoding

Rust harness: `dreg-pkm/src/main.rs` generates both systems; msolve 0.11.0
performs F4 and its `-v 2` round table is parsed for the maximum selected
degree. No Python is used in the experiment.

## Method

- Same PKM factor base `V = x(R + <K>)` in both arms, same target `T`, same
  `S_{m+1}` equation, same field and monomial order (DRL).
- **Arm A (chain)**: `L` quadratic Velu equations per x-coordinate (`mL`
  variables).
- **Arm B (dense)**: the same `V` as one minimal polynomial of degree `2^L`
  per x-coordinate (`m` variables).
- `d_reg` = maximum `deg` in msolve F4 rounds. Base cells: 3 seeds, 60 s cap.
  Supplement: one seed, 300 s cap.

## m = 2 (S3)

| L | d_reg chain A | d_reg dense B | B − A | median F4 s A | median F4 s B |
|---:|---:|---:|---:|---:|---:|
| 3 | 5 | 10 | 5 | 0.049 | 0.045 |
| 4 | 5 | 18 | 13 | 0.039 | 0.031 |
| 5 | 5 | 34 | 29 | 0.048 | 0.033 |
| 6 | 5 | 66 | 61 | 0.251 | 0.048 |
| 7 | 5 | 130 | 125 | 6.660 | 0.115 |
| 8 | 5* | 258 | 253 | >60 | 0.788 |
| 9 | 5 | 514 | 509 | 52.277 | 3.106 |

## m = 3 (S4 via two S3 equations sharing X)

| L | d_reg chain A | d_reg dense B | B − A | F4 s A | F4 s B | note |
|---:|---:|---:|---:|---:|---:|---|
| 3 | 6 | 12 | 6 | 28.656 | 2.440 |  |
| 4 | 6* | 20 | 14 | >60 | 30.573 | A hit 60 s timeout |
| 5 | 7* | 36 | 29 | >300 | 263.047 | A hit 300 s timeout |

## Finding

The dense encoding grows as **2^L + 2** for m=2 (10, 18, 34, 66, 130, 258,
514) and **2^L + 4** for m=3 (12, 20, 36). The chain encoding stays small:
**5** for m=2 through L=9 (the L=9 chain run completed in 52 s) and at most 7
for m=3 through L=5 (the L=5 chain run hit the 300 s cap; 7 is a lower bound).
At the largest completed m=2 cell the advantage is **514 vs 5**; at m=3 L=5 it
is at least **36 vs 7**.

**Important scope:** this establishes a *d_reg* advantage, not a total F4
runtime or index-calculus advantage. At these toy sizes the chain system has
more variables and is often slower in wall time (e.g. m=2 L=9: 52 s vs 3 s),
because msolve exploits the dense univariate structure. The result is about
the algebraic degree reached by F4, which is the quantity the goal names;
translating it into a cost win needs a solver that does not collapse the dense
univariate system.

## Reproduce

```sh
cd dreg-pkm
cargo build --release --offline
./target/release/dreg-pkm > ../results/dreg-results.jsonl
DREG_MODE=supp ./target/release/dreg-pkm > ../results/dreg-supplement.jsonl
```

Raw data: `results/dreg-results.jsonl`, `results/dreg-supplement.jsonl`.
