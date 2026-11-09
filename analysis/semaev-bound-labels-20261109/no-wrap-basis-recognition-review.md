# Independent review: no-wrap recognition and label transport

Date: 2026-11-09. Source-only review of `no-wrap-basis-recognition-and-label-transfer.md`. No execution.

**The filtered transport lemma and guarded recognition contract are correct.** An invertible affine Boolean substitution and its inverse preserve degree filtration; each substituted variable is affine, so strict variable multiplication transports at the same cap. At D>=2 all normalized quadratic rows are eligible, making equality of their binary row spans sufficient. The resulting two inclusions prove the displayed W_D equality. This does not extend unconditionally to caps zero and one.

The all-degree LFD upper-four property transports because every required cap max(4,deg f) is at least two. A missing affine ideal generator at cap two transports the lower bound three. Hence exact degree three at r=6 is preserved. The stronger cap-two upper bounds through r=5 also transport, without asserting presentation-invariant exact degree at low caps.

In a validated polynomial-basis field presentation, k independent vectors supported entirely on coordinates 0,...,k-1 form exactly the full initial polynomial subspace. Their low-coordinate matrix supplies the explicit invertible variable transformation. Together with n>4(k-1), z=a6=1, and the exact normalized m=2 Boolean input contract, this is sufficient for the no-wrap theorem. Equal dimensions alone, an arbitrary point list, a non-full-vector-space domain, or an unknown field basis is not sufficient.

For externally supplied equations, full monomial coefficient row-span comparison after the declared coordinate map is needed. The note correctly retains input/presentation hashes and theorem-derived rather than measured status, and does not grant dataset admission from recognition alone.

The proposed field-isomorphism checks are sufficient: an invertible binary map fixing one and preserving multiplication on basis pairs preserves products everywhere by bilinearity. Alternatively a root of the irreducible source modulus in a verified same-degree destination field defines an injective field map and hence an isomorphism. Factor-base transport still needs verification. Choosing literal initial powers under a new modulus is independently covered by the theorem and should not be confused with transporting an arbitrary prior subspace.

The elementary row-mixing example correctly changes the literal first fall from two to one while preserving all W_D for D>=2. Thus the conservative rule not to copy FFD metadata solely from row-span equivalence is necessary. Literal-power FFD labels in an implementation should additionally enforce r>=1, as that theorem excludes the constant-only k=1 case. No substantive correction to this proof note is required.

## Appended fixed-output-coordinate FFD permission

Reviewed the later appended proof allowing arbitrary recognized input bases while retaining literal polynomial output rows. It is correct. In the standard basis, summing all positive coefficient rows gives sum_(i>0)(x_i+y_i), since F(1)=s(1) in the Boolean ring and f0=s0. This nonzero linear fall witness is independent of the only affine input f0 for r>=1. All other nonzero rows have genuine degree two. An invertible input-variable change preserves exact degree and linear independence because both it and its inverse preserve the filtration. Thus the witness and absence of a degree-one fall transfer without changing output rows. This justifies FFD2 for arbitrary recognized input bases if the inspector reconstructs and binds those literal output rows. It does not authorize transport through arbitrary output-row mixing, and the r>=1 exclusion remains essential.
