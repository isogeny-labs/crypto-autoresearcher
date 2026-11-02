# Degree-two quotient component implementation, 2026-11-02

The prospective quotient component now implements actual elliptic-curve points, the general odd-characteristic group law, a full in-memory E(K)/2E(K) coset partition with half-point witnesses, quotient quartic charts and coefficient-aware K(t) square relations. It extends the checked polynomial construction from the first snapshot. EXP-PEXT-bf8f96 / H-PEXT-c3a11d remain an unapproved review_required design; zero scientific census trials ran.

## Construction and source review

Source: ../../implementation/quotient_core.rs; symbolic predecessor: ../../implementation/degree2_identity.py. The module includes the existing EXP-PEXT-212d5c cover_census_n7.rs arithmetic at source SHA256 0336e5c594fc7f27d56a27ed957e281af7e9af9d0b15df4797a12bf8e86d5251 without invoking its main. The new Point type distinguishes infinity. General group arithmetic retains a2, including characteristic three. Quotient classes explicitly partition all enumerated rational points into translates R+2E(K), each member P carrying a half-point Q with P=R+2Q. These are in-memory construction witnesses; durable serialization and independent checking remain required.

The forward quotient chart treats O and T as distinct quartic infinity branches. For v!=0, -T uses the removable-point expression; v=0 follows the order-two pole branch. Inverse maps verify the quartic and original curve equations. Current small fixture checks exercise those paths; full prospective cohorts are not sampled or enumerated here.

## Static square-class review

The review read the implementation and its included arithmetic. For at most seven nonzero squarefree binary quartics, degree three or four, square_relations normalizes affine factors to monic support while retaining the original leading coefficient square class. Symmetric differences of root supports track factor parity; the explicit infinity bit tracks the degree-three branch. When support vanishes, the product is a square precisely when the product leading coefficient is square. A false scalar flag therefore denotes a nonsquare-constant geometric relation, rather than a K(t) square relation.

The function rejects zero forms, invalid encodings, repeated roots, projective degree below three and more than seven forms. The mask upper bound is 128 and source polynomial capacity32 covers the union of at most28 branch points. This supports the stated K(t) square-class interface; it does not certify Frobenius descent. No blocking source correctness defect was found within that interface. This static review is separate from independent scientific verification.

## Software checks and accounting

Actual commands, compiler version and output: software-tests.txt, recorded by the implementing root session. Final producer software check: rustc1.99.1; four unit tests pass, zero failures. Fixed F5/F3 curves exercise expected orders9/6/4/6 and quotient-class counts1/2/4/2, chart inverse/involution, scalar-twist distinction and invalid domains. Fixed embedded curves over F9 and F125 have expected12 and108 points from the Frobenius trace recurrence and check encoding, quotient coverage and chart inverses. These are software fixtures, not a parameter sweep or census.

Final source SHA256: 52cf914b453fdd6e069362a49e0063199400d5622e5cf7366d7456c3ee8c50f8. FieldIdentity exports prime, extension degree, reconstructed monic defining polynomial, primitive-element polynomial index and the entire log-to-polynomial encoding table. The reviewed reconstruction computes the polynomial-basis X^n relation; the extension fixtures verify its root identity and encoding permutation. The constructor restricts q to {3,5,7,11,13}, checks the allocation ceiling and bounds field size by u32::MAX/2, addressing the borrowed arithmetic overflow boundary. SquareClasses reports geometric/arithmetic ranks and a nonsquare-constant flag; the latter can increase arithmetic rank by one without changing geometric support rank.

No timing, census minimum, subgroup transfer or new experimental observation is claimed from these software checks. Root is the producer; this static source review and its algebra reasoning do not substitute for an independent census checker.

## Remaining implementation obligations

The full curve-class/structure enumerator, projective-transformed binary-form scalar bookkeeping, all-scope geometric rank/genus joins, descent/lift certificate, Type2 predicate, independent checker, deterministic checkpoint/export/analysis and frozen launcher/manifest/queue/handoff remain next work. Original geometric P3 cohorts and descriptive q13 H1 scope are preserved in the original specification. Existing old min_genus sentinel99 and m1 omission must not enter new all-map minima unchanged.

The inherited field encoding is logarithmic: raw2 is not constant2; use field.integer. inv(0) and pow(0,0) require guarded use. The implemented field size/characteristic guards must remain in place because source u32 arithmetic is not a promise of arbitrary-size support. The component is not the full experiment launcher.

## Sources, report and custody

Primary mathematics reviewed in the original source-bound design notes remains applicable: Iijima-Momose-Chao, ePrint2015/805 sections3.1-3.3, https://eprint.iacr.org/2015/805.pdf ; Chao ECC2007 slides25-26, https://maths.ucd.ie/~gmg/ECC2007Talks/chao.pdf . No additional novelty or scientific outcome follows from this source implementation review.

The diagram depicts implemented components and outstanding interfaces. Canonical lead graphs checked in the original report retain their scientific states: there are still no validated census/descent measurements to add. This fresh report and source are archived under TASK-20261102-697d80, preserving the first design archive and all prior hashes. The report is a component progress record, not an approval or a run receipt.
