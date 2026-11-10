#!/usr/bin/env python3
"""Harness-change gate: no loosening of the harness without a fresh eval baseline.

Proposal I5 of docs/autoresearcher-harness-review-20261110.md. A pull request
that does any of the following

  * edits a budget constant in tools/check_instruction_budget.py,
  * touches coordination/skill-tuning/**,
  * adds a new docs/*loop*.md,

must find a committed `evals/baselines/<YYYY-MM-DD>/summary.json` no older than
30 days. The baseline is a discipline-eval record (Wilson intervals), so a
harness change is judged against a measured level and not against the change's
own author. Evidence about the harness, not about ECDLP (evals/README.md).

    python3 tools/check_harness_change_gate.py [--base origin/main] [--today YYYY-MM-DD]

Exit 0: no trigger, or a fresh baseline exists. Exit 1: gate fails; the message
names the trigger and the command that creates the baseline.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUDGET_FILE = "tools/check_instruction_budget.py"
MAX_AGE_DAYS = 30
BASELINE_DIR = "evals/baselines"
BUDGET_LINE = re.compile(r"^[+-]\s*[A-Z][A-Z0-9_]*BUDGET[A-Z0-9_]*\s*[:=]")
NEW_LOOP_DOC = "docs/*loop*.md"
BASELINE_COMMAND = ("python3 -m orchestration.eval run --suite "
                    "evals/suites/discipline.yaml --backend anthropic --trials 10 "
                    "--out evals/baselines/{date}")


def triggers(changes: list[tuple[str, str]], budget_patch: str = "") -> list[str]:
    """Why this diff needs a baseline. `changes` is (status, path), status A/M/D/R."""
    reasons = []
    if any(path == BUDGET_FILE for _, path in changes) and any(
            BUDGET_LINE.match(line) for line in budget_patch.splitlines()):
        reasons.append(f"changes a budget constant in {BUDGET_FILE}")
    if any(path.startswith("coordination/skill-tuning/") for _, path in changes):
        reasons.append("touches coordination/skill-tuning/**")
    added = [p for s, p in changes if s.startswith("A")
             and fnmatch.fnmatchcase(p, NEW_LOOP_DOC)]
    if added:
        reasons.append(f"adds a new loop document ({', '.join(sorted(added))})")
    return reasons


def fresh_baseline(root: Path, today: dt.date) -> tuple[Path | None, list[str]]:
    """Newest valid baseline within MAX_AGE_DAYS, plus why others were skipped."""
    notes, best = [], None
    base = root / BASELINE_DIR
    for child in sorted(base.iterdir()) if base.is_dir() else []:
        try:
            day = dt.date.fromisoformat(child.name)
        except ValueError:
            continue
        summary = child / "summary.json"
        if not summary.is_file():
            notes.append(f"{child.name}: no summary.json")
            continue
        try:
            if not isinstance(json.loads(summary.read_text(encoding="utf-8")), dict):
                raise ValueError("not a JSON object")
        except (OSError, ValueError) as exc:
            notes.append(f"{child.name}: unreadable summary.json ({exc})")
            continue
        age = (today - day).days
        if age < 0:
            notes.append(f"{child.name}: dated in the future")
        elif age > MAX_AGE_DAYS:
            notes.append(f"{child.name}: {age} days old (limit {MAX_AGE_DAYS})")
        elif best is None or day > dt.date.fromisoformat(best.parent.name):
            best = summary
    return best, notes


def evaluate(changes: list[tuple[str, str]], budget_patch: str, root: Path,
             today: dt.date) -> tuple[bool, list[str]]:
    reasons = triggers(changes, budget_patch)
    if not reasons:
        return True, ["no harness-loosening change in this diff; gate not triggered"]
    found, notes = fresh_baseline(root, today)
    if found:
        return True, [f"triggered: {'; '.join(reasons)}",
                      f"fresh baseline: {found.relative_to(root)}"]
    lines = [f"FAIL: this change {'; '.join(reasons)}.",
             f"It needs a committed {BASELINE_DIR}/<date>/summary.json no older "
             f"than {MAX_AGE_DAYS} days, and there is none."]
    lines += [f"  skipped {n}" for n in notes]
    lines += ["Create one (needs a backend credential) and commit it:",
              "  " + BASELINE_COMMAND.format(date=today.isoformat())]
    return False, lines


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                          check=True).stdout


def diff_changes(base: str) -> tuple[list[tuple[str, str]], str]:
    span = f"{base}...HEAD"
    changes = []
    for row in _git("diff", "--name-status", span).splitlines():
        status, *paths = row.split("\t")
        changes.append((status, paths[-1]))
    patch = _git("diff", "-U0", span, "--", BUDGET_FILE)
    return changes, patch


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--today", help="YYYY-MM-DD (default: today, UTC)")
    args = ap.parse_args(argv)
    today = (dt.date.fromisoformat(args.today) if args.today
             else dt.datetime.now(dt.timezone.utc).date())
    try:
        changes, patch = diff_changes(args.base)
    except subprocess.CalledProcessError as exc:
        print(f"cannot diff against {args.base}: {exc.stderr.strip()}", file=sys.stderr)
        return 2
    ok, lines = evaluate(changes, patch, REPO, today)
    print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
