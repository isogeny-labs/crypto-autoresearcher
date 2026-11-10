#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
= First no-wrap obstruction and an infinite constant bound
2026-11-09. Frozen exact-computation attempt1; symbolic follow-up.

*Scope:* Fixed-m=2 normalized Boolean Semaev equations, z=a6=1, V=span(1,t,...,t^r), and n>4r. All members have precisely the two constant solutions (0,1),(1,0). Twelve deterministic coefficient systems were computed; no timing or population estimate is claimed.

#image("closure-profile.svg", width: 100%)

*Observed:* All controls and all12 certificate replays passed. For r1–5, full affine ideals are derived at cap2. For r6–12, the closed space misses a named affine ideal consequence, proving LFD>=3. At r6, rank(W2)=71, affine dimension5, codimension35. An independent reviewer replayed this certificate and checked all27 manifest entries.

*Symbolic explanation:* At r6, affine elimination leaves nine variables. Two polynomial coefficient generators have gcd t(t+1); their shifted spans have dimension11. The sole quadratic cancellation gives zero, so the reduced space has no nonzero affine consequence and is already closed at cap2. This independently recovers the measured dimensions.

*Infinite transfer:* Setting coordinates above degree6 to zero preserves strict cap2 derivations. The missing coordinate remains a known ideal consequence in every larger member because the same two-point count holds. Therefore LFD>=3 for every r>=6 and n>4r. Selector lifting also gives LFD<=4 at r6. No growing lower bound follows yet.

*Custody and limits:* Source and protocol were pushed before computation. One local attempt; CPU ceiling60seconds, wall ceiling90seconds, memory512MiB, no new cloud job. Raw DAGs, complete closure checks, source hashes, controls, export and reviews are retained. The protocol's reference-arm hash repeated the producer hash; replay source was independently bound correctly before execution. Export records the actual replay hash and preserves this metadata deviation. These are finite computation and reviewed written proofs, not a Lean theorem.
