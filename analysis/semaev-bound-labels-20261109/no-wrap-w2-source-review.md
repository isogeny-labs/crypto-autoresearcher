# Independent source review: bounded no-wrap W2 producer and replay

Date: 2026-11-09. Read-only source review of `no-wrap-w2/closure.py` and `no-wrap-w2/replay.py`, as initially supplied before the campaign. No campaign or tests executed by this reviewer.

## Mathematical checks

The producer's source construction and replay's independently expanded source agree with the coefficients of (xy)²+xy+x²+y²+1 in the no-wrap regime. Boolean coefficient squares are reduced correctly. Both use the full set of nonzero coefficient rows.

The producer keeps independent raw events and tracks echelon-row provenance as XOR combinations of those events. Assigning a proposed event its next event bit before reduction is valid; dependent proposals are discarded without advancing the event list. Each retained echelon row therefore has correct raw-event provenance. A variable multiplication event references a complete affine row represented by earlier events. No quadratic row is multiplied at cap two.

Ordering pivots by degree followed by mask ensures that echelon rows whose pivots have degree at most one span the entire affine intersection. Indeed any nontrivial combination containing a higher pivot retains a highest such pivot. The producer repeatedly multiplies every affine basis row by every variable until no new independent row appears, giving the full saturated W2.

The replay independently reconstructs polynomial sets, checks each input event or XOR-source multiplication event, and requires the multiplication source to have degree at most one. It verifies event independence, input containment, and closure of the complete affine intersection under every variable multiplication. Derivation provenance proves its space is contained in W2; input containment and saturation prove the reverse containment. Thus equality is certified, not merely a closed superset.

The known affine two-point generators are encoded correctly. A missing one in the certified closed-containing space proves LFD>=3. If none is missing, the replayed derivations plus degree-preserving affine ideal reduction prove LFD<=2. No exact LFD is reported merely from the upper bound. These labels rely on the separately proved no-wrap solution theorem n>4r,z=a6=1 and are not measurements of an arbitrary supplied modulus or diagonal parameter family.

## Admission corrections identified before execution

The initial replay uses Python assertions for essential validation. It must explicitly refuse execution under optimized Python (`if not __debug__: raise RuntimeError(...)`), or replace assertions with unconditional checks. Otherwise `python -O` removes the validation. This was communicated to the parent before the campaign.

The initial CLI reads JSON with unbounded `read_text()` before checking event count. A finite artifact-byte cap should be enforced before parsing. The r<=12 bound limits legitimate generated artifacts, but does not bound an untrusted replay file before allocation. This was also communicated to the parent. The producer's maximum independent-event count and its finite variable/monomial universe otherwise bound its allocations and termination.

These are source-review findings, not evidence of a campaign result. Any subsequently applied fixes should be identified by the actual source revision and checked before treating this initial review as acceptance of the corrected replay.
