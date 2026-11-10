# Comparison software controls, 2026-11-09

Tested source: `9a5b7714b1fa2fe95ec5ead8a9b5a2bd13124f50`.
The final commands returned zero after actual waits: 12 reporting tests,
10 existing v6 tests and 14 process/control tests (36 total).
All 71 captured source keys matched before/after and matched the delivered
source. The framed fixture preserves all seven logical outputs and the derived
pairing/counter reports. The checker rejects a falsified derived summary even
when its export hashes are recomputed. Failed arms retain null result totals.

`software-checks.json` retains the actual command receipts, initial failure and
correction, artifact digest and full-GET proof. `software-controls.tar.gz` is
managed by the native artifact store; its manifest and ignore rule live here.
It contains both integration attempts, all six command captures and the SEC1
primary source retrieved for the task. Use the repository artifact tool to
hydrate the archive with an authorized profile and a writable cache.

The initial integration attempt failed because the new report incorrectly
assumed one diagnostic vector per curve; the original verifier revisits curves
with disjoint oracle counter segments. The corrected report preserves and
combines those segments within their declared phase. BSGS retains a single
solver vector per domain. The failure and its raw controls are preserved.

These are disclosed software controls, not sampled-cohort results, a fresh
scientific run, independent review or performance qualification. No fresh
nonce, curve or cloud compute job was created. The mathematical kernels and
historical records remain unchanged. Native execution readiness is still false.
