# Independent audit: restriction transfer, one-bit extension, and finite feasibility

Date: 2026-11-09. Source-only mathematical review of `lower-bound-transfer-obligation.md` and `certificate-feasibility-contract.md`. No solver, build, experiment, or certificate replay. Verdict: the stated transfer lemmas and finite feasibility equivalence are valid at their qualified scopes; none constructs an infinite hard family.

## 1. Restriction-indicator lower bound

For an affine restriction rho of codimension t, strict bounded-degree derivations restrict without increasing degree. Generator degrees may drop, but that only makes additional target generators eligible: every eligible original generator maps to an eligible restricted one. Affine multiplication is simulated by scalar combinations and variable products within the same cap.

If G=rho(F) is UNSAT, the affine-subspace indicator e has degree≤t, vanishes on every zero of F, and restricts to1. Because explicit Boolean equations make the ideal the Boolean vanishing ideal, e belongs to the original ideal. Thus

d_ref(G)≤max(d_LFD(F),t,2).

The extra2 is a conservative bridge convention; it is harmless for the stated d_ref(G)≥3 target. If d_ref(G)>t, the desired lower bound d_LFD(F)≥d_ref(G) follows. The strict inequality is essential. A high-codimension embedding of R35a does not transfer its degree5 lower bound to the full-field system when the indicator degree is34.

Fixing **all** s selectors yields only affine fibres and hence cannot furnish a hard restricted refutation. A successful restriction route must retain enough interacting selector variables while keeping indicator degree below the hard refutation degree.

## 2. One-bit normal-form identity

After the compatible trace relation is eliminated, an affine Artin–Schreier section r0(t) exists with r0²+r0=s+c, c=sqrt(a6)/z. All its preimages are r0+epsilon for one Boolean epsilon. Since epsilon²=epsilon and its Artin–Schreier image is0,

G(x,r0+epsilon)=G0(x,t)+z epsilon.

For any F2-linear lambda with lambda(z)=1, the output projection P(u)=u+z lambda(u) and q=lambda(G0) give the equivalent coordinate system

F_red=P(G0)=0,     epsilon+q=0.

The original reduced system has coordinates of L_z(G0)=G0²+zG0. Since ker L_z=F2 z and P projects along that kernel, L_z restricted to ker lambda is injective and maps onto im L_z. Thus the two reduced output systems have the same coordinate row span. At degree caps≥2, every quadratic-or-lower row is eligible, so their strict closures agree. The affine trace-elimination repairs are also available at cap2. No unrestricted low-cap row-basis invariance is required.

The normal-form domain must retain x∈V and r in the specified affine Artin–Schreier preimage of the remaining s-domain. Treating r as an unrelated unrestricted block would change the system.

## 3. Additive refutation overhead is sound

For UNSAT F_red and G_red=F_red∪{epsilon+q}, clearly d_ref(G_red)≤d_ref(F_red).

For the reverse direction, substitute epsilon=q into a strict cap-D Boolean derivation. A multilinear line h=h0+epsilon*h1 has substituted degree≤deg(h)+1. Every eligible original F_red input stays unchanged and the definitional input maps to0.

If a proof step multiplies a source h with deg h≤D−1 by an ordinary variable, its substituted source has degree≤D and the product fits capD+1. If the step multiplies by epsilon, multiply the substituted h by each monomial of q, whose degree is≤2. The source has degree≤D, so the two successive variable products fit D+1 and D+2. Their sum equals the substituted target because substitution into the Boolean algebra is a ring homomorphism: q²=q. This equality does not excuse an unbudgeted intermediate operation; the argument explicitly pays D+2.

Therefore d_ref(F_red)≤d_ref(G_red)+2. The note properly limits the claim to refutations. For SAT LFD, an overhead depending on the arbitrary output degree still fails to supply max(C,deg f), so no general SAT-LFD equivalence follows.

The conservative +2 is justified; no smaller overhead was established by this audit.

## 4. Exact finite feasibility contract

Let C have columns c_m for all squarefree monomials of degree≤D, let T_i be q-by-q matrices, and R a right inverse. The constraints c_1=e1, C(f_j)=0, T_i c_m=c_(m union{i}) for degree(m)≤D−1, and CR=I exactly encode rank-q proper closed kernels.

**Forward:** for any low-degree u with C(u)=0, linearity gives C(x_i u)=T_i C(u)=0. This controls the entire low-degree kernel, including cancellations, rather than just literal input multiples. CR=I proves rankq and c_1=e1 separates1.

**Reverse:** for a rank-q closed kernel, multiplication defines a well-defined linear map on C(B_≤D−1): representatives differ by a low-degree kernel vector, whose product stays in the kernel. Extend it arbitrarily to the whole quotient space to obtain T_i. Surjectivity supplies R; a quotient basis change normalizes C(1) to e1. This loses no certificate.

The unknown and equation counts in the contract match the displayed matrices: 2Mq+Nq² unknown bits and q+rq+NLq+q² scalar equations before redundant-row removal or SAT gate encoding.

No global commutation or idempotence constraints should be added. Such matrices would form an actual Boolean algebra representation; simultaneous decomposition into joint0/1 eigenspaces, together with a nonzero cyclic vector and generator annihilation, supplies an actual Boolean solution. The truncated identities only on the allowed low-degree image are crucial for UNSAT nonmembership certificates.

The LFD bridges are correctly separated: UNSAT needs an independent unsatisfiability proof; SAT/unknown can use a rigorous solution-count upper bound strictly belowq or a specified missing ideal consequence with independent membership proof. A certificate candidate does not prove its own bridge. Searching finitely many q values, timing out, or finding infeasibility at one q does not settle all ranks or unboundedness.

## 5. Publication scope

These are useful transfer and certificate-encoding theorems. They reduce the search to exact admissible structures and avoid invalid amplification shortcuts, but the parameter-uniform construction is still missing. Source-level proof review is not an executed encoder/checker validation or a new large-instance certificate. No infinite-family lower bound is claimed.
