# Exact LFD characterization for the two-point fixed-m=2 family

Date: 2026-11-09. Source-only derivations; no code execution, certificate search, closure computation, build or cloud job. These results assume the chosen individual subspace has been proved to have exactly the two stated solutions. The averaging existence theorem does not certify an arbitrary supplied basis.

## Setting

Use a basis of V beginning with 1 and coordinates a_1,...,a_k,b_1,...,b_k. For the family with z=a6=1, assume the Boolean zero set is exactly

    P=(a_1=0,b_1=1, all other coordinates zero),
    Q=(a_1=1,b_1=0, all other coordinates zero).

Let F be the normalized coordinate equations and tilde F include all Boolean field equations. Let I be its ordinary polynomial ideal and I_B its image in the Boolean ring B. Since field equations are present, I is radical and equals the vanishing ideal of {P,Q}.

Define the known affine generating list

    G={a_i,b_i : 2<=i<=k} union {a_1+b_1+1}.

This list has 2k-1 independent affine forms. Together with the field equation a_1^2+a_1 it generates I; in B, G alone generates I_B. Write t=a_1. Every function on {P,Q} has a unique representative alpha+beta*t.

## 1. Degree-nonincreasing affine reduction

**Lemma (derived).** If f is an ordinary polynomial of degree r vanishing on {P,Q}, then f has a representation in G and t^2+t in which every nonzero product has total degree at most r.

**Proof.** Eliminate each a_i,b_i for i>=2 by replacing it by zero, and replace b_1 by 1+a_1. For a monomial containing a pivot variable, subtract its pivot affine equation multiplied by the remaining monomial. This substitution does not increase total degree. Iterating yields a polynomial h(t) of degree at most r and a representation of f-h whose products with G have degree at most r. Divide h by t^2+t; univariate division does not increase total degree. The remainder has degree at most one and vanishes at t=0 and t=1, so it is zero. QED.

The same statement in B omits the field-equation terms. This is a direct constructive argument, not an assumption about a solver's Gröbner basis.

## 2. Exact reduction of LFD to derivation of the known linear forms

Let

    d_* = min { d>=1 : every g in G belongs to V_(tilde F,d) }.

This minimum exists. For each g one may equivalently define its least derivation cap d_g>=1; because G is finite and closure spaces are nested, d_*=max_{g in G} d_g.

**Theorem (derived).** Under the convention allowing last fall degree zero:

    d_LFD(tilde F) = d_*  if d_*>1;
    d_LFD(tilde F) = 0    if d_*=1.

If a convention forces the statistic to be a positive integer, the second value is instead its conventional minimum1. Every degree-cap statement below uses D>=2 and is independent of that convention.

**Upper bound.** Fix f in I of degree r and put E=max(d_*,r). Every affine generator g in G belongs to V_E. The lemma represents f using products h*g with degree<=r, so the defining closure operation makes all these products available in V_E. Products involving the explicit field equation t^2+t are also available: they occur only when r>=2, and that generator and its multipliers fit cap r<=E. Therefore f belongs to V_max(d_*,deg f). This proves d_LFD<=d_*.

**Lower bound when d_*>1.** Some g in G fails to belong to V_(d_*-1). If d<d_*, then max(d,deg g)=max(d,1)<=d_*-1. Thus the definition of LFD fails on that g, proving d_LFD>=d_*.

**Small-degree exception.** If d_*=1, the same representation proves every f in I is derivable at its own degree. The ideal is proper, hence contains no nonzero constant. Consequently the requirements at d=0 and d=1 are identical, giving d_LFD=0 under a nonnegative convention. In particular, one must not automatically identify the maximum linear derivation cap1 with exact LFD1 for this satisfiable family.

**Consequence for an unboundedness proof.** It is necessary and sufficient to prove that at least one member of the explicit finite list G needs a growing derivation cap. Because the list grows with k, the witness may depend on n; a proof need not select the same coordinate index for every n. One may equivalently take the maximum derivation cap over all affine forms vanishing on the two points, but the displayed basis G is sufficient.

## 3. Necessary and sufficient degree-D conditions

For any D>=2 define the exact quotient dimension

    r_D = dim(B_{<=D}/W_D(F)).

Evaluation B_{<=D}->F_2^{\{P,Q\}} has rank exactly two: 1 and t separate the two points. Since W_D is contained in the vanishing ideal, r_D>=2.

The following are equivalent:

1. d_LFD>D;
2. some g in G is not in W_D;
3. W_D is a proper subspace of (I_B)_{<=D};
4. r_D>2;
5. there exists a full closed-kernel certificate of rank q>2 at cap D;
6. there exists a full closed-kernel certificate C and a g in G with C(g)!=0.

**Proof.** The previous theorem and the Boolean/polynomial closure bridge give1 iff2. If every g in G belongs to W_D, degree-nonincreasing affine reduction and closure derive every degree<=D member of I_B. Thus2 iff3. The exact evaluation rank gives3 iff4. An exact quotient map B_{<=D}->B_{<=D}/W_D proves4 implies5 and separates each missing g, proving2 implies6. A rank-q certificate has W_D subset ker C, so q>2 proves4. A separated g proves2. QED.

For a *given* certificate, q>2 is sufficient but not necessary for its missing-linear-form proof. A quotient map can kill a genuine solution-function direction as well as some ideal directions; its rank need not exceed two even when it separates an ideal form. Do not reject an independently checked C(g)!=0 witness merely because q<=2. Conversely, any rank-q>2 certificate must separate at least one g in G: if it killed all G, closure and affine reduction would put the entire degree-D vanishing ideal in its kernel and force q<=2.

This makes the solution-count bridge exact for this family rather than merely sufficient: exact closure codimension greater than two is equivalent to a missing known linear consequence.

## 4. Strengthened filtration obstruction for the EXACT quotient

Let Q=B_{<=D}/W_D and Q_e be the image of B_{<=e}. Assume r_D>2. Then

    dim Q_1 >=3,
    dim Q_0 < dim Q_1 < ... < dim Q_{D-1},
    hence r_D >=D+1.

**Proof of the first inequality.** Evaluation rank on affine forms is two, and some known vanishing affine form is missing from W_D. Thus W_D intersect B_{<=1} is a proper subspace of the affine vanishing space, giving dim Q_1>=3.

**No early plateau.** If Q_e=Q_{e+1} at e<=D-2, the closed-kernel plateau argument propagates equality to all Q. The resulting coordinate operators are commuting idempotents, so Q is a cyclic module over B with cyclic vector [1]. Every f in F annihilates that vector, and commutativity makes it annihilate the whole module. The module therefore factors through B/I_B, whose dimension is exactly two. This contradicts r_D>2. Thus all inclusions through Q_{D-1} are strict. Starting from dim Q_1>=3 gives r_D>=D+1. QED.

**Gap consequence.** For this exact two-point family and D>=2, exact closure codimension is either two or at least D+1. Values3,...,D cannot be exact closure codimensions. This is a semantic control for future exact-closure profiles, not a claim that a certificate's lower-bound rank equals the exact codimension.

For an arbitrary accepted certificate of rank q>2, the early-plateau argument still gives q>=D, because an early plateau would force the certificate quotient to factor through the two-point coordinate ring. The stronger q>=D+1 does NOT automatically apply: the certificate kernel can strictly contain W_D and can contain nonvanishing polynomials, so its affine image need not retain both evaluation directions.

## 5. Evaluation-augmented certificate normalization

Given any closed-kernel certificate C separating g in G, append the two actual evaluation functionals:

    C'(f)=(C(f),f(P),f(Q)).

Its kernel is ker C intersect I_B, which is closed under the allowed variable multiplications. It still contains F and separates g. Since g lies in I_B but not ker C, the kernel is a proper subspace of I_B on B_{<=D}; hence rank C'>2. The rank is at most q+2. Taking a basis of the image yields a surjective certificate with the same kernel.

This is a mathematically valid way to convert a missing-linear-form certificate into a codimension-excess certificate. It is not an arbitrary projection of C: arbitrary quotient projections can destroy kernel closure. Appending evaluation also makes the quotient preserve both actual solution directions, so its affine image has dimension at least three when it separates a known affine vanishing form; the strengthened rank lower bound D+1 then applies.

A future encoder could require the two evaluation rows as a fixed subspace of its quotient map. That is an optional normalization justified here, not an implemented feature. It may increase the certificate rank and search size; no efficiency claim follows.

## 6. What has and has not been reduced

The family's lower-bound problem is now exactly a proof-complexity problem for the explicit affine consequences G. One need not reason about an unknown high-degree final Gröbner basis, and a correct rank-excess certificate always supplies an immediately identifiable missing affine generator.

However, knowledge that the final ideal is affine does not imply that its low-degree generators are cheaply derivable from the supplied quadratic Semaev rows. The distinction between the semantic ideal and bounded-degree derivability is precisely the remaining hardness question. No growing d_g, q, D or explicit V_n construction has been proved here.

The reviewed existence theorem produces qualifying V for every odd n but does not give an efficiently computable basis or certify arbitrary V. For later dataset records, the exact two-point predicate must be established for the particular input by an independent count, exhaustive algebraic characterization or a constructive theorem covering that basis. The polynomial ideal's generators and this characterization may then be attached without another closure computation.

Sources: `low-solution-count-family.md` and `low-solution-count-family-review.md` for the assumed two-point family; `certificate-route.md` for full-kernel and plateau arguments; `certificate-feasibility-contract.md` for the finite search encoding; the historical theorem dossier's Boolean/polynomial closure bridge. No outside priority or novelty claim is made.
