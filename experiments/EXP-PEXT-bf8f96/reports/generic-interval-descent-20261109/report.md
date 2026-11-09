# Prospective generic interval descent certificate

**Scope:** Source-only design increment for H-PEXT-c3a11d and EXP-PEXT-bf8f96. The experiment remains `review_required` and `frozen: false`. No scientific cohort or benchmark ran.

## Mathematical construction

The draft contract's retrieved [square-class and descent source](https://eprint.iacr.org/2015/805.pdf), sections 3.1–3.3, and [Type-II branch slides](https://maths.ucd.ie/~gmg/ECC2007Talks/chao.pdf), slides 25–26, supply the prior descent context. This increment applies an elementary square-class argument to the already specified generic complement. For an odd-characteristic field of extension degree n in {3, 5, 7}, assume the coefficient Frobenius orbit is exact and the conjugate squarefree binary quartics have pairwise disjoint projective branch supports, including infinity. Every nonempty subset of the quartics then has an odd valuation at a branch point unique to one selected factor. Its product is not a square even over the algebraic closure. Coefficient square classes cannot introduce a relation. The radical extension has rank n and is geometrically connected; coefficient Frobenius with x fixed and y_i mapped to y_(i+1 mod n) has order n and gives base-field descent. Riemann–Hurwitz gives genus 1+(n−1)2^n.

The application is conditional on the candidate-set checker's exact collision-completeness claim, which still requires independent scientific review. It applies to the generic complement only. Exceptional rows retain separate unresolved descent/counterexample obligations, and C5 remains unresolved overall.

## Bound artifact and checks

The producer recomputes the exact exceptional set from an externally bound sealed unit, then emits a compact certificate for its entire generic complement. It binds cohort, class/T, field/model/target/form, input/manifest/join-plan digests, structure range, raw and canonical unit digests, exceptional ordinal and interval digests, counts, rank, action, and genus. A separate checker recomputes the certificate from the sealed bytes. The candidate review carries the compact hash/count summary; the geometric reducer validates that summary against its bound review and raw-unit identity. This avoids duplicating the full interval list in every review row.

The fixed F27 fixture has 819 structures: 279 exceptional, 540 generic across 109 intervals; rank 3 gives genus 17. Mutation checks reject changed interval or digest fields. The combined focused Python suite passed 25 tests. These are software fixture checks, not full-cohort observations.

## Remaining design work

Independent review of collision completeness, certified exceptional descent/counterexample metadata, final C5 blind custody, H1 q13, remaining controls, full-cohort CPU/RSS/storage qualification, final analysis/export/checker, lawful lane, Executor route, trial-plan/RUN allocation, runbook, preapproval packet, and freeze/approval remain open. The standing ceilings remain six runs, 4 GB, 24 CPU-hours, 24 hours, zero cloud dollars and no retries.
