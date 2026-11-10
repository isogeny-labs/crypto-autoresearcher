# Prospective raw-coordinate review preflight

At `3f7e3e4d0d049256e0ae23571553e806aab230ab`, the pinned static inventory script from `docs/reports/2026-11-08-formal-target-inventory/audit.py` passed `--require-clean`: 126 formal target specs, no duplicate claim or theorem identities, 47 declared sources, 83 theorem files, and zero direct run-artifact sources. Compared with its 125-target November 8 inventory, the only added target is `semaev-raw-coordinate-certificate.yaml`; the 125 earlier target, source, and theorem SHA-256 values are unchanged. The inventory is structural only and neither runs Lean nor judges semantic fidelity.

The new target is therefore selected for a separate three-joint technical review. Its typed raw-coordinate iff and the source's serialized-certificate interpretation receive separate judgments. The existing hosted Lean run 42666660822 is the machine-evidence candidate; reviewers must authenticate its actual artifact before using it. No duplicate Lean or cloud job is authorized by this plan.

The plan and isolated blind card were committed and pushed before reviewer dispatch. The blind reviewer receives only the card and cannot read this preflight, the plan, source, theorem, target, receipts, or sibling reports.
