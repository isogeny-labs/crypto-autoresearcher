# Independent blind derivation for joint F

Task: `TASK-20261102-bb100a`  
Reviewer: `Reviewer F` (`/root/review_blind`)

## Scope and verdict

This is a hand derivation from the blind mathematical statement only. It does
not inspect or assess any producer proof, Lean declaration, source file,
machine receipt, or sibling report. Joint F **holds** in this exact scope: the
five finite mathematical boundary results, counterexamples, and repaired
statements proved below are valid. This verdict says nothing about machine
verification or correspondence with an unseen producer claim.

## 1. One-shot counts do not determine repeated history

Write the outcome space as `Omega = {false, true}` and identify a trial with
its success set.

* Process A has success sets `A_0 = A_1 = {true}`. Each set has cardinality
  one, while the outcomes failing both trials form `{false}`, of cardinality
  one.
* Process B has success sets `B_0 = {true}` and `B_1 = {false}`. Again each
  set has cardinality one, but no outcome fails both trials, so the relevant
  cardinality is zero.

Thus identical marginal counts do not determine even a two-step joint event.
The same obstruction persists for trials indexed by the natural numbers. If
every trial succeeds exactly on `{true}`, then `false` fails forever. If even
trials succeed on `{true}` and odd trials on `{false}`, every trial still has
one successful outcome, but neither outcome fails forever. Identical
one-trial counts therefore cannot rule out a forever-failing outcome.

For the recurrence, put `q = 1 - epsilon`. The stated range gives
`0 <= q <= 1`. More generally, for all `k,j` in `N`, induction gives

```
S(k + j) >= q^j S(k).
```

Indeed, the claim is an equality at `j = 0`; if it holds at `j`, then
`S(k+j+1) >= q S(k+j) >= q^(j+1) S(k)`, where the second inequality uses
`q >= 0`. Taking `k = 0` and `S(0) = 1` yields the sharp pointwise bound

```
S(n) >= (1 - epsilon)^n.
```

It is sharp because `S(n) = q^n` satisfies every recurrence inequality with
equality.

There are two useful finite, division-free tail forms. For `0 <= k <= N`,
summing the shifted pointwise bounds and using the polynomial identity
`epsilon * sum_(t=0)^(d-1) q^t = 1 - q^d` gives

```
epsilon * sum_(j=k)^(N-1) S(j) + q^(N-k) S(k) >= S(k).       (1)
```

No division by `epsilon` is used. Directly rewriting the recurrence as
`S(j) - S(j+1) <= epsilon S(j)` and telescoping also gives

```
epsilon * sum_(j=k)^(N-1) S(j) + S(N) >= S(k).               (2)
```

For `k = 0`, (1) reads
`epsilon * sum_(j=0)^(N-1) S(j) + (1-epsilon)^N >= 1`.
Both forms include `N = k`, with the empty sum understood as zero.
At `epsilon = 0`, the recurrence says `S(n+1) >= S(n)`, so `S(n) >= 1`.
At `epsilon = 1`, it supplies only nonnegativity after time zero and the
pointwise lower bound is zero for `n >= 1`. No upper bound, convergence, or
extinction statement follows from the given assumptions.

A marginal one-shot count does not supply the recurrence because the latter
is a history-conditioned restriction. For Process B, if `S(n)` is the
fraction of outcomes failing the first `n` trials, then
`S(0)=1`, `S(1)=1/2`, and `S(2)=0`. Although each trial succeeds on half the
outcomes, the putative `epsilon=1/2` recurrence fails at `n=1`, since it
would require `1/4 <= 0`.

**Weakened-premise control.** The upper bound `epsilon <= 1`, equivalently
`q >= 0`, is load-bearing for the geometric induction. With `epsilon=2` and
`S=(1,0,0,...)`, the recurrence `-S(n) <= S(n+1)` and nonnegativity hold, but
the claimed even-time bound would give `S(2) >= (-1)^2 = 1`, which is false.
Removing the recurrence altogether leaves the two marginal-count examples
above and hence no history bound.

## 2. Distinct cubic evaluation points need not give full rank

Order the degree-three monomial basis as

```
x^3, x^2 y, x^2 z, x y^2, x y z, x z^2, y^3, y^2 z, y z^2, z^3.
```

For `i = 0,...,9`, take the ten distinct rational triples
`P_i = (1,i,0)`. The evaluation row at `P_i` is

```
(1, i, 0, i^2, 0, 0, i^3, 0, 0, 0).
```

All ten rows lie in a four-dimensional coordinate subspace, so the matrix has
rank at most four and determinant zero. Equivalently, the nonzero coefficient
vector of `z^3` lies in its kernel because `z^3(P_i)=0` for every `i`.
Distinctness alone is therefore insufficient; this example does not rely on
using scalar multiples of a single triple.

Here is the exact determinant repair. Let `M` be the resulting `10 x 10`
rational evaluation matrix, let `c in Q^10` be a coefficient vector, and let
`f_c` be the corresponding homogeneous cubic. Then

```
[f_c(P_i)=0 for every i] and det(M) != 0  ==>  c=0.
```

The vanishing conditions are exactly `M c = 0`; if `det(M) != 0`, the matrix
has an inverse over `Q`, and multiplication by that inverse gives `c=0`.
This condition is also necessary for that conclusion for an unrestricted
coefficient vector: if `det(M)=0`, square-matrix linear algebra over `Q`
produces a nonzero `c` with `Mc=0`. Thus the repaired statement is an
if-and-only-if injectivity criterion, not merely a convenient sufficient
condition.

**Weakened-premise/proves-too-much control.** Replacing `det(M) != 0` by
pairwise distinct triples is refuted by the displayed points. With fewer than
ten unrestricted rows, even maximal row rank leaves a nonzero kernel by
rank-nullity; for example, a rank-nine `9 x 10` matrix has a one-dimensional
kernel. None of this proves a statement about projective quotients,
nonsingularity of a cubic, or a restricted lower-dimensional coefficient
family; those require separate hypotheses and rank checks.

## 3. Scalar clearing: image and exact fibres

Use additive cyclic groups. A bad clearing example is

```
K = Z/2Z,  S = Z/2Z,  h = 2.
```

Multiplication by two kills `K`, but it also kills `S`. Its image on
`K x S` is only `{(0,0)}`, strictly smaller than the intended
`{0} x S`.

A good example is

```
K = Z/2Z,  S = Z/3Z,  h = 2.
```

Multiplication by two kills `K` and permutes `S` by swapping `1` and `2`.
For each target `(0,t)`, the preimages are exactly
`(k,2t)` with arbitrary `k in K`, since `2` is its own inverse modulo three.
Thus the image is `{0} x S` and every target has exactly two preimages.

The generic statement is a standard finite-homomorphism calculation, included
here explicitly. Write `mu_K(k)=hk` and `mu_S(s)=hs`. For arbitrary finite
additive groups,

```
im(mu_K x mu_S) = hK x hS,
ker(mu_K x mu_S) = ker(mu_K) x ker(mu_S).
```

Every nonempty fibre of a group homomorphism is a coset of its kernel, so
every point of `hK x hS` has exactly
`|ker(mu_K)| |ker(mu_S)|` preimages, and points outside that image have none.
Consequently, under the explicit hypotheses

```
hk = 0 for every k in K,          and
mu_S is bijective,
```

the image is exactly `{0} x S` and every target fibre has cardinality `|K|`.
Conversely, for finite `S`, image equality with `{0} x S` forces `hK={0}`
and `hS=S`; surjectivity of the self-map of finite `S` then makes `mu_S`
bijective. These are therefore the exact coordinatewise image conditions.
The endpoint cases behave as the formula says: if `K` is trivial, each fibre
has size one; if `S` is trivial and `h` kills `K`, the sole target has `|K|`
preimages; and `h=0` can permute `S` only when `S` is trivial.

For a uniform input on the whole finite product, equal fibres do imply a
uniform pushforward on `{0} x S`. They do not imply the same for an
unspecified encoder `E`: the probability above `(0,t)` is the sum of the
input masses that `E` assigns to the group elements in that fibre, not merely
the fibre's cardinality. Uniformity, surjectivity, and distributional behavior
of a hash encoder are additional premises.

**Weakened-premise control.** Keeping the hypothesis that `h` kills `K` but
dropping bijectivity on `S` gives the `Z/2Z x Z/2Z` counterexample above.
Conversely, if `h` permutes `S` but does not kill `K`, then the first image
coordinate need not be zero. Thus neither coordinate hypothesis can be
silently omitted.

## 4. Constant challenges in the acceptance equation

Let the constant value of `H` be `c in F`.

If `c=0`, acceptance is simply `sG=R`; it is independent of both `m` and
`X`. Hence any choice of `m,s` together with `R=sG` accepts for every public
element `X`.

More generally, if the known constant `c` is chosen before `R`, then for any
chosen public element `X` and scalar `s`, one can set

```
R = sG - cX.
```

The equation then holds identically. For `c != 0`, this is a key-specific
chosen-`R` construction rather than a single transcript accepting different
keys.

A concrete zero-challenge example uses `F = F_5`, `A = F_5` additively,
`G=1`, `m=0`, `s=2`, and `R=2`. With `H` constantly zero, both distinct
public elements `X_1=1` and `X_2=3` satisfy

```
2*1 = 2 = 2 + 0*X_i.
```

For a fixed transcript `(m,R,s)` whose challenge value `c` is nonzero, two
accepting public elements must coincide. Indeed,
`R+cX_1=sG=R+cX_2`, hence `c(X_1-X_2)=0`; multiplying by `c^(-1)` in the
field gives `X_1=X_2`. This exhausts the scalar endpoints: zero permits
multi-key acceptance, while every nonzero field scalar is invertible.

**Weakened-premise/proves-too-much control.** Nonzeroness is not enough if
the scalar ring is not a field. In the `Z/4Z`-module `A=Z/4Z`, take the
nonzero scalar `c=2`, `G=1`, `s=0`, and `R=0`; both `X=0` and `X=2` satisfy
the same fixed equation. Also, fixed-transcript key uniqueness does not imply
unforgeability or extraction: for a known nonzero constant, the chosen-`R`
construction above creates an accepting transcript for every selected key.
Random-oracle unpredictability, replay conditions, two-transcript forking,
and witness extraction are separate hypotheses and conclusions.

## 5. Full relation kernel of the commitment

For `(m,r) in F^2`, the relation `H=alpha G` gives

```
Com(m,r) = (m + alpha r) G.
```

Injectivity of `a |-> aG` therefore yields the exact kernel

```
ker(Com) = {(m,r) : m + alpha r = 0}
         = {(-alpha t, t) : t in F}.
```

The pair `(-alpha,1)` is a nonzero relation.

Given an opening `(m,r)` and a requested message `m'`, define

```
r' = r + (m - m') alpha^(-1).
```

Then `m' + alpha r' = m' + alpha r + m - m' = m + alpha r`, so the
commitments coincide. The minus sign is equivalently visible in the
difference relation
`(m'-m, r'-r) = (delta, -delta/alpha)`.

Suppose two openings collide and `m != m'`. Injectivity gives

```
m + alpha r = m' + alpha r',
m - m' = alpha (r' - r).
```

The denominator `r'-r` is nonzero: if it were zero, the last equality would
force `m=m'`. Thus the relation scalar is recovered exactly as

```
alpha = (m - m') / (r' - r).
```

For a concrete collision, take `F=F_5`, `V=F_5` additively, `G=1`,
`alpha=2`, and `H=2`. Then

```
Com(0,0)=0=3+2*1=Com(3,1)  (mod 5).
```

The recovery formula returns `(0-3)/(1-0)=2` in `F_5`, as required.

**Weakened-premise control.** If injectivity is dropped, take `G=0` (and
therefore `H=0`); the entire plane `F^2`, not the displayed line, is the
kernel, and different messages can collide with `r'=r`, defeating the
denominator argument. If instead `alpha=0` while injectivity is retained,
the kernel is `{(0,t)}`, but `alpha^(-1)` does not exist and an arbitrary
requested message cannot be opened to the same commitment. Both hypotheses
are load-bearing for the equivocation and recovery formulas.

## Computational limits of the finite results

These derivations are finite algebra and combinatorics only.

* The history examples do not instantiate independent trials, conditional
  success bounds, an asymptotic adversary, or any computational game.
* Evaluation-matrix rank proves no geometric nonsingularity and supplies no
  algorithmic attack.
* Equal fibres of scalar multiplication say nothing about an unmodeled
  hash-to-group or hash-to-curve encoder.
* A constant function is not a random oracle; the Schnorr equations establish
  neither a ROM/QROM attack nor replay, forking, or extraction claims.
* Although `alpha` exists algebraically and a party knowing it can equivocate,
  computing `alpha` from represented public elements `G,H` may be a discrete
  logarithm problem. The finite collision with coordinate-visible `F_5`
  elements is not an ECDLP algorithm and does not by itself refute a
  computational binding theorem.

No conclusion here applies to a paper, implementation, or formal theorem whose
actual hypotheses and bridges were not part of the blind input.
