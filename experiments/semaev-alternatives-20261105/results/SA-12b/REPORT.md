# SA-12b report

## Summary
**Verdict: KILL** against the frozen criterion, with a noise caveat. At n <= 300 the best full-mode family is at or below the matched convex optimum on all three seeds: full minus convex at cap 300 is -0.0087 (seed 0), +0.0014 (seed 1), -0.0002 (seed 2) paired by seed, and -0.0033 against the best convex of any seed. No seed exceeds convex by more than 0.005 at n <= 300, so SUCCESS fails. All certified reaches (<= 0.134) stay well below 1/6.

## What was run
cert.py and search.py reused unchanged; search2.py (evolutionary search, 1200 s per run, convex and full modes, 3 seeds each, NCAP=300, sequential, nice 10) and grid_convex.py (convex reference). Best-by-cap tables come from all evaluated candidates with lattice dimension n <= cap.

## Results (certified reach, results_table.md, reach_by_cap.png)
| cap n | convex s0/s1/s2 | full s0/s1/s2 | best convex | best full | diff |
|---|---|---|---|---|---|
| 90 | .0843/.1134/.0890 | .0843/.1281/.0890 | .1134 | .1281 | +.0148 |
| 120 | .1340/.1267/.1085 | .1017/.1281/.1040 | .1340 | .1281 | -.0059 |
| 200 | .1340/.1267/.1145 | .1252/.1281/.1107 | .1340 | .1281 | -.0059 |
| 300 | .1340/.1267/.1309 | .1252/.1281/.1307 | .1340 | .1307 | -.0033 |
Convex grid reference: 0.1193 at n=196 (caps >= 200).
Episodes: convex 2580/5583/804, full 3191/16930/477.

## Verdict reasoning
KILL needs the best full family within 0.002 of or below the matched convex optimum on all seeds at n <= 300: true at cap 300 (paired and against the best convex). The only full gain above 0.005 is at cap 90 on seed 1 (+0.0148 vs best convex 0.1134); it is one seed, and at cap >= 120 the convex seed 0 run (0.1340, n=110) is above it, so it reflects search variance in the convex runs, not a family advantage. The prediction (full never exceeds convex by more than 0.002) is violated only at the n=90 cap on one seed. Both modes plateau 0.125-0.134 at n <= 300; approach to 1/6 is not shown at this size.

## Limitations
- Search variance between seeds of the same mode (0.1267 to 0.1340 convex) is about 0.007, larger than the 0.002 and 0.005 thresholds; the matched "optimum" is a search lower bound, not exact (no MILP, see DEVIATIONS).
- Episode counts differ up to 35x between runs under equal wall clock (host load).
- No planted recovery run (success precondition not met). Single cert instance, 48-bit p.

## Suggested lead-atlas update
LEAD-EXO-ml-learned-models, lattice-design arm: disposition toward closed/negative for non-convex, non-monomial shifts on S_3 up to lattice dimension 300 (full minus convex = -0.0033 at n <= 300, paired by seed -0.0087/+0.0014/-0.0002; both modes plateau at 0.13, below 1/6). Caveat: search noise (~0.007) exceeds the thresholds, so reopen only with an exact convex optimum under the cert.py metric.
