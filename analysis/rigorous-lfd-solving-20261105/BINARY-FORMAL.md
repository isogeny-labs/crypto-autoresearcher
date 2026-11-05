# The raw binary two-S3 last-fall upper bound is now instantiated in Lean

5 November 2026. Exact theorem:
`CryptoResearch.FallDegree.lastFallDegree_binary_two_S3_chain_le`
in `formal/CryptoResearch/FallDegree/BinaryCoefficientDescent.lean`.
Scoped source build and all 27 automatic axiom-audit declarations pass.
Independent raw-instantiation review is recorded separately in
`coefficient-descent/review.md`; no scientific-status promotion is asserted.

## Actual inputs, without localized-row assumptions

Let K be a field of characteristic2, ell>=1. Let Sx,Sy,Sz be finite sets of
base-bit indices, each of size<=ell; they may be disjoint as in production.
Set x=sum_i cx_i*X_i on Sx, y likewise on Sy, z likewise on Sz, with
arbitrary K coefficients and zero constant terms. Let u,v be arbitrary
finite linear forms in auxiliary bits, also with zero constant terms.
Fix r,a in K and use

    f1=(x*y+x*u+y*u)^2+x*y*u+a,
    f2=(u*z+u*r+z*r)^2+u*z*r+a,
    optional h=v*(x+y)+1.

For each selected row use an additive coefficient map phi_i:K->F2. It acts
on each coefficient of the raw polynomial, leaving monomials unchanged.
The selector 'which' chooses a first-S3, second-S3 or guard projection per
row. The generator set is EXACTLY the range of those projected raw rows,
union every explicit bit equation. The only inconsistency hypothesis is
that there is no assignment of zero/one to all the bits satisfying every
projected row. The final theorem proves

    lastFallDegree(F)<=3*ell+1.

It assumes no normalized-support condition, supplied refutation, localized
row, affine-fibre refutation certificate, or finite-last-fall premise.
It permits arbitrary numbers of auxiliary bits and projection rows.
The finite row family is explicit; the auxiliary type need not be finite
for the LFD statement. Its ordinary polynomial closure is the original V,
not an executable proxy.

For K=F_(2^n), choose phi_i to be the actual basis-coordinate additive maps,
u and v to use the chosen K/F2 basis, and three ell-bit embeddings for
x,y,z. These satisfy the statement directly. Omitting the guard uses a row
selector that never selects it. Nonsingularity a!=0 and rational-lift/target
conditions give curve relation semantics but are not needed for this
syntactic degree upper bound. The full theorem is stronger on these
parameters; it does not weaken the production degree statement.

## The formal chain

1. `coefficientProjection` is a real additive map between polynomial rings,
   constructed by mapping the finite coefficient function. No map is
   assumed multiplicative or unital. In particular projecting the guard's
   one gives phi_i(1), which need not be one for each coordinate.
   `coefficientProjection_booleanNF`, `_degree`, `_localAffine` prove
   commutation with normalization, degree nonincrease, and preservation of
   supported-affine shape. The last proof controls all source-field scalar
   combinations, not just the basis monomials.
2. The original-degree Boolean repair is in BooleanNormalization.lean.
   `binaryS3_repair` derives the raw/reduced S3 difference at cap four.
   `binaryS3_normal_support` proves the reduced/raw-normalized first S3 is
   in the supported-affine span on Sx union Sy. It derives this from the
   actual linear forms using Frobenius and normalized base multiplication.
   The second S3 uses support Sz; `binaryS3_cycle` proves the exact cyclic
   equality with the production ordering. The optional guard has support
   Sx union Sy and is affine in v.
3. `lastFallDegree_raw_projected_supported_affine_le` derives the NORMALIZED
   projected rows from their raw input rows using explicit bit repairs.
   It proves raw/normalized evaluation equality on bits, rather than
   assuming that replacing the equations preserves the needed semantics.
4. BinaryLocalization.lean proves the actual staged localization: every
   intermediate normal form has degree<=|A|+1, and the next multiplication
   and repair fit |A|+2. Its interpolation identity leaves auxiliary
   variables as indeterminates. Multiplication by the complementary
   indicator costs at most |B|+1. The full low-degree combination space is
   controlled by the supported-affine submodule.
5. AffineFibreRefutation.lean derives constant-coefficient refutations of
   affine systems with NO FIELD SOLUTION by dual separation. The binary
   wrapper proves every F2 field element is zero or one, so Boolean UNSAT
   implies the required affine-fibre inconsistency. This is not inferred
   merely from characteristic two in a larger field. The exact indicator
   partition then derives one in ordinary V and the last-fall definition
   yields the global bound for every ideal consequence.
6. Raw degree<=4, total base support<=3ell and row support<=2ell are all
   proved from the source forms and cardinality hypotheses. Thus

       max(4,|B|+1,2ell+2)<=3ell+1  for ell>=1.

   This cap includes raw normalization, not only Boolean operations.

The independently reviewed generic core has the exact bound
`LFD<=max(|B|+1,r+2)` for normalized F2 supported-affine inputs with row
support<=r. The new raw theorem derives its structural hypotheses and input
eligibility from the actual S3 construction.

## Solving degree and remaining scope

On finite actual presentations, Boolean UNSAT and explicit bit equations
make the ideal the unit ideal. Caminata--Gorla Theorem3.1 for a
degree-compatible order gives sd=max(d_F,maxGBdegree); the reduced basis
is {1}, so

    sd_sigma(F)=d_F<=3ell+1.

This solving-degree identification is a written application of the primary
source, not a Lean formalization of Groebner/Macaulay solving-degree
machinery. The theorem does not prove a growing binary lower bound.

The full standard workspace verification did not pass: the first attempt
timed out while building uncached dependencies; after cache repair, an
existing unrelated degree-three rank certificate was killed with exit137
and an observed cgroupOOM. These preserved receipts do not negate the
successful scoped build/axiom checks and are not reported as a passing full
workspace gate. Exact source pins and fresh-kernel outcomes are in
formal-status.md and the final validation summary.
