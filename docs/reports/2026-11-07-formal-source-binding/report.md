# Formal receipt binding to declared research sources

The direct formal verifier now includes the target's declared research source
file in its input checks. A receipt records that file's SHA-256, refuses a
missing, absolute, escaping, or symlinked source path, detects source changes
while Lean runs, and fails readback when the source bytes no longer match.
This closes a concrete source-content gap for future formal verification
receipts. It does not decide whether a theorem faithfully states a claim or
authenticate a historical experiment.

## Current-main inventory that exposed the gap

At base commit `598f4c6a4fb7fa405ad3a0800fc7456170f0a380`, the repository's
exact-tree `formal_pointer_inventory.py` found 123 formal targets and 2,903
experiment directories. Eleven experiment IDs have an exact lexical pointer
from a target; 2,892 do not. The separate
`formal_target_source_inventory.py` found 46 distinct declared source files,
8 targets with a direct experiment path, no targets with a direct run path,
and 12 distinct experiment IDs mentioned literally in those sources. These
are **path and lexical inventory counts only**. They neither prove coverage
nor show that the other experiments lack a relevant theorem.
The exact-tree outputs are preserved as
[experiment pointers](formal-pointer-inventory.json) and
[target/source links](target-source-inventory.json); both name their inspected
commit and record their limited method.

The prior `cmd_verify` receipt hashed the target spec, theorem file,
toolchain, manifest, and files inside the Lean workspace. A target could
declare a research source outside `formal/`, but its content was not among
the receipt's input hashes. `receipt_errors` likewise did not compare it.

## Verification

`PYTHONPATH=/var/tmp/binstd-pylibs:. ELAN_HOME=/var/tmp/binstd-elan
python3.11 -m pytest -q tests/test_lean_live.py` passed **14/14** with the
pinned Lean 4.22.0 smoke workspace; the exact output is in
[test-lean-live.log](test-lean-live.log). The controls cover a valid source
outside the Lean workspace, a source mutation after receipt creation, a
mutation during the real Lean verification, a removed digest, missing and
escaping source paths, and a symlink. Existing theorem, axiom, and imported
helper controls in the same test file also passed.

The verifier does not grant old receipts a new source binding: a receipt
without `declared_source_sha256` fails the current readback check and needs
fresh verification under the new verifier. This is an evidence-status change,
not a claim that an archived theorem was mathematically false. A newly
created receipt still requires independent semantic review, and its source
hash binds bytes observed during that run rather than proving that those
bytes were committed to Git or that the experiment actually ran.

No experiment, cloud job, Lean theorem statement, measured value, or
performance dashboard changed in this patch. The next validation step is to
run the current-head hosted formal gate and inspect any compatibility failures
on the PR before merge.
