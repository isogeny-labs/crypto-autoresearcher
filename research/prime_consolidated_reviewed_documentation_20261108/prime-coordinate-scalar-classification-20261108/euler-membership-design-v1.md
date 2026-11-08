# Source-only design: certified Euler membership circuit

Status: mathematical construction/design, no implementation, imports, tests, manifest generation, or execution. Extends the reviewed coordinate classification without reopening its frozen files. Assumptions: p is a verified prime >3, curve and target satisfy that note, and projected digit coordinates are injective. This concerns the coordinate chart only; the six coefficient charts need separate proofs. No producer or independent scientific allowance is allocated.

## Exact circuit, including zero RHS
For each coordinate X independently let q=X³+aX+b and e=(p-1)/2. Introduce field wires U,Q with equations

    G_U=U-X²=0,
    G_Q=Q-UX-aX-b=0.

Compute Q^e by deterministic left-to-right binary exponentiation: start V=Q at the leading one of e; for each remaining exponent bit append a square wire Z=V²; if the bit is one append a multiply wire T=ZQ; update V accordingly. Each new wire has its equation G_j=Z_j-Z_u Z_v=0. Let W be the last wire. Append acceptance equation

    A=W(W-1)=0.

Euler's criterion says W is 0 for q=0, 1 for a nonzero square, and -1 for a nonsquare. Since p>3, acceptance holds exactly for square-or-zero RHS. This reproduces the existing membership predicate M_X=0, including the crucial zero case; demanding W=1 would incorrectly discard points with ordinate zero. No Legendre-table polynomial is built.

For ell=bit_length(e), h=popcount(e), there are ell-1 squarings and h-1 additional multiplications after Q. Exactly K=2+(ell-1)+(h-1)=ell+h new field wires and K+1 equations per coordinate, with no wire for the initial V alias. Both coordinates use2K wires and2(K+1) equations. This is a symbolic size count, not measured performance.

## Projection and domain obligations
Every X in F_p uniquely determines every circuit field wire. Thus adding the circuit plus acceptance preserves exactly the coordinate pairs admitted by the existing membership-augmented system. It also preserves the existing lifted system if redundant membership is added: its elimination E=0 implies that each curve RHS is square-or-zero (from the reviewed discriminant argument, treating X=r separately). Original EC witness reconstruction and complete projected coverage remain mandatory.

For compatibility with the Boolean checker represent each wire Z by k=bit_length(p) bits, Z=sum 2^i z_i modulo p. Canonical representatives require 0<=integer(Z)<p for every wire. A direct domain CNF can forbid every integer p..2^k-1, costing (2^k-p) clauses of length k per wire. This may be large; no logarithmic-cost canonical-domain implementation is assumed. A separately specified comparator circuit could replace it, but would add variables, equations/clauses and proof obligations. Noncanonical aliases do not invalidate polynomial identities over F_p, yet abandoning canonical ranges changes witness uniqueness and the supported domain contract and is not silently permitted.

The existing adapter supports only one legacy auxiliary-range bound on the entire suffix integer. It does NOT directly support independent bounds on each new wire block. Therefore this design is not drop-in compatible with the current adapter/domain verifier. Before implementation, either specify an independently checked product-domain extension and cover semantics, or give a rigorously equivalent supported encoding. The current checker may still check an individual restricted polynomial identity: that does not certify the new domain or a complete transcript.

All circuit equations have Boolean polynomial degree<=2. W(W-1) also has degree<=2. Bit expansion nevertheless creates up to quadratic-in-k term pairs per multiplication; wire count, term count, domain clauses, storage, inverse operations and checking costs must be charged. Low-degree local equations are not evidence of low original-system regularity.

## Exact conditional certificate after fixing a whole coordinate
Fix X=u with q(u) a nonsquare. Evaluate the specified arithmetic circuit to its field constants c_j; its output constant is c_W=-1. This deterministic arithmetic evaluation is future producer work, charged once per attempted coordinate. It is not a precomputed model oracle. Define E_j=Z_j-c_j. The first two restricted equations give E_U=G_U and E_Q=G_Q+u E_U. For every multiplication or square gate G_j=Z_j-Z_u Z_v, c_j=c_u c_v, use the exact identity

    E_j = G_j + Z_v E_u + c_u E_v.

For a square the two predecessor indices coincide; retain both terms or combine correctly. Thus every E_j lies in the ideal of the restricted circuit equations. At the output E_W=W+1 and

    A=(W-2)(W+1)+2,
    1=(1/2) A -(W-2)/2 E_W.

This is an explicit certificate recurrence proving the entire coordinate fiber impossible, without fixing any circuit wire or partner-coordinate bit. The original E/g1/g2 need zero multipliers in this extended-generator proof. For current x-first prefix clauses, fixing x=u gives a representable depth-s rejection of all M partner values; the y-only clause still requires a suitable clause interface or finer prefix.

## Three different degree and size statements
1. **Local equations:** degree<=2 after digit substitution.
2. **PC derivation with retained extension variables:** once X=u is fixed, derive each linear E_j by the displayed recurrence. Multiply the linear E_u by linear Z_v (or bitwise linear combination), add constant c_u E_v and quadratic G_j. Every intermediate polynomial has degree<=2. At the end multiply linear E_W by W-2 and combine with A. This is an explicitly described degree<=2 conditional PC derivation in the EXTENDED system. It does not guarantee the current bounded refute search discovers it.
3. **Flat certificate in the existing identity-checker style:** recursively expand E_j=sum_i q_ji G_i, using q_ji=delta_ji+Z_v q_ui+c_u q_vi, then apply the final identity. Multiplier degrees can grow with circuit path length. A conservative product-degree upper bound is K+2 before Boolean reduction: each recurrence increases the earlier bound by at most one and the final step by at most one. Expanded multiplier term counts may grow severely from branching and digit expansion. No degree2 bound for this flat expanded certificate is asserted. A DAG proof checker could avoid full expansion but would be a new proof format requiring independent verification and accounted cost. Eliminating the circuit variables is yet another operation and can restore high-degree Euler polynomials.

Thus a broad fiber rejection is available symbolically; realizing it cheaply depends on domain verification and certificate representation. No uncharged field-exponentiation primitive, new checker, or auxiliary elimination is assumed.

## Independent review targets and bounded next action
Review exact exponent schedule/count, zero handling, unique field extension, relation to reviewed discriminant, per-wire Boolean domains vs current adapter, recurrence signs including squares, conditional PC-degree2 reasoning vs expanded degree bound, and all scope distinctions. No runtime review is requested.

Rank this as a source-only next-construction design, not an admitted experiment. A minimal publication can append this reviewed design and its critique to the same documentation packet before root admits that packet. Retain the already reviewed classification and its inputs unchanged. No need for separate EXP/RUN, campaign, or source implementation handoff now. If native policy requires publication metadata, one bounded documentation source handoff plus its standard snapshot and one Coordinator decision can cover the consolidated note/report packet; root allocates IDs only after final path scope. No canonical records are edited here.
