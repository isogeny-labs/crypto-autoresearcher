# n33 trace-zero D5 nonmembership is impossible

- **Status:** resolved
- **Kind:** proved mathematical obstruction, supported by independently reproduced exact finite computation
- **Affected work:** [frozen n33 D5 request](../analysis/semaev-degree-five-quotient-lift/runtime/n33-tr0-01-d5-local-request-001.json), [branch result](../analysis/semaev-degree-five-quotient-lift/reports/n33-branch-d4-screen-001/report.md)
- **Next action owner:** Semaev fall-degree research lane
- **Last updated:** 2026-11-03

## Problem

The frozen D5 request on `fresh-n33-tr0-01` cannot establish LFD at least six:
the constant already lies in the original system's degree-five closure. A
valid D5 nonmembership map for this exact Boolean presentation cannot have a
nonzero image of 1.

## Evidence and uncertainty

- **Observed:** Both `a0=0` and `a0=1` restricted inputs were refuted in W4
  by the native engine and by a separate full fixed-point implementation.
  Every complete run obtained dimensions `[1,34,562,6018,46938]` and found
  1. Independent descent matched the original and restricted polynomials
  exactly. All raw outputs and hashes are in the [result packet](../analysis/semaev-degree-five-quotient-lift/reports/n33-branch-d4-screen-001/evidence.json).
- **Derived or proved:** Lemma 1.3 of the theorem dossier gives `1 in W5`
  from the two W4 branches. The original D4 quotient certificate was freshly
  accepted by its independent checker with `1 not in W4` and codimension at
  least 4,888. The retained exact count is zero. Thus this named system has
  exact LFD 5 by Proposition 1.2.
- **Suspected explanation:** No conjecture is needed for this named result.
- **Missing capability:** A compact separately checkable W4 membership
  witness for each branch has not been exported; the upper bound is presently
  reproduced by two complete exact implementations.
- **What this evidence does not establish:** It does not classify any other
  n33 subspace, the n47–51 frontier, or asymptotic LFD growth.

## What would unblock the degree-six search

No further computation on the same n33 D5 request can make the constant absent
from W5. The successor must be a different named presentation whose D5
closure admits a nonzero dual image of 1, with independent checker acceptance
and the exact-count bridge.

- [ ] Use another fixed input, such as the accepted n50 polynomial03 D4 seed,
  and obtain an independently checked D5 map with nonzero image of 1.
- [ ] Check that its D5 codimension is strictly larger than the exact solution
  count, or prove unsatisfiability separately.

These conditions would establish a named LFD lower bound of six. A growing
bound still requires a family theorem or certificates over a justified range.

## Next discriminating step

- **Action or proof obligation:** Independently check the affine-sliced n50
  polynomial03 D4 seed, then freeze a new sliced D5 protocol. The existing
  unsliced protocol is not repurposed.
- **Inputs and controls:** Pin the published n50 D4 source hash, proved affine
  combination, independent descent source and checker, and fresh exact count.
- **Execution limits and stop condition:** Apply current host, memory,
  ownership and cloud-cost admission before any D5 producer; preserve failure
  or refusal as an explicit unknown.
- **Outcomes and next actions:** An accepted positive D5 map plus count bridge
  proves a named degree-six lower bound. A checked D5 refutation gives an upper
  bound; resource refusal leaves the question open for that input.
- **Recheck trigger:** A new D5 certificate or proved family argument.

## Resolution and history

Resolved for the named n33 request on 2026-11-03 by the [branch result](../analysis/semaev-degree-five-quotient-lift/reports/n33-branch-d4-screen-001/report.md).
The broader degree-six goal remains active. The frozen n33 D5 request is
preserved as history and must not be launched as a nonmembership search.
