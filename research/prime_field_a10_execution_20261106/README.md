# Fresh progression/hash sources with kernel-free recovery

Prospective finite A10 follow-up to [A9](../prime_field_a9_json_control_20261105/RESULTS.md).
See [design](design.md), [literature](literature.md), and fixed [rules](inputs.json).
No native results exist at source publication.

The panel generates four fresh synthetic curves and 32 public target points only
AFTER admission. It collects six paired AP/hash source schedules, each 128points,
then evaluates nine prefixes, two explicit knowledge scopes and two kernel-free
solvers (432systems/864cold solver calls). All candidate rejections, miss traces,
constructor intermediate points, certificates and separate costs are retained.

Software controls (public small fixtures only):

```sh
PYTHONPATH=src:. /workspace/factor-base-venv/bin/python -m pytest -q research/prime_field_a10_execution_20261106/test_controls.py
```

The selected constructor minimizes exact group-add API calls within the actual
binary/positional-window1..8 portfolio using public scalar labels only. This is
not a weighted field-cost optimum. Nine scalar simulations are charged as policy
work; one selected EC constructor runs. Known-point cache reuse is uniform.
Explicit base and direct-target anchors enter only at their first paid prefix;
column identities never shrink. Query/checker/other-arm intermediate points do
not enter this supplied constructor cache, an operational scope rather than a
secrecy claim. Direct public target equations are separate from natural triples.

Publication and launch order is source/input commit+push, prospective protocol
freeze, frozen protocol commit+push, actual current S3 checkpoint, explicit root
release, release commit+push, real checkpoint gate, then `supervise.py` once.
The native driver refuses absent release/changed source/input/protocol bytes.
A release-specific write-once attempt marker refuses automatic retry.

```sh
# Substitute the actual full published source SHA; these are templates only.
python prepare.py protocol --source-commit FULLSHA --out protocol.json --freeze
python prepare.py release --source-commit FULLSHA --protocol protocol.json --out root-release.json --owner a10-root --authorize-root
python supervise.py --protocol protocol.json --release root-release.json --owner a10-root --out runs/FRESHID
```

Use absolute study paths from repository root and the pinned Python interpreter.
Native bounds: one existing worker/thread, 2GiB,21600CPU/wall seconds, one attempt,
no automatic retries or new paid capacity. Preserve any failure, publish raw
records before rendering its report, then append the database and metrics.
Counter coverage: new collector/solvers split Fp and Fr add/sub/mul/inv; legacy
curve-generation field_add merges subtraction and rejected-fixture arithmetic is
not fully primitive-expanded. Candidate point tests and inclusive process CPU,
RSS and diagnostic clocks remain separate; no end-to-end advantage is inferred.
