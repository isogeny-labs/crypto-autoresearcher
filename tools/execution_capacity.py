#!/usr/bin/env python3
"""Execution capacity versus approved-unrun demand (harness review I3).

Read-only. Capacity comes from `orchestration/execution-capacity.yaml`
(CPU-hours per week per route; every seeded number is `unverified`). Demand
is the sum, over approved contracts that never ran (tools/portfolio_kpis.py's
definition), of each specification's declared budget:

1. `budget.total_cpu_hours`, else
2. `budget.wall_clock_seconds_per_run * budget.maximum_runs / 3600`, else
3. `default_contract_cpu_hours` from the YAML (0.5, the modal declared value).

The Coordinator copies the printed sentence into its wake receipt and fills N:
"capacity X h, demand Y h, dispatching N / recording why not".

Usage:
    python3 tools/execution_capacity.py [--dispatching N] [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import portfolio_kpis as kpis  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
CAPACITY_FILE = REPO / "orchestration" / "execution-capacity.yaml"
FALLBACK_DEFAULT_HOURS = 0.5


def load_capacity(path: Path = CAPACITY_FILE) -> dict[str, Any]:
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    routes = []
    for r in doc.get("routes") or []:
        routes.append({
            "name": str(r.get("name")),
            "cpu_hours_per_week": float(r.get("cpu_hours_per_week") or 0),
            "number_status": str(r.get("number_status", "unverified")),
            "last_verified": str(r.get("last_verified", "")),
            "source_of_truth": " ".join(str(r.get("source_of_truth", "")).split()),
        })
    default = float(doc.get("default_contract_cpu_hours") or FALLBACK_DEFAULT_HOURS)
    return {"routes": routes, "default_contract_cpu_hours": default}


def declared_hours(spec_budget: Any) -> float | None:
    """CPU-hours a specification's budget declares, or None."""
    if not isinstance(spec_budget, dict):
        return None
    try:
        if spec_budget.get("total_cpu_hours") is not None:
            return float(spec_budget["total_cpu_hours"])
        secs = spec_budget.get("wall_clock_seconds_per_run")
        runs = spec_budget.get("maximum_runs")
        if secs is not None and runs is not None:
            return float(secs) * float(runs) / 3600.0
    except (TypeError, ValueError):
        return None
    return None


def find_budget(node: Any) -> Any:
    """First `budget` mapping found anywhere in a loaded specification."""
    if isinstance(node, dict):
        if isinstance(node.get("budget"), dict):
            return node["budget"]
        for v in node.values():
            found = find_budget(v)
            if found is not None:
                return found
    elif isinstance(node, list):
        for v in node:
            found = find_budget(v)
            if found is not None:
                return found
    return None


def contract_hours(root: Path, exp_id: str, default: float) -> tuple[float, bool]:
    """(hours, declared) for one experiment."""
    spec = root / "experiments" / exp_id / "specification.yaml"
    body = kpis._load(spec, "experiment") if spec.exists() else None
    hours = declared_hours(find_budget(body)) if body else None
    return (hours, True) if hours is not None else (default, False)


def compute(root: Path = REPO, capacity_file: Path | None = None,
            dispatching: int | None = None) -> dict[str, Any]:
    cap = load_capacity(capacity_file or root / "orchestration" / "execution-capacity.yaml")
    default = cap["default_contract_cpu_hours"]
    backlog = kpis.approved_unrun(root)
    demand, declared, contracts = 0.0, 0, 0
    for ids in backlog.values():
        for exp_id in ids:
            hours, was_declared = contract_hours(root, exp_id, default)
            demand += hours
            contracts += 1
            declared += was_declared
    capacity = sum(r["cpu_hours_per_week"] for r in cap["routes"])
    util = demand / capacity if capacity else None
    n = "<N>" if dispatching is None else str(dispatching)
    sentence = (f"capacity {capacity:.0f} h, demand {demand:.1f} h, "
                f"dispatching {n} / recording why not")
    return {
        "routes": cap["routes"],
        "capacity_hours_per_week": capacity,
        "demand_hours": round(demand, 2),
        "utilisation": None if util is None else round(util, 4),
        "approved_unrun_contracts": contracts,
        "contracts_with_declared_budget": declared,
        "default_contract_cpu_hours": default,
        "numbers_status": ("unverified" if any(r["number_status"] == "unverified"
                                               for r in cap["routes"]) else "verified"),
        "sentence": sentence,
    }


def render(r: dict[str, Any]) -> str:
    lines = [f"{'route':<24}{'h/week':>10}  {'status':<11}last_verified"]
    for x in r["routes"]:
        lines.append(f"{x['name']:<24}{x['cpu_hours_per_week']:>10.0f}  "
                     f"{x['number_status']:<11}{x['last_verified']}")
    util = r["utilisation"]
    lines += [
        f"{'capacity (total)':<24}{r['capacity_hours_per_week']:>10.0f}",
        f"{'demand (approved-unrun)':<24}{r['demand_hours']:>10.1f}  "
        f"{r['approved_unrun_contracts']} contracts, "
        f"{r['contracts_with_declared_budget']} with a declared budget, "
        f"rest at {r['default_contract_cpu_hours']} h",
        f"{'utilisation':<24}"
        f"{'n/a' if util is None else format(util, '.1%'):>10}  "
        f"(numbers {r['numbers_status']})",
        "",
        "Copy into the wake receipt (fill N):",
        r["sentence"],
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dispatching", type=int, default=None,
                    help="N, the runs dispatched this wake (fills the sentence)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--repo-root", type=Path, default=REPO)
    args = ap.parse_args(argv)
    r = compute(args.repo_root, dispatching=args.dispatching)
    print(json.dumps(r, indent=2) if args.json else render(r))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
