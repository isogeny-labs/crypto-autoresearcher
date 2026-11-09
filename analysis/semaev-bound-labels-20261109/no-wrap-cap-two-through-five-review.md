# Independent review: no-wrap cap two through r=5

Date: 2026-11-09. Source-only review of `no-wrap-cap-two-through-five.md`. No execution.

**All three lemmas are correct, establishing the claimed cap-two upper bounds for r=1,...,5.**

The reduced equation E=A(x)+x*A(q)+q² follows from y=x+1+A(q) and xy=q². The substitutions are affine in Boolean coefficient coordinates, including the earlier constant-coefficient elimination; they preserve cap-two derivations via affine-cofactor corrections.

For odd r, q has degree at most (r-1)/2. Consequently x*A(q) has degree at most 2r-1, and the coefficient at T^(2r) is exactly x_r. Deriving x_r and eliminating it leaves the same reduced system for r-1. This is a valid derivation step, rather than a set-theoretic degree argument.

For even r=2d, each independent quadratic monomial x_i*q_j contributes the two-vertex coefficient vector at i+j and i+2j. These are distinct vertices. The j=1 edges connect vertices 1 through r+2. For each larger j the two new highest vertices connect to the already connected component through the stated lower endpoints. Thus the graph on 1,...,2r is connected, its edge space has codimension one, and the all-ones functional is its only annihilator. The constant output row is zero. Summing positive coefficient rows gives E(1)=q(1), a nonzero linear form in the independent q bits. This proves exactly the claimed initial affine-span characterization; it says nothing by itself about saturation.

For r=4, substituting q=c(T+T²) indeed gives A(q)=c(T+T⁴). I checked all eight displayed coefficient rows directly, including the required ce term in R4. R2+R5+R8=b+d+f+c. After eliminating d, the stated R2' and R3' are correct, and R3'+R2'+R8=e+c. Multiplication of that affine consequence by c is permitted at cap two; adding R7=ce derives c. Every remaining product c times a variable is then available at the same cap, yielding the full affine ideal. No quadratic-source multiplication at cap two is used.

The r=3 and r=5 bounds follow by the odd-r reduction from r=2 and r=4. The statement correctly stops short of a general even-r induction. These are symbolic upper bounds for the specified no-wrap regime n>4r; they do not alter the previous odd-diagonal lower bounds and do not establish a growing lower bound in either regime.
