# D3 correction review — FiatShamirZeroHash

Reviewer task: `TASK-20261102-c855e5`

Joint owned: `D3` only

Plan: `4248241742b2672e46173500e6e4dc4562bf89ca`

Plan SHA-256: `f55ab631c4d216ffcd33edd2e08cdef9962fcb220905d0acf0c3f261aa7187bf`

Original snapshot: `674b3248a8b007748a2cf4f10e5063e7de123be4`

Final producer snapshot: `db090984ca1e78e92cea5e0840885ae982f12921`

## Verdict

`D3: holds`.

For the exact finite algebraic scope in the target, machine status is
`passed`, semantic fidelity is `faithful_scoped`, and the correction outcome
is `validated_scoped`. This says only that the final correction preserves the
constant-challenge countermodel, its concrete `ZMod 5` control, and the
fixed-transcript nonzero-challenge uniqueness control. It is not a ROM/QROM,
proof-of-knowledge, implementation, or ECDLP result.

## Bound inputs and hashes

- Final source SHA-256:
  `b958dfb175dd7c0a7bcd59be48b5e3b9298a7729ff337cf3d96b76e48022bc4d`.
- Original source SHA-256:
  `899ab12153f4957bcedcbf3a7d34d67f4235d24ba464c5adaeaca1ac9cdc0ecf`.
- Final and original target-spec SHA-256:
  `212f836682b853cb679bab80583a8df748a2c25a5aa2a2b28448e6bc04944017`.
- The final source hash equals the v2 plan's bound D3 source hash. The target
  spec is byte-identical between the original and producer snapshots.

## Exact correction delta

The exact `git show` comparison of the assigned source has two changes and no
others:

1. `fun _ _ ⇒ challenge` becomes `fun _ _ ↦ challenge`. This replaces the
   implication token with Lean's lambda-mapsto token and gives the intended
   constant function. The definition's binders and return type are unchanged.
2. A namespace-local instance is added:
   `local instance : Fact (Nat.Prime 5) := ⟨by decide⟩`. It supplies the true
   primality fact needed to elaborate the concrete `ZMod 5` field/module
   operations. Ordinary `decide` produces a kernel-checked proof; this is not
   `native_decide` and introduces no axiom or public premise.

All public declaration headers, theorem proposition text, binder order, and
conclusions are unchanged. In particular, the final audited theorem still
quantifies `{Message F A}`, then `[Field F]`, `[AddCommGroup A]`,
`[Module F A]`, followed by `H`, `m`, the generator/commitment/two public keys,
and response/challenge. The local prime fact is not a new theorem binder. The
original snapshot did not supply a successful elaborated object to compare;
the defensible comparison is therefore byte-level statement preservation plus
the final named-declaration check, not a claim about an old `.olean`.

## Independent finite replay

For the concrete conjunct, take the module `ZMod 5` over itself with
`generator = 1`, `response = 3`, `commitment = 3`, and public keys `0` and
`1`. Since scalar action is multiplication,

```text
LHS = 3 • 1 = 3.
RHS(publicKey = 0) = 3 + 0 • 0 = 3.
RHS(publicKey = 1) = 3 + 0 • 1 = 3.
```

Also `0 != 1` in `ZMod 5`. Thus the same message, generator, commitment, and
response accept two distinct public keys under the constant-zero challenge,
exactly as claimed.

The generic controls also retain their stated strength:

- At challenge zero, choosing `R = s • G` makes
  `s • G = R + 0 • X` for every `X`.
- For an arbitrary known constant `c`, choosing
  `R = s • G - c • X` makes `s • G = R + c • X`.
- For one fixed transcript and nonzero challenge `c`, two accepting equations
  give `R + c • X0 = R + c • X1`; additive cancellation gives
  `c • X0 = c • X1`, and the nonzero field scalar is a unit, so `X0 = X1`.

The last item is fixed-equation uniqueness only. It does not construct two
forks, an oracle replay, an extractor, or a security reduction.

## Hypothesis-delta audit

| elaborated input or side condition | source treatment | classification |
| --- | --- | --- |
| `[Field F]` | The target says “over any field-module additive group.” | implied |
| `[AddCommGroup A]`, `[Module F A]` | These are the stated additive module model of the verification equation. | implied |
| `Fact (Nat.Prime 5)` used for the concrete field | The concrete object is `ZMod 5`; primality of 5 is discharged locally by kernel `decide`, not assumed from the caller. | implied |
| `H m commitment != 0` | Appears only in the fixed-transcript uniqueness implication and is stated by the source and target. | implied |

There is no added `scoping` or `unjustified` hypothesis. Transcript encoding,
group decoding/subgroup validation, random-oracle behavior, query bounds,
rewinding, extraction, and implementation refinement remain outside the type,
as the target and source note require.

## Trust-boundary scan

An exact-path token scan of both source revisions found zero occurrences of
`sorry`, `admit`, `axiom`, `unsafe`, `extern`, `implemented_by`, or
`native_decide`. The only decision proof added is ordinary kernel `decide` for
`Nat.Prime 5`.

## Exact hosted machine evidence

I independently inspected GitHub Actions run
[`41512636120`](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41512636120)
and job
[`125508254976`](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41512636120/job/125508254976)
with `gh`.

- Workflow `lean-verification`, event `workflow_dispatch`, completed
  `success` at exact head
  `db090984ca1e78e92cea5e0840885ae982f12921`.
- Hosted runner: `GitHub Actions 1000144301`, label `ubuntu-latest`, Azure
  `westus2`; Ubuntu `26.04.1`, runner image `ubuntu-26.04` version
  `20261025.179.1`.
- Proof runtime: Lean `4.35.0`, Lake
  `5.0.0-src+eb6cafb`; Python `3.11.17` was reported in the proof job.
- `lake build` explicitly built
  `CryptoResearch.AttackCorpus.FiatShamirZeroHash` and ended
  `Build completed successfully (9135 jobs)`.
- The all-target command was
  `python3 tools/verify_formal_targets.py --artifact-dir formal-receipts --min-verified 66`.
  Its log names the exact declaration
  `CryptoResearch.AttackCorpus.FiatShamirZeroHash.zero_hash_acceptance_and_nonzero_control`,
  records `formal-receipts/attack-fs-zero-hash.json`, reports that target as
  `verified`, and closes with `113 verified, 0 not verified, 0 infrastructure,
  0 undischarged`. Under the verifier contract in `formal/README.md`, that
  named result includes the exact theorem target and axiom audit rather than
  only a project-root build.
- Dependency-pin checks before and after the proof checks both passed with
  manifest SHA-256
  `b46170db7f5631f573ff808cf1bc53655f3bd5385aeecc717c009a42dc01cec7`.
  Every installed revision equaled its expected revision and reported clean
  sources: CryptoLean `60952c696ded7f3da4f4517006d9af6482662487`,
  mathlib `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`, plausible
  `dfa4f38190d07c37e315953e08b90fe2d95b3c24`, LeanSearchClient
  `d6b4c7be5be75ec4917c873ac50c756dc1436372`, importGraph
  `a41f0e9a4dea23188ea9cc1c41ac9f8bbafe0b93`, proofwidgets
  `df72b022e558978a1c50264cfc4d7fec86fa8e04`, aesop
  `4a174c490d8707121c4a9290800489f105d85e07`, Qq
  `dce0ad79c486cb1fb504af04f953c3466b0c6db8`, batteries
  `66e469188fe07963e5cf666c7d4433f45b8131c5`, and Cli
  `c24fe6078c630e89b489bffe59b3e20ac30d12c8`.
- The pin record explicitly says `binary_or_independent_kernel_recheck: false`:
  Git source custody was checked, while Lean/Lake binaries remain in the
  declared trust boundary.
- GitHub reports artifact `formal-verification-receipts`, id `13175228889`,
  size `1,523,974` bytes, unexpired, attached to the exact head above, with
  server digest
  `sha256:4df8ae98f7487ba386bb4bcebd6ab0ade17cefeaabe2b4212919513f29a740c3`.
  The job log records 115 uploaded files, the same digest, successful
  finalization, and the artifact id.

## Procedure deviation

The environment's network proxy refused the artifact's Azure Blob redirect:
both `gh api .../artifacts/13175228889/zip` and `gh run download` ended with
`CONNECT tunnel failed, response 403`; bypassing the proxy could not connect.
Consequently I did not independently open or recompute the downloaded zip or
the receipt JSON bytes. I did independently inspect the GitHub artifact
metadata/digest, successful upload-finalization log, exact named verifier log,
and clean pre/post pin records. This bounded artifact-byte access limitation is
recorded rather than silently treating a failed download as a source or proof
failure. No local formal build or scientific run was performed, as required by
the handoff.

## Scoped conclusion

The two-line correction resolves syntax/instance elaboration without changing
the public propositions, concrete arithmetic, or stated trust boundary. The
final exact hosted run passes the full workspace and named target verifier on
the producer snapshot. Joint `D3` therefore holds, solely for the finite
constant-challenge and fixed-equation claims enumerated above.
