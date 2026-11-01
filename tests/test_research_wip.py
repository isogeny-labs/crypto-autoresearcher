from __future__ import annotations

import json
from pathlib import Path

from tools import research_wip


def _policy(path: Path) -> Path:
    path.write_text(json.dumps({
        "schema": research_wip.SCHEMA,
        "github_org": "example",
        "total_open_pr_cap": 4,
        "repositories": {"crypto": 2, "cryptanalysis": 2},
        "expanding_actions": ["run", "design", "prepare", "portfolio"],
        "draining_actions": ["repair", "review"],
        "refresh_seconds": 300,
    }), encoding="utf-8")
    return path


def test_measurement_reports_repository_and_aggregate_violations(tmp_path: Path) -> None:
    policy = research_wip.load_policy(_policy(tmp_path / "policy.json"))
    counts = {"example/crypto": 3, "example/cryptanalysis": 2}
    report = research_wip.measure(policy, counter=counts.__getitem__)

    assert report["available"] is True
    assert report["total"] == 5
    assert report["repositories"]["crypto"]["over_by"] == 1
    assert report["violations"] == [
        "crypto:open=3>cap=2", "total:open=5>cap=4"]


def test_enforcement_filters_expansion_but_keeps_drain_actions(tmp_path: Path) -> None:
    policy = research_wip.load_policy(_policy(tmp_path / "policy.json"))
    report = research_wip.measure(policy, counter=lambda _repo: 3)

    assert research_wip.decide(
        policy, report, action="design", mode="enforce")["allowed"] is False
    assert research_wip.decide(
        policy, report, action="review", mode="enforce")["allowed"] is True
    assert research_wip.decide(
        policy, report, action="design", mode="advisory")["allowed"] is True


def test_unavailable_measurement_fails_closed_only_for_expansion(tmp_path: Path) -> None:
    policy = research_wip.load_policy(_policy(tmp_path / "policy.json"))

    def unavailable(_repo: str) -> int:
        raise RuntimeError("offline")

    report = research_wip.measure(policy, counter=unavailable)
    assert report["available"] is False
    assert report["violations"] == ["measurement_unavailable"]
    assert research_wip.decide(
        policy, report, action="portfolio", mode="enforce")["allowed"] is False
    assert research_wip.decide(
        policy, report, action="repair", mode="enforce")["allowed"] is True


def test_gate_caches_measurement_until_policy_ttl(tmp_path: Path) -> None:
    calls: list[str] = []
    now = [100.0]

    def count(repo: str) -> int:
        calls.append(repo)
        return 1

    gate = research_wip.Gate(_policy(tmp_path / "policy.json"), mode="enforce",
                             counter=count, clock=lambda: now[0])
    assert gate("design")["allowed"] is True
    assert gate("portfolio")["allowed"] is True
    assert len(calls) == 2

    now[0] += 301
    assert gate("run")["allowed"] is True
    assert len(calls) == 4
