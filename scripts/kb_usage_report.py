#!/usr/bin/env python3
"""Report research-kb adoption from the shared session logs.

The KB rule asks every research session to record a "Sources checked (KB)"
receipt: a `source_id` and a `repo:path`, or an explicit "KB unavailable".
This script counts those receipts over the dated session logs so adoption has
a number instead of an intention.

It reads only `docs/session-logs/*.md` in each root, ignores the template and
README, and never edits a log. It does not call the KB.

Usage:
    python3 scripts/kb_usage_report.py
    python3 scripts/kb_usage_report.py --since 2026-11-05
    python3 scripts/kb_usage_report.py --ref origin/main
    python3 scripts/kb_usage_report.py --root . --root ../crypto-autoresearcher
    python3 scripts/kb_usage_report.py --json --out docs/knowledge-base-usage-baseline.json

`--ref` reads the logs from a git ref, so a scheduled run or a measurement
taken while the working tree has uncommitted sessions still counts committed
history. Without it the working tree is read.

Exit status is 0 unless --fail-under is given and coverage is below it.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "kb-usage/v1"
DATE_RE = re.compile(r"(20\d{2}-\d{2}-\d{2})")
ID_RE = re.compile(r"\b(?:source|paper|lean):[0-9a-fA-F]{8,}\b")
QUERY_RE = re.compile(r"(?:query|queries)\s+[\"“]([^\"”]+)[\"”]", re.IGNORECASE)


def default_roots() -> list[Path]:
    here = Path(__file__).resolve().parents[1]
    workspace = here.parent
    candidates = [
        here,
        workspace / "crypto",
        workspace / "crypto-autoresearcher",
        workspace / "cryptanalysis",
        workspace / "crypto-lean",
    ]
    seen: set[Path] = set()
    out: list[Path] = []
    for path in candidates:
        path = path.resolve()
        if path in seen or not path.is_dir():
            continue
        seen.add(path)
        out.append(path)
    return out


def _git(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip()[:200] or "git failed")
    return proc.stdout


def log_paths(root: Path, ref: str | None = None) -> list[str]:
    """Session-log paths relative to root, from the working tree or a ref."""
    if ref:
        names = _git(root, "ls-tree", "-r", "--name-only", ref, "--", "docs/session-logs").splitlines()
    else:
        directory = root / "docs" / "session-logs"
        if not directory.is_dir():
            return []
        names = [str(p.relative_to(root)) for p in directory.glob("*.md")]
    return sorted(
        name
        for name in names
        if name.endswith(".md") and Path(name).name not in {"README.md", "TEMPLATE.md"}
    )


def read_log(root: Path, name: str, ref: str | None = None) -> str:
    if ref:
        return _git(root, "show", f"{ref}:{name}")
    return (root / name).read_text(encoding="utf-8", errors="replace")


def file_date(name: str) -> str | None:
    m = DATE_RE.fullmatch(Path(name).stem)
    return m.group(1) if m else None


HEADING_RE = re.compile(r"^(#{2,3})\s+(.*)$")
TIME_RE = re.compile(r"\b\d{1,2}:\d{2}\b")


def entries(path: Path) -> list[dict]:
    """Parse one log file from disk."""
    return parse_entries(path.read_text(encoding="utf-8", errors="replace"), path.name)


def parse_entries(text: str, name: str) -> list[dict]:
    """Entries are dated ## headings, or ### headings carrying a time.

    crypto-autoresearcher writes ``### 05:29 UTC — ...`` entries; other
    repositories write ``## 2026-... — ...``. Subheadings such as
    ``### What was done`` belong to the entry above and are not entries.
    """
    fallback_date = file_date(name)
    out: list[dict] = []
    current: dict | None = None
    for line in text.splitlines():
        match = HEADING_RE.match(line)
        is_entry = False
        date = fallback_date
        heading = ""
        if match:
            heading = match.group(2).strip()
            date_match = DATE_RE.search(heading)
            if date_match:
                date = date_match.group(1)
                is_entry = True
            elif match.group(1) == "###" and TIME_RE.search(heading):
                is_entry = True
        if is_entry:
            if current is not None:
                out.append(current)
            current = {"heading": heading, "date": date, "lines": [line]}
        elif current is not None:
            current["lines"].append(line)
    if current is not None:
        out.append(current)

    for entry in out:
        text = "\n".join(entry.pop("lines"))
        entry["receipt"] = bool(
            re.search(r"Sources checked\s*\(KB\)", text, re.IGNORECASE)
            or re.search(r"Sources checked\s*:[^\n]*\bKB\b", text, re.IGNORECASE)
        )
        entry["unavailable"] = bool(re.search(r"KB unavailable", text, re.IGNORECASE))
        # An explicit "KB unavailable" is a receipt too: the session recorded
        # that it tried and why it could not use the catalog.
        entry["receipt"] = entry["receipt"] or entry["unavailable"]
        entry["ids"] = sorted(set(ID_RE.findall(text)))
        entry["queries"] = sorted(set(QUERY_RE.findall(text)))
    return out


def audit_root(root: Path, since: str | None, ref: str | None = None) -> dict:
    files = log_paths(root, ref)
    rows: list[dict] = []
    for name in files:
        for entry in parse_entries(read_log(root, name, ref), name):
            if since and entry["date"] and entry["date"] < since:
                continue
            entry["file"] = name
            rows.append(entry)
    receipt_rows = [r for r in rows if r["receipt"]]
    ids = sorted({i for r in rows for i in r["ids"]})
    queries = sorted({q for r in rows for q in r["queries"]})
    by_date: dict[str, dict[str, int]] = {}
    for row in rows:
        key = row["date"] or "undated"
        bucket = by_date.setdefault(key, {"entries": 0, "receipts": 0})
        bucket["entries"] += 1
        bucket["receipts"] += int(row["receipt"])
    last = max((r["date"] for r in receipt_rows if r["date"]), default=None)
    return {
        "root": str(root),
        "name": root.name,
        "logs": len(files),
        "entries": len(rows),
        "receipts": len(receipt_rows),
        "coverage": (len(receipt_rows) / len(rows)) if rows else 0.0,
        "unavailable": sum(1 for r in rows if r["unavailable"]),
        "unique_source_ids": len(ids),
        "source_ids": ids,
        "queries": queries,
        "last_receipt": last,
        "by_date": dict(sorted(by_date.items())),
    }


def report(roots: list[Path], since: str | None, ref: str | None = None) -> dict:
    by_root = [audit_root(root, since, ref) for root in roots]
    entries_n = sum(r["entries"] for r in by_root)
    receipts_n = sum(r["receipts"] for r in by_root)
    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "since": since,
        "ref": ref,
        "roots": [str(r) for r in roots],
        "by_root": by_root,
        "totals": {
            "entries": entries_n,
            "receipts": receipts_n,
            "coverage": (receipts_n / entries_n) if entries_n else 0.0,
            "unavailable": sum(r["unavailable"] for r in by_root),
            "unique_source_ids": len({i for r in by_root for i in r["source_ids"]}),
        },
    }


def print_table(data: dict) -> None:
    print(
        f"{'root':28} {'logs':>4} {'entries':>7} {'receipts':>8} "
        f"{'coverage':>8} {'ids':>4} {'last receipt':>12}"
    )
    for row in data["by_root"]:
        print(
            f"{row['name']:28} {row['logs']:4d} {row['entries']:7d} "
            f"{row['receipts']:8d} {row['coverage']:7.1%} "
            f"{row['unique_source_ids']:4d} {str(row['last_receipt'] or '-'):>12}"
        )
    totals = data["totals"]
    print(
        f"{'TOTAL':28} {'':4} {totals['entries']:7d} {totals['receipts']:8d} "
        f"{totals['coverage']:7.1%} {totals['unique_source_ids']:4d}"
    )
    print(
        "Receipt = an entry carrying 'Sources checked (KB)' or an explicit "
        "'KB unavailable'; coverage = receipts / dated entries."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", action="append", type=Path, default=None, help="repository root (repeatable)")
    parser.add_argument("--since", default=None, help="include entries dated on/after YYYY-MM-DD")
    parser.add_argument("--ref", default=None, help="read docs/session-logs from this git ref instead of the working tree")
    parser.add_argument("--json", action="store_true", help="print JSON instead of a table")
    parser.add_argument("--out", type=Path, default=None, help="write JSON to this path")
    parser.add_argument("--fail-under", type=float, default=None, help="exit 1 below this coverage (0..1)")
    args = parser.parse_args(argv)

    roots = [p.resolve() for p in (args.root or default_roots()) if p.is_dir()]
    if not roots:
        print("kb_usage_report: no repository roots found", file=sys.stderr)
        return 2
    try:
        data = report(roots, args.since, args.ref)
    except RuntimeError as exc:
        print(f"kb_usage_report: {exc}", file=sys.stderr)
        return 2
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print_table(data)
    if args.fail_under is not None and data["totals"]["coverage"] < args.fail_under:
        print(
            f"kb_usage_report: coverage {data['totals']['coverage']:.1%} below "
            f"--fail-under {args.fail_under:.1%}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
