"""tools/runbook.py replay comparison: a pointer absent from both outputs and
per-trial compare items (DEC-20261105-6e2616 NA-1(b); sheriff case
SHF-20261106-a114e7, ICV-1).

RBS-ICPERF-8cdc92's runbook lists one replay.compare item that unions the
pointers of six heterogeneous trials. The audit scored every pointer a trial
does not write (39 rows, "recorded null, replay null") as a mismatch, so the
preregistered A/A instrument flagged a session whose outputs replay equal.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import runbook as rb  # noqa: E402

SESSION_8CDC92 = "experiments/EXP-ICPERF-284bc4/runbook-sessions/RBS-ICPERF-8cdc92"


def step(compare, mode="fields"):
    return {"id": "S01", "replay": {"mode": mode, "compare": compare}}


def outputs(tmp_path: Path, recorded: dict, replayed: dict) -> tuple[Path, Path]:
    a, b = tmp_path / "recorded", tmp_path / "replay"
    for directory, doc in ((a, recorded), (b, replayed)):
        directory.mkdir(parents=True)
        (directory / "raw-result.json").write_text(json.dumps(doc))
    return a, b


def compare(tmp_path, recorded, replayed, items, trial="t1"):
    a, b = outputs(tmp_path, recorded, replayed)
    record: dict = {}
    problems, toleranced = rb.compare_outputs(step(items), trial, a, b, record)
    return problems, toleranced, {row["pointer"]: row["result"] for row in record["compared"]}


def test_a_pointer_absent_from_both_outputs_is_not_applicable(tmp_path) -> None:
    problems, toleranced, rows = compare(tmp_path, {"x": 1}, {"x": 1},
                                         [{"file": "raw-result.json", "pointers": ["/x", "/y"]}])
    assert problems == [] and toleranced is False
    assert rows == {"/x": "equal", "/y": "not_applicable"}


def test_a_pointer_present_on_one_side_only_is_a_mismatch(tmp_path) -> None:
    for recorded, replayed in (({"x": 1, "y": None}, {"x": 1}), ({"x": 1}, {"x": 1, "y": None})):
        problems, _, rows = compare(tmp_path / str(len(recorded)), recorded, replayed,
                                    [{"file": "raw-result.json", "pointers": ["/x", "/y"]}])
        assert rows["/y"] == "mismatch" and any("present only in the" in p for p in problems)


def test_a_replay_where_no_pointer_applies_reproduced_nothing(tmp_path) -> None:
    problems, _, rows = compare(tmp_path, {"x": 1}, {"x": 1},
                                [{"file": "raw-result.json", "pointers": ["/y", "/z"]}])
    assert set(rows.values()) == {"not_applicable"}
    assert problems and "reproduced nothing" in problems[0]


def test_a_differing_value_is_still_a_mismatch(tmp_path) -> None:
    problems, _, rows = compare(tmp_path, {"x": 1}, {"x": 2},
                                [{"file": "raw-result.json", "pointers": ["/x", "/y"]}])
    assert rows == {"/x": "mismatch", "/y": "not_applicable"} and len(problems) == 1


def test_per_trial_compare_items_apply_only_to_their_trials(tmp_path) -> None:
    items = [{"file": "raw-result.json", "pointers": ["/x"]},
             {"file": "raw-result.json", "pointers": ["/only_t2"], "trials": ["t2"]}]
    problems, _, rows = compare(tmp_path / "a", {"x": 1}, {"x": 1}, items, trial="t1")
    assert problems == [] and rows == {"/x": "equal"}
    problems, _, rows = compare(tmp_path / "b", {"x": 1}, {"x": 1}, items, trial="t2")
    assert rows == {"/x": "equal", "/only_t2": "not_applicable"} and problems == []
    problems, _, rows = compare(tmp_path / "c", {"x": 1, "only_t2": 3}, {"x": 1, "only_t2": 4},
                                items, trial="t2")
    assert rows["/only_t2"] == "mismatch" and problems


def test_lint_checks_per_trial_compare_items() -> None:
    from test_runbook_audit_tolerance import RUNBOOK, build  # noqa: PLC0415
    import tempfile
    import yaml

    with tempfile.TemporaryDirectory() as temporary:
        root = build(Path(temporary))
        path = root / RUNBOOK
        doc = yaml.safe_load(path.read_text())
        compare_list = doc["steps"][0]["replay"]["compare"]
        compare_list.append({"file": "raw-result.json", "pointers": ["/n"], "trials": ["t01"]})
        path.write_text(yaml.safe_dump(doc, sort_keys=False))
        assert rb.lint(rb.load_runbook(root, RUNBOOK)) == []
        for bad in (["t99"], [], "t01"):
            compare_list[-1]["trials"] = bad
            path.write_text(yaml.safe_dump(doc, sort_keys=False))
            assert any(".trials:" in f for f in rb.lint(rb.load_runbook(root, RUNBOOK))), bad


def committed_bytes(relative: str) -> bytes | None:
    """A file as committed at HEAD, read from Git: CI's sparse checkouts do
    not put run directories on disk."""
    result = subprocess.run(["git", "-C", str(REPO), "show", f"HEAD:{relative}"],
                            capture_output=True, check=False)
    return result.stdout if result.returncode == 0 else None


@pytest.mark.skipif(committed_bytes(f"{SESSION_8CDC92}/journal.jsonl") is None,
                    reason="RBS-ICPERF-8cdc92 is not in this repository's history")
def test_rbs_icperf_8cdc92_recorded_outputs_compare_clean_against_themselves(tmp_path) -> None:
    """Regression on the committed 8cdc92 bytes: each valid unit's recorded
    raw-result.json, compared with an identical replay, has no problem, and
    the pointers it does not write are the 39 not_applicable rows the
    sheriff reader saw as 'recorded null, replay null' mismatches."""
    import yaml
    entries = [json.loads(line) for line in
               committed_bytes(f"{SESSION_8CDC92}/journal.jsonl").decode().splitlines() if line.strip()]
    runbook_doc = yaml.safe_load(committed_bytes("experiments/EXP-ICPERF-284bc4/runbook.yaml"))
    trials_step = next(s for s in runbook_doc["steps"] if s["kind"] == "trials")
    units = rb.latest_units(entries)
    valid = {tid: unit for (sid, tid), unit in units.items()
             if sid == trials_step["id"] and unit["valid"]}
    assert len(valid) == 6
    not_applicable = 0
    for trial_id, unit in valid.items():
        run_dir = tmp_path / trial_id
        run_dir.mkdir()
        for item in trials_step["replay"]["compare"]:
            data = committed_bytes(f"{unit['run_dir']}/{item['file']}")
            assert data is not None, (trial_id, item["file"])
            (run_dir / item["file"]).write_bytes(data)
        record: dict = {}
        problems, toleranced = rb.compare_outputs(trials_step, trial_id, run_dir, run_dir, record)
        assert problems == [] and toleranced is False, (trial_id, problems)
        results = [row["result"] for row in record["compared"]]
        assert "mismatch" not in results and "equal" in results
        not_applicable += results.count("not_applicable")
    assert not_applicable == 39
