# C3 correction review: cofactor pushforward

- Recorded: 2026-11-02T20:18:02Z
- Task: `TASK-20261102-0b8513`
- Joint owned: `C3` only

## Verdict

`C3: holds`.

The final correction at producer snapshot
`db090984ca1e78e92cea5e0840885ae982f12921` preserves every public
declaration type and the frozen target. The corrected proof has the right image
orientation, proves multiplication by two annihilates `ZMod 2`, proves it
permutes `ZMod 3`, establishes the bad `4/0` fibres, specializes the generic
repair to the good product, and retains all three required conjuncts. The exact
hosted final-SHA run built the module and reported the exact named target
machine-verified.

| Dimension | Scoped verdict |
| --- | --- |
| Machine status | `passed` at the exact producer snapshot |
| Fidelity | `faithful_scoped` |
| Review outcome | `validated_scoped` for C3 only |
| Correction-round verdict | `holds` |

This is not an adjudication of any other joint or of the round as a whole.

## Immutable bindings

| Object | Binding |
| --- | --- |
| v2 plan | commit `4248241742`; supplied and recomputed SHA-256 `f55ab631c4d216ffcd33edd2e08cdef9962fcb220905d0acf0c3f261aa7187bf` |
| Original snapshot | `674b3248a8b007748a2cf4f10e5063e7de123be4` |
| Final producer snapshot | `db090984ca1e78e92cea5e0840885ae982f12921` |
| Original source SHA-256 | `c28754bcf4568282f3524633bbfbbbc29e8ce432cd9068f2cecbdc3d072b90ca` |
| Final source SHA-256 | `53445da9ae485ed4cd5d76088b6932d842dfc61299cf98d986a5cc34125a9d5c` |
| Frozen target SHA-256, both snapshots | `4313d96609a4335cdab3da50a5bf3bb07cac3727f80652e312a80b26d8109ff4` |
| Named declaration | `CryptoResearch.AttackCorpus.CofactorPushforward.cofactor_failure_and_product_fiber_repair` |
| Hosted evidence | run `41512636120`, job `125508254976`, head `db090984ca1e78e92cea5e0840885ae982f12921` |

The working-tree source and target hashes equal the final producer blobs. The
target blob is byte-identical between original and final snapshots.

## Public types and correction delta

The exact original-to-final diff changes proof terms only. It changes no
import, namespace, definition header, abbreviation, theorem statement, binder,
instance, quantifier, conjunction, or target field. These public types are all
unchanged: `fiberCount`, `productClear`, `productTarget`,
`product_image_and_fiber_repair`, `BadAmbient`, `badClear`, `GoodAmbient`,
`goodClear`, `goodTarget`, and
`cofactor_failure_and_product_fiber_repair`.

The proof-only changes are load-bearing and correct:

1. The forward image inclusion needs `0 = h • k`; the correction uses
   `(hkill k).symm`.
2. The `ZMod 2` proofs explicitly rewrite `nsmul` to multiplication and reduce
   the cast of `2` to zero.
3. The `ZMod 3` injectivity proof cancels nonzero `2`; surjectivity uses inverse
   `2`, with `2 * 2 = 1` proved by kernel `decide`.
4. The bad fibres are proved as an all-elements filter and an empty filter.
5. The good specialization proves the definitional equalities between the
   named good maps and generic product maps, then transports the generic
   theorem. The final `And.intro hbad (And.intro hgood hgeneric)` loses no
   conjunct.

## Independent replay

For `P = (k,s)`,

```text
productClear h P = (h • k, h • s) = (0, h • s),
```

so the cleared range is contained in the target range. Conversely, if
`e(s) = h • s` is the equivalence supplied by `hperm`, then

```text
productClear h (0, e⁻¹(t)) = (0, t) = productTarget t.
```

This proves the range equality in the stated orientation. For fixed `t`,
`k ↦ (k,e⁻¹(t))` is inverse to projection of the fibre onto `K`. Every target
fibre therefore has size `|K|`, and multiplying by `|S|` gives `|K × S|`.
The corrected private equivalence also has the right equality orientation:
from `h • s = t`, injectivity reduces `e⁻¹(t) = s` to `t = h • s`.

For `BadAmbient = ZMod 2 × ZMod 2`, all four inputs map to `(0,0)` because
`2 = 0` in `ZMod 2`. Thus the fibre at `(0,0)` has size four and the fibre at
`(0,1)` is empty.

For `GoodAmbient = ZMod 2 × ZMod 3`, multiplication by two on the second
factor is the permutation `0 ↦ 0, 1 ↦ 2, 2 ↦ 1`, and the first factor is
annihilated. The exact fibres are:

| Target | Two preimages |
| --- | --- |
| `(0,0)` | `(0,0)`, `(1,0)` |
| `(0,1)` | `(0,2)`, `(1,2)` |
| `(0,2)` | `(0,1)`, `(1,1)` |

Hence the good image is exactly `{0} × ZMod 3`, every target has two
preimages, and the cardinal identity is `2 * 3 = 6`.

## Hypothesis deltas

| Declaration | Binder / instance / condition | Classification | Reason |
| --- | --- | --- | --- |
| both public theorems | `{K S : Type*}` | implied | The supplied factors in the claim. |
| both | `[AddCommGroup K]`, `[AddCommGroup S]` | implied | The source's finite additive groups in this additive cofactor model. |
| both | `[Fintype K]`, `[Fintype S]` | implied | Exact finiteness premise. |
| both | `[DecidableEq K]`, `[DecidableEq S]` | implied | Finite types admit decidable equality; this enables the finite filter without narrowing the mathematics. |
| both | `(h : ℕ)` | implied | The natural clearing scalar named by the claim. |
| both | `hkill : ∀ k, h • k = 0` | implied | Exact annihilation premise. |
| both | `hperm : Function.Bijective (fun s => h • s)` | implied | Exact bijective-action premise. |
| final theorem | fixed bad and good products, scalar `2` | implied | Exact source countermodel and finite control. |

No source-unstated scoping or unjustified premise was found. The final
declaration contains countermodel, good control, and generic repair in the
required order. It adds no ambient bijection, reverse implication, or
idempotent-retraction claim.

## Forbidden constructs and scope

An exact scan of the final source found no `sorry`, `admit`, project `axiom`,
`unsafe`, `extern`, `implemented_by`, or `native_decide`. Its `by decide`
proofs are ordinary kernel-checked decisions. The private `noncomputable`
equivalence is not a kernel bypass.

The statement is only about explicit finite products and a conditional generic
product. It does not construct or decompose an elliptic-curve group, identify a
concrete cofactor or suite, refine an implementation, establish hash-to-curve
uniformity or indifferentiability, prove an ECDLP result, or assert a protocol
vulnerability.

## Hosted machine evidence

Run `41512636120` (`lean-verification`) and formal job `125508254976`
completed successfully at the exact producer head.

- Machine: GitHub hosted compute agent, runner `2.338.2`, Ubuntu `26.04.1`
  LTS, image `ubuntu-26.04` version `20261025.179.1`, region `westus2`.
- Toolchain: Lean `4.35.0` commit
  `eb6cafb7290e8bd5f2937522d8d804f58f02bafc`; Lake
  `5.0.0-src+eb6cafb`.
- Build: `Build completed successfully (9135 jobs)`; the assigned module was
  explicitly built, with only import module-style warnings.
- Verifier: `113 verified, 0 not verified, 0 infrastructure, 0 undischarged`.
  The log announces the exact target and declaration, writes
  `formal-receipts/attack-cofactor-pushforward.json`, reports
  `machine_verified`, and lists that exact target as `verified`. Under the
  documented verifier contract, this includes its generated named declaration
  and axiom audit rather than only a project-root build.
- Pins: before and after checks passed identically with manifest SHA-256
  `b46170db7f5631f573ff808cf1bc53655f3bd5385aeecc717c009a42dc01cec7`.
  Expected and installed revisions matched with clean sources for CryptoLean
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
- Trust limit: the pin receipt says
  `binary_or_independent_kernel_recheck: false`; Lean/Lake binary trust remains
  disclosed.
- Artifact: `formal-verification-receipts`, ID `13175228889`, unexpired,
  `1,523,974` bytes, bound by the API to the exact run/head. Upload reported
  115 files and zip SHA-256
  `4df8ae98f7487ba386bb4bcebd6ab0ade17cefeaabe2b4212919513f29a740c3`.

Artifact metadata and the upload log were inspected. Direct archive download
was blocked by the reviewer container's network proxy at the redirected Azure
blob CONNECT tunnel (HTTP 403), so its internal JSON was not re-parsed. This
procedure deviation does not erase the exact log's build, verifier, named
target, pin, receipt-path, and upload evidence.

No sibling report, original review/blind output, abandoned correction
candidate, prior correction plan, initial evidence packet, sibling
conversation, or parent conversation was read. The v2 plan does not require a
new blind re-derivation; none is claimed. No local Lean build or run was
performed.
