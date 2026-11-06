# A13: paid public-log factor-base control

Implementation and prospective preparation. No native A13 panel has run.

Compare a source-free, independently hash-labelled known-log base with the
unchanged norm-base collector on four fresh coefficient curves and eight
public targets per curve. Both bases have 32 atoms and their own paid index,
pair table and caches. The known arm pays construction, signs, supplied unit
equations, direct substitution, arbitrary-target elimination, certificate
lifting and public checks. Known logs are supplied information, not learned
relations; ranks and Delta are not compared across different point sets.

The norm arm retains AP/hash seeds 0/1/2, source horizon 128, relations/anchors,
and target walk/hash-offset/general budgets 1/2/4/8. The known control runs
once per curve/policy/budget and is reused explicitly in cold comparisons.
Its P cache comes from its own paid base construction, with no source work.
Sparse joint and a base-aware control execute on every system: outside-first
for norm, direct known-label substitution for known. There are 624 dependent
systems and 1248 actual solver calls; these are not independent target draws.

See [design](design.md), [sources](literature.md), [input rules](inputs.json)
and the retained [software-control output](validation/software-controls-20261106T2056Z.txt).
Only tiny p<=211 controls have run, with admission explicitly mocked for the
stream/export software test. Native release, prospective source binding,
current S3 custody and the normal gate remain required.

```sh
/workspace/factor-base-venv/bin/python -m pytest \
  research/prime_field_a13_execution_20261106/test_known.py \
  research/prime_field_a13_execution_20261106/test_admin13.py -q
```

After the complete source/input commit is pushed, prepare and freeze once:

```sh
/workspace/factor-base-venv/bin/python research/prime_field_a13_execution_20261106/prepare.py protocol \
  --source-commit <published-source-SHA> \
  --out research/prime_field_a13_execution_20261106/protocol.json --freeze
```

Publish that protocol and current canonical checkpoint before issuing an
explicit root release. The supervisor enforces one attempt, one existing
worker/thread, 2 GiB and a fresh deadline within 21600 CPU/wall seconds.
No automatic retry or new paid capacity. Publish every raw outcome before
rendering reports, then append the database/export/benchmark record and PR.

Cost vectors retain incomplete generation/hash/pow/checker/Python/NumPy
internal/OS/IO accounting and unisolated clock limits. Local controls and
storage receipts do not grant trusted signed scientific standing.
