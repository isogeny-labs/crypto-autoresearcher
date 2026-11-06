#!/usr/bin/env python3
"""Ordered list of trials (one per run.py invocation) for the frozen grid:
T0 fixtures, then T1 cells in ascending N, then T3, then T2 in ascending N;
within a cell, for r = 0..4: EQS4, EQS2, NULL-PROF, NULL-SHUF, PC-TRI, then
EQS4-AA (r in {0,1}), then EQS4-U, then EQS4-FULLFE and EQS4-NOFE (r in {0,1},
N <= 20). Prints JSON lines {"cell","arm","r"}; allocates nothing and runs
nothing. Dynamic rules (AA re-run of every non-contained target, SR-3 budget
skips) are applied by the runner, not here.

    python3 plan.py [--cells m3n03,m3n04]
"""
import argparse
import json

import cells as CE


def plan(only=None):
    out = []
    for cid in CE.EXECUTION_ORDER:
        if only and cid not in only:
            continue
        c = CE.CELLS[cid]
        per = CE.ARMS_PER_TIER[c["tier"]]
        for r in range(5):
            for arm in ("EQS4", "EQS2", "NULL-PROF", "NULL-SHUF", "PC-TRI"):
                if arm not in per or r >= per[arm]:
                    continue
                if arm == "NULL-SHUF" and c["N"] > 26:
                    continue
                out.append({"cell": cid, "arm": arm, "r": r})
        for arm, rs in (("EQS4-AA", range(2)), ("EQS4-U", range(5)), ("EQS4-FULLFE", range(2)),
                        ("EQS4-NOFE", range(2))):
            if arm not in per:
                continue
            for r in rs:
                if r >= per[arm]:
                    continue
                if arm in ("EQS4-FULLFE", "EQS4-NOFE") and c["N"] > 20:
                    continue
                out.append({"cell": cid, "arm": arm, "r": r})
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", default=None)
    a = ap.parse_args()
    for t in plan(set(a.cells.split(",")) if a.cells else None):
        print(json.dumps(t))
