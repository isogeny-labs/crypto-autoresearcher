# Harness mechanisms: retire or measure

Harness review I7 (2026-11-10). Each review added mechanisms and none was
retired; the bus, handoff returns, the challenge loop, the tuner and the eval
had no measurement of their own effect.

## Rule

Every mechanism is listed in `docs/harness-mechanisms.yaml` with an owner doc,
a `use_metric` (a shell command printing one number), `added_on` and
`review_by` (`added_on` + 30 days). Entries cover the bus, handoff returns, the
challenge loop, tune-skill, the autopilot, the weekly eval, session receipts,
the instruction-budget check, the pcc canary, the approval cap, and one entry
per `AGENTS.md` H2 section.

`python3 tools/mechanism_review.py` runs each metric (120 s limit; failure is
`unavailable`) and prints the number and days to review.
`python3 tools/mechanism_review.py --overdue` lists mechanisms past `review_by`
whose status is not `measured`, or whose metric is 0 or unavailable. For each,
**make it optional and move its text to `docs/`**; do not raise a budget to
keep it. The 30-day clock starts at registry entry, not at introduction.
A metric of use is not a metric of effect: AGENTS.md section entries count
citing files, so they stay `unmeasured` until someone measures an effect.

## Falsifier

Removal is safe only while discipline holds. If removing a mechanism coincides
with a regression in the discipline eval (`evals/`, harness review I5), restore
it and record the measured dependence in its registry entry. Until the eval
produces results (none exists today), a removal is provisional.

## Metrics for the programme

Always-loaded words back at or below 4,000 without raising the budget; bus
unread fraction; mechanisms with a measured effect over mechanisms total.
