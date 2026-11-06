#!/usr/bin/env python3
"""Compare every replayed census job record with the recorded one, field by field (seconds excluded),
keyed by (cell, block, c). The runbook audit itself compares only raw-result.json /summary.
usage: python3 -I compare_jobs.py <recorded.jsonl> <replay.jsonl> <out.json>"""
import json, sys
rec = {}
for l in open(sys.argv[1]):
    r = json.loads(l); rec[(r["cell"], r["block"], r["c"])] = r
n = eq = 0; diffs = []
for l in open(sys.argv[2]):
    if not l.endswith("\n"):
        continue  # partial last line while the replay is still writing
    r = json.loads(l); k = (r["cell"], r["block"], r["c"]); n += 1
    a = {x: y for x, y in rec[k].items() if x != "seconds"}; b = {x: y for x, y in r.items() if x != "seconds"}
    if a == b:
        eq += 1
    else:
        diffs.append({"key": k, "fields": sorted(x for x in set(a) | set(b) if a.get(x) != b.get(x))})
res = {"replayed_records": n, "equal_records": eq, "recorded_records": len(rec), "differing": diffs[:20],
       "cells_covered": sorted({k[0] for k in rec if False} | set())}
json.dump(res, open(sys.argv[3], "w"), indent=1); print(json.dumps({k: v for k, v in res.items() if k != "cells_covered"}))
