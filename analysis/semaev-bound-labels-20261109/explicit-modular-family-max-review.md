# Independent review of the explicit modular affine-separator family

Date: 2026-11-09. Independent source-only mathematical review. No experiment,
solver, closure computation, certificate replay, compilation, or cloud job was
performed. This report does not make an official scientific promotion.

**Verdict: the stated infinite family and its strict Boolean degree-three
upper bound are supported. No substantive mathematical flaw was found.** The
bound applies to the multilinear-normalized Boolean coordinate presentation
on the full vector-space domain `V x V`, with Boolean field equations. The
review below supplies a direct identity in the original variables that makes
the degree transfer explicit.

## Sources and independence

The reviewed producer artifact is
`explicit-half-diagonal-affine-separator-family.md`, including its final
`eta` notation and rational-target sentence. Its SHA-256 is
`38fcc07811a9a0ef15c745b5119fe835e779f49cbab5643c88e8bf38a0aaf392`.

The following companion sources were read:

| Source | SHA-256 |
| --- | --- |
| `epsilon-elimination-dual-pencil.md` | `3a10d18ad53f556d5d23567731e0a83b71597ea2d936b5eb30711f5663e38f0c` |
| `trace-slice-cubic-parametrization.md` | `eb34f3cf25f189807f11604e48adf26d532e1618ad84da8f1bca6dc66b4189ec` |
| `definition-audit.md` | `8e5a626ba230499be7e91bb9713e5aaac1d58cade9b70cb9180dbb2fcf4bb04e` |

The earlier epsilon-elimination review and the trace-active existence note
were also inspected for context; their verdicts are not premises of this
review. This is a separate reviewer derivation after reading the producer's
proof, not a blind review. The normal-basis reference linked by the producer
was not independently consulted here: the elementary root-count proof below
is sufficient. All mathematical source provenance in this report is internal
except for explicitly rederived elementary facts.

The reviewed joints are the Frobenius module, reciprocal-factor restriction,
trace orthogonality, the small-field quadratic form, literal separator,
original-system degree transfer, and the edge case and domain. No numerical
or asymptotic-cost claim is inferred from these symbolic checks.

## 1. Frobenius really is the required regular module

Write `F(u)=u^2` on `K=F_(2^n)`, with `n=3*7^j`. If a nonzero polynomial
`p(X)=sum_(i=0)^d c_i X^i` of degree `d<n` annihilated `F`, then the nonzero
ordinary polynomial `sum c_i Z^(2^i)` would vanish on all `2^n` elements of
`K`, although its degree is at most `2^d<2^n`. The root bound rules this out.
Since `F^n=I`, the minimal polynomial is exactly `X^n-1`.

The characteristic polynomial has degree `n`, is divisible by the minimal
polynomial, and therefore also equals `X^n-1`. Because `n` is odd, this
polynomial is squarefree: its derivative is `X^(n-1)` and has no common root
with it. Consequently the module is a direct sum of one copy of each
irreducible factor module; for a factor `p`, `ker p(F)` has dimension
`deg p`. This justifies the claimed regular-module description and the
factor-kernel construction without importing a normal-basis theorem.

## 2. Exactly two factors are self-reciprocal

For a root of unity `alpha` of order `m|n`, its irreducible factor is
self-reciprocal precisely when `alpha^(-1)=alpha^(2^a)` for some `a`, or
equivalently `2^a=-1 mod m`. Every divisor of `n` is `1`, `3`, `7^h`, or
`3*7^h`, with `h>=1` in the latter two cases.

The binomial induction from `2^3=1+7` gives
`2^(3*7^(h-1))=1 mod 7^h`. Thus the multiplicative order of `2 mod 7^h`
divides an odd number. It cannot contain `-1`, whose order is two. Reduction
modulo `7^h` also excludes `2^a=-1 mod 3*7^h`. The only remaining root
orders are one and three, giving precisely `X+1` and `X^2+X+1`.

The latter module is
`S={u in F8: u+u^2+u^4=0}`. Indeed `F^2+F+I` annihilates exactly this
two-dimensional space, and `F^3=I` on it. The absolute trace on `F8`
is `(n/3)` times its `F8/F2` trace, which is the same trace because
`n/3=7^j` is odd.

## 3. The selected complement has all needed orthogonality properties

Use `B(u,v)=Tr(uv)`. This form is nondegenerate: if `u!=0`, taking
`v=u^(-1)` gives `B(u,v)=Tr(1)=1`. It satisfies
`B(Fu,Fv)=B(u,v)`.

After scalar extension, Frobenius is diagonalizable by squarefreeness. For
eigenvectors of eigenvalues `alpha,beta`, invariance gives
`(alpha*beta-1)B(u,v)=0`. Hence a factor component can pair only with its
reciprocal component. Selecting one component from every non-self-reciprocal
pair therefore gives

```text
dim L = (n-3)/2,
F(L) = L,
B(L,L) = 0,
B(L,S) = 0,
B(L,1) = 0.
```

In particular `Tr(L)=0`. This argument controls products only after applying
the trace; it does not assert multiplicative closure of `L`, and none is
needed later.

For independent `w,eta in S`, put `W=<w> direct_sum L`, `e=1+eta`, and
`V=W direct_sum <e>`. The direct decompositions and `Tr(e)=1` give
`dim W=(n-1)/2`, `dim V=(n+1)/2`, and `V intersect ker Tr=W`. If `1`
belonged to `V`, its trace would force its `e` coefficient to be one,
putting `eta` in `W`, which contradicts independence in `S` and the direct
sum with `L`. Also `L` is orthogonal to every element of `V`.

The choices are constructive: factor `X^n-1`, select one factor from each
reciprocal pair, and form their Frobenius kernels. The theorem works for
every such selection and every ordered independent pair in `S`. A unique
deterministic instance additionally fixes an ordering of the field
representation and these finite choices. No efficient factorization or
basis-construction complexity bound is supplied or required.

## 4. The F8 quadratic form is anisotropic on S

On `K0=ker Tr`, `A=F+I` is invertible: its kernel on `K` is `<1>`, and
`Tr(1)=1`. Let `J=A^(-1)` and `H=FJ=J+I`. The subspaces `L` and `S`
are stable under `J` and `H`, because `A` restricts to an invertible map
on each.

On `S`, `F^2+F+I=0`, so `(F+I)F=I`, giving `J=F` and `H=F^2`.
For `0!=u in S`, division of `u^4+u^2+u=0` by `u` yields
`u^3=u+1`. Thus

```text
u H(u) = u^5 = u^2+u+1,
Tr(u H(u)) = Tr(u^2)+Tr(u)+Tr(1) = 1.
```

At zero the same quadratic form is zero. The use of the absolute trace is
valid because its restriction to `F8` is the trace already checked above.

For `s in S,l in L`, all three terms `Tr(l H(l))`, `Tr(s H(l))`, and
`Tr(l H(s))` vanish by stability and the established trace orthogonality.
Consequently `Tr((s+l)H(s+l))=Tr(sH(s))`. This is the exact reason the
small-field form extends across the growing complement.

## 5. The separator is a literal identity

For `t in W`, set `lambda=t+eta`. It lies in `K0`; also `t+e=lambda+1`.
The adjoint of squaring for the trace pairing is inverse Frobenius, since
`Tr(lambda*x^2)=Tr(F^(-1)(lambda)*x)`. Therefore

```text
Tr(lambda*pi(x^2+(t+e)x))
  = Tr((F^(-1)(lambda)+(t+e)lambda)*x)
  = Tr((F^(-1)+F+I)(lambda)*x).
```

Here pairing with `pi` removes no term because `Tr(lambda)=0`.
`T=F^(-1)+F+I` vanishes on `S`, preserves `L`, and hence sends
`lambda=eta+bw+l` into `L`. Since `L` is orthogonal to `V`, the displayed
expression is zero for every `x in V`.

The constant part is `H(t)+H(eta)=H(lambda)`. Independence of `w,eta`
ensures `eta+bw!=0` for both Boolean values of `b`, and the preceding
quadratic-form calculation gives `Tr(lambda H(lambda))=1`. Thus

```text
Tr(lambda(t) F_t(x)) = 1
```

for every pair of independent Boolean coordinate assignments in `V x W`.
Evaluation on the Boolean cube identifies the Boolean polynomial ring with
its function ring, so this is a literal normalized polynomial identity. Its
multipliers are affine and its generators have degree at most two.

## 6. A direct original-variable identity verifies strict cap three

The transfer can be checked without appealing to mere ideal equivalence or
to an auxiliary epsilon variable. In the normalized Boolean ring on the
coordinates of the original `x,y in V`, define

```text
U = (xy)^2 + xy + x^2 + y^2 + 1,
ell = Tr(x+y+1) = Tr(U),
t = x+y+(1+ell)e,
lambda = t+eta,
R = J pi(U).
```

The equality `ell=Tr(U)` follows by cancellation of `Tr((xy)^2)` with
`Tr(xy)`. Thus `ell` is an affine original-row consequence already in
`W_2`. The definition of `t` gives `t in W` for every assignment, and
`y=x+t+(1+ell)e`. Both `t` and `lambda` are affine in the original bits.
`J pi` is a fixed `F2`-linear map of the output space, so every coordinate
of `R` is a constant linear combination of the original normalized rows.

To verify the identity, put `s=x+y+1=lambda+ell e`. The two relations

```text
J A(v) = pi(v),
J pi(s^2) = H(pi(s))
```

give `R=pi(xy)+H(pi(s))`. Since

```text
xy = x^2+(t+e)x+ell e x,
pi(s) = lambda+ell eta,
```

one obtains the exact field-valued Boolean identity

```text
R = F_t(x) + ell*(pi(ex)+H(eta)).
```

Pairing with `lambda` and using the checked separator therefore yields

```text
1 = Tr(lambda R) + ell*Tr(lambda*(ex+H(eta))).
```

This explicitly proves the claimed strict degree accounting. The first term
multiplies degree-at-most-two row consequences by affine polynomials, which
is permitted at cap three. In the second term the multiplier of `ell` has
degree at most two. Starting from the available affine `ell`, multiply by
at most two individual variables in sequence: the intermediate degrees are
at most two and three. All multiplications obey the strict rule that the
source degree is at most the cap minus one. There is no appeal to the
weaker rule that a reduced product merely happens to fit the cap.

Equivalently, affine elimination of `ell` costs cap two and the separator
lifts at cap three, as asserted in the producer note. The direct identity
above removes any ambiguity in that sentence. It establishes `1 in W_3`
for the original normalized presentation.

For this UNSAT Boolean system, deriving `1` at cap three implies
`d_LFD<=3`: every polynomial in the unit ideal can be obtained by multiplying
that constant within cap `max(3,deg f)`. The degree-two Boolean/polynomial
closure bridge is sufficient at this cap. This argument supplies an upper
bound and does not require a nonmembership or solution-count inference.

## 7. Edge case, necessary divisibility, and exact scope

For `j=0`, `n=3`, there are no remaining reciprocal factor pairs and
`L=0`. All isotropy assertions are then vacuous; `W=<w>` and
`V=<w,1+eta>` still have the required dimensions and traces. The two possible
values of `lambda` are `eta` and `eta+w`, both nonzero in `S`. The same
literal identity proves UNSAT and the same cap-three upper bound. No
positive-dimensional complement was silently assumed.

The stated necessity of `3|n` for this particular natural separator is also
correct. With `n=2r+1`, the annihilator condition forces
`T(W) subset V_perp intersect K0`. The latter has dimension `r-1`, because
`dim V_perp=r` and its trace is nonzero exactly when `1 not in V`.
When `3` does not divide `n`, the polynomials `X^2+X+1` and `X^n-1`
are coprime, making `T` invertible. Then `dim T(W)=r`, a contradiction.
This tests the natural `lambda=t+e+1` construction; it does not exclude other
affine separators or other cap-three refutations.

The supported family has fixed `m=2`, `z=a6=1`, growing
`n=3*7^j`, and `dim V=(n+1)/2`. The compatible curve
`E: Y^2+XY=X^3+1` is nonsingular (`a6=1`), and `(1,0)` is visibly rational
on it. Its double is `(0,1)`, the nontrivial point of order two, so the
named target has order four. It is not a prime-order-target construction.

The degree bound is for the full vector-space input domain with linear
coordinate maps for `x` and `y`. It neither requires every element of `V`
to lift to an `E(K)` point nor gives a degree-preserving transport through a
nonlinear point-selector encoding. It also makes no degree-three assertion
for an unnormalized raw quartic coordinate presentation: the normal forms
are the input rows whose degree has been used throughout.

The theorem therefore supplies an explicit infinite, trace-active,
half-dimensional UNSAT family with a uniform upper bound of three. It does
not assert exact LFD, exclude degree-two refutations for some members, or
give a bound for arbitrary choices of the half-dimensional subspace.
These scope distinctions agree with the producer's final text.

## Disposition

No correction to the mathematical theorem is required. The direct original
identity in Section 6 is a useful optional expansion of the short lifting
sentence. This independent written review supports the exact scoped
construction; it is neither a formal proof-assistant check nor an official
ledger decision.
