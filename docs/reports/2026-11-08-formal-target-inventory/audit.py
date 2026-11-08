#!/usr/bin/env python3
"""Static, commit-pinned formal target inventory; no Lean execution."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path

import yaml


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), *args])


def blob(repo: Path, commit: str, path: str) -> bytes:
    if not path or path.startswith("/") or ".." in Path(path).parts:
        raise ValueError(f"invalid source path: {path!r}")
    return git(repo, "show", f"{commit}:{path}")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inventory(repo: Path, commit: str) -> dict:
    resolved = git(repo, "rev-parse", commit).decode().strip()
    if resolved != commit or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("--commit must be a full, existing Git commit SHA")
    paths = git(repo, "ls-tree", "-r", "--name-only", commit, "formal/targets").decode().splitlines()
    specs = sorted(p for p in paths if p.endswith(".yaml"))
    experiments = {name for name in git(repo, "ls-tree", "-d", "--name-only", f"{commit}:experiments").decode().splitlines() if name.startswith("EXP-")}
    rows = []
    for path in specs:
        raw = blob(repo, commit, path)
        spec = yaml.safe_load(raw)
        if not isinstance(spec, dict) or spec.get("schema") != "crypto.autoresearch.formal_task.v1":
            raise ValueError(f"invalid formal target schema: {path}")
        source = spec["source"]
        theorem = spec["workspace"].rstrip("/") + "/" + spec["theorem_file"]
        source_raw, theorem_raw = blob(repo, commit, source), blob(repo, commit, theorem)
        mentioned = sorted(set(re.findall(r"\bEXP-[A-Z0-9]+-[0-9a-f]{6}\b", raw.decode() + source_raw.decode(errors="replace"))) & experiments)
        rows.append({
            "spec": path, "spec_sha256": sha(raw), "task_id": spec["task_id"],
            "claim_id": spec["claim_id"], "source": source, "source_sha256": sha(source_raw),
            "source_status": spec["source_status"], "theorem_name": spec["theorem_name"],
            "theorem_file": theorem, "theorem_sha256": sha(theorem_raw),
            "explicit_run_reference": bool(re.search(r"(?:/runs/|\bRUN-[A-Za-z0-9-]+\b)", raw.decode())),
            "source_is_run_artifact": "/runs/" in "/" + source + "/",
            "exact_experiment_ids_mentioned": mentioned,
        })
    collisions = {}
    for key in ("task_id", "claim_id", "theorem_name"):
        groups = collections.defaultdict(list)
        for row in rows:
            groups[row[key]].append(row["spec"])
        collisions[key] = {k: v for k, v in sorted(groups.items()) if len(v) > 1}
    statuses = collections.Counter(row["source_status"] for row in rows)
    return {
        "schema": "crypto.validation.formal_target_static_audit/v1",
        "commit": commit,
        "formal_tree": git(repo, "rev-parse", f"{commit}:formal").decode().strip(),
        "scope": "Git object bytes, declared paths and syntactic pointers only; no Lean build, semantic fidelity, execution replay or experiment coverage inference",
        "status": "integrity_fail" if any(collisions.values()) else "structurally_consistent",
        "summary": {
            "specs": len(rows), "unique_theorem_files": len({r["theorem_file"] for r in rows}),
            "unique_sources": len({r["source"] for r in rows}),
            "experiment_directories": len(experiments),
            "specs_with_exact_experiment_pointer": sum(bool(r["exact_experiment_ids_mentioned"]) for r in rows),
            "specs_with_explicit_run_reference": sum(r["explicit_run_reference"] for r in rows),
            "source_run_artifacts": sum(r["source_is_run_artifact"] for r in rows),
            "source_statuses": dict(sorted(statuses.items())),
        },
        "collisions": collisions,
        "targets": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[3])
    ap.add_argument("--commit", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--require-clean", action="store_true")
    args = ap.parse_args()
    result = inventory(args.repo, args.commit)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], **result["summary"], "collisions": result["collisions"]}, sort_keys=True))
    return int(args.require_clean and result["status"] != "structurally_consistent")


if __name__ == "__main__":
    raise SystemExit(main())
