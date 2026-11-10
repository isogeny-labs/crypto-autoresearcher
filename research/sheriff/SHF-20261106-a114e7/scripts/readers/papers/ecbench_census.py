#!/usr/bin/env python3
"""Census of committed ecbench sessions in isogeny-labs/crypto at a given tree (reader `papers`, SHF-20261106-a114e7).

Inputs (data only, nothing from the audited repository is executed):
  argv[1]  output of `git ls-tree -r --name-only HEAD` (one path per line)
  argv[2]  output of `git cat-file --batch` fed with HEAD:<dir>/session.json for every
           directory in argv[3], in the same order
  argv[3]  the list of directories holding a session.json (one per line)
Prints counts and writes ecbench_census.json next to this script.

Classifies each ecbench.session/v1 directory by status, by whether audit.rs's never_finalised
predicate holds (status running, no finished_unix_ms, no records_sha256), by where its records
live (git: records.jsonl / records.jsonl.gz / ecbench_records.jsonl.gz; or only the
`.artifacts.json` pointer), and by whether ci-scope.mjs's directory rules (not the file-name
rule) would select ecbench_replay for an edit of a non-records file in it.
"""
import json
import re
import sys
from pathlib import Path

tree = set(Path(sys.argv[1]).read_text().splitlines())
blob = Path(sys.argv[2]).read_bytes()
dirs = Path(sys.argv[3]).read_text().splitlines()

# Parse git cat-file --batch output.
objs, i = [], 0
while i < len(blob):
    nl = blob.index(b"\n", i)
    header = blob[i:nl].decode()
    parts = header.split()
    if len(parts) == 2 and parts[1] == "missing":
        objs.append(None)
        i = nl + 1
        continue
    size = int(parts[2])
    objs.append(blob[nl + 1: nl + 1 + size])
    i = nl + 1 + size + 1
assert len(objs) == len(dirs), (len(objs), len(dirs))

# ci-scope.mjs:70-79 directory rules (a non-prose file in these trees selects ecbench_replay).
DIR_RULES = [
    re.compile(r"^research/factor_base_shape_leads_20261018/"),
    re.compile(r"^docs/(ecbench|bounds)/"),
    re.compile(r"^research/(ecbench_[^/]+|ghs_curve_comparison_20261009)/"),
    re.compile(r"^research/notes/ecc2k130/(cold_compact_orbit_ic_20261003|full_rank_compact_orbit_ic_20261003)/"),
]
NAME_RULE = re.compile(r"(^|/)(session\.json|(ecbench_)?records\.jsonl(\.gz)?)$")

rows = []
for d, o in zip(dirs, objs):
    if o is None:
        rows.append({"dir": d, "schema": None})
        continue
    try:
        s = json.loads(o)
    except Exception:
        rows.append({"dir": d, "schema": "unparseable"})
        continue
    if not isinstance(s, dict):
        rows.append({"dir": d, "schema": "non-object"})
        continue
    rec_in_git = any(f"{d}/{n}" in tree for n in ("records.jsonl", "records.jsonl.gz", "ecbench_records.jsonl.gz"))
    ptr = f"{d}/.artifacts.json" in tree
    rows.append({
        "dir": d,
        "schema": s.get("schema"),
        "status": s.get("status"),
        "never_finalised": s.get("status") == "running" and s.get("finished_unix_ms") is None
        and s.get("records_sha256") is None,
        "records_in_git": rec_in_git,
        "pointer_manifest": ptr,
        "dir_rule_selects": any(r.search(f"{d}/.artifacts.json") for r in DIR_RULES),
        "pointer_name_rule_selects": bool(NAME_RULE.search(f"{d}/.artifacts.json")),
    })

eb = [r for r in rows if r.get("schema") == "ecbench.session/v1"]
status = {}
for r in eb:
    status[r["status"]] = status.get(r["status"], 0) + 1
nf = [r["dir"] for r in eb if r["never_finalised"]]
ptr_only = [r for r in eb if not r["records_in_git"] and r["pointer_manifest"]]
ptr_only_unselected = [r["dir"] for r in ptr_only if not r["dir_rule_selects"]]
nf_ptr_only_unselected = [r["dir"] for r in ptr_only if not r["dir_rule_selects"] and r["never_finalised"]]
neither = [r["dir"] for r in eb if not r["records_in_git"] and not r["pointer_manifest"]]
out = {
    "session_json_dirs": len(rows),
    "ecbench_session_v1": len(eb),
    "other_schemas": sorted({str(r.get("schema")) for r in rows if r.get("schema") != "ecbench.session/v1"}),
    "status_counts": status,
    "never_finalised": len(nf),
    "never_finalised_dirs": nf,
    "records_only_behind_pointer": len(ptr_only),
    "pointer_only_outside_ci_scope_dir_rules": len(ptr_only_unselected),
    "pointer_only_outside_dir_rules_and_never_finalised": nf_ptr_only_unselected,
    "pointer_name_rule_selects_any": any(r["pointer_name_rule_selects"] for r in eb),
    "records_neither_in_git_nor_pointer": neither,
    "examples_pointer_only_outside_dir_rules": ptr_only_unselected[:5],
}
print(json.dumps({k: v for k, v in out.items() if not k.endswith("_dirs")}, indent=1))
Path(__file__).with_name("ecbench_census.json").write_text(json.dumps(out, indent=1))
