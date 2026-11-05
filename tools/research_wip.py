#!/usr/bin/env python3
"""Measure lab pull-request WIP and admit only policy-compatible actions.

This is an operational admission signal, not research evidence.  It counts
open GitHub pull requests without interpreting their scientific status.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Callable


SCHEMA = "lab.research-wip/v1"
MODES = ("off", "advisory", "enforce")


class PolicyError(ValueError):
    """The committed WIP policy is malformed."""


def load_policy(path: Path) -> dict:
    try:
        policy = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PolicyError(f"cannot read WIP policy {path}: {exc}") from exc
    if policy.get("schema") != SCHEMA:
        raise PolicyError(f"WIP policy schema must be {SCHEMA}")
    org = policy.get("github_org")
    repos = policy.get("repositories")
    total = policy.get("total_open_pr_cap")
    if not isinstance(org, str) or not org:
        raise PolicyError("github_org must be a non-empty string")
    if not isinstance(repos, dict) or not repos:
        raise PolicyError("repositories must be a non-empty object")
    if not isinstance(total, int) or isinstance(total, bool) or total < 1:
        raise PolicyError("total_open_pr_cap must be a positive integer")
    for name, cap in repos.items():
        if not isinstance(name, str) or not name:
            raise PolicyError("repository names must be non-empty strings")
        if not isinstance(cap, int) or isinstance(cap, bool) or cap < 1:
            raise PolicyError(f"repository cap for {name} must be a positive integer")
    expanding = policy.get("expanding_actions")
    draining = policy.get("draining_actions")
    if not isinstance(expanding, list) or not all(isinstance(x, str) for x in expanding):
        raise PolicyError("expanding_actions must be a string array")
    if not isinstance(draining, list) or not all(isinstance(x, str) for x in draining):
        raise PolicyError("draining_actions must be a string array")
    if set(expanding) & set(draining):
        raise PolicyError("expanding_actions and draining_actions must be disjoint")
    refresh = policy.get("refresh_seconds", 300)
    if not isinstance(refresh, int) or isinstance(refresh, bool) or refresh < 1:
        raise PolicyError("refresh_seconds must be a positive integer")
    return policy


def _gh_count(repo: str) -> int:
    result = subprocess.run(
        ["gh", "pr", "list", "--repo", repo, "--state", "open",
         "--limit", "1000", "--json", "number"],
        text=True, capture_output=True, check=False,
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).strip().splitlines()
        suffix = f": {detail[0]}" if detail else ""
        raise RuntimeError(f"gh pr list failed for {repo} (exit {result.returncode}){suffix}")
    try:
        rows = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"gh pr list returned invalid JSON for {repo}") from exc
    if not isinstance(rows, list):
        raise RuntimeError(f"gh pr list returned a non-list for {repo}")
    if len(rows) == 1000:
        raise RuntimeError(f"open PR count for {repo} reached the 1000-row safety limit")
    return len(rows)


def measure(policy: dict, *, counter: Callable[[str], int] = _gh_count) -> dict:
    """Return exact observed counts, or one explicit unavailable report."""
    org = policy["github_org"]
    repositories: dict[str, dict[str, int]] = {}
    try:
        for name, cap in policy["repositories"].items():
            count = counter(f"{org}/{name}")
            repositories[name] = {
                "open_pull_requests": count,
                "cap": cap,
                "over_by": max(0, count - cap),
            }
    except (OSError, RuntimeError) as exc:
        return {
            "schema": SCHEMA,
            "available": False,
            "source": "github_cli",
            "error": f"{type(exc).__name__}: {exc}",
            "repositories": repositories,
            "total": None,
            "total_cap": policy["total_open_pr_cap"],
            "violations": ["measurement_unavailable"],
        }
    total = sum(row["open_pull_requests"] for row in repositories.values())
    violations = [
        f"{name}:open={row['open_pull_requests']}>cap={row['cap']}"
        for name, row in repositories.items() if row["over_by"]
    ]
    if total > policy["total_open_pr_cap"]:
        violations.append(f"total:open={total}>cap={policy['total_open_pr_cap']}")
    return {
        "schema": SCHEMA,
        "available": True,
        "source": "github_cli",
        "repositories": repositories,
        "total": total,
        "total_cap": policy["total_open_pr_cap"],
        "violations": violations,
    }


def decide(policy: dict, report: dict, *, action: str, mode: str) -> dict:
    if mode not in MODES:
        raise PolicyError(f"mode must be one of {', '.join(MODES)}")
    violations = list(report.get("violations") or [])
    draining = action in set(policy["draining_actions"])
    if mode == "off":
        allowed, reason = True, "WIP admission disabled"
    elif mode == "advisory":
        allowed = True
        reason = "WIP within cap" if not violations else "WIP violation is advisory"
    elif not violations:
        allowed, reason = True, "WIP within cap"
    elif draining:
        allowed, reason = True, "repair/review remains admitted while WIP is over cap"
    else:
        allowed, reason = False, "action would expand work while WIP is over cap or unavailable"
    return {
        "allowed": allowed,
        "mode": mode,
        "action": action,
        "reason": reason,
        "violations": violations,
        "measurement_available": bool(report.get("available")),
    }


class Gate:
    """Cached admission callable for a long-running campaign supervisor."""

    def __init__(self, policy_path: Path, *, mode: str,
                 clock: Callable[[], float] = time.monotonic,
                 counter: Callable[[str], int] = _gh_count):
        self.policy_path = policy_path
        self.policy = load_policy(policy_path)
        if mode not in MODES:
            raise PolicyError(f"mode must be one of {', '.join(MODES)}")
        self.mode = mode
        self.clock = clock
        self.counter = counter
        self._measured_at: float | None = None
        self._report: dict | None = None

    def report(self, *, refresh: bool = False) -> dict:
        if self.mode == "off":
            return {"schema": SCHEMA, "available": None, "source": "disabled",
                    "repositories": {}, "total": None,
                    "total_cap": self.policy["total_open_pr_cap"], "violations": []}
        now = self.clock()
        expired = (self._measured_at is None or
                   now - self._measured_at >= self.policy.get("refresh_seconds", 300))
        if refresh or expired or self._report is None:
            self._report = measure(self.policy, counter=self.counter)
            self._measured_at = now
        return self._report

    def __call__(self, action) -> dict:
        kind = action.kind if hasattr(action, "kind") else str(action)
        report = self.report()
        decision = decide(self.policy, report, action=kind, mode=self.mode)
        return {**decision, "report": report}

    def allowed_kinds(self) -> set[str] | None:
        """Return a selector hint; final admission still checks each action."""
        report = self.report()
        if self.mode == "enforce" and report.get("violations"):
            return set(self.policy["draining_actions"])
        return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path,
                        default=Path("docs/research-wip-policy.json"))
    parser.add_argument("--mode", choices=MODES, default="advisory")
    parser.add_argument("--action", default="portfolio")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not shutil.which("gh") and args.mode != "off":
        report = {"schema": SCHEMA, "available": False, "source": "github_cli",
                  "error": "gh CLI unavailable", "repositories": {}, "total": None,
                  "total_cap": None, "violations": ["measurement_unavailable"]}
        try:
            policy = load_policy(args.policy)
            report["total_cap"] = policy["total_open_pr_cap"]
            decision = decide(policy, report, action=args.action, mode=args.mode)
        except PolicyError as exc:
            print(json.dumps({"error": str(exc)}, sort_keys=True))
            return 2
    else:
        try:
            gate = Gate(args.policy, mode=args.mode)
            report = gate.report(refresh=True)
            decision = gate(args.action)
        except PolicyError as exc:
            print(json.dumps({"error": str(exc)}, sort_keys=True))
            return 2
    print(json.dumps({"decision": decision, "report": report}, indent=2, sort_keys=True))
    return 0 if decision["allowed"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
