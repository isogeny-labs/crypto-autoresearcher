# L7 — sign / Kummer bookkeeping audit (2026-11-24)

**Status:** audit note, unreviewed. One claim, checked against the code.

## The question

x-coordinates determine points only up to sign, so every relation search has a
2^m sign ambiguity. Is that factor (a) missing from the density laws, (b) a
per-candidate cost that engines should charge, or (c) already absorbed?

## What the code does

| Engine | Sign handling | What it pays |
|---|---|---|
| `crypto/src/cryptanalysis/ec_index_calculus.rs` `find_one_relation` | tries all four combinations `(ε_i, ε_j) ∈ {±1}²` for 2-sums; doc comment states S₃ = 0 only *implies* some signed sum | 4 point additions per candidate x-tuple |
| `crypto/src/cryptanalysis/gaudry_cubic.rs` | "signs settled by group arithmetic", enumerates `s₁,s₂,s₃ ∈ {±1}` for 3-sums | up to 8 point operations per candidate x-triple |
| `crypto-autoresearcher/harness/semaev.py` | enumerates `(sA, sB) ∈ {A, −A} × {B, −B}` when checking a decomposition | 4 point tests per candidate |
| `crypto/scripts/ic_semaev_msolve.py` (this week) | none — solves the x-system only | 0 (signs are *not* resolved; the output is an x-tuple set) |

## The finding

**The 2^m factor is not missing from the density law, and it is not free in the
solver.**

- The density law counts **x-tuples**: `|B|^m/(m!·N)`. That is correct, because
  `S_{m+1}(x₁…x_m, x_Q) = 0` holds iff *some* signed sum equals `O`, so each
  x-tuple is one candidate regardless of signs. Putting 2^m into the density
  formula would double-count.
- The 2^m appears instead as a **per-candidate verification cost**: once a
  candidate x-tuple is found, deciding *which* sign pattern (if any) realises
  the target costs up to 2^m point operations. The three engines above pay it
  explicitly; a solver that stops at the x-system (`ic_semaev_msolve.py`)
  does not pay it but also does not produce usable relations.
- Therefore the cost model must charge `2^m` **point operations per candidate
  x-tuple in the verification step**, while leaving `|B|^m/(m!·N)` unchanged.
  Any model that multiplies the *density* by 2^m is wrong in the same way as
  one that omits the verification cost.

## Recommendation

Add a `sign_convention` field to the experiment contract with three values:

- `full` — enumerate all 2^m sign patterns (what `ec_index_calculus`,
  `gaudry_cubic`, `harness/semaev.py` do); charge 2^m point ops per candidate.
- `kummer` — work on `E/±`, double the relation count needed, and pay the
  parity/consistency check in linear algebra.
- `one_rep` — one representative per ±-orbit in the base; density is halved
  (base is half as large for the same point set) and no sign search is needed.

Two of the three (full, one_rep) are already used somewhere in the tree; the
contract should say which, per experiment, so the numbers are comparable.

## What this does not establish

- No claim about which convention is *better* — that is a cost-model question
  per engine.
- The audit covers four implementations, not the whole tree; a grep for
  `negate(`/`±` in other modules is the cheap next step.
- No new measurement: every number here is a count read from the code.
