# Targeted Lean verification record

Date: 2026-10-31

This record distinguishes checks of the new module from the repository-wide
verification receipt. It is not a substitute for the latter.

## Pinned environment

- Lean: `v4.35.0-rc1`
- Mathlib: `7fa22735254ddf7e11f119250a9f2d0352bc7c3a`
- Theorem source SHA-256:
  `97b8284498168c22d848bf3368b34e99c76db86c88d2072817c59e5926019d92`
- Generic target SHA-256:
  `b9a9bf971c11ce3b02371e4ae7e46ec1954bdd08d7c5d2716caf88870cbf1b63`
- Horizontal target SHA-256:
  `cc56db52b05517c1169d4ca62be56b1f02e5d1a522f7c77794fe7488be3da0fd`
- Theory-note SHA-256:
  `2ea525e0726afe8ae5235b5d158ad21339167bd2cf15e135f97d3efbaa863a3b`

## Passing checks

```text
python3 tools/formal_task.py \
  formal/targets/k163-coprime-recovery-transfer-20261031.yaml \
  --validate-only
OK ... k163_transfer_preserves_scalar_relations

python3 tools/formal_task.py \
  formal/targets/k163-horizontal-recovery-control-20261031.yaml \
  --validate-only
OK ... k163_horizontal_control_preserves_scalar_relations

lake build +CryptoResearch.Isogeny.CoprimeTransfer
Build completed successfully (1259 jobs).
```

The repository verifier's exact requested-theorem axiom check was replayed for
both named declarations. Each exists as a theorem and reports only the allowed
Mathlib axioms:

```text
target axiom audit passed:
  CryptoResearch.Isogeny.CoprimeTransfer.k163_transfer_preserves_scalar_relations
axioms=[propext, Classical.choice, Quot.sound]

target axiom audit passed:
  CryptoResearch.Isogeny.CoprimeTransfer.k163_horizontal_control_preserves_scalar_relations
axioms=[propext, Classical.choice, Quot.sound]
```

The formal harness tests pass after materializing every target's source file,
matching the CI sparse-checkout protocol:

```text
333 passed, 12 skipped
```

No `sorry`, `admit`, custom `axiom`, or `unsafe` construct occurs in the new
Lean source.

## Repository-wide receipt attempt

The immutable
[`verification-attempt-oom.json`](verification-attempt-oom.json) records the
full verifier invocation. It stopped before the project axiom audit because
the pre-existing
`CryptoResearch.Semaev.BooleanParityDegreeThreeRankCertificate` process was
killed for memory exhaustion (`Lean exited with code 137`). The new K-163
module had already built separately; the failed receipt therefore records an
infrastructure limitation and makes no mathematical conclusion. A one-thread
retry of that same unrelated module also exceeded the 17 GiB local
environment.

Independent semantic-fidelity review and a passing repository-wide receipt
remain pending. No weak-curve or cryptanalytic-breakthrough label follows from
the targeted checks.
