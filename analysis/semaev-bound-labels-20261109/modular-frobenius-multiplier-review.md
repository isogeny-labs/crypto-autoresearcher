# Independent review: Frobenius multiplier obstruction

Date: 2026-11-09. Source-only review of `modular-frobenius-multiplier-obstruction.md`. No execution.

**The span-preservation, relative-shift obstruction, trace condition, and radical/invariance lemma are correct before eliminating the trace relation.** Interpret every shift modulo n; in formulas containing n-j choose its representative 1<=j<n.

Simultaneously applying Frobenius to x and G produces exactly a Frobenius transform of xG, so its field-coordinate rows stay in the same span. For unequal shifts, applying inverse Frobenius reduces to their relative shift. Squaring fixes Boolean variables and only transforms field coefficients, making these legitimate constant output-row operations.

The only possible field-valued cubic part of x^(2^j)G is x^(2^j)*x*y. Polarization in the x block gives the stated condition x*z^(2^j)+z*x^(2^j)=0. Fixing nonzero z makes Frobenius^j scalar on V. Ratios of nonzero solutions of X^(2^j)=aX belong to the fixed subfield of degree gcd(j,n), bounding the binary solution-space dimension by that degree. For a nonzero relative shift and odd n>=3, this is at most n/3 and cannot contain the half-dimensional V. This proves the field-valued obstruction, not the scalar trace obstruction.

Taking trace pairs the polarized coefficient with the independently varying y block, giving precisely condition (2). Affine B and the epsilon term cannot contribute cubic terms. The condition is therefore necessary and sufficient for that particular scalar product to have degree at most two in the unsliced coordinates.

## Radical calculation

For nonzero lambda and gcd(j,n)=1, the radical equation is

    (lambda*x)^(2^(n-j))+lambda*x^(2^j)=0.

Raising to 2^j gives lambda*x+lambda^(2^j)*x^(2^(2j))=0. Because n is odd, gcd(2j,n)=1, so exponent 2^(2j)-1 is coprime to 2^n-1. Thus there is exactly one nonzero radical element. Also gcd(2^j+1,2^n-1)=1, and the unique r satisfying r^(2^j+1)=lambda^(-1) satisfies the radical equation: lambda*r=r^(-2^j), whose 2^(n-j)-power is r^(-1), equal to lambda*r^(2^j). This independently verifies both the exponent and uniqueness claimed.

The form is alternating and its radical is one-dimensional, hence its rank is n-1. If an isotropic k=(n+1)/2 dimensional subspace failed to contain that radical, its projection into the nondegenerate quotient would retain dimension k, exceeding half the quotient dimension. Therefore it must contain the radical. Applying this to lambda=a*w for every nonzero w in V yields the inverse-power containment (4). The power map is a permutation of K*, so its containment on the finite V-minus-zero set implies a permutation of that set.

Containing the radical is only necessary for total isotropy, as the note states. No impossibility theorem for the inverse-power condition is inferred. Nor do these restrictions exhaust arbitrary linear multipliers or quadratic-feedback closure.

The before-trace-elimination qualifier is essential throughout: affine elimination of ell can create additional cancellations modulo its multiples. The conclusion does not assert a complete sliced W3 description, a stable closed space, or any new LFD lower bound. No substantive mathematical correction is required beyond making the canonical shift representative explicit where needed.
