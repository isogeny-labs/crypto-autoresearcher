#!/usr/bin/env python3
"""Retire-or-measure review of harness mechanisms (harness review I7).

Reads `docs/harness-mechanisms.yaml`. Each mechanism carries a `use_metric`, a
shell command (run from the repository root) that prints one number. This tool
runs every metric (120 s timeout; a failure, timeout or non-numeric output is
recorded as `unavailable`), then prints the number and days to `review_by`.

`--overdue` lists mechanisms past `review_by` that show no measured use: status
is not `measured`, or the metric is 0 or unavailable. Retired mechanisms are
skipped. The listed action: make optional, move text to docs/.

Usage:
    python3 tools/mechanism_review.py [--json] [--overdue] [--today YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[1]
REGISTRY = REPO / "docs" / "harness-mechanisms.yaml"
TIMEOUT_S = 120
STATUSES = {"measured", "unmeasured", "retired"}
_NUM = re.compile(r"^-?\d+(?:\.\d+)?$")


def load_registry(path: Path = REGISTRY) -> list[dict[str, Any]]:
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return list(doc.get("mechanisms") or [])


def run_metric(cmd: str, cwd: Path = REPO, timeout: int = TIMEOUT_S) -> float | None:
    """The number the command prints (last non-empty stdout line), or None."""
    try:
        proc = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True,
                              text=True, timeout=timeout)
    except (subprocess.TimeoutExpired, OSError):
        return None
    if proc.returncode != 0:
        return None
    lines = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
    if not lines or not _NUM.match(lines[-1]):
        return None
    return float(lines[-1])


def _date(value: Any) -> dt.date:
    return value if isinstance(value, dt.date) else dt.date.fromisoformat(str(value))


def evaluate(mech: dict[str, Any], today: dt.date, value: float | None) -> dict[str, Any]:
    review_by = _date(mech["review_by"])
    status = str(mech.get("status", "unmeasured"))
    no_use = status != "measured" or value is None or value == 0
    days_left = (review_by - today).days
    return {
        "id": mech["id"],
        "name": mech.get("name", ""),
        "owner_doc": mech.get("owner_doc", ""),
        "status": status,
        "value": value if value is not None else "unavailable",
        "review_by": review_by.isoformat(),
        "days_to_review": days_left,
        "overdue": status != "retired" and days_left < 0 and no_use,
    }


def review(mechs: list[dict[str, Any]], today: dt.date,
           runner=run_metric) -> list[dict[str, Any]]:
    out = []
    for m in mechs:
        value = None if m.get("status") == "retired" else runner(str(m["use_metric"]))
        out.append(evaluate(m, today, value))
    return out


def render(rows: list[dict[str, Any]]) -> str:
    lines = [f"{'id':<56}{'status':<11}{'value':>12}  {'days':>5}  review_by"]
    for r in rows:
        v = r["value"]
        v = v if isinstance(v, str) else f"{v:g}"
        lines.append(f"{r['id']:<56}{r['status']:<11}{v:>12}  "
                     f"{r['days_to_review']:>5}  {r['review_by']}")
    return "\n".join(lines)


def render_overdue(rows: list[dict[str, Any]]) -> str:
    over = [r for r in rows if r["overdue"]]
    if not over:
        return "no mechanism is overdue without measured use"
    lines = [f"{len(over)} overdue with no measured use: make optional, "
             "move text to docs/"]
    lines += [f"  {r['id']}  ({r['owner_doc']}, review_by {r['review_by']}, "
              f"value {r['value']})" for r in over]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--overdue", action="store_true",
                    help="list mechanisms past review_by with no measured use")
    ap.add_argument("--today", type=dt.date.fromisoformat, default=None)
    ap.add_argument("--registry", type=Path, default=REGISTRY)
    args = ap.parse_args(argv)
    rows = review(load_registry(args.registry), args.today or dt.date.today())
    if args.overdue:
        rows_out = [r for r in rows if r["overdue"]]
        print(json.dumps(rows_out, indent=2) if args.json else render_overdue(rows))
    else:
        print(json.dumps(rows, indent=2) if args.json else render(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
