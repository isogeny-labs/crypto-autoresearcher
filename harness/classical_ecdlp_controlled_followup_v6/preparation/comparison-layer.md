# Domain-paired correctness and cost coverage

The v6 export now derives `paired-domain-report.json` and `cost-coverage.json`
from the same terminated, sealed candidate and baseline processes. They are
analysis outputs, not extra physical arms or scientific approval records.
The checker recomputes both reports from the retained inputs and raw results;
changing a report and updating its export hashes is insufficient to pass.

The pairing report checks BSGS scalars and every distinct scalar reported as
recovered in each cell against the public equation sG = Q. It checks exact
public-target, job and six-cell membership. Repeated target replicates under
new job IDs are rejected. Production needs all eight scheduled blindings per
target; the existing disclosed fixture explicitly retains its two. Each row
reports one domain and one decoder setting, with attempt/status counts and
unique target coverage. Repeated blindings are nested within targets and
targets within domains. No pooled independence, confidence interval, asymptotic
exponent or performance ratio is inferred.

Cost coverage preserves like named instrumentation increments separately by
domain and phase, and by decoder setting where applicable. Setup, point
sampling, trace draws, original/incremental computations, decoder work, BSGS
solver work and the diagnostic verifier remain separate. The verifier can
recreate its oracle when it revisits a curve; those disjoint segments are
summed within their declared phase and their segment count is retained. BSGS
retains one solver per curve. Its repeated per-target setup fields describe a
shared baby table and are not added as fresh setup work. Missing vectors are
explicit. Reported vectors are not independently replayed primitive prices.
Storage gauges are not summed into arithmetic counters. Shared generation,
process/source custody, transport, storage and the new analysis itself still
need pricing. Qualification flags remain false and the speedup field is null.

A failed arm produces an incomplete report with unknown result counts and
vectors rather than interpreting a retained prefix as a completed denominator.
The raw partials and their seals remain attached. A complete arm with malformed
or incomplete declared data is rejected. This code does not repair or relabel
prior experiment records.

## Sources and scope

Reviewed the existing v6 candidate engine, BSGS/reference and independent host
verifier, `public_verify.py`, schedule/fixture contract, source closure and v6
scope-and-literature notes. Read SEC1 v2.0, section 2.2.1, pages 6–7,
https://www.secg.org/sec1-v2.pdf (retrieved 2026-11-09), for affine addition,
inverses, doubling and scalar-multiplication conventions. The new equations
reuse the independent public implementation. This primary-source read supports
the checking convention only; it establishes no decoder theorem or novelty
claim. The prior notes' Miller/HAC evidence gaps remain. The BSGS reference is
used for finite correctness, not asserted to be a matched attack-cost workload.

## Software controls and execution boundary

`test_compare.py` plants correct and incorrect scalars in the disclosed F11/F23
fixture, checks nesting and all six settings, and exercises missing/duplicate
membership, reused replicates, false verification flags, scalar/type/status
contradictions and disjoint diagnostic segments. `test_contracts.py` exercises
actual child processes, framed/plain report equivalence, incomplete-arm nulls,
and rejection of a forged report even after its export hashes are recomputed.
The first integration attempt exposed the diagnostic-segment assumption and is
retained with the corrected attempt. See `verification/comparison-20261109/`
for the final command receipts and raw-control archive after delivery.

This is software development using disclosed deterministic fixtures. No fresh
nonce, cohort, cloud compute job or scientific run was created. The capture
closure increases from 69 to 71 keys. Native admission must bind this new
published source and its analysis outputs; prior review and test captures do
not become evidence for these new bytes. The frozen future protocol, source
review, protected journal synchronization and live budget/placement gates
remain pending. No canonical scientific status or standing is changed.
