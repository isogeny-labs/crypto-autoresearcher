# A3 correction review: OneShotHistory

## Verdict

**A3 holds.** At producer snapshot
`db090984ca1e78e92cea5e0840885ae982f12921`, the OneShotHistory correction is
proof-only, preserves every public declaration type and the frozen target, and
proves the range-sum inequality in the required direction. Hosted run
`41512636120`, formal job `125508254976`, passed the exact workspace build,
all-target verifier, and named audit for
`CryptoResearch.AttackCorpus.OneShotHistory.correlated_history_and_hazard_repair`.

This verdict is scoped to correction joint A3. It does not decide the other
correction joints or imply an xedni, ECDLP, probability-model, expectation, or
runtime result.

## Frozen bindings

- Review plan: `correction-review-plan-v2.yaml`, commit `4248241742`, SHA-256
  `f55ab631c4d216ffcd33edd2e08cdef9962fcb220905d0acf0c3f261aa7187bf`.
- Original snapshot: `674b3248a8b007748a2cf4f10e5063e7de123be4`.
- Final producer snapshot: `db090984ca1e78e92cea5e0840885ae982f12921`.
- Original source SHA-256:
  `d0f23ea9395bc8b3a8e2da15f73fdb43d30025571b708cdb4f2ed8bb2b8e76c1`.
- Final source SHA-256:
  `5420db0c7a6f1e6db1cc7d3e167f6811cc2f3d20f0b23f202101d9aeaa923cc6`,
  matching the v2 plan.
- Original and final target-spec SHA-256:
  `454e43192383e8e38c465eca5b2d9827c844e1d3a3edef6207918bfcda9c037e`.
  The target is byte-identical across the two snapshots.

## Source and public-type delta

The only original-to-final source change is inside the proof of `hsum` in
`survival_lower_bound_and_finite_tail`:

```lean
-- original
exact Finset.sum_le_sum fun i _hi ↦ hgeometric i

-- final
induction N with
| zero => simp
| succ N ih =>
    simpa only [Finset.sum_range_succ] using
      add_le_add ih (hgeometric N)
```

No definition or theorem signature changes. In particular, the types of
`correlatedSuccess`, `complementarySuccess`, `correlatedNatSuccess`, the five
finite countermodel theorems, `survival_lower_bound_and_finite_tail`, and the
audited declaration `correlated_history_and_hazard_repair` are unchanged.
The final declaration still contains all source-stated premises: `S 0 = 1`,
`0 ≤ epsilon`, `epsilon ≤ 1`, pointwise nonnegativity of `S`, and the
history-uniform recurrence `(1 - epsilon) * S n ≤ S (n + 1)`.

Hypothesis-delta result: empty. The correction adds no binder, instance,
`Fact`, fixed parameter, or side condition. The `S`-nonnegativity premise is
unused by this particular derivation, but it is explicitly present in both the
source statement and unchanged Lean type; that is not a hidden assumption or
a weakening.

## Independent proof replay

1. From `epsilon ≤ 1`, `1 - epsilon` is nonnegative. The geometric lower
   bound starts at equality because `(1-epsilon)^0 = 1 = S 0`.
2. In the successor step, multiplying
   `(1-epsilon)^n ≤ S n` on the left by the nonnegative factor preserves the
   order. The recurrence then gives
   `(1-epsilon)^(n+1) ≤ S (n+1)`. The orientation is therefore the claimed
   lower bound on survival, not its converse.
3. The corrected range-sum induction is exact. At `N = 0`, both sums are zero.
   At `N + 1`, `Finset.sum_range_succ` rewrites both sides to their `N`-term
   partial sums plus the final term. `add_le_add ih (hgeometric N)` gives the
   desired inequality in the same left-to-right orientation.
4. Multiplication by `epsilon ≥ 0` preserves the range-sum inequality.
   The finite geometric identity gives
   `1 - (1-epsilon)^N = epsilon * sum_{i<N}(1-epsilon)^i`; combining it with
   the scaled inequality yields the stated finite-tail bound. For `N = 0`,
   both sides are zero.

This is a finite algebraic consequence of an explicit recurrence. It neither
derives that recurrence from conditional probabilities nor identifies the
finite sum with an expectation.

## Forbidden constructs and scope

An exact-path scan of the final module found no occurrences of `sorry`,
`admit`, `axiom`, `unsafe`, `extern`, `implemented_by`, or `native_decide`.
The correction uses ordinary induction, `simp`, order lemmas, the geometric-sum
identity, and `ring`. The target remains a two-outcome Bool countermodel plus a
conditional real-sequence theorem. Its target prerequisites and non-implications
remain unchanged.

## Hosted machine evidence

`gh run view` reports run `41512636120` as successful on head SHA
`db090984ca1e78e92cea5e0840885ae982f12921`. Formal job `125508254976`
completed successfully.

- Toolchain: Lean `4.35.0`, Lake `5.0.0-src+eb6cafb`.
- Workspace build: `lake build` built
  `CryptoResearch.AttackCorpus.OneShotHistory` and finished successfully with
  9,135 jobs. The OneShotHistory messages were only import-deprecation and
  unnecessary-`simpa` lints.
- Verifier: `python3 tools/verify_formal_targets.py --artifact-dir
  formal-receipts --min-verified 66` reported `113 verified, 0 not verified,
  0 infrastructure, 0 undischarged`.
- Named audit: the log explicitly began verification of
  `attack-one-shot-history` with the exact declaration
  `CryptoResearch.AttackCorpus.OneShotHistory.correlated_history_and_hazard_repair`,
  wrote `formal-receipts/attack-one-shot-history.json`, and reported
  `machine_verified`; the final verifier table repeats that exact target and
  declaration as `verified`.
- Dependency custody: before and after proof checks, manifest SHA-256
  `b46170db7f5631f573ff808cf1bc53655f3bd5385aeecc717c009a42dc01cec7`
  passed. Expected and installed revisions matched with clean sources for
  CryptoLean `60952c696ded7f3da4f4517006d9af6482662487`, mathlib
  `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`, plausible
  `dfa4f38190d07c37e315953e08b90fe2d95b3c24`, LeanSearchClient
  `d6b4c7be5be75ec4917c873ac50c756dc1436372`, importGraph
  `a41f0e9a4dea23188ea9cc1c41ac9f8bbafe0b93`, proofwidgets
  `df72b022e558978a1c50264cfc4d7fec86fa8e04`, aesop
  `4a174c490d8707121c4a9290800489f105d85e07`, Qq
  `dce0ad79c486cb1fb504af04f953c3466b0c6db8`, batteries
  `66e469188fe07963e5cf666c7d4433f45b8131c5`, and Cli
  `c24fe6078c630e89b489bffe59b3e20ac30d12c8`.
- Receipt artifact: `formal-verification-receipts` uploaded 115 files as
  artifact `13175228889`, 1,523,974 bytes, with zip SHA-256
  `4df8ae98f7487ba386bb4bcebd6ab0ade17cefeaabe2b4212919513f29a740c3`.

The dependency receipt explicitly records
`binary_or_independent_kernel_recheck: false`; the evidence therefore retains
the stated Lean/Lake binary trust boundary. No local build was run, as required
by the v2 review plan's zero-build budget.

## Scoped conclusion

The source/spec hashes, unchanged public types, hand replay, forbidden-token
check, exact-SHA workspace build, all-target verifier, named theorem/axiom
audit result, clean pre/post pins, and uploaded receipts agree. Joint A3 holds.
