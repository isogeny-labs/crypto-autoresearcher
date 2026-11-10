# Certificate route to unbounded fixed-m=2 Semaev LFD

Date: 2026-11-09. Scope: proof research, source inspection and exact arithmetic from saved records only. No new solver run, certificate replay, compilation, cloud job or experiment. This note proves certificate-structure lemmas below; it does not prove unbounded Semaev LFD.

## Sources actually inspected

1. `/home/ec2-user/crypto-autoresearcher/analysis/semaev-m2-last-fall-degree/theorem-dossier.md`: definitions of Boolean closure W_D, Propositions 1.1–1.4, Theorem 2.1, Theorems 3.1–3.2. This supplies the system and the unsatisfiability/solution-count bridge.
2. The same directory's `results/verification.md`: independent reproduction of R35a, its two restricted branches, Q35a and C19a; explicit polynomial-subspace closure profiles.
3. `/home/ec2-user/lfd-streamed-d5-20261101/analysis/semaev-m2-last-fall-degree/verify/cert_check.py`: certificate contract C0–C3 and implementation. This is the later separately written quotient-map checker; no checker execution is claimed here.
4. `/home/ec2-user/lfd-streamed-d5-20261101/analysis/semaev-degree-five-quotient-lift/README.md` and `reports/n45-poly04-d5-concurrent-001/report.md`: larger certificate panel and an inconclusive D5 quotient attempt. The latter reports relation rank 13,688 on 13,688 working coordinates and `projection_kills_one`, explicitly not an upper bound. Old live-job statements in that README were not checked against live infrastructure and must not be treated as current.

## Exact certificate obligation

Let B=F_2[x_1,...,x_N]/(x_i^2+x_i), D>=2, and F have degree at most D. A certificate is a linear map pi:B_{<=D}->Q with:

- pi(f)=0 for every f in F;
- pi(x_i u)=0 whenever pi(u)=0 and deg(u)<=D-1;
- pi(1)!=0.

The checker additionally proves pi is onto its claimed q-dimensional target. Writing U=ker(pi), the first two properties imply W_D(F) subset U. Thus pi(1)!=0 proves 1 notin W_D; q gives a lower bound on codimension, not necessarily the exact codimension. For an unsatisfiable Boolean system this proves LFD>D. For a satisfiable system an independent exact solution count s and q>s suffice for the dossier's lower-bound bridge.

A generalization of the certificate to an infinite family needs a formula for pi_{n,D}, valid for unbounded D, and proofs of these identities for all parameters. Fitting q from a finite panel does not supply any of them.

## Derived lemma 1: scalar closed-kernel certificates cannot refute unsatisfiability

**Statement.** If Q=F_2, pi(1)=1, and the three certificate properties hold, then F has a Boolean solution.

**Proof.** Set a_i=pi(x_i). For any g of degree <=D-1, u=g+pi(g)*1 has pi(u)=0. Closure gives 0=pi(x_i g)+pi(g)pi(x_i), so pi(x_i g)=a_i pi(g). Inducting over squarefree monomials yields pi(m)=m(a) for every degree <=D monomial. Linearity gives pi(f)=f(a)=0 for every f in F. Thus a is a solution. QED.

**Implication.** Taking an arbitrary single linear functional of an existing vector certificate generally destroys the kernel-closure property: its enlarged kernel need not be closed. A scalar moment/dual witness for the initial Macaulay matrix is not automatically a witness for the saturated closure W_D. This is a precise barrier to naive pseudoexpectation extrapolation. It does not rule out scalar functionals annihilating W_D; it rules out using the entire scalar kernel as the closed certificate super-space.

## Derived lemma 2: an early filtration plateau forces a solution

For a certificate pi define Q_e=pi(B_{<=e}) for 0<=e<=D.

**Statement.** If Q_e=Q_{e+1} for any e<=D-2, then F has a Boolean solution. Consequently, on an unsatisfiable system, every accepted certificate has strict inclusions Q_0 subsetneq Q_1 subsetneq ... subsetneq Q_{D-1}, and q>=D.

**Proof of plateau propagation.** Suppose Q_e=Q_{e+1}, e<=D-2. For a monomial x_i m with deg(m)<=e+1, choose h of degree <=e with pi(m)=pi(h). Then m+h lies in ker(pi) and has degree <=D-1, so pi(x_i m)=pi(x_i h) belongs to Q_{e+1}=Q_e. Thus Q_{e+2}=Q_e. Induction propagates equality to Q_D.

**Multiplication operators.** On Q=Q_D define T_i(pi(g))=pi(x_i g), choosing g of degree <=D-1. This is well defined by the kernel-closure property. The plateau supplies degree <=e<=D-2 representatives for every vector. Hence T_iT_j(pi(g))=pi(x_i x_j g)=T_jT_i(pi(g)), and T_i^2(pi(g))=pi(x_i^2g)=T_i(pi(g)). The intermediate products have degree at most D, so no operation beyond the certificate domain was used.

Put v=pi(1)!=0. For every monomial m of degree <=D, pi(m)=m(T)v, and thus f(T)v=0 for every f in F. The commuting idempotents T_i yield mutually orthogonal projectors P_a=product_i [T_i if a_i=1, I+T_i if a_i=0], indexed by a in F_2^N, whose sum is I. Some P_a v is nonzero. On that component f(T) acts as f(a), so f(a)P_a v=0 forces f(a)=0 for every f. This gives a Boolean solution. QED.

For an unsatisfiable certificate Q_0 has dimension 1 and no plateau can occur before Q_{D-1}, hence dim Q_{D-1}>=D and q>=D.

**What this does not establish.** This is a necessary condition on an unbounded certificate family, not its construction. A sequence with D fixed at 4 and q growing does not prove LFD grows. It shows why a bounded-dimensional closed quotient cannot certify arbitrarily large refutation degree on unsatisfiable systems.

## What the existing profiles say

From the exact closed W4 profiles in verification.md, q_e=dim(B_{<=e})-dim(W4 intersect B_{<=e}) gives:

| instance | N | q_0 | q_1 | q_2 | q_3 | q_4 |
|---|---:|---:|---:|---:|---:|---:|
| R35a | 36 | 1 | 36 | 562 | 3922 | 5287 |
| P45a | 46 | 1 | 46 | 858 | 7312 | 12742 |

These are exact arithmetic from recorded closure profiles, not new measurements. Both obey strict filtration growth. R35a nevertheless has exact LFD 5, demonstrating concretely that a large degree-4 quotient need not survive even one more degree. The filtered ranks are better hypothesis inputs than q_4 alone, but cannot extrapolate through D=5.

## Failed infinite-family shortcuts

### Extension-field replication does not amplify a certificate

Embed K=F_{2^n} in L=F_{2^{rn}}, retaining the same V and parameters a6,z in K. Relative to a basis of L extending a K basis, S3(X1,X2,z) still takes values in K. Its L-coordinate equations are the old equations together with zeros. Any other coordinate basis is an invertible F_2 linear recombination, so the span of descended equations and every W_D remain unchanged. The LFD is unchanged. This yields infinitely many presentations of the same Boolean problem, not unbounded LFD. It also fails the diagonal requirement dim V=ceil(rn/2).

### Disjoint copies of an unsatisfiable example do not add refutation degree

The union of disjoint copies contains an original inconsistent subsystem. Its known degree-5 refutation remains valid, giving degree at most 5 regardless of the number of copies. Moreover such a union has not been embedded into a single m=2 Semaev equation. Tensorizing R35a is therefore not an amplification proof.

### Enlarging V preserves a hard restriction only conditionally

Restricting the coordinates of new basis directions to zero maps every degree-D derivation in the larger system to a derivation in the original system for D>=2. Thus a hard restricted system supplies a lower bound for refutation of the larger system *if the larger system is also unsatisfiable*. Enlarging V can introduce solutions, and no mechanism here preserves unsatisfiability or raises the inherited bound above 5. Therefore nesting V alone does not prove unboundedness.

### Degree-five quotient failure is not an upper bound

The later quotient-lift report explicitly says `projection_kills_one` gives neither a degree-six lower bound nor an upper bound. Its provisional quotient may impose extra relations; disappearance of pi(1) need not show 1 in the exact W5. Such rows must remain inconclusive when selecting a family.

## Concrete proof route worth pursuing

Seek a parameterized *vector-valued filtered quotient*, with unbounded filtration depth rather than merely unbounded vector dimension. Use the Artin–Schreier reformulation in Theorem 2.1 to enforce the known trace relation and cubic falls from the outset. A candidate must specify:

1. an explicit sequence (n_j,V_j,a6_j,z_j), with dim V_j=ceil(n_j/2), nonzero a6_j,z_j, and irreducible field presentations;
2. a proof of unsatisfiability (or a uniform exact/upper solution count for the satisfiable route);
3. a growing D_j and a symbolic formula for pi_j on every monomial of degree <=D_j;
4. generator annihilation and full kernel-closure, not just annihilation of initial Macaulay multiples;
5. pi_j(1)!=0, or codimension exceeding the solution bound;
6. ideally specialization to the existing finite certificates, up to an invertible change of quotient coordinates.

The surviving unproved step is item 3 together with item 4. No presently inspected certificate supplies a parameter-uniform multiplication rule. The most direct next source-only analysis is to extract canonical low-degree multiplication maps from retained certificates and look for a formula invariant under basis change; this must be separately resource-bounded before large binary artifacts are loaded or eliminated. Existing certificates are valuable examples and controls, not an infinite-family construction.
