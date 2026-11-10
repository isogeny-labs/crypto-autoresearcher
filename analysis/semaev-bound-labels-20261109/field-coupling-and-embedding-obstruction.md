# Actual-field coupling and direct-embedding obstructions for fixed m=2

Date: 2026-11-09. Source-only algebra. No solver, certificate search, build, field sampling, or cloud execution. This note gives concrete restrictions on prospective hard-system embeddings; it does not construct a growing closed-kernel family.

## 1. The normalized quadratic coefficient tensor

Let K=F_(2^n), z,a6 nonzero, and V have ordered F2-basis v_1,...,v_k. With X=sum a_i v_i and Y=sum b_i v_i in zero-origin coordinates, normalized Boolean S3 is the K-valued polynomial

    S3(X,Y,z)
      = a6 + sum_i L_i(a_i+b_i) + sum_(i,j) C_ij a_i b_j,
    L_i=z² v_i²,
    C_ij=(v_i v_j)²+z v_i v_j.

There are no a_i*a_j or b_i*b_j terms: squaring is coefficientwise Frobenius after Boolean normalization. The full descended system is every F2 coordinate of this one K-valued polynomial. Discarding some coordinates changes the generating system and requires a separate valid degree-reduction argument.

## 2. Mandatory modular reduction on the half-dimensional z=1 diagonal

Choose any polynomial presentation K=F2[t]/p(t), deg p=n, and use canonical representatives of degree below n. Suppose z=1. The raw, unreduced diagonal cross coefficient of a_i b_i is

    v_i(t)^4+v_i(t)^2.

If e=deg v_i>0, this polynomial has degree exactly4e: its top fourth-power term cannot cancel with the lower-degree square. A k-dimensional subspace cannot have all its basis representatives of degree below k-1, because that polynomial space has dimension k-1. Thus some basis element has e>=k-1.

**No-wrap obstruction (derived).** If every normalized quadratic coefficient were to be represented by ordinary polynomial multiplication with no modular reduction, it would be necessary that

    4(k-1)<n.

For k=ceil(n/2) and n>=3, this inequality never holds. At least one actual Semaev coefficient necessarily crosses the degree-n modulus boundary. This argument does not require a monomial basis: it applies to every basis expressed in a polynomial field presentation.

Consequently a no-wrap convolution model, a truncated polynomial ring, or a nilpotent t-model cannot be substituted wholesale for this half-dimensional family. Any proof using such a model must explicitly account for the reduction of t^n and higher powers. The modular reduction can create lower-degree coefficient couplings; this note does not claim that those couplings force high or low LFD.

For smaller factor bases with k<=floor((n-1)/4)+1 the argument does not forbid no-wrap coefficients, but those parameters are outside the chosen half-dimensional diagonal. This is a necessary-condition obstruction, not a characterization of that smaller regime.

## 3. The full interaction graph cannot be sparse

For any nonzero u in K,

    u²+zu=u(u+z)=0 iff u=z.

Since each v_i and v_j is nonzero,

    C_ij=0 iff v_i v_j=z.

For a fixed i there is at most one j satisfying this, namely v_j=z/v_i; basis vectors are distinct. Similarly each column has at most one zero. Therefore the full K-valued bilinear interaction matrix is nonzero on at least k²-k positions. Its zero positions form a partial matching. This remains true for separate bases of the same factor-base subspace on the X and Y sides, because the same argument only needs nonzero distinct vectors.

An invertible coordinate-row transformation over F2 cannot erase a nonzero K-valued monomial coefficient: it merely applies an invertible linear map to its coordinate vector. A separate linear change of the a variables or of the b variables amounts to choosing new bases, so the same dense-interaction condition continues to hold.

**Direct-embedding obstruction (derived).** A sparse bipartite quadratic hard system in which many pairs have zero coefficient in every equation cannot equal the full normalized Semaev vector system under only separate factor-base basis changes and invertible output-row changes, unless its interaction pattern satisfies this dense matching restriction.

This does not rule out a more general affine substitution mixing the X and Y blocks, nonlinear encodings, restrictions, or deriving extra Semaev rows from the hard system. It says exactly why identifying selected coefficient equations with a sparse hard graph and ignoring all other cross interactions is not a sound embedding. A genuine reduction must establish that every additional full-coordinate row is derivable at the claimed uniform cap.

## 4. Linear coefficients determine every bilinear coefficient

The field square map is bijective. For fixed z, the displayed linear coefficient L_i determines

    v_i = sqrt(L_i)/z.

Substituting this into C_ij gives the exact compatibility identity

    C_ij = L_i L_j / z^4 + sqrt(L_i L_j)/z.       (K)

The linear coefficients must be nonzero and F2-independent, because Frobenius and nonzero scaling preserve independence. They must agree on the a and b sides for the same ordered basis.

**Direct coefficient-recognition lemma (derived).** Consider a K-valued Boolean polynomial of the form

    c + sum_i L_i(a_i+b_i) + sum_(i,j) C_ij a_i b_j

with c!=0 and fixed z!=0. It is exactly a zero-origin normalized S3 descent for some ordered k-dimensional factor-base basis iff the L_i are F2-independent and every cross coefficient satisfies (K). In that case the basis is uniquely v_i=sqrt(L_i)/z and a6=c.

**Proof.** Necessity was derived from the S3 expansion. Conversely recover the v_i from the independent L_i, and substitution into the displayed normalized S3 coefficients gives the supplied polynomial term by term. QED.

This is a stronger restriction than symmetry of C or the mere presence of a trace syzygy. It shows that the bilinear rows cannot be independently chosen once the full linear coefficient data and z are fixed. The lemma concerns the standard zero-origin coordinates. An affine translation of Boolean variables changes the linear coefficients; a reduction using such a translation must keep and invert that translation rather than applying (K) to the translated list as though its origin remained zero.

For different X and Y bases with linear coefficients L_i and M_j, the corresponding condition is

    C_ij = L_i M_j / z^4 + sqrt(L_i M_j)/z,

together with equality of the recovered factor-base spans when the same V is required. No claim about computational difficulty follows from this recognition identity.

## 5. A rank-one Artin-Schreier lift of the top tensor

If only the bilinear coefficients are being studied, normalize them as c_ij=C_ij/z². The actual Semaev coefficients admit lifts

    U_ij=v_i v_j/z,
    U_ij²+U_ij=c_ij.

Thus the symmetric K-matrix U has rank one, all its entries are nonzero, and the recovered words v_i=sqrt(z U_ii) are F2-independent. In particular all normalized coefficients satisfy Tr_K(c_ij)=0.

Conversely, if a supplied symmetric coefficient matrix c admits a symmetric rank-one lift U with U_ij²+U_ij=c_ij, nonzero diagonal, and independent recovered v_i=sqrt(z U_ii), then it is a Semaev bilinear coefficient matrix. Indeed rank-one symmetry gives U_ij²=U_ii U_jj; unique square roots imply U_ij=v_i v_j/z.

After choosing an Artin-Schreier section G on trace-zero elements, every possible lift has the form

    U_ij=G(c_ij)+epsilon_ij, epsilon_ij in F2.

A candidate field-compatible top tensor must therefore satisfy the rank-one minors and symmetry for some such binary branch choices, plus the recovered-basis independence condition. These are explicit algebraic compatibility obligations, not free tensor parameters. The full linear coefficient identity (K) is stricter because it fixes the diagonal lift and hence the recovered basis.

On the odd half-dimensional diagonal, the previously proved span(V*V)=K implies the C_ij span exactly the rank-(n-1) image of u->u²+zu. This explains the common top-form trace annihilator, but it does not classify the higher saturated closure.

## 6. What this contributes to the growing-LFD target

These lemmas narrow a genuine construction:

- the half-dimensional z=1 family necessarily uses actual modulus coupling;
- direct sparse hard-graph coefficient matching is obstructed by dense full-field interactions;
- the linear and quadratic coefficient tensors must obey (K), or equivalently the appropriate rank-one Artin-Schreier lift restrictions;
- a valid hard-system reduction still needs all substituted Semaev rows to be low-degree consequences and a separate source ideal-consequence/UNSAT bridge.

The actionable positive route is to build a hard family whose complete coefficient tensors already obey (K), rather than embedding an arbitrary collection of independent quadratic equations. Alternatively, a reduction can permit extra dense rows only after proving they belong to the hard system's bounded-degree closure at a uniform cap. Neither construction is supplied here.

The fixed degree-five certificates demonstrate that these field-compatible restrictions do not force a universal degree-four bound. They do not establish a parameter-uniform hard tensor or growing degree. No rank growth has been promoted to degree growth in this note.

Sources: the normalized S3 coefficient expansion in the historical theorem dossier and current exact inspector; `degree-two-family-obstruction.md` for the product-span statement; `closure-transport-and-amplification.md` for the full-row substitution and source-bridge obligations. All new specialized identities and obstructions are proved directly above. No external novelty claim is made.
