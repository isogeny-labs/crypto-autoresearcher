# Fixed-m=2 binary Semaev: toward an unbounded last fall degree

2026-11-09. Parallel proof research, with no new solver run, native build, cloud job or certificate replay. The user requested an infinite family and a growing lower bound, with Git/S3 preservation. **That target remains open.** This round supplies written, independently cross-checked restrictions on candidate families and certificate constructions. No official hypothesis or evidence status is promoted.

## Exact target

Let K=F_(2^n), V an F2-linear subspace of dimension k=ceil(n/2), z and a6 nonzero. Descend S3(X,Y,z)=(XY)^2+z^2(X+Y)^2+zXY+a6 with X,Y in V. Inputs are normalized multilinear Boolean coordinate polynomials, together with explicit Boolean field equations. W_D is the strict saturated closure: multiply a derived polynomial by a variable only when its current degree is at most D-1. A raw quartic presentation requires its own degree bookkeeping.

We seek systems F_j of this exact family and a proved g(j) tending to infinity with LFD(F_j)>=g(j). For the UNSAT route it suffices to prove no Boolean zero and 1 not in W_Dj for D_j tending to infinity. SAT examples remain allowed, but require an actual missing ideal consequence or the applicable solution-count bridge. If targets must be rational curve-point abscissae, that property must also be proved. Neither changing m nor changing to odd-characteristic digit equations meets this binary target.

## Derived result A: the natural subfield tower cannot amplify UNSAT degree

For n=2k and V=H=F_(2^k) inside K, every unsatisfiable normalized m=2 instance satisfies **LFD<=3**.

For z outside H write z^2=pz+q and a6=A+Bz with coefficients in H. Separability and nonzero norm give p,q nonzero. Put s=X+Y and P=XY. The coordinate system is equivalent by output row operations to

    E1=P+p s^2+B,    E0=P^2+q s^2+A.

The original equation span contains all coordinates of E0+E1^2=p^2 s^4+q s^2+A+B^2. Squaring here is F2-linear on coordinate equations because their Boolean coefficients are idempotent. This is an affine-linear constraint on the bits of s. Its homogeneous kernel is exactly {0,sqrt(q)/p}, so either there is an immediate inconsistency or at most one bit of s remains free.

Eliminate the resulting linear constraints at degree 2: the difference between a quadratic and its affine substitution is a sum of those constraints times affine polynomials. Fix the remaining bit. Then P=X^2+sX, and the remaining equations are affine-linear in X. Both branches of an unsatisfiable instance refute by linear combination. One-bit selector lifting gives a refutation at degree 3. If z lies in H but a6 does not, an output functional gives a nonzero constant equation. If both lie in H, X=Y=a6^(1/4) is a solution.

The algebraic and definition-audit workers independently derived and checked this argument. Full proofs are in [algebraic-route.md](algebraic-route.md) and [definition-audit.md](definition-audit.md). This statement concerns UNSAT instances only. Arbitrary subspaces, including polynomial bases, are not ruled out. No Lean formalization or new finite replay is claimed.

## Derived result B: an unbounded closed-kernel certificate needs growing filtration

Let pi:B_(<=D)->Q be an onto linear map annihilating the generators, with pi(1)!=0 and its entire low-degree kernel closed under permitted variable multiplication. Then W_D is contained in ker(pi). Put Q_e=pi(B_(<=e)).

If Q_e=Q_(e+1) for e<=D-2, kernel closure propagates this equality to Q_D. Every vector then has a representative of degree <=D-2; multiplication by the Boolean variables gives well-defined commuting idempotent operators on Q. The nonzero vector pi(1) has a nonzero Boolean joint-eigencomponent. Generator annihilation implies that component's assignment is a common zero. Consequently, for an UNSAT system,

    Q_0 strictly contained in Q_1 strictly contained in ... strictly contained in Q_(D-1),
    dim Q >= D.

The final step Q_(D-1)->Q_D may plateau. Two workers derived this independently; their full proofs are retained. In particular, a rank-one closed-kernel certificate evaluates at a Boolean solution and cannot witness UNSAT non-refutation. Ordinary scalar functionals annihilating W_D still exist; their entire kernels need not be closed. This distinction prevents an incorrect pseudoexpectation argument.

This is a necessary condition on a certificate family, not the missing construction. Large rank at fixed D=4 does not prove growth in D.

## Existing certificates guide the construction but do not supply it

The saved verification record gives R35a exact LFD=5. Both degree-4 non-refutation and its two degree-4 branch refutations were independently reproduced. Derived filtration ranks are:

| Saved instance | Boolean variables | q0 | q1 | q2 | q3 | q4 |
|---|---:|---:|---:|---:|---:|---:|
| R35a | 36 | 1 | 36 | 562 | 3922 | 5287 |
| P45a | 46 | 1 | 46 | 858 | 7312 | 12742 |

These are arithmetic from saved profiles, not new measurements. P45a's cited profile has implementation-A provenance, not the independent replay standing of R35a. R35a shows that a large degree-4 quotient can coexist with a degree-5 refutation. The later inspected D5 quotient-lift failure `projection_kills_one` is inconclusive: a provisional quotient may add relations not in the true closure. It establishes neither a degree-six lower bound nor an upper bound.

The explanatory diagram and profile graph are in [proof-map.svg](proof-map.svg) and [profiles.svg](profiles.svg); [render.py](render.py) and [profiles.json](profiles.json) regenerate them. Each profile is one named instance; no uncertainty estimate, statistical sample inference or asymptotic fit is made.

## Other amplification routes checked

- Embedding unchanged parameters and V into a larger field preserves the equation span and W_D; it also loses the k=ceil(n/2) diagonal.
- A conjunction of disjoint unsatisfiable copies retains one copy's original refutation, so it does not add refutation degrees.
- The full cross term is H_z(uv)=(uv)^2+zuv. If it vanishes for all u in nonzero U and v in nonzero W, then UW is contained in {0,z}. Injectivity of multiplication by a nonzero field element forces dim U,dim W<=1. This rules out simply uncoupling larger sparse gadgets in the full descent. More elaborate reductions are not ruled out.
- Eliminant or determinant degree alone supplies no lower bound against saturated closure. Deleting troublesome equations gives a weaker system; its hardness does not automatically lower-bound the original stronger system.

## Literature and prior-work reconciliation

Primary sources consulted: [Caminata–Gorla, 2112.05579, Section 3](https://arxiv.org/html/2112.05579), [Huang–Kosters–Yang–Yeo, 1505.02532](https://arxiv.org/html/1505.02532), and [Kosters–Yeo, 1503.08001](https://arxiv.org/html/1503.08001). The first separates solving degree, Gröbner basis degree and LFD. The latter sources motivate the descent and trace constraints; none supplies the desired binary family theorem here. No novelty claim is made for the abstract quotient lemmas.

At base dadfb1b2a5b6e8e6045f8547d26ec2b40d4ff81a, the existing [growing binary bound problem](../../../problems/growing-boolean-semaev-lower-bound.md) already identifies the uniform closed separator as the missing obligation. Newer prime-digit family results in analysis/rigorous-lfd-solving-20261105 explicitly do not settle characteristic two. The strict closure bridge in analysis/boolean-fall-certificates-20261104/THEORY.md matches this round's convention. The historical blanket FFD=2 wording has additional hypotheses; no universal FFD statement is needed or asserted here.

## Next constructive obligation

Construct a genuinely varying half-dimensional V_j, not an unchanged field embedding or a full quadratic subfield, and a formula for vector quotient maps pi_j on all monomials through increasing D_j. Prove generator annihilation, full low-degree kernel closure and nonzero constant image for every j, together with UNSAT. An alternative SAT route needs the missing-consequence bridge. The maps must respect the actual field multiplication tensor, not arbitrary symbolic or nilpotent replacements.

The next certificate analysis should seek canonical low-degree multiplication maps invariant under changes of quotient basis, using R35a as a bounded-degree negative control: any proposed persistence rule that predicts its survival at D=5 is false. Loading large certificates, new degree-five replay, builds and cloud work require their own finite resource authorization; none was started in this proof round. The existing [problem record](../../../problems/growing-boolean-semaev-lower-bound.md) retains explicit acceptance conditions.
