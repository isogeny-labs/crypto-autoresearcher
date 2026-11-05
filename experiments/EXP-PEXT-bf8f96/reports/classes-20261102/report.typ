#set page(paper: "a4", margin: 15mm)
#set text(size: 9.1pt)
= Actual curve classes and isomorphism witnesses
2026-11-02 | EXP-PEXT-bf8f96 | H-PEXT-c3a11d

Complete pointed K-model class enumeration, actual twists and explicit model-isomorphism witnesses are now implemented and replayed by a separate polynomial-basis checker. The experiment stays review_required/unapproved; no cover/genus census ran.

#image("class-flow.svg", width: 100%)

*Witness direction:* x_source=u^2 x_target+r, y_source=u^3 y_target. Hence a2'=(a2+3r)/u^2, a4'=(a4+2a2r+3r^2)/u^4, a6'=f_source(r)/u^6. Separate software tests expand f_source(u^2 X+r)=u^6 f_target(X); the checker replays the coefficient formula with independent arithmetic. These give every origin-preserving isomorphism of the stated odd-characteristic models.

*Complete families:* p>3 translates to a2=0, with only scaling between short models. In char3, a2!=0 uniquely translates to A=(a2,0,a6); normalized A-to-A maps have r=0. B=(0,a4,a6), a4!=0, retains all translations. Since a2'=a2/u^2, A/B never mix. Complete residual orbits partition the normalized universe and retain exceptional automorphisms/twists.

*Checks:* source-bound software-tests.txt records versions, commands and warnings:6Rust,6quotientPython,5structurePython and5classPython groups pass, zero failures. Fixed F3/F5/F9 class certificates, full small-field normalization, F3/F5 full affine partitions, polynomial witnesses, a distinct quadratic twist, ten malformed variants, limits and CLI binding are checked. F3 has8classes including4j=0; F5 has12. These are software fixtures, not scientific cover/genus observations.

*Historical cohort:* immutable fixture SHA256 starts8f03e3d1 and endsd9123fa; full hash and path in report.md. Its488 records are the full K-isomorphism cohort with twists. New-family ordering differs; a new488model bijection has not yet been materialized. Match field/model identities and explicit witnesses, not ordinal or j labels.

*Next:* whole-JSON16MiB/1,000,000-candidate limits do not fit n3/q11's1,771,561 candidate models. Build streaming coverage/input manifests and the full historical488 bijection, preserving original cohorts. Full T/structure joins, scalar/descent and frozen launch/export/analysis remain required. Candidate slots, nonsingular normalized members and classes are separate counts.

Full derivation and primary-source boundaries: report.md. No canonical scientific graph edge changes. Archive TASK-20261102-fce0e3 preserves previous snapshots.
