# Frozen formal target machine-receipt inventory

## Current target snapshot (2026-11-07)

At `main` commit `23c5aeca09f8f512d90755193660c1b2aa509714`, the strict
inventory rebuild found **122** tracked `formal/targets/*.yaml` targets, **122**
present named Lean sources, and **122** matching named `machine_verified`
receipts, with no unmatched claim IDs. The full [122-row inventory](matched-receipts-23c5aeca.json)
records each frozen target and source hash, theorem name, receipt file and hash,
and source run ID. Its SHA-256 is
`1ab57bda23d6f1c764e16c443d552aa2db4439ac35f77f79be4a170ca45a4756`.

The receipts come from successful hosted [Lean verification run 42260198392](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/42260198392)
at `ba7a85965dab6eef75e24395cca9edb80b53d6cc`. Its formal workspace and
kernel-controls jobs passed; its before/after dependency-pin files match at
SHA-256 `2ae448d9f1491f633cd748b1b9a7cfdf1b038f647194dd2213dfc39b13c0187a`.
The `formal/` Git tree at that run commit and at this inventory commit is the
same object, `2d19c92d105492046124a4149d0e683536046a95`. The rebuild
also compares each named source and target byte hash with the corresponding
receipt, so this conclusion is limited to the named formal inputs and the
recorded run. It does not assert that later workflow or verifier code outside
`formal/` is identical.

To reproduce from a checkout containing the pinned `main` commit:

```sh
gh run download 42260198392 -R isogeny-labs/crypto-autoresearcher \
  -n formal-verification-receipts -D /tmp/formal-receipts-42260198392
python3 docs/reports/formal-target-inventory-20261102/rebuild.py \
  --revision 23c5aeca09f8f512d90755193660c1b2aa509714 \
  --receipts 42260198392:/tmp/formal-receipts-42260198392 \
  --output /tmp/matched-receipts-23c5aeca.json --require-complete
sha256sum /tmp/matched-receipts-23c5aeca.json
```

This is receipt coverage and byte identity, not a fresh Lean build at the
inventory commit or an independent authentication of the run. It does not
review semantic correspondence to the research claims, implementation
behavior, experiment measurements, or performance dashboards. Those require
separate claim-level review and measurement evidence.

## Earlier snapshot (2026-11-02)

At crypto-autoresearcher `main` commit `685914319621828a458a19c1ce8693ca0174f7f5`, all **108** tracked `formal/targets/*.yaml` targets name source files present in that Git tree. Every target's exact YAML bytes and named Lean source bytes match one `machine_verified` receipt from the successful combined-tree hosted Lean run below. The full [108-row inventory](matched-receipts-68591431.json) records the source hash, target hash, matched receipt file, run ID, and receipt hash for each claim.

| Hosted run | What it contributes | Pin comparison |
| --- | --- | --- |
| [41494797344](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41494797344) | One completed full-workspace run with 108 named `machine_verified` receipts at merged proof commit `d0b766449942b04bf3316d005624b3ce83f0c5f4` | pre/post files byte-identical, SHA-256 `4745b2be5cedbf0024a23350a9f0ff8365b283462e0bd00c8abb8e3c51881d1b` |

The comparison requires matching `task_id`, workspace, `theorem_name`, and `theorem_file` across the target, task and verification sections. It checks the frozen target hash and Lean source hash against receipt provenance, including the named workspace input; successful build and axiom-audit flags; no forbidden constructs or infrastructure failure; and a nonempty audit log. It also rejects a run whose pre/post dependency-pin files differ. The inventory is pinned to this one Git commit; later `main` commits require a new snapshot or an explicit tree-diff showing no relevant source changes.

## Rebuild

From a checkout containing commit `685914319621828a458a19c1ce8693ca0174f7f5`, with PyYAML and authenticated `gh` access:

```sh
gh run download 41494797344 -R isogeny-labs/crypto-autoresearcher -n formal-verification-receipts -D /tmp/formal-combined-receipts
python3 docs/reports/formal-target-inventory-20261102/rebuild.py \
  --revision 685914319621828a458a19c1ce8693ca0174f7f5 \
  --receipts 41494797344:/tmp/formal-combined-receipts \
  --output /tmp/matched-receipts-68591431.json --require-complete
sha256sum /tmp/matched-receipts-68591431.json
```

Expected inventory SHA-256: `c9cbee7535a035c4b5bbbc414e2afd5327ef18ad1a881978cc4046fdf613e91e`.

The local positive run returned 108 targets, 108 named sources, 108 targets with matching named receipts from this one run, and no unmatched claims. Earlier negative controls on the same checker used a scratch copy of run 41365419446's artifact: replacing the polynomial-alias theorem hash with zeros made the strict command exit 1 and identify `ATTACK-POLYNOMIAL-FUNCTION-ALIAS` as unmatched (107/108). Altering the copied post-run pin file made it exit 2 with `dependency pins changed during run 41365419446`. The downloaded originals were not modified.

## Evidence boundary and next checks

This is a byte-identity and receipt-coverage audit of one successful combined-tree full-workspace run. It does **not** run Lean afresh at the later pinned `main` commit, authenticate the artifact service or installed Lean/Lake binaries independently, or compare the other 103 theorem types to their scientific source claims. The five attack-corpus claims have a separate source and adversarial review in [their technical packet](../2026-11-01-attack-corpus-five-lean/README.md), including its stated procedural deviations. The later Nagao target has a matching named machine receipt here; this inventory does not assess its semantic fidelity.

The run's source commit is `d0b766449942b04bf3316d005624b3ce83f0c5f4`; the later pinned `main` tree is covered by per-target source and target byte matches, not by another full-workspace build. Experiments, implementation behavior, performance dashboards, and the `crypto` and `cryptanalysis` repositories are outside this inventory and retain their own validation work.
