# L1 execution — N3 and N4 arms at 30 curves/size (2026-11-24)

**Lead:** L1 in `crypto-autoresearcher/docs/open-leads-20261123.md`
(charter-signal follow-up cell 13/N3/m=4).

**Scope.** Executes both the original **N3** arm and the new
**N=⌊p^(1/4)⌋** arm at 2000 targets and **30 curves per size** (13 and 17
bits), meeting the L1 curve count. Null: negation-closed random base, 50 draws.
A preliminary 10-curve run with the uniform secondary null is included for the
null-bias comparison.

## Setup

- Curves: the frozen G31-001 replication curves (prime order, distinct j) for
  slots 0–9; new deterministic slots 10+ with distinct j until 30 per size.
- `N3 = ⌊p^(1/3)⌋`; `N4 = ⌊p^(1/4)⌋`; base = first N x-values.
- Ordered m-tuple counting by `replib.py` cyclic convolution.
- 2000 targets per curve, shared across `m` and null draws.
- Primary null: negation-closed random base (B/2 pairs `{±P}`), 50 draws.
- Cell z = mean per-curve z / (sd/√n), t p-value; Holm over the four cells in
  each arm (m=3,4 × 13,17 bits).

## N3 arm — 30 curves/size, 2000 targets, 50 symmetric draws

| cell | b range | predicted frac | d (pp) | cell z | p | Holm4 | signs |
|---|---:|---:|---:|---:|---:|---:|---:|
| 13/N3/m=3 | 12–28 | 0.1796 | +0.062 | −0.25 | 0.808 | 1.000 | 14/16 |
| 13/N3/m=4 | 12–28 | 0.5971 | **+0.943** | **+2.13** | 0.041 | 0.166 | 18/12 |
| 17/N3/m=3 | 38–60 | 0.1336 | −0.158 | −1.05 | 0.304 | 0.912 | 11/19 |
| 17/N3/m=4 | 38–60 | 0.7725 | +0.004 | −0.02 | 0.985 | 1.000 | 16/14 |

**The 13/N3/m=4 near-miss does not replicate at the L1 curve count.** The
10-curve frozen run had +2.23 pp, cell z=+2.22, 9/1 signs. At 30 curves the
effect attenuates to **+0.94 pp**, cell z=+2.13, **18/12 signs**, Holm-4
p=0.166. It is below the pre-registered bar (`|z|>=2.5`, Holm p<0.05,
sign consistency >=7/10). The original 2.2 pp was a small-sample maximum, not a
stable effect.

## N4 arm — 30 curves/size, 2000 targets, 50 symmetric draws

| cell | b range | predicted frac | d (pp) | cell z | p | Holm4 | signs |
|---|---:|---:|---:|---:|---:|---:|---:|
| 13/N4/m=3 | 6–14 | 0.0217 | −0.018 | −0.24 | 0.809 | 1.000 | 13/17 |
| 13/N4/m=4 | 6–14 | 0.0596 | +0.219 | +1.63 | 0.114 | 0.457 | 19/11 |
| 17/N4/m=3 | 10–24 | 0.0080 | +0.039 | +1.32 | 0.199 | 0.596 | 17/13 |
| 17/N4/m=4 | 10–24 | 0.0388 | +0.023 | +0.14 | 0.886 | 1.000 | 15/15 |

No N4 cell reaches |cell z| >= 2.5; largest is 13/N4/m=4 at +1.63.

## Preliminary 10-curve run and the uniform null

On the frozen 10/size set, the uniform secondary null keeps its known
conservative bias:

| cell | d vs uniform (pp) | cell z (uni) | Holm4 (uni) | signs (uni) |
|---|---:|---:|---:|---:|
| 13/N4/m=3 | −0.51 | −3.39 | 0.0160 | 2/8 |
| 13/N4/m=4 | −2.78 | −6.43 | 0.00048 | 0/10 |
| 17/N4/m=3 | −0.05 | −1.71 | 0.122 | 2/8 |
| 17/N4/m=4 | −1.14 | −5.29 | 0.00150 | 0/10 |

This is non-exchangeability, not an x-geometry signal.

## Exact commands

```sh
cd notes/g31-001-replication-20261121
python3 l1_n3_run_30.py        # N3 arm, 30 curves/size, symmetric null
python3 l1_n4_run_30.py        # N4 arm, 30 curves/size, symmetric null
python3 l1_n4_run.py           # 10-curve preliminary, both nulls
```

Each 30-curve run is ≈10 minutes on one machine.

## What this establishes

- **L1 verdict: not replicated.** At 30 curves/size and 2000 targets, neither
  the N3 nor the N4 arm has a cell passing the pre-registered bar against the
  negation-closed null. The 13/N3/m=4 pilot signal attenuates from +2.2 pp
  (10 curves) to +0.94 pp (30 curves), Holm p=0.166.
- The uniform-null bias persists, as expected.

## What this does not establish

- No claim at larger p; toy sizes only.
- One seed family, 50 null draws, one machine.
- This is a negative for the tested cells; it does not exclude effects below
  the achieved MDE.
