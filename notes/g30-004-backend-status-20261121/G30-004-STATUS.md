# G30-004 backend status — what exists, what it can measure, what it cannot (2026-11-21)

**Status:** instrument note, unreviewed. This is **not** G30-004 completed: no
harness module was commissioned and no ledger state changed. It records what a
one-session attempt established, so the next attempt starts from facts.

## 1. Toolchain is available on this machine

- `sage` (/Users/adamburan/.local/bin/sage) with Singular inside — GB over GF(p) works.
- `msolve` (/opt/homebrew/bin/msolve) — F4 over prime fields, fast.
- `sympy` 1.14.

So G30-004's blocker ("no true d_reg backend") is an integration/validation
problem, not an availability problem.

## 2. Validated: the solver agrees with brute force on the real object

`validate_dreg.py`: builds the m=3 system S₄(x₁,x₂,x₃,x_Q)=0 with the three
membership polynomials of an x-window base (roots = base x-values), computes a
Gröbner basis over GF(p), and compares `vector_space_dimension()` against
brute-force counting of base triples summing to the target.

| p | k (base x-values) | brute-force decompositions | GB solutions | dim |
|---|---|---|---|---|
| 4099 | 4 | 1 | 1 | 0 |
| 4099 | 5 | 1 | 1 | 0 |
| 4099 | 6 | 1 | 1 | 0 |

**That is the important positive result:** the system encoding (S₄ via
Res_D(S₃(x₁,x₂,D), S₃(x₃,x_Q,D)) plus membership polynomials) is *faithful* —
it reproduces the combinatorial solution count exactly. Note the bug that was
found and fixed on the way: the first version used S₂ for one side of the
resultant, which produced an inconsistent system (dim = −1) while brute force
found a decomposition; the correct recursion is S₃-slice against S₃-slice.

## 3. What the obvious metrics cannot do

- **Final reduced GB max degree is worthless as a d_reg proxy.** For a
  one-solution ideal the reduced basis is linear (`maxdeg = 1`) regardless of
  the input degrees (12, 4–8). The repo's existing `max_degree` proxy is
  flagged as "NOT d_reg" in `harness/semaev.py`; this is a concrete
  demonstration of exactly how it fails.
- **`I.regularity()` does not exist** on `MPolynomialIdeal` in this Sage build,
  so Castelnuovo–Mumford regularity needs `hilbert_series()` post-processing (or
  Singular's `hilb` directly). Not implemented here.
- **Normal-basis degree and quotient dimension are degenerate** when the ideal
  has ≤ 1 solution, which is the typical case at toy scale (see §4).

## 4. The design constraint nobody had written down

At m = 3, the expected number of decompositions of a target is |B|³/p. For the
solving-degree question to be non-degenerate (say ≥ 30 solutions, so the
quotient algebra is a real object), one needs

  |B| ≥ (30 p)^{1/3}.

At p = 4099 that is |B| ≈ 50; at p ≈ 2²⁰ it is ≈ 200. Membership polynomials
then have degree |B|, and the system is 4 equations in 3 variables of degree
|B| — computable, but not at the "k = 4–8" scale of the pilots above, where
every cell is a one-solution ideal and every d_reg statistic collapses.

**Consequence for G32-001 WP2 and G30-006:** a meaningful cell needs
|B| ≈ (few×p)^{1/m}, not a fixed small base. Previous toy cells may have been
measuring the collapse, not the degree.

## 5. What is still missing for G30-004

1. A regularity/solving-degree measurement that survives multi-solution ideals
   (hilbert series post-processing, or an explicit F4 that records the top
   degree reached).
2. A harness module with admission checks (the repo's harness-change gate
   applies; this session deliberately did not write into `harness/`).
3. The cell-design rule from §4 encoded in the experiment contract, so future
   d_reg cells cannot be one-solution degenerates.
4. Reproducing one published cell (e.g. a D6-at-n=12 boolean cell) as an
   external correctness check before any new measurement is trusted.

## 6. Honest summary

One positive (system encoding is faithful, solver agrees with brute force), one
negative (the obvious metrics are degenerate or unavailable), and one design
finding (base size must scale as p^{1/m} for the degree question to mean
anything). No d_reg number is claimed.
