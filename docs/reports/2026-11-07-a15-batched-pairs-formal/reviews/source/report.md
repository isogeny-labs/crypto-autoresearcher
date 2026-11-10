# A15 source-fidelity review — independent source reviewer

Archival task: **T-1779**. Reviewer identity: `/root/a15_source_xhigh`, review-adversarial source-fidelity lane. Filed 2026-11-07. This report was composed before reading any sibling report or prior reviewer output. The task's corrected output path is `/var/tmp/a15-source-report-xhigh-20261107.md`.

## Verdict

**holds**, for the exact abstract-field claim in `formal/targets/prime-field-a15-batched-pairs.yaml` and its correspondence to the two identified local source joints. The named declaration has both nonzero child hypotheses, the two child-inverse conclusions, and the four signed-coordinate equalities. The inspected Python formula and emitted sign order agree with those equalities.

**breaks**, for an interpretation of the opening review-plan phrase “exact finite scalar/batched parity” as an end-to-end implementation or retained-run theorem. There is no theorem about lists, NumPy arrays, recursive tree shape, table entries, an elliptic curve, scalar `QueryIndex`, a run, or a metric. The target and Lean header correctly state these exclusions. The final packet should use the target's local-joint wording when it reports what is proved.

**inconclusive**, for a fresh independent machine replay in this reviewer session. The archived pass receipt is hash-consistent with the supplied snapshot and explicitly prints the elaborated type and standard axiom dependencies. A fresh lightweight Lean command did not reach Lean because the pinned release was absent. This is an infrastructure limitation, not a theorem failure. I do not independently assert `validated_scoped` for the whole review packet.

| Dimension | Finding |
| --- | --- |
| Archived machine status | `passed` as recorded: `machine_verified`, build and named audit true, no forbidden constructs, semantic review pending |
| Fresh machine status | `infrastructure_error`: no Lean elaboration output obtained; no build launched |
| Fidelity to exact target | `faithful_scoped` |
| Source-review joint verdict | `holds` at the local formula and order scope |
| Concrete software, geometry and run parity | Outside this theorem; bridges enumerated below |

## Input binding and receipt checks

The worktree HEAD was `bafd5233baef85efa1afa5a385fe3d5cc5d3235f`, clean at both status checks. A read-only `git ls-remote --heads origin refs/heads/formal/a15-batched-pairs-20261107` returned that same full SHA. The local `origin/main` was `d4cf45f012a0208b179d947052cb47b82f06ee09`. I preserved the supplied producer snapshot and did not fetch, merge, commit, push, or change tracked source.

Recomputed SHA-256 values:

| File | SHA-256 |
| --- | --- |
| `formal/CryptoResearch/PrimeField/BatchedPairs.lean` | `a25ec80d038925424f377eec7a5caa55a92f9dc756893edfd07df0bccda94e9e` |
| `formal/targets/prime-field-a15-batched-pairs.yaml` | `dc1239267fbd3f0f70b25252ed4335613df64ec5d771fdab3512574db3c2b37a` |
| `research/prime_field_a15_execution_20261107/pairbuild15.py` | `c8cbe4ab864157ff4c4c4f0b0414950847e7de0355585199629778c50280f55a` |
| `research/prime_field_a12_execution_20261106/batch_query.py` | `30f20fc9c8c276d2c2f90881b48f8a33ca6d32d9b67ec60a70580a241b30f72b` |

The review plan's displayed Lean digest is missing the final `e`; its text ends `...94e9`, whereas the actual file and both verifier receipts end `...94e9e`. Treat that plan digest as a transcription defect and correct it additively when assembling the packet. The target and Python digests match exactly.

Both receipts name source commit `d4cf45f012a0208b179d947052cb47b82f06ee09`, so that field alone does not assert execution on the later pushed proof commit. I reconciled their content manifests with the supplied files:

- `verify-passed.json`: all 104 `workspace_inputs` and all 10 `verifier_inputs` matched their current bytes. Its manifest digest is `b46170db7f5631f573ff808cf1bc53655f3bd5385aeecc717c009a42dc01cec7` and matches the current file. The separate target, theorem and toolchain digests match. This is content correspondence, not authentication of historical execution.
- `verify-timeout.json`: every listed workspace and verifier input matched except `formal/lake-manifest.json`, whose recorded older digest is `e6121ce2d40bd8baf6d7dfac66e2ac6a3cc1d39b443dcf5072b2abcd8838b409`. It records `verification: null`, empty `build_log`, empty `audit_log`, and `TimeoutExpired: Command '['lake', 'build']' timed out after 120 seconds`. The empty logs do not independently locate the timed-out command inside a particular Semaev module.
- The pass log contains the default build success (`9145 jobs`), explicit `CryptoResearch.PrimeField.BatchedPairs` target success (`789 jobs`), and the named declaration audit. It includes a 317-second Semaev module build, but that observation does not reconstruct the missing timeout log. Its audit reports 1302 theorems with standard axioms only and names the exact A15 theorem.

Pins read from the current files: Lean `leanprover/lean4:v4.35.0`; Mathlib `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`; CryptoLean `60952c696ded7f3da4f4517006d9af6482662487`. I did not check installed dependency cleanliness or independently recheck dependency binaries.

## Exact elaborated type and algebraic joint

The following is the elaborated named type recorded in the pass receipt; source inspection gives the same binders and conclusions. Prefixes below are shortened only by opening the namespace:

```lean
CryptoResearch.PrimeField.BatchedPairs.a15_algebraic_joints.{u_1}
  {F : Type u_1} [Field F] (x y xj yj xk yk : F)
  (hx : x ≠ 0) (hy : y ≠ 0) :
  (x * y)⁻¹ * y = x⁻¹ ∧
    (x * y)⁻¹ * x = y⁻¹ ∧
      pairX xj (-yj) xk (-yk) = pairX xj yj xk yk ∧
        pairY xj (-yj) xk (-yk) = -pairY xj yj xk yk ∧
          pairX xj (-yj) xk yk = pairX xj yj xk (-yk) ∧
            pairY xj (-yj) xk yk = -pairY xj yj xk (-yk)
```

The pass receipt prints `[propext, Classical.choice, Quot.sound]` for the theorem. The source has no `sorry`, custom axiom, `native_decide`, unsafe kernel bypass, or assumed parity conclusion. `autoImplicit` is false. I inspected the proof text; this report does not claim a fresh transitive axiom audit.

`x,y` are universally quantified product-tree child values. `xj,yj,xk,yk` are six unrelated field parameters after including `x,y`; no constraint links children to pair-coordinate denominators. There is no finiteness, characteristic, primality, curve, subgroup, distinct-x, ordering, or software assumption hidden in this type. In particular the sign formulas hold even in characteristic two and at equal x as totalized field expressions. That generality is correct for the stated formula identities.

The inverse propagation is a direct conditional field identity. For a parent product `x*y`, the left inverse is `(x*y)^-1*y` and the right inverse is `(x*y)^-1*x`. The two hypotheses suffice; they are satisfiable, e.g. in F_17 with x=y=1. The individual left identity fails when the other child y=0 and x=1; the right fails when x=0 and y=1. They therefore cannot be dropped from the combined theorem.

For sign reuse, negating both y inputs changes `(yk-yj)` to its negative and leaves the inverse denominator unchanged, so the slope changes sign. Its square preserves `pairX`; substituting the changed slope and changed first y into `pairY` negates `pairY`. Applying that identity to `(yj,-yk)` gives the `(-,+)` versus `(+,-)` result. This derivation uses the producer definitions and is source review, not the designated blind derivation.

## Source-to-formula and order fidelity

| Source joint | Exact match and remaining obligation |
| --- | --- |
| `batch_query.py:36`–48 | Leaves are nonempty and checked for literal zero at line 38. Odd levels get a 1, products are formed in adjacent even/odd slices, and reverse propagation writes left slots from the opposite right child and right slots from the opposite left child at line 47. This is the theorem's two local inverse identities. The theorem does not prove the loop invariant, padding, lengths, trim, or root inverse correctness. |
| `pairbuild15.py:70`–81 | `combinations(range(n),2)` fixes lexicographic j<k. `product((0,1),repeat=2)` yields `(side,coordinate)=(0,0),(0,1),(1,0),(1,1)`, hence Xj,Yj,Xk,Yk. This aligns the parameter order with the Lean definitions. |
| `pairbuild15.py:82`–106 | The denominator is Xk−Xj. The numerator is Y−Yj. The code evaluates `slope*slope−(Xj+Xk)` and `slope*(Xj−xx)−Yj`, exactly `pairX` and `pairY`. There is no swapped denominator or first-input y sign. |
| `pairbuild15.py:103`–112 | Direct outputs are `(yj,yk)` and `(yj,−yk)`. Negations are assigned as `neg_minus, neg_plus`, so the third output negates the minus output and the fourth negates the plus output. This matches the named Lean sign lemmas. |
| `pairbuild15.py:115`–124 | The emitted signs are `(++),(+-),(-+),(--)`, zipped strictly with `plus,minus,neg(minus),neg(plus)`. Coordinates, geometric indices and native indices stay in that order. |
| A14 `query_index.py:42`–55 | The retained scalar control iterates the same outer combinations then the same sign product. The ordering matches on inspection. Its use of actual group addition is not identified by the Lean theorem. |

A singleton geometric base has no pair combinations; `BatchedPairIndex` returns at lines 79–80 without calling `batch_inverse`. An empty geometric base is refused by A14 `require` (`1 <= len(points)`); an empty batch is independently refused by `batch_inverse`. There is no empty-case vacuity hiding the local theorem, but its source application to these control-flow cases remains unformalized.

## Adversarial controls and exact results

The finite-field calculations below were independently computed with Python integer modular arithmetic, using inverse 0 defined to be 0 to model Lean's totalized inverse. They are concrete counterexamples or formula checks, not Lean-checked examples and not executions of NumPy:

```
zero_child x=1 y=0: left 0 versus 1; right 0 versus 0
zero_child x=0 y=1: left 0 versus 0; right 0 versus 1
signed outputs for (5,1),(6,3): [((1, 1), (10, 6)), ((1, -1), (5, 16)), ((-1, 1), (5, 1)), ((-1, -1), (10, 11))]
equal-x totalized formula P+P: (7, 16); genuine curve double: (6, 3)
equal-x totalized formula P+(-P): (7, 16); genuine curve sum: infinity
```

- **Dropped hypotheses — breaks the widened claims.** In F_17, x=1,y=0 makes the left equation 0=1; x=0,y=1 makes the right equation 0=1. The actual theorem retains both hypotheses.
- **Equal x — breaks the geometric overinterpretation.** On the nonsingular toy curve y²=x³+2x+2 over F_17, P=(5,1) and 2P=(6,3). The totalized candidate formula for P+P is (7,16), different from 2P; for P+(−P) it remains a finite candidate while the group sum is infinity. Negation equalities continue to hold at xj=xk, which is precisely why those equalities cannot certify geometric addition there.
- **Source equal-x guard — source holds.** Executing the AST-extracted `validate_geometry` on `[(5,1),(5,16)]` reached and raised `pair geometry must contain finite, non-order-two, distinct sign classes`. Independently, source lines 87–90 refuse a zero denominator before inversion, including a direct constructor call that bypassed `build`'s geometry validation. That latter branch was inspected, not executed.
- **Sign-order swap — known-false nearby control.** With (5,1),(6,3), the second and third outputs are (5,16) and (5,1); swapping their values while retaining the signs is observably wrong. The actual emitted layout is the correct one.
- **Off-curve input — missing bridge is observable.** The pair validator checks coordinate type/range, y≠0, distinct x and consistency with the fixture's factor-base entry. It does not evaluate the curve equation. For p=17, coordinate entries (1,1),(2,1) can satisfy those local structural tests while failing y²=x³+2x+2. A runtime trial of this path did not complete because the available Python lacks `zip(strict=True)`; the guard conclusion here follows from the read code, not that failed trial.

## Uint64 boundary

For reduced operands 0≤a,b<p and the actual strict gate `3 <= p < 2**32`, the greatest integer p admitted by the gate is 4294967295. It is not prime; the greatest prime below 2**32 is 4294967291, but primality is a separate input obligation. The generic gate bound gives:

- Multiplication: `(p−1)^2 <= (2**32−2)^2 = 18446744056529682436 < 2**64`.
- Addition: `a+b <= 2p−2 <= 8589934588`.
- Subtraction as implemented: `p−b` lies in [1,p], so no unsigned underflow occurs; `a+(p−b) <= 2p−1 <= 8589934589`.
- Reduction by `np.remainder` preserves operands in [0,p−1]; padding 1 is reduced under p≥3. Conditional on a matching scalar modulus and reduced root inverse, the same bounds continue through each tree level and pair operation.

The product bound is sound at the stated gate. Extending it to p=2**32+1 would fail: a=b=2**32 gives exact product 2**64, which wraps to 0 in uint64, while the exact residue modulo p is 1. This is an arithmetic counterexample to broadening the gate; it is not an observed NumPy execution.

No concrete NumPy primitive test completed in this session: `python3` failed at `import numpy` with `ModuleNotFoundError`. The gate applies to `fixture['p']`, while `VectorField` uses `meter.f.p`; matching them and proving every input/root inverse remains reduced are additional implementation invariants. Neither the type nor the local pair validator proves primality. Over a composite modulus, initially nonzero leaves can multiply to zero (e.g. 3*5 modulo 15), so “literal nonzero leaves” alone does not instantiate the field theorem.

## Missing bridges, individually

1. **Concrete field refinement:** a proof or verified connection from each NumPy uint64 primitive, scalar `inv`, input conversion and modulus to the chosen field, including reducedness, broadcasting, mutation and alias behavior.
2. **Input validity and admission:** proof that the actual construction uses `build` with validated points, that meter and fixture moduli agree, that p is prime, and that the geometric/native mapping is valid. The direct `BatchedPairIndex` constructor itself invokes `require`, not full `validate_geometry`.
3. **Whole inverse tree:** nonzero products at every level, root inverse correctness, odd padding, slice lengths, reverse-loop induction, final trim, singleton and empty handling.
4. **Curve addition:** an actual nonsingular curve, valid input points and negation model, distinct x, and an affine-addition theorem equating the formulas with that curve's group operation. The pair validator does not establish membership on its own.
5. **Ordered scalar parity:** a theorem comparing the complete scalar `QueryIndex` output with the candidate list, native index mapping, table insertion, collisions, event order and inherited query consumers.
6. **Experiment and counters:** custody of the exact executed version, inputs and configuration, runtime/dependency state, retained rows, certificates, complete raw records, operation counts, measured costs and final run replay. Neither hashes nor the field identities establish these facts.

These are acknowledged scope boundaries in the target, not defects in the local identities. A next local construction would formalize an ordered list-level inverse-tree invariant and then connect a checked curve-addition formula to the four-output list. The report makes no novelty, speed or original-run claim.

## Fresh-check attempts and procedure deviations

I attempted only a cached-import command, `timeout 45s lake env lean --stdin`, containing an import of the exact module, a `#check` of the theorem, `#print axioms`, prints of the three definitions and small counterexample examples. The command reached the elan shim, found release Lean 4.35.0 absent, and began downloading/installing it. I terminated the exact timeout process with TERM; final exit was 143. No Lean output, example check or build was obtained. The attempted toolchain installation created automatic runtime artifacts under `/home/ec2-user/.elan/toolchains/`; I did not treat them as reviewed inputs, remove shared state, or run another installation. This automatic side effect is disclosed because the task limited deliberate writes to this report. The repository remained clean.

The attempted NumPy diagnostic exited 1 before loading source code because NumPy was unavailable. A subsequent standard-library extraction reached the real equal-x rejection, then exited 1 at `zip(strict=True)` on the off-curve case. `/usr/local/bin/python3`, suggested by the repository's cloud-specific instruction, was absent (exit 127). I stopped those runtime attempts and finished with source inspection and the exact integer controls recorded above. No failed control is presented as a successful runtime replay.

A broad `rg` over A14 accidentally included run JSON and produced truncated output. Those paths are disclosed below as search scope. It did not include the sibling blind packet, sibling report, or prior interrupted reviewer output. No conclusions about the A14 run are drawn from those snippets. No literature or prior-result claim is made: the primary sources for this local audit are the exact proof, executable source, dependency pins and verifier evidence listed here. Relevant memory registry search returned no matching A15 guidance and contributed no substantive fact.

The parent owns final composition, independence checking, archival, visual report, publication and current-head CI. This report changes no official evidence or hypothesis status.

## Review attestation

```yaml
review_attestation:
  reviewer: /root/a15_source_xhigh
  policy: review-adversarial
  archival_task: T-1779
  snapshot: bafd5233baef85efa1afa5a385fe3d5cc5d3235f
  joints_owned:
    - machine theorem and hypotheses
    - code-to-formula bridge
  sources_read: complete explicit-content, search-scope and hash-only lists below
  sibling_report_access: false
  prior_reviewer_output_access: false
  blind_input_access: false
  sibling_isolation_attested: true
  blind_rederivation:
    role: source reviewer, not designated blind reviewer
    claimed: false
    producer_source_read: true
  verdict: holds
  verdict_scope: exact target field identities and inspected local formula/order correspondence
  widened_implementation_or_run_claim_verdict: breaks
  fresh_independent_machine_replay: inconclusive
```

I attest that I did not open `/var/tmp/a15-blind-report-20261107.md`, any other blind report, `blind-input.md`, or any prior interrupted source-review output. A directory listing exposed the name of `blind-input.md` and a toolchain glob exposed names `/var/tmp/a15-axioms.lean` and `/var/tmp/a15-lean-toolchain`; I did not read their contents. I did not receive a sibling verdict; the parent only notified me that the sibling report was filed. The complete content-read scope follows. Automatic Lean/elan runtime accesses and ordinary Git object reads are distinct from explicitly reviewed source files.

### Explicit content reads (full or selected lines)

- `/var/lib/spot-codex/home/skills/review-evidence/SKILL.md`
- `/var/lib/spot-codex/home/skills/review-evidence/references/lean-review.md`
- `/var/tmp/dashboard-fullhistory-main-20261107/AGENTS.md`
- `/var/tmp/dashboard-fullhistory-main-20261107/docs/agent-contract-extended.md`
- `/var/tmp/dashboard-fullhistory-main-20261107/docs/agent-contract-supplement.md`
- `/var/tmp/dashboard-fullhistory-main-20261107/docs/reports/2026-11-07-a15-batched-pairs-formal/review-plan.md`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/targets/prime-field-a15-batched-pairs.yaml`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/PrimeField/BatchedPairs.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a15_execution_20261107/pairbuild15.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a12_execution_20261106/batch_query.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a15_execution_20261107/deps15.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/query_index.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/guards.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/shared.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/lean-toolchain`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/lakefile.toml`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/lake-manifest.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/docs/reports/2026-11-07-a15-batched-pairs-formal/evidence/verify-timeout.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/docs/reports/2026-11-07-a15-batched-pairs-formal/evidence/verify-passed.json`

### Recursive search scope

These are the complete file paths in the earlier A14 search input; some supplied matched snippets and some were scanned without a match. No source outside this scope was introduced by that search.

- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a12_execution_20261106/affine_solver.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/PROOF-STATUS.md`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/README.md`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/RESULTS.md`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/admission-assessment.a14-source.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/admission-assessment.a14-source.v2.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/affine_branch.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/analyze14.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/check_base.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/check_construct.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/check_information.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/check_mixed.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/check_partial.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/check_query.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/cold14.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/controls-refinement.md`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/custody14.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/database/v17-mixed-known-helpers/.artifacts.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/database/v17-mixed-known-helpers/validation.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/database14.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/design.md`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/diagnostic-custody-correction.md`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/driver14.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/execution-plan.md`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/geometry.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/guards.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/implementation-readiness.md`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/implementation-readiness.v2.md`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/information.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/inputs.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/literature.md`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/mixed_collection.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/native_case.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/next-leads.md`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/partial_solver.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/prepare14.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/protocol.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/protocol.preview.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/protocol.preview.v2.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/public_base.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/query_index.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/record_benchmark14.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/report14.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/reports/a14-mixed-known-helpers-4bbcf6/.artifacts.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/reports/a14-mixed-known-helpers-4bbcf6/cold-components.svg`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/reports/a14-mixed-known-helpers-4bbcf6/inspection.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/reports/a14-mixed-known-helpers-4bbcf6/observation.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/reports/a14-mixed-known-helpers-4bbcf6/old-base-information.svg`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/reports/a14-mixed-known-helpers-4bbcf6/plotted-data.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/reports/a14-mixed-known-helpers-4bbcf6/recovery-general.svg`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/reports/a14-mixed-known-helpers-4bbcf6/recovery-hash_offset.svg`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/reports/a14-mixed-known-helpers-4bbcf6/recovery-walk.svg`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/reports/a14-mixed-known-helpers-4bbcf6/render.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/reports/a14-mixed-known-helpers-4bbcf6/report.typ`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/root-release.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/.artifacts.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/checkpoint-p262139-i0.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/checkpoint-p262139-i1.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/checkpoint-p524287-i0.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/checkpoint-p524287-i1.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/child.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/derived-encodings/analysis.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/derived-encodings/export.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/execution.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/host.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/metrics.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/ownership.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/.artifacts.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/admission.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/generated.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/generation-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/generation.events.jsonl`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.base16-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.base16.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.base32-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.base32.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.base48-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.base48.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.complete.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.encodings.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.hybrid.prelude-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.hybrid.prelude.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.hybrid.query-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.hybrid.source-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.known32.prelude-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.known32.prelude.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.known32.query-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.known32.source-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.known32.source.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.known48.prelude-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.known48.prelude.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.known48.query-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.known48.source-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.known48.source.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.norm.prelude-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.norm.prelude.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.norm.query-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.norm.source-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.target-recipes.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.targets-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i0.targets.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.base16-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.base16.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.base32-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.base32.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.base48-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.base48.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.complete.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.encodings.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.hybrid.prelude-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.hybrid.prelude.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.hybrid.query-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.hybrid.source-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.known32.prelude-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.known32.prelude.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.known32.query-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.known32.source-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.known32.source.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.known48.prelude-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.known48.prelude.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.known48.query-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.known48.source-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.known48.source.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.norm.prelude-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.norm.prelude.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.norm.query-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.norm.source-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.target-recipes.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.targets-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p262139-i1.targets.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.base16-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.base16.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.base32-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.base32.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.base48-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.base48.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.complete.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.encodings.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.hybrid.prelude-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.hybrid.prelude.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.hybrid.query-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.hybrid.source-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.known32.prelude-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.known32.prelude.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.known32.query-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.known32.source-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.known32.source.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.known48.prelude-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.known48.prelude.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.known48.query-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.known48.source-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.known48.source.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.norm.prelude-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.norm.prelude.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.norm.query-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.norm.source-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.target-recipes.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.targets-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i0.targets.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.base16-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.base16.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.base32-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.base32.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.base48-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.base48.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.complete.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.encodings.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.hybrid.prelude-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.hybrid.prelude.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.hybrid.query-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.hybrid.source-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.known32.prelude-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.known32.prelude.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.known32.query-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.known32.source-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.known32.source.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.known48.prelude-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.known48.prelude.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.known48.query-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.known48.source-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.known48.source.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.norm.prelude-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.norm.prelude.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.norm.query-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.norm.source-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.target-recipes.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.targets-check.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw/p524287-i1.targets.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/stderr.txt`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/stdout.txt`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/shared.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/source-publication.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/source-publication.v2.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/source_construct.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/streams14.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/supervise14.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/target_cache.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/test_base.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/test_cache.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/test_construct.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/test_geometry.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/test_information.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/test_mixed.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/test_native.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/test_partial.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/test_query.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/test_runner14.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/benchmark-final-check.txt`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/benchmark-progress-inspection.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/benchmark-registration-recovery.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/component-status.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/diagnostic-custody-software-status.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/diagnostic-partial-export-controls-20261106T2308Z.txt`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/mixed-native-information-component-status.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/native-assembly-preparation-failure-20261106.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/observation-format-failure.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/official-s3-final.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/official-s3-raw-upload.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/official-s3-raw-verify.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/official-s3-report-database-upload.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/paid-source-components-status.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/pcc-claim-creation.txt`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/pcc-local-verdict.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/pcc-standing.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/progress-export-software-controls.txt`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/prose-standing-qualification.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/query-index-component-status.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/runnable-source-software-status.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/runner-export-tamper-controls-20261106T2257Z.txt`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/session-receipt-publication.txt`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/software-controls-20261106T2132Z.txt`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/software-controls-20261106T2142Z.txt`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/software-controls-20261106T2243Z.txt`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/software-controls-20261106T2300Z.txt`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/software-controls-20261106T2310Z.txt`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a14_execution_20261106/validation/startup-checkpoint-heading-failure.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/research/prime_field_a15_execution_20261107/deps15.py`

The memory registry `/var/lib/spot-codex/home/memories/MEMORY.md` was searched only for `A15|batched.pairs|T-1779|review.*Lean|proof.*workflow`; no match was returned. No rollout summary or memory skill was read.

### Receipt-manifest byte reads for SHA-256 verification

The following 104 workspace paths and 10 verifier paths were read as bytes solely to compare the recorded manifests; this is not a semantic review of those adjacent sources. The paths are complete and intentionally include overlap with the explicit-content list.

- `/var/tmp/dashboard-fullhistory-main-20261107/formal/AxiomAudit.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/AttackCorpus/AdaptiveBatching.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/AttackCorpus/CofactorPushforward.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/AttackCorpus/CubicEvalRank.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/AttackCorpus/FiatShamirZeroHash.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/AttackCorpus/ModAlias.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/AttackCorpus/OneShotHistory.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/AttackCorpus/PedersenRelationKernel.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/AttackCorpus/PolynomialFunctionAlias.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/AttackCorpus/SchnorrSpecialSoundness.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/AttackCorpus/SubgroupMembership.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Binstd/CanonicalFrobenius.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Binstd/EncodedDivisors.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Binstd/Factorization.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Binstd/Irreducibility.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Binstd/YieldCeiling.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Endosweep/AlphaAdic.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Endosweep/BinaryGLS.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Endosweep/Blinding.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Endosweep/ChainEigen.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Endosweep/Discriminant.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Endosweep/DkExact.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Endosweep/DkExactBatch2.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Endosweep/DkExactBatch3.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Endosweep/DkExactBatch4.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Endosweep/DkExactBatch5.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Endosweep/DkExactBatch6.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Endosweep/DkExactBatch7.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Endosweep/FrobeniusSplit.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Endosweep/Koblitz.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Endosweep/LambdaCoordinates.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Endosweep/NativeChains.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Endosweep/NistCertificates.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Endosweep/Pippenger.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Endosweep/RMGoldenNorm.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Endosweep/SubgroupIndex.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Endosweep/XOnlyConjugate.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/FallDegree/AffineFibreRefutation.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/FallDegree/BinaryCoefficientDescent.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/FallDegree/BinaryLocalization.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/FallDegree/BinarySemaevShape.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/FallDegree/BooleanNormalization.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/FallDegree/ClosureCertificates.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/FallDegree/FirstFallBounded.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/FallDegree/LastFall.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/FrobTrace/CharacteristicFive.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/FrobTrace/FactorKernel.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/FrobTrace/FiniteFieldTrace.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/FrobTrace/NullCurveOrder.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/FrobTrace/OrderFive.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/FrobTrace/QuotientFrobeniusMap.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/FrobTrace/QuotientKernelTransport.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/FrobTrace/QuotientMatrices.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/FrobTrace/QuotientMatrixKernels.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Galbraith/MontgomeryReduction.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/IC/ArityOracleCompleteRealModel.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/IC/ArityOracleThreshold.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/IC/ExtensionFieldEmbedding.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/IC/MemoryCouplingArityTwo.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Isogeny/CoprimeTransfer.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/NCP/AffineNormalForm.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/NCP/CommutatorCompanion.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/NCP/CommutatorIdeal.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/NCP/CyclicPointAction.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/NCP/PointAction.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/NCP/Reachability.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/NCP/ReachabilityControls.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Nagao/Bridge.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Nagao/BridgeB.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Nagao/FakeExact.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Nagao/Lemma4Outside.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Nagao/Lemma4Witness.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Nagao/RecoveryRule.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/PrimeField/BatchedPairs.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Quotient/TranslationDescent.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Runbook/BsgsCoverage.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Semaev/BooleanParityDegreeThreeRankCertificate.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Semaev/BooleanParityFiltrationCertificate.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Semaev/BooleanParityFiniteCertificate.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Semaev/BooleanParitySemanticRankCertificate.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Semaev/Certificate.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Semaev/ConcreteFirstFallWitness.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Semaev/DegreeTwoFall.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Semaev/FiniteEquationSemantics.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Semaev/FrobeniusCollapse.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Semaev/Symmetrization.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/CryptoResearch/Stark/AffineTransition.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/FoundationAxiomAudit.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/RetrospectiveAxiomAudit.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/lake-manifest.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/lakefile.toml`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/lean-toolchain`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/scoped-obstructions/AxiomAudit.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/scoped-obstructions/ScopedObstructions.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/scoped-obstructions/ScopedObstructions/Torsion.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/scoped-obstructions/lake-manifest.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/scoped-obstructions/lakefile.toml`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/scoped-obstructions/lean-toolchain`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/smoke/CryptoResearch.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/smoke/CryptoResearch/Smoke.lean`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/smoke/lake-manifest.json`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/smoke/lakefile.toml`
- `/var/tmp/dashboard-fullhistory-main-20261107/formal/smoke/lean-toolchain`
- `/var/tmp/dashboard-fullhistory-main-20261107/orchestration/formal/__init__.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/orchestration/formal/cli.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/orchestration/formal/integration.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/orchestration/formal/lean_worker.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/orchestration/formal/mathcode.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/orchestration/formal/models.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/orchestration/formal/pipeline.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/orchestration/formal/receipts.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/orchestration/formal/targets.py`
- `/var/tmp/dashboard-fullhistory-main-20261107/orchestration/formal/workspace.py`

Only the assigned report path was deliberately written. No commit, push, heavy build, cloud submission or scientific-status mutation was performed.
