# PROTOCOL: F4 trace compile-and-replay (track P5)

Frozen and committed 2026-10-31 (relaunch) before any replay measurement. Source: LAUNCH.md ("replay <= 0.5x fresh with >= 95% success"), REVIEW.md P5.
Disclosure: first-launch pilots exist (one fresh MutantXL run on a 16,384-column cell: 657.8 s wall, 4.7e10 ops, certified False; one trivial 17-item pilot). They are pilot data and not counted in the test.
Moderate priority; honest baseline is Joux-Vitse F4Remake style trace reuse (not ML). Learned row/pair selection only if replay itself wins.

## Question
All PDP instances for a fixed (curve, V, m) share one monomial structure and differ only in coefficients. Compile the elimination trace on one instance, replay it on others: is replay cost <= 0.5x a fresh solve with >= 95% success?

## Method
Per cell choose cells where fresh MutantXL finishes in <= 60 s (the 657 s cell is too expensive for a paired test). Compile on instance 1, replay on >= 50 other instances of the same cell, compare with fresh solves of the same instances, same machine. Success = replay yields the same certified solution set as fresh. Failure of a trace (pivot becomes zero) counts as a failure, not a retry.

## Decision rule
Win = median replay/fresh ratio <= 0.5 (bootstrap upper bound <= 0.6) AND success rate >= 95%, on at least 2 cells. Otherwise closure for this cell family; do not move to learned schedules.

## Amendment 1 (2026-10-31, before any replay measurement; frozen text above unchanged)

Certification of the 657.8 s pilot. The pilots (pilot2.py, pilot2b.py) called fresh(..., S=-1, d_need=0), which by construction never requests a certificate, so the `certified: False` field was an artefact of the call, not a failed proof. Evidence from its own log: cell N = 15 (l = 5, m = 3), rank_le[7] = 16384 = sum_{k<=7} C(15,k) = number of columns at D = 7, and S = 0 from independent brute-force enumeration (enum_s4), so codim = cols - rank = 0 = S at stage 7 >= d_need = 0. This is the UNSAT certificate (1 is in the row space). The pilot is therefore certified post hoc from the log (no rerun). Certification rule for all test rows: codim == S (S from the independent enumeration) at a stage >= d_need, as in certificate_params; certification must also pass when called with the real (S, d_need), checked on a 0.1 s pilot before the grid.
Cells: l = 5 (657 s) is excluded by the frozen <= 60 s rule. Candidate cells use l = 4 (N = 12): (koblitz, n = 17, STD) and (ordinary, n = 17, GPD); admission = median fresh wall <= 60 s on 3 probe UNSAT targets; if a cell is inadmissible, drop it to l = 3 and record it. If fewer than 2 cells are admissible the decision is `not_run`. Targets: 30 UNSAT (natural stream; the compile target is the first UNSAT draw) as the primary arm; 30 planted-SAT as the secondary arm (reported, not decisive). Disclosure: the replay/fresh ratio uses operation counts (ops) as primary and wall as secondary, same machine; under load > 40 wall is unreliable and only ops decide the verdict. Primary ratio per target = replay ops / fresh ops; bootstrap over targets, 10,000 resamples.
