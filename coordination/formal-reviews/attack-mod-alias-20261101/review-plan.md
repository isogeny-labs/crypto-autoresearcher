# ATTACK-MOD-ALIAS-BOUNDED-REPAIR review plan

Producer input: crypto-autoresearcher PR #2942, head `7c7d879bdaf660c47a0bc519056545e7749d3d1d`; target `formal/targets/attack-mod-alias.yaml`, source `research/cryptographic_assumption_attack_corpus_20261101/README.md`, theorem `CryptoResearch.AttackCorpus.ModAlias.modulus_alias_and_bounded_repair`.

Prior: The arithmetic alias and canonical-range injectivity look mathematically standard. The proof source has not yet passed pinned Lean CI. The source claim is explicitly limited to natural casts in `ZMod q`; any inference about a concrete circuit is outside scope.

Joint owners and worked attacks:

1. Source reviewer: Check target/source-to-elaborated-type fidelity, both halves, `2 ≤ q`, all quantified x,y and strict bounds, and check that proof uses no holes or custom axioms. Attack by removing the bound and testing the pair x=0,y=q. Review official Mathlib lemma dependencies and any mismatched casts.
2. Blind reviewer: Receive only the mathematical target (not producer proof or report). Re-derive alias and injectivity including q=2 and composite q; produce a nearby false case and identify all model and implementation bridges. Do not read producer code, source report, or other reviewer output.

Known-false controls: Unbounded injectivity fails at x=0,y=q for q≥2. q=0 makes the canonical interval empty and is excluded by the stated premise. A claim that a named circuit omits range checks does not follow from a `ZMod` equality.

Machine gate: inspect exact PR-head `formal workspace (lake build + axiom audit)` and complete-source coverage; require its success plus named declaration and allowed transitive axioms before `machine_status=passed`. No local build on the shared host while another memory-heavy job is active. Treat unavailable or failed CI accurately.

Synthesis rule: Do not mark validated until machine status passes and both independent reports support faithful scope. Leave `source_status: STATED` and all protocol-security claims unchanged.

## Head amendment, 2026-11-01 23:38 UTC

The source reviewer identified a missing pinned Mathlib import at producer head `7c7d879bdaf660c47a0bc519056545e7749d3d1d`. The producer removed that import and replaced `omega` with core `Nat` facts. Current PR head is `288d5612b599501119f6c0d130a56241b7e2c9b4`; all machine and source-review verdicts must bind this revision. The original prior and attacks above are retained.
