# Compressed quadratic canonical range over an odd prime

2026-10-31. New derivation, unreviewed. No implementation or solver/suite execution. This proposal is outside the current authenticated-interface contract and independent-review scope.

Let p>3 be prime, b=ceil(log2 p), t=p-1, and h=popcount(t). Work in the Boolean quotient over F_p. Write the one-bit positions of t as j1>j2>...>jh. Since t is even, jh>=1; since b is minimal, j1=b-1. Define s1=x[j1] as an alias, not a new variable. For r=2,...,h introduce s[r] and impose

    s[r] - s[r-1] x[jr] = 0.

For each zero-bit position j of t, let r(j) be the number of one-bit positions above j. This number is at least one because the highest threshold bit is one. Impose

    s[r(j)] x[j] = 0.

There are h-1 auxiliary Boolean variables, h-1 recurrence equations and b-h forbidden equations, hence b-1 equations in total, all of degree at most two. No boolean field equations are included in these counts: the ambient Boolean quotient already supplies them. In an ordinary polynomial ring they must be accounted for explicitly.

## Exactness and unique extension

For any fixed input bits, the recurrences determine s[r] uniquely as the product of x[jq] for q<=r. These values are Boolean. If the represented integer X exceeds t, at the highest differing position j one has t[j]=0 and x[j]=1. Every higher one-bit of t then has x=1. Consequently s[r(j)]=1 and the forbidden equation at j fails.

Conversely, suppose a forbidden equation at a zero position j fails. Then x[j]=1 and all higher one-bit positions of t have x=1. At the highest position where X and t differ, a difference with t=1 and x=0 cannot lie above j. Either some higher zero-bit position already has x=1, or j itself is the highest differing position. In both cases X>t. Thus all equations hold exactly for X<=t. Together with recurrence uniqueness, the projection to input bits is a bijection onto {0,...,p-1}.

Replacing a canonical-domain predicate in any other Boolean polynomial system by these equations preserves its projected canonical solutions and the number of its original auxiliary witnesses: the new extension is unique. This statement requires all pre-existing equations and projections to be preserved. It does not say the polynomial ideals are equal in rings with different variables.

## Relation to the earlier full-prefix draft

The earlier construction used b-1 new prefix-equality bits and (b-1)+(b-h) equations. At a threshold zero bit, its forbidden equation e*x[j]=0 already gives e*(1-x[j])=e, so that prefix state need not change. At the highest one bit, the new state equals that bit and can be aliased. Removing those states gives the construction above. It saves b-h auxiliary bits and b-h equations relative to that specific full-prefix draft. This is an exact syntactic count, not a benchmark or degree-of-regularity assertion.

Examples derived directly from the formulas:
- p=5, t=100: no auxiliaries; x2*x1=0, x2*x0=0.
- p=7, t=110: one auxiliary s=x2*x1; s*x0=0.
- p=11, t=1010: one auxiliary s=x3*x1; x3*x2=0, s*x0=0.
- p=17, t=10000: no auxiliaries; x4*xj=0 for j=0,1,2,3.

## Certificate integration obligations

Keep the existing comparator CNF for SAT propagation. Bind these polynomial generators, bit order, p and aliases to the trusted public descriptor before using a polynomial refutation. Place new state variables after projected variables. Charge construction, generator authentication, states, rows and certificate checking. Independent review must challenge reversed bit order, missing forbidden equations, omitted recurrence, aliases and noncanonical inputs. A future frozen comparison must retain identical complete projected models. No integration, experiment, novelty claim or performance claim is made here.
