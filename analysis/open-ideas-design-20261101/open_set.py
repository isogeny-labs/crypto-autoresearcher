#!/usr/bin/env python3
"""Open ideas under EXPLICIT proposal links (corrected definition).

An idea is open when it is `proposed`, not `dominated_by`, and no hypothesis or
experiment record LINKS it (proposal_id / source_proposal / derived_from_idea /
source_idea, or an index refs entry). A mere textual mention is not a link; the
earlier 2026-10-31 pass counted mentions and therefore undercounted the set.

`--pre` reports the five ideas this pass designs. The default asserts the set is
now empty and that every designed idea is linked downstream.
"""
import glob
import json
import os
import sys

from orchestration import fast_yaml

DESIGNED = {
    "IDEA-20261029-2e292c", "IDEA-20261029-3d0e71", "IDEA-20261029-8d82e6",
    "IDEA-20261029-e4edce", "IDEA-20261029-ec08bc",
}


def taken_ids():
    taken = set()
    for p in ("ledger/.index/hypotheses.jsonl", "ledger/.index/experiments.jsonl"):
        if not os.path.isfile(p):
            continue
        for line in open(p):
            d = json.loads(line)
            for k in ("proposal_id", "derived_from_idea"):
                if isinstance(d.get(k), str):
                    taken.add(d[k])
            for x in d.get("refs") or []:
                if isinstance(x, str) and x.startswith("IDEA-"):
                    taken.add(x)
    for f in glob.glob("ledger/hypotheses/*.yaml"):
        d = fast_yaml.safe_load(open(f)) or {}
        h = d.get("hypothesis", {}) if isinstance(d, dict) else {}
        if not isinstance(h, dict):
            continue
        for k in ("proposal_id", "source_proposal"):
            if isinstance(h.get(k), str):
                taken.add(h[k])
        for x in h.get("depends_on") or []:
            if isinstance(x, str) and x.startswith("IDEA-"):
                taken.add(x)
    for f in glob.glob("experiments/*/specification.yaml"):
        d = fast_yaml.safe_load(open(f)) or {}
        e = d.get("experiment", {}) if isinstance(d, dict) else {}
        if not isinstance(e, dict):
            continue
        for k in ("derived_from_idea", "source_idea"):
            if isinstance(e.get(k), str):
                taken.add(e[k])
    return taken


def scan(ignore_taken=False):
    taken = taken_ids()
    rows = []
    for f in glob.glob("ledger/proposals/*.yaml"):
        iid = os.path.basename(f)[:-5]
        i = (fast_yaml.safe_load(open(f)) or {}).get("idea", {})
        if not isinstance(i, dict) or i.get("status") != "proposed" or i.get("dominated_by"):
            continue
        if not ignore_taken and iid in taken:
            continue
        rows.append((str(i.get("added") or ""), iid, i.get("recommended_priority"),
                     i.get("question_id") or "", i.get("title", "")))
    return sorted(rows)


def main():
    pre = "--pre" in sys.argv
    rows = scan(ignore_taken=pre)
    if pre:
        rows = [r for r in rows if r[1] in DESIGNED]
    for r in rows:
        print(f"{r[0]} {r[1]} {r[2]} {r[3]} | {r[4][:100]}")
    if pre:
        found = {r[1] for r in rows}
        print(f"\nopen ideas (pre-design, explicit links): {len(rows)}; designed: {len(DESIGNED)}")
        if found != DESIGNED:
            print(f"SET MISMATCH {sorted(found ^ DESIGNED)}", file=sys.stderr)
            return 1
        print("OK: the designed set equals the pre-design open set")
        return 0
    print(f"\nopen ideas now: {len(rows)}; designed: {len(DESIGNED)}")
    if rows:
        print(f"REMAINING OPEN {sorted(r[1] for r in rows)}", file=sys.stderr)
        return 1
    taken = taken_ids()
    if not DESIGNED <= taken:
        print(f"NOT LINKED {sorted(DESIGNED - taken)}", file=sys.stderr)
        return 1
    print("OK: no open idea remains, and all 5 designs are linked downstream")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
