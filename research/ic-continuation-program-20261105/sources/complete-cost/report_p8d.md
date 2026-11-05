# P8d results: end-to-end pipeline, cheap membership, charged selection

Protocol [`PROTOCOL_P8D.md`](PROTOCOL_P8D.md) with amendment P8d-1. 480 runs, all verified and replayed; there were 0 fallbacks. Every phase is charged in GAE, including the selector's own work. This accounting is new, so these numbers are not comparable with earlier S.

## Comparisons over the 15 band-17 curves (mean log2 ratio, bits, 95% interval)

| comparison | low prices | mid prices | high prices |
|---|---|---|---|
| **headline: S16 vs L16** | -1.17 (-1.67, -0.69), n=12 | -1.21 (-1.71, -0.70), n=12 | -1.23 (-1.76, -0.68), n=12 |
| headline, h = 1 only | -0.85 (-1.23, -0.20), n=3 | -0.88 (-1.17, -0.31), n=3 | -0.94 (-1.26, -0.56), n=3 |
| headline, h > 1 | -1.28 (-1.92, -0.62), n=9 | -1.31 (-1.96, -0.63), n=9 | -1.32 (-2.05, -0.55), n=9 |
| S16 vs old pipeline (Lfresh) | -4.89 (-5.84, -3.93), n=12 | -4.82 (-5.76, -3.87), n=12 | -4.65 (-5.55, -3.73), n=12 |
| X16 (scan all) vs L16 | +3.16 (+2.36, +4.00), n=12 | +3.50 (+2.76, +4.27), n=12 | +4.02 (+3.37, +4.71), n=12 |
| S16 (staged) vs X16 (scan all) | -4.51 (-4.98, -3.98), n=15 | -4.84 (-5.21, -4.41), n=15 | -5.33 (-5.64, -5.01), n=15 |
| Sfresh vs Lfresh | -2.20 (-3.24, -1.14), n=12 | -2.18 (-3.20, -1.14), n=12 | -2.10 (-3.07, -1.12), n=12 |
| L16 vs Lfresh (walk alone) | -3.72 (-4.54, -2.81), n=12 | -3.62 (-4.49, -2.68), n=12 | -3.42 (-4.37, -2.40), n=12 |
| S1 vs S16 (k = 1 vs 16) | -0.16 (-0.26, -0.06), n=15 | -0.15 (-0.24, -0.06), n=15 | -0.12 (-0.20, -0.04), n=15 |

The headline rule is **met**: the mid-band mean is at most −0.5 bits, and the upper interval end is below 0 in every band.

Legacy has **no usable base** on 68041-generic, 68041-j1728, 87481-generic (h = 4, 4, 7). The expanded domain solves them. These curves are left out of the paired means, so the means understate the domain gain.

## Reading

* **Staged selection is essential.** Scanning every expanded candidate costs about 3.5 bits *more* than legacy, because inspecting the grid outweighs the solve. Choosing m from expected counts first, then inspecting only that m's cosets, removes that cost (S16 vs X16 about −4.8 bits).
* **The new pipeline beats the old one end to end.** It improves on the same runner with the same walk by about 1.2 bits, and on the old fresh-target pipeline by about 4.8 bits. The h = 1 line, the deployed-curve case, is −0.9 bits.
* **One jump beats 16 jumps by about 0.15 bits** in every band. This was a pre-registered secondary question, so k = 1 becomes the default to test next.
* **Leaderboard curve** (p = 65353, h = 1): S16 costs 2^12.42 GAE. The programme's best recipe costs 2^11.54, with rho at 2^8.79. These are indicative only, since the runner and unit pins differ. This pipeline is still about 0.9 bits behind the leaderboard's prime-field method on its own curve.
* **These are constant-factor gains.** The exponent is unchanged.

## S16 per workload: matched-rho gap (mid band)

| workload | h | r | pick (m, c, fold) | S16 GAE | L16 GAE | matched rho | gap bits | selection share |
|---|---|---|---|---|---|---|---|---|
| 68041-j0 | 1 | 68023 | (42, 67, 1) | 3688 | 8291 | 133 | 4.8 | 40% |
| 68041-j1728 | 4 | 17021 | (108, 1, 1) | 3714 | no base | 82 | 5.5 | 61% |
| 68041-generic | 4 | 17077 | (90, 620, 1) | 5443 | no base | 116 | 5.6 | 49% |
| 76801-j0 | 7 | 10903 | (150, 30, 1) | 16956 | 66213 | 53 | 8.3 | 82% |
| 76801-j1728 | 2 | 38677 | (64, 1, 1) | 4009 | 15221 | 123 | 5.0 | 39% |
| 76801-generic | 2 | 38449 | (64, 1, 1) | 4179 | 14546 | 174 | 4.6 | 26% |
| 87481-j0 | 7 | 12577 | (135, 1, 1) | 12299 | 14242 | 57 | 7.7 | 79% |
| 87481-j1728 | 2 | 43481 | (72, 328, 1) | 3486 | 24615 | 131 | 4.7 | 45% |
| 87481-generic | 7 | 12491 | (162, 223, 1) | 9291 | no base | 99 | 6.6 | 65% |
| 96001-j0 | 1 | 96079 | (48, 3515, 1) | 4202 | 9387 | 159 | 4.7 | 42% |
| 96001-j1728 | 4 | 23873 | (120, 1, 1) | 4061 | 6360 | 97 | 5.4 | 57% |
| 96001-generic | 1 | 95507 | (40, 1, 1) | 7661 | 9480 | 274 | 4.8 | 17% |
| 121501-j0 | 7 | 17383 | (162, 1886, 1) | 17423 | 34989 | 67 | 8.0 | 83% |
| 121501-j1728 | 8 | 15269 | (180, 68, 1) | 15164 | 10331 | 77 | 7.6 | 81% |
| 121501-generic | 2 | 60779 | (75, 103, 1) | 6956 | 27936 | 218 | 5.0 | 22% |
| LB16-65353 | 1 | 65003 | (42, 1, 1) | 5471 | 16352 | 226 | 4.6 | 19% |
