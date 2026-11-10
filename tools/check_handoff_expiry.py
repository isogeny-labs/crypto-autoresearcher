#!/usr/bin/env python3
"""Orphan handoffs expire (harness review I8).

A dispatched `TASK-*` handoff with no `archived_by` after 14 days is an
*expired candidate* (advisory). `tools/expire_handoffs.py --apply` records
`status: expired` and `expired_on` on such records, write-once. A role with
more than 5 expired handoffs cannot be dispatched a newer one: the check turns
that into an error on the newer handoff, unless a DEC-* record lists the
expired ids under `clears_expired`.

`check_handoff_expiry(ctx, today=None)` uses the validate_ledger Ctx API
(`record_types`, `records`, `ids`, `advise`, `err`). Wire it in
`validate_ledger.main` next to `check_aged_handoffs(ctx)`:

    from check_handoff_expiry import check_handoff_expiry
    check_handoff_expiry(ctx)
"""
from __future__ import annotations

import datetime as dt
import re
from typing import Any, Iterable

EXPIRY_DAYS = 14
EXPIRED_ROLE_LIMIT = 5

_ID_DATE = re.compile(r"-(\d{8})-")


def id_date(rec_id: str) -> dt.date | None:
    m = _ID_DATE.search(str(rec_id or ""))
    if not m:
        return None
    try:
        return dt.datetime.strptime(m.group(1), "%Y%m%d").date()
    except ValueError:
        return None


def _today(today: Any) -> dt.date:
    if today is None:
        return dt.date.today()
    if isinstance(today, dt.date):
        return today
    s = str(today)
    return dt.datetime.strptime(s, "%Y%m%d" if len(s) == 8 else "%Y-%m-%d").date()


def role_of(body: dict) -> str:
    to = body.get("to") or body.get("role") or ""
    if isinstance(to, list):
        to = ",".join(str(x) for x in to)
    return str(to).strip().strip('"')


def is_expired(body: dict) -> bool:
    return str(body.get("status") or "") == "expired"


def is_expired_candidate(rec_id: str, body: dict, today: dt.date) -> bool:
    """Dispatched TASK-*, no archived_by, not yet expired, older than 14 days."""
    if not str(rec_id).startswith("TASK-") or body.get("archived_by") or is_expired(body):
        return False
    when = id_date(rec_id)
    return when is not None and (today - when).days > EXPIRY_DAYS


def cleared_ids(decisions: Iterable[dict]) -> set[str]:
    out: set[str] = set()
    for body in decisions:
        listed = body.get("clears_expired") if isinstance(body, dict) else None
        if isinstance(listed, list):
            out.update(str(x) for x in listed)
    return out


def _key(rec_id: str) -> tuple[str, str]:
    when = id_date(rec_id)
    return (when.isoformat() if when else "", str(rec_id))


def roles_over_limit(handoffs: dict[str, dict], cleared: set[str],
                     limit: int = EXPIRED_ROLE_LIMIT) -> dict[str, list[str]]:
    """role -> uncleared expired handoff ids, for roles with more than `limit`."""
    by_role: dict[str, list[str]] = {}
    for rec_id, body in handoffs.items():
        if is_expired(body) and rec_id not in cleared:
            by_role.setdefault(role_of(body), []).append(rec_id)
    return {r: sorted(ids, key=_key) for r, ids in by_role.items() if len(ids) > limit}


def check_handoff_expiry(ctx, today=None) -> None:
    now = _today(today)
    handoffs = {rid: ctx.records[rid] for rid, kind in ctx.record_types.items()
                if kind == "handoff" and isinstance(ctx.records[rid], dict)}
    for rec_id, body in handoffs.items():
        if is_expired_candidate(rec_id, body, now):
            age = (now - id_date(rec_id)).days
            ctx.advise(ctx.ids[rec_id],
                       f"expired candidate: dispatched {age} days ago with no "
                       "archived_by; run tools/expire_handoffs.py --apply or "
                       "record its return")
    decisions = [ctx.records[rid] for rid, kind in ctx.record_types.items()
                 if kind == "coordinator_decision"]
    over = roles_over_limit(handoffs, cleared_ids(decisions))
    for role, expired in over.items():
        newest = _key(expired[-1])
        for rec_id, body in handoffs.items():
            if (role_of(body) == role and not is_expired(body)
                    and _key(rec_id) > newest):
                ctx.err(ctx.ids[rec_id],
                        f"role '{role}' has {len(expired)} expired handoffs "
                        f"(limit {EXPIRED_ROLE_LIMIT}); a DEC-* record must "
                        "list them under clears_expired before a new handoff "
                        "is dispatched to it")
