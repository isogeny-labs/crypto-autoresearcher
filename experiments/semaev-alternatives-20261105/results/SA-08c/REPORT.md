# SA-08c: excess-sign flag, K = 7, 8 and exact SVP checks

## Summary

**Verdict: KILL** against the frozen criterion. Absolute excess of the lambda_2 crossing over the determinant threshold delta_K is 0.0024 at K = 7 and 0.0033 at K = 8 (both <= 0.005), and every extrapolation and leave-one-out value over K = 3..8 lies between 0.1455 and 0.1637, i.e. below 1/6 + 0.005 = 0.1717 (and also below 1/6 itself). No SUCCESS clause holds: no estimate exceeds 1/6 + 0.01, and the excess is negative and growing in magnitude, not positive.

Deciding numbers (64 bits, planted, box support, BKZ-20 mpfr proxy):

| K | n | delta_K | lambda_2 crossing | signed excess | absolute excess |
|---|---|---|---|---|---|
| 3 | 49 | .1190 | .1216 | +.0026 | .0026 |
| 4 | 81 | .1296 | .1305 | +.0009 | .0009 |
| 5 | 121 | .1364 | .1359 | -.0004 | .0004 |
| 6 | 169 | .1410 | .1395 | -.0016 | .0016 |
| 7 | 225 | .1444 | .1421 | -.0024 | .0024 |
| 8 | 289 | .1471 | .1438 | -.0033 | .0033 |

K = 3..6 from SA-08b (grid 0.01); K = 7, 8 new (grid 0.005).

Extrapolation to K -> infinity over K = 3..8 (leave-one-out range in brackets):

| estimator | 1/K model | 1/K^2 model |
|---|---|---|
| plain crossing | 0.1573 [0.1572, 0.1574] | 0.1462 [0.1455, 0.1477] |
| 1/6 + extrapolated excess | 0.1604 [0.1595, 0.1608] | 0.1633 [0.1625, 0.1637] |

## What was run

- lam2.py (lam.py of SA-08b, planted-only, isqrt norm fix): K = 7 at delta .135/.140/.145 (4 instances each), K = 8 at .140/.145 (2 each), 64 bits, box support, LLL then BKZ-20 (4 loops, mpfr 300 bit). Raw: raw/box_64_7.json, raw/box_64_8.json.
- svp.py: exact enumeration of lambda_1 and lambda_2 at 48 bits, K = 2, 3, 4, planted, near the crossing, compared with the BKZ-20 proxy on the same instance. Raw: raw/svp_48_{2,3,4}.json; table svp_table.md.
- analyze.py: crossings (linear interpolation of mean log lambda_2 - log HG), signed and absolute excess, fits and leave-one-out; results.json; fig_excess.png.

## Results

Mean log(lambda_2) - log(HG bound): K = 7: -4.44 (.135), -1.30 (.140), +1.86 (.145); K = 8: -2.73 (.140), +0.86 (.145). Instance spread within a point is <= 0.15 log units for K = 7, <= 0.07 for K = 8, i.e. a crossing error of about 0.0001 from instance noise; the interpolation across a 0.005 step is the larger error (about 0.0005, since the transition is steep and nearly linear). lambda_1 and lambda_2 agree to 0.1 log units everywhere.

Exact SVP versus proxy (svp_table.md, 16 instance-points): K = 2 and 3 identical in all but one entry (lambda_2 lower by 0.009 at K = 3). K = 4 (dim 81): exact lambda_1 is lower than the proxy by 0.09, 0.00, 0.010, 0.014 in log, lambda_2 by 0.083, 0.00, 0.010, 0.044. The slope of log lambda against delta there is about 250, so the worst proxy error moves a crossing by 0.0004, and always downward (exact minima are shorter, so the true crossing is at or below the proxy's). That error direction cannot raise the crossing above delta_K, so it cannot support SUCCESS and, if anything, makes the excess more negative.

## Verdict reasoning

- KILL clause 1 (absolute excess <= 0.005 at K = 7 and 8): 0.0024 and 0.0033, met.
- KILL clause 2 (leave-one-out range at or below 1/6 + 0.005 = 0.1717): the maximum over all four estimators and all LOO fits is 0.1637, met. The plain-crossing fits (0.146-0.157) are biased low as in SA-08b; the excess-corrected ones (0.160-0.164) are not, and both are below 1/6.
- SUCCESS: needs an extrapolation above 0.1767 with LOO above 1/6 (maximum is 0.1637), or a positive excess growing beyond 0.01 (the excess is negative, -0.0033 at K = 8). Not met.
- The earlier flag is resolved as follows: the absolute excess did keep growing after crossing zero (0.0004, 0.0016, 0.0024, 0.0033 at K = 5..8, roughly linear in K in this range), but it is the crossing falling below the determinant threshold, never above it. It does not stabilise yet at K = 8; it stays under the frozen 0.005 bar but would pass it near K = 10-11 if the linear trend continued (extrapolation, not measured). Because the sign is negative, this is the wrong sign for SUCCESS, though it means the pre-registered prediction "absolute excess <= 0.005 for K = 5..8" holds only marginally.

## Limitations

- BKZ-20 proxy; exact SVP only to K = 4 at 48 bits (dimension 81). K = 7, 8 (dimension 225, 289) rest on the proxy, validated indirectly by the K = 4 comparison and SA-08b's BKZ-30 comparison (K = 4).
- K = 8 has 2 instances per point and only two grid points, so its crossing is a single linear interpolation, error about +-0.001. K = 3..6 use SA-08b's coarser grid (0.01). Planted instances only at K = 7, 8; one curve, box support only.
- Extrapolation from K <= 8 where delta_K is still 0.02 below 1/6; the two excess-corrected estimators assume the excess is smooth in 1/K, whereas it is drifting roughly linearly in K here. A fit that extrapolated that drift would give an even lower ceiling, so the assumption is conservative for KILL.
- Not a proof of a ceiling; the Zhang-balance step from SA-08b remains open.

## Suggested lead-atlas update

LEAD-ICP-coppersmith-smallroot-semaev: SA-08c resolves the SA-08b sign flag: with K extended to 7 and 8 at 64 bits (box, planted, BKZ-20 proxy, exact SVP checked to K = 4 at 48 bits with proxy error <= 0.09 log units, about 0.0004 in delta), the lambda_2 crossing sits below the determinant threshold by 0.0024 (K = 7) and 0.0033 (K = 8), increasing in magnitude with K, extrapolated ceiling 0.146-0.164 (all leave-one-out values below 1/6). Disposition: KILL for any K-growing reach beyond the determinant bound on the realised Rees lattices; keep SA-08 "closed for determinant arguments". Next action only if someone wants a proof: the Zhang-type balance statement; further numerics at K >= 9 would not change the disposition.
