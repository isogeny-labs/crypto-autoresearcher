# Boolean normalization: scoped formal result

Date: 2026-11-05. Producer task: `TASK-20261105-9e5cbb`.
Archive owner: `TASK-20261104-df29f3`.
Input/base commit: `047002010983c6deba923743bba110e45ef137dd`.
Source: `formal/CryptoResearch/FallDegree/BooleanNormalization.lean`.
Source SHA-256: `a7fde065840c9ad19c11932fb65f5747cc95eb75d799ae9de6ae059ca8d0ab8d`.

The source compiles, and all 31 theorem declarations have an exact-name axiom
audit. This is proof construction and machine verification at the statements
below; no independent semantic-fidelity review or scientific promotion is
asserted. No scientific trial, external model/API request, delegation, or
scientific status transition was performed. Source and logs are left for the
named archive owner to commit.

## Exact proved scope

Write `P = MvPolynomial σ k`, `FE = fieldEqGens σ k 2`, and
`NF = booleanNF`. Here `k` is any field and `σ` is arbitrary unless a finite
variable hypothesis is explicitly given. `FE` is exactly the set of
polynomials `X i ^ 2 - X i`. Coefficients remain in `k`, including in odd
characteristic. `V` is the ordinary iterated polynomial filtration from
`LastFall.lean`, with the strict sum-of-degrees multiplication condition.

`booleanExponent` replaces each exponent `a` by `min a 1`.
`booleanNF` is a `k`-linear map that sends `monomial s c` to
`monomial (booleanExponent s) c`.

| Exact declaration (namespace `CryptoResearch.FallDegree`) | Statement |
| --- | --- |
| `X_pow_sub_X_mem_V` | For `1 ≤ a`, `X i ^ a - X i ∈ V FE a`. |
| `monomial_boolean_repair_mem_V` | `monomial s 1 - monomial (booleanExponent s) 1 ∈ V FE (wt s)`. |
| `monomial_boolean_repair_coeff_mem_V` | The same repair with any coefficient `c : k`, at the same weight. |
| `boolean_repair_mem_V` | **For every polynomial `p`, `p - NF p ∈ V FE p.totalDegree`.** |
| `totalDegree_booleanNF_le` | `(NF p).totalDegree ≤ p.totalDegree`. |
| `booleanNF_idempotent` | `NF (NF p) = NF p`. |
| `mem_V_iff_booleanNF_mem_V` | If `p.totalDegree ≤ D`, then `p ∈ V (F ∪ FE) D ↔ NF p ∈ V (F ∪ FE) D`. |
| `booleanNF_mul_left`, `booleanNF_mul_right` | `NF (NF p * q) = NF (p * q)` and `NF (p * NF q) = NF (p * q)`. |
| `booleanNF_eq_zero_iff_mem_bit_ideal` | `NF p = 0 ↔ p ∈ Ideal.span FE`. |
| `mem_V_bit_iff_degree_and_booleanNF_eq_zero` | **For every `D`, `p ∈ V FE D ↔ p.totalDegree ≤ D ∧ NF p = 0`.** |

The last two identities concern actual formal polynomial ideal membership,
not merely equality on Boolean evaluations. The bounded identity includes
`D = 0, 1`; it assumes no artificial `D ≥ 2` exception.

The original-degree proof proceeds by the identity
`X^(a+1)-X = (X^a-X)*X + (X^2-X)`, Finsupp induction on exponent support,
coefficient-linear monomial repair, and summing over the original polynomial
support. Every intermediate multiplication is checked against its original
monomial weight. Consequently no factor of two is introduced in the degree
cap. The theorem gives bounded `V` membership, rather than explicit cofactor
polynomials `q_i` in a sum representation.

## Finite-variable last-fall upper bound

Assume `[Fintype σ]`, put `N = Fintype.card σ`, and retain the original raw
polynomial generator set `F`.

- `totalDegree_booleanNF_le_card` proves `deg (NF p) ≤ N` for every `p`.
- `booleanNF_mem_V_of_mem_ideal_span` proves that if `N+1 ≤ D` and every
  raw `f ∈ F` has degree at most `D`, then every
  `p ∈ Ideal.span (F ∪ FE)` satisfies `NF p ∈ V (F ∪ FE) D`.
- `lastFallSet_boolean_system` proves under those same hypotheses that
  `D ∈ lastFallSet (F ∪ FE)`. Thus every ideal consequence `p` is derivable
  at `max D p.totalDegree`. Finiteness of the last fall degree is established
  by this witness, not assumed.
- `lastFallDegree_boolean_system_le` gives `lastFallDegree (F ∪ FE) ≤ D`.
- `lastFallDegree_boolean_system_le_max_card_degree` states the explicit
  presentation-aware bound `lastFallDegree (F ∪ FE) ≤ max (N+1) B` when
  all raw input degrees are at most `B`.
- `lastFallDegree_boolean_system_le_card_succ` gives `≤ N+1` if
  `NF f = f` for every input generator.
- `booleanNF_eq_self_of_degreeOf_le_one` and
  `lastFallDegree_multilinear_system_le_card_succ` give that same `N+1`
  bound from the conventional multilinearity hypothesis
  `∀ f ∈ F, ∀ i, f.degreeOf i ≤ 1`.

The proof builds an actual polynomial ideal consisting of the polynomials
whose normal forms belong to `V (F ∪ FE) D`. Each normalized representative
has degree at most `N`, so its variable product fits cap `D ≥ N+1`.
Normalization multiplicativity then proves arbitrary polynomial multiplier
closure. Ideal-span inclusion gives every normal-form consequence, and the
original-degree repair lifts it back to the original polynomial at
`max D (deg p)`.

This is a generic variable-count upper bound. It is neither an exact value
nor a bound independent of the variable count. The raw input eligibility
hypothesis is essential to the stated proof: no unconditional removal of a
high-degree raw input by normalization is claimed.

## Verification and preserved attempts

Commands ran from `/workspace/crypto-autoresearcher/formal`:

```text
/home/agent/.elan/bin/lake build +CryptoResearch.FallDegree.FirstFallBounded
/home/agent/.elan/bin/lake build +CryptoResearch.FallDegree.BooleanNormalization
/home/agent/.elan/bin/lake env lean --stdin
```

The last command imports the built module, prints the axioms of every one of
its 31 theorem declarations, and checks the main theorem types. Its exact
input, source hash, output, and exit status are preserved in the final audit
log. Final build and final audit both exited zero.

- `normalization-dependency-build-01.log`: successful dependency build.
- `normalization-build-01.log`, `02`, `03`, `05`, `06`: preserved failed
  compilations while resolving API names, the wrapped polynomial coefficient
  representation, a bit-equation simplification, and scalar multiplication.
  Attempt `02` repeated the first source after an edit used the wrong working
  directory; the edit was corrected before attempt `03`.
- `normalization-build-04.log`, `07`, `08`: intermediate successful builds.
- `normalization-build-09.log`: final successful build, including the exact
  bounded bit-kernel identity. SHA-256:
  `65079e03b1c96aa9a5384afd2838a4b5e35e55ab0aa5a05da16e1f4c92ffd8a0`.
- `normalization-axiom-audit-01.log`: earlier successful audit, before the
  final three bit-kernel declarations were added.
- `normalization-axiom-audit-02.log`: final audit of all 31 declarations.
  SHA-256: `b231a447b99c5a5e9e5bcea091dc6a466ffc50a978969bac66231ec996ebde9e`.
- `normalization-validation-01.log`: exact versions, input hashes, final
  source hash, and zero matches for the forbidden-construct scan. SHA-256:
  `20bf27f83eb31127466b6ccf04df7cb2c7089dae58afef001dfc0252a1c2bab5`.

Every audited declaration depends only on Lean's standard logical axioms
`propext`, `Classical.choice`, and `Quot.sound`. There is no custom axiom,
proof hole, or unsafe declaration in the new source. The final build has the
existing Mathlib module-system import warnings; it has no proof errors.

Toolchain: `leanprover/lean4:v4.35.0`, Lean commit
`eb6cafb7290e8bd5f2937522d8d804f58f02bafc`; Lake
`5.0.0-src+eb6cafb`. Mathlib is pinned in `lake-manifest.json` to
`cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`, and the CryptoLean dependency to
`60952c696ded7f3da4f4517006d9af6482662487`.
`lean-toolchain` SHA-256 is
`ca5f1f601d34c49079e38d7e7041eb0f2a9c227fbc1df0f404820069a052330c`;
`lake-manifest.json` SHA-256 is
`b46170db7f5631f573ff808cf1bc53655f3bd5385aeecc717c009a42dc01cec7`.

## Sources checked and remaining gaps

- **Internal, read:** `analysis/boolean-fall-certificates-20261104/THEORY.md`,
  section 1, supplies the requested original-degree Boolean reduction and
  distinguishes raw from multilinear input eligibility.
- **Internal, read:** `FirstFallBounded.lean`, `LastFall.lean`, and
  `ClosureCertificates.lean` supply the actual `V` definition, weighted
  Finsupp infrastructure, and ordinary derivation-to-ideal lemma.
- **Retrieved primary source, read 2026-11-05:** Caminata--Gorla,
  <https://arxiv.org/html/2112.05579v2>, Definition 1.5 and adjacent text.
  Its vector-space closure agrees with the existing repository's strict
  sum-of-degrees implementation; the adjacent discussion distinguishes that
  iterated closure from an unaugmented Macaulay row space.
- **Retrieved local primary library source, read:** pinned Mathlib
  `Algebra/MvPolynomial/{Basic,Degrees}.lean`,
  `Data/Finsupp/{Defs,Basic}.lean`,
  `LinearAlgebra/Finsupp/LSum.lean`, and
  `Algebra/MonoidAlgebra/{Defs,Module}.lean`. These specify monomial
  linearity, total-degree bounds, and the actual wrapped coefficient
  representation used by this Lean version. No literature-priority claim
  is made.

The optional full arbitrary-system bridge to a separately defined strict
Boolean variable closure `W_D` at every cap is **not formalized here**.
`mem_V_iff_booleanNF_mem_V` is an equivalence inside the existing ordinary
closure, and the exact bounded kernel identity concerns the bit-equation
system. Neither is presented as an independently defined `W_D` theorem.
A future proof must separately define that closure and simulate arbitrary
ordinary polynomial multipliers by strict Boolean variable steps with every
intermediate degree budget checked.

No specific Semaev input, support-localized binary construction, binary
`3*ell+1` upper bound, growing lower bound, exact last fall degree, Gröbner
basis degree, or solving-degree comparison is proved by this module. Those
remain separate obligations; the formal result does not transfer a first-fall
statement into a last-fall or solving-degree statement.
