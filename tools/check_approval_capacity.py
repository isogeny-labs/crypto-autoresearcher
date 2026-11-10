#!/usr/bin/env python3
"""Per-area approval capacity: approval is bounded by execution (harness review I2).

Reinstates, per AREA rather than per goal, the P0.1 gate that commit
304547eb2c removed from tools/validate_ledger.py on 2026-10-11. The cap is
one field of the research-priority policy, `approved_unrun_cap_per_area`
(orchestration/research-priority.yaml), read through
portfolio_kpis.approved_unrun_cap(); `tools/portfolio_kpis.py --capacity
area:AREA` reports headroom against the same value. Rule, dates, metric and
falsifier: docs/execution-capacity-cap.md.

The rule. An approve-kind coordinator_decision that leaves an area (the
`EXP-<AREA>-` token) holding more than the cap of approved contracts with no
run must name, under `supersedes:` (a string or a list; the legacy keys
`supersedes_experiments` and `withdraws_experiments` are also read), one
RETIRED contract of the same area per newly approved one. Retired means the
named experiment is no longer approved-unrun (superseded, withdrawn, or it
has run) or another specification lists it under `supersedes`.

Which contracts count against a decision: the area's approved-unrun backlog
(portfolio_kpis definition) minus the decision's own targets, minus retired
ids it names, minus contracts approved by a LATER decision (ordered by id
date, then decided_at, then id), so a decision that was lawful when made is
not failed by approvals that came after it. Contracts whose `approved_by` is
not a decision id are legacy and always count.

Dates. Decisions dated (id date) from ADVISORY_FROM to the day before
ENFORCED_FROM go to ctx.advise (never fail the build); from ENFORCED_FROM
on they are ctx.err. Wiring, in validate_ledger.main():

    from check_approval_capacity import check_approval_capacity; check_approval_capacity(ctx)

This module only reads Ctx (`record_types`, `records`, `ids`, `err`,
`advise`); it does not import validate_ledger.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
import portfolio_kpis  # noqa: E402  (one definition of "approved" and "unrun")

# The original P0.1 enforcement date: the cap's absence since 2026-10-11 stays
# visible as advisories rather than being re-litigated as errors.
ADVISORY_FROM = "20261007"
# Owner's "fix it all" instruction 2026-11-10; errors from the next UTC day.
ENFORCED_FROM = "20261111"
APPROVE_DECISIONS = {"approve", "approved", "approve_protocol",
                     "approve_experiment", "approval"}
RELEASE_KEYS = ("supersedes", "supersedes_experiments", "withdraws_experiments")
_ID_DATE = re.compile(r"-(\d{8})-")
_EXP_ID = re.compile(r"EXP-[A-Za-z0-9]+-(?:[0-9a-fA-F]{6}|\d{3,6})")


def _id_date(rec_id: str) -> str | None:
    match = _ID_DATE.search(str(rec_id or ""))
    return match.group(1) if match else None


def _ids(raw: Any) -> set[str]:
    if isinstance(raw, str):
        return set(_EXP_ID.findall(raw))
    if isinstance(raw, list):
        found: set[str] = set()
        for item in raw:
            found |= _ids(item.get("id") if isinstance(item, dict) else item)
        return found
    return set()


def _order(dec_id: str, body: dict) -> tuple[str, str, str]:
    return (_id_date(dec_id) or "", str(body.get("decided_at") or body.get("recorded_at") or ""),
            dec_id)


def _has_runs(exp_id: str, ctx) -> bool:
    path = ctx.ids.get(exp_id)
    return bool(path) and portfolio_kpis.runs_present(Path(os.path.dirname(path)))


def check_approval_capacity(ctx, *, policy_file: Path | None = None) -> None:
    """Refuse (advise before ENFORCED_FROM) approvals that push an area over the cap."""
    cap = portfolio_kpis.approved_unrun_cap(policy_file or portfolio_kpis.POLICY_FILE)
    if cap is None:
        return
    experiments = {i: ctx.records[i] for i, kind in ctx.record_types.items()
                   if kind == "experiment"}
    backlog: dict[str, set[str]] = {}
    superseded_by_spec: set[str] = set()
    for exp_id, body in experiments.items():
        superseded_by_spec |= _ids(body.get("supersedes"))
        if body.get("status") == "approved" and not _has_runs(exp_id, ctx):
            backlog.setdefault(portfolio_kpis.area_of(exp_id), set()).add(exp_id)
    unrun = set().union(*backlog.values()) if backlog else set()
    decisions = {i: ctx.records[i] for i, kind in ctx.record_types.items()
                 if kind == "coordinator_decision"}

    for dec_id in sorted(decisions, key=lambda d: _order(d, decisions[d])):
        when = _id_date(dec_id)
        body = decisions[dec_id]
        if when is None or when < ADVISORY_FROM:
            continue
        if str(body.get("decision") or "").strip().lower() not in APPROVE_DECISIONS:
            continue
        mine = _order(dec_id, body)
        named: set[str] = set()
        for key in RELEASE_KEYS:
            named |= _ids(body.get(key))
        retired = {e for e in named if e in experiments
                   and (e not in unrun or e in superseded_by_spec)}
        targets = _ids(body.get("target_ids"))
        # A target that already ran is a continuation, not a new approval
        # (user ruling 2026-10-09, DEC-20261009-ff58fe).
        new = {e for e in unrun if e in targets or experiments[e].get("approved_by") == dec_id}
        report = ctx.advise if when < ENFORCED_FROM else ctx.err
        for area in sorted({portfolio_kpis.area_of(e) for e in new}):
            new_here = {e for e in new if portfolio_kpis.area_of(e) == area}

            def earlier(exp_id: str) -> bool:
                by = str(experiments[exp_id].get("approved_by") or "")
                return by not in decisions or _order(by, decisions[by]) < mine

            standing = {e for e in backlog.get(area, set()) - new_here - retired if earlier(e)}
            if len(standing) + len(new_here) <= cap:
                continue
            swaps = {e for e in retired if portfolio_kpis.area_of(e) == area}
            if len(swaps) >= len(new_here):
                continue
            report(ctx.ids[dec_id],
                   f"approval capacity: {area} would hold {len(standing) + len(new_here)} "
                   f"approved contract(s) with no run (cap {cap}, "
                   f"orchestration/research-priority.yaml approved_unrun_cap_per_area); "
                   f"approving {', '.join(sorted(new_here))} needs {len(new_here)} retired "
                   f"{area} contract id(s) under supersedes: (named {len(swaps)}); "
                   "run or supersede one first (docs/execution-capacity-cap.md)")
