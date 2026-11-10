# Exact finite feasibility contract for closed-kernel LFD certificates

Date: 2026-11-09. Status: source-only algebraic construction and proofs. No solver, build, experiment, or cloud execution. This contract parameterizes the full bounded-degree closure condition; it is not an initial-Macaulay-only relaxation. It gives a finite search interface, not a construction of an infinite hard Semaev family.

## 1. Fixed input and target statement

Fix the normalized Boolean coordinate system F=(f_1,...,f_r) of a specified m=2 Semaev instance over K=F_{2^n}, with factor-base dimension k, N=2k variables, and D>=2. Let B=F_2[x_1,...,x_N]/(x_i^2+x_i). The input contract must bind n, irreducible modulus, ordered V basis, z,a6, coordinate basis, all Boolean equation coefficient vectors, D, and the exact normalization convention. Changing the coordinate basis preserves the relevant W_D at D>=2; no low-cap FFD invariance is assumed.

Let M_D be the ordered set of squarefree monomial masks of degree <=min(D,N), M=|M_D|, and L=|M_{D-1}|. A mask m represents product_{i in m} x_i, and multiplication by x_i is mask union m|{i}. Every generator here has degree <=2<=D.

The desired certificate is a linear map C:B_{<=D}->F_2^q such that:

1. C(f_j)=0 for every supplied equation;
2. C(x_i u)=0 whenever deg(u)<=D-1 and C(u)=0;
3. C(1)!=0;
4. rank C=q (so q is a certified codimension lower bound).

These imply W_D(F) subset ker C, hence 1 notin W_D and codim(W_D) >= q. Kernel containment is the essential direction.

## 2. Bilinear equations encoding ALL closure constraints

Fix a candidate positive q. Introduce binary unknowns:

- a vector c_m in F_2^q for every monomial m in M_D (the columns of C);
- a q-by-q matrix T_i for each variable x_i;
- a matrix R of size M-by-q, a right inverse of C.

Impose the following equations over F_2:

(A) c_empty=e_1, where e_1 is the first standard basis vector.

(B) For each generator f_j=sum_m f_{j,m} m,

    sum_m f_{j,m} c_m = 0.

(C) For each i=1,...,N and each m in M_{D-1},

    T_i c_m = c_{m union {i}}.

(D) C R = I_q.

Every scalar equation has degree at most two in the unknown bits. If encoded as an ordinary polynomial system, append a Boolean field equation for each unknown. As a Boolean SAT instance, the bit domain is intrinsic; multiplication is AND and addition is XOR, with any auxiliary gate encoding explicitly bound.

The raw unknown count is 2Mq+Nq^2 bits. The displayed vector/matrix equalities give q + rq + NLq + q^2 scalar equations before removal of redundancies or gate conversion. These counts are source formulas, not measured solver costs.

**Why this is exact (derived).** Given a solution, take any u=sum_{m in M_{D-1}} u_m m with C(u)=0. Then

    C(x_i u)=sum_m u_m c_{m union {i}}
            =T_i sum_m u_m c_m
            =T_i C(u)=0.

Thus (C) enforces closure on every low-degree kernel vector, not just on generator multiples or a presumed kernel basis. (B) enforces generator containment, (A) separates 1, and (D) proves surjectivity.

Conversely, suppose a full closed-kernel certificate C of rank q exists. On Q_low=C(B_{<=D-1}), define T_i(C(u))=C(x_i u). This is well defined exactly because of kernel closure. Extend each T_i arbitrarily to an endomorphism of F_2^q. It satisfies (C). Surjectivity gives a right inverse R. Since C(1)!=0, a change of quotient basis makes C(1)=e_1 without altering any certificate property, yielding (A). Thus the finite feasibility system is equivalent to rank-q closed-kernel certificates.

Normalization (A) loses no valid certificate. In fact, (C) and rank(C)>0 already force C(1)!=0: inducting over monomials shows every c_m is obtained by repeated T_i action on c_empty, so c_empty=0 would make C zero.

## 3. What MUST NOT be imposed on the T_i

The T_i are extensions of partial multiplication maps. They need not commute or be idempotent on the entire quotient space. Imposing globally

    T_i T_j=T_j T_i and T_i^2=T_i

would make every nonzero feasible certificate evaluate at an actual Boolean solution. It would therefore destroy the intended unsatisfiable-instance lower-bound search.

The true constraints imply local identities only where degree permits. For any monomial m of degree <=D-2,

    (T_i T_j+T_j T_i)c_m=0,
    (T_i^2+T_i)c_m=0.

They do not require these matrices to vanish on arbitrary vectors outside the low-degree generated image. This truncation is exactly where an unsatisfiable closed separator can live.

## 4. Precise bridges to LFD

### UNSAT case

If a separately verified proof establishes that F has no Boolean solution, any feasible positive-q certificate establishes 1 notin W_D and therefore d_LFD>D under the stated closure/field-equation bridge. A certificate of nonmembership does not establish UNSAT; it must not be used circularly as its own unsatisfiability proof.

### SAT or unknown-satisfiability case: count bridge

If an independent bound S_upper on the number of Boolean solutions is valid and q>S_upper, then

    codim W_D >= q > S_upper >= |S|.

The degree-D ideal component has codimension at most |S|, so it contains a degree<=D vanishing polynomial missing from W_D. Hence d_LFD>D. An exact count is sufficient but not necessary: any rigorous upper bound strictly below q suffices. The generic bound |S|<=3*2^k-2 from the product-profile note is usable but may be too loose. Product-profile-specific bounds can be substituted when independently verified.

### Explicit missing-consequence bridge

Alternatively fix g in B_{<=D} and independently prove g vanishes on every actual solution. Add a selector vector h in F_2^q with h^T C(g)=1. This enforces C(g)!=0 and hence g notin W_D. It proves d_LFD>D without requiring UNSAT or a count. The polynomial g and its vanishing proof must be supplied independently; an arbitrary nonzero quotient column is not automatically a missing ideal consequence. Since a finite Boolean ideal is its solution-set vanishing ideal, universal vanishing is the required membership statement.

If the proof uses a high-degree ideal representation g=sum a_j f_j plus field equations, that is an acceptable separate membership witness. The representation must not already assume a bounded-degree derivation contradicting the separator.

## 5. Completeness and non-completeness of bounded searches

If 1 notin W_D, the exact quotient B_{<=D}/W_D gives a feasible certificate with q=dim(B_{<=D}/W_D). Conversely every feasible certificate proves 1 notin W_D. Therefore searching all 1<=q<=M is mathematically complete for this nonmembership question.

For an unsatisfiable instance, the filtration-plateau lemma gives q>=D, so q<D can be omitted in that case. Also q<=M-rank(span F) is necessary by (B). These are pruning conditions, not sufficient conditions.

A failed search at one q, or even every q below a practical cap, is not a refutation: a smaller-dimensional closed quotient need not exist just because a larger one does. Feasibility is not claimed monotone in q. Arbitrary projection of a vector certificate can enlarge its kernel and violate closure. A timeout or resource failure is neither infeasibility nor LFD upper-bound evidence.

To establish infeasibility, a solver must return an independently checked proof for the complete encoded finite system and that fixed q. To infer 1 in W_D by exhaustion, all relevant q must be covered or an equivalent rank-free complete formulation must be proved. No such execution is performed here.

## 6. Interaction with the fixed-m=2 normal form

The general normal-form proof gives d_LFD<=k+3, with sharper bounds under stated trace/product hypotheses. Thus at D>=k+3 a certificate with q>|S| cannot exist, although evaluation-type certificates of q<=|S| can exist for SAT instances. In the UNSAT case the earlier bound k+2 implies no positive-q feasible certificate at D>=k+2.

The theorem therefore supplies exact positive/negative semantic controls for a future implementation, but not an unbounded lower bound. A genuinely growing UNSAT separator family must choose D growing below k+2 and must retain filtered quotient growth to degree D-1. A SAT separator family must exhibit an actual excess over solution-set dimension or an explicit missing vanishing consequence.

## 7. Useful prospective export contract

A future dataset record should include:

- immutable normalized instance and variable/monomial ordering hashes;
- n,k,N,D,q and the claimed bridge type;
- certificate C bytes/hash and, optionally, T_i/R feasibility witnesses;
- exact generator reconstruction identity;
- independent direct-check results for rank, C(1), generator annihilation and kernel closure;
- filtered ranks dim C(B_{<=e}) for e=0,...,D;
- UNSAT proof or solution-count upper-bound proof or explicit missing-g membership proof;
- solver outcome separately labeled as candidate/checked/infeasible/timeout, with the complete encoded formula and proof hashes when relevant.

The independent verifier should reconstruct F and check the mathematical C0–C3 predicates directly, rather than merely trusting the search solver's equations or T_i witnesses. Existing cert_check.py already checks the kernel condition directly; exported T_i/R can be supplementary witnesses and debugging aids. Search candidate artifacts must not be labeled rigorous LFD bounds until the bridge is verified as well.

The finite equation emitter is now implemented in encode_certificate.py and checked on fixed software controls. No search solver, direct large-certificate replay, learned predictor or random-family probability follows from that implementation. Its allocation caps and formula-size counts are not solver-runtime bounds.

## 8. Nontrivial deductions and remaining construction gap

The construction makes the source of difficulty precise: an unsatisfiable certificate is a nonzero truncated cyclic representation of Boolean multiplication that is locally commutative/idempotent on low-degree images but cannot extend globally to a nonzero Boolean algebra module. A family proof must construct these partial actions for increasing D while preserving the actual Semaev generator relations. Global commuting actions collapse to genuine solutions, so ordinary evaluation at fictitious field points is not a shortcut.

The current finite certificates provide feasible examples at specific D and exact inputs. They can be converted to this contract by extending their well-defined partial actions and choosing a right inverse, without changing the underlying proof. No parameter-uniform rule for those actions has been derived here. This is the precise remaining step toward an infinite family.

Sources: `certificate-route.md` (rank-one and plateau lemmas); `general-m2-time-bound.md` (all-instance normal form); `factor-base-product-obstruction.md` (solution capacities); historical `analysis/semaev-m2-last-fall-degree/theorem-dossier.md` (definitions and bridges); `/home/ec2-user/lfd-streamed-d5-20261101/analysis/semaev-m2-last-fall-degree/verify/cert_check.py` (independent direct checker contract). No external literature priority or novelty claim is made.
