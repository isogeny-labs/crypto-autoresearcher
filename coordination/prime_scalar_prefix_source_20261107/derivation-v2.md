# Cancellation-aware certified prefix fallback — staged derivation

Status: staged mathematical derivation with independent written critique completed; no implementation, execution, or official claim promotion. This extends the completed source report without modifying that report, its task, or any published source.

Let F=(f_1,...,f_s) consist of canonical multilinear Boolean-coordinate polynomials over F_p, represented by square-free monomial masks and coefficients modulo p. Variables x_0,...,x_(n-1) have the existing fixed order. A full Boolean assignment a is polynomial-invalid when some f_j(a) != 0. Domain-invalid but polynomial-valid assignments alone do not satisfy this premise.

Write R_d f for substitution x_i=a_i for i<d, collected canonically modulo p. Define P(d) to mean that some R_d f_j is a nonzero constant. If P(d), its witness remains the same nonzero constant under every further substitution along a. Thus P is monotone nondecreasing on integer depths0,...,n. Invalidity establishes P(n); P(0) can hold. This is stronger than a syntactic support bound because canonical coefficient collection admits cancellation.

## Shortest prefix in this certificate family

Check P(0). If false, keep lo=0 with P(lo)=false and hi=n with P(hi)=true. Repeatedly evaluate P(floor((lo+hi)/2)); update hi on true and lo on false until hi=lo+1. Return d*=hi and a witnessing j with R_d* f_j=c != 0. With P(0) true, return d*=0. If the full assignment is not already known polynomial-invalid, first evaluate P(n); false means this fallback is inapplicable. The empty-variable case n=0 is handled entirely by P(0).

At each predicate evaluation, visit each generator's monomials. Delete terms containing a fixed zero variable; clear fixed-one variables from masks; add coefficients with identical residual masks modulo p; delete resulting zero coefficients. A generator qualifies exactly when its canonical result has only mask0 with nonzero coefficient. Checking surviving syntactic supports without collecting coefficients is insufficient.

For example f=1+x_1-x_0*x_1 restricts to1 after a_0=1, although syntactic support reaches x_1. At a_0=0 it remains1+x_1, so the shortcut depends on the actual prefix. This illustrative identity holds over every prime field, including characteristic2, with coefficients interpreted modulo p.

The search uses O(log(n+1)) predicate evaluations plus endpoint handling. If T is total input monomial count and s is the generator count, a direct implementation visits O(T(1+log(n+1))) monomials including endpoints, with O(s(1+log(n+1))) generator-header overhead and at most the monomial-visit order of coefficient updates; dictionary/key and n-bit mask costs are separate, not unit-cost guarantees. Evaluate one generator at a time to bound transient dictionaries by its term count. Charge final all-generator restriction, inverse, complete multiplier-vector construction and unchanged certificate checking separately. The finding is the shortest prefix admitting a certificate in which one restricted original generator is itself a nonzero constant and receives its scalar inverse as multiplier, not the shortest polynomial-calculus refutation, arbitrary-support explanation, clause, or domain-assisted obstruction. No worst-case strict improvement over d=n is claimed.

## Certificate transport

At d*, set q_j=c^(-1), all other q_i=0. Then sum_i q_i R_d* f_i=1. This is exactly a multiplier vector for the current restricted-generator identity schema. The unchanged checker must independently restrict every original generator at the claimed prefix and check the identity before emitting the clause.

An explicit original-ring transport is also available. Put f^(k)=f with the first k coordinates substituted. Multilinearity gives f^(k)-f^(k+1)=(x_k-a_k) g_k, where g_k is the coefficient of x_k in f^(k). Telescoping yields f_j-c=sum_(k<d*) (x_k-a_k)g_k, so

1 = c^(-1) f_j - sum_(k<d*) c^(-1) g_k (x_k-a_k).

This identity is in the polynomial ring for the chosen multilinear representative; if conversion from other representatives is needed, Boolean ideal identities must be retained explicitly. Its degree is at most deg(f_j), but this local identity does not establish degree-of-regularity reduction or completeness of a bounded-degree algorithm. Existing checker compatibility uses the restricted identity and needs no schema change or transported multiplier construction.

## Clause and complete projection semantics

The learned clause is the existing ordered prefix blocker: for each i<d*, use NOT x_i when a_i=1 and x_i when a_i=0. Its falsifying cylinder is exactly the2^(n-d*) full Boolean assignments extending that prefix, all polynomial-invalid. At d*=0 this fallback emits an empty clause using a nonzero-constant original generator. The general checker can also accept an empty clause from other certificates, for example f_1=x_0 and f_2=1-x_0 with multipliers both 1.

Assume the first m bits are projection coordinates, as required by the current adapter. If d*<=m, the invalid cylinder contains every auxiliary extension of every projected assignment sharing that prefix; these projected assignments may safely be excluded. If d*>m, the clause fixes some auxiliary bits and excludes only those full extensions. It does not establish that the whole projected assignment has no other valid witness. Keep it as a learned full-assignment prefix; never convert it into an m-bit projection blocker.

A verified valid full model may independently justify the existing model-projection blocker after recording its witness. The adapter separately checks such models, forbids duplicate projections, and checks coverage by the union of invalid prefixes and recorded model projection cylinders. The proposed fallback changes only sound invalid-prefix explanations. It neither makes a censored run complete nor supplies full projected-set equality without complete coverage and witness verification. Aux-bound domain restrictions can reduce the number of domain-admissible assignments in a cylinder;2^(n-d*) is ambient Boolean coverage only.

## Independent critique route and next obligations

The independent review assignment was to receive this note and the exact public polynomial/prefix/projection contract, without producer control outputs. Request adversarial review of monotonicity, canonical cancellation, binary-search endpoints, the invalidity premise, transport signs, Boolean-ring interpretation, projected/auxiliary boundary and cost accounting. Ask for explicit counterexamples to overbroad versions of each claim, including a d>m prefix with a different valid auxiliary witness. The critic performs written reasoning only, no candidate imports, solver calls or scientific slot use. Keep the existing blinded software reviewer and reserved slot separate.

Any implementation would require a new exact source scope and subsequent separately authorized validation. Preserve all106coordinate+6coefficient comparisons, all five leads, complete projected-model equality, reconstruction/certificate cost and complete chart handling. The exhausted producer allowance remains zero. No claim of novelty, empirical speedup or global regularity reduction is made here.
