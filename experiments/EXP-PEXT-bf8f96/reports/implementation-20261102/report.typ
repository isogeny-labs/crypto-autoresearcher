#set page(paper: "a4", margin: 16mm)
#set text(size: 10pt)
= Degree-two quotient component implementation
2026-11-02 | EXP-PEXT-bf8f96 | H-PEXT-c3a11d

The prospective module now implements actual curve points, a group law retaining a2, complete in-memory E(K)/2E(K) coset witnesses, quotient charts and leading-scalar square-class relations. The experiment remains review_required and unapproved; zero scientific census trials ran.

#image("construction.svg", width: 100%)

*Static review:* for up to seven squarefree binary quartics, support parity and the original leading-coefficient square class determine every K(t) square relation, including degree-three infinity branches. Nonsquare-constant relations remain explicitly distinct. The implementation does not certify Fq descent. No blocking source defect was identified within this interface; independent scientific checking remains required.

*Software checks:* software-tests.txt records rustc 1.99.1, source hash, commands and four passing tests, zero failures. Fixed F5/F3 fixtures have expected orders9/6/4/6 and quotient counts1/2/4/2. Fixed F9/F125 embedded curves check expected12/108 points from the Frobenius recurrence, field identity/encoding, coset coverage and chart inverses. These are software fixtures, not census/minimum observations.

*Identity and guards:* FieldIdentity exports the monic field polynomial, primitive polynomial index and log-to-polynomial table. SquareClasses separates geometric/arithmetic rank and nonsquare constants. Declared prime and allocation/arithmetic guards preserve the borrowed field domain.

*Next:* complete all-cohort and projective-structure coverage, scalar/descent/lift certificates, independent checker, checkpoint/export/analysis and the frozen runnable packet. Retain original P3 and q13 descriptive scope. Component source: quotient_core.rs; archive TASK-20261102-697d80 preserves the first snapshot.

*Sources:* #link("https://eprint.iacr.org/2015/805.pdf")[Iijima-Momose-Chao2015/805 sections3.1-3.3]; #link("https://maths.ucd.ie/~gmg/ECC2007Talks/chao.pdf")[Chao ECC2007 slides25-26]. Full review detail and source boundaries: report.md. No canonical scientific graph edge changes because this round implements a component rather than producing validated census/descent data.
