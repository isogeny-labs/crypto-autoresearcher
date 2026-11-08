# Source review and provenance

Reviewed by the current Codex session before prototype implementation.
Repository base: crypto-autoresearcher a0ca384c7a6984bcba83cf9ffa7f49f590e4612b.
The supplied PR #3095 text is the proposal source; no assertion is made that its
historical code paths, timing predictions, or prior-work audit were valid.

Internal sources at that base:

- src/crypto_autoresearcher/index_calculus/factor_base.py: actual small_x,
  subgroup, Dickson membership and parameterization; planted replaces points.
- src/crypto_autoresearcher/index_calculus/curve.py: point lift and sign convention.
- knowledge/leads/ecdlp/ic-prime/LEAD-ICP-coincidence-harvest-structured-base.yaml:
  identifies FAM-1 families and prior coincidence work. Historical measurements
  are not re-reviewed or reproduced by this change.
- experiments/EXP-PFDR-2d36f9/specification.yaml R2: FAM-1 means the subgroup,
  small_x and Dickson arms; that older checkout's missing implementation is not
  current absence. We recovered the current source from Git.
- knowledge/leads/ecdlp/ic-prime/LEAD-ICP-coppersmith-smallroot-semaev.yaml and
  research/joint_smallroot_reach_20261024/README.md: prior single-block versus
  joint-system scope and outstanding root extraction. The notes point to Ryan
  2025; that paper was not independently retrieved here, so its theorem is not
  used to establish a new bound in this report.
- knowledge/leads/ecdlp/structure/LEAD-STR-special-j-ic-semaev.yaml:
  earlier support-count and matched-order work; generic norm expansion and
  rational-lift validation are the present construction delta.
- knowledge/leads/ecdlp/ic-prime/LEAD-ICP-isogeny-transported-relation-yield.yaml:
  missing old panel arms stay missing; no continuation of their jobs is attempted.
- knowledge/leads/ecdlp/ic-prime/LEAD-ICP-digit-presentation-solving-degree.yaml:
  existing m=3 solver work and warnings against interpreting degree alone as cost.

Primary external sources (retrieved):

- Kosters and Yeo, *Notes on summation polynomials*, arXiv:1503.08001v3,
  https://arxiv.org/pdf/1503.08001, section 2 / Proposition 2.1. Used for the
  summation polynomial and its algebraic-closure point-sum semantics. Its binary
  first-fall discussion is not transferred into a prime-field degree theorem.
- SageMath isogeny reference,
  https://doc.sagemath.org/html/en/reference/arithmetic_curves/sage/schemes/elliptic_curves/ell_curve_isogeny.html.
  Used for explicit maps, duals and model-isomorphism handling. The prototype's
  formulas are also checked directly on finite fixtures; Sage was not installed.
- Semaev 2004/031 PDF retrieval returned HTTP 403. It remains a bibliographic
  pointer; the accessible Kosters-Yeo full text supplies the formula used here.

Retrieval limitation: no search_knowledge tool was exposed in this session.
Read-only Git source inspection was used; no corpus index was edited. This is a
scoped overlap audit, not a claim of exhaustive novelty or independent review of
prior experimental results.
