# Independent review C: cofactor scalar image, fibres, and pushforward scope

Task: `TASK-20261102-00e54b`  
Joint: `C` only  
Verdict: **holds**, as a source-level semantic-fidelity verdict.  
Machine status: **pending** on exact Lean run `41503944712`; this report does not claim kernel verification or a completed axiom audit.

## Bound claim and inputs

The review head is `fbb6c5d6f8bbae160e51404172996c837efb0a07`; the producer snapshot is `674b3248a8b007748a2cf4f10e5063e7de123be4`. The producer snapshot is an ancestor of the review head, and the target spec, Lean source, and tranche-two README have identical SHA-256 hashes at both revisions.

| Input | SHA-256 |
|---|---|
| `docs/reports/2026-11-02-attack-corpus-next-five-lean/review-plan.yaml` | `7a55598bad9dddb2f6b462fa981d6f4afb7e17871c417174692f1c3201f1f77f` |
| `formal/targets/attack-cofactor-pushforward.yaml` | `4313d96609a4335cdab3da50a5bf3bb07cac3727f80652e312a80b26d8109ff4` |
| `formal/CryptoResearch/AttackCorpus/CofactorPushforward.lean` | `c28754bcf4568282f3524633bbfbbbc29e8ce432cd9068f2cecbdc3d072b90ca` |
| `research/cryptographic_assumption_attack_corpus_tranche2_20261102/README.md` | `4834787c796eec875c33ca16ad75801c99102b31bbc565e0694311cc63b70a68` |
| RFC 9380 text, retrieved from `https://www.rfc-editor.org/rfc/rfc9380.txt` | `a2e6ab02b2117d6f52ac293020857752972b2e23ae005c33f612e40436ff4b6d` |
| `formal/lean-toolchain` (`leanprover/lean4:v4.35.0`) | `ca5f1f601d34c49079e38d7e7041eb0f2a9c227fbc1df0f404820069a052330c` |
| `formal/lake-manifest.json` | `b46170db7f5631f573ff808cf1bc53655f3bd5385aeecc717c009a42dc01cec7` |

The exact audited declaration is `CryptoResearch.AttackCorpus.CofactorPushforward.cofactor_failure_and_product_fiber_repair` at source lines 140–173. It conjoins the bad finite control, the good finite control, and the generic repair; it does not silently verify only one of them. A static scan of this source found no `sorry`, `admit`, custom `axiom`, or `unsafe` declaration. That scan is not a substitute for run `41503944712`, the exact named-declaration audit, or `#print axioms`.

## Exact finite maps and fibres

All residues below use their canonical representatives.

### Bad control: `ZMod 2 × ZMod 2`

Here `badClear(k,s) = (2k,2s) = (0,0)`.

| input | output |
|---|---|
| `(0,0)` | `(0,0)` |
| `(0,1)` | `(0,0)` |
| `(1,0)` | `(0,0)` |
| `(1,1)` | `(0,0)` |

The intended target copy is `{0} × ZMod 2 = {(0,0),(0,1)}`. Its fibres are

| target | exact fibre | size |
|---|---|---:|
| `(0,0)` | all four inputs | 4 |
| `(0,1)` | empty | 0 |

Thus the image is `{(0,0)}`, not the intended two-point target. The statement should be read as failure of surjectivity and uniformity **on that intended target**. The point mass is, trivially, uniform on its actual singleton image; the source does not need or support the stronger claim that every collapsed image is itself “nonuniform.” This is consistent with source lines 145–147.

### Good control: `ZMod 2 × ZMod 3`

Multiplication by two kills `ZMod 2` and permutes `ZMod 3` by `0 ↦ 0`, `1 ↦ 2`, `2 ↦ 1`.

| input | output |
|---|---|
| `(0,0)` | `(0,0)` |
| `(0,1)` | `(0,2)` |
| `(0,2)` | `(0,1)` |
| `(1,0)` | `(0,0)` |
| `(1,1)` | `(0,2)` |
| `(1,2)` | `(0,1)` |

The exact target fibres are

| target | exact fibre | size |
|---|---|---:|
| `(0,0)` | `{(0,0),(1,0)}` | 2 |
| `(0,1)` | `{(0,2),(1,2)}` | 2 |
| `(0,2)` | `{(0,1),(1,1)}` | 2 |

Consequently the image is exactly `{0} × ZMod 3`, and for every target `2 · 3 = 6 = |ZMod 2 × ZMod 3|`. The map is neither an ambient bijection nor an idempotent retraction: applying it twice sends the second coordinate `s` to `4s = s`, while applying it once sends it to `2s`, so the two differ at `s = 1,2`.

## Generic image and fibre audit

Write

```text
e : S -> S,       e(s) = h • s,
F_t = { (k,s) in K × S | h • (k,s) = (0,t) }.
```

`hperm` makes `e` an equivalence. The private equivalence at source lines 38–60 is exactly

```text
Phi_t : F_t -> K,       Phi_t((k,s), proof) = k,
Psi_t : K -> F_t,       Psi_t(k) = ((k, e^{-1}(t)), proof).
```

Both directions check:

1. `Psi_t` is well-defined because `hkill(k)` gives the first coordinate `0`, and `e(e^{-1}(t)) = t` gives the second.
2. `Phi_t(Psi_t(k)) = k` definitionally.
3. If `P = ((k,s), hs)` lies in `F_t`, the second-coordinate projection of `hs` gives `e(s) = t`. Since `e` is injective and `e(e^{-1}(t)) = t`, `e^{-1}(t) = s`; hence `Psi_t(Phi_t(P)) = P` as a subtype.

The image equality at lines 79–93 also holds in both directions:

```text
h • (k,s) = (0,e(s)) = productTarget(e(s))
productTarget(t) = h • (0,e^{-1}(t)).
```

The first direction uses `hkill(k)`; the reverse direction uses `hkill(0)` and surjectivity of `e`. The fibre equivalence then gives `|F_t| = |K|`. Together with `|K × S| = |K| |S|`, it gives the exact division-free identity

```text
fiberCount(productClear h, productTarget t) * |S| = |K × S|.
```

No denominator, coprimality inference, or unstated cancellation is used.

## Removing the load-bearing premises

These are mathematical controls, not additional Lean runs.

### Remove `hkill`, retain `hperm`

Take `K = S = ZMod 3` and `h = 2`. Multiplication by two is a permutation on `S`, so `hperm` holds, but it does not annihilate `K`. The product map is a bijection on all nine points, so its image is the whole product rather than `{0} × S`. The target fibres are

| target | exact fibre | actual size | claimed size `|K|` |
|---|---|---:|---:|
| `(0,0)` | `{(0,0)}` | 1 | 3 |
| `(0,1)` | `{(0,2)}` | 1 | 3 |
| `(0,2)` | `{(0,1)}` | 1 | 3 |

The cardinal identity becomes `1 · 3 = 3`, not `|K × S| = 9`. Thus `hkill` is load-bearing for the image, fibre size, and cardinal clauses.

### Remove `hperm`, retain `hkill`

Take `K = S = ZMod 2` and `h = 2`. The scalar annihilates `K`, but its action on `S` is constant, not bijective. This is the bad table above: target fibres have sizes `4` and `0`, not `|K| = 2`, and the image omits `(0,1)`. Thus `hperm` is load-bearing.

In the proof, surjectivity of `hperm` supplies a preimage for every target and proves the reverse image inclusion; injectivity makes the second fibre coordinate unique. For a finite self-map either injectivity or surjectivity implies bijectivity, but the two logical uses remain distinct.

### Retain both algebraic premises, remove uniform ambient sampling

In the good `ZMod 2 × ZMod 3` model, let the input distribution be a point mass at `(0,0)`. The output is then a point mass at `(0,0)`, not uniform on the three-point target, even though all set-theoretic fibres have size two. By contrast, a uniform ambient input gives probability `2/6 = 1/3` to each target point.

Therefore uniform ambient input is not a hidden algebraic hypothesis of the fibre theorem—it makes no probabilistic statement—but it is an indispensable premise of the uniform-distribution corollary. It is explicit in the target proof map and tranche-two README. Applying the result to a concrete encoder additionally requires a proved bridge from that encoder’s output distribution to the uniform counting measure on `K × S`; no such bridge is present here.

## Typeclass and hypothesis delta

| Binder or fixed condition | Function in the theorem | Relation to the source claim |
|---|---|---|
| `{K S : Type*}` | Abstract factors | Matched. The source deliberately supplies abstract factors rather than a curve. |
| `[AddCommGroup K] [AddCommGroup S]` | Zero, componentwise natural scalar action, group structure | Matched to the finite additive/elliptic-curve group scope. It is conservative and stronger than the proof machinery actually needs; no extra conclusion is obtained from commutativity or inverses. |
| `[Fintype K] [Fintype S]` | Finite fibres and cardinalities | Matched exactly to “finite additive groups.” Additive groups are nonempty through `0`; no empty-type case is hidden. |
| `[DecidableEq K] [DecidableEq S]` | Makes the `Finset.filter` definition of `fiberCount` executable on the product codomain | Constructive implementation scaffolding. Finite mathematical groups have decidable equality classically; this adds no cryptographic premise. |
| `h : Nat` | Natural scalar multiplication | Matched. No positivity is assumed; the conditional theorem remains true in any degenerate case satisfying `hperm`. It does not infer that an integer called a cofactor satisfies the other premises. |
| `hkill : forall k, h • k = 0` | Collapses the first factor | Matched exactly and shown load-bearing above. |
| `hperm : Bijective (s -> h • s)` | Supplies and uniquely identifies the second coordinate | Matched exactly and shown load-bearing above. It is the target-action invertibility premise; no separate gcd claim is smuggled in. |
| Fixed ambient representation `K × S`, fixed target embedding `s -> (0,s)` | Identifies the kernel-like and target factors | Explicit scoping prerequisite in the target. The theorem proves no decomposition of any concrete curve group. |
| Uniform distribution on the full ambient product | Needed only to turn counts into target probabilities | Not a theorem binder because the declaration states counts, not probability. It is explicit in the prose corollary and is not established for any encoder. |

The helper definitions use only `[Fintype A] [DecidableEq B]` for `fiberCount`, `[AddMonoid K] [AddMonoid S]` for `productClear`, and `[Zero K]` for `productTarget`. The audited theorem strengthens these to finite additive commutative groups. `productFiberEquiv` is marked `noncomputable` only to package a bijective function as an equivalence; this is not an `unsafe` declaration or a computational encoder.

There are no hidden field, characteristic, curve, subgroup-order, nontriviality, coprimality, or `h_eff = h` hypotheses. Their absence is a scope boundary, not evidence that a concrete suite satisfies the abstract premises.

## Exact RFC 9380 comparison

I read the primary RFC text, Sections 2–3 and 7, at the URL and hash bound above.

| RFC 9380 statement | Relationship to this target |
|---|---|
| Section 2.1 defines a curve group of order `n = h r`, a prime-order subgroup `G`, and cofactor clearing as mapping an arbitrary curve point into `G`. | The RFC does not say that this map is surjective onto `G`, has constant fibres, or uniformizes its input. In the bad control, `[2]P = 0` still lands in the intended order-two subgroup; failure to cover its nonzero point does not refute the RFC definition. |
| Section 3 defines `encode_to_curve` as `hash_to_field(msg,1)`, then `map_to_curve`, then `clear_cofactor`, and explicitly says its output is nonuniform: only a fraction of `G` may occur and probabilities may differ. | This directly blocks the straw-man inference that cofactor clearing alone makes this encoder uniform. Equal fibres under uniform ambient counting say nothing about the distribution of `map_to_curve(hash_to_field(msg,1))`. |
| Section 3 defines `hash_to_curve` using two field elements, two mapped points, addition, and then clearing; its output is statistically close to uniform in `G`. | The near-uniformity belongs to the complete construction and its assumptions. The Lean theorem proves neither statistical closeness nor indifferentiability and does not instantiate this pipeline. |
| Section 7 says scalar multiplication by `h` always clears the cofactor, while fast methods may be equivalent to multiplication by a configured `h_eff`. When such a fast method is used, multiplication by `h` generally gives a different result and must not replace it. | The generic Lean scalar `h` can model any scalar only after `hkill`, `hperm`, and the product decomposition are separately proved. It neither asserts `h_eff = h` nor certifies any suite’s configured `h_eff`. |

The target is therefore a valid guardrail against an overbroad uniformization inference. It is not a counterexample to RFC 9380, an audit of a concrete suite, a hash-to-curve distribution proof, or a protocol-security claim.

## Verdict

Joint C **holds** at source-level semantic fidelity:

- the two finite controls have the stated images and exact fibres;
- the generic fibre equivalence works in both directions;
- the image equality and cardinal identity follow under exactly the named product, annihilation, bijectivity, finiteness, and decidable-equality scope;
- removing either algebraic premise produces a smallest clear failure, and removing uniform ambient sampling defeats only the probabilistic corollary;
- the RFC comparison is narrow and accurate, including `encode_to_curve` nonuniformity and the distinction between `h` and `h_eff`.

This is not yet `validated_scoped`: exact run `41503944712`, the named-declaration audit, and the axiom audit remain pending. No source, spec, or producer artifact was edited; no sibling reviewer output was consulted.
