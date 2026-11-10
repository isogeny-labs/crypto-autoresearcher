# Independent review: uniform quotient operator contract

2026-11-10. Source-only review of `uniform-quotient-operator-20261110.md`; no experiment, certificate search, or build.

Accepted. The K-tensored input equation has the correct coefficients: the Boolean Frobenius square of XY preserves the mixed masks, with coefficients v_i^2 v_j^2, while zXY contributes z v_i v_j. The pure X^2,Y^2 terms are affine in the independent Boolean coordinates. An equality in K tensor Q enforces every field-coordinate row, unlike a single trace projection.

The multiplication constraints on all columns of degree at most D-1 imply closure for every low-degree kernel combination. Their converse uses extension of a well-defined linear partial action and requires no globally commuting extension.

The new global-commutation obstruction is correct. Local degree-two identities give (T_i^2+T_i)e=0. Global commutation propagates this to every word applied to e, and monomial columns span Q, so each T_i is globally idempotent. The same propagation makes every input f(T) vanish on Q. The resulting cyclic Boolean representation is a quotient of the actual solution coordinate algebra, with dimension at most the number of solutions. Therefore it cannot preserve a genuine missing ideal consequence. This argument requires D>=2 and the actual input degree bound; both are present.

The local defect assertions are also correct. On Q_{D-2}, both multiplication orders reach exactly the same union mask. A quadratic input f(T) annihilates that subspace because each f*m is obtained from the admitted input by successive multiplications staying within cap D. Thus the defect operators kill Q_{D-2}; their rank bounds follow without asserting that they preserve the filtration layer or map into a special boundary summand.

The dual span condition is precisely the full kernel condition: a shifted functional restricted to B_{<=D-1} must factor through the restricted quotient map. Extension of a functional from that image to Q gives the required member of the full dual span. Testing only one functional or initial Macaulay multiples would not suffice.

The filtration size statement can be sharpened from q>=D to q>=2^(D-1), as independently proved in `quotient-exponential-rank-review.md`. This applies when the certificate retains any independently proved ideal consequence, including UNSAT separators and solution-count rank excess. The proof uses a degree-compatible multiplicative monomial order; Boolean leading-term overlap is accounted for. Neither bound establishes existence of a certificate.

No defect in the reviewed mathematical claims was found. The note correctly leaves the field-compatible infinite truncated quotient and the independent ideal-membership/count bridge as construction obligations. An operator family satisfying only generic local relations must not be labeled a Semaev lower bound without the exact K-valued equation and that bridge.
