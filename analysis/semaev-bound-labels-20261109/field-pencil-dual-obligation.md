# Field-specific linear-pencil certificates and the remaining degree obstruction

2026-11-09. Source-only algebra; no instance search, closure execution, build, or cloud job. Previous notes remain unchanged.

## Exact dual equations on a coordinate-one slice

Use the unique-zero branch system

H(u,v)=v²u²+(v+1)u+v²,  u,v in W subset ker Tr(K/F2),

where K has odd degree n and dim W=r. Assume H has precisely the zero (0,0), as established for the count-controlled family. All statements below are conditional on this exact unique-zero property; they do not assume a random tensor.

For fixed v define the F2-linear map L_v:W -> K by

L_v(w)=v²w²+(v+1)w.

For every nonzero v in W, v² is outside L_v(W). Consequently nondegeneracy of the field trace pairing provides lambda in K such that

Tr(lambda L_v(w))=0 for all w in W,
Tr(lambda v²)=1.                                             (1)

This is ordinary separation of a vector from a linear subspace, not a degree bound. In a basis w_i of W its first condition is exactly

Tr(((lambda v²)^(2^(n-1))+lambda(v+1)) w_i)=0 for every i.     (2)

The equality uses Tr(a w²)=Tr(a^(2^(n-1)) w). Thus the actual field tensor supplies an explicit dual system. Arbitrary rectangular-MQ coefficient matrices cannot be substituted into (2).

Fix a coordinate j and restrict v_j=1. If there is a K-valued Boolean polynomial lambda(v), in the remaining r-1 coordinates, of degree at most c, satisfying (1) at every point of this slice, then its multilinear identities give

Tr(lambda(v) H(u,v))=1                                       (3)

in the Boolean coordinate ring of the slice. Relative to any output basis, (3) is a combination of the original H coordinate equations with multipliers depending only on v and of degree at most c. Forming each monomial multiplier by successive strict multiplication costs at most c+2. Hence the slice refutation degree is at most c+2. This proof uses a literal polynomial identity in a Boolean ring, not only a pointwise inconsistency assertion.

If such certificates of degree c exist for every j, lifting with the gate v_j costs one more degree and derives every v_j at cap c+3. Once all v_j are available, each quadratic term of H containing v is removable at cap max(c+3,2), leaving every coordinate of u. Therefore

                d_LFD(H) <= c+3.                            (4)

The original trace-selector system then has LFD at most c+4 by the previously established additive-one transfer. These caps are conservative and respect the degree-two input threshold.

There always exists some lambda function on each slice: choose a separator independently at each v, then interpolate its field coordinates in the Boolean basis. Its degree is at most r-1. This gives the unconditional bound h<=r+2 for this unique-zero H, but does not improve the existing selector-scale bound. A uniform-degree solution of (1)-(2) would give a constant bound and is a concrete additional lemma to seek.

Conversely, failure to find such a low-degree lambda is NOT a full-closure lower bound. It only excludes certificates whose multipliers depend on v alone. Strict closure may use u-dependent multipliers, derive new quadratic consequences, and feed them back. To turn a lower bound on the degree of lambda into an LFD lower bound one must prove a degree-controlled normalization theorem for arbitrary full-closure refutations into this restricted dual form. No such theorem is established here.

## Exact rank-drop locus and why inversion does not prove hardness

On the full field, for v nonzero and v !=1,

ker L_v = {0, kappa(v)},   kappa(v)=(v+1)/v².

Thus on W the kernel has dimension one precisely when kappa(v) belongs to W, and is otherwise zero. The value v=1 never occurs because W is trace zero and n is odd. For v=0, L_v is the identity.

Writing u=kappa(v)t, the full-field equation L_v(u)=v² becomes

t²+t=1/kappa(v)².

Its full-field solvability criterion is Tr(1/kappa(v))=0. Since

1/kappa(v)=v²/(v+1)=v+1+1/(v+1),

and Tr(v)=0, Tr(1)=1, this criterion is equivalently

Tr(1/(v+1))=1.                                               (5)

Equation (5) says nothing by itself about whether a full-field solution lies in W. A high algebraic degree for inversion, a determinant of L_v, or a denominator-cleared expression only establishes complexity of that representation. The u variables remain present in the original system and may provide a short derivation bypassing inversion. This is the exact missing transfer in the determinant/inverse-map route.

## A conditional minor-based constant bound, and a failed field construction

Suppose all Boolean rank-one minors

M_ij=u_i v_j+u_j v_i

are available already in W2(H). This additional algebraic hypothesis implies h<=4:

* Restrict u_i=1 and then v_i=b. The minor equations give v_j=b u_j as affine consequences.
* For b=0, H reduces to u=0. For b=1, H reduces to u⁴+u=0.
* On trace-zero W in an odd-degree field, u⁴+u has zero kernel: its full-field roots lie in F4 intersect K=F2, and W excludes 1. Thus each double slice refutes at degree at most two.
* Gate over v_i to refute the u_i=1 slice at degree three, then gate over u_i to derive u_i at degree four. Once all u_i are derived, H gives v²=0, hence all v_i, at the same cap.

Restriction sends W2 consequences into W2 of the restricted system, so this argument does not silently promote consequences to inputs at a lower cap. It is an actual strict-closure conditional theorem, not a claim that the minor hypothesis holds.

One tempting way to obtain the minors fails at growing size. Suppose additionally W²=W and Tr(uv)=0 for all u,v in W. Then A(w)=w²+w maps W bijectively to itself, and H=0 implies uv belongs to W: A(uv)=u+v² belongs to W, so uv lies in W+F2; trace isotropy excludes the nonzero F2 component. Projecting uv modulo W gives linear combinations of the minors, because each diagonal product w_i² lies in W. If the pair-product classes [w_i w_j], i<j, were independent modulo W, this would yield all minors directly as combinations of H outputs. But their number is r(r-1)/2 whereas dim K/W=r+1 when n=2r+1. Independence is impossible for r>=4. Thus this direct route cannot produce an infinite uniform-bound family.

A weaker geometric property can still be meaningful: the kernel of the projected multiplication tensor might contain no nonzero alternating tensor u wedge v arising from independent u,v. That property would force set-theoretic dependence at solutions, but it would NOT place the minors in W2. Promoting that property to bounded-degree minor derivations is an additional proof obligation, not a consequence of solution geometry.

## Next precise obligations

The useful alternatives are now explicit:

1. Construct constant-degree dual separator polynomials satisfying (1)-(2) on every coordinate-one slice of an infinite qualifying family; this would prove a constant LFD bound for that family.
2. Prove a degree-controlled normalization of all strict-closure slice refutations into dual separators, then prove those separators require growing degree for an explicit qualifying family; both steps are needed for unboundedness.
3. Construct an explicit stable degree-three quadratic consequence space omitting a required linear, as in degree-three-family-analysis.md. Initial pencil ranks or initial Macaulay ranks do not replace stability.

No growing lower bound or universal W3 outcome is claimed by this note.
