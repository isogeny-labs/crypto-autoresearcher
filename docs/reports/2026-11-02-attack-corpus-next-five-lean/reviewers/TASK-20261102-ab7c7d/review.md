# Reviewer D: constant-challenge Fiat--Shamir algebra

Task: `TASK-20261102-ab7c7d`  
Joint: `D`  
Review head: `fbb6c5d6f8bbae160e51404172996c837efb0a07`  
Producer snapshot: `674b3248a8b007748a2cf4f10e5063e7de123be4`  
Named declaration: `CryptoResearch.AttackCorpus.FiatShamirZeroHash.zero_hash_acceptance_and_nonzero_control`  
Machine status: **failed** (hosted Lean 4.35 run `41503944712`); this reviewer ran no local Lean build or scientific trial.

## Verdict

**D breaks for the submitted formal artifact.** The intended field-module algebra holds and is faithful to the source note at its narrow scope, but the named Lean declaration is not formally discharged: the exact hosted build failed in this module before target verification or axiom audit. The appropriate separated dimensions are therefore machine status `failed`, intended-statement fidelity `faithful_scoped`, and review outcome `needs_revision`.

This failure does not refute the mathematical equations derived below. Conversely, correct paper algebra cannot be reported as a verified Lean result when the submitted module does not compile.

The producer spec, Lean module, and tranche-two source at the review head have the same SHA-256 digests as their blobs at the producer snapshot. No later source bytes were substituted for the reviewed producer inputs.

## Machine failure on the exact producer snapshot

GitHub Actions run [`41503944712`](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41503944712), head `674b3248a8b007748a2cf4f10e5063e7de123be4`, completed with conclusion `failure`. In job `125478457720`, Lean 4.35 reported for this module:

- line 32: `unexpected token '⇒'; expected '↦', '=>'` in the `constantHash` lambda;
- lines 40 and 50: unsolved goals cascading from the malformed definition;
- lines 63, 65, 99, and 101: failure to synthesize `Field (ZMod 5)`, because the source supplies no `Fact (Nat.Prime 5)` instance;
- further unsolved goals and compiler-recovery `declaration uses sorry` warnings after those failures.

The workspace-build step failed, and the exact discharged-target verification/axiom-audit step was skipped. This is a source failure, not an infrastructure error. A repair would need a new producer version and a fresh verification receipt; this review does not edit the frozen source.

## Equation-by-equation audit

The model is exactly the proposition at `FiatShamirZeroHash.lean:23-27`:

```text
Accepts(H,m,G,X,R,s)  :=  s • G = R + H(m,R) • X.
```

### Zero challenge

Set `H(m,R)=0` and choose `R=s•G`. The right side is

```text
R + 0 • X = s • G + 0 = s • G,
```

for every `X`. No scalar witness for `X` occurs in the constructor. This is precisely the universally quantified helper at lines 36-41 and the first conjunct of the audited declaration at lines 94-95.

### Arbitrary known constant

For a constant challenge `c` known before the commitment is chosen, set

```text
R = s • G - c • X.
```

Then

```text
R + c • X
  = (s • G - c • X) + c • X
  = s • G.
```

This works whether `c` is zero or nonzero. Lines 46-51 prove exactly that statement for `constantHash c`; lines 96-97 carry it into the named declaration. The statement does not overgeneralize to an arbitrary nonconstant `H`, for which solving `R=s•G-H(m,R)•X` could be a fixed-point problem.

An explicit nonzero adaptive-commitment control over `ZMod 5` makes the quantifiers visible. Take `G=1`, `s=3`, and `c=2`. For the two nonzero public group elements

```text
X₀ = 1,  R₀ = 3 - 2*1 = 1;
X₁ = 2,  R₁ = 3 - 2*2 = 4.
```

Both equations accept:

```text
3 = 1 + 2*1,
3 = 4 + 2*2 = 8 = 3  (mod 5).
```

The commitments differ. Thus replacing zero by a known nonzero constant does not repair the construction, and this example does not contradict fixed-transcript uniqueness.

### Exact `ZMod 5` distinct-key conjunct

Lines 55-67, repeated literally at lines 98-102, fix `G=1`, `s=3`, `R=3`, `c=0`, `X₀=0`, and `X₁=1`. In `ZMod 5`,

```text
s • G = 3*1 = 3,
R + 0*X₀ = 3,
R + 0*X₁ = 3,
0 ≠ 1.
```

So the same `(m,G,R,s)` accepts both distinct group elements. One selected element is the additive identity. That is permitted by the declared module model, which has no key-validity predicate. It is not by itself a concrete Pointcheval--Stern key-generation example. The universal zero-challenge theorem also applies to two nonzero elements such as `1` and `2`, but concrete key generation, encoding, and subgroup validation remain unformalized as the target says.

### Fixed-transcript nonzero cancellation

Let `c=H(m,R)≠0`, and assume, for the same `m`, `G`, `R`, `s`, and `H`,

```text
s • G = R + c • X₀,
s • G = R + c • X₁.
```

Equating the right sides and cancelling `R` gives `c•X₀=c•X₁`. Because `F` is a field, `c` is a unit; scalar multiplication by `c⁻¹` gives `X₀=X₁`. This is the proof at lines 72-84 and the final implication at lines 103-106.

Both hypotheses are load-bearing:

- If `c=0`, the exact `ZMod 5` distinct-key example falsifies uniqueness.
- If nonzero is weakened from a field element to a nonunit in a ring, cancellation can fail. Over `ZMod 6`, `c=2`, `X₀=0`, and `X₁=3` give `2X₀=2X₁=0` with `X₀≠X₁`.
- If `R` may vary after seeing nonzero `c`, the preceding `ZMod 5` adaptive-commitment pair accepts for two distinct nonzero `X` values. The Lean theorem correctly fixes `R`.

## Clause fidelity

| Source obligation | Formal location | Result |
| --- | --- | --- |
| Zero constant accepts `R=s•G` for arbitrary `X` | lines 36-41; 94-95 | Exact |
| Any pre-known constant accepts `R=s•G-c•X` | lines 46-51; 96-97 | Exact |
| Same zero-hash transcript accepts two distinct elements over `ZMod 5` | lines 55-67; 98-102 | Exact; no concrete key-validity bridge |
| One fixed transcript plus nonzero challenge determines at most one `X` | lines 72-84; 103-106 | Exact |
| Keep all four facts in the named declaration | lines 89-114 | Exact conjunction |

The arbitrary `challenge` used by the constant-hash conjunct and the arbitrary `H` used by the fixed-transcript implication are intentionally separate. The source states two constructions and a separate control; it does not assert that this `challenge` equals `H m commitment`.

## Hypothesis-delta table

There are no source-unstated binders, instances, fixed parameters, or side conditions in the named declaration.

| Formal premise or binder group | Source support | Classification |
| --- | --- | --- |
| `F` with `[Field F]` | Target says “over any field” | implied |
| `A` with `[AddCommGroup A] [Module F A]` | Target says “field-module additive group” | implied |
| Message type, `H`, `m`, `G`, `R`, `X₀`, `X₁`, `s`, and constant `c` | These are exactly the verifier, transcript, public elements, response, and challenge quantified by the source claim | implied |
| `H m R ≠ 0` in the uniqueness implication | Source explicitly limits the algebraic control to a nonzero challenge | implied |
| `ZMod 5` constants in the finite conjunct | Source explicitly requests a concrete finite distinct-key control | implied |

Notably absent are assumptions that `G` is nonzero or generating, that `X` has a known discrete logarithm, that a parser accepts `X`, or that `H` is random. None is needed for the stated algebra, and none may be inferred from it.

## Fixed-equation uniqueness is not extraction

The Lean control fixes one challenge and one response and varies the public group element:

```text
(same H,m,G,R,s,c; X₀ and X₁)  ==>  X₀=X₁.
```

Schnorr special soundness and the Pointcheval--Stern fork instead fix one public key and commitment, while obtaining distinct challenges and generally distinct responses:

```text
(same public key and commitment; c₀≠c₁; s₀,s₁)  ==>  recover a witness scalar.
```

The Lean result recovers no scalar `x` with `X=x•G`; indeed no such scalar appears in its type. It supplies no second transcript, replay algorithm, success probability, query bound, or extractor. Even though a nonzero `c` makes the equation injective as a function of the group element `X`, an attacker targeting a pre-existing `X` can choose `R=s•G-c•X` when `c` is a public constant. Public-element uniqueness therefore gives no knowledge guarantee.

## Primary-literature comparison

I retrieved the publisher PDF through DOI <https://doi.org/10.1007/s001450010003> (`Security Arguments for Digital Signatures and Blind Signatures`, Journal of Cryptology 13 (2000), pp. 361-396). The retrieved PDF SHA-256 is `e9fd8e8213b725d9f16f915dce4d5f5a973a1a18c880fc286036df951c0a58d6`; it is a different binary from the author-hosted digest recorded in the tranche note.

The paper supports the tranche's boundary description:

- Section 1.1, p. 363, defines the random oracle as returning a truly random value on each new query and the same value when a query is repeated.
- Section 2.1, p. 371, describes replay with different random oracles to obtain signatures on the same message with the same first signature component/commitment and different hash values.
- Section 3, pp. 372-373, describes the Fiat--Shamir conversion as replacing the verifier's random challenge with `f(m,a)`, where commitment `a` is bound not to change.
- Lemma 8 and Theorem 10, pp. 373-376, assume a probabilistic polynomial-time forger making at most `Q` random-oracle queries and meeting a success threshold. The proof fixes the attacker's random tape and the oracle prefix before the selected query, then seeks the same commitment with a distinct challenge.
- Theorem 11, p. 377, applies that fork to Schnorr and derives the discrete logarithm from two same-commitment, distinct-challenge signatures.

A deterministic constant function is not the random-oracle experiment used by those results. The Lean construction therefore does not refute Pointcheval--Stern under its premises. The 2000 paper is a classical-ROM result and supplies no QROM claim; this finite constant-function construction is neither a ROM nor a QROM attack.

The tranche sentence that the example “refutes only the slogan that special soundness by itself implies Fiat--Shamir security” is acceptable only as an unnamed logical guardrail. The reviewed Pointcheval--Stern paper does not make that premise-free slogan: it supplies the missing random-oracle, query, replay, success, and computational assumptions. Accordingly, the source note correctly says that it does not refute the paper; the slogan must not be promoted into a literature finding attributed to Pointcheval--Stern.

## Missing bridges and non-implications

The theorem intentionally leaves all of the following outside its scope:

- message/transcript serialization and hash-domain separation;
- group decoding, subgroup membership, and key-validity checks;
- the relation between an abstract module element `X` and a witness scalar;
- random-oracle sampling, classical or quantum oracle access, and query bounds;
- an adversary, running time, success probability, rewinding, or forking;
- special-soundness or knowledge-extractor correctness;
- a reduction to discrete logarithm or a concrete implementation vulnerability.

Those are missing bridges to broader security claims, not defects in the intended algebraic statement. For the submitted artifact, however, the appropriate joint result is `breaks`, intended-statement fidelity `faithful_scoped`, machine status `failed`, and review outcome `needs_revision`. No `validated_scoped` or machine-verified conclusion is available from this version.
