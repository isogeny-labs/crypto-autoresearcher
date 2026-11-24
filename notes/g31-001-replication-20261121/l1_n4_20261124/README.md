# L1 execution — N=⌊p^(1/4)⌋ arm (2026-11-24)

**Lead:** L1 in `crypto-autoresearcher/docs/open-leads-20261123.md`
(charter-signal follow-up cell 13/N3/m=4).

**Scope.** This executes the **new N = ⌊p^(1/4)⌋ arm** at 2000 targets.

- **Primary run:** 30 curves per size (13 and 17 bits), 50 negation-closed null
  draws, symmetric null only. This meets the L1 curve count for the N4 arm.
- **Preliminary run:** the frozen 10-curve/size set with 50 symmetric + 50
  uniform draws; included for the uniform-null comparison.

The full L1 design also re-tests the **N3** arm at 25–30 curves/cell (the
13/N3/m=4 near-miss). That is not done here; the frozen N3 replication had 10
curves/size.

## Setup

- Curves: the frozen G31-001 replication curves (prime order, distinct j) for
  slots 0–9; new deterministic slots 10+ with distinct j until 30 per size.
- `N = ⌊p^(1/4)⌋`; base = first N x-values; ordered m-tuple counting by
  `replib.py` cyclic convolution.
- 2000 targets per curve, shared across `m` and null draws.
- Primary null: negation-closed random base (B/2 pairs `{±P}`), 50 draws.
- Cell z = mean per-curve z / (sd/√n), t p-value; Holm over the four N4 cells.

## Primary result (30 curves/size, 2000 targets, 50 symmetric draws)

| cell | curves | b range | predicted frac | d (pp) | cell z | p | Holm4 | signs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 13/N4/m=3 | 30 | 6–14 | 0.0217 | −0.018 | −0.24 | 0.809 | 1.000 | 13/17 |
| 13/N4/m=4 | 30 | 6–14 | 0.0596 | +0.219 | +1.63 | 0.114 | 0.457 | 19/11 |
| 17/N4/m=3 | 30 | 10–24 | 0.0080 | +0.039 | +1.32 | 0.199 | 0.596 | 17/13 |
| 17/N4/m=4 | 30 | 10–24 | 0.0388 | +0.023 | +0.14 | 0.886 | 1.000 | 15/15 |

No N4 cell reaches |cell z| ≥ 2.5; no Holm-adjusted p is below 0.05. The
largest is 13/N4/m=4 at z=+1.63 (19/11 signs, Holm p=0.457).

## Preliminary 10-curve run and the uniform null

On the frozen 10/size set, the symmetric-null result was already null (max
|z|=1.41). The uniform secondary null keeps its known conservative bias:

| cell | d vs uniform (pp) | cell z (uni) | Holm4 (uni) | signs (uni) |
|---|---:|---:|---:|---:|
| 13/N4/m=3 | −0.51 | −3.39 | 0.0160 | 2/8 |
| 13/N4/m=4 | −2.78 | −6.43 | 0.00048 | 0/10 |
| 17/N4/m=3 | −0.05 | −1.71 | 0.122 | 2/8 |
| 17/N4/m=4 | −1.14 | −5.29 | 0.00150 | 0/10 |

This is the same non-exchangeability seen in the frozen N3 replication, not an
x-geometry signal.

## Exact commands

```sh
cd notes/g31-001-replication-20261121
python3 l1_n4_run_30.py        # primary 30-curve N4 arm, symmetric null
python3 l1_n4_run.py           # 10-curve preliminary, both nulls
```

The 30-curve run is ≈10 minutes on one machine.

## What this establishes

- At 13/17 bits, `N=⌊p^(1/4)⌋`, 2000 targets, 30 curves/size, there is no
  detectable x-window advantage against a negation-closed null. The N4 arm is
  a recorded negative at the L1 curve count.
- The uniform-null bias persists, as expected.

## What this does not establish

- Not the full L1 verdict: the N3 arm is still at 10 curves/size, so the
  13/N3/m=4 near-miss is not re-tested at 25–30 curves.
- No claim at larger p; toy sizes only.
- One seed family, 50 null draws, one machine.
