#!/usr/bin/env python3
"""Classify a published dashboard integrity snapshot without editing records."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from orchestration import fast_yaml
from ui.index import ResearchIndex, id_kind


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def duplicate_class(paths: list[str]) -> str:
    if any("/schema-supersessions/" in path for path in paths):
        return "stored_schema_supersession"
    if any(path.startswith("ledger/archives/") for path in paths):
        return "archive_copy"
    if any(path.startswith("ledger/corrections/") for path in paths):
        return "other_correction_copy"
    if all(path.startswith("ledger/") for path in paths):
        return "active_ledger_collision_or_legacy_alias"
    return "experiment_header_collision"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--site-integrity", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    snapshot = json.loads(args.site_integrity.read_text())
    index = ResearchIndex(repo).build()
    resolvable = {"GOAL", "RQ", "H", "EXP", "EV", "DEC", "IDEA", "KN"}
    refs: Counter[str] = Counter()
    for record in index.records.values():
        for ref in record.refs:
            if id_kind(ref) in resolvable and ref not in index.records:
                refs[ref] += 1
    assert len(refs) == snapshot["dangling_refs_total"]
    assert len(index.duplicate_paths) == len(snapshot["duplicate_ids"])

    duplicates = []
    for item in snapshot["duplicate_ids"]:
        paths = item["paths"]
        hashes = {path: digest(repo / path) for path in paths}
        duplicates.append({
            "id": item["id"], "classification": duplicate_class(paths),
            "paths": paths, "sha256": hashes,
            "same_bytes": len(set(hashes.values())) == 1,
        })
    dangling = []
    for ref, count in sorted(refs.items(), key=lambda kv: (-kv[1], kv[0])):
        kind = id_kind(ref)
        directory = repo / "experiments" / ref if kind == "EXP" else None
        dangling.append({
            "id": ref, "kind": kind, "cited_by": count,
            "experiment_directory_exists": bool(directory and directory.is_dir()),
            "classification": "present_experiment_directory_not_indexed"
            if directory and directory.is_dir() else "unresolved_in_dashboard_index",
        })
    malformed = []
    for item in snapshot["unparseable"]:
        path = repo / item["path"]
        try:
            fast_yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
        except Exception as error:  # exact dashboard parser failure is the target
            headline = str(error).splitlines()[0][:200]
            assert headline == item["error"], (item["path"], headline, item["error"])
            mark = getattr(error, "problem_mark", None)
            malformed.append({**item, "sha256": digest(path),
                              "error_line": mark.line + 1 if mark is not None else None})
        else:
            raise AssertionError(f"published parse failure no longer reproduces: {item['path']}")
    result = {
        "schema": "dashboard-integrity-triage/1",
        "commit": "e23868a6e59297d0f97875b6454692c59f1cc11d",
        "site_integrity_sha256": digest(args.site_integrity),
        "counts": {
            "unparseable": len(malformed), "duplicate_ids": len(duplicates),
            "id_path_mismatch": len(snapshot["id_path_mismatch"]),
            "dangling_ids": len(dangling), "published_dangling_sample": len(snapshot["dangling_refs"]),
        },
        "malformed": malformed, "duplicates": duplicates,
        "dangling": dangling,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
