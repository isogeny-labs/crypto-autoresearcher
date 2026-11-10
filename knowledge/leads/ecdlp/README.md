# ECDLP lead atlas

**What this program has already tried against the elliptic-curve discrete log,
one mechanism family per file, across all four repositories. It is written so
that a fresh clone answers "has this been done?" by computation, not by
re-reading 280,000 files.**

The known-results map (`knowledge/frontiers/ecdlp/`) records what the
*literature* established. This atlas records what *we* did: each lead's
disposition, the obstruction that closed it or the next step that would decide
it, and the evidence in `crypto-autoresearcher`, `crypto`, `cryptanalysis` and
`ecc-challenges`.

```sh
python3 tools/lead_atlas.py --brief          # what the session-start hook prints
python3 tools/lead_atlas.py --match "idea"   # leads and KR rows an idea collides with
python3 tools/lead_atlas.py --delta          # watched paths changed since the last review
python3 tools/lead_atlas.py --coverage       # ECDLP ledger records with no lead
python3 tools/lead_atlas.py --pursuit        # every lead not disproven in scope
python3 tools/lead_atlas.py --tiers          # evidence-tier counts per family, leads at tier >= 2
python3 tools/lead_atlas.py --check          # CI (make check-ledger)
python3 tools/lead_atlas.py --render --out knowledge/leads/ecdlp/ATLAS.md
python3 tools/lead_atlas.py --stamp <session> # close a review: pin every repo's HEAD
```

## Why it exists

At the first 2026-10-24 review the ledger held 2,049 ECDLP-area hypotheses and ideas. 971 of its
1,031 hypotheses (94%) had no terminal status. Every new session re-surveyed the same ground, and idea generation
re-proposed mechanisms that an earlier lane had already measured or closed. The
known-results map stops re-derivation of *published* results. Nothing stopped
re-derivation of *our own*.

The later 2026-10-24 coverage reconciliation maps 2,078 current records. Its
29 new mappings and two open transfer leads are recorded in
`docs/reports/ecdlp-lead-atlas-20261024/coverage-20261024-mapping-review.json`.
`REVIEW_STATE.json` still identifies the earlier four-repository review; coverage
alone does not certify a fresh review of every changed sibling path.

## What "already done" means

`REVIEW_STATE.json` pins the commit of each repository at the last completed
review. `--delta` lists the watched paths (ledger records, ideas, findings,
problem records, research notes, leaderboards) added or modified since those
commits. The session-start brief combines that with the tallies:

- **nothing new since review**: every lead and every idea in the four
  repositories has been examined. The work is the open leads' `next_action`s,
  or a genuinely new lead that `--match` does not find.
- **changed since review**: fold the listed paths into leads (skill
  `lead-atlas`), then `--stamp`.

The atlas is **saturated** when three gates hold together: no lead is
`open_unexamined`, every ECDLP ledger record maps to a lead in `coverage.tsv`,
and nothing has changed since the review. Saturation is a reporting state. It
pauses no goal (AGENTS.md "Goals are never paused"), and open next steps remain
work.

### Pursuit invariant

Only `closed_obstructed` removes a lead from the pursuit queue, and only for
the mechanism and assumptions its obstruction actually covers. The atlas
renders every other disposition in `--pursuit` and in the generated report's
Pursuit queue:

- `closed_known` remains pursued when a new implementation, parameter regime,
  or improvement beyond the reproduced known result becomes available;
- `closed_dominated` remains pursued at the condition that could remove the
  stated dominance;
- `exhausted_at_scale` remains pursued at its explicit scale or capability
  trigger; and
- all `open_*` rows remain pursued directly, including blocked and unexamined
  work.

A timeout, bounded null, resource limit, missing implementation, or dominance
on finite toy rows is not a disproof. If a `closed_obstructed` row is later
found to cover only one submechanism, reopen or split the uncovered mechanism;
do not let the broad title inherit a narrow obstruction. This scheduling view
changes no hypothesis, experiment, or goal status.

## Layout

```text
knowledge/leads/ecdlp/
  README.md               this file
  REVIEW_STATE.json       commits examined, date, reviewer, tallies (--stamp writes it)
  coverage.tsv            <ledger record id> TAB <lead id | NONE>, every ECDLP H-* and IDEA-*
  ATLAS.md                GENERATED (gitignored): --render
  <family>/LEAD-<FAM>-<slug>.yaml
```

Families: `generic` (RHO), `ic-binary` (ICB), `ic-engine` (ICE), `ic-prime`
(ICP), `transfer` (TRF), `structure` (STR), `exotic` (EXO).

## Row schema

```yaml
id: LEAD-ICB-frobenius-invariant-factor-base
family: ic-binary
title: one line
mechanism: what it does and why it could help
disposition: open_next_step   # see below
obstruction:                  # required for closed_* and exhausted_at_scale
  kind: measured              # theorem | proof | measured | literature | cost_model
  statement: the precise reason, with scope
  revisit_when: the condition that reopens it
next_action:                  # required for open_*
  step: the concrete next experiment or proof obligation
  from_revisit_when: false    # true reuses obstruction.revisit_when after a scoped reopening
  discriminates: what each outcome decides
  blocked_by: problems/x.md   # open_blocked only
best_measured: "S_IC/S_rho = 5.23x at log2 r = 36.6 (Table A)"   # or null
evidence:                     # >= 1; paths are checked
  - {repo: crypto, path: docs/ic/LEADERBOARD.md, note: one line}
ledger_refs: [H-FROB-..., DEC-..., EV-...]   # must exist under ledger/
known_results: [KR-IC-...]                   # must exist in the known-results map
related: [LEAD-...]                          # optional
dominated_by: LEAD-...                       # closed_dominated only
forecloses: [>= 3 phrases an idea would use when re-proposing this]
areas: [FROB, QSP]
tier: 0                       # 0-3, see "Evidence tiers"; absent reads as 0 (untiered)
tier_evidence:                # required when tier >= 1: path or pcc id for the tier reached
  2: crypto:benchmarks/<dir>/VALIDATION.json
last_reviewed: 2026-10-24
oracle_class: algebraic       # required for ic-prime and ic-binary; see Oracle class
oracle_class_note: one line of justification   # optional
```

Dispositions:

| disposition | meaning |
|:--|:--|
| `closed_obstructed` | a named theorem, proof or controlled measured scaling shows it cannot beat the matched baseline in scope |
| `closed_known` | a literature result (KR or KN-LIT) the program reproduced; nothing new in scope |
| `closed_dominated` | works, but another lead (`dominated_by`) strictly dominates it |
| `exhausted_at_scale` | measured across the reachable range with controls, no improvement, no named mechanism left; `revisit_when` names the scale that reopens it |
| `open_next_step` | a concrete, runnable, discriminating next step exists |
| `open_blocked` | the next step is known but blocked (`blocked_by`) |
| `open_unexamined` | ideas exist; no experiment or evidence has touched it |

## Oracle class

Owner ruling R1 (crypto `research/prime_ic_program_20261029/DECISIONS.md`,
AGENTS.md "Tracks of index calculus") splits index calculus into a generic
track and an algebraic track. The optional field `oracle_class` records which
oracle produces a lead's relations. It is required for families `ic-prime`
and `ic-binary` and optional elsewhere; `--check` rejects a value outside the
list and a missing value in those two families. `oracle_class_note` is one line
of justification.

| value | meaning |
|:--|:--|
| `generic` | decomposition by enumeration, subtraction, table lookup, meet-in-the-middle, k-sum, residual or coincidence collection; it runs identically on a random base |
| `algebraic` | the solver is given the factor-base membership constraint inside the system (PKM tower, digit presentation, Weil descent, summation-polynomial Groebner, Coppersmith small roots, SAT with membership encoded) |
| `structural` | exploits curve structure: isogeny, CM, automorphism, torsion, special j |
| `transfer` | moves the problem: covers, extension fields, pairings, lifts |
| `engineering` | constant-factor implementation of an otherwise classified method |
| `not_applicable` | none of the above: audits, references, accounting |

A lead that mixes classes is classified by the oracle that produces its
relations. A generic oracle is bounded by sqrt(r) (Shoup; Corrigan-Gibbs and
Kogan), so it can never beat rho.

**Rule: a generic-oracle lead never carries a vs_rho exponent claim; its
improvements are constants on the generic track.** Such a lead may stay open and
report measured constants and its distance to the matched rho, but not an
exponent below rho. `python3 tools/lead_atlas.py --genericity` lists every
generic-oracle lead (open ones first) with its best measured result and next
action, and `--brief` reports the count.
## Evidence tiers

Promotion is by tier, not by wording. `disposition` stays narrative; `tier`
says how far the lead's evidence has climbed (harness review 2026-11-10, I10):

| tier | meaning |
|:--|:--|
| 0 | proposed or prose only (no `tier` field reads as 0 and is flagged `untiered`) |
| 1 | toy exact count or Stage-0 check on a small instance, with a committed command |
| 2 | scaled instance with a matched rho reference and the section 5a GAE band: an ecbench or autolab record with a replay certificate |
| 3 | index-calculus leaderboard row with `VALIDATION.json` (crypto `docs/ic/LEADERBOARD.md`) |

`tier_evidence` maps the tier reached to a path or pcc claim id (a lower tier is
implied by a higher one and needs no entry of its own). `--check` fails an
invalid tier or a tier >= 1 with no evidence for it, and advises (does not
fail) a lead whose `status` or `best_measured` wording claims measured progress
(`measured`, `confirmed`, `advanced`, `promoted`) at tier < 2. Rows cited
only from pre-gate leaderboard tables or same-host, native-unpriced ecbench
sessions are not tiered up: they lack the matched rho and band, or the
validation record.

### Metric baseline (2026-11-10)

Leads with a tier-2 record / leads proposed = 2 / 176 (1.1%), at tiers
0: 174, 1: 0, 2: 2, 3: 0 (`--tiers`). The two are ICB-large-prime-variants
and ICP-prime-ic-constant-engineering, whose VALIDATION.json files exist in
crypto. ICB-learned-cost-model-factor-base-selection and
ICP-residual-partial-relations cite VALIDATION.json paths that resolve in no
checkout and stay at tier 0 until they do. Tier 1 is empty because no lead yet
carries a verified committed Stage-0 command; it is a backfill gap, not a
finding.

Falsification test (does tier-2 predict leaderboard rows better than status?):
at each later review, take the leads that gained a validated leaderboard row
(or `VALIDATION.json`-gated improvement) since the previous stamp. For each
lead, record the tier and the `disposition` it held at the previous stamp.
Compare the precision of "tier 2 at the earlier stamp" against "disposition
`open_next_step`" as predictors of gaining a row, on the same leads, with a
paired bootstrap over leads. The tier ladder is falsified if its precision is
not above the disposition's after three reviews, or if tier-2 leads gain rows
no more often than tier-0 leads.

## Rules

1. **A closure names its obstruction** (AGENTS.md "Research direction":
   premature closure fails like overclaiming). A null or timed-out search is
   not an obstruction; use `exhausted_at_scale` with the scale reached, or an
   open disposition.
2. **The atlas changes no research state.** A disposition cites the decision,
   evidence or known-result row that decided it; hypothesis, experiment and goal
   statuses move only by Coordinator decision records.
3. **Rows are curated and editable.** A review updates `disposition`,
   `next_action`, `evidence` and `last_reviewed` in place; git keeps the history.
   Never delete a lead: a lead absorbed into another becomes `closed_dominated`
   or names the successor in `related`.
4. **Every ECDLP idea names its lead.** From IDEA-20261025-* on, an idea whose
   `prior_art.frontier_map` is an ECDLP map carries `prior_art.lead`: a LEAD id
   it advances, or `new` with `new_lead_reason` saying why `--match` found
   nothing (`tools/validate_ledger.py`). A new lead is added to the atlas in the
   same PR as the idea.
5. **Gaps to rho are distance remaining**, never pass or fail (AGENTS.md "Every
   improvement is a success"). Superseded leaderboard wins are not results.
