# A11: paid affine-target coverage with general outside columns

Implementation in progress; **no native A11 curves, targets or experiment have
been generated**. No frozen protocol, root release or launch interface exists
yet. [Design](design.md) and [literature](literature.md) are prospective notes.
The A10 source collector and kernel-free arithmetic are reused as code, with
new rules to be frozen before fresh generation; the closed A10 trial is not rerun.

The new solver supports raw general outside vectors, including non-unit target
coefficients and cross-target point coincidences. Outside elimination retains
sparse original-row certificates, constructs base-only rows, reduces each target
unit through the outside span, then tests the resulting base functional without
building a full kernel. The joint method keeps raw coefficients. Both lift to
and check the original joint row system.

Target policies are consecutive Q+jP, independently hashed Q+alphaP, and general
alphaP+betaQ with nonzero beta. Cold target constructors use only their own source
schedule/prefix's paid cache, with one P table shared by eight targets within a
branch and separate symbolic Q-coefficient caches. Cached scalar sums avoid EC
addition; metadata and lookups are still charged. A physical query cache retains
all aliases while cold-prefix views reference deterministic query counts rather
than inventing executions or clocks. Base matches, identity, public and
cross-target coincidences remain explicit paid equations.

Current tiny software controls cover general-U positive/negative/corrupt cases,
JSON roundtrips, independent dense rank and certificates, all nine cache-aware
constructor policies, affine labels/offsets/identities/cross-target equalities,
query misses, prefix availability and failed construction prefixes. These are
producer software checks, not signed PCC standing. [pcc:unverified]

```sh
PYTHONPATH=src:. /workspace/factor-base-venv/bin/python -m pytest -q research/prime_field_a11_execution_20261106/test_solver.py research/prime_field_a11_execution_20261106/test_construct.py research/prime_field_a11_execution_20261106/test_collection.py
```

Planned fixed panel: four fresh curves,32public targets,six source schedules,
source prefixes64/128,two knowledge scopes,three target policies,target budgets
1/2/4/8,two solvers:1152dependent systems/2304solver calls.704formal endpoint
expressions bound unique physical target points; coordinate aliases may reduce
actual queries. One existing worker/thread,2GiB,21600CPU/wall seconds,oneattempt,
no automatic retry or new paid capacity. Exact source/rules publication, protocol
freeze, real S3 custody, explicit release and normal admission precede any native
math. The general production aP+bQ implementation is a baseline, not a novelty
claim, and no whole-solver improvement is asserted. [pcc:unverified]
