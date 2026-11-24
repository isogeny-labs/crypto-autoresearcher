# L1 partial execution — N=⌊p^(1/4)⌋ arm (2026-11-24)

**Lead:** L1 in `crypto-autoresearcher/docs/open-leads-20261123.md`
(charter-signal follow-up cell 13/N3/m=4).

**Scope.** This executes the **new N = ⌊p^(1/4)⌋ arm** at 2000 targets on the
**20 frozen G31-001 replication curves** (10 per size, 13 and 17 bits). It is a
partial L1 execution: the pre-registered L1 design asks for 25–30 curves per
cell; this run has 10 per size. It is therefore a recorded negative for the N4
arm at this power, **not** the full L1 verdict.

## Setup

- Curves, generators, and target rule are the frozen
  `notes/g31-001-replication-20261121/frozen_config.json` curves (prime order,
  distinct j).
- `N = ⌊p^(1/4)⌋`; base = first N x-values on the curve; ordered m-tuple
  counting by the existing `replib.py` cyclic-convolution engine.
- 2000 targets per curve, shared across `m` and null draws.
- Primary null: negation-closed random base (B/2 pairs `{±P}`); secondary:
  uniform random base. 50 draws per cell, as in the frozen replication.
- 10 curves per cell; cell z = mean per-curve z / (sd/√10), t₉ p-value; Holm
  over the four N4 cells (`m=3,4` × 13,17 bits).

## Results (N4, 2000 targets, 50 null draws)

| cell | b range | predicted frac | d vs symmetric (pp) | cell z (sym) | p (sym) | Holm4 (sym) | signs (sym) |
|---|---|---:|---:|---:|---:|---:|---:|
| 13/N4/m=3 | 6–14 | 0.0252 | −0.01 | +0.26 | 0.802 | 1.000 | 5/5 |
| 13/N4/m=4 | 6–14 | 0.0714 | +0.22 | +1.41 | 0.191 | 0.763 | 7/3 |
| 17/N4/m=3 | 10–24 | 0.0077 | +0.06 | +1.01 | 0.341 | 1.000 | 6/4 |
| 17/N4/m=4 | 10–24 | 0.0372 | −0.13 | −0.48 | 0.644 | 1.000 | 4/6 |

Secondary (uniform null), shown only to confirm the known null bias:

| cell | d vs uniform (pp) | cell z (uni) | p (uni) | Holm4 (uni) | signs (uni) |
|---|---:|---:|---:|---:|---:|
| 13/N4/m=3 | −0.51 | −3.39 | 0.0080 | 0.0160 | 2/8 |
| 13/N4/m=4 | −2.78 | −6.43 | 0.00012 | 0.00048 | 0/10 |
| 17/N4/m=3 | −0.05 | −1.71 | 0.122 | 0.122 | 2/8 |
| 17/N4/m=4 | −1.14 | −5.29 | 0.00050 | 0.00150 | 0/10 |

## Reading

- Against the **negation-matched** null, no N4 cell reaches |cell z| ≥ 2.5
  (largest is +1.41) and no Holm-adjusted p is below 0.05. The N4 arm shows no
  x-window effect at this power.
- Against the **uniform** null, the same conservative bias as in the N3
  replication appears: every informative cell is negative, with 0/10 signs at
  m=4. This is the known non-exchangeability of the uniform null, not an
  x-geometry signal.
- The N4 result is consistent with the frozen replication's N3 conclusion and
  does not support the pilot's 2.2 pp cell.

## Exact commands

```sh
cd notes/g31-001-replication-20261121
python3 l1_n4_run.py          # writes l1_n4_20261124/results_n4.json and analysis_n4.json
```

Runtime ≈ 4 minutes on one machine.

## What this establishes

- At 13/17 bits, N=⌊p^(1/4)⌋, 2000 targets, 10 curves per cell, there is no
  detectable x-window advantage against a negation-closed null.
- The uniform-null bias persists in the new arm, as expected.

## What this does not establish

- Not the full 25–30-curve L1 design; the achieved MDE is larger than the
  pre-registered design's.
- No claim at larger p or for the `13/N3/m=4` cell specifically; that cell is
  not re-tested here with 25–30 curves.
- Single machine, one seed family, 50 null draws.
