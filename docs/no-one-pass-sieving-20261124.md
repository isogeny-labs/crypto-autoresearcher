# No one-pass sieving: full-sumset methods cost Ω(p)

**Status:** closure note, 2026-11-24. Lemma + proof sketch; no experiment needed.
Scope: any factor base B ⊆ G with G cyclic of prime order ≈ p, any m ≥ 1.

## The claim

Computing the **complete** m-fold sumset `mB = {P₁ + … + P_m : Pᵢ ∈ B}` — or
equivalently the full decomposition table for *all* targets — requires Ω(p)
work and Ω(p) space in the dense representation. Consequently "build the entire
relation table on a GPU" is dominated by Pollard rho by a factor ~p^{1/2},
unconditionally, for every base and every m.

## Why

1. `mB ⊆ G` and `|G| ≈ p`. Producing a table that answers decomposition queries
   for every target means producing information about a subset of a set of size
   p; in the dense (indicator/table) representation that is Ω(p) bits, and
   filling a dense table is Ω(p) operations.
2. With a fast transform, the m-fold cyclic convolution of the base indicator
   costs Θ(p log p) field operations (FFT over Z/N) — asymptotically optimal for
   dense output, and still Ω(p).
3. The generic lower bound for computing the *whole* table is therefore Ω(p),
   while rho costs Θ(√p). The ratio is p^{1/2}, not a small constant.

## What this closes, and what it does not

**Closed:** any proposal of the form "enumerate all m-tuples once / convolve the
base with itself / build a full relation table" as a way to beat rho. This
recurs whenever relation search gets expensive, and the bound is independent of
m, of the base's geometry, and of the solver.

**Not closed:** sparse or structured computation that produces only a *slice* of
the table (e.g. decompositions for a small target set, or a compressed
representation). Such a method would be a genuine result — but it must then pay
the per-target cost, which is where the interesting question lives (see the
prime-field solver leads, L5/L16 in `open-leads-20261123.md`).

**Also not closed:** using a convolution as an *offline counting* instrument at
toy scale. That is what the G31-001 replication did to verify pair-sum tables,
and it is legitimate precisely because it is not proposed as an attack.

## Relation to the program

- Consistent with the IG/IC cost accounting in G30-001: a full table is a
  preprocessing cost S ≈ p, and the CGK gate (G30-002) already rejects advice
  regimes with S·T² above the generic floor. This note is the ECDLP-specific
  instance of that same accounting.
- Does not depend on any conjecture, calibration, or implementation detail, so
  it needs no experiment and no review of measurement.

## One-line version

Any method that materialises the whole relation table pays Ω(p) ≥ √p · √p, so
it cannot be a sub-rho attack; only per-target/structured computation can be.
