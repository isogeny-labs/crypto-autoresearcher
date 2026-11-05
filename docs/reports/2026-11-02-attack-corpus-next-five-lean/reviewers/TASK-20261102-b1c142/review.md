# Independent review — joint E: Pedersen relation kernel

## Verdict and scope

**Joint E breaks as delivered.** At review head
`fbb6c5d6f8bbae160e51404172996c837efb0a07`, the intended mathematics in
`PedersenRelationKernel.lean` has the right kernel, equivocation sign,
collision denominator, recovered-`alpha` sign, and `ZMod 5` arithmetic.
However, exact Lean 4.35 run `41503944712` failed to elaborate the concrete
control at source lines 123/125: the unannotated pairs in the
`commitmentMap` equality led Lean to seek `Field Nat`. The module did not
build, target verification and the axiom audit were skipped, and the exact
audited declaration is not formally discharged.

The review plan permits no reviewer formal builds, and I ran none. Therefore:

| dimension | result |
| --- | --- |
| Joint-E verdict on the delivered artifact | `breaks` |
| Intended algebra, recomputed independently | `holds` |
| Machine status | `failed` |
| Semantic fidelity of the intended statement | `faithful_scoped` |
| Full formal-review outcome | `needs_revision` |

The target does **not** establish computational binding, a DLP algorithm, a
concrete curve/subgroup refinement, or the uniform-hiding clause of
Pedersen's Theorem 3.1.

## Bound inputs

- Review plan SHA-256:
  `7a55598bad9dddb2f6b462fa981d6f4afb7e17871c417174692f1c3201f1f77f`.
- Producer snapshot:
  `674b3248a8b007748a2cf4f10e5063e7de123be4`.
- Frozen target SHA-256:
  `73f3d6e4cf64f14906a113176614dcbad26431cd08d5598a70644b8f9797538d`.
- Lean source SHA-256:
  `1b491e1005822c1dca4b38e15c98d427a14c6572c0e12c121235d1ed08c1d6da`.
- Tranche-two source note SHA-256:
  `4834787c796eec875c33ca16ad75801c99102b31bbc565e0694311cc63b70a68`.
- Pedersen publisher PDF SHA-256:
  `79c0634a04b7bc869715770519eca9dcfcb3011012dbff054b9487b187558b18`.
- GitHub Actions formal-workspace job-log SHA-256:
  `988ca37064f5422f1736a7506d297aa2375c0c83440e38a1985d8c5e16905efe`.

The target and Lean source have the same hashes at the producer snapshot and
the review head. A static scan of the reviewed source text found no literal
`sorry`, `admit`, custom `axiom`, `unsafe`, or `native_decide` token. The
failed elaboration nevertheless produced an unsolved goal and Lean reported
that `concrete_zmod_five_control` used `sorry`; thus the static token scan did
not establish a proof. The exact run is bound to producer snapshot
`674b3248a8b007748a2cf4f10e5063e7de123be4`, used Lean 4.35.0, and failed in
formal-workspace job `125478457720`.

## Exact machine failure

The relevant job log reports:

```text
error: CryptoResearch/AttackCorpus/PedersenRelationKernel.lean:123:4:
  failed to synthesize instance of type class Field Nat
error: CryptoResearch/AttackCorpus/PedersenRelationKernel.lean:123:31:
  failed to synthesize instance of type class Field Nat
error: CryptoResearch/AttackCorpus/PedersenRelationKernel.lean:125:64:
  unsolved goals
warning: CryptoResearch/AttackCorpus/PedersenRelationKernel.lean:126:12:
  declaration uses `sorry`
```

In `concreteZModFiveControl`, `G`, `H`, and `alpha` are typed as `ZMod 5`, and
the inequality explicitly types one pair as `ZMod 5 × ZMod 5`. That type does
not propagate across the later conjunction into
`commitmentMap G H (0,0) = commitmentMap G H (2,4)`. Lean infers the
unannotated pair coordinates there as naturals and consequently asks for an
impossible `Field Nat` instance. The arithmetic proposition is sound, but
this source does not prove it.

A likely repair is to give both commitment-map arguments the explicit type
`ZMod 5 × ZMod 5` (or otherwise explicitly bind the scalar field to
`ZMod 5`). That is a producer change requiring a new immutable source version,
fresh exact verification, and affected-joint re-review; this review does not
assume the repair works.

## Independent symbolic recomputation

Let

```text
Phi(m,r) = m • G + r • H,
H = alpha • G.
```

Associativity and distributivity of scalar multiplication give

```text
Phi(m,r)
  = m • G + r • (alpha • G)
  = (m + r*alpha) • G.                         (1)
```

If `a |-> a • G` is injective, comparison with `0 • G` turns (1) into

```text
(m,r) in ker(Phi)  <->  m + r*alpha = 0.        (2)
```

Thus the complete kernel is

```text
ker(Phi)
  = {(-r*alpha, r) : r in F}
  = {t*(alpha,-1) : t in F}.
```

In the second form take `t=-r`. In particular, `(alpha,-1)` is a kernel
vector because `alpha + (-1)*alpha = 0`. It is nonzero. Under the target's
`alpha != 0` premise the first coordinate already proves this; in fact the
pair would remain nonzero even at `alpha=0` because `-1 != 0` in a field.

### Equivocation sign

For a requested message `m'`, equality of openings requires

```text
m + r*alpha = m' + r'*alpha.
```

Because `alpha != 0`, solving for the new blinder gives

```text
r' = r + (m-m')/alpha.                           (3)
```

Substitution checks the sign:

```text
m' + (r + (m-m')/alpha)*alpha
  = m' + r*alpha + m - m'
  = m + r*alpha.
```

Equivalently, the opening displacement is

```text
(m',r')-(m,r)
  = ((m'-m)/alpha) * (alpha,-1),
```

so it lies in the kernel found above.

### Collision denominator and recovered relation

For a collision with `m != m'`, injectivity yields

```text
m + r*alpha = m' + r'*alpha,
m-m' = (r'-r)*alpha.                             (4)
```

If `r'=r`, (4) gives `m=m'`, a contradiction. Hence `r'-r != 0`, and

```text
alpha = (m-m')/(r'-r).                           (5)
```

Both the numerator and denominator signs in the Lean declaration are
therefore correct. Reversing both signs would be equivalent; reversing only
one would be wrong.

## Complete `ZMod 5` control

For `G=1`, `H=2`, and `alpha=2`, scalar multiplication is ordinary
multiplication modulo five and

```text
Phi(m,r) = m + 2r (mod 5).
```

The full kernel enumeration is:

| `r` | `2r mod 5` | required `m=-2r mod 5` | kernel pair `(m,r)` |
| ---: | ---: | ---: | ---: |
| 0 | 0 | 0 | `(0,0)` |
| 1 | 2 | 3 | `(3,1)` |
| 2 | 4 | 1 | `(1,2)` |
| 3 | 1 | 4 | `(4,3)` |
| 4 | 3 | 2 | `(2,4)` |

This is exactly the five-element span of `(2,-1)=(2,4)`. The concrete
openings in the Lean control satisfy

```text
Phi(0,0) = 0,
Phi(2,4) = 2 + 2*4 = 10 = 0 (mod 5).
```

They have different messages and blinders. Formula (5) recovers

```text
(0-2)/(4-0) = 3/4 = 3*4 = 12 = 2 (mod 5),
```

because `4^{-1}=4`. This recovers the declared `alpha=2` with the exact Lean
sign convention.

Mathematically, the intended instance also satisfies the outer injectivity
premise: `a • 1 = a`, so `a |-> a • G` is the identity map. Once correctly
typed, the example would witness a satisfiable instance of all mathematical
premises, not just a coincidental collision. As committed, though, the closed
control does not elaborate and witnesses nothing to the Lean kernel.

## Load-bearing-premise controls

### Remove `alpha != 0`

Take `F=V=ZMod 5`, `G=1`, `H=0`, and `alpha=0`. The scalar action by `G`
is still injective and `H=alpha • G`.

- The kernel characterization survives: `Phi(m,r)=m`, so the kernel is
  `{(0,r)}` and equation (2) reduces to `m=0`.
- `(0,-1)` remains a nonzero kernel vector.
- Different-message collisions are impossible under injectivity, so the
  collision-recovery implication survives only vacuously.
- Arbitrary-message equivocation fails. For `m=0`, `r=0`, and `m'=1`, Lean's
  totalized field division has `(-1)/0=0`; the proposed new blinder is still
  zero, while `Phi(0,0)=0 != 1=Phi(1,0)`.

Thus `alpha != 0` is load-bearing for formula (3) and for `H` being nonzero,
but not for (2), collision extraction conditional on an actual collision, or
the nonzeroness of the particular vector `(alpha,-1)`.

### Remove injective scalar action

Take `F=V=ZMod 5`, `alpha=2`, and `G=H=0`. Then `alpha != 0` and
`H=alpha • G`, but the scalar action by `G` is not injective.

- `Phi` is the zero map, so its kernel has all 25 pairs. The claimed equation
  describes only five; for example `(1,0)` is in the kernel although
  `1+0*2 != 0`.
- `(0,0)` and `(1,0)` are a different-message collision with equal blinders,
  directly falsifying the recovery conclusion `r' != r`.
- Relation membership and the equivocation equality still hold (the latter
  trivially), showing exactly which directions use injectivity.

Over a module for a field, injectivity of `a |-> a • G` is equivalent to
`G != 0`. In Pedersen's concrete prime-order group, the corresponding fact is
that `g` has exact order `q`; the Lean target assumes this bridge rather than
formalizing it.

## Hypothesis delta and model boundary

Relative to the frozen tranche-two claim and target YAML, the elaborated
declaration adds no unstated binder, typeclass, `Fact`, or side condition:

| Lean input | frozen claim | assessment |
| --- | --- | --- |
| `[Field F]` | “Let `F` be a field” | implied |
| `[AddCommGroup V] [Module F V]` | “`V` an `F`-module” | implied |
| `G H : V`, `alpha : F` | explicitly named | implied |
| `hAlpha : alpha != 0` | “nonzero `alpha`” | implied |
| `hH : H = alpha • G` | explicitly stated | implied |
| injectivity of `a |-> a • G` | explicitly stated | implied |

The correspondence to Pedersen's concrete scheme is deliberately narrower:

| bridge to the paper | status |
| --- | --- |
| Instantiate `F` as `Z_q` for prime `q` | stated in Pedersen Section 2; not instantiated in Lean |
| Equip the order-`q` cyclic group with its `Z_q` scalar action | standard bridge; not constructed in Lean |
| Derive scalar injectivity from `g` having exact order `q` | implied after that bridge; assumed in Lean |
| Identify `alpha` with `log_g(h)` | existence/uniqueness follows from cyclicity; supplied explicitly in Lean |
| Express that nobody can efficiently compute `alpha` | absent by design; Lean has no adversary/game/runtime |
| Uniform hiding for random `t` | first clause of Theorem 3.1; outside this target |

Accordingly, the declaration is `faithful_scoped` to its frozen abstract
claim, but it is not a complete formalization of Pedersen's theorem or scheme.

## Primary-source and straw-man audit

I retrieved the Springer publisher PDF of Torben Pryds Pedersen,
“Non-Interactive and Information-Theoretic Secure Verifiable Secret Sharing,”
CRYPTO '91, LNCS 576, pp. 129–140, DOI
`10.1007/3-540-46766-1_9`. Its SHA-256 exactly matches the tranche note:
`79c0634a04b7bc869715770519eca9dcfcb3011012dbff054b9487b187558b18`.

Section 2 fixes primes `p,q` with `q | p-1`, the unique subgroup `G_q` of
order `q`, and a generator `g`. It explicitly says discrete logarithms with
respect to any nonidentity base in this group are defined. Section 3 chooses
`g,h` so that nobody knows `log_g(h)` and defines
`E(s,t)=g^s h^t`. Theorem 3.1 then states:

1. `E(s,t)` is uniform in `G_q` for uniform `t`; and
2. if `s != s'` and `E(s,t)=E(s',t')`, then `t != t' (mod q)` and
   `log_g(h)=(s-s')/(t'-t) (mod q)`.

Under the additive translation

```text
g -> G,  h -> H,  log_g(h) -> alpha,
s -> m,  t -> r,
```

the second clause is exactly equations (4)–(5). One attribution nuance should
be preserved in synthesis: computational unknownness is stated in the Section
3 setup immediately before Theorem 3.1, rather than as a formal quantified
hypothesis inside the theorem's displayed statement. The setup plus theorem
nevertheless give precisely the boundary described by the tranche note.

The literature does **not** claim literal linear independence of two elements
of one cyclic prime-order group. On the contrary, the paper defines
`log_g(h)` and relies on its computational unknownness. The Lean result is
therefore not a counterexample to Pedersen. It is a counterexample only to the
external shorthand “independent generators” when that phrase is mistakenly
read as algebraic linear independence rather than unknown discrete-log
relation.

| statement | supported here? | reason |
| --- | --- | --- |
| Every pair `G,H` in the same prime-order cyclic group is algebraically related | yes, after the standard cyclic-group bridge | `H=alpha • G` for a unique scalar |
| A party given `alpha` can equivocate | yes | formula (3) |
| A different-message collision yields `alpha` | yes | formula (5), matching Theorem 3.1 |
| An outsider can compute `alpha` from `G,H` alone | no | that is the discrete-log problem |
| The formal target breaks Pedersen computational binding | no | no adversary, setup distribution, probability, runtime, or reduction is modeled |
| The target proves Pedersen hiding | no | random `t` and uniform distributions are absent |

## Final assessment

Joint E's intended algebra and scoped literature interpretation hold. The
load-bearing assumptions fail in the expected places, the finite arithmetic
is exact, and the source note correctly avoids a computational-security
conclusion. The only literature caveat is to attribute unknownness to the
Section 3 setup together with Theorem 3.1 and never portray Pedersen as making
the literal-independence claim.

The delivered formal artifact nevertheless **breaks**: exact run
`41503944712` failed on its `ZMod 5` control before target verification or an
axiom audit. It needs a typed concrete-domain repair and a fresh formal run;
the existing source cannot receive a machine-verified or `validated_scoped`
status.
