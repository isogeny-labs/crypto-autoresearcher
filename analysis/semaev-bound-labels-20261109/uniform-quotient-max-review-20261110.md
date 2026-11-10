# Independent high-scrutiny review of the uniform quotient obstructions

2026-11-10. Source-only mathematical review. No experiment, solver, closure
computation, certificate replay, build, or official scientific promotion.

**Verdict: the exponential rank bound, global-commutation obstruction, and
factorized-block obstruction are correct under their stated hypotheses.**
The binomial filtration-profile corollary requested during review is also
valid and is derived below. No growing lower-bound family is supplied by
these results.

Reviewed source versions, identified by SHA-256:

| Artifact | SHA-256 |
| --- | --- |
| `quotient-exponential-rank-review.md` | `25e1579ea27d9ae1b848ca60bf323e46fe1b41f5f056e4bb3a1165df9964cb03` |
| `uniform-quotient-operator-20261110.md` | `080e3dfaa5198aa4b1489e80e2da946e2b2edfd202d101ed712d65077fc0c4ed` |
| `uniform-quotient-algebraic-20261110.md` | `b52c9b6589470cb1fdb3e91385a0613e18723f0e90e5b2b338d2d60f777b5891` |
| `uniform-quotient-operator-review-20261110.md` | `945e9171cf66f50b6ae50f90d339352d87bc43f451e73db8ae480f8379a17398` |
| `uniform-quotient-algebraic-review-20261110.md` | `1c985bbc1bbde2730ca9ad57b18ff17e01ecb54974fc15c35185c71a4056062f` |

The finite feasibility contract was read for definitions. This is a separate
reviewer rederivation after reading the producer notes and their reviews,
not a blind review. No external lower-bound theorem is used.

## 1. Leading terms and the exponential rank bound

Let `C:B_(<=D)->Q` be surjective, `D>=2`, and `U=ker C`. Require that
every input generator is admitted at this cap and belongs to `U`, and that
`h*u in U` whenever `u in U` has normalized Boolean degree at most `D-1`.
For the UNSAT statement also require independent UNSAT and `C(1)!=0`.

Choose graded lexicographic order inherited from ordinary monomials. If
`LT(f)=m`, `deg m=d<D`, and `h` is absent from `m`, the term `h*m` has
degree `d+1`. Any term of `f` containing `h` has reduced product of degree
at most `d`; all remaining terms retain their relative order under ordinary
multiplicativity. None can collide with `h*m`. Thus
`LT(h*f)=h*m`, and closure makes the truncated leading-monomial set upward
closed. Its complement is a squarefree downset. Row reduction shows that
these standard monomials form a quotient basis. Degree compatibility also
shows that the standards of degree at most `a` form a basis of
`Q_a=C(B_(<=a))`.

The no-plateau argument works even when admitted inputs have degree greater
than two, provided their degree is at most `D`. Suppose
`Q_a=Q_(a+1)` for some `a<=D-2`. Define variable actions on `Q_a` using
representatives of degree at most `a`. Kernel closure makes them well
defined. Replacing higher-degree representatives by lower-degree ones and
multiplying each difference while its degree is at most `D-1` shows that
every `Q_b` with `a<=b<=D` equals `Q_a`. Multiplying the low representatives
twice is legal because `a+2<=D`; it proves global commutation and
idempotence. The vector `C(1)` is cyclic, and every admitted input kills it.
The resulting Boolean representation is supported on actual common zeros.
For UNSAT it must be zero, contradicting `C(1)!=0`.

In particular `Q_(D-2)` is properly contained in `Q_(D-1)`, so at least
one standard monomial `m` has degree `D-1`. All `2^(D-1)` divisors of `m`
are standard. Therefore the actual rank satisfies

```text
q = rank C = dim Q >= 2^(D-1).
```

The proof uses a multiplicative degree-compatible order, not an arbitrary
degree-sorted ordering. It uses full kernel closure, not merely the input
Macaulay rows. Excluded high-degree generators cannot be used in its UNSAT
premise. A declared codomain dimension is not a substitute for actual rank.

## 2. Derived binomial filtration-profile corollary

Put `Q_(-1)=0` and `h_a=dim Q_a-dim Q_(a-1)`. The same standard monomial
`m` has exactly `binom(D-1,a)` divisors of degree `a`. The filtered basis
identified above therefore gives, for every `0<=a<=D-1`,

```text
h_a >= binom(D-1,a),
dim Q_a >= sum_(i=0)^a binom(D-1,i).
```

No additional independence assumption is needed: distinct standard
monomials are already independent modulo `U`, including modulo lower
filtration levels. This is a constraint on every useful quotient's entire
low-degree profile, not just on its final rank.

Both bounds also hold if independent evidence excludes a global Boolean
quotient here: either a named `g` in the input ideal, `deg g<=D`, with
`C(g)!=0`, or actual rank exceeding a rigorous solution-count upper bound.
A plateau would annihilate every such `g` and have dimension at most the
actual solution count. Without that premise the conclusion is false: a
single evaluation at an actual solution is a closed rank-one quotient at
every cap. This is an explicit scope control, not a contradiction.

## 3. Global commutation alone is fatal to a useful obstruction

The operator note's assumptions are sufficient. Local multiplication at
`D>=2` gives `(T_h^2+T_h)C(1)=0`. Every prescribed monomial column is an
operator word applied to `C(1)`, and the columns span `Q`. If the operators
commute globally, the displayed relation propagates to every word, forcing
global idempotence. The same argument propagates each input relation from
the cyclic vector to the whole module. Simultaneous Boolean eigenspaces
then occur only at actual solutions; cyclicity makes each eigenspace at
most one-dimensional. Hence `dim Q<=#solutions`, and every ideal
consequence of degree at most `D` maps to zero.

The stated local defects correctly vanish on `Q_(D-2)`. For the claim about
input operators on this subspace, the inputs must be quadratic, as they are
in the normalized Semaev presentation. The exact tensor identity (S)
enforces all field-coordinate rows, and (M) enforces closure for every
low-degree kernel vector. The dual-span criterion likewise tests the full
kernel. No global commutation follows merely from global idempotence.

## 4. Tensor-factorization already collapses at input degree two

Under `C(p(x)q(y))=C_x(p) tensor C_y(q)` and `C(1)!=0`, choose linear
functionals `phi,psi` with `phi(C_x(1))=psi(C_y(1))=1`. Set
`alpha_i=phi(C_x(x_i))` and `beta_j=psi(C_y(y_j))`. Each normalized
Semaev row is constant plus linear terms plus cross terms `x_i*y_j`.
Applying `phi tensor psi` to its zero image gives exactly its evaluation at
the Boolean assignment `(alpha,beta)`. Thus an actual common zero exists,
without any higher-degree or closure hypothesis.

The stronger source claim about variation spaces is also sound. Applying
functionals that kill the constant columns forces
`(u*w)^2+z*u*w=0`; its kernel is `{0,z}`. If both direction spaces are
nonzero, field multiplication forces each to have dimension one. All pairs
of normalized functionals give a four-point solution rectangle. Direct sums
remain excluded when each component separately kills every input and some
component has nonzero constant image. Correlated sums with cancellations
and nonlinear within-block inputs are outside this argument.

No mathematical correction is required. These necessary conditions permit
`D` of order `log n` when quotient rank is polynomial in `n`; they do not
preclude growing caps. Constructing correlated columns with the actual
field-tensor identities, full closure, and an independent ideal-membership
or solution-count bridge remains the outstanding family construction.
