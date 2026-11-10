# Prospective manifest repair candidate

`run_manifest_v3.py` is software-only, unapproved for execution. The frozen
`run.py`, plan, protocol and failed run remain unchanged. The independent pilot
validation gate has not admitted a derivative input, so this source creates no
permission to launch any stage.

The candidate requires explicit experiment/hypothesis bindings and its own exact
source digest before a build. It rejects unsupported trial-wide seed, curve and
parameter claims; PFDR stage parameters remain fixed in the scientific source.
Its manifest records stage/input paths under `inputs.derived`, binds the actual
plan path/hash, retains the launch-authority commit, and quotes command arguments
with `shlex.join` (including paths with spaces).

The zero-science `test_manifest_v3.py` mocks build/census/analysis, generates each
of the four stage envelopes, and sends them through the real supervisor
`complete_manifest` and ledger run-schema checks. It also checks pre-build
refusal for absent bindings and unsupported inputs, and AST equality of all
scientific functions/constants with the frozen driver. This is a software test,
not an accepted research attempt or a check of the scientific kernel.

Run from the repository root:

```
uv run --no-project --python 3.12 --with pyyaml python experiments/EXP-PFDR-7c7c95/implementation/test_manifest_v3.py
uv run --no-project --python 3.12 --with pyyaml python tools/test_pfdr_manifest_recovery.py
```

Before any future trial, a new approved contract must vendor and bind the exact
candidate, satisfy independent input eligibility, correct all protocol instrument
hashes, and pass the full publication/ownership/resource admission workflow. No
existing trial plan should be edited to point at this file.
