# Independent review: finite-selector bounds and coordinate transport

Date: 2026-11-09. Source-only review of `finite-selector-bounds-and-transfer.md`. No enumeration, solver, build, or replay.

**The universal Boolean bound, count semantics, and qualified nonlinear transport theorem are correct.**

For independent selector blocks the normalized S3 expression has Boolean degree at most s_X+s_Y, since field squaring is a linear Frobenius map on coefficient coordinates. This applies to the actual selector maps, including repeated codes; replacing their images by a vector-space span changes the system. Invalid-code constraints and shared variables require their exact own system, as stated.

At cap N+1 every multilinear Boolean polynomial is eligible for multiplication by every variable. The resulting minimal closed space is the full Boolean ideal, proving LFD<=N+1. Under the study's ordinary-polynomial bridge with explicit Boolean field equations, reduction of higher-degree polynomials does not raise degree, so the same bound transfers to the normalized system. The claim is not a bound for an arbitrary unnormalized high-degree input list whose generator eligibility differs.

Exhaustive code counting measures Boolean assignments, not distinct field pairs or group lifts. The multiplicity product formula is correct for independent unconstrained blocks; coupled validity constraints need not factor. Exact count alone supplies no degree lower bound. A separately checked quotient/codimension excess over that count is the requisite ideal-consequence bridge.

For nonlinear injective coordinates, adding equations for the source image and retaining inverse degree are both necessary. Under the stated hypotheses, h(q(u)) belongs to the image-constrained source ideal and has degree at most tL. A source derivation at cap max(d,tL) transports through a degree-s substitution at cap s*max(d,tL). The inverse identity restores the target polynomial h exactly. Applying this to a degree-compatible ideal basis and then reducing without degree increase proves the claimed target LFD upper bound. No hidden factor depending on the number of coordinates is required, but neither may the source image constraints or target-basis degree L be omitted. The stated degenerate-map exclusions avoid s=0 or t=0 ambiguity.

For a nonempty affine solution set, L=1 is valid in the Boolean ring; ordinary polynomial representations additionally include the already available Boolean field equations. Noninjective code maps have no inverse and are correctly excluded from this transfer theorem, while the universal cap and exact counting remain valid.

No mathematical correction is required. The label/custody rules correctly preserve exact equations, domain multiplicities, unknown exact LFD/FFD, and separate dataset admission.
