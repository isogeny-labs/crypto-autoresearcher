#set page(paper: "a4", margin: 15mm)
#set text(size: 9pt)
= Complete class inputs and historical bijection
2026-11-02 | EXP-PEXT-bf8f96 | H-PEXT-c3a11d | TASK-20261102-6ea195

All five prescribed class cohorts are materialized and independently checked. New q3/n5 representatives have a checked one-to-one polynomial isomorphism mapping to all 488 archived classes, preserving actual twists and exceptional models. These are deterministic input-coverage results; the scientific contract stays review_required/unapproved.

#image("cohort-flow.svg", width: 100%)

#table(columns: (1.7fr,1fr,1.4fr,1.5fr,1fr), inset: 4pt,
 [*Cohort*],[*Field Q*],[*Candidate slots*],[*Nonsingular*],[*Classes*],
 [q3/n5],[243],[117,855],[117,370],[488],
 [q5/n3],[125],[15,625],[15,500],[252],
 [q7/n3],[343],[117,649],[117,306],[690],
 [q11/n3],[1,331],[1,771,561],[1,770,230],[2,662],
 [q13/n3 descriptive],[2,197],[4,826,809],[4,824,612],[4,400])

*Coverage:* p>3 short-model nonsingular cardinality is Q(Q-1). Characteristic 3 families A=(a2,0,a6), a2,a6 nonzero, and B=(0,a4,a6), a4 nonzero, give (Q-1)(2Q-1). The checker reconstructs complete residual isomorphism orbits, rejects overlap using a dense owner array, checks canonical minima and exact cardinality. Independent polynomial arithmetic generates its acceleration tables. This fits all original cohorts without whole-member JSON; current bounds are Q<=2197 and 10,000,000 candidate slots.

*488 witnesses:* x_rep=u^2*x_old+r, y_rep=u^3*y_old; independently expanded identity f_rep(u^2*X+r)=u^6*f_old(X). Every old model and new class is used once. Historical indices are polynomial-basis coefficients, not log labels; old/new ordering differs. Builder, fixture, field identity and all input bytes are hash-bound. The legacy mapper pins modulus X^5+2X+1 and the full identity fingerprint; the generic checker validates the named field parameters. No archived genus/order outcome selected inputs.

*Checks:* input-checks.txt records rustc1.99.1, Python3.9.25, source hashes, retained warnings, four passing software methods, all five independent full-input checks and a valid488-class bijection replay. All-pair arithmetic tests cover F9/F125/F243; controls cover F3/F5/F9, witnesses and malformed inputs. Exact counts, complete byte hashes and replay commands are in report.md; final log marker ALL_COHORT_INPUT_CHECKS_PASS.

*Next:* join all byte-bound classes with rational-T cosets and projective structures, preserving scalar identities and exact shard coverage. Connectedness/geometric genus, Frobenius descent/Type2, original geometric P3 and descriptive q13 H1 analysis, exports/checkpoints and frozen launcher bindings follow. No canonical scientific graph change. Earlier snapshots remain intact; archive completion requires the actual native receipt and GitHub publication.
