#!/usr/bin/env python3
"""Replay the archived benchmark dashboard provenance comparison offline."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PINNED = REPO / "ui/benchmarks/cryptanalysis-primary.json"


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_json(path: Path):
    raw = path.read_bytes()
    return json.loads(raw), sha256(raw)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def without_commit_locations(snapshot: dict) -> dict:
    result = copy.deepcopy(snapshot)
    result.pop("source_commit")
    for row in result["rows"]:
        row["id"] = row["id"].split(":", 1)[1]
    for source in result["sources"].values():
        source.pop("url")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=PINNED)
    parser.add_argument("--current-export", type=Path, default=HERE / "current-export.json")
    args = parser.parse_args()
    pinned, pinned_sha = read_json(args.snapshot)
    catalog, _ = read_json(REPO / "ui/benchmarks/catalog.json")
    receipts, _ = read_json(REPO / "ui/receipts.json")
    current, current_sha = read_json(args.current_export)
    live, live_sha = read_json(HERE / "live-comparisons.json")
    meta, meta_sha = read_json(HERE / "live-meta.json")
    live_latest, live_latest_sha = read_json(HERE / "live-comparisons-20261103.json")
    meta_latest, meta_latest_sha = read_json(HERE / "live-meta-20261103.json")

    require(pinned["schema"] == current["schema"] == 1, "schema mismatch")
    require(pinned["source_commit"] == "5ab7d5bc5a16ff4d87a5ef8bed45cf9543f47c14",
            "pinned source revision mismatch")
    require(current["source_commit"] == "bf155c25e57c6eefbaeed2c19b84786e402851f7",
            "current export revision mismatch")
    require(pinned["source_repository"] == current["source_repository"], "source repository mismatch")
    require(pinned_sha == catalog["sha256"], "catalog hash mismatch")
    require(len(pinned["rows"]) == len(current["rows"]) == 9, "row count mismatch")
    require(len(pinned["sources"]) == len(current["sources"]) == 7, "source count mismatch")
    require(without_commit_locations(pinned) == without_commit_locations(current),
            "measurement, identity, or source hash mismatch")
    require(live["benchmarks"] == pinned, "live benchmark payload mismatch")
    require(meta["mode"] == "static", "live mode mismatch")
    require(meta["commit"] == "6d5e7c5c6d442e85e0a78864e84d74898becab73",
            "live build revision mismatch")
    require(live_latest["benchmarks"] == pinned, "latest live benchmark payload mismatch")
    require(meta_latest["mode"] == "static", "latest live mode mismatch")
    require(meta_latest["commit"] == "9b721d74256afa5e007e21f24d86e2953e33b214",
            "latest live build revision mismatch")
    registered = [r for r in receipts["receipts"] if r["adapter"] == "benchmark-snapshot/1"]
    require(len(registered) == 9, "receipt count mismatch")
    require({r["row_id"] for r in registered} == {r["id"] for r in pinned["rows"]},
            "receipt row IDs mismatch")
    require(all(r["snapshot"]["path"] == "ui/benchmarks/cryptanalysis-primary.json"
                and r["snapshot"]["sha256"] == pinned_sha for r in registered),
            "receipt snapshot pin mismatch")

    print(json.dumps({
        "result": "pass",
        "pinned_source_commit": pinned["source_commit"],
        "current_source_commit": current["source_commit"],
        "live_site_commit": meta["commit"],
        "live_site_built_at": meta["built_at"],
        "latest_live_site_commit": meta_latest["commit"],
        "latest_live_site_built_at": meta_latest["built_at"],
        "rows": len(pinned["rows"]),
        "source_files": len(pinned["sources"]),
        "registered_receipts": len(registered),
        "measurement_and_source_hash_differences": 0,
        "pinned_sha256": pinned_sha,
        "current_export_sha256": current_sha,
        "live_comparisons_sha256": live_sha,
        "live_meta_sha256": meta_sha,
        "latest_live_comparisons_sha256": live_latest_sha,
        "latest_live_meta_sha256": meta_latest_sha,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
