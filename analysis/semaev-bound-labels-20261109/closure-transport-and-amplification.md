# Closure transport, field towers, and the limits of tensor amplification

Date: 2026-11-09. Source-only derivations. No solver, build, certificate search, or cloud execution. The results isolate transports that preserve a known obstruction without increasing its degree, and explain why disjoint copies cannot prove unbounded LFD. No embedding of a hard proof-complexity family into Semaev descent is claimed.

## 1. Degree-controlled substitution transports strict Boolean closure

Let B_X and B_Y be Boolean polynomial rings. Let phi:B_X->B_Y send every source variable to a Boolean polynomial of degree at most s, with s>=1. Such assignments define ring homomorphisms because every Boolean polynomial is idempotent. Let F and G be generating lists, and fix a source cap D. Assume that every source generator eligible at cap D has image in W_c(G), for one common c. Put E=max(sD,c).

**Transport lemma (derived).**

    phi(W_D(F)) subset W_E(G).

**Proof.** Eligible input images belong to W_E. For an allowed source operation x_i*u with deg(u)<=D-1, the image phi(u) has degree at most s(D-1). By induction it already belongs to W_E. Expand phi(x_i) into monomials of degree at most s. Multiply phi(u) by each monomial one variable at a time. Before each multiplication, its actual degree is at most s(D-1)+s-1<=E-1, so every step satisfies the strict source-degree rule. The final product lies in W_E; add the monomial terms. Linear combinations preserve membership. QED.

For an affine substitution, s=1, giving cap E=max(D,c). If c<=D, there is no degree loss at all. This includes fixing variables, invertible affine changes of Boolean variables, and identifying variables. It does not mean an arbitrary nonlinear substitution is free: its degree factor s is explicit.

### Pulling back a closed-kernel certificate

Suppose C:B_(Y,<=E)->Q is a checked closed-kernel certificate for G at cap E. Define C'=C composed with phi on B_(X,<=D). If its generator images meet the preceding assumption, C' annihilates F and has a closed kernel at cap D, by the same variable-by-variable proof. Also C'(1)=C(1)!=0. It may lose rank; restrict the codomain to its image if a surjective certificate is required. Never transfer a codimension count without recomputing that image rank.

If h is a source ideal consequence of degree at most D and C(phi(h))!=0, then h notin W_D(F). This is a valid missing-consequence transfer. For an UNSAT source lower bound, unsatisfiability of F must be established separately. An unsatisfiable restricted target does not prove the unrestricted source is unsatisfiable.

This gives a concrete proof obligation for a hard-system embedding: construct a bounded-degree substitution from the Semaev variables into the hard system, derive each substituted Semaev row at a uniform target cap c, and separately establish the needed source ideal/UNSAT bridge. A formal resemblance between coefficient tensors is insufficient.

## 2. Exact tower replication of a fixed Semaev instance

Embed K=F_(2^n) into L=F_(2^(rn)) and retain the same V<=K, a6,z in K, transported by the field embedding. Keep the same 2k Boolean variables for X,Y. Every coefficient of S3(X,Y,z) remains in the embedded K. In an L basis extending a basis of that embedded subspace, descent gives the original coordinate rows and zeros. In any other L coordinate basis, it gives an injective linear recombination of those rows, so the equation spans agree.

Since all normalized rows have degree at most two,

    W_D(new descent)=W_D(old descent), for D>=2.

This qualification matters: row mixing can expose affine inputs and change W0 or W1. For an old obstruction/refutation entirely in degrees at least two, including the exact degree-five R35a example, the tower copy has the same late degree behavior. Its Boolean variable count and solution set are unchanged.

The construction therefore produces infinitely many ambient field presentations of one fixed Boolean problem, not increasing LFD. It also fails the diagonal requirement k=ceil(rn/2) once r grows while V is fixed.

### Enlarging V to restore the diagonal

If V_old is a subspace of V_new, setting all new coefficient variables to zero is an affine restriction of the larger normalized Semaev system to the old one. The transport lemma preserves the corresponding nonmembership obstruction under that restriction, at the same cap. To turn it into a missing-consequence LFD lower bound for the larger system, the source polynomial must independently be proved to vanish on every solution of the larger system: a polynomial vanishing on all old solutions may fail on new ones. Likewise, transferring a refutation-degree lower bound requires independent proof that the larger system is unsatisfiable. The restriction itself supplies neither property and does not increase the inherited cap. Additional points in V_new can create solutions.

If a proposed tower construction additionally forces all extra coordinates to affine functions by uniformly low-degree relations, it risks being only a dummy-variable extension. The next section explains why that type of construction preserves rather than amplifies late LFD.

## 3. Disjoint satisfiable systems have maximum LFD, not additive LFD

Let tilde F in variables X and tilde G in disjoint variables Y include their respective field equations. Assume both have nonempty Boolean solution sets. Let H be their union. Then, under the ordinary polynomial last-fall-degree convention,

    d_LFD(H)=max(d_LFD(tilde F),d_LFD(tilde G)).

**Upper bound.** Take reduced Gröbner bases P and Q for the two ideals, using the restrictions of a degree-compatible monomial order on the combined variables. Because their variables are disjoint, the union is a Gröbner basis: cross leading monomials are relatively prime, and their S-polynomials reduce to zero by the two factors. For any f in the sum ideal of degree r, degree-compatible division gives a representation using products of these basis polynomials, each of total degree at most r.

By the definition of each component's LFD, every p in P is derivable at cap max(d_F,deg p), and similarly every q in Q. At E=max(d_F,d_G,r), the Gröbner basis elements actually used in the division are therefore available, since each of them has degree at most r. Unused higher-degree basis elements need not be available at this cap. Multiply each used basis element by its representation coefficient; actual product degrees stay <=r<=E. Thus f belongs to V_(H,E), proving the upper bound.

**Lower bound.** Fix any solution y0 of G. Evaluation Y=y0 maps each G input to zero and leaves each F input unchanged. It maps every bounded-degree polynomial derivation from H to a derivation from F at no larger cap: all substitutions are constant and all surviving original F rows retain their eligibility. Therefore a missing consequence of F cannot acquire a smaller cap in H. The same argument with a solution of F preserves the other component's lower bound. QED.

Adding unconstrained Boolean variables is a special case: the second ideal consists only of its field equations and has LFD zero under the nonnegative convention. Adding affinely constrained dummy variables also cannot amplify the late bound: change coordinates to turn them into zero variables and apply the same disjoint-system argument, with the usual D>=2 qualification for changed field-equation presentations.

This theorem applies to genuinely disjoint products of two satisfiable systems. It does not assert that arbitrary shared-variable gluing or nonlinear encodings preserve the maximum.

## 4. Tensor nonmembership certificates and disjoint UNSAT systems

Suppose C_F:B_(X,<=D)->Q_F and C_G:B_(Y,<=D)->Q_G are closed-kernel certificates with C_F(1),C_G(1) nonzero. For each squarefree combined monomial x^a y^b of total degree at most D, define

    C(x^a y^b)=C_F(x^a) tensor C_G(y^b).

Extend linearly. This is well-defined because each factor degree is at most D. It annihilates every eligible equation of F or G and maps1 to a nonzero tensor.

**Closure proof.** The certificate contracts supply well-defined partial variable actions on images of polynomials of degree at most D-1; extend these linearly to the ambient Q_F or Q_G. For a combined low-degree monomial, multiplication by an X variable is represented by T_i^F tensor I, and by a Y variable by I tensor T_j^G. Therefore any linear relation in the combined certificate kernel remains in the kernel after an eligible variable multiplication. Restricting the codomain to the combined image gives a surjective full certificate if needed.

The rank need not equal dim(Q_F)dim(Q_G): a total-degree truncation does not contain every pair of factor monomials. Only nonzero constant image and the actual computed rank are justified.

Consequently, at every D>=2,

    1 notin W_D(F union G)
      iff 1 notin W_D(F) and 1 notin W_D(G).

The reverse implication is the tensor construction; the forward implication follows because either component derivation is a derivation in the union. A satisfiable component always admits an evaluation certificate at every cap, so the equivalence also covers one UNSAT and one SAT component.

Thus, when the relevant refutation degrees are at least three, the disjoint union's refutation degree is the minimum of the component refutation degrees, treating a satisfiable component as infinity. If a component already refutes at cap<=2, the union is already refutable there and cannot amplify to a larger degree. No low-cap row-presentation convention is concealed in this statement.

In particular, repeating R35a in disjoint variable blocks never raises its degree-five refutation bound. Tensor certificate dimensions can grow dramatically while the attainable refutation degree remains five.

## 5. Why indicator gluing is different and where its degree loss enters

To combine incompatible branches, one often multiplies branch identities by Boolean selectors of degree t. The established branching lemma gives a refutation upper bound D+t if every t-bit restriction refutes at cap D. That is an upper-bound construction; it is not a lower-bound amplification theorem.

A proposed lower-bound transport using a substitution whose coordinate polynomials are such degree-t selectors has, from Section1, target cap at most tD (or the larger generator-image cap). This factor cannot be dropped. If t grows comparably to a target lower bound, the transported source lower bound may become constant. A valid no-loss argument must instead supply affine substitution or another independently proved degree-preserving map.

The existence of independently hard branches also does not imply their selector-glued union is harder: there may be cross-branch low-degree consequences. Those must be excluded by a full closed-kernel construction, not by separate branch ranks.

## 6. Actionable next lemma for a genuine Semaev amplification attempt

A successful candidate must escape all three preservation mechanisms:

1. it must introduce genuinely growing Boolean dimension, rather than only an ambient field extension;
2. it must couple the new coordinates in a way not removable by low-degree affine constraints or a disjoint product;
3. it must exhibit a full closed-kernel certificate, or a bounded-degree pullback from one, at a strictly increasing cap while independently preserving the source UNSAT or missing-consequence bridge.

One concrete specification is a sequence of affine substitutions phi_j from candidate Semaev variables to a known hard family, satisfying phi_j(F_j) subset W_c(G_j) for fixed c and with a known source affine consequence h_j mapping to a target consequence absent from W_(D_j)(G_j), D_j growing. Then Section1 transfers the lower bound without indicator-degree loss. No such actual-field substitution is constructed here; field multiplication and the same-subspace constraint on X,Y remain essential obligations.

This note establishes transport and non-amplification facts. It supplies no increasing sequence of Semaev closed kernels and no new LFD data.

Sources: `certificate-route.md` for the existing tower/disjoint-copy cautions; `certificate-feasibility-contract.md` for partial multiplication actions; `two-point-lfd-characterization.md` for explicit affine witnesses; the historical theorem dossier's strict closure and branching definitions. The disjoint-system proofs and degree-s substitution bound are written out here. No external novelty claim is made.
