# Complete projective-coset coverage and scalar-preserving transformations

2026-11-02 | EXP-PEXT-bf8f96 | H-PEXT-c3a11d

The prospective component now traverses complete left PGL2(Fq) cosets in PGL2(K), transports binary quartics without dropping their scalar, serializes the finite-group/transformation certificate and checks it with separate polynomial-basis arithmetic. This is group/coordinate construction progress within the same review_required, unapproved experiment. No scientific curve census or genus/descent measurement ran.

## Exact orientation and coverage proof

Let G=PGL2(K), H=PGL2(Fq), K=F_(q^n), and sigma be coefficient q-Frobenius. The parameterization tau=M sigma M^-1 is unchanged by M -> M h, h in H. For N=M^-1 the corresponding parameter is therefore the left coset H N, and tau=N^-1 sigma N has linear part C(N)=N^-1 sigma(N). Its transformed branch coordinate is N(B).

The checker needs no claim about every abstract semilinear descent datum. For any N1,N2 in G, C(N1)=C(N2) projectively if and only if h=N2 N1^-1 is fixed by sigma. Indeed sigma(h)=N2 C(N2) C(N1)^-1 N1^-1=h. Conversely h fixed implies C(hN)=C(N). A projectively Frobenius-fixed matrix, normalized by its first nonzero entry, has entries in Fq. Thus C(N1)=C(N2) if and only if HN1=HN2.

Consequently, valid invertible matrices producing exactly [G:H]=(Q^3-Q)/(q^3-q) pairwise-distinct normalized cocycles certify one representative of every left coset. This is the checker's complete-coverage argument. It covers the conjugate structures N^-1 sigma N; no stronger classification theorem about arbitrary semilinear structures is claimed here. Extending that statement uses a separately sourced Hilbert90/descent bridge and is not needed for this certificate.

## Borrowed triple transversal

The source represents N by its ordered distinct image triple (a,b,c)=(N(infinity),N(0),N(1)). Under left H there are three disjoint cases:

- A1: a,b rational. Normalize a=infinity,b=0; c ranges over K*/Fq*, giving r1=(Q-1)/(q-1) representatives.
- A2: a rational,b nonrational. Normalize a=infinity; choose b modulo the affine Fq group, then c in K minus {b}. Its affine stabilizer is trivial, so r2=(Q-q)/(q(q-1)).
- B: a nonrational. Choose a modulo H, then b in P1(K) minus {a} and c in P1(K) minus {a,b}. A nonidentity Mobius map over Fq has fixed points of degree at most2. At n=3,5,7 prime, nonrational a has degree n>=3, so H acts freely and rB=(Q-q)/(q(q^2-1)).

The emitted total r1+r2(Q-1)+rB*Q*(Q-1) equals (Q^3-Q)/(q^3-q). Degree1 is the identity fixture (H=G); degree2 is rejected. These arguments explain the enumeration; distinct-cocycle/index checking independently certifies its produced coverage.

## Literal scalar-preserving identity

For N=[[a,b],[c,d]], retain the homogeneous degree4 form F, including a cubic's infinity branch, and define

`G_N(X,Z)=F(dX-bZ,-cX+aZ)=F(adj(N)*(X,Z))`.

Then `G_N(N*(X,Z))=det(N)^4 F(X,Z)`. The weighted ordinate map is W'=det(N)^2 W; on the affine chart it is y'=det(N)^2*y/(c*x+d)^2. In particular this transports the actual coefficient square class. The implementation never replaces G_N by an unrecorded monic form. Rescaling N by lambda rescales its literal transformed form by lambda^4; certificates normalize matrices first and compare exact coefficients. Composition follows `transform(transform(F,N),H)=transform(F,H*N)`.

The checker recomputes the invertibility, canonical normalization, cocycle orientation, semilinear norm, exact group index, cocycle uniqueness and every literal transformed coefficient. It binds external expected field and input forms. It imports the existing separate Python polynomial field implementation, not Rust arithmetic. Invalid matrices, forms, counts, duplicates, reversed orientation and nonsquare whole-form changes are rejected in fixed software controls.

## Source review and actual software validation

Sources reviewed: implementation/quotient_core.rs transform_form, normalize_matrix, structure_cocycle, structure_count and visit_structures; structure_certificate.rs; check_structure_certificate.py; test_structure_certificate.py. The borrowed trans/from_triple/mob implementation remains hash-pinned and unchanged in EXP-PEXT-212d5c. No blocking source correctness issue was found within the declared group/coordinate interface.

The source-bound software-tests.txt records actual compiler/interpreter versions, commands, source hashes, warnings and results: five Rust core groups, six existing quotient-certificate Python methods and five structure-certificate Python methods pass, zero failures. The new fixed group fixture independently enumerates PGL2(F27) and verifies the exact disjoint partition 19,656=819*24 by H*N. It also checks the degree1 identity fixture, nine restored determinant-four identities spanning A1/A2/B, explicitly reversed cocycle orientation, scalar changes, malformed rows and limits, and CLI expected-input binding. These finite-group and fixed unit tests are software validation, not the planned scientific curve census, independent scientific review or official hypothesis support.

## Remaining scaling and scientific interfaces

The traversal enforces its declared count ceiling before constructing the transversal and propagates callback errors immediately. The current independent checker is a whole-JSON fixed-fixture interface with a16MiB file cap and100,000-structure ceiling. It is not a full-cohort streaming verifier. Complete protocol cohorts must retain their original scope; next build streaming/partition certificates with exact cross-shard coverage and scalar-preserving curve/T bindings, rather than reducing cohorts to fit these fixture limits.

The next actual-curve manifest must retain twists and explicit isomorphism witnesses: characteristic3 uses both the a2!=0 family normalized with r=-a4/(2a2) and the a2=0 family; p>3 uses short models. The proposal's n5/q3 count488 remains an unresolved convention until source-bound enumeration and identity alignment. Do not substitute j-only labels.

Then connect complete actual-curve/T iteration, every projective structure, connectedness and geometric genus accounting, Frobenius-lift/descent certificates, Type2 predicates, original geometric P3 and descriptive q13 H1 analysis, checkpoint/export and frozen launch bindings. A cocycle's projective norm certifies its coordinate structure, not a covering-curve descent. No approval or trial authority is supplied by this component.

## Sources and custody

The group identities and triple count above are derivations from the stated finite-group actions and inspected source. The experiment's primary cover/descent sources remain Iijima-Momose-Chao2015/805 sections3.1-3.3 (https://eprint.iacr.org/2015/805.pdf) and Chao ECC2007 slides25-26 (https://maths.ucd.ie/~gmg/ECC2007Talks/chao.pdf), reviewed in the original design notes; no new literature novelty is asserted. Canonical lead graph scientific edges remain unchanged because no full-cohort genus/descent evidence was produced.

Archive TASK-20261102-e53374 covers this fresh report, new/changed source, source-bound software log and additive problem progress. Earlier design, implementation and certificate report snapshots retain their original bytes and native receipts.
