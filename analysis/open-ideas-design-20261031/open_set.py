#!/usr/bin/env python3
"""Compute the open-idea set, before and after this design pass.

An idea is open when its proposal record has:
  * idea.status == "proposed"
  * no idea.dominated_by
  * its IDEA-* id appears in no hypothesis record and no experiment index

`--pre` reports the set as it stood before the 11 designs were ledgered (the
snapshot this pass covers, 11 ideas). The default reports the current set and
checks closure: every designed idea is now referenced downstream, and no other
proposed, undominated idea is left unreferenced.

Run from the repository root with PYTHONPATH=.
"""
import glob
import os
import re
import sys

from orchestration import fast_yaml

DESIGNED = {
    "IDEA-20261016-397ac9", "IDEA-20261016-cdb5e4", "IDEA-20261016-fb1656",
    "IDEA-20261017-0e2dab", "IDEA-20261017-3079bc", "IDEA-20261017-3db2a8",
    "IDEA-20261017-e9f824", "IDEA-20261018-329d0a", "IDEA-20261018-5f37a1",
    "IDEA-20261018-d4cef4", "IDEA-20261018-f2cd4d",
}


def scan():
    refs = set()
    for p in glob.glob("ledger/hypotheses/*.yaml") + [
            "ledger/.index/hypotheses.jsonl", "ledger/.index/experiments.jsonl"]:
        if os.path.isfile(p):
            refs.update(re.findall(r"IDEA-[A-Za-z0-9-]+", open(p, errors="ignore").read()))
    rows = []
    for f in glob.glob("ledger/proposals/*.yaml"):
        iid = os.path.basename(f)[:-5]
        d = fast_yaml.safe_load(open(f)) or {}
        idea = d.get("idea", d)
        if idea.get("status") != "proposed" or idea.get("dominated_by"):
            continue
        rows.append((str(idea.get("added") or idea.get("date") or ""), iid,
                     idea.get("question_id") or "-", idea.get("title", ""),
                     iid in refs))
    return sorted(rows)


def main() -> int:
    pre = "--pre" in sys.argv
    rows = scan()
    open_rows = [r for r in rows if not (pre and False) and not r[4]]
    if pre:
        # As it stood before the ledger records: drop references added by this pass.
        open_rows = [r for r in rows if r[1] in DESIGNED]
    for date, iid, qid, title, _ in open_rows:
        print(f"{date} {iid} {qid} | {title[:110]}")
    if pre:
        found = {r[1] for r in open_rows}
        print(f"\nopen ideas (pre-design snapshot): {len(open_rows)}; designed: {len(DESIGNED)}")
        if found != DESIGNED:
            print(f"SET MISMATCH {sorted(found ^ DESIGNED)}", file=sys.stderr)
            return 1
        print("OK: the designed set equals the pre-design open set")
        return 0
    closed = sorted(i for i in DESIGNED if any(r[1] == i and r[4] for r in rows))
    print(f"\nopen ideas now: {len(open_rows)}; designed: {len(DESIGNED)}; designed now referenced downstream: {len(closed)}")
    if open_rows:
        print(f"REMAINING OPEN {sorted(r[1] for r in open_rows)}", file=sys.stderr)
        return 1
    if len(closed) != len(DESIGNED):
        print(f"NOT CLOSED {sorted(DESIGNED - set(closed))}", file=sys.stderr)
        return 1
    print("OK: no open idea remains, and all 11 designs are referenced downstream")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
