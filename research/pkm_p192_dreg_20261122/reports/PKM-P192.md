# PKM auxiliary-curve test over NIST P-192 (Rust)

Implementation: `rust/src/main.rs` — `num-bigint` field arithmetic, affine Velu 2-isogeny chain, Jacobian coset enumeration, P-192 target factor-base census, Semaev S3 positive control. No Python in the executed test.

## Command

```sh
cd rust
cargo build --release --offline
./target/release/pkm-p192-test > ../results-rust.json
```

Runtime: **17.31 s** on the local host.

## Field and curves

- p = 2^192 - 2^64 - 1, **192 bits**, p mod 4 = 3, v2(p+1) = **64**.
- Auxiliary E0: y^2 = x^3 + x, j = 1728, supersingular by j=1728 and p=3 mod 4; #E0 = p+1 (trace 0). A point R of exact 2^64 order was found.
- Target: NIST P-192, y^2 = x^3 - 3x + b with b = 0x64210519e59c80e7… and the NIST order field pinned.

## Full 64-step chain

- Steps: **64**, all curve/kernel assertions passed in **0.027 s**.
- Final curve: a = 34198730508578093839…, b = 55784721071112265148…
- R image at the end: **infinity**. This is expected: with L=64 the kernel is <R>, so R maps to O and the x-set is negation-collapsed.

## Subchain census and P-192 factor base

| L | V points | V distinct x | P-192 points with x in V | density | chain map | planted recoveries | S3=0 |
|---:|---:|---:|---:|---:|---|---:|---:|
| 4 | 16 | 16 | 15 | 0.9375 | True | 24/24 | 24/24 |
| 8 | 256 | 256 | 119 | 0.4648 | True | 25/25 | 25/25 |
| 12 | 4096 | 4096 | 2052 | 0.5010 | True | 25/25 | 25/25 |
| 16 | 65536 | 65536 | 32848 | 0.5012 | True | 25/25 | 25/25 |

Every planted P+Q target was recovered by x-coordinate lookup, and the Semaev S3 relation vanished for every recovered pair. The factor-base density is ~1/2, as expected.

## Structural P-192 index-calculus regime

| L | V points | distinct x | FB points (~half) | log2(V_x^6 / N) | R image |
|---:|---:|---:|---:|---:|---|
| 32 | 4294967296 | 4294967296 | 2147483648 | 0 | 18776508982497 |
| 64 | 18446744073709551616 | 9223372036854775808 | 4611686018427387904 | 186 | infinity |

For P-192, the m=6 relation count scales as V_x^6 / N, i.e. 6L - 192 in log2 using distinct x (L=64 collapses to 63). With B ~ |FB| ~ V_x/2, subtract 6: L=32 is ~2^-6 expected relations and **L=33 is the first rung with O(1) expected relation supply**. At L=32 the dense minimal-polynomial encoding has degree 2^32, while the chain encoding uses 2L = 64 variables/equations per point.

## What this establishes / does not establish

- Establishes: the PKM p+1 supersingular auxiliary construction and its 64-step 2-isogeny chain exist and verify over the actual NIST P-192 prime; the chain-mapped x-set is a valid factor base on the P-192 target curve; planted decompositions satisfy the Semaev S3 relation.
- Does not establish: any Groebner/F4 degree-of-regularity advantage, any relation campaign, or any ECDLP speedup. L=32 was built structurally, not enumerated or solved.
- The test does not recompute #E0 by SEA; supersingularity follows from j=1728 with p=3 mod 4, and #E0=p+1 from trace 0.
