# P4 reference arm: status 2026-10-31 (blocked, not run)
No measurement was made. The load gate (1-min load < 40) failed for 20 minutes (23:24-23:44 PDT, load 46-55; see gate_p4_20261031.log),
following the earlier failure logged in RELAUNCH_LOG.md. Per the hard constraint, nothing was started and nothing was killed.
PROTOCOL.md unchanged. Ready: msolve installed, stock WDSat built, builders and tiny_validate.py written but unrun.
Resume order: tiny_validate.py -> build_wdsat.py per cell -> timing driver (not yet written) over n=17,19 m=3 then m=4.
The gating baseline still does not exist; P1/P3/P5 wins remain "vs ourselves".

## 2026-11-01 second attempt: still blocked
Gate re-run 21:54-22:14 PDT (gate_p4_20261101.log, 40 readings every 30 s): 1-min load min 74.3, peak 183; never < 40 (the 21:52 reading of 32.8 had risen to 55 by 21:54 and to 174 by 21:57, from other sessions' fan-out). 20-minute rule triggered; no compute job started, nothing killed. (One stray `find /` I started was stopped immediately.)
Nothing else changed: no timings, PROTOCOL.md untouched, decision not_run. Resume order as above.

## 2026-11-02 run (third attempt, gate passed at load 39-40)
Design note written before the SAT-stratum measurement: the random-target sample (40/cell) contained 0 targets with an algebraic solution,
so SAT-instance cost is unmeasured. A second stratum of 20 targets with a genuine decomposition (exact label) is timed for ms_F1, ms_F2, WDSat
(MXL skipped: the lab arm has no SAT termination rule). Cost per attempt is then (1-P)*c_UNSAT + P*c_SAT, cost per relation = that / P.
No decision thresholds are added; PROTOCOL.md unchanged.

## RESULTS 2026-11-02 (m=3, Koblitz a2=0 a6=1, 40 random targets/cell, 1 thread, timeout 120 s, 0 censored, 0 incorrect)

Mean seconds per UNSAT attempt [95% bootstrap CI]; P = exact genuine-decomposition probability; cost/rel = mean/P (UNSAT-only, SAT-mixed in parentheses where measured).

| cell | P | msolve F1 | msolve F2 (FGHR-style) | WDSat -b | lab MXL (F2) |
|---|---|---|---|---|---|
| n17_l3 | 0.00166 | 0.1032 [0.0990,0.1080] -> 62.0 s/rel | 0.0232 [0.0213,0.0252] -> 13.9 s/rel | 0.0079 [0.0065,0.0101] -> 4.7 s/rel | 0.0046 [0.0044,0.0050] -> 2.8 s/rel |
| n17_l4 | 0.01174 | 3.4152 [3.3129,3.5155] -> 290.8 s/rel (295.2 SAT-mixed) | 2.5079 [2.4011,2.6166] -> 213.6 s/rel (216.6 SAT-mixed) | 0.0113 [0.0101,0.0131] -> 1.0 s/rel (1.0 SAT-mixed) | 0.8594 [0.8181,0.9015] -> 73.2 s/rel |
| n19_l3 | 0.00042 | 0.1773 [0.1523,0.2056] -> 425.8 s/rel | 0.0314 [0.0274,0.0364] -> 75.5 s/rel | 0.0144 [0.0066,0.0285] -> 34.6 s/rel | 0.0046 [0.0044,0.0048] -> 11.0 s/rel |
| n19_l4 | 0.00155 | 3.5081 [3.3205,3.6961] -> 2256.1 s/rel (2258.1 SAT-mixed) | 3.9956 [3.7864,4.2368] -> 2569.6 s/rel (2572.1 SAT-mixed) | 0.0178 [0.0112,0.0292] -> 11.5 s/rel (11.5 SAT-mixed) | 1.2104 [1.1372,1.2872] -> 778.4 s/rel |

Lab MXL / msolve-F2 mean-time ratio (paired bootstrap CI): n17_l3 0.20 [0.18, 0.22]; n17_l4 0.34 [0.33, 0.35]; n19_l3 0.15 [0.13, 0.17]; n19_l4 0.30 [0.29, 0.32]
WDSat / msolve-F2: n17_l3 0.341; n17_l4 0.004; n19_l3 0.458; n19_l4 0.004

Headline: lab MXL is NOT slower than FGHR+msolve on any shared cell (0.15-0.34x). Stock WDSat -b is ~75x (n=17) / ~70x (n=19) faster than lab MXL at l=4; at l=3 lab MXL is 1.7-3x faster than WDSat. Any P1/P3/P5 gain must be measured against WDSat -b, not lab MXL.
Caveats: see results.json caveats (m=3 only, l<=4 only because msolve exceeds 60 s at l=5, lab MXL UNSAT-only, SAT stratum 20 targets for msolve/WDSat at l=4, one curve/seed).
Files: run_cells.py, analyze.py, results/*.json, results_cells.json, results.json. WDSat binaries in /Volumes/SSD990-2/ml-ic-20261031-data/p4/wdsat/bin (sha256 in .json beside each).
