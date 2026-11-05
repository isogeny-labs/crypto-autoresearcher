# Degree-two quotient construction and census design, 2026-11-02

The design now gives an explicit same-curve quartic quotient and separates branch genus from constant square relations and descent. Experiment EXP-PEXT-bf8f96, hypothesis H-PEXT-c3a11d, goal GOAL-PEXT-4a1d6b, IDEA-20261024-d84f20. This report records source review and prospective design; zero scientific trials ran.

The symbolic residual/discriminant/inverse/removable-point identities is a checked algebra component (root SymPy1.14.0 replay). Complete T quotients, projective exceptions, twisted curve identities, full structure coverage and descent certificates remain implementation work. Parameters are n=3/q=5,7,11 and n=5/q=3 full cohorts, with abstract n=7 placements. No measured counts or runtime estimates are invented.

Primary sources checked: Iijima-Momose-Chao2015/805 sections3.1-3.3, https://eprint.iacr.org/2015/805.pdf ; Chao ECC2007 slides25-26, https://maths.ucd.ie/~gmg/ECC2007Talks/chao.pdf . The first requires coefficient-aware descent; the second distinguishes Type2 signature from its hyperelliptic exception. These are retrieved source statements; P1-P4 remain unreviewed predictions.

The schematic shows pending interfaces, not established transfer edges. Full details and equations: ../../design-obligations.md. Readiness: review_required, unapproved; missing full launcher/checker/analysis, published hashes, exact trial plan/handoff/queue, lawful lane and permitted Executor route. Two PEXT lanes are open at cap2; no new live lane is created. Next: implement projective quotient and coefficient/square-class checks, then complete original cohorts and exact-byte preapproval.

Canonical graphs checked: knowledge/leads/ecdlp/transfer/LEAD-TRF-odd-prime-ghs-cover-floor.yaml and LEAD-TRF-small-genus-cover-general.yaml. Their scientific facts are unchanged: this round creates a design and component algebra check, not validated genus/descent measurements. Therefore no canonical verified edge is updated.


Scope clarification: P3 tests the original geometric genus minima. Descent-admissible minima are a separate descriptive output, never a strengthened P3 criterion. The original H1 configuration/curve-count ratio arm retains q=5,7,11,13, with q=13 separate from the P3 cohort. H1 equidistribution is not asserted or gated. Symbolic replay command: `/var/tmp/pext-design-report-venv/bin/python experiments/EXP-PEXT-bf8f96/implementation/degree2_identity.py`; four checks PASS, recorded in symbolic-check.json. The root is the producer; this is no independent scientific review.
