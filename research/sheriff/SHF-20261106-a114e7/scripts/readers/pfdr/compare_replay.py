#!/usr/bin/env python3
"""Byte-compare a replayed unit directory against the recorded run directory.
usage: python3 -I compare_replay.py <recorded_runs_dir> <replay_base> <out.json> trial:RUN ..."""
import hashlib, json, os, sys
rec_base, rep_base, out_p = sys.argv[1:4]
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
res = {}
for spec in sys.argv[4:]:
    trial, run = spec.split(":")
    rd, pd = os.path.join(rec_base, run), os.path.join(rep_base, trial, run)
    interp = json.load(open(os.path.join(rep_base, trial, "interp.json"))) if os.path.exists(os.path.join(rep_base, trial, "interp.json")) else None
    files = {}
    for f in sorted(set(os.listdir(rd)) | set(os.listdir(pd))):
        a, b = os.path.join(rd, f), os.path.join(pd, f)
        files[f] = {"recorded": sha(a) if os.path.exists(a) else None, "replay": sha(b) if os.path.exists(b) else None}
        files[f]["equal"] = files[f]["recorded"] == files[f]["replay"]
    # stdout/stderr of run.py were captured beside the unit dir by the driver
    for f in ("stdout.log", "stderr.log", "check.stdout.log", "check.stderr.log"):
        b = os.path.join(rep_base, trial, f)
        if os.path.exists(b):
            files[f]["replay"] = sha(b); files[f]["equal"] = files[f]["recorded"] == files[f]["replay"]
    res[spec] = {"interpreter": interp, "files": files,
                 "unequal": [f for f, v in files.items() if not v["equal"]]}
json.dump(res, open(out_p, "w"), indent=1)
for k, v in res.items():
    print(k, (v["interpreter"] or {}).get("version"), "unequal:", v["unequal"])
