# Full-workspace verification exceeds resources in an existing rank proof

Raised2026-11-05. Status: open operational obstruction; not a mathematical
counterexample or an impossibility claim. It blocks a passing FULL workspace
verification receipt, not the exact new source proofs or scoped checks.

After repairing the pinned Mathlib cache, the standard whole-workspace
verifier failed in the unchanged 80-row
CryptoResearch.Semaev.BooleanParityDegreeThreeRankCertificate module. Its
Lean process exited137 after398s. The workspace memory limit was
17179869184bytes and cgroup memory.events showed oom1/oom_kill1. No new
formal-module error was in the build output. The first standard attempt had
already timed out900s while compiling the previously uncached dependencies.

Receipts and raw evidence: ../validation/{boolean-normalization-repair-
20261105-receipt.json,boolean-normalization-repair-20261105-cached-receipt.json,
workspace-resource-failure.json}. The verifier's second receipt calls the
result formalization_blocked because lake build failed; this record preserves
the distinct observed OOM signal. The original files/receipts are unchanged.

Exit: rerun the unchanged complete workspace successfully under declared
resources, or preserve the same theorem statements while separately reviewing
a resource-bounded decomposition of the existing finite rank certificate.
Do not replace kernel proof with unchecked rank data, remove the frozen
module, lower the verification floor or call a scoped check a full pass.

Next useful step: isolate that existing module and inspect its large `decide`
steps for row/column proof decomposition before any new full rerun. Repeating
the same full build with unchanged16GiB memory provides no new evidence.
No paid infrastructure, cloud run or permission request is scheduled here.

## Later CI scope update

Full-workspace GitHub run41996349062 succeeded for proof head69b20afa on
synthetic merge0cfa6988. Its five matching LFD receipts are retained in the
publication-readiness packet. This clears the absence of a passing complete-
workspace result for that proof snapshot. The16GiB local replay obstruction
and all original failed receipts remain as recorded. Later delivery revisions
still require their own CI.
