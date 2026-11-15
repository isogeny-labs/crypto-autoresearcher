# SA-09b deviations

(Saved by the main session verbatim from the executor's final message.)

1. Three inert primes (3, 5, 13) used for 37a1 instead of two; K = Q(sqrt-7) (h = 1) with conductors {1,3,5,13,15}. Reason: h = 1 keeps heights small; 13 adds a third bound.
2. Primes used are about 2^18 (266239, 267199, 268291), not larger, because they must split completely in the conductor-195 ring class field.
3. Level 39 and 65 for 37a1 were not algebraised or reduced mod p (recognition failed at 1300 and 1900 digits for level 39; needs more than about 3000 digits and more than one 10-minute foreground call). Relations for B > 15 are therefore not F_p-verified. Substitute: class-group fibres compared with complex-analytic Hecke neighbour lists up to conductor 65 (9/9 edges) and rank computed from the class-group fibres.
4. Rank/points at larger B comes from the class-group fibre computation (`arith.py`), validated edge by edge against the numeric neighbours (17/17 edges across 37a1, 36a1 with Q(sqrt-23), 36a1 with Q(sqrt-47)). The B = 500 rank uses a random projection mod a 31-bit prime.
5. Second field for 36a1 (Q(sqrt-47)): ranks only. No Heegner-point algebraisation or F_p reduction; numeric check limited to conductors {1,5,11,55} (all a_l = 0).
6. "Largest conductor bound reachable in 60 minutes" was read as B = 250 for 36a1 and B = 500 for 37a1, since the rank step is cheap and the limit is the class-form enumeration.
7. Descent test: 36a1 uses SA-09's levels 1, 5, 7 (45 points) because the conductor-35 points were not saved; 37a1 uses all 49 points. Repeats of the same point are allowed in the sum. Control sets are random points of E(F_p), 100 per prime.
8. No git or parent-directory edits. REPORT.md and DEVIATIONS.md could not be written by the Write tool; text was returned in the final message instead.
