# Prefix extraction refinement: incidence sweep and counterexamples

Status: written derivation, not implementation, not independently accepted. No candidate execution. Extends derivation.md without changing it.

## A single forward sweep

Canonical input generators f_j are sums of nonzero coefficients c_t times square-free monomials M_t. Let s be the number of generators, T be total terms and I=sum_t |M_t| the term-variable incidences. Retain original terms separately even if their residual contributions later cancel. For each original term store generator index, coefficient, current residual mask, and a live flag. Build a bucket B_i containing original term IDs whose masks contain variable i. Maintain for each generator a dictionary D_j from residual masks to the sum of live term coefficients modulo p, deleting zero entries, and a count of nonzero dictionary entries with nonempty masks.

Initially D_j=f_j. Check whether a generator is already a nonzero constant. Then process variables i=0,...,n-1. For each live term in B_i, subtract its coefficient from its current dictionary key. If a_i=0, mark the term dead. If a_i=1, remove i from its current mask and add its coefficient at the new key. Do not test the predicate between these updates or before the entire variable bucket is processed. Maintain a touched-generator set for the batch; only these generators can change their qualification status. Maintain a set of qualifying generators, initialized by one scan of all s generators and updated only after the full batch. After the whole B_i batch, test this set for a generator with zero nonconstant entries and a nonzero constant entry. If one exists, return depth i+1 with that generator and constant. Stop at the first qualifying depth. No output means the full assignment is polynomial-valid.

Invariant proof: after depth d, each live original term contributes c_t times its original monomial with the first d variables substituted. A term becomes dead exactly when its original monomial contains a fixed zero. Therefore each D_j is exactly the canonical restricted polynomial R_d f_j. Initialization establishes this invariant at d=0. Updating all terms containing the next variable implements precisely that substitution; other terms are unchanged. Summing equal residual keys gives coefficient cancellation modulo p. The post-batch test is therefore exactly P(d). Testing depths in order returns the same d* as binary search. Term IDs that cancel in the dictionary must not be deleted from their incidence schedule without an alternative aggregation proof.

With arrays of n buckets, there are O(n+s+T+I) bookkeeping operations and O(T+I) coefficient updates (at most two per live visited incidence plus initialization), with O(s) initial generator checks. Dictionary operations have expected constant probe count only under the usual hash-map assumption. This is not an O(n+s+T+I) bit-time claim: monomial keys occupy up to n bits, field residues up to log p bits, and allocation, key hashing, equality, mask updates and modular arithmetic must be charged. Space is O(n+s+T+I) entries, plus their bit lengths. Constructing incidence lists from integer masks also has a cost; do not hide it behind unit-cost bit enumeration. A sorted sparse event schedule can avoid n empty buckets at additional ordering cost, which is a different implementation option.

The sweep avoids rerestricting all terms at O(log n) binary-search queries, but it adds incidence storage and mutation overhead. No empirical superiority follows. It is intended as an exact alternative, with binary search retained as a simple independent reference specification. The final certificate still requires the full multiplier-vector format and independent all-generator restriction/checking. Neither the producer's residual dictionary nor the chosen d* is trusted by the verifier.

## Exact examples and limits

1. Strict cancellation benefit: for n>=2, f=x_0+x_(n-1)-x_0*x_(n-1). On any full assignment with a_0=1, R_1 f=1. R_0 f is nonconstant, so d*=1. The syntactic support bound is n. The prefix x_0=1 excludes 2^(n-1) Boolean full assignments, while assignments x_0=x_(n-1)=0 satisfy this equation. This identity is valid over every prime field. It is an illustrative family, not an elliptic-curve workload result.

2. No strict gain: f=x_(n-1), with a_(n-1)=1, has d*=n in the fixed variable order. A different variable order could change the result, but the current projection/checker order is fixed and no reorder is proposed here.

3. Not globally shortest proof: over F_3, f=1+x_0 has no Boolean root. Before any restriction, f is nonconstant, so the constant-inverse family requires d*=1. Yet (1+x_0)^2=1 in F_3[x_0]/(x_0^2-x_0), giving a nonconstant multiplier refutation at depth0. Thus shortest-in-family is essential.

4. Auxiliary boundary: take one projected bit x_0 and one auxiliary bit x_1, with f=x_1. The invalid full assignment (0,1) yields d*=2>m=1. The learned clause excludes only (0,1). The projected value x_0=0 still has valid witness (0,0). Truncating the clause to depth1 would be unsound.

5. Batch boundary: f=1-x_0*x_1 and a_0=1. While moving the x_0*x_1 term during a sweep, subtracting its old contribution temporarily leaves constant1 before adding -x_1. The correct post-batch residual is1-x_1, which has the root x_1=1. Testing after only the subtraction would learn an unsound clause.

6. Non-prime coefficient ring: the inverse step requires a field or an independently checked unit. A nonzero residue is not enough over a composite modulus (e.g.2 modulo4). The public adapter does not prove primality; retain the prime-field input assumption.

## Original-ring and projected scope

Use the restricted certificate in the unchanged checker. The telescoping original-ring identity in derivation.md additionally explains why substitution witnesses can be transported, with product degree at most deg(f_j). This is a local contradiction identity after adjoining fixed-variable equations, not a bound on the global system's degree of regularity.

All true full roots survive each learned clause. Consequently their projected set survives, even when several auxiliary witnesses share one projection. Complete enumeration still requires independent coverage checking and model witness verification; censored output is not made complete by shorter clauses.

## Prior work and novelty boundary

Deharbe, Fontaine, Le Berre and Mazure, Computing prime implicants (FMCAD2013), https://www.verit-solver.org/papers/fmcad2013.pdf, studies shrinking models into prime implicants using solver data structures, including clause and cardinality cases. This establishes prior work on smaller sufficient assignments; it does not directly prove this finite-field coefficient-dictionary sweep. The present construction minimizes only along one fixed prefix chain and only within the constant-residual witness family. No claim of new general prime-implicant computation is made.
