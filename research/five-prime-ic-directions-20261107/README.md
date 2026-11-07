# Five prime-field IC directions: exact constructions

This first construction round implements all five directions requested from
crypto-autoresearcher PR #3095: **58, 69, 71, 56, 87**. Seven deterministic
software checks pass. The next research work is specified per direction below;
these prototypes do not complete the proposed scaling or performance panels.

## What was constructed

### 58: invariant-coordinate elimination

For the short-Weierstrass third summation polynomial

    f3(x,y,z) = (x-y)^2 z^2 - 2((x+y)(xy+a)+2b)z + (xy-a)^2 - 4b(x+y),

we construct the exact iterated resultant

    R_k(u,v,z) = Res_y(y^k-v, Res_x(x^k-u, f3(x,y,z))).

For k=2 use (a,b)=(c,0); for k=3 use (a,b)=(0,c). These are monic
eliminations in x and y, so specialization retains their product-over-roots
meaning over the algebraic closure. We do not claim that the resultant is a
reduced generator of the elimination ideal. Rational lifting, subgroup
membership, and signs are checked afterward.

The generic symbolic results over Z[u,v,z,c] are:

| Case | Degree in each of u,v | Degree in z | Expanded terms |
|---|---:|---:|---:|
| k=2, j=1728 | 4 | 8 | 45 |
| k=3, j=0 | 6 | 18 | 175 |

These are exact representation sizes, not solver timings. The original f3 has
degree 2 in each factor coordinate. All target powers are divisible by k:
R_k(u,v,z)=H_k(u,v,z^k). The compressed polynomial H_k has degree 4 or 6 in
its target invariant. `derive.py` serializes both expressions; the equality is
tested coefficient-for-coefficient. On F13, complete rational fibers and signs
are checked for every invariant pair on y²=x³+2 and y²=x³+x, with automorphism
scalar action checked on the selected prime-order subgroup.

**Next construction:** keep the low-degree lifted equations with explicit
orbit labels alongside H_k; compare exact solution sets before selecting a
solver representation. Expansion did not lower the individual factor degree.
This observation does not decide whether a factored circuit or symmetry-aware
solver benefits.

### 69: exact transport and relation columns

For E: y²=x³+A x²+B x, the degree-2 map is

    phi(x,y) = (x+A+B/x, y(1-B/x²)),
    E': y²=x³-2A x²+(A²-4B)x.

Infinity and (0,0) map to infinity. Apply the same construction to E', then
scale (x,y) by (1/4,1/8), to obtain the dual map. On a prime subgroup of odd
order r, normalization is [2^(-1) mod r] dual(phi). This is the inverse of phi
on that subgroup. Composition gives the analogous product-degree rule for
chains.

The test checks both dual compositions on every rational point and the
homomorphism law on every pair for E/F101 with (A,B)=(3,2). It constructs coordinate-window bases and a global signed-point registry. A
post-test coverage audit found base sizes 2 and 0 and zero internal relation
tuples: the row-identity loop was vacuous. Thus this fixture validates dual maps
and subgroup normalization, but not normalized relation rows. A separate
finite-field rank routine passes explicit dependent/independent matrix tests.
The next relation fixture must assert nonempty rows before claiming coverage.

**Next construction:** connect a digit-system solver to these local endpoint
bases and retain one global column registry. The current path is a rational
2-isogeny control, not a certified crater-to-floor path: endpoint conductors and
volcano direction are not certified, and no level-dependent conclusion is made.

### 71: homogeneous factored membership

If x(T_i(P))=N_i(X)/D_i(X), membership in the coordinate set S is represented by

    M_i(X) = product_{s in S} (N_i(X)-s D_i(X)), with D_i(X) != 0.

For a degree-2 step the shared numerator/denominator recurrence is

    N_next = N²+A ND+B D²,    D_next = ND.

The prototype exposes the individual factors and the expanded polynomial;
explicit labels can select an endpoint without multiplying all endpoint
membership polynomials together. No shared intermediate across distinct input
points is assumed. Finite-field pole checks agree with direct rational
evaluation at every field element for S={0,1,2,3}, lengths 0..3 over F101.

**Next construction:** retain this recurrence as a straight-line circuit rather
than expanding N and D at every step, and attach operation counters to circuit
nodes. The present implementation proves membership semantics, not an optimized
circuit implementation or measured saving.

### 56: actual FAM-1 equations and extraction gates

The audited source identifies small_x, subgroup and Dickson families. There is
no single arbitrary quadratic FAM-1 parameterization. The implementation uses
x=t for small_x/subgroup and x=t+c/t for Dickson. It imports the actual
repository builders and their coset and membership parameters.

For m=3/4 it constructs chained f3 systems, clears denominators, retains pole
exclusions and supplies the actual parameter-domain equations. A Dickson
parameter must lie in its original multiplicative coset; arbitrary t is not an
admissible replacement. Internal chain coordinates are still unknowns; the
prototype does not assign them artificially small bounds.

The lattice builder retains shifts p^(k-j) t^e f^j and exact bound scaling.
Decoding is exact. A sufficient integer-root certificate is

    sum_monomials |coefficient| product_i (B_i-1)^exponent_i < p^k,

conditional on modular vanishing and 0 <= t_i < B_i. Zero polynomials are
excluded. Root readiness distinguishes insufficient equations,
positive-dimensional ideals, inconsistent ideals and zero-dimensional ideals.
A univariate LLL positive control actually recovers a root polynomial; this is
not a successful multivariate Semaev recovery.

**Next construction:** select a joint shift family for the chained equations,
with truthful internal-coordinate bounds, and test whether certified integer
relations define a zero-dimensional ideal on exhaustive tiny instances. The
existing single-block reach notes remain a scoped prior dependency, not a
reason to substitute another family or abandon this direction.

### 87: controls that preserve the base

The repository's `FactorBase.planted` starts from a random base and replaces
points to force relations. That is useful for its declared detector but changes
the base. The new complementary-point generator fixes each original small_x,
subgroup or Dickson base and records every tested signed prefix. It accepts the
last point only if it is in that same signed point set and the full group sum
matches. No membership relaxation is used.

For m=3/4, tests compare all accepted plants with exhaustive signed tuple
oracles. Wrong targets and outside-base points are rejected by the same
predicate. Repeated points and cancelling tuples remain in this completeness
fixture: a production relation canonicalizer must later classify trivial and
duplicate rows, not count all plants as useful relations.

**Next construction:** integrate these fixtures with the existing mitm screening
stages and report first rejection stage. The current predicate checks base,
curve, signs, optional subgroup and sum; it is not a replay of every historic
FAM-1 screening/canonicalization stage.

## Validation and reproduction

Use Python >=3.10; tested with Python 3.11 and SymPy. From repository root:

```sh
python3.11 -m venv /tmp/five-ic-env
/tmp/five-ic-env/bin/pip install -r research/five-prime-ic-directions-20261107/requirements.txt
/tmp/five-ic-env/bin/python -m unittest discover -s research/five-prime-ic-directions-20261107 -p test_constructions.py -v
/tmp/five-ic-env/bin/python research/five-prime-ic-directions-20261107/derive.py --output /tmp/five-ic-eliminants.json
```

In a sparse checkout, materialize src/crypto_autoresearcher/index_calculus/curve.py
and factor_base.py. The package is imported through the source tree; no copied
or redefined FAM builder is used. `CHECKS.md` fixes the finite regression scope.
The first invocation failed at import under Python 3.9; invocation 2 passed six
checks; invocation 3 added compression and root-extraction gates and passed all
seven. All three logs are retained. Tests were limited to one process, 2 GiB
address space, 180 seconds per invocation, at most three invocations. Test-runner
durations are not performance evidence. No cloud experiment or benchmark ran.

See `SOURCES.md`, `NEXT.md`, `migration-reconciliation.md`, `report.pdf` and
`pipeline.svg`. The report is a construction report, not an experiment export
or independent scientific review. No hypothesis status, lead-atlas conclusion,
canonical frontier graph or historical run was changed. The five directions
remain active research tasks; the remaining obligations are explicit above.

## Delivery checks

The full package import also passes after materializing its actual __init__ and
imports. The repository-wide benchmark-record gate was run. After resolving
sparse-checkout omissions, it still reports four pre-existing missing validation
files in the A11–A14 benchmark records. Those records and their results were not
changed; `checks/base-benchrec-gate.txt` preserves the failures. No benchmark
record was added because this round ran software regressions and symbolic
construction, not benchmarks. The seven recorded code checks pass, with the #69 row-coverage gap explicitly
identified above; the global gate is not reported green.
