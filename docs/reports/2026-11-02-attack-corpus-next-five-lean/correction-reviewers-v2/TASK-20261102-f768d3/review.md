# E3 correction review: Pedersen relation kernel

## Verdict

`holds` for joint E3 at producer snapshot
`db090984ca1e78e92cea5e0840885ae982f12921`.

The correction preserves the frozen algebraic claim and its public declaration
types.  It supplies a proved prime instance for the concrete field, makes the
two commitment-map pairs explicitly `ZMod 5 × ZMod 5`, and closes the reduced
finite proposition with ordinary kernel `decide`.  It does not use
`native_decide` or another forbidden trust escape.

Formal-review dimensions:

| dimension | verdict |
| --- | --- |
| machine status | `passed` |
| semantic fidelity | `faithful_scoped` |
| review outcome | `validated_scoped` for E3 only |

## Bound inputs

- Review plan: commit `4248241742b2672e46173500e6e4dc4562bf89ca`,
  SHA-256 `f55ab631c4d216ffcd33edd2e08cdef9962fcb220905d0acf0c3f261aa7187bf`.
- Original snapshot: `674b3248a8b007748a2cf4f10e5063e7de123be4`.
- Producer snapshot: `db090984ca1e78e92cea5e0840885ae982f12921`.
- Frozen target SHA-256 at both snapshots:
  `73f3d6e4cf64f14906a113176614dcbad26431cd08d5598a70644b8f9797538d`.
- Original Lean source SHA-256:
  `1b491e1005822c1dca4b38e15c98d427a14c6572c0e12c121235d1ed08c1d6da`.
- Producer Lean source SHA-256:
  `7b1cd73987824b69c5024b37ae9367e86b76346795375bf61f814e4031678b13`.

The local plan, target, and source bytes match those bound revisions and
hashes.

## Exact correction audit

An exact `git show` comparison of the assigned source and spec found no spec
delta and only these source changes:

1. `local instance : Fact (Nat.Prime 5) := ⟨by decide⟩` was added.
   This is a locally proved fact, not a new theorem hypothesis.  The proof of
   primality is evaluated by Lean's kernel.
2. Both arguments to `commitmentMap G H` in the concrete equality were
   explicitly annotated as `ZMod 5 × ZMod 5`.  These annotations select the
   same pair type already determined by `G` and `H`; they change neither the
   proposition nor a public declaration type.
3. The proof of `concrete_zmod_five_control` changed from
   `norm_num [...]` to `norm_num [...] <;> decide`.  `norm_num` performs the
   concrete arithmetic reduction and ordinary `decide` discharges the
   remaining decidable proposition with a kernel-checkable proof term.

No binder, quantifier, hypothesis, conclusion, definition name, theorem name,
or public declaration type changed.  In particular,
`known_relation_kernel_and_alternate_openings` still requires nonzero
`alpha`, `H = alpha • G`, and injectivity of `a ↦ a • G`, and still returns
the nonzero relation, full kernel equation, arbitrary-message equivocation,
collision recovery, and concrete finite control.

## Mathematical replay

For `G = 1`, `H = 2`, and `alpha = 2` in `ZMod 5`:

- `alpha ≠ 0` and `H = alpha • G`;
- `(0, 0) ≠ (2, 4)` because their first coordinates differ;
- `Com(0,0) = 0`;
- `Com(2,4) = 2·1 + 4·2 = 10 = 0 (mod 5)`.

Thus the advertised concrete collision is genuine.  The generic conjunction
also replays directly: substituting `H = alpha • G` gives
`Com(m,r) = (m + r*alpha) • G`; injectivity of scalar action turns kernel
membership into `m + r*alpha = 0`; `(alpha,-1)` satisfies that equation and is
nonzero when `alpha` is nonzero.  The alternate blinder
`r + (m-m')/alpha` preserves the exponent.  From a different-message
collision, equality of exponents forces `r' ≠ r` and
`alpha = (m-m')/(r'-r)`.

Hypothesis-delta audit:

| item in elaborated context | source disposition |
| --- | --- |
| `[Field F]`, `[AddCommGroup V]`, `[Module F V]` | stated model/scoping |
| `hAlpha : alpha ≠ 0` | stated |
| `hH : H = alpha • G` | stated |
| `hG : Function.Injective (fun a => a • G)` | stated exact-generator premise |
| local `Fact (Nat.Prime 5)` | discharged internally by `by decide`; not a binder |

There is no new hidden hypothesis from the correction.

## Trust-boundary audit

The producer source has no token match for `sorry`, `admit`, `axiom`,
`unsafe`, `extern`, `implemented_by`, or `native_decide`.  Its only `decide`
uses are the local proof that 5 is prime and the final ordinary finite proof.
Ordinary `decide` elaborates and reduces a proof term checked by Lean's kernel;
it is materially different from the plan-forbidden `native_decide`, which
delegates evaluation to compiled native code.

The theorem remains an abstract algebraic statement.  It does not establish
computational binding, an adversary or security game, DLP hardness, outsider
recovery of `alpha`, hiding, generator derivation, commitment parsing, a
concrete curve/subgroup refinement, runtime, or success probability.

## Hosted machine evidence

GitHub Actions run `41512636120`, job `125508254976`, completed successfully
on the exact producer SHA.  The job used hosted runner `2.338.2`, Ubuntu
26.04.1 (`ubuntu-26.04`, image `20261025.179.1`), Lean 4.35.0 commit
`eb6cafb7290e8bd5f2937522d8d804f58f02bafc`, and Lake
`5.0.0-src+eb6cafb`.

- `lake build` compiled
  `CryptoResearch.AttackCorpus.PedersenRelationKernel` and finished all 9,135
  jobs successfully.  The module emitted style/import warnings only.
- `python3 tools/verify_formal_targets.py --artifact-dir formal-receipts
  --min-verified 66` reported 113 verified, zero not verified, zero
  infrastructure failures, and zero undischarged targets.
- The verifier explicitly audited target `attack-pedersen-relation-kernel`
  and exact declaration
  `CryptoResearch.AttackCorpus.PedersenRelationKernel.known_relation_kernel_and_alternate_openings`,
  reported it `machine_verified`, and wrote
  `formal-receipts/attack-pedersen-relation-kernel.json`.  Under the documented
  workspace verifier contract this includes the module build, workspace axiom
  audit, and generated exact-named-declaration audit.
- Dependency-pin checks passed both before and after proof checks with manifest
  SHA-256 `b46170db7f5631f573ff808cf1bc53655f3bd5385aeecc717c009a42dc01cec7`.
  Installed clean revisions matched the manifest: CryptoLean
  `60952c696ded7f3da4f4517006d9af6482662487`, mathlib
  `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`, plausible
  `dfa4f38190d07c37e315953e08b90fe2d95b3c24`, LeanSearchClient
  `d6b4c7be5be75ec4917c873ac50c756dc1436372`, importGraph
  `a41f0e9a4dea23188ea9cc1c41ac9f8bbafe0b93`, proofwidgets
  `df72b022e558978a1c50264cfc4d7fec86fa8e04`, aesop
  `4a174c490d8707121c4a9290800489f105d85e07`, Qq
  `dce0ad79c486cb1fb504af04f953c3466b0c6db8`, batteries
  `66e469188fe07963e5cf666c7d4433f45b8131c5`, and Cli
  `c24fe6078c630e89b489bffe59b3e20ac30d12c8`.
- The job uploaded 115 receipt files as artifact
  `formal-verification-receipts`, ID `13175228889`, 1,523,974 bytes, archive
  SHA-256 `4df8ae98f7487ba386bb4bcebd6ab0ade17cefeaabe2b4212919513f29a740c3`.
  GitHub's artifact API reports it unexpired.

The pin receipt expressly records
`binary_or_independent_kernel_recheck: false`: this evidence retains the
documented Lean/Lake binary trust boundary and is not a `lean4checker`
recheck.  In addition, this review environment's CONNECT proxy returned HTTP
403 for the Azure blob host, so I could not reopen the artifact zip payload;
the exact receipt path, upload count, byte count, digest, artifact ID, and
successful finalization were independently checked in the GitHub job log and
artifact API metadata.  No local build or scientific run was performed, as
the assigned protocol required.

## Scoped conclusion

E3 holds.  The producer correction is a proof/elaboration repair for the
unchanged finite Pedersen relation-kernel target.  This verdict supports only
that algebraic theorem and the concrete `ZMod 5` nonvacuity control; none of
the excluded computational or implementation claims follows from it.
