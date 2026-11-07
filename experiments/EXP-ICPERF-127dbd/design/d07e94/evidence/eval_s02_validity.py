import importlib.util, pathlib, sys, yaml
repo = pathlib.Path(sys.argv[1]); rec_dir = pathlib.Path(sys.argv[2])
spec = importlib.util.spec_from_file_location("rb", repo / "tools/runbook.py"); mod = importlib.util.module_from_spec(spec); sys.modules["rb"] = mod; spec.loader.exec_module(mod)
doc = yaml.safe_load((repo / "experiments/EXP-ICPERF-127dbd/runbook.yaml").read_text())
step = next(s for s in doc["steps"] if s["id"] == "S02-reconcile-t1")
files = [dict(o, path=o["path"].replace("{out}/", "", 1)) for o in step["validity"]["outputs"]]
res = mod.evaluate_file_block(rec_dir, files, unit={"trial_id": "T1", "run_id": "RUN-ICPERF-8b0d47"})
for r in res:
    for f in r["failures"]: print("FAIL", f)
print("checked", sum(len(r.get("results", [])) if isinstance(r, dict) else 0 for r in res), "blocks; failures above")
