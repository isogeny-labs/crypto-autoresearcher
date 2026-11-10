# Fixed-m=2 product structure, qualified FFD, and additive corrections

2026-11-09. Parallel source-only continuation. The prior turn made progress by deriving all-instance LFD upper bounds and explicit arithmetic-work bounds. This round refines the factor-base criterion and first-fall definitions; it launches no solver experiment, build, certificate replay or cloud job. The arbitrary-subspace boundedness/unboundedness question remains open. No native solver-time measurements or official scientific status changes are claimed.

## Exact fibre classification

For s=X+Y in V, the homogeneous part of the affine Semaev fibre factors as

    L_s(X)=X^4+(s^2+z)X^2+zsX=X(X+s)(X^2+sX+z).

For nonzero s the kernel on V always contains {0,s}. It has dimension2 precisely when z=uv for distinct nonzero u,v in V with u+v=s; otherwise it has dimension1. At s=0 the kernel dimension is delta_z=1 iff sqrt(z) belongs to V, and is0 otherwise. These assertions concern the homogeneous kernels; the actual affine right-hand side can still be inconsistent.

Define P_dist(V) as the set of products of two distinct nonzero V elements. The independently checked normal-form proof now gives

    z outside P_dist(V)  ==>  LFD <= k+2 for SAT and UNSAT.

This is sharper than the general k+3 bound. It does not say product-rich targets attain a larger LFD; failing a sufficient condition is not a lower bound. Full derivation: [factor-base-product-obstruction.md](factor-base-product-obstruction.md). The FFD audit independently checked the factorization and this degree consequence.

## Trace reduction sharpens the selector bound

The affine-fibre proof gives LFD<=max(h+2,h+r+1), where h is the number of remaining selector bits and r bounds nonempty-fibre dimension. If Tr_K restricted to V is nonzero, the known row-span constraint Tr(s)+Tr(a6/z²)=0 removes one selector bit at cap2. It follows that:

| Hypotheses | All-instance LFD upper bound |
|---|---:|
| Arbitrary V | k+3 |
| Nonzero trace on V | k+2 |
| z outside distinct-product set | k+2 |
| Both preceding conditions | k+1 |

If the trace residual is zero, it eliminates no bit; if it is constant1, it instead gives a refutation at cap2. The formula keeps its floor2 when k=1 and h=0. In the remaining full-subfield case z,a6 in H, use Tr_H rather than the ambient trace (which vanishes on H); this gives k+2, not a constant bound. The selector repair and boundary cases were independently audited in trace-refinement-audit.md. The original derivation is in fibre-refinement.md.

## Guaranteed target strata and exact count capacity

There are at most (2^k−1)(2^k−2)/2 distinct-product values, since unordered pairs can collide. For k=ceil(n/2), every V therefore has at least the following numbers of nonzero field targets outside P_dist(V):

| n | Guaranteed count |
|---|---:|
| 2k−1 | 3·2^(k−1)−2 |
| 2k | 2^(n−1)+3·2^(k−1)−2 |

These are algebraic counts, not sample estimates or fixed-curve target-distribution statements. If curve parameters can be chosen jointly, a2=0 and a6=z^3 place (z,0) on the nonsingular ordinary curve y²+xy=x³+a6. That is a constructed admissible curve-target pair; it provides no hardness or fixed-curve sampling guarantee.

Let T_z={u in V\{0}:z/u in V\{0}}. The involution u↦z/u pairs all elements except the possible fixed point sqrt(z). If B_z counts unordered distinct product pairs, |T_z|=2B_z+delta_z. The exact homogeneous fibre capacities imply the bound on ordered S3 solutions

    S <= 2^(k+1)−1+|T_z| <= 3·2^k−2.

This improves the prior generic capacity 4·2^k. It does not assert simultaneous consistency of all fibres or equality. Swap symmetry gives a separate invariant: if H is the number of diagonal ordered solutions, the unordered count is (S+H)/2. These are prospective dataset and solver-check labels, not implemented measurements.

## A precise FFD criterion, and why the input presentation must be bound

For a list consisting only of genuine nonzero quadratics, let P send coefficient vectors to full row combinations, and Q to their homogeneous quadratic parts. Literal Petit–Quisquater first fall degree is2 exactly when

    ker Q is not contained in ker P.

A nonzero trace residual supplies one sufficient witness. A zero full-polynomial syzygy does not. Top-form syzygy FFD and a new class in W2/W1 are distinct observables. Mixed-degree lists require separate lower-degree checks.

The [FFD audit](ffd-qualified-statement.md) supplies a hand-worked actual Semaev example over F16 with V=F4, z²=z+w, w²=w+1, a6=1. Its four initial coordinate rows are genuine quadratics and sum in a specified combination to1, giving PQ FFD2 and LFD2. An invertible output-coordinate change exposes two affine rows l,l+1, giving PQ FFD1 and LFD1. It is the same polynomial ideal and same input solution set, but a different literal generating list.

Consequently, equality of row spans preserves W_D for D>=2 in these quadratic presentations, not necessarily at caps0 or1. The recorded degree5 obstruction and the unboundedness target are unaffected, but first-fall labels cannot be defined solely from the ideal or an undocumented row-reduced system.

## Corrected witness and affected records

The earlier algebraic note and first synthesis proposed X=Y=a6^(1/4) for the inside-subfield case. This is wrong because S3(X,X,z)=X^4+zX^2+a6. The correct witness is X=0,Y=sqrt(a6)/z. The SAT conclusion stands and the independent audit had already used the correct witness. The outside-target constant bound and arbitrary-V k+3 proof do not rely on the wrong diagonal formula.

[corrections.md](corrections.md) identifies affected files and also narrows the old blanket row-span/extension invariance statement to its correct degree range. Earlier Git/S3 bundles are unchanged. The correction is part of the proof record, not concealed as an edit to the old evidence.

## Verification scope and next step

The factorization and product-conditioned upper bound were independently derived by two agents and checked by parent. Parent checked the target counts, capacity involution and explicit F16 row arithmetic. These are written derivations and hand-worked controls, not machine-certified theorems or new dataset draws. Primary definitions remain those cited in the prior reports; no new external theorem is imported.

Next implement prospective product-profile and presentation-bound FFD labels under an explicit generator/checker contract, while continuing the uniform-separator versus constant-bound proof search. Large product enumeration, native solver execution and renewed cloud production remain subject to their existing resource and authorization constraints. The extensive dataset, full m=2–15 coverage and measured total native solver time remain unfinished.
