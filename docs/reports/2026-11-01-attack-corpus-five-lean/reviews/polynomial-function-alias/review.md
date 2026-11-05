# Independent review: polynomial/function alias

## Review state

- Assigned producer commit: `f5a8f8ac8c3cbae424b5cc56170f2e5db2dfa7cd`
- Producer tree: `95cf566e1d0f97e4719cc3c070b52765f8f35fd2`
- Claim: `ATTACK-POLYNOMIAL-FUNCTION-ALIAS`
- Machine status: `not_verified` pending the pinned Lean `v4.35.0` receipt.
- Scoped outcome: the two formal statements hold on human inspection and a non-authoritative Lean/Mathlib `v4.34.1` proxy; this does not promote the official research state.

## Blind-review compliance

Before opening the Lean proof, I read only:

- `formal/targets/attack-polynomial-function-alias.yaml`; and
- the source subsection `POLY-FUNCTION — finite-field functions do not identify formal polynomials` in `research/cryptographic_assumption_attack_corpus_20261101/README.md`.

I then recorded the following derivation before inspecting the proof module.

## Blind derivation

Let

`P := X^2 - X : (ZMod 2)[X]`.

1. **Formal nonzeroness.** Compare the coefficient at exponent `2`. The coefficient of `X^2` there is `1`, while the coefficient of `X` there is `0`, so `P.coeff 2 = 1`. Since `ZMod 2` is nontrivial, this coefficient is nonzero and therefore `P != 0` as a formal polynomial.
2. **Zero induced function.** For each `x : ZMod 2`, either enumerate the two elements or use the field identity `x^2 = x`. Evaluation gives `P.eval x = x^2 - x = 0`.
3. **Repair.** For a finite field `F`, suppose `P : F[X]`, `P.natDegree < Fintype.card F`, and every `x : F` is a root. If `P != 0`, the root-count theorem bounds the number of distinct roots by `P.natDegree`, while the hypothesis supplies all `Fintype.card F` field elements as distinct roots. Thus `Fintype.card F <= P.natDegree`, contradicting the strict degree bound. Hence `P = 0`.
4. **Negative control.** Removing the strict degree hypothesis must make the repair false. For arbitrary finite `F`, `X^(Fintype.card F) - X` is formally nonzero (its degree is the field cardinality, which is at least `2`) but evaluates to zero everywhere by finite-field Frobenius. This witnesses pointwise function equality without formal polynomial equality.

## Snapshot, hashes, and sources

The review used `git show` at the assigned commit. The relevant working-tree inputs had no delta from that commit when checked.

| artifact | frozen SHA-256 |
| --- | --- |
| `formal/targets/attack-polynomial-function-alias.yaml` | `d7beb7c95e6588ba70b0bf64346854367f859eb6b23ef0e9fb62a85a4d023760` |
| `formal/CryptoResearch/AttackCorpus/PolynomialFunctionAlias.lean` | `a8eefb2b425b7148b789eaa552008241ce62d7fc7b58ce5faf8c6b6be324a503` |
| source README | `a96c1ba72851c01501622503443ea7094557f1b2aa9e7b5c0bfc5641de095bc6` |
| `formal/lean-toolchain` | `ca5f1f601d34c49079e38d7e7041eb0f2a9c227fbc1df0f404820069a052330c` |
| `formal/lake-manifest.json` | `b46170db7f5631f573ff808cf1bc53655f3bd5385aeecc717c009a42dc01cec7` |

Sources read were the assigned YAML, only the named `POLY-FUNCTION` source subsection before derivation, the review plan and pin metadata, the assigned producer module, and the directly used Mathlib finite-field and polynomial-roots reference lemmas. No sibling proof module or sibling review was read.

## Hypothesis delta

| joint | frozen requirement | producer declaration | delta |
| --- | --- | --- | --- |
| counterexample carrier | exactly `ZMod 2` | exactly `ZMod 2` | none |
| formal witness | `X^2 - X != 0` in the polynomial ring | identical proposition in `Polynomial (ZMod 2)` | none |
| semantic witness | zero evaluation at every base-field point | `forall x : ZMod 2, (...).eval x = 0` | none |
| repair carrier | arbitrary finite field | `{F} [Field F] [Fintype F]` | none |
| repair object | univariate formal polynomial | `P : F[X]` | none |
| degree boundary | strict `P.natDegree < card F` | explicit premise with exactly that inequality | none |
| evaluation premise | every `x : F` is a zero | explicit `forall x : F, P.eval x = 0` | none |
| conclusion | formal equality `P = 0` | exactly `P = 0` | none |

`Function.injective_id` only witnesses that the `card F` evaluation points are distinct; it adds no hypothesis. The theorem introduces no multivariate, commitment, quotient, or protocol premise or conclusion.

## Controls

- The exact assigned source passed a Lean/Mathlib `v4.34.1` proxy compile. Its only diagnostic was an `unnecessarySimpa` linter warning.
- The nonzeroness branch proves formal polynomial nonzeroness independently of the pointwise vanishing branch over exactly `ZMod 2`.
- A separate generic proxy control established, for every finite field `F`, both `(X^(card F) - X : F[X]) != 0` and pointwise-zero evaluation, plus `natDegree (X^(card F) - X) = card F`. Thus removing the strict bound admits the standard counterexample exactly at the boundary.
- Function extensionality turns pointwise zero into equality of the induced function with the zero function, while formal nonzeroness simultaneously rules out polynomial equality. The two notions are not conflated.

## Machine evidence

Status remains `not_verified`: the frozen toolchain is `leanprover/lean4:v4.35.0`, while the local proxy was Lean/Mathlib `v4.34.1`. The source and generic negative control passed that proxy, but it is non-authoritative. Proxy `#print axioms` reported only `propext`, `Classical.choice`, and `Quot.sound` for both producer theorems. A scoped scan found no `sorry`, `admit`, explicit `axiom`, `unsafe`, or `implemented_by`. The exact 4.35 build, named-declaration audit, and fail-closed receipt remain pending elsewhere.

## Proof fidelity

The counterexample and repair faithfully match the frozen claim. The repair keeps the strict natural-degree premise, quantifies over every base-field element, and concludes formal polynomial equality only inside that bounded theorem. File comments correctly disclaim polynomial-commitment and protocol semantics.

One traceability limitation does not break the proof: the YAML's single `theorem_name` freezes only `nonzero_polynomial_zero_function`; the required repair is present as adjacent theorem `degree_bounded_zero_function_is_zero`, but is not separately named for an exact named-declaration check.

## Missing bridges and exclusions

There is no refinement from a protocol's committed object, evaluation domain, quotient constraints, SRS, or opening verifier to `Polynomial F` and base-field evaluation. Multivariate degree notions, extension-field domains, quotient rings, lookup arguments, and committed-polynomial interfaces remain excluded. The exact pinned machine receipt is also outstanding. No commitment break or proof-system security conclusion follows from this scoped theorem alone.

## Final attestation

`holds`

## Correction-round addendum

### Bound correction snapshot

- Correction plan commit: `0e096a9d9889c5eb7f74e4142cb55b0cdde1f2bf`
- Corrected producer commit: `37cc75cfebb30c7582e90e3b632d3454ff5804dc`
- Corrected producer tree: `e243b992c16f79a68277320be130b485fc0035b2`
- Corrected `PolynomialFunctionAlias.lean` SHA-256: `2f75204ec9aa9269f21bedd1d38f34ed44b6451eba46d0928ae461367662ae10`
- Frozen target remains `CryptoResearch.AttackCorpus.PolynomialFunctionAlias.nonzero_polynomial_zero_function`; the assigned YAML has no delta from the original producer commit.

I re-read only the assigned `f5a8f8a..37cc75c` module diff and the corrected full module. No sibling proof module or sibling review was read.

### Delta and named-target coverage

The reusable repair theorem is unchanged in hypotheses and conclusion: for every `{F}` with `[Field F] [Fintype F]`, every `P : F[X]` satisfying the strict premise `P.natDegree < Fintype.card F` and pointwise vanishing still concludes `P = 0`.

The correction moves that reusable theorem before the audited declaration and strengthens the exact named target from the counterexample pair to a bundle containing:

1. formal nonzeroness of `X^2 - X` in `(ZMod 2)[X]`;
2. zero evaluation at every `x : ZMod 2`; and
3. the universally quantified finite-field strict-degree repair.

The bundled repair delegates to the unchanged reusable theorem. No field, polynomial, evaluation, degree, or quantifier hypothesis is weakened. In particular, the strict `< Fintype.card F` boundary remains syntactically inside the exact target type.

This resolves the original theorem-name traceability gap: auditing the frozen `theorem_name` can no longer accept the counterexample while silently omitting the requested repair. The earlier traceability-limitation paragraph is therefore superseded by this addendum.

### Machine status and residual gaps

Machine status remains `not_verified` pending the exact Lean `v4.35.0` receipt. The correction-round Lean/Mathlib `v4.34.1` proxy passed with only the same `unnecessarySimpa` warning; it remains non-authoritative.

Residual gaps are unchanged and external to the corrected formal statement: there is still no refinement for committed polynomials, protocol evaluation domains, quotient constraints, SRS or opening verification, multivariate degree notions, extension-field domains, quotient rings, or lookups. The generic `X^(card F) - X` negative control still shows why the strict degree premise is necessary. No polynomial-commitment or proof-system security conclusion follows.

### Updated attestation

`holds`
