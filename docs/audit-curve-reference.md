# audit-curve reference

Binding detail moved verbatim from `.claude/skills/audit-curve/SKILL.md` on
2026-11-10 to keep that skill's wake within the 7,000-word budget
(`tools/check_instruction_budget.py`). The skill links each section; apply it
as if it were inline.

## Per-representative properties

(From step 2, "Separate class invariants from representative properties".)

Do not sample multiple representatives as independent support for these
facts. Properties worth checking per representative include rational group
decomposition, exact endomorphism order and conductor, rational torsion,
`j`-invariant, efficiently computable automorphisms or endomorphisms, model
and formula behavior, descent-friendly representation, and explicit path
cost. A small coefficient, special model, short isogeny, small discriminant,
or unusual `j`-invariant is only a lead until tied to an attack.

## Sampling frame

(From step 5, "Treat statistics as coverage evidence".)

Before sampling, freeze the population and distribution: uniform
`F_q`-isomorphism classes, the deployed curve generator, and a neighbor walk
are different populations. Deduplicate isomorphism classes rather than
equations or `j`-invariants alone. Record allowed edge degrees, component,
radius, conductor or volcano strata, stopping rule, revisits, and coverage.
Correct degree bias and autocorrelation with a justified mixing or
finite-population argument; an effective sample size is a diagnostic, not a
mixing proof. Confirm adaptive discoveries on fresh samples and account for
multiple testing.

## Prevalence bounds beyond i.i.d.

(From step 5, after the exact binomial interval.)

Stratified,
unequal-probability, or dependent samples require stratum- or design-aware
inference; use a hypergeometric bound for sampling without replacement from a
known finite population. None of these bounds proves absence, and a low
estimated prevalence does not protect against a parameter generator
deliberately selecting a rare representative.
