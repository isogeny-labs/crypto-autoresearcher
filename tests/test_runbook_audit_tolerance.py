"""tools/runbook.py audit: float tolerance and interpreter parity
(TASK-20261029-1bcf80, DEC-20261029-5554ee).

RBS-PFDR-bb0d26 was recorded under CPython 3.11 and replayed under 3.13. Its
two calibration floats differed by about 400 ulps, because CPython 3.12 made
builtin sum() of floats compensated. Every other leaf replayed equal. These
tests rebuild that drift in a synthetic EXAMPLE-* session in a temporary
directory. The driver sums 45 floats, and the drift comes either from the real
interpreters (when python3.11 and a 3.12+ python3 are both installed) or from
an environment switch that picks a strict left fold (3.11 semantics) or a
Neumaier sum (3.12+ semantics). The data give a 386-ulp difference in the mean.

The contract under test: exact equality stays the default and stays a finding;
a declared or audit-time tolerance turns a float-only drift into
matched_within_tolerance, never matched; a non-float difference is a mismatch
under any tolerance; the replay interpreter is recorded and a version
difference is an environment_drift note; a pinned interpreter that differs
makes the unit not_covered. The recorded interpreter is read from the
canonical places real manifests use (DEC-20261105-6e2616 NA-1), and a unit
that records none is an explicit interpreter_parity: unknown note.
"""
from __future__ import annotations

import functools
import hashlib
import json
import operator
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import runbook as rb  # noqa: E402

BASE = "examples/runbooks/float-drift"
RUNBOOK = f"{BASE}/runbook.yaml"
SESSION = f"{BASE}/runbook-sessions/RBS-FLT-0a1b2c"
TOLERANCE = {"rel_tol": 1e-9, "abs_tol": 1e-12}

# The PFDR pair quoted in DEC-20261029-5554ee facts_relied_on.summary_diff.
PFDR_RECORDED = -0.26757013662385903
PFDR_REPLAY = -0.26757013662383594

DRIVER = '''#!/usr/bin/env python3
"""Mean of 45 floats whose large terms cancel. RUNBOOK_TEST_SUM picks the
summation: left_fold (CPython 3.11 sum), compensated (CPython 3.12+ sum), or
unset for the running interpreter's builtin sum."""
import argparse, functools, json, math, operator, os, platform, random
from pathlib import Path


def neumaier(xs):
    s = c = 0.0
    for x in xs:
        t = s + x
        c += (s - t) + x if abs(s) >= abs(x) else (x - t) + s
        s = t
    return s + c


parser = argparse.ArgumentParser()
parser.add_argument("--trial-id", required=True)
parser.add_argument("--seed", type=int, required=True)
parser.add_argument("--run-dir", required=True)
args = parser.parse_args()
r = random.Random(args.seed)
xs = [r.gauss(0, 1) * 10 ** r.randint(0, 3) for _ in range(44)]
xs.append(-math.fsum(xs) - 12.0)
mode = os.environ.get("RUNBOOK_TEST_SUM")
total = (functools.reduce(operator.add, xs, 0.0) if mode == "left_fold"
         else neumaier(xs) if mode == "compensated" else sum(xs))
label = os.environ.get("RUNBOOK_TEST_LABEL", "calibration")
out = Path(args.run_dir)
out.mkdir(parents=True, exist_ok=True)
scale = float(os.environ.get("RUNBOOK_TEST_SCALE", "1"))
(out / "raw-result.json").write_text(json.dumps({
    "schema": "example.float_drift.result.v1", "trial_id": args.trial_id, "seed": args.seed,
    "n": len(xs), "mean": scale * total / len(xs), "positive": sum(1 for x in xs if x > 0),
    "label": label}, sort_keys=True) + "\\n")
version = os.environ.get("RUNBOOK_TEST_PYTHON_VERSION") or platform.python_version()
shape = os.environ.get("RUNBOOK_TEST_MANIFEST_SHAPE")
if shape == "icperf":
    # The shape of EXP-ICPERF-284bc4 / 283a70 run manifests: /run/environment
    # names python and version, never python_version, and environment.json
    # carries the full sys.version string.
    (out / "manifest.yaml").write_text(json.dumps({"run": {"id": "RUN-FLT", "environment": {
        "file": "environment.json", "implementation": "CPython", "version": version,
        "executable": "/opt/py/bin/python3", "python": version}}}, indent=2) + "\\n")
    (out / "environment.json").write_text(json.dumps({
        "platform": "linux", "python": version + " (main, Oct 14 2026, 01:05:33) [Clang 23.1.3 ]"}) + "\\n")
elif shape == "none":
    (out / "manifest.yaml").write_text(json.dumps({"run": {"id": "RUN-FLT", "status": "completed"}}) + "\\n")
else:
    (out / "manifest.yaml").write_text(f"run:\\n  environment:\\n    python_version: {version}\\n")
'''

CHECK = '''#!/usr/bin/env python3
import json, sys
from pathlib import Path
doc = json.loads((Path(sys.argv[1]) / "raw-result.json").read_text())
sys.exit(0 if doc["n"] == 45 and isinstance(doc["mean"], float) else 1)
'''


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ulps(a: float, b: float) -> int:
    ia, ib = (struct.unpack("<q", struct.pack("<d", x))[0] for x in (a, b))
    return abs(ia - ib)


def build(root: Path, *, tolerance: dict | None = None, python_pin: str | None = None) -> Path:
    base = root / BASE
    base.mkdir(parents=True)
    (base / "driver.py").write_text(DRIVER)
    (base / "check.py").write_text(CHECK)
    (base / "README.md").write_text("Synthetic float-drift session for the runbook audit tests.\n")
    sources = {f"{BASE}/{n}": sha(base / n) for n in ("driver.py", "check.py")}
    trials = []
    for index, trial_id in enumerate(("t01", "t02"), 1):
        trials.append({
            "id": trial_id, "run_id": f"RUN-FLT-00000{index}",
            "argv": ["python3", f"{BASE}/driver.py", "--trial-id", trial_id, "--seed", "2",
                     "--run-dir", "{run_dir}"],
            "check_argv": ["python3", f"{BASE}/check.py", "{run_dir}"],
            "artifacts": ["manifest.yaml", "raw-result.json"], "depends_on": [],
            "memory_mb": 512, "watchdog_seconds": 60, "watchdog_reason": "toy computation; a hang is a defect"})
    plan = {"schema": rb.PLAN_SCHEMA, "experiment_id": "EXAMPLE-float-drift", "frozen": True,
            "queue": None, "task_id": None, "approved_by": "example: no approval",
            "specification": f"{BASE}/README.md", "specification_sha256": sha(base / "README.md"),
            "source_sha256": sources, "trials": trials}
    (base / "trial-plan.json").write_text(json.dumps(plan, indent=1, sort_keys=True) + "\n")
    toleranced = {"file": "raw-result.json", "pointers": ["/mean"]}
    if tolerance is not None:
        toleranced["tolerance"] = tolerance
    environment = {"programs": ["python3"]}
    if python_pin:
        environment["python"] = python_pin
    doc = {
        "schema": rb.SCHEMA, "experiment_id": "EXAMPLE-float-drift", "session_id": "RBS-FLT-0a1b2c",
        "title": "Compute the mean of the fixed float sample for each trial",
        "purpose": "Conformance fixture for toleranced replay comparison and interpreter parity.",
        "executor_tier": "mechanical", "approval": {"mode": "example"},
        "binds": [{"path": f"{BASE}/{n}", "sha256": sha(base / n)}
                  for n in ("README.md", "trial-plan.json", "driver.py", "check.py")],
        "environment": environment,
        "steps": [{
            "id": "S01-mean", "kind": "trials",
            "title": "Run both trials of the frozen plan and record each unit",
            "explain": "Runs driver.py then check.py for every trial in trial-plan.json.",
            "plan": f"{BASE}/trial-plan.json", "engine": "local", "timeout_seconds": 120,
            "validity": {"files": [
                {"path": "manifest.yaml"},
                {"path": "raw-result.json", "json": True,
                 "assertions": [{"pointer": "/trial_id", "equals": "{trial_id}"},
                                {"pointer": "/n", "equals": 45}]}]},
            "replay": {"mode": "fields", "sample": 2, "compare": [
                toleranced,
                {"file": "raw-result.json", "pointers": ["/n", "/positive", "/label", "/seed"]}]},
        }],
    }
    (base / "runbook.yaml").write_text(yaml.safe_dump(doc, sort_keys=False))
    return root


def record(root: Path, monkeypatch, **env: str) -> None:
    with monkeypatch.context() as patch:
        for key, value in env.items():
            patch.setenv(key, value)
        result = rb.Runner(rb.load_runbook(root, RUNBOOK)).run()
    assert result["status"] == "completed", result


def audit(root: Path, monkeypatch, *, env: dict | None = None, **kwargs):
    with monkeypatch.context() as patch:
        for key in ("RUNBOOK_TEST_SUM", "RUNBOOK_TEST_LABEL", "RUNBOOK_TEST_PYTHON_VERSION",
                    "RUNBOOK_TEST_MANIFEST_SHAPE", "RUNBOOK_TEST_SCALE"):
            patch.delenv(key, raising=False)
        for key, value in (env or {}).items():
            patch.setenv(key, value)
        report, target = rb.audit(root, root / SESSION, samples=99, nonce="5e", auditor="test", **kwargs)
    written = json.loads((target / "audit.json").read_text())
    written["_target"] = target
    return report, written


def mean_row(replay: dict) -> dict:
    return next(c for c in replay["compared"] if c["pointer"] == "/mean")


# ---------------------------------------------------------------------------
# The fixture reproduces the drift
# ---------------------------------------------------------------------------

def _drift_pair() -> tuple[float, float]:
    import random
    import math
    r = random.Random(2)
    xs = [r.gauss(0, 1) * 10 ** r.randint(0, 3) for _ in range(44)]
    xs.append(-math.fsum(xs) - 12.0)
    s = c = 0.0
    for x in xs:
        t = s + x
        c += (s - t) + x if abs(s) >= abs(x) else (x - t) + s
        s = t
    return functools.reduce(operator.add, xs, 0.0) / len(xs), (s + c) / len(xs)


def test_the_fixture_reproduces_a_sum_drift_of_about_400_ulps() -> None:
    left, compensated = _drift_pair()
    assert 300 <= ulps(left, compensated) <= 500
    assert abs(left - compensated) / abs(left) < 1e-12
    if sys.version_info >= (3, 12):
        # This interpreter's builtin sum is the compensated one.
        assert _drift_pair()[1] == compensated
    assert 300 <= ulps(PFDR_RECORDED, PFDR_REPLAY) <= 500


def test_the_pfdr_pair_fails_exact_compare_and_passes_under_the_ruled_tolerance() -> None:
    exact = rb.compare_tolerant({"mean": PFDR_RECORDED, "n": 44}, {"mean": PFDR_REPLAY, "n": 44}, None)
    assert exact["result"] == "mismatch" and exact["float_leaves_differing"] == 1
    toleranced = rb.compare_tolerant({"mean": PFDR_RECORDED, "n": 44}, {"mean": PFDR_REPLAY, "n": 44},
                                     TOLERANCE)
    assert toleranced["result"] == "within_tolerance"
    assert toleranced["max_abs_diff"] == pytest.approx(abs(PFDR_RECORDED - PFDR_REPLAY))
    assert 8e-14 < toleranced["max_rel_diff"] < 9e-14


@pytest.mark.parametrize("recorded, replay", [
    ({"n": 44, "x": 1.0}, {"n": 45, "x": 1.0}),                 # an integer
    ({"c": "null", "x": 1.0}, {"c": "invalid", "x": 1.0}),      # a string
    ({"pass": True}, {"pass": False}),                          # a flag
    ({"v": None}, {"v": 0.0}),                                  # null
    ({"x": 1.0}, {"x": 1.0, "y": 2.0}),                         # a key set
    ([1.0, 2.0], [1.0, 2.0, 3.0]),                              # a list length
    ([1.0, 2.0], [2.0, 1.0]),                                   # list order (beyond tolerance)
    ({"k": 3}, {"k": 3.0000000000001}),                         # int versus float
    ({"x": 1.0}, {"x": 1.1}),                                   # a float beyond tolerance
])
def test_a_non_float_or_out_of_tolerance_difference_is_a_mismatch_under_any_tolerance(recorded, replay) -> None:
    assert rb.compare_tolerant(recorded, replay, {"rel_tol": 1e-3, "abs_tol": 1e-3})["result"] == "mismatch"


def test_exact_compare_is_unchanged_without_a_tolerance() -> None:
    assert rb.compare_tolerant(1, 1, None)["result"] == "equal"
    assert rb.compare_tolerant(True, 1, None)["result"] == "mismatch"
    assert rb.compare_tolerant(0.1 + 0.2, 0.3, None)["result"] == "mismatch"
    assert rb.compare_tolerant(0.1 + 0.2, 0.3, TOLERANCE)["result"] == "within_tolerance"


@pytest.mark.parametrize("value", [{}, {"rel": 1e-9}, {"rel_tol": -1.0}, {"rel_tol": True},
                                   {"abs_tol": "1e-12"}, "rel_tol", "rel_tol=x"])
def test_a_malformed_tolerance_is_refused(value) -> None:
    with pytest.raises(rb.RunbookError):
        rb.parse_tolerance(value)
    assert rb.parse_tolerance("rel_tol=1e-9,abs_tol=1e-12") == TOLERANCE


# ---------------------------------------------------------------------------
# Lint validates a declared tolerance
# ---------------------------------------------------------------------------

def test_lint_accepts_a_declared_tolerance_and_refuses_a_bad_one(tmp_path) -> None:
    good = build(tmp_path / "good", tolerance=TOLERANCE)
    assert rb.lint(rb.load_runbook(good, RUNBOOK)) == []
    bad = build(tmp_path / "bad", tolerance={"rel_tol": -1})
    assert any("tolerance" in f for f in rb.lint(rb.load_runbook(bad, RUNBOOK)))
    typo = build(tmp_path / "typo", tolerance={"relative": 1e-9})
    assert any("tolerance" in f for f in rb.lint(rb.load_runbook(typo, RUNBOOK)))


def test_lint_refuses_a_tolerance_on_a_bytes_replay(tmp_path) -> None:
    root = build(tmp_path)
    path = root / RUNBOOK
    doc = yaml.safe_load(path.read_text())
    doc["steps"][0]["replay"] = {"mode": "bytes", "compare": [{"file": "raw-result.json", "tolerance": TOLERANCE}]}
    path.write_text(yaml.safe_dump(doc, sort_keys=False))
    assert any("replay.compare[0]: keys are" in f for f in rb.lint(rb.load_runbook(root, RUNBOOK)))


# ---------------------------------------------------------------------------
# Audit: the drift end to end
# ---------------------------------------------------------------------------

def test_float_drift_without_tolerance_is_a_mismatch_finding(tmp_path, monkeypatch) -> None:
    root = build(tmp_path)
    record(root, monkeypatch, RUNBOOK_TEST_SUM="left_fold")
    report, written = audit(root, monkeypatch, env={"RUNBOOK_TEST_SUM": "compensated"})
    assert report["verdict"] == "flagged" and written["verdict"] == "flagged"
    assert written["schema"] == "crypto.autoresearch.runbook_audit.v2"
    assert all(r["result"] == "mismatch" and not r["matched"] for r in report["replays"])
    assert any("/mean" in f for f in report["findings"])
    row = mean_row(report["replays"][0])
    assert row["result"] == "mismatch" and "tolerance" not in row
    assert 300 <= ulps(*_drift_pair()) <= 500 and 0 < row["max_rel_diff"] < 1e-12
    assert report["float_tolerance"] is None


def test_float_drift_under_a_declared_tolerance_is_matched_within_tolerance(tmp_path, monkeypatch) -> None:
    root = build(tmp_path, tolerance=TOLERANCE)
    record(root, monkeypatch, RUNBOOK_TEST_SUM="left_fold")
    report, written = audit(root, monkeypatch, env={"RUNBOOK_TEST_SUM": "compensated"})
    assert report["verdict"] == "clean_within_tolerance", report["findings"]
    assert written["replay_results"] == {"matched": 0, "matched_within_tolerance": 2, "mismatch": 0}
    for replay in report["replays"]:
        assert replay["result"] == "matched_within_tolerance" and replay["matched"] is False
        row = mean_row(replay)
        assert row["result"] == "within_tolerance"
        assert row["tolerance"] == {"source": "runbook", **TOLERANCE}
        assert row["max_abs_diff"] > 0 and row["max_rel_diff"] < 1e-12
        exact = [c for c in replay["compared"] if c["pointer"] != "/mean"]
        assert exact and all(c["result"] == "equal" and "tolerance" not in c for c in exact)


def test_an_identical_replay_under_a_tolerance_is_matched(tmp_path, monkeypatch) -> None:
    root = build(tmp_path, tolerance=TOLERANCE)
    record(root, monkeypatch, RUNBOOK_TEST_SUM="left_fold")
    report, _ = audit(root, monkeypatch, env={"RUNBOOK_TEST_SUM": "left_fold"})
    assert report["verdict"] == "clean"
    assert all(r["result"] == "matched" and r["matched"] for r in report["replays"])


def test_the_audit_time_tolerance_is_recorded_and_applies_to_a_frozen_runbook(tmp_path, monkeypatch) -> None:
    root = build(tmp_path)
    record(root, monkeypatch, RUNBOOK_TEST_SUM="left_fold")
    report, written = audit(root, monkeypatch, env={"RUNBOOK_TEST_SUM": "compensated"},
                            float_tolerance="rel_tol=1e-9,abs_tol=1e-12")
    assert report["verdict"] == "clean_within_tolerance", report["findings"]
    assert written["float_tolerance"] == {"source": "audit_option", **TOLERANCE}
    assert all(r["result"] == "matched_within_tolerance" for r in report["replays"])
    assert mean_row(report["replays"][0])["tolerance"]["source"] == "audit_option"


def test_a_non_float_difference_is_a_mismatch_even_under_a_tolerance(tmp_path, monkeypatch) -> None:
    root = build(tmp_path, tolerance=TOLERANCE)
    record(root, monkeypatch, RUNBOOK_TEST_SUM="left_fold")
    report, _ = audit(root, monkeypatch, env={"RUNBOOK_TEST_SUM": "compensated", "RUNBOOK_TEST_LABEL": "other"},
                      float_tolerance=TOLERANCE)
    assert report["verdict"] == "flagged"
    assert all(r["result"] == "mismatch" for r in report["replays"])
    assert any("/label" in f for f in report["findings"])
    assert not any("/mean" in f for f in report["findings"])


def test_the_cli_takes_the_float_tolerance(tmp_path, monkeypatch) -> None:
    root = build(tmp_path)
    record(root, monkeypatch, RUNBOOK_TEST_SUM="left_fold")
    env = {k: v for k, v in os.environ.items() if not k.startswith("RUNBOOK_TEST_")}
    env["RUNBOOK_TEST_SUM"] = "compensated"
    tool = [sys.executable, str(REPO / "tools/runbook.py"), "--repo", str(root), "audit", SESSION,
            "--nonce", "aa", "--samples", "9"]
    exact = subprocess.run(tool, capture_output=True, text=True, env=env)
    assert exact.returncode == 1, exact.stderr
    toleranced = subprocess.run([*tool, "--float-tolerance", "rel_tol=1e-9,abs_tol=1e-12"],
                                capture_output=True, text=True, env=env)
    assert toleranced.returncode == 0, toleranced.stdout + toleranced.stderr
    out = json.loads(toleranced.stdout)
    assert out["replay_results"]["matched_within_tolerance"] == 2


# ---------------------------------------------------------------------------
# Interpreter parity
# ---------------------------------------------------------------------------

def test_the_replay_interpreter_is_recorded_and_a_difference_is_an_environment_drift_note(tmp_path, monkeypatch) -> None:
    root = build(tmp_path, tolerance=TOLERANCE)
    record(root, monkeypatch, RUNBOOK_TEST_SUM="left_fold", RUNBOOK_TEST_PYTHON_VERSION="3.11.15")
    report, written = audit(root, monkeypatch, env={"RUNBOOK_TEST_SUM": "compensated"})
    here = ".".join(str(n) for n in sys.version_info[:3])
    for replay in report["replays"]:
        assert replay["interpreter"]["version"] and replay["interpreter"]["executable"]
        assert replay["interpreter"]["recorded_python_version"] == "3.11.15"
        if replay["interpreter"]["python_version"] != "3.11.15":
            drift = replay["environment_drift"]
            assert drift["recorded_python_version"] == "3.11.15"
            assert drift["replay_python_version"] == replay["interpreter"]["python_version"]
        # The note sits beside the result and never replaces it.
        assert replay["result"] == "matched_within_tolerance"
    assert written["audit_interpreter"]["version"] == sys.version
    assert written["replay_interpreters"] and written["replay_interpreters"][0]["program"] == "python3"
    if here != "3.11.15":
        assert len(written["environment_drift"]) == 2
        assert {d["recorded_python_version"] for d in written["environment_drift"]} == {"3.11.15"}


def test_no_environment_drift_when_the_versions_agree(tmp_path, monkeypatch) -> None:
    root = build(tmp_path)
    record(root, monkeypatch)
    report, _ = audit(root, monkeypatch)
    assert report["environment_drift"] == []
    assert report["verdict"] == "clean"
    assert all(r["result"] == "matched" and "environment_drift" not in r for r in report["replays"])


def test_a_pinned_interpreter_that_differs_is_not_covered_and_not_replayed(tmp_path, monkeypatch) -> None:
    other = "3.99"
    root = build(tmp_path, python_pin=other)
    # Record under the pin by faking the preflight's probe, then audit honestly.
    real_run = rb.subprocess.run

    def probe(argv, *args, **kwargs):
        if argv[:2] == ["python3", "-c"] and "version_info" in argv[2]:
            return subprocess.CompletedProcess(argv, 0, stdout=f"{other}\n", stderr="")
        return real_run(argv, *args, **kwargs)
    with monkeypatch.context() as patch:
        patch.setattr(rb.subprocess, "run", probe)
        record(root, monkeypatch)
    report, written = audit(root, monkeypatch)
    assert report["replays"] == []
    assert sum("pins python 3.99" in item and "not replayed" in item for item in report["not_covered"]) == 2
    assert not (written["_target"] / "replay").exists()


def _here() -> str:
    return ".".join(str(n) for n in sys.version_info[:3])


def test_icperf_shaped_manifests_record_the_interpreter_and_a_3_11_record_drifts(tmp_path, monkeypatch) -> None:
    """DEC-20261105-6e2616 NA-1: the ICPERF manifests write
    /run/environment/python, and the parity check must read it."""
    root = build(tmp_path, tolerance=TOLERANCE)
    record(root, monkeypatch, RUNBOOK_TEST_SUM="left_fold", RUNBOOK_TEST_PYTHON_VERSION="3.11.17",
           RUNBOOK_TEST_MANIFEST_SHAPE="icperf")
    report, written = audit(root, monkeypatch, env={"RUNBOOK_TEST_SUM": "compensated"})
    for replay in report["replays"]:
        assert replay["interpreter"]["recorded_python_version"] == "3.11.17"
        assert replay["interpreter"]["recorded_source"] == "manifest.yaml#/run/environment/python"
        assert replay["result"] == "matched_within_tolerance"
    assert written["notes"] == []
    if _here() != "3.11.17":
        assert written["interpreter_parity"] == {"match": 0, "mismatch": 2, "unknown": 0}
        assert len(written["environment_drift"]) == 2
        assert {d["recorded_python_version"] for d in written["environment_drift"]} == {"3.11.17"}
        assert {d["replay_python_version"] for d in written["environment_drift"]} == {_here()}


def test_environment_json_is_read_when_the_manifest_has_no_interpreter(tmp_path) -> None:
    run = tmp_path / "RUN-X"
    run.mkdir()
    (run / "manifest.yaml").write_text(json.dumps({"run": {"environment": {"file": "environment.json"}}}))
    (run / "environment.json").write_text(json.dumps({"python": "3.11.17 (main, Oct 14 2026) [Clang 23.1.3 ]"}))
    assert rb.recorded_interpreter(run) == {"python_version": "3.11.17", "source": "environment.json#/python"}
    # python_version stays first; a non-CPython "version" is not an interpreter.
    (run / "manifest.yaml").write_text(yaml.safe_dump({"run": {"environment": {
        "python_version": "3.13.18", "python": "3.11.17"}}}))
    assert rb.recorded_interpreter(run)["python_version"] == "3.13.18"
    (run / "manifest.yaml").write_text(yaml.safe_dump({"run": {"environment": {
        "implementation": "pari", "version": "2.15.4"}}}))
    (run / "environment.json").unlink()
    assert rb.recorded_interpreter(run)["python_version"] is None


@pytest.mark.parametrize("run_id", ["RUN-ICPERF-8e3acd", "RUN-ICPERF-2c627f", "RUN-ICPERF-850008"])
def test_the_committed_icperf_runs_record_cpython_3_11(run_id) -> None:
    run = REPO / "experiments/EXP-ICPERF-284bc4/runs" / run_id
    if not (run / "manifest.yaml").exists():
        pytest.skip("the ICPERF run records are not in this checkout")
    assert rb.recorded_interpreter(run)["python_version"] == "3.11.17"


def test_no_recorded_interpreter_is_an_explicit_unknown_note(tmp_path, monkeypatch) -> None:
    root = build(tmp_path)
    record(root, monkeypatch, RUNBOOK_TEST_MANIFEST_SHAPE="none")
    report, written = audit(root, monkeypatch)
    assert written["interpreter_parity"] == {"match": 0, "mismatch": 0, "unknown": 2}
    assert len(written["notes"]) == 2
    assert all("interpreter_parity: unknown" in n and "no recorded interpreter" in n for n in written["notes"])
    assert all(r["interpreter"]["interpreter_parity"] == "unknown"
               and r["interpreter"]["recorded_python_version"] is None for r in report["replays"])
    # Unknown is a note beside the result, never a drift and never a finding.
    assert written["environment_drift"] == [] and report["verdict"] == "clean"


def test_matching_versions_report_parity_match(tmp_path, monkeypatch) -> None:
    root = build(tmp_path)
    record(root, monkeypatch, RUNBOOK_TEST_MANIFEST_SHAPE="icperf")
    _, written = audit(root, monkeypatch)
    assert written["interpreter_parity"] == {"match": 2, "mismatch": 0, "unknown": 0}
    assert written["environment_drift"] == [] and written["notes"] == []


# ---------------------------------------------------------------------------
# The real interpreters, when both are installed
# ---------------------------------------------------------------------------

def _python311() -> str | None:
    path = shutil.which("python3.11")
    if not path or sys.version_info < (3, 12):
        return None
    probe = subprocess.run(["python3", "-c", "import sys;print(sys.version_info >= (3, 12))"],
                           capture_output=True, text=True)
    return path if probe.stdout.strip() == "True" else None


@pytest.mark.skipif(_python311() is None, reason="needs python3.11 and a 3.12+ python3")
def test_the_real_3_11_versus_3_13_drift(tmp_path, monkeypatch) -> None:
    root = build(tmp_path, tolerance=TOLERANCE)
    shim = tmp_path / "py311"
    shim.mkdir()
    (shim / "python3").symlink_to(_python311())
    record(root, monkeypatch, PATH=f"{shim}{os.pathsep}{os.environ['PATH']}")
    recorded = json.loads(next((root / SESSION).rglob("raw-result.json")).read_text())["mean"]
    report, written = audit(root, monkeypatch)
    replayed = json.loads(next(written["_target"].rglob("raw-result.json")).read_text())["mean"]
    assert recorded == _drift_pair()[0] and replayed == _drift_pair()[1]
    assert 300 <= ulps(recorded, replayed) <= 500
    assert report["verdict"] == "clean_within_tolerance", report["findings"]
    assert all(r["result"] == "matched_within_tolerance" for r in report["replays"])
    assert {d["recorded_python_version"][:5] for d in report["environment_drift"]} == {"3.11."}
    # Without the tolerance the same pair is a mismatch.
    assert rb.compare_tolerant(recorded, replayed, None)["result"] == "mismatch"


# ---------------------------------------------------------------------------
# SHF-20261106-a114e7 LGX-3: the tolerance is bounded, and a toleranced
# screen is never reported as an exact one
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value", [{"rel_tol": 0.5}, {"rel_tol": 1}, {"rel_tol": 1e6},
                                   {"abs_tol": 1e9}, {"abs_tol": 1e300}, {"rel_tol": 1.1e-9},
                                   {"abs_tol": 2e-12}, "rel_tol=1", "abs_tol=1e9",
                                   "rel_tol=1e-9,abs_tol=1e-6"])
def test_a_tolerance_above_the_documented_maximum_is_refused(value) -> None:
    with pytest.raises(rb.RunbookError, match="exceeds the maximum"):
        rb.parse_tolerance(value)


def test_the_documented_maximum_is_the_ruled_tolerance() -> None:
    assert rb.TOLERANCE_MAX == TOLERANCE
    assert rb.parse_tolerance(dict(rb.TOLERANCE_MAX)) == TOLERANCE
    assert rb.parse_tolerance({"rel_tol": 0, "abs_tol": 0}) == {"rel_tol": 0.0, "abs_tol": 0.0}


def test_why_the_cap_is_needed_a_1000x_change_is_within_rel_tol_1() -> None:
    """At rel_tol=1 math.isclose accepts any same-sign pair; the cap is what
    keeps such a tolerance out of a runbook and out of an audit."""
    assert rb.compare_tolerant(0.25, 250.0, {"rel_tol": 1.0})["result"] == "within_tolerance"
    assert rb.compare_tolerant(0.25, 250.0, rb.TOLERANCE_MAX)["result"] == "mismatch"
    assert rb.compare_tolerant(0.25, -0.25, rb.TOLERANCE_MAX)["result"] == "mismatch"


def test_lint_refuses_a_runbook_declaring_more_than_the_maximum(tmp_path) -> None:
    for index, tolerance in enumerate(({"rel_tol": 1}, {"abs_tol": 1e9}, {"rel_tol": 0.5})):
        root = build(tmp_path / str(index), tolerance=tolerance)
        findings = rb.lint(rb.load_runbook(root, RUNBOOK))
        assert any("tolerance" in f and "exceeds the maximum" in f for f in findings), findings


def test_the_cli_refuses_a_float_tolerance_above_the_maximum(tmp_path, monkeypatch) -> None:
    root = build(tmp_path)
    record(root, monkeypatch, RUNBOOK_TEST_SUM="left_fold")
    env = {k: v for k, v in os.environ.items() if not k.startswith("RUNBOOK_TEST_")}
    env["RUNBOOK_TEST_SCALE"] = "1000"
    tool = [sys.executable, str(REPO / "tools/runbook.py"), "--repo", str(root), "audit", SESSION,
            "--nonce", "ab", "--samples", "9"]
    loose = subprocess.run([*tool, "--float-tolerance", "rel_tol=1"], capture_output=True,
                           text=True, env=env)
    assert loose.returncode != 0
    assert "exceeds the maximum" in loose.stdout + loose.stderr
    assert not list((root / BASE).glob("audits/*/audit.json")), "a refused tolerance writes no audit"
    with pytest.raises(rb.RunbookError, match="exceeds the maximum"):
        audit(root, monkeypatch, env={"RUNBOOK_TEST_SCALE": "1000"}, float_tolerance={"rel_tol": 1.0})


def test_a_1000x_change_is_a_mismatch_under_the_maximum_tolerance(tmp_path, monkeypatch) -> None:
    root = build(tmp_path, tolerance=TOLERANCE)
    record(root, monkeypatch, RUNBOOK_TEST_SUM="left_fold")
    for scale in ("1000", "2", "-1"):
        report, written = audit(root, monkeypatch,
                                env={"RUNBOOK_TEST_SUM": "left_fold", "RUNBOOK_TEST_SCALE": scale})
        assert report["verdict"] == "flagged", scale
        assert written["replay_results"]["mismatch"] == 2
        assert any("/mean" in f for f in report["findings"])


def test_a_toleranced_screen_names_its_bound_and_never_reads_clean(tmp_path, monkeypatch) -> None:
    root = build(tmp_path, tolerance=TOLERANCE)
    record(root, monkeypatch, RUNBOOK_TEST_SUM="left_fold")
    report, written = audit(root, monkeypatch, env={"RUNBOOK_TEST_SUM": "compensated"})
    assert report["verdict"] == "clean_within_tolerance"
    assert len(written["tolerance_notes"]) == 2
    assert all('"source": "runbook"' in note and "not an exact replay" in note
               for note in written["tolerance_notes"])
    exact, _ = audit(root, monkeypatch, env={"RUNBOOK_TEST_SUM": "left_fold"})
    assert exact["verdict"] == "clean" and exact["tolerance_notes"] == []


# ---------------------------------------------------------------------------
# SHF-20261106-a114e7 LGX-8
# ---------------------------------------------------------------------------

def test_a_step_with_no_valid_unit_is_not_covered_never_silently_clean(tmp_path, monkeypatch) -> None:
    root = build(tmp_path, tolerance=TOLERANCE)
    record(root, monkeypatch, RUNBOOK_TEST_SUM="left_fold")
    latest = rb.latest_units

    def all_invalid(entries):
        return {key: {**unit, "valid": False} for key, unit in latest(entries).items()}

    monkeypatch.setattr(rb, "latest_units", all_invalid)
    report, written = audit(root, monkeypatch)
    assert report["replays"] == []
    assert any(line.startswith("S01-mean: no valid unit to replay (2 recorded")
               for line in written["not_covered"]), written["not_covered"]


@pytest.mark.parametrize("text,version", [("3.10", "3.10"), ("3.11", "3.11"), ("'3.10'", "3.10"),
                                          ("3.11.17", "3.11.17")])
def test_an_unquoted_yaml_python_version_is_read_from_its_source_text(tmp_path, text, version) -> None:
    (tmp_path / "manifest.yaml").write_text(f"run:\n  environment:\n    python_version: {text}\n")
    found = rb.recorded_interpreter(tmp_path)
    assert found == {"python_version": version, "source": "manifest.yaml#/run/environment/python_version"}

