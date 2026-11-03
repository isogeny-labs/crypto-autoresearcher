# J2 current source and elaborated-type fidelity

**Verdict: holds for J2.** At producer commit `01df8d319edad2b28395167eed86581e6e54b302`, the seventh declaration exports the precise finite four-probe obstruction in the pinned Rust comment, with no extra premise beyond a nontrivial commutative ring. The original six theorem declarations are byte for byte unchanged from the sealed prior J2 source at `d4f1279102709518247f5a7d1926de354fe5929a`. The supplied hosted artifact prints all seven elaborated types and the two expected missing-`Nontrivial (ZMod 1)` diagnostics. This is a source/type verdict; the independent native-receipt and execution audit belongs to J3.

Task `TASK-20261103-5c964f`, Conductor `T-1512`. Source bindings are `input-bindings.json` and `review-plan.yaml` in `docs/reports/2026-11-03-stark-affine-proof-review/` at the pinned producer commit. I read no current J3 report or output and made no source edits, build, experiment, or network request.

## Exact bindings and reproducible controls

| Object | Pin / SHA-256 |
| --- | --- |
| Producer source commit | `01df8d319edad2b28395167eed86581e6e54b302` |
| Current Lean module | `3311451f0dfa19c9c696b872bb3b85d0ed60e68a75c89c871052cbd39dadfa0d` |
| Sealed prior J2 module | `f36f8650b18d26eaa64ce669dd5bf4cc501008c3322fd4967d40617166e2218b` |
| Rust source commit | `8ce2800fbe3d265027e2341ec193ad69b946a8bd` |
| Rust `src/zk/stark_v2.rs` | blob `6cb057163d6a12a4d69c037f16c753034228e59f`; SHA-256 `3bfe1facc87a2e522ffb69984cee5c18db71d1a216e72e521a5c694142b0e223` |
| Supplied compressed hosted artifact | `dab33a983b3140b5e387075eb937443e39321848b000af387507834ca36a36a1` |
| Extracted type/control print excerpt | `019ff2d9cacc37d63a6865f4d11362ebc036760c904def013db949943f1d2392` |

`check_source_types.py` reads exact Git objects and the named supplied artifact, writes `raw-checks.json` and `raw-type-and-control-prints.txt`, and exits with all checks true. It checks every `tracked_sha256` binding, the Rust blob and SHA, all seven declaration names, byte equality of the original six complete declaration bodies, presence of seven type prints and seven axiom prints, the seventh type's binders and four equality nodes, and both `ZMod 1` diagnostics. Run:

```sh
python3 /home/ec2-user/stark-affine-review-staging-20261103/TASK-20261103-5c964f/check_source_types.py
```

The printed types are supplied artifact text, not a fresh Lean execution or an authenticated runner record. J3 reviews receipt provenance and machine controls independently. The prior sealed J2 report at `research/stark-affine-proof-20261029/reviewers/TASK-20261029-55585f/report.md` established the historical six proposition correspondences; the byte comparison shows their statements and proofs remain the same in this source revision.

## Seventh claim against the Rust source

The Rust `AffineTransition` has private `previous`, `next`, and `constant` coefficients. Its `evaluate` text composes `fr_mul` and `fr_add` in the order `previous_coefficient * previous + next_coefficient * next + constant` (lines 176–204). The Lean `evaluate (a b c x y : R) := a*x+b*y+c` matches that algebraic expression, with `a,b,c` in the same order. Rust's comment at lines 954–957 names four field points and asserts that no affine rule agrees with `prev*next` at all of them. Its test constructs the candidate forced by the first three product values, verifies those three equalities, and asserts inequality at `(1,1)` (lines 959–970).

The actual seventh `#check @multiplication_not_affine_on_four_probes` type begins

```lean
∀ {R : Type u} [CommRing R] [Nontrivial R] (a b c : R),
  ¬ (E(a,b,c,0,0) = 0*0 ∧ E(a,b,c,1,0) = 1*0 ∧
     E(a,b,c,0,1) = 0*1 ∧ E(a,b,c,1,1) = 1*1)
```

Here `E` abbreviates the source `evaluate`; the receipt prints four nested `And`/`Eq` nodes with the four literal pairs in this exact order. Coefficients are quantified before the negation, so the assertion is uniform over *every* coefficient triple. There is no premise assuming product disagreement or coefficient values. The only extra structure compared with the three-probe theorem is `[Nontrivial R]`; this is required for `0 ≠ 1`, and the intended Rust scalar field is within that mathematical scope. The theorem is over all nontrivial commutative rings, a stronger algebraic domain than the specific scalar field. It assumes neither field inverses, characteristic, finiteness, nor a specific modulus.

The proof boundary is nonvacuous: `E00=c`, `E10=a+c`, `E01=b+c`, and `E11=a+b+c`. Agreement with multiplication at the first three points forces `c=a=b=0`; at the fourth it would force `0=1`, contradicted by `Nontrivial R`. An ordinary nontrivial ring such as `ZMod 2` witnesses the assumption's satisfiability. In `ZMod 1`, `0=1`; the existing `zero_ring_product_control` supplies equality everywhere, and the hosted text records both attempted applications failing specifically to synthesize `Nontrivial (ZMod 1)`. This checks the theorem cannot be applied to the known false zero-ring case. The older `two_probes_insufficient` gives a separate fixed pair of affine rules equal at `(0,0),(1,0)` and unequal at `(0,1)`.

The Rust test itself is one constructed candidate, while the Lean statement quantifies every triple. The first-three-probe coefficient recovery is the mathematical step linking the test's candidate to the universal statement. That is a valid source-claim refinement, not a claim that every possible Rust execution has been checked.

## Existing six and claim boundaries

| Declaration | Current elaborated type, normalized | J2 result |
| --- | --- | --- |
| `recover_coefficients` | For every `R : Type u`, `[CommRing R]`, and `a,b,c`, the tuple `(E10−E00,E01−E00,E00)` equals `(a,b,c)`. | Same complete declaration bytes as sealed J2; faithful. |
| `coefficients_eq_of_probes` | For six coefficients in any commutative ring, equality at `(0,0),(1,0),(0,1)` implies equality of coefficient triples. | Same bytes; faithful. |
| `three_probe_extensionality` | The same three hypotheses imply equality of evaluations for every subsequent `x,y : R`. | Same bytes; faithful to the registered three-probe target. |
| `multiplication_not_affine` | For `[CommRing R] [Nontrivial R]`, no affine triple agrees with `x*y` for **all** `x,y`. | Same bytes; global obstruction remains distinct from the seventh finite-point theorem. |
| `two_probes_insufficient` | Explicit zero and `(0,1,0)` coefficient triples agree at two named probes and disagree at the third in any nontrivial commutative ring. | Same bytes; fixed missing-probe control. |
| `zero_ring_product_control` | For all `x,y : ZMod 1`, zero affine expression equals `x*y`. | Same bytes; catches omission of nontriviality. |

All seven current printed types show their actual binders; `zero_ring_product_control` specializes to the genuine `ZMod.commRing 1`. The seven current axiom prints list `[propext]` for six declarations and `[propext, Quot.sound.{u}]` for the zero-ring control. This supports absence of custom axioms *in the supplied printout*, not an axiom-free claim or an independent kernel recheck.

The result concerns ring-valued expressions. Rust `BigUint` reduction and `fr_add`/`fr_mul` semantics have no refinement proof here. The `air_fingerprint` text evaluates the first three designated points plus public probe points and concatenates `reduced_bytes`; no theorem here establishes canonical byte injectivity, unambiguous concatenation, or full AIR identity. Likewise, the Lean propositions do not establish the runtime transition, trace validity, polynomial protocol, or STARK soundness. The producer `CLAIMS.md` and target notes keep those bridges separate. No Rust test run or historical execution is inferred from source text.

**J2 conclusion:** the repaired seventh theorem closes the prior exported-type gap for the exact finite four-probe assertion at the stated ring-expression level. The original six remain unchanged and their current supplied type prints match that scope. J3's independent receipt audit and the coordinator's combined review remain the next evidence steps.
