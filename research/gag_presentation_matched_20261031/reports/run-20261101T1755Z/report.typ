#set page(paper: "a4", margin: 2cm)
#set text(size: 10pt)
#set heading(numbering: none)

= Run report: GAG presentation matched study, run-001

*Study* `research/gag_presentation_matched_20261031` (no ledger EXP id; protocol
`GAG-PRESENTATION-MATCHED-20261031` v1, frozen sha256 `609c701c…5ad2` at commit
`7635a467`, filed before any study data). *Lead*
`LEAD-ICE-gag-contraction-planner`. *Run* `runs/run-001`, 2026-11-01 17:55:01–17:55:57 UTC,
code commit `bfccbce5`, clean tree. *Export* `runs/run-001/export.json`
(`check-export --verify-files`: 0 findings).

== What ran

Gaudry/Diem decomposition systems at $n = m = 3$ over $FF_(p^3)$, factor base = points
with abscissa in $FF_p$, built by `descent.descent_system` and solved by msolve 0.6.5-1build2
(sha256 `c2722288…`) with `-c 0 -P 1 -t 1 -v 2`. Primes 1009, 4099, 32749; ten planted
instances per prime (`design.json` instance rule), one warmup instance (1009, 99) excluded.
Four arms per instance, order shuffled per instance: *chain* (baseline, Semaev's chained
system, 6 unknowns, degree 2), *tree* (merge tree, 6 unknowns), *monolithic* (wire contracted
over $FF_q$ to $S_4$, then descended: 3 unknowns, degree 4 per variable), *chain-aa* (chain
with a different separating-form stream: the A/A control).

Command: `PYTHONPATH=src python3 research/gag_presentation_matched_20261031/driver.py
--protocol …/protocol.json --out …/runs/run-001`, then the frozen `analyze.py`.

Host: shared 2-vCPU cloud container (Intel Xeon 2.1 GHz, kernel 6.18.44), no isolation;
load average 4.13 at start, 2.35 at end. The S3 resume-checkpoint gate failed (no upload
token in the session; `checkpoint_gate.txt`); the owner waived it for this run before launch.

== Flow

Planned 124, attempted 124, completed 124, not completed 0, interrupted 0, resumed 0, excluded 0.
Every arm: 30 measured rows + 1 warmup. One execution needed two msolve attempts
(`0035-p1009-i7-chain-aa`: first attempt reported a non-separating form); both attempts are
charged, as the protocol requires.

== Exact checks (claim C1): hold

All 30 instances: every arm returned status `ok`, ideal degree 384, and the same set of
relations verified by point addition over $FF_(p^3)$; the planted decomposition was in it on
every row. (Three instances at $p = 4099$ have two decompositions; all arms return both.)

== Counted measurements (measured; medians over 10 instances, min–max in brackets)

#table(
  columns: 5,
  [*arm*], [*F4 cells, p=1009*], [*p=4099*], [*p=32749*], [*F4 max degree / rounds*],
  [chain], [11 795 457], [11 795 457 \[11 792 928 – 11 795 457\]], [11 795 457], [8 / 20],
  [tree], [12 911 317 \[12 909 180 – 12 911 317\]], [12 911 317 \[12 848 210 – 12 911 317\]], [12 911 317], [8 / 20],
  [monolithic], [1 298 729 \[1 298 254 – 1 298 729\]], [1 298 729 \[1 298 541 – 1 299 222\]], [1 298 729], [15 / 33],
  [chain-aa], [11 795 457 \[11 790 746 – 23 590 914\]], [11 795 457 \[11 792 928 – 11 795 457\]], [11 795 457], [8 / 20],
)

F4 cells = sum over msolve's printed F4 rounds of rows × columns, summed over attempts. The
chain-aa maximum 23 590 914 at $p = 1009$ is the two-attempt execution.

== Comparisons (derived by the frozen analyze.py)

Per prime: median over instances of $log_2$(arm cells / chain cells); percentile bootstrap
interval at level $1 - 0.05 slash 6$ (20 000 resamples); exact paired sign-flip test.

#table(
  columns: 5,
  [*comparison*], [*median ratio (each prime)*], [*bootstrap interval, log2*], [*sign-flip p*], [*A/A max |log2|*],
  [monolithic / chain], [0.1101, 0.1101, 0.1101], [\[−3.183, −3.183\] at all three], [0.00195 (each)], [1.000, 0.000, 0.000],
  [tree / chain], [1.0946, 1.0946, 1.0946], [\[0.130, 0.130\] at all three], [0.00195 (each)], [1.000, 0.000, 0.000],
  [chain-aa / chain], [1.0000, 1.0000, 1.0000], [\[0, 0\]], [1.0], [—],
)

*Verdicts (protocol vocabulary).* C-mono: *supported_within_scope*: the monolithic ($S_4$)
presentation used 0.110 times the chain's F4 matrix cells (about 9.1 times fewer) at every
prime, beyond the A/A spread. C-tree: *inconclusive*: the tree used 1.095 times the chain's
cells at every prime, but at $p = 1009$ the A/A maximum $|log_2|$ is 1.0, set by the
two-attempt chain-aa execution, so the frozen rule does not pass at that prime; at the other
two primes the A/A spread is 0.

#figure(
  image("ratios.svg", width: 100%),
  caption: [Per-instance $log_2$(arm / chain) F4 matrix cells, 10 instances per prime, run-001
  (`runs/run-001/analysis.json`). The A/A point at +1.0 ($p = 1009$) is the execution charged
  with two msolve attempts.],
)

== Secondary, descriptive only (wall time, isolation none)

Median msolve subprocess time per execution: chain 0.22–0.23 s, tree 0.24–0.25 s,
monolithic 0.031–0.032 s, chain-aa 0.22–0.23 s. Not a result (protocol: wall time decides
nothing on an unisolated host).

== Scope

This describes msolve 0.6.5's F4 on these $n = m = 3$ toy instances over $FF_(p^3)$ for three
primes below $2^16$. It makes no ECDLP cost, scaling, other-solver or other-$(n, m)$ statement,
and charges no point extraction or Python system build. It is the opposite direction from
the characteristic-2 Boolean report recorded in `KN-TECH-b18366` (chaining up to 50 times
faster), in a different field, encoding and solver. $n = m = 4$ was not run (memory).

== Next step

Evidence review of run-001 (`review-evidence`), then the $n = m = 4$ chain vs tree cell on a
host with more than 8 GB, and the prime-field $m = 3, 4$ arms named in the lead.
