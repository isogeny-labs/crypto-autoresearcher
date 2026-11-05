#!/usr/bin/env python3
"""Producer-written output checker of EXP-PEXT-0b2c75 (not independent review).

  python3 check.py RUN_DIR PLAN TRIAL_ID      exit 0 iff the recorded run directory is well formed and its instrument
                                              counters are clean. A law mismatch (a result) is NOT a checker failure;
                                              an instrument defect is.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bitalgebra  # noqa: E402
import run as drv  # noqa: E402

VALID = drv.VALIDITY_KEYS


def fail(msgs: list, m: str) -> None:
    msgs.append(m)


def check_stream(rd: str, name: str, expected_arms: list, msgs: list) -> None:
    path = os.path.join(rd, name)
    if not os.path.exists(path):
        return fail(msgs, f"missing {name}")
    with gzip.open(path, "rb") as f:
        raw = f.read()
    with open(os.path.join(rd, "raw-result.json")) as f:
        summ = json.load(f).get("summary", {})
    if summ.get("stream_sha256") != hashlib.sha256(raw).hexdigest():
        fail(msgs, f"{name}: stream sha256 differs from raw-result.json")
    arms = []
    cur = None
    for line in raw.decode().splitlines():
        r = json.loads(line)
        if r["rec"] == "field":
            cur = {"field": r, "units": [], "totals": None}
            arms.append(cur)
        elif r["rec"] in ("unit", "rand"):
            cur["units"].append(r)
        elif r["rec"] == "totals":
            cur["totals"] = r
    got = [(a["field"]["q"], a["field"]["n"], ",".join(map(str, a["field"]["S"])) if "S" in a["field"] else "random") for a in arms]
    if got != expected_arms:
        fail(msgs, f"{name}: arms {got} != expected {expected_arms}")
    for a in arms:
        f, tot = a["field"], a["totals"]
        if tot is None:
            fail(msgs, f"{name}: arm without totals")
            continue
        if "S" in f:
            if f["orbits"] != f["orbits_expected"] or tot["units"] != len(a["units"]) or len(a["units"]) != 2 * f["orbits"]:
                fail(msgs, f"{name}: orbit/unit count at q={f['q']} n={f['n']}")
            for k in VALID:
                if tot[k] != 0:
                    fail(msgs, f"{name}: validity counter {k} = {tot[k]} at q={f['q']} n={f['n']} S={f['S']}")
            for u in a["units"]:
                bits = {k + 1: b for k, b in enumerate(u["bits"])}
                sp, w, h, e4p = bitalgebra.predict(f["n"], tuple(f["S"]), u["eps"], u["t"], bits)
                if u["E4_pred"] != e4p or u["s_pred"] != list(sp):
                    fail(msgs, f"{name}: tool predictor differs from bitalgebra.py at q={f['q']} orbit={u['orbit']}")
                    break
                if u["E4"] not in (4, 8, 16) or u["order"] % u["E4"] != 0 or u["order"] != u["order_quartic"] or u["E4"] != u["E4_M1"]:
                    fail(msgs, f"{name}: inconsistent unit at q={f['q']} orbit={u['orbit']}")
                    break
        else:
            if tot["units"] != 2 * f["configs"] or any(tot[k] != 0 for k in ("m1_m2_mismatch", "quartic_cubic_order_mismatch", "hasse_fail", "e2_not_4")):
                fail(msgs, f"{name}: random arm counters at q={f['q']}")


def main() -> int:
    rd, plan_path, tid = sys.argv[1:4]
    with open(plan_path) as f:
        plan = json.load(f)
    trial = next(t for t in plan["trials"] if t["id"] == tid)
    msgs: list = []
    for a in trial["artifacts"]:
        if not os.path.exists(os.path.join(rd, a)):
            fail(msgs, f"missing artifact {a}")
    rrp = os.path.join(rd, "raw-result.json")
    if os.path.exists(rrp):
        with open(rrp) as f:
            rr = json.load(f)
        if rr.get("invalid_reason"):
            fail(msgs, f"raw-result.json invalid_reason: {rr['invalid_reason']}")
        if rr.get("attack_claimed") is not False or rr.get("run_id") != trial["run_id"]:
            fail(msgs, "raw-result.json header")
    st = trial["stage"]
    if not msgs:
        if st == "regression":
            with open(os.path.join(rd, "regression.json")) as f:
                if not json.load(f).get("pass"):
                    fail(msgs, "regression.json pass is false")
        elif st == "n5core":
            check_stream(rd, "n5-core.jsonl.gz", [(q, 5, drv.S5) for q in drv.N5CORE], msgs)
        elif st == "n5ext":
            check_stream(rd, "n5-ext.jsonl.gz", [(q, 5, drv.S5) for q in drv.N5EXT], msgs)
        elif st == "n7":
            arms = [(q, 7, drv.N7_PRIMARY[0]) for q in drv.N7_PRIMARY[1]] + [(q, 7, s) for s in drv.N7_SECONDARY[0] for q in drv.N7_SECONDARY[1]]
            check_stream(rd, "n7.jsonl.gz", arms, msgs)
        elif st == "negative":
            check_stream(rd, "negative.jsonl.gz", [(q, 5, "random") for q in drv.NEG_Q], msgs)
        elif st == "analyze":
            with open(os.path.join(rd, "analysis.json")) as f:
                an = json.load(f)
            if not isinstance(an.get("valid"), bool) or not an.get("headline"):
                fail(msgs, "analysis.json lacks valid/headline")
    print(json.dumps({"trial": tid, "ok": not msgs, "failures": msgs}))
    return 0 if not msgs else 1


if __name__ == "__main__":
    sys.exit(main())
