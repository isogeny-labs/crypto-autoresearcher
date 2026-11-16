#!/usr/bin/env python3
"""Probe-or-nothing admission (review I1) and nearest-neighbour citation (I12).

A new ECC-area `IDEA-*` proposal carries a `probe:` block (a committed command
of at most 10 CPU-minutes, an evaluator emitting one number, a pre-stated
threshold, a scaled-down instance) and a `nearest:` block (the closest existing
IDEA or lead and a stated difference).  Source:
docs/autoresearcher-harness-review-20261110.md, section 4, I1 and I12.

Findings are advisories before PROBE_RULE_ENFORCED_AS_ERROR_FROM and errors
from that date, for proposals dated on/after PROBE_RULE_ENFORCED_FROM.

    python3 tools/check_probe_admission.py ledger/proposals/IDEA-....yaml
"""
from __future__ import annotations

import datetime as _dt
import glob
import math
import os
import re
import sys

import yaml

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import ecc_priority                                          # noqa: E402
import validate_ledger                                       # noqa: E402

# Proposals dated before this are exempt; from it, findings are advisories.
PROBE_RULE_ENFORCED_FROM = "2026-11-11"
# From this date the same findings are errors.
PROBE_RULE_ENFORCED_AS_ERROR_FROM = "2026-12-01"

PROBE_MAX_CPU_MINUTES = 10
NEAREST_MIN_DIFFERENCE_CHARS = 40
PROBE_DIRECTIONS = ("higher_is_better", "lower_is_better")
_IDEA_ID = re.compile(r"^IDEA-(\d{8})-")


def _date(value: str | None) -> _dt.date:
    if value is None:
        return _dt.date.today()
    return _dt.date.fromisoformat(str(value)) if "-" in str(value) \
        else _dt.datetime.strptime(str(value), "%Y%m%d").date()


def _is_number(x) -> bool:
    return (isinstance(x, (int, float)) and not isinstance(x, bool)
            and math.isfinite(x))


def _nonempty(x) -> bool:
    return isinstance(x, str) and bool(x.strip())


def _area(body: dict) -> str | None:
    area = body.get("area")
    if _nonempty(area):
        return str(area).strip()
    return ecc_priority.area_of(str(body.get("question_id") or ""))


def probe_problems(probe) -> list[str]:
    if not isinstance(probe, dict):
        return ["probe: block is missing (command, evaluator, metric, "
                "threshold, direction, cpu_minutes, instance)"]
    out = []
    for key in ("command", "metric", "instance"):
        if not _nonempty(probe.get(key)):
            out.append(f"probe.{key} must be a non-empty string")
    ev = probe.get("evaluator")
    if not _nonempty(ev):
        out.append("probe.evaluator must be the path of code that emits "
                   "exactly one number")
    elif not os.path.isfile(os.path.join(validate_ledger.REPO, ev.strip())):
        out.append(f"probe.evaluator '{ev}' is not a committed file")
    if not _is_number(probe.get("threshold")):
        out.append("probe.threshold must be a number")
    if probe.get("direction") not in PROBE_DIRECTIONS:
        out.append(f"probe.direction must be one of {list(PROBE_DIRECTIONS)}")
    cpu = probe.get("cpu_minutes")
    if not _is_number(cpu) or not 0 < cpu <= PROBE_MAX_CPU_MINUTES:
        out.append(f"probe.cpu_minutes must be a number in "
                   f"(0, {PROBE_MAX_CPU_MINUTES}]")
    return out


def _known_idea(ref: str, ctx) -> bool:
    if ref in ctx.ids:
        return True
    return bool(glob.glob(os.path.join(validate_ledger.REPO, "ledger",
                                       "proposals", ref + ".*")))


def nearest_problems(nearest, rec_id: str, ctx) -> list[str]:
    if not isinstance(nearest, dict):
        return ["nearest: block is missing (id of the closest IDEA or lead, "
                "and difference)"]
    out = []
    ref = nearest.get("id")
    if not _nonempty(ref):
        out.append("nearest.id must name an existing IDEA-* or LEAD-* id")
    else:
        ref = ref.strip()
        if ref == rec_id:
            out.append("nearest.id must be another record, not the idea itself")
        elif ref.startswith("IDEA-"):
            if not _known_idea(ref, ctx):
                out.append(f"nearest.id '{ref}' is not an existing idea")
        elif not validate_ledger._lead_exists(ref):
            out.append(f"nearest.id '{ref}' is neither an existing IDEA-* nor "
                       "a lead in knowledge/leads/ecdlp/")
    diff = nearest.get("difference")
    if (not isinstance(diff, str)
            or len(diff.strip()) < NEAREST_MIN_DIFFERENCE_CHARS):
        out.append(f"nearest.difference must state, in at least "
                   f"{NEAREST_MIN_DIFFERENCE_CHARS} characters, how this idea "
                   "differs from the nearest one")
    return out


def check_probe_admission(ctx, today: str | None = None) -> None:
    """I1 + I12 for new ECC-area proposals; advisory, then error."""
    now = _date(today)
    start = _dt.date.fromisoformat(PROBE_RULE_ENFORCED_FROM)
    hard = now >= _dt.date.fromisoformat(PROBE_RULE_ENFORCED_AS_ERROR_FROM)
    areas = ecc_priority.ecc_areas()
    for rec_id, kind in ctx.record_types.items():
        if kind != "idea":
            continue
        m = _IDEA_ID.match(rec_id)
        if not m:
            continue
        try:
            made = _dt.datetime.strptime(m.group(1), "%Y%m%d").date()
        except ValueError:
            continue
        body = ctx.records[rec_id]
        if made < start or _area(body) not in areas:
            continue
        path = ctx.ids[rec_id]
        problems = (probe_problems(body.get("probe"))
                    + nearest_problems(body.get("nearest"), rec_id, ctx))
        for msg in problems:
            full = (f"{msg} (ECC ideas from IDEA-"
                    f"{PROBE_RULE_ENFORCED_FROM.replace('-', '')} on; "
                    "docs/autoresearcher-harness-review-20261110.md I1/I12)")
            if hard:
                ctx.err(path, full)
            else:
                ctx.advise(path, f"{full}; error from "
                                 f"{PROBE_RULE_ENFORCED_AS_ERROR_FROM}")


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print(__doc__)
        return 2
    ctx = validate_ledger.Ctx(legacy_paths=set())
    for path in args:
        with open(path, encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)
        body = doc.get("idea", doc) if isinstance(doc, dict) else None
        if not isinstance(body, dict) or not body.get("id"):
            print(f"{path}: not an IDEA record (no id)", file=sys.stderr)
            return 2
        ctx.register(str(body["id"]), os.path.abspath(path), body, "idea")
    check_probe_admission(ctx)
    for line in ctx.advisories:
        print("ADVISORY:", line)
    for line in ctx.errors:
        print("ERROR:", line)
    if not ctx.errors and not ctx.advisories:
        print("probe admission: ok")
    # Exit status follows errors only; advisories are printed and become
    # errors on PROBE_RULE_ENFORCED_AS_ERROR_FROM, so fix them now.
    return 1 if ctx.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
