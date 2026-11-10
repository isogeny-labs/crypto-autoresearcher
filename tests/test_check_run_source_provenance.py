"""check_run_source_provenance: supervisor plan-pinned runs (sheriff case
SHF-20261106-a114e7, ICV-2). The nine ICPERF manifests recorded the hashed
plan sources in run.environment.source_sha256 but no code.source, so --strict
reported them unpinned; units launched since the supervisor records
sources_committed count as plan-pinned."""
from __future__ import annotations

import os
from pathlib import Path
import sys

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import check_run_source_provenance as provenance  # noqa: E402

DIGEST = "a" * 64


def test_plan_pinned_needs_hashed_sources_and_the_committed_flag():
    assert provenance.plan_pinned({"source_sha256": {"run.py": DIGEST}, "sources_committed": True})
    for environment in ({"source_sha256": {"run.py": DIGEST}},
                        {"source_sha256": {"run.py": DIGEST}, "sources_committed": "true"},
                        {"source_sha256": {}, "sources_committed": True},
                        {"source_sha256": {"run.py": "short"}, "sources_committed": True},
                        {"source_sha256": {"run.py": "A" * 64}, "sources_committed": True},
                        None, "environment.json"):
        assert not provenance.plan_pinned(environment), environment


def test_audit_counts_plan_pinned_runs_separately(tmp_path, monkeypatch):
    def manifest(run_id, environment):
        path = tmp_path / "experiments" / "EXP-P-1" / "runs" / run_id / "manifest.yaml"
        path.parent.mkdir(parents=True)
        path.write_text(yaml.safe_dump({"run": {"id": run_id, "code": {"dirty": False},
                                                "environment": environment}}))
    manifest("RUN-P-1", {"source_sha256": {"run.py": DIGEST}, "sources_committed": True})
    manifest("RUN-P-2", {"source_sha256": {"run.py": DIGEST}})
    monkeypatch.setattr(provenance, "REPO", str(tmp_path))
    pinned, unpinned, unreadable = provenance.audit(None, None)
    assert pinned == [("RUN-P-1", 1, "plan")]
    assert [run_id for run_id, _, _ in unpinned] == ["RUN-P-2"] and unreadable == []


def test_the_supervisor_records_sources_committed_in_environment_json():
    text = (REPO / "tools/experiment_execution.py").read_text()
    assert '"sources_committed": True' in text
