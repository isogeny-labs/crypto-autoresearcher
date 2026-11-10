# Independent review: two-point LFD characterization

Date: 2026-11-09. Source-only audit of `two-point-lfd-characterization.md`. No execution.

**Verdict: the characterization and exact-codimension gap are correct under the stated exact two-point hypothesis and full closed-kernel convention.**

Affine substitution eliminates the pivot coordinates without increasing total degree; univariate reduction by t²+t then proves the claimed degree-controlled ideal representation. This establishes the equivalence between LFD>D and failure to derive at least one of the named affine ideal generators, for D>=2. The special case d_*=1 is handled correctly: for a proper ideal, derivability at each polynomial's own degree gives LFD zero under the nonnegative convention, not automatically one.

Evaluation has rank exactly two already on affine polynomials. Hence exact closure codimension greater than two is equivalent to a missing affine vanisher. Full-kernel certificates give the stated sufficient implications; conversely the exact quotient supplies a certificate. A given small-rank certificate may separate an ideal form without retaining all genuine solution directions, so rank greater than two is not necessary for that particular certificate's nonmembership proof.

The strengthened filtration gap is sound. A missing affine vanisher forces the exact quotient's affine image to have dimension at least three. A plateau at level e<=D-2 allows multiplication to be defined on degree-e representatives; closed-kernel stability makes these operators well-defined, and the room through degree e+2 establishes commutation and Boolean idempotence. The resulting cyclic module factors through the two-point coordinate ring and has dimension at most two, a contradiction. Thus strict growth through degree D-1 gives exact quotient dimension at least D+1. This includes D=2, when the affine image itself already has dimension at least three.

For an arbitrary certificate the weaker q>=D bound is justified by the same plateau argument with a nonzero constant image. The stronger bound requires retaining the two solution directions; it cannot be imposed on every arbitrary certificate solely from q>2. Appending both evaluation maps has kernel equal to the intersection with the vanishing ideal, preserves full-kernel closure, and supplies that stronger normalization. Taking an image basis preserves the kernel.

These conclusions concern a subspace independently known to have precisely the displayed two zeros. The averaging existence theorem does not admit an arbitrary input basis as such a subspace. No growing derivation cap follows from the characterization alone, and no mathematical correction is required.
