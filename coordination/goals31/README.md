# Goals 31 — proposal record (2026-11-20)

**Status:** proposal only. Nothing here is registered in the campaign DAG and no
experiment may cite a G31 ID until the Coordinator activates it. No results, no
cost claims, no crypto-scale language.

**Parent goal:** GOAL-ECDLP-001.

## Provenance

This campaign answers a scouting audit of the goals30 portfolio (2026-11-20). The
audit's five claims were checked against the trunk checkout before any goal was
drafted. Two survived in substance, two were refuted, one was partly inverted;
the corrections are part of the record so the refuted lines are not re-proposed.

| # | Audit claim | Verdict | Evidence |
|---|---|---|---|
| 1 | Secant varieties: "zero hits", ingested but never used | **Gap real, statistics wrong.** One active secant *presentation* lead exists, and the secant-rank paper has a literature digest; no goal measures secant defectivity. | `knowledge/leads/ecdlp/ic-prime/LEAD-ICP-split-graph-secant-presentation.yaml`; `knowledge/literature/KN-LIT-1861.md` (no backlinks) |
| 2 | No characteristic-0 / Mordell–Weil supply work | **Confirmed.** Literature review has no height/lift/Mordell-Weil material; only incidental Hensel/Mordell mentions in findings. | `docs/ecdlp-literature-review-20260926.md` (0 hits); 9 `KN-FIND` files |
| 3 | Large-prime variation "cited once, never staffed" | **Refuted.** Three open leads, one of them prime-field and explicitly single/double large prime; two literature entries, one read at source. | `LEAD-ICP-residual-partial-relations.yaml`, `LEAD-ICB-large-prime-variants.yaml`, `LEAD-ICE-relation-graph-rank-large-prime.yaml`, `KN-LIT-92caf4` |
| 4 | Semaev summation polynomials never computed in odd characteristic | **Absent but inverted.** Patault–Plesis is genuinely missing from the corpus; odd-characteristic S₃ is the easy case (resultants), char 2 is the hard one. m=4 validation is a control fix, not a campaign. | 0 corpus hits; `coordination/goals30/drafts/cluster_09_harness_G30-025..027.md` gap #2 |
| 5 | Diem's non-existence results unstaffed | **Confirmed.** DLP I/II are digested one-sided (positive subexponentiality only); no Diem correspondence/cohomological entry. | `KN-LIT-003`, `KN-LIT-65f76d` |

The two staffed items are therefore G31-001 (geometric instrument for D2) and
G31-002 (characteristic-0 supply barrier). Items 3–5 are routed as deferrals in
`registry.yaml`, not as goals.

## Relation to goals30

- G31-001 is a *second instrument* for D2, complementary to the arithmetic
  monodromy line G30-007/008/009. It does not re-run or re-sort their panels and
  does not claim to supersede them.
- G31-002 is a *barrier derivation* on the lift/transfer side, complementary to
  the empirical closure of the correspondence engines (G30-013/015) and to the
  existing lift leads. It closes the supply half, not the relation half, of the
  `LEAD-TRF-global-lift-small-height` obstruction.
- Neither goal consumes G30-001's GOE ruler, because neither makes a rho-relative
  performance claim.

## Files

- `drafts/cluster_11_secant_G31-001.md` — G31-001
- `drafts/cluster_12_lift_G31-002.md` — G31-002
- `registry.yaml` — machine-readable index (mirrors the goals30 registry shape)
