# Factor-base product obstructions and symmetry labels for fixed m=2

Date: 2026-11-09. Source-only algebraic derivation. No solver runs, closure computations, builds, jobs or new empirical data. The all-instance LFD bounds here depend on the independently reviewed selector normal-form argument in `general-m2-time-bound.md`. They do not prove an n-independent bound or unboundedness.

## Exact fibre factorization

Use the same setting: K=F_{2^n}, n>=3, V<=K of dimension k>=1, z,a6 nonzero, and s=X+Y in V. The S3 equation becomes

    L_s(X)=z^2 s^2+a6,
    L_s(X)=X^4+(s^2+z)X^2+zsX
          =X(X+s)(X^2+sX+z).

The factorization follows by setting q=X(X+s)=X^2+sX and expanding q(q+z). L_s is F_2-linear. This note classifies its kernel on V exactly, before considering whether the affine right-hand side belongs to its image.

### Nonzero s

For s!=0, 0 and s are distinct roots in V. The other possible roots solve

    r^2+sr=z, equivalently r(r+s)=z.

If a root r lies in V, then r+s lies in V too, and neither is 0 or s because z!=0. The four roots 0,s,r,r+s form a two-dimensional F_2-subspace. Otherwise the kernel is exactly {0,s} and has dimension one.

Thus, for s in V minus {0},

    dim ker(L_s|V)=2
      iff there are distinct nonzero u,v in V with u+v=s and uv=z;
    dim ker(L_s|V)=1 otherwise.

A given nonzero s admits at most one unordered pair {u,v}: the pair is the complete root set of T^2+sT+z. In the ambient field, the usual equivalent condition is Tr(z/s^2)=0, but that is not sufficient for the roots to lie in V. Factor-base membership must be checked separately.

### s=0: the repeated-root exception

Here L_0(X)=X^2(X^2+z). The square map is an automorphism of K. Its set of roots is {0,sqrt(z)}, even though the displayed factors have multiplicities. Therefore

    dim ker(L_0|V)=delta_z,
    delta_z=1 if sqrt(z) is in V, and 0 otherwise.

The affine zero-s fibre has 0 or 2^{delta_z} solutions. It never has four solutions. In particular, a square representation z=u^2 with u in V does not produce a two-dimensional fibre kernel.

## Precise factor-base condition

Define

    P(V)={uv : u,v in V minus {0}},
    P_dist(V)={uv : u,v in V minus {0}, u!=v}.

All nonempty affine fibres have dimension at most one if z notin P_dist(V). Equivalently, the *linear* fibres all have kernel dimension at most one if and only if z notin P_dist(V). The first assertion is sufficient for an affine instance; the converse need not hold for nonempty affine fibres, because a two-dimensional linear fibre could be inconsistent for the chosen a6.

The weaker exclusion of distinct products is the right criterion. Excluding every product is sufficient but not necessary: z=u^2 can occur without any distinct-product representation, and then the s=0 kernel has dimension one, which is still allowed.

Combining this condition with the normal-form proof gives the derived, all-instance upper bound

    z notin P_dist(V)  ==>  d_LFD <= k+2.

The uniform all-instance bound is k+3. If z belongs to P_dist(V), this does not establish LFD=k+3 or even LFD>k+2: it says only that the sufficient hypothesis for the one-degree improvement fails. Some extra-kernel fibres might be empty, and other reductions might lower the degree.

If z notin P(V), there is the stronger kernel profile: dimension zero at s=0 and dimension one for every nonzero s. The same LFD<=k+2 follows; no further degree improvement has been proved here.

## How many such targets must exist on the half-dimensional diagonal?

This is elementary counting, not a distribution model. Put M=2^k-1=|V minus {0}|. Every distinct-product value is the image of an unordered pair of distinct nonzero elements, so

    |P_dist(V)| <= C(M,2).

Similarly |P(V)| <= M(M+1)/2, counting unordered pairs with repetition. Product collisions can only make these sets smaller.

There are 2^n-1 eligible nonzero field targets before any target-on-curve restriction. Therefore the number outside the two product sets is at least

    max(0, 2^n-1 - (2^k-1)(2^k-2)/2)     [outside P_dist],
    max(0, 2^n-1 - (2^k-1)2^k/2)         [outside P].

For k=ceil(n/2), these simplify to:

| field parity | guaranteed count outside P_dist(V) | guaranteed count outside P(V) |
|---|---:|---:|
| n=2k-1 (odd) | 3*2^{k-1}-2 | 2^{k-1}-1 |
| n=2k (even) | 2^{n-1}+3*2^{k-1}-2 | 2^{n-1}+2^{k-1}-1 |

These guarantees hold for every k-dimensional V on the stated diagonal. For even n they include more than half of all nonzero field targets. For odd n the guaranteed fraction tends to zero, although the absolute count grows.

Important scope: a target z required to be an x-coordinate of a rational point on a particular curve is an additional condition. This counting argument does not establish how many excluded-product targets satisfy that condition, and it does not permit changing the target distribution silently. For the defined Semaev polynomial family with arbitrary z!=0, no such extra restriction is present. If curve parameters may be chosen with the target, set a2=0 and a6=z^3. Then a6!=0 and (z,0) lies on the nonsingular ordinary binary curve y^2+xy=x^3+a6, since z^3+a6=0. Thus every such z can be realized by a constructed admissible curve-target pair. This is not a fixed-curve or random-target guarantee, and this particular curve choice is not claimed to produce hard or unsatisfiable systems.

## Exact product-profile labels and solution-count bounds

For fixed z define

    T_z={u in V minus {0} : z/u in V minus {0}},
    B_z=#{unordered distinct pairs {u,v} subset V minus {0} : uv=z}.

The involution u -> z/u has the unique possible fixed point sqrt(z), so

    |T_z| = 2 B_z + delta_z.

Each distinct pair gives a unique nonzero sum s, and different pairs cannot have the same sum. Therefore B_z is exactly the number of nonzero s with two-dimensional kernel. The remaining 2^k-1-B_z nonzero fibres have kernel dimension one.

Let S be the number of ordered S3 solutions (X,Y) in V^2 for the actual a6. Each fibre is either empty or a coset of its classified kernel. Consequently

    S <= 2(2^k-1-B_z)+4 B_z+2^{delta_z}
       = 2^{k+1}-1+2 B_z+delta_z
       = 2^{k+1}-1+|T_z|
       <= 3*2^k-2.

The last bound is sharper than the direct quartic bound 4*2^k because there cannot be a two-dimensional kernel at every nonzero s. It is a capacity upper bound; it does not assert that a single a6 makes every fibre consistent or that equality is attained.

Special cases:

- z notin P_dist(V): B_z=0, so S<=2^{k+1}-1+delta_z<=2^{k+1}.
- z notin P(V): B_z=delta_z=0, so S<=2^{k+1}-1.
- delta_z=0 generally: |T_z| is even and <=2^k-2, hence S<=3*2^k-3.

## Solver invariants available without closure computation

These are exact semantic checks for the direct fibre solver and dataset labeling:

1. For s!=0 the n-by-k matrix rank is k-1 or k-2, with rank k-2 exactly when that s has a distinct-product representation of z. The k-2 alternative requires k>=2.
2. For s=0 its rank is k-delta_z.
3. A consistent nonzero fibre has exactly two or four solutions, grouped into swap pairs (X,Y) and (Y,X), since replacing X by X+s exchanges the two coordinates.
4. A consistent zero-s fibre has one or two diagonal solutions. Therefore the parity of the total ordered solution count equals the parity of the diagonal count. Nonzero fibres contribute an even number.
5. If the solver's exact count is S and its diagonal count is H, then the number of unordered solutions is (S+H)/2. Do not compare an ordered count with an unordered count in certificate acceptance.
6. The pair-count invariant |T_z|=2B_z+delta_z independently checks that distinct-product and square-product labels agree.
7. Product-profile labels depend on V and z but not a6. Fibre consistency and actual solution counts do depend on a6; labels must not be treated as unsatisfiability certificates.

Suggested prospective labels, not implemented here: `factor_base_target_product_member`, `factor_base_target_distinct_product_member`, `factor_base_target_square_member`, `distinct_product_pair_count`, `nonzero_fibres_kernel_dim_2`, `zero_fibre_kernel_dimension`, and `proved_lfd_upper_bound`. Any `proved_lfd_upper_bound` label must bind the exact system convention including field equations and cite the reviewed normal-form theorem. Missing product-set checks are unknown, not false.

## Research implication

This creates an explicit control stratum for the fixed-m=2 program: product-excluded targets have a proved one-degree smaller all-instance upper bound, and their fibre ranks/count capacities are known without a closure engine. It does not show these controls have low constant LFD, that they are statistically representative, or that the complementary product-rich stratum has growing LFD. For an unboundedness proof, a candidate family must still supply a growing lower bound below its applicable upper bound.

Sources inspected: the exact S3 and closure conventions in `/home/ec2-user/crypto-autoresearcher/analysis/semaev-m2-last-fall-degree/theorem-dossier.md`; the newly derived all-instance normal-form bound in `general-m2-time-bound.md`. All algebra in this note is displayed directly rather than attributed to an uninspected external reference.
