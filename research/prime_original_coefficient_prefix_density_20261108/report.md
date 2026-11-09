# Conditional pruning on an original coefficient

The finite h5 interval chart admits a moment-prefix predicate directly on its original A1 coefficient. It needs no new moment fields. Fix v,q,B0 in A=X³+vX²+A1X+A0, B=qX+B0. For finite target(a,b), norm and target rows imply

u=a+2v−q²; S=−u−5t;
E=2A1+c, c=(a+4t)u+v²−2qB0+10t²;
A0=b(qa+B0)−a³−va²−aA1.

Keep all original source rows. A0 remains in the original projection, constrained or reconstructed by its target row; no target-coordinate division is used. A clause conditions on every bit of original v,q,B0 and a low-bit A1 prefix. It leaves A0/witness bits unassigned and preserves the original bit layout. This arbitrary subcube is not accepted by the current contiguous-prefix checker without a new authenticated semantic rule.

For any canonical E arc[L,U], pull it back to A1 by intersecting[0,p−1] with [ceil((L−c+mp)/2),floor((U−c+mp)/2)] for m0,1,2. Intersect each resulting interval with the original A1 prefix using signed mathematical ceiling/floor. This is O(h) endpoint work for the complete moment lift/arc predicate, plus field/input arithmetic, authentication and O(log p) literal work. Charge all proof and model/witness checking. No two-field compilation overhead is incurred in this specialized rule; the earlier generic moment-extension design does incur that overhead.

A quantitative regime gives nonvanishing rejection beyond the global E bound. Let M=B−1>=1,K=10M² and p>K. Choose H as the least power of two at least ceil((K+1)/2), and d=log2 H. Then d<ell=ceil(log2p), so at least one original A1 bit remains syntactically unassigned. For a fixed triple with S in[0,M], let G be the A1 prefixes admitted by global E in[0,K]. At most three pullback intervals, each shorter than or equal to H, imply |G|>=ceil((K+1)/3). Conditional E has at most floor(2M²/5)+1 values. Consequently the rejected fraction within G is at least

max(0,1−(floor(2M²/5)+1)/ceil((10M²+1)/3)),

at least3/4 for every M>=1; this guaranteed lower bound tends to22/25 in the stated growing-width regime. Uniformity is over the affine shift and fixed triples with this S, not over solver trajectories. Each S can be realized by coefficient triples via v=(q²−a−5t−S)/2, but remaining equations may make the full root fiber empty. Syntactically free bits also need not represent independent surviving choices. These are precise limitations, not measured speedup claims.

Hand control: p17,y²=x³+1,target(0,1),B2,t0,q1,v0,B0=0 gives S1,E=2A1. Global pullback[0,5]U[9,13] gives six low-three-bit prefixes; conditional E0 retains only prefix0. Five of six are rejected. The clause has15 fixed-triple bits plus3 prefix bits. The critic additionally proved this fixed triple has no full source root: S1 forces U=X⁴(X−1), E0 gives A1=A0=0, and the norm X⁶−X⁵−X² differs from XU=X⁶−X⁵. Thus this is an arithmetic predicate control, not evidence of savings on a feasible branch. No experiment or feasibility census was run. p<=K invalidates this no-wrap density theorem; h4 q0 does not admit this h5 coefficient2 transport.

The next performance gap is whether an actual coefficient-search ordering encounters these branches with lower charged work than existing propagation and direct h5 pair/triple MITM. Do not enumerate all triples/prefixes to exploit a constant density. This does not establish a regularity reduction. Original six coefficient cells use coset support and need separate interval transport. All106+6/five leads, exhausted producers, reserved independent slot and failed metadata caps remain unchanged.

Independent producer-visible written critique accepted the scoped theorem; see independent-review.md. No blind rederivation or native scientific gate is claimed.
