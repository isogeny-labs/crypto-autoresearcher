# Frozen formal target machine-receipt inventory

At crypto-autoresearcher `main` commit `685914319621828a458a19c1ce8693ca0174f7f5`, all **108** tracked `formal/targets/*.yaml` targets name source files present in that Git tree. Every target's exact YAML bytes and named Lean source bytes match at least one `machine_verified` receipt from the two successful hosted Lean runs below. The full [108-row inventory](matched-receipts-68591431.json) records the source hash, target hash, matched receipt file, run ID, and receipt hash for each claim.

| Hosted run | What it contributes | Pin comparison |
| --- | --- | --- |
| [41365419446](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41365419446) | 107 named receipts, including the five merged attack-corpus proof sources and their frozen targets | pre/post files byte-identical, SHA-256 `006ffd7bb3c7c5711049386a53eadcc38701d03007ec74ab427ce51b10ca235d` |
| [41488317240](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41488317240) | the later Nagao exact-degree target, plus matching receipts for existing sources | pre/post files byte-identical, SHA-256 `fb62d1952a368023bbf13dfb42f245d69e500693e11e5f631ed8a8a648e4caa7` |

The comparison requires matching `task_id`, workspace, `theorem_name`, and `theorem_file` across the target, task and verification sections. It checks the frozen target hash and Lean source hash against receipt provenance, including the named workspace input; successful build and axiom-audit flags; no forbidden constructs or infrastructure failure; and a nonempty audit log. It also rejects a run whose pre/post dependency-pin files differ. The inventory is pinned to this one Git commit; later `main` commits require a new snapshot or an explicit tree-diff showing no relevant source changes.

## Rebuild

From a checkout containing commit `685914319621828a458a19c1ce8693ca0174f7f5`, with PyYAML and authenticated `gh` access:

```sh
gh run download 41365419446 -R isogeny-labs/crypto-autoresearcher -n formal-verification-receipts -D /tmp/formal-five-receipts
gh run download 41488317240 -R isogeny-labs/crypto-autoresearcher -n formal-verification-receipts -D /tmp/formal-nagao-receipts
python3 docs/reports/formal-target-inventory-20261102/rebuild.py \
  --revision 685914319621828a458a19c1ce8693ca0174f7f5 \
  --receipts 41365419446:/tmp/formal-five-receipts \
  --receipts 41488317240:/tmp/formal-nagao-receipts \
  --output /tmp/matched-receipts-68591431.json --require-complete
sha256sum /tmp/matched-receipts-68591431.json
```

Expected inventory SHA-256: `25ad8057f4fda53b299ca78ed6ec2b636031ca43b04f89d284c94a86966f70fe`.

The local positive run returned 108 targets, 108 named sources, 108 targets with matching named receipts, and no unmatched claims. In a scratch copy of run 41365419446's artifact, replacing the polynomial-alias theorem hash with zeros made the strict command exit 1 and identify `ATTACK-POLYNOMIAL-FUNCTION-ALIAS` as unmatched (107/108). Altering the copied post-run pin file made it exit 2 with `dependency pins changed during run 41365419446`. The downloaded originals were not modified.

## Evidence boundary and next checks

This is a byte-identity and receipt-coverage audit. It does **not** run Lean afresh, authenticate the artifact service or installed Lean/Lake binaries independently, establish a single full-workspace build at this exact `main` commit, or compare the other 103 theorem types to their scientific source claims. The five attack-corpus claims have a separate source and adversarial review in [their technical packet](../2026-11-01-attack-corpus-five-lean/README.md), including its stated procedural deviations. The later Nagao target has a matching named machine receipt here; this inventory does not assess its semantic fidelity.

The #2968 combined-tree [Lean run 41494797344](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41494797344) was still building when this snapshot was prepared. Its final result must be checked separately before claiming a combined-tree workspace pass. Experiments, implementation behavior, performance dashboards, and the `crypto` and `cryptanalysis` repositories are outside this inventory and retain their own validation work.
