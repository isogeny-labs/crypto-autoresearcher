# Exactness route for the n51 degree-four seed

The accepted n51 polynomial-01 degree-four map proves only
`W4(F) subset ker(pi4)`. The current sliced degree-five computation uses
this kernel as its seed. If it kills the constant, seed exactness is the
missing premise before that observation can say anything about membership
in the true `W5`. Lemma 1.6 of the theorem dossier states the bridge.

There is a source-and-receipt route to exactness that is logically
independent of the queued sliced direct-W4 rank calculation:

1. The original 52-variable D3 seed, SHA-256
   `deb3a6bd3c77db940da319b89fc94c8873fe1d8a509f348116b8b9c76ee80d8a`,
   came from `lfdclose2` and reports `W3_dims ... 10970`, `W3_one 0`,
   two closure iterations. The direct fixed-point invariant in
   `DIRECT-W4-RANK-AUDIT.md` applies verbatim at D3: initial generator
   multiples lie in W3; every added product lies in W3; termination makes
   the rowspace closed. Thus, subject to the pinned native execution
   matching the audited source, its rowspace is exactly W3. The separate
   D3 checker accepted codimension 12509, consistent with
   `23479 - 10970 = 12509`.
2. The D4 producer read that exact D3 seed. The published receipt
   `bounded-d4-archive-001/fresh-n51-poly-01-D5-cascade01-bounded-D4-001.receipt.json`
   records a completed `produce4` with binary SHA-256
   `fc0911db6560fe10b49d88d6206f89f8de6494616020a864c82d8be552749613`
   and output SHA-256
   `c160792a7530b20dd17affcdabafb8d95494eed51c8ee6d818af3212f3e304f6`.
   The build receipt `runtime/blocked-checkpoint-build-001.json` binds this
   binary to the actual `quotient_lift_blocked_checkpoint.cpp` source,
   SHA-256 `b9cbe65514244d15b2a4de1c653783d50322ba18e9334eb5891f348dd487c0cf`,
   and `quotient_checkpoint.hpp` SHA-256
   `553e26f10907206d622684bec776d1e65ee1b91f096b8f0b271b378b9d27816e`.
   Both hashes match the preserved source worktree. The D4 plan lists the
   earlier `quotient_lift_checkpoint.cpp` source hash; that is not the
   source of this binary and must not be used for its provenance. The
   blocked source changes only the triangular high-monomial rewrite:
   outside-block dependencies are accumulated by an F2 matrix product,
   while within-block dependencies are substituted in descending order.
   Its relation-generation and fixed-point loops are unchanged from the
   earlier source.
3. In the actual D4 source, each old nonrepresentative monomial relation is
   multiplied by every variable (the `seed variable` loop), and every
   new relation whose pivot is in the old-coordinate block is multiplied
   by every variable in the `closure round` loop. Each row therefore
   comes from the closure of W3 and belongs to W4. At fixed-point
   termination, the rowspace contains all products of the old kernel and
   is closed under all allowed D4 multiplications. Hence it equals the
   image of W4 in the provisional coordinate space. The exported map
   quotients by precisely that rowspace. On a successful, faithful native
   execution, its kernel equals W4, rather than merely containing W4.
4. The original D4 checker accepted the 45,615-dimensional quotient.
   The affine-slice equality in Proposition 2.5b transfers the exact
   original W4 closure to the 51-variable slice. The sliced quotient
   checker established onto-ness with the same dimension, so the sliced
   kernel would be exactly the sliced W4.

This is a proof of the algorithmic invariant and a provenance chain,
**not an independent primal rank certificate**. It relies on the native
source/binary and execution receipts faithfully describing the D3 and D4
computations, and on the recorded affine-slice construction. The queued
direct-W4 calculation tests the critical equality through a different
algorithm and independently reconstructed equations: its target rank is
226437 in the 272052-column sliced universe. Until that reverse check
finishes, describe seed equality as source-audited conditional evidence,
not as a checker-certified fact. Even if equality is established, a
`projection_kills_one` producer status needs its own checked D5 derivation
before claiming `1 in W5`.

For the desired lower bound of six, a D5 quotient with nonzero image of
one is more direct: independently check the candidate map, combine its
positive codimension with the already checked zero solution count, and
apply Proposition 2.5b to the original system. No D5 conclusion follows
from this D3/D4 audit alone.
