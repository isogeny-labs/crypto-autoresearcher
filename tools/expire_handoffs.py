#!/usr/bin/env python3
"""Mark orphan handoffs expired (harness review I8).

Dry run by default: lists dispatched `TASK-*` handoffs with no `archived_by`
older than 14 days (tools/check_handoff_expiry.py). `--apply` writes
`status: expired` and `expired_on: <date>` into each. Write-once: a record that
already has `expired_on` is never touched, and no record is deleted. A
pre-existing `status` is kept as `status_before_expiry`.

    python3 tools/expire_handoffs.py [--apply] [--today YYYY-MM-DD]
    python3 tools/expire_handoffs.py --role [ROLE]   # roles with >5 expired
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_handoff_expiry as che  # noqa: E402

REPO = Path(__file__).resolve().parents[1]


def _body(path: Path) -> dict | None:
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, yaml.YAMLError):
        return None
    body = doc.get("handoff") if isinstance(doc, dict) else None
    return body if isinstance(body, dict) else None


def scan(root: Path) -> dict[Path, dict]:
    out = {}
    for p in sorted((root / "ledger" / "handoffs").glob("TASK-*.yaml")):
        body = _body(p)
        if body is not None:
            out[p] = body
    return out


def mark_expired(path: Path, today: dt.date) -> bool:
    """Write status/expired_on into one record. False when already expired."""
    text = path.read_text(encoding="utf-8")
    if re.search(r"^  expired_on:", text, re.M):
        return False
    status = re.search(r"^  status:[ \t]*(.*)$", text, re.M)
    add = f"  expired_on: '{today.isoformat()}'\n"
    if status:
        old = status.group(1).strip()
        if old == "expired":
            return False
        text = (text[:status.start()] + "  status: expired\n"
                + (f"  status_before_expiry: {old}\n" if old else "")
                + add + text[status.end() + 1:])
    else:
        text = text if text.endswith("\n") else text + "\n"
        text += "  status: expired\n" + add
    path.write_text(text, encoding="utf-8")
    return True


def role_report(handoffs: dict[Path, dict], decisions: list[dict],
                role: str | None) -> dict[str, list[str]]:
    by_id = {str(b.get("id") or p.stem): b for p, b in handoffs.items()}
    over = che.roles_over_limit(by_id, che.cleared_ids(decisions))
    return {r: ids for r, ids in over.items() if role in (None, r)}


def _decisions(root: Path) -> list[dict]:
    out = []
    for p in sorted((root / "ledger" / "decisions").glob("DEC-*.yaml")):
        try:
            doc = yaml.safe_load(p.read_text(encoding="utf-8"))
        except (OSError, ValueError, yaml.YAMLError):
            continue
        body = doc.get("coordinator_decision") if isinstance(doc, dict) else None
        if isinstance(body, dict) and "clears_expired" in body:
            out.append(body)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--role", nargs="?", const="", default=None,
                    help="report roles with more than 5 expired handoffs "
                         "(optionally only ROLE)")
    ap.add_argument("--today", type=dt.date.fromisoformat, default=None)
    ap.add_argument("--repo-root", type=Path, default=REPO)
    args = ap.parse_args(argv)
    today = args.today or dt.date.today()
    handoffs = scan(args.repo_root)
    if args.role is not None:
        over = role_report(handoffs, _decisions(args.repo_root), args.role or None)
        if not over:
            print("no role has more than "
                  f"{che.EXPIRED_ROLE_LIMIT} uncleared expired handoffs")
        for r, ids in sorted(over.items()):
            print(f"{r}: {len(ids)} expired (> {che.EXPIRED_ROLE_LIMIT}); "
                  "new dispatch blocked until a DEC-* lists clears_expired")
        return 0
    cands = [p for p, b in handoffs.items()
             if che.is_expired_candidate(str(b.get("id") or p.stem), b, today)]
    per_role = collections.Counter(che.role_of(handoffs[p]) for p in cands)
    done = 0
    for p in cands:
        if args.apply and mark_expired(p, today):
            done += 1
    verb = "expired" if args.apply else "would expire"
    print(f"{verb} {done if args.apply else len(cands)} handoff(s) "
          f"(dispatched > {che.EXPIRY_DAYS} days, no archived_by)")
    for r, n in per_role.most_common():
        print(f"  {r or '(none)'}: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
