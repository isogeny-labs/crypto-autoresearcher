# Sparse functional controls strengthen the target-recovery baseline

The corrective A9 panel completed **288 fixed systems / 1,152 cold solver calls**,
with zero unknowns. All four modes matched target outcomes, scalars, full kernels
and original-row certificates. Both dense modes reproduced **all A8 Fr phase
vectors exactly**. This is a conditioned implementation control on the same four
observed curves and 32 public targets, with no new collection or independent draw.

| Clean panel: logical Fr calls, all arm phases | Dense joint | Dense cancellation | Sparse joint | Sparse cancellation |
|:--|--:|--:|--:|--:|
| Addition | 1,097,774 | 322,672 | 169,246 | 114,394 |
| Subtraction | 537,790 | 506,680 | 537,790 | 506,680 |
| Multiplication | 1,616,582 | 813,356 | 688,054 | 605,078 |
| Inversion | 5,508 | 4,428 | 5,508 | 4,428 |

Sparse evaluation builds canonical nonzero coefficient support. An exact unit
functional reads kernel coordinates directly; other supports retain Fr dot
products over support only. The same rule applies to **both** representations.
Every other algorithmic phase, reduction, certificate and public check is unchanged.
Negative/non-unit coefficients never take the unit shortcut. Full kernels are
still constructed and retained.

The observed aggregate multiplication-count difference between representations
is 803,226 in dense mode and 82,976 with sparse evaluation in both methods
(derived subtraction of the table entries). This shows why A8's dense unit-query
baseline needed the additional control. These are logical component vectors,
not calibrated time, full-S, weighted or end-to-end attack-cost improvements.

Compared with sparse joint recovery, sparse cancellation used more additions
and multiplications in **two** of 288 cases, and more subtractions in **50**.
It used fewer inversions in all 288. Every adverse case is retained. Dense
traversal is uninstrumented, not zero; sparse-only scans/visits are separately
labelled and do not measure a total CPU/memory advantage.

## Phase boundary and the next baseline

| Clean-panel Fr multiplication phase | Sparse joint | Sparse cancellation |
|:--|--:|--:|
| Elimination | 508,756 | 428,154 |
| Complete kernel | 136,564 | 57,630 |
| Identification | 10,052 | 86,612 |
| Original-row certificate verification | 32,682 | 32,682 |

After direct unit-coordinate evaluation, joint identification is cheaper in this
unit than representative identification; kernel/elimination work accounts for
the remaining aggregate difference. `CertifiedSystem.identify` already reduces
the queried vector with carried original-row weights. A zero residual proves
row-space membership without constructing a full kernel. Kernel-free recovery
in **both** methods is therefore a baseline prerequisite for the next fresh
comparison, with separate dense-oracle verification and explicit non-membership
checks. No kernel-free native experiment was executed here.

The next ranked work is a fresh curve/target, complete-cost comparison of public
arithmetic-progression source walks against **optimized fixed-base hash-source
construction**. The existing `FixedBaseMultiplier` implementation must be used
or matched, with cold table setup and the original 1..64 prerequisite optimized
as a walk. All labelled setup/intermediate/step points can reveal anchors and
must remain explicit data/diagnostics, never silently shrink U or disappear
from cost accounting. AP correlations may harm relation yield/rank; no favorable
outcome or novelty is assumed. See [next-leads.md](next-leads.md).

The standing campaign remains active: fresh holdouts and complete construction,
collection, elimination, extraction, lifting and verification accounting are
still required before claiming improvement over the strongest baseline. More
code, this control, or publication alone does not meet that objective.

## Retained failed attempt and explicit repair

The original A9 run `a9-sparse-functionals-6be915` stopped at its first case after
four producer outputs. Its direct comparison used live integer representative
keys versus string keys from archived JSON. It wrote no accepted case receipt;
287 cases were unexecuted. The failed run, source, protocol, journal and export
remain unchanged, and its benchmark is closed **invalid**.

The corrective contract canonicalizes only representative-map keys, preserving
values and every other check. A real `json.dumps`/`json.loads` regression proves
the frozen old checker fails, the corrected checker passes, and wrong values
still refuse. This was one explicit prospective corrective pass, not an automatic
retry or outcome/seed selection. The original one-attempt contract stayed exhausted.

| Cumulative observed Fr calls, including failed-prefix work | Dense joint | Dense cancellation | Sparse joint | Sparse cancellation |
|:--|--:|--:|--:|--:|
| Addition | 1,101,614 | 323,347 | 169,406 | 114,514 |
| Subtraction | 537,850 | 506,680 | 537,850 | 506,680 |
| Multiplication | 1,620,439 | 814,031 | 688,231 | 605,198 |
| Inversion | 5,511 | 4,428 | 5,511 | 4,428 |

There were **two physical attempts / 1,156 observed producer calls**: 1,152
checked new calls and four old observed/unverified outputs. The latter are charged,
not retroactively accepted. Journal accounting also charges `solver_failed` phase
prefixes if present and flags hard-killed/unrecorded work unknown. It does not
require a finalized case JSON before acknowledging observed work.

Shared projection is outside arm totals and charged once per input system. The
clean panel records Fr add/sub/mul **213,296 / 6,752 / 220,048**; the failed
prefix adds **45 / 3 / 48**, giving cumulative **213,341 / 6,755 / 220,096**.
Inclusive failed-process CPU/wall separately retains checker, IO and startup
work; no invented Fr units or inclusive-phase double counting.

**Additive prose correction:** A8 `RESULTS.md` omitted digits in its shared
projection add/mul totals. The original raw analysis and PDF correctly recorded
213,296 additions and 220,048 multiplications. The [correction receipt](corrections/a8-projection-prose.json)
preserves the earlier report and changes no measurement or solver outcome.

## Execution, checks and custody

Corrective source **d8c25fa8cf20dc94ed627e1742a57ca401dd569f**, protocol
**c07abf57a49fb5779c13f6f4e830d4fba72313ac6f39bea60e4b0eb45389cc52**,
run **a9-json-control-4e271c**. Exact publication, prospective freeze, real canonical
S3 checkpoint, explicit root release and owner lease preceded native work.
The original 2026-11-06T04:14:15.825283Z deadline was preserved; prior CPU
3.078974s and wall 3.458040659s were subtracted, remaining time recomputed at
launch, CPU soft/hard limits equal, and timeout termination has no extra scientific
grace. No new paid infrastructure was submitted.

The clean run started 2026-11-05T22:38:38.943120Z and finished 22:39:03.598267Z,
exit 0, no timeout/exception, source unchanged. Diagnostic wall 24.655149365s,
CPU user 22.914887s/system 1.340561s, peak RSS 112,435,200 B, effective watchdog
20,136s; wall_valid=false. Combined observed child CPU across both attempts is
27.334422s. These resources are not an isolated-clock performance comparison.

**78 software controls passed** in 1.51s. Controls include actual archived JSON,
wrong values, all four logical traversal counts, exact Fr add/mul delta and
unchanged other counters, valid public targets, empty/absent/non-unit/zero cases,
A/A, fault retention, stopped/hard-killed prefix accounting, original deadline/
CPU/wall bounds, 1,152 export identities and committed metrics.

Separate projection, dense affine rank/consistency, complete kernel spans,
unit-row identifiability, lifted original coefficients/RHS and independent public
multiplication check every mode. Both dense controls and all A7/A8 outcomes match.
Each mode identifies 486 slots summed over dependent systems, not 486 independent
targets. This is separate implementation checking, not staffed scientific review
or a primitive-counter audit. Configured model/provider remain unverified.
Full-ledger validation refused 114,637 sparse off-disk records; no full pass is claimed.

The [analysis](runs/a9-json-control-4e271c/analysis.json) and raw manifests were
committed/pushed as **4d736301299e25b0f582c57b7829ad5c6ec165d7** before rendering.
All eight raw gzip files and the large unified export were officially S3-stored
and remote-verified. The canonical 1,075,849-byte export is losslessly encoded
as `export.json.gz`; hydrate it and decompress to ignored `export.json`, verify
the encoding receipt, then run `check-export --verify-files` (zero findings).
The committed exporter emits 6,915 A9-corrective metric samples with explicit
failed-prefix and cumulative scopes.

The inspected [three-page report](reports/a9-json-control-4e271c-v3/report.pdf),
[primitive graph](reports/a9-json-control-4e271c-v3/primitive-counts.svg),
[budget graph](reports/a9-json-control-4e271c-v3/budget-counts.svg) and plotted data
retain measured vectors. Two presentation-build errors before a PDF existed
were corrected in the renderer; all partial build outputs were losslessly
archived with a receipt, without rerunning science. The original failed attempt
also has an inspected one-page report and an S3-backed journal.

[v12 receipt](database/v12-functional-control/generation-v12.json) proves unchanged
v11 bytes, every inherited row preserved, integrity/FKs and gzip roundtrip. It adds
the failed attempt, the completed study, 288 cases and 1,152 solver/certificate
records: historical totals **10 curves/bases and 14 physical executions**, with
zero new independent curve/target draws. PDF/database/render archive are S3-backed.
Sources and evidence gaps are recorded in design/literature and the KB-fallback
receipt. Original accepted records, frozen protocols and closed benchmarks remain
unchanged; no official scientific state or attack-cost frontier moved.
