#!/usr/bin/env python3
"""Evaluate the S03-trial-s2 validity of the committed runbook.yaml on a trial record directory (test helper of rt_regression.sh).

usage: python3 -I rt_validity.py RUNBOOK.yaml RECORD_DIR
Prints one line: VALID, or INVALID: <the first failing assertion>. The assertions are those of the runbook step S03-trial-s2
(validity.files and by_trial.T2.files), evaluated by tools/runbook.py evaluate_file_block, not a transcription (9d2b6a transcribed
them by hand). RECORD_DIR holds raw-result.json. The unit is trial T2 of run RUN-ICPERF-efb7ef.
"""
import importlib.util
import pathlib
import sys

import yaml

runbook_path, record_dir = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
repo = pathlib.Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location("runbook_tool", repo / "tools" / "runbook.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["runbook_tool"] = mod
spec.loader.exec_module(mod)
doc = yaml.safe_load(runbook_path.read_text(encoding="utf-8"))
step = next(s for s in doc["steps"] if s["id"] == "S03-trial-s2")
files = list(step["validity"]["files"]) + list(step["by_trial"]["T2"]["files"])
results = mod.evaluate_file_block(record_dir, files, unit={"trial_id": "T2", "run_id": "RUN-ICPERF-efb7ef"})
bad = [f for r in results for f in r["failures"]]
print("VALID" if not bad else "INVALID: " + bad[0] + (" (+%d more)" % (len(bad) - 1) if len(bad) > 1 else ""))
