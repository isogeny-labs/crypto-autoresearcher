# What would establish a summation-polynomial obstruction?

Status: proof-search specification and elementary written derivations. No new
Lean-checked theorem, signed PCC standing, solver lower bound or security claim
is asserted. All new derivations await independent review [pcc:unverified].

## Specify the claim before trying to prove it

“Summation polynomials never work” is false if work means finding correct
decompositions: exhaustive search does so. Replace it with a precise complexity
statement. Separate four possible targets:

1. This exact implementation cannot beat this matched baseline on a fixed panel.
   A complete finite comparison decides that panel, not all future sizes.
2. A named presentation/solver family cannot achieve sub-square-root expected
   total work on a stated infinite family. This requires a genuine lower bound.
3. A specified constant-solving-degree hypothesis is false. A faithfully encoded
   counterexample suffices; it does not settle target 2 for other solvers.
4. Every coordinate-aware summation-polynomial-based algorithm fails to beat
   rho. This is a broad unresolved complexity statement. “Based on” must be
   defined; encoding a solution as polynomial constraints does not by itself
   restrict the algorithms allowed to find it.

Define r as prime subgroup order; n=ceil(log2 r); distribution over nonsingular
curves/subgroups and rational targets; success probability; uniform/nonuniform
algorithms; RAM/bit/field-operation model; field-operation bit costs; memory and
advice; reusable preprocessing and target count T; allowed arities and encodings;
uniformity of parameters; and whether the assertion is worst-case or average-case.
Exclude or explicitly stratify anomalous curves and other known weak classes.
No one universal conclusion follows from a result on one curve family.

## P1: exact relation-mass lemma (first formalization target)

Let H be a finite group written additively, |H|=r>0. Let F be a finite set of
actual group points, |F|=B, and m>=1. F may include both signs, but count its
actual elements exactly once. Use ordered m-tuples with repetitions. For R in H,
define N_m(R)=|{(P1,...,Pm) in F^m: P1+...+Pm=R}|, with a fixed parenthesization.
Then

    sum_(R in H) N_m(R) = B^m.

Proof: the tuple-to-sum function partitions its domain F^m into disjoint fibres.
Summing the fibre cardinalities counts every ordered tuple exactly once. No
elliptic-curve or pseudorandomness hypothesis is required. If R is uniform on H,
E[N_m(R)]=B^m/r. If s is the number of targets with a nonempty fibre, then
s<=min(r,B^m), hence Pr[N_m(R)>0]<=min(1,B^m/r).

This does NOT say that probability equals mean tuple count. Nor does it imply
independent relation rows or uniform coverage among successful targets.
Do not divide by m! without dealing with repeated points, signs and stabilizers.
Multisets, signed x-coordinate solutions, points in a twist and rejected
subgroup lifts are different objects and require explicit correspondence lemmas.

Formal target: a finite type for H, finite tuple domain, cardinality of fibres
and a probability corollary over the uniform distribution. Reuse mathlib's finite
fibre/cardinality machinery; pin its toolchain and audit axioms. The Python
reference tests below are development checks only, not a formal proof.

## P2: a conditional full-cost floor for a restricted collection model

Assume independent uniform targets R_i in H, a fixed factor base F, a complete
oracle reporting success exactly when N_m(R_i)>0, and a cost at least c0>0 for
EVERY attempted query. Suppose the algorithm needs K successful queries before
it can finish, regardless of any additional rank/dependence losses. Write setup
cost A>=0. If s>0, the expected number of queries to K successes is Kr/s, so

    E[work] >= A + c0*K*r/min(r,B^m).

Proof: each trial has constant success probability s/r; the waiting times between
successes are geometric with expectation r/s, and linearity of expectation gives
Kr/s. Substitute the support bound in P1 and the per-query lower bound. If s=0
and K>0, the collection never succeeds. K=0 is a separate trivial case.

This assumes iid queries and a fixed required K, not adaptively selected targets,
early known-log termination, coverage-changing base changes, retained global
state or conditional query costs. A lower bound c0 on every query cannot be
replaced by a mean measured on a different target distribution. A particular
linear-algebra model may prove K>=C, where C is its number of genuinely unknown
independent base columns; do not assume C=B after orbit compression or known-log
reductions. Prove the relation-system bridge explicitly.

Theorem goal for one algorithm family: prove A(B,m,r), c0(B,m,r), K(B,m,r)
and the query-distribution assumptions for EVERY allowed choice of B,m and its
preprocessing. Then minimize the lower bound over those choices, add necessary
linear-algebra/descent/storage costs, and compare with a stated rho cost model.
An oracle-cost guess or a fitted finite slope does not establish this theorem.

## P3: direct univariate membership degree (second formalization target)

For a field k and a nonzero f in k[X], if f(a)=0 for every element of a finite
set V of B distinct field elements, deg(f)>=B.

Proof: a nonzero polynomial over a field has at most its degree many distinct
roots. This remains true if V is exactly its root set. The zero polynomial is
excluded. The statement does not constrain the degree of a system with auxiliary
variables, a rational/arithmetic circuit or a compressed tower representation.
PKM2016 explicitly uses compositions of small-degree rational maps to express
large-degree membership; that paper is a countercontrol against overclaiming P3.

Formal target: bind to mathlib's polynomial root-cardinality bound and specialize
it faithfully; do not add a custom axiom containing the conclusion. This is
classical algebra, not a novelty claim.

## P4: solver/presentation lower bounds (substantial open work)

Choose ONE exact family and define its field equations, charts, monomial order,
grading, allowable specialization, preprocessing and F4/XL/Mutant closure rules.
Prove a lower bound on a necessary charged resource: dimensions actually
materialized, obligatory row operations under the chosen algorithm, or certified
time-space product. A lower bound on last-fall degree is not automatically a
lower bound on every solver's runtime. A large binomial count of possible
monomials is not proof that an implementation must materialize all of them.

For a random-target conclusion, extend beyond one adversarial family: prove that
the lower-bound condition holds with the stated probability over the target and
curve distribution. Include SAT witness extraction as well as UNSAT refutation.
Arity m=2 results do not decide m>=3. A change of variables preserving an ideal
need not preserve the solver's filtered cost. This is the principal missing
bridge in turning the current degree measurements into a no-go theorem.

## P5: broader models (open, not inherited closures)

Generic-group bounds cover their oracle model. They do not exclude algorithms
that read coordinates. The original low-degree-coordinate query conjecture in
the lab was withdrawn: tests on coordinates of large-multiplier points can have
large pulled-back degree, while a query count hides interpolation cost. A usable
replacement must charge description length/local work/preprocessing and account
for adaptive multipliers.

A k-SUM conditional obstruction needs an explicit reduction preserving input
access, implicit coordinate representation, distribution, preprocessing, memory,
success probability and cost. Statistical agreement with a matched random null
does not prove this reduction. A fixed-domain #CSP dichotomy does not automatically
apply when the field alphabet grows. Tensor-rank invariance excludes a specified
rank-reduction maneuver, not every exact contraction algorithm.

## Proof search and falsification map

| Target | First check | Artifact required | What would remain open |
|---|---|---|---|
| P1 mass/support | Tiny finite groups; permutations, repetitions and signs | Written proof + faithful Lean fibre theorem | Solver work and independent rank |
| P2 restricted collection | Nonuniform/adaptive query countermodels | Model definitions + waiting-time proof + exact algorithm bridge | Other query policies and preprocessing |
| P3 membership | Auxiliary-variable low-degree countercontrol | Root theorem specialization + axiom audit | Towers and compressed representations |
| P4 solver family | Known degree-fall/alternative-solver examples | Unconditional necessary-resource lower bound and target-distribution theorem | Other presentations and arities |
| P5 general attack class | Coordinate/interpolation and weak-curve controls | Explicit computational model and proved reduction/lower bound | Anything outside that model |

No theorem is promoted until its readable proof, Lean statement (where feasible),
dependency/toolchain pin, axioms, countermodels and independent review agree.
The original broad question remains open if only P1-P3 are completed.

## Sources and retrieval scope

- Retrieved and read: Petit-Kosters-Messeng, *Algebraic approaches for the ECDLP
  over prime fields* (PKC 2016), introduction, construction and experimental
  conclusions. Primary PDF: https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf.
  It supplies an explicit reason direct membership-degree bounds do not settle
  tower methods; its asymptotic solver analysis remains conditional/uncertain.
- Retrieved lab theorem ledger, degree-at-scale lead and corrected low-degree
  query desk report: pinned in program.json. Existing claims retain their own
  evidence standing; they are not independently re-proved here.
- Zhang-Liu ePrint 2018/795 PDF retrieval returned HTTP 403 this session.
  Its full decoder is not treated as read, implemented, or refuted.
- Shoup-style bounds and broader degree/circuit literature require a fresh
  primary-source assumption audit before a new closure theorem is asserted.
