#!/usr/bin/env python3
"""Recompute the open-idea set this design pass covers.

An idea is open when its proposal record has:
  * idea.status == "proposed"
  * no idea.dominated_by
  * its IDEA-* id appears in no hypothesis record and no experiment index

Run from the repository root with PYTHONPATH=. ; prints one line per idea and
exits 0 only if the count is 11 (the set designed in DESIGN.md).
"""
import glob
import json
import os
import re
import sys

from orchestration import fast_yaml

EXPECTED = {
    "IDEA-20261016-397ac9", "IDEA-20261016-cdb5e4", "IDEA-20261016-fb1656",
    "IDEA-20261017-0e2dab", "IDEA-20261017-3079bc", "IDEA-20261017-3db2a8",
    "IDEA-20261017-e9f824", "IDEA-20261018-329d0a", "IDEA-20261018-5f37a1",
    "IDEA-20261018-d4cef4", "IDEA-20261018-f2cd4d",
}


def main() -> int:
    refs = set()
    for p in glob.glob("ledger/hypotheses/*.yaml") + [
            "ledger/.index/hypotheses.jsonl", "ledger/.index/experiments.jsonl"]:
        if os.path.isfile(p):
            refs.update(re.findall(r"IDEA-[A-Za-z0-9-]+", open(p, errors="ignore").read()))
    out = []
    for f in glob.glob("ledger/proposals/*.yaml"):
        iid = os.path.basename(f)[:-5]
        d = fast_yaml.safe_load(open(f)) or {}
        idea = d.get("idea", d)
        if idea.get("status") != "proposed" or idea.get("dominated_by"):
            continue
        if iid in refs:
            continue
        out.append((str(idea.get("added") or idea.get("date") or ""), iid,
                    idea.get("question_id") or "-", idea.get("title", "")))
    out.sort()
    for date, iid, qid, title in out:
        print(f"{date} {iid} {qid} | {title[:110]}")
    found = {x[1] for x in out}
    print(f"\nopen ideas: {len(out)}; designed: {len(EXPECTED)}")
    if found != EXPECTED:
        print(f"SET MISMATCH missing={sorted(found ^ EXPECTED)}", file=sys.stderr)
        return 1
    print("OK: the designed set equals the recomputed open set")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
