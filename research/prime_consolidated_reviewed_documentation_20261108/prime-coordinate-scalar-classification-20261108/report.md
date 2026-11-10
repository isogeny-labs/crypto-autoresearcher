# Coordinate scalar certificates: coverage obstruction and next construction

Independent written review accepted the coordinate classification with no substantive algebraic defect. This is source-static mathematics, not runtime validation or official status promotion.

For M=2^s coordinate values, any nonzero scalar restriction of the actual quartic covers at most four projected pairs. An x-first contiguous prefix covers at most two for s>=2. Each x-fiber has at most two quartic roots. Thus covering all invalid pairs solely with this scalar family requires at least ceil((M²−2M)/4) arbitrary-subcube clauses or ceil((M²−2M)/2) prefix clauses. Other PC/SAT certificates, membership, auxiliary-domain reasoning and coefficient charts are outside the bound.

The lifted originals g1=L²−S and g2=CL−H cannot individually become scalar through projected-only restrictions. Nevertheless E=H²−C²S=C²g1−(CL+H)g2 exactly equals the existing quartic. If E restricts to c!=0, multipliers C²/c and −(CL+H)/c reject the projected cylinder without auxiliary assignments. Conditional product degree is at most four, or two after a whole coordinate is fixed. The same coverage bound applies.

Membership differs: a nonsquare curve RHS at fixed x makes its indicator1 and rejects all M partner values. Its current table construction unnecessarily spans both coordinate blocks; a support-local Möbius transform yields the same polynomial. No implementation or measured advantage is claimed.

The next design replaces the table with an Euler circuit: Q=x³+ax+b, W=Q^((p−1)/2), acceptance W(W−1)=0. It retains zero RHS, permits squares, and excludes nonsquares. Fixed invalid x admits a degree2 PC propagation derivation in the extended circuit variables. Expanded flat certificates can grow in degree/size. Per-wire canonical-domain checking is not supported by the existing single-suffix adapter; naive domain exclusion can be large. These are explicit design obligations, not assumed facilities. Independent written review also accepted this next design with no substantive defect; domain/coverage and certificate representation remain implementation dependencies.

Current engine schedule is {0,s,2s,n}, omitting 2s−1 for s>1; fallback fixes n bits. Complete projected coverage, witness reconstruction, construction/checking costs and all chart obligations remain. Administrative target remains106+6 cells and five leads; no budget reset, retry, candidate import or scientific execution.

Sources: mathematical-note-v2.md; independent-review.md; source-bindings.json; euler-membership-design-v1.md; frozen plans and derivations. Exact local source: encoding.py:36–97, adapter.py:110–200, engine_counted.py:213–275 and442–449. Scope applies to coordinate encodings, not the six coefficient charts.
