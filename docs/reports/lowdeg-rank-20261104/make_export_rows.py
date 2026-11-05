"""Rebuild ld_rows.jsonl (the raw file named in export.json) from rows.jsonl: adds deficit, status, verification, tier."""
import json, sys
with open(sys.argv[2], "w") as f:
    for l in open(sys.argv[1]):
        r = json.loads(l); r["deficit"] = r["expected_generic"] - r["rank"]
        r["status"] = "succeeded"; r["verification"] = "not_run"; r["tier"] = "none"; f.write(json.dumps(r) + "\n")
