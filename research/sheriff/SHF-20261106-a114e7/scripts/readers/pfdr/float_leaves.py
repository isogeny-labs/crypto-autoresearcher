#!/usr/bin/env python3
"""Count differing leaves between a recorded and a replayed JSON file (float vs non-float), max rel diff.
usage: python3 -I float_leaves.py <recorded.json> <replay.json>"""
import json, sys, struct
def leaves(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items(): yield from leaves(v, f"{p}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from leaves(v, f"{p}/{i}")
    else:
        yield p, o
a = dict(leaves(json.load(open(sys.argv[1])))); b = dict(leaves(json.load(open(sys.argv[2]))))
fl = [k for k in a if isinstance(a[k], float)]
diff_f = [k for k in fl if a[k] != b.get(k)]
diff_nf = [k for k in a if not isinstance(a[k], float) and a[k] != b.get(k)] + [k for k in b if k not in a]
def ulps(x, y):
    i = lambda v: struct.unpack("<q", struct.pack("<d", v))[0]
    return abs(i(x) - i(y))
print(json.dumps({"leaves": len(a), "float_leaves": len(fl), "float_leaves_differing": len(diff_f),
                  "nonfloat_differing": diff_nf[:10],
                  "max_rel": max((abs(a[k] - b[k]) / abs(a[k]) for k in diff_f if a[k]), default=0),
                  "max_ulps": max((ulps(a[k], b[k]) for k in diff_f), default=0)}))
