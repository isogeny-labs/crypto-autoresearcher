# EXP-PEXT-bf8f96: prospective exact exceptional-index construction

The native support path now streams any exact join interval, counts its generic rows, and emits only overlapping rows with their geometric rank, projective branch count and genus. This is a **linear scan** of the interval. On the complete fixed F27 software fixture it returns 1,358 generic and 280 exceptional positions, with exactly identical exceptional ordinals and genera under 113-position shards. The separate square-relation implementation agrees on every emitted rank. The [source-bound log](software-tests.json) records the nine core and eleven join test results. This adds a bounded-memory exact screening route for any cohort; it is not a demonstrated fit for the proposed 24 CPU-hour total.

## Candidate generator for the complete exceptional set

Let `K = F_(q^n)`, `Q = q^n`, `B` be the four projective roots of the actual quotient binary quartic, and `sigma(x)=x^q`. The frozen structure order is a transversal of **left** `PGL2(F_q)` cosets of `N in PGL2(K)`. The transported branch support is `N(B)`. It overlaps a conjugate exactly when, for some `1 <= k <= (n-1)/2`, there are roots `alpha,gamma in B` with

`N(alpha) = sigma^k(N(gamma))`.

The indices `k` and `n-k` are equivalent after applying the inverse Frobenius, so this half-range is complete. Every generated candidate must be mapped back to the existing structure ordinal, sorted, deduplicated and checked by direct support gcd. The complement intervals then have the generic rank/genus certificate from the disjoint-support lemma.

### Roots rational over K

Write `x = N(alpha) = sigma^k(N(gamma))`. Because `N` is defined over `K`, rational branch roots give `x in P1(K)`. Normalize `x` under the left `PGL2(F_q)` action. Its rational points are one orbit; every nonrational point in the specified odd-prime extensions has trivial stabilizer, since a nonidentity Möbius map over `F_q` can fix only points of degree at most two. Thus `q=5,7,11; n=3` each have one nonrational orbit, while `q=3; n=5` has ten.

If `x` is rational over `F_q`, injectivity forces `alpha=gamma`. Fixing `x` under the left action leaves exactly `Q(Q-1)/(q(q-1))` structure cosets per rational root. If `x` is nonrational, `alpha != gamma`; each orbit representative, ordered branch-root pair and retained `k` gives exactly `Q-1` projective matrices mapping `alpha` to `x` and `gamma` to `sigma^(-k)(x)`. These formulas enumerate the rational-root collision cases without scanning all structures.

### Roots of degree 2, 3 or 4 over K

Factor the squarefree quartic over `K`. Represent each irreducible factor's roots in a documented **symbolic** degree-`d` extension of `K`, with explicit embeddings into a common extension for comparisons. Never allocate the elements of `F_(Q^4)` as a table. For roots `alpha,gamma` of equal degree `d`, put `beta=sigma^k(gamma)` and `C=N^(-1) sigma^k(N)`. The collision equation is `C(beta)=alpha`. For `C=[a b; c d]`, its coordinates in the symbolic basis give the exact `d x 4` linear system

`a*beta + b - c*alpha*beta - d*alpha = 0`.

Enumerate every projective kernel vector with nonzero determinant. A degree-two root has `Q+1` invertible maps to another degree-two root; a degree-three or four root has at most one, because the stabilizer of a point of degree at least three is trivial. For each `C`, require the ordered projective cocycle norm `C sigma^k(C) ... sigma^((n-1)k)(C)` to be the identity. A scalar lift can then be scaled to norm one, and the `F_q`-linear row equations `sigma^k(v)=v C` yield an invertible `N`. All solutions differ by left `GL2(F_q)`, so they give one structure coset. This is the finite-field Lang/Hilbert-90 step; the [original Lang paper](https://wstein.org/papers/bib/Lang-Algebraic_Groups_Over_Finite_Fields.pdf) gives the connected-group surjectivity used here.

A once-per-field map from the normalized `N^(-1) sigma(N)` cocycle to the exact existing structure ordinal avoids repeated canonicalization. Verify it has precisely `S=(Q^3-Q)/(q^3-q)` distinct entries before accepting any generated index.

## Completeness and resource gates

Every exceptional row supplies a shared branch root. Its degree over `K` is one of `1,2,3,4`; the rational and symbolic-extension cases above enumerate the corresponding equation. Conversely, every retained candidate is checked against the literal transformed quartic and conjugate support gcd. A second implementation must regenerate the orbit partition and linear kernels, test all five squarefree quartic factor patterns (`1+1+1+1`, `1+1+2`, `1+3`, `2+2`, `4`) on small exhaustive fixtures, verify norm and Lang witnesses, and compare the exact sorted index set with a full small-field structure scan. Its production certificate must include per-`T` branch-factor pattern, candidate counts by degree and `k`, duplicate counts, sorted ordinal digest, complement-interval coverage, and total `S`.

For `q=11,n=3`, a conservative degree-one bound is `4*16093 + 12*1330 = 80332` candidate matrices per `T`, versus `1,786,323` structures. Across `5,322` `T` blocks that is at most `427,526,904` degree-one candidates before deduplication; degree-two and higher candidates are additional. For `q=3,n=5`, the corresponding degree-one bound is `97,284` per `T`. These are **construction counts**, not measured time or a proven budget fit. Before protocol approval, implement the complete degree-1 through degree-4 generator, independent checker, streaming receipts, all original controls and a source-bound feasibility measurement under the proposed 24 CPU-hour total and 4 GB ceiling. If that gate fails, preserve the full cohorts and revise the execution route through a prospective contract decision.
