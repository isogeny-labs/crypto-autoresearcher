# A10 proof-status correction

The full panel is an unverified producer measurement assertion under the PCC
contract. Claim `PCC-20261106-028bb6` pins the raw analysis bytes, but the local
PCC result is `not_covered`: independent signed replay and recomputation are
absent. Its standing is `unverified`. Existing producer fields such as
`verified:true` and phrases about checks describe local software output only;
they are not signed PCC standing or execution verification. [pcc:unverified]

Claim `PCC-20261106-6f9635` carries the existing public toy scalar certificate:
Q=(7855,3278)=[7274]P on the specified order8233curve over F8191. The standard PCC
arithmetic checker returns a local pass. Standing remains `unverified` until a
trusted signature exists. This certificate covers only that scalar equation;
it establishes no source budget, rank6/14, measured cost, search distribution,
novelty or whole-solver advantage. [pcc:unverified]

This correction was filed after initial PR publication when pcc-gate flagged
an unqualified storage-check word in the PR body. It does not claim the records
were filed earlier. The PR wording is now explicit about producer reports and
proof coverage. Original frozen protocol, raw outputs, closed benchmark and
rendered PDF bytes remain unchanged. No scientific rerun, fabricated replay,
trusted signature, new native attempt or official scientific transition occurs.

The original report and benchmark should be read with this companion. Exact
registration and local coverage outputs are in validation/pcc-claim-registration.txt
and validation/pcc-local-coverage.json. The measurement and solve claim JSON
records live under pcc/claims, with append-only entries in pcc/ledger.jsonl.
