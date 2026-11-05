# A growing fixed-degree Semaev lower bound needs a uniform separator

- **Status:** `open`
- **Kind:** mathematical proof gap; not an impossibility or resource result
- **Affected work:** [four-track request and proof note](../analysis/boolean-fall-certificates-20261104/THEORY.md), RQ-DREG-bd6c86, prime digit and binary descent lanes
- **Next action owner:** formal/theory continuation of the current owner request
- **Last updated:** 2026-11-04

## Problem

We cannot yet prove unbounded last fall for the fixed-degree Boolean/digit
presentations because no separator construction has been established for
arbitrarily growing parameters with full kernel closure.

The binary target is the exact normalized S3 subspace descent with explicit
Boolean equations (or a separately specified chained encoding). The prime
target is the F_p-coefficient Boolean-digit S3 presentation with explicit bit
equations, not a carry circuit or the degree-B membership polynomial model.
The arity, input normalization, target admissibility, subspace/digit maps,
auxiliary blocks and field must be fixed in the family statement. Point/group
interpretation is a separate obligation when the coordinate constraints omit
rational-lift or sign restrictions.

## Evidence and uncertainty

- Observed software checks: the [new finite checker](../analysis/boolean-fall-certificates-20261104/certificate.py)
  tests both inclusions and produces explicit SAT missing-consequence
  witnesses; its N<=12 ceiling is a disclosed instrument boundary.
- Written argument: a uniform family of closed separating kernels at caps
  D tending to infinity, paired with UNSAT or an actual missing ideal
  consequence, would give the requested family lower bounds.
- Missing proof: a parameter-uniform formula for those kernels, or a
  degree-controlled reduction to these particular Semaev systems.
- The one-pass shortcut fails a deterministic quadratic software control:
  products of newly fallen combinations can escape the initial span.
  Hilbert-series or raw-row counts alone do not discharge closure.
- This is not evidence that a growing bound is false. The measured prime
  width law and binary finite ladder do not settle it either way.

## What would unblock it

- [ ] State an exact deterministic family or probability distribution and
  which parameters grow, preserving the production generators and degree.
- [ ] For arbitrarily increasing caps D, construct pi_D that kills every
  eligible input and whose low-degree kernel is closed under all variables.
- [ ] Prove pi_D(1) is nonzero with independent UNSAT, or exhibit an ideal
  consequence g_D separated by pi_D for SAT systems. Check source-to-model
  and degree bookkeeping in the polynomial/Boolean bridge.

These are sufficient conditions for family lower bounds, not requirements
that every other possible proof must use this route. Finite certificates and
formalizing a conditional composition lemma alone do not meet them.

## Next discriminating proof step

Derive candidate kernels after quotienting the known trace/degree-three
falls, then test the symbolic variable-closure identity. Begin with the
unchanged finite controls and degree-compatible elimination. If closure fails,
retain the escaping product and revise the candidate space; if it holds only
for finitely many parameters, retain the finite lower bound and do not infer
growth. A successful uniform construction proceeds to independent semantic
review under the existing claim-tier rules. No new trial or spending is
scheduled by this record.

## History

2026-11-04: Opened while delivering the two-sided certificate and scoped
formalization tranche. The original request remains unresolved at this
mathematical obligation; no goal or hypothesis status was changed.
