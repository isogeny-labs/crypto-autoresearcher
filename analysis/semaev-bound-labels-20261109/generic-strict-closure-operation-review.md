# Independent review: saturated strict-closure operation bounds

Date: 2026-11-09. Source-only review of `generic-strict-closure-operation-bound.md`. No closure execution, benchmark, or build.

**The algorithm, saturation proof, and operation/storage bounds are correct in the stated arithmetic model.**

With degree-first pivots, the first selected pivot in a nonzero combination cannot cancel against rows with later pivots. Consequently low-pivot rows span exactly the full eligible intersection with degrees at most D-1, including after later insertions. Immutable stored rows therefore need processing only once. Every insertion has valid strict-cap provenance, and exhaustion of their variable multiples gives a closed containing space. These two inclusions prove exact W_D rather than one-pass Macaulay rank.

There are at most M independent pivots and at most L eligible pivots. Thus at most R+N*L insertion attempts occur, each performing at most M whole-row XORs. An M-bit XOR requires O(M) coefficient operations under the unit indexed-bit-access model, giving O((R+N*L)*M²) arithmetic. Dense row coefficients occupy at most M² bits. The note explicitly accounts separately for queue/pivot metadata, monomial masks, optional indexing tables, and non-unit access/ranking costs; the dense-row storage expression is not presented as total implementation memory.

At D=N+1, every Boolean row is eligible and M=L=2^N. The resulting R*4^N+N*8^N arithmetic expression and 4^N dense-row storage follow. The N=0 case is safe with M=L=1 and no variable products; D=0 is separately specified with L=0. The bound does not imply that a distinct F4/F5/SAT backend has the same work profile.

The exact-LFD criterion is also correct: d_F<=d precisely when every ideal polynomial of degree at most e lies in W_e for every e=d,...,N+1. The first condition includes lower-degree polynomials whose required cap is d. Checking only a successful isolated smaller cap would omit later degree falls. Exact evaluation on all solutions can determine the ideal intersections, but its cost and the repeated closure computations are additional to the single-cap expression.

No correction is required. This proves a total arithmetic bound for the named closure procedure, with explicit model exclusions, not a measured native-instruction or wall-time bound.

## Source readback: finite-selector operation envelope

Also reviewed the added `closure_algorithm_cost_bound` in `join_finite_selector.py`. It instantiates M=2^N, R=n, and D=N+1 correctly. Candidate attempts n+N*M, whole-row XORs (n+N*M)*M, Gaussian coefficient XORs (n+N*M)*M², product-column visits N*M², and dense basis coefficient bits M² are conservative maxima for the named reference algorithm. Product-column visits are separately exposed and should not be silently folded into the Gaussian coefficient-XOR number.

The source labels these as theorem-derived and not executed, identifies the arithmetic model and excluded costs, and keeps native instruction count and wall-time bound null and training-cost eligibility false. Parsing/reconstruction, indexing, metadata, solution extraction, provenance, and I/O remain excluded explicitly. Thus the envelope is not misrepresented as a total measured join cost or a bound on the native solver. It retains exact input/equation binding and hashes the proof/review sources at CLI output time. No new test or production artifact was executed by this reviewer.
