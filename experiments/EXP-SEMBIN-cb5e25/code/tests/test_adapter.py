"""Tests for code/adapter.py and code/check_trial.py (supervisor contract)."""
import gzip
import hashlib
import json
import os
import sys

import pytest
import yaml

CODE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, CODE)

import _paths                  # noqa: E402,F401
import adapter                 # noqa: E402
import check_trial as CT       # noqa: E402
import provenance              # noqa: E402

PROTO = "ab" * 32


def make_dirs(tmp_path, name="RUN-SEMBIN-abc123", fixtures=True):
    rdir = tmp_path / name
    rdir.mkdir()
    (rdir / "command.txt").write_text(json.dumps(["python3", "adapter.py"]) + "\n")
    (rdir / "environment.json").write_text(json.dumps({"python": sys.version, "commit": "0" * 40}))
    (rdir / "stdout.log").write_text("")
    (rdir / "stderr.log").write_text("")
    shared = tmp_path / "shared"
    shared.mkdir(exist_ok=True)
    if fixtures:
        fx = shared / "fixtures.json"
        if not fx.exists():
            fx.write_text(json.dumps({"fixtures": [{"id": f"F-{i}", "verdict": "pass"} for i in range(1, 9)],
                                      "sr1_all_pass": True}))
    return rdir, shared


@pytest.fixture(autouse=True)
def code_hash_current(monkeypatch):
    """CODE_SHA256.json is regenerated as the last step of a round; tests must not depend on that."""
    recorded = json.load(open(os.path.join(CODE, "CODE_SHA256.json")))
    monkeypatch.setattr(provenance, "compute", lambda: {"files": dict(recorded["files"])})
    return recorded


def args(rdir, shared, cell="m3n06", arm="EQS4", r=0, kind="trial", *extra):
    a = ["--run-dir", str(rdir), "--shared-run-dir", str(shared), "--kind", kind, "--cell", cell,
         "--protocol-sha256", PROTO]
    if kind == "trial":
        a += ["--arm", arm, "--r", str(r)]
    return a + list(extra)


class Clock:
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t


def test_valid_trial_and_manifest_passes_check_run(tmp_path, capsys):
    rdir, shared = make_dirs(tmp_path)
    assert adapter.main(args(rdir, shared)) == 0
    raw = json.load(open(rdir / "raw-result.json"))
    assert raw["trial_id"] == "m3n06__EQS4__r0" and raw["exit_code"] == 0
    assert raw["trial_record"]["status"] == "completed"
    app = raw["shared_artifacts_appended"]
    assert "instances.jsonl.gz" in app and "closures.jsonl.gz" in app and "cost.jsonl" in app
    assert all(len(v["sha256"]) == 64 for v in app.values())
    man = yaml.safe_load(open(rdir / "manifest.yaml"))["run"]
    assert man["id"] == "RUN-SEMBIN-abc123" and man["status"] == "completed"
    import validate_ledger
    ctx = validate_ledger.Ctx(set())
    validate_ledger.check_run(str(rdir / "manifest.yaml"), ctx)
    assert ctx.errors == []
    capsys.readouterr()
    assert CT.main([str(rdir), "--shared-run-dir", str(shared)]) == 0
    out = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert out["valid"] is True and out["reasons"] == []


def test_dynamic_remaining_seconds_shrink_with_fake_clock(tmp_path):
    rdir1, shared = make_dirs(tmp_path, "RUN-SEMBIN-000001")
    assert adapter.main(args(rdir1, shared, "m3n05", "EQS4", 0), clock=Clock(1000.0)) == 0
    rdir2 = tmp_path / "RUN-SEMBIN-000002"
    rdir2.mkdir()
    assert adapter.main(args(rdir2, shared, "m3n05", "EQS2", 0), clock=Clock(1500.0)) == 0
    r1 = json.load(open(rdir1 / "raw-result.json"))["budget"]
    r2 = json.load(open(rdir2 / "raw-result.json"))["budget"]
    assert r1["remaining_seconds"] == 43200 - 1200 - 0
    assert r2["remaining_seconds"] == 43200 - 1200 - 500
    assert r2["remaining_seconds"] < r1["remaining_seconds"]
    start = json.load(open(shared / "session_start.json"))
    assert start["started_at_epoch"] == 1000.0               # written once, never overwritten
    # run.py received the dynamic values
    t2 = json.load(open(shared / "trials" / "m3n05__EQS2__r0.json"))["args"]
    assert t2["remaining_seconds"] == 43200 - 500 and t2["reserve_seconds"] == 1200
    assert t2["timings_file"] == str(shared / "cost.jsonl")


def test_refuses_to_rerun_finished_trial(tmp_path, capsys):
    rdir, shared = make_dirs(tmp_path)
    assert adapter.main(args(rdir, shared)) == 0
    before = open(rdir / "raw-result.json").read()
    assert adapter.main(args(rdir, shared)) == 3               # same supervisor dir
    assert open(rdir / "raw-result.json").read() == before
    other = tmp_path / "RUN-SEMBIN-def456"
    other.mkdir()
    assert adapter.main(args(other, shared)) == 3               # same trial, new dir: shared trial exists
    assert not (other / "raw-result.json").exists()


def test_existing_shared_artifact_modified_is_exit_4(tmp_path, monkeypatch):
    rdir, shared = make_dirs(tmp_path)
    assert adapter.main(args(rdir, shared)) == 0
    rdir2 = tmp_path / "RUN-SEMBIN-fedcba"
    rdir2.mkdir()
    real = adapter.subprocess.run

    def corrupting(cmd, **kw):
        p = real(cmd, **kw)
        with open(shared / "instances.jsonl.gz", "r+b") as f:     # rewrite old bytes
            f.seek(0)
            f.write(b"\x00")
        return p
    monkeypatch.setattr(adapter.subprocess, "run", corrupting)
    assert adapter.main(args(rdir2, shared, "m3n06", "EQS2", 1)) == 4
    raw = json.load(open(rdir2 / "raw-result.json"))
    assert raw["shared_artifact_violations"] == ["instances.jsonl.gz"]


def test_no_rlimit_set_by_adapter():
    src = open(os.path.join(CODE, "adapter.py")).read()
    assert "RLIMIT_AS" not in src.replace("never RLIMIT_AS", "").replace("(never RLIMIT_AS)", "")
    assert "setrlimit" not in src and "preexec_fn" not in src


def test_certify_kind_passthrough(tmp_path, capsys):
    rdir, shared = make_dirs(tmp_path)
    assert adapter.main(args(rdir, shared, "m3n12", "PC-TRI", 0)) == 0      # no decisive instance in the cell
    rdir2 = tmp_path / "RUN-SEMBIN-aaaaaa"
    rdir2.mkdir()
    assert adapter.main(args(rdir2, shared, "m3n12", None, None, "certify")) == 0
    raw = json.load(open(rdir2 / "raw-result.json"))
    assert raw["kind"] == "certify" and raw["certify"]["results"] == [] and raw["trial"] == "m3n12__certify"
    capsys.readouterr()
    assert CT.main([str(rdir2), "--shared-run-dir", str(shared)]) == 0
    assert adapter.main(args(rdir2, shared, "m3n12", None, None, "certify")) == 3


def test_certify_range_error_is_propagated(tmp_path):
    rdir, shared = make_dirs(tmp_path)
    assert adapter.main(args(rdir, shared, "m3n06", None, None, "certify")) != 0     # N = 12 outside 21..26
    assert json.load(open(rdir / "raw-result.json"))["exit_code"] != 0
    assert yaml.safe_load(open(rdir / "manifest.yaml"))["run"]["status"] == "failed"


# ------------------------------------------------------------------ check_trial invalid conditions
def gzput(path, rows):
    with open(path, "wb") as raw:
        for r in rows:
            with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as g:
                g.write((json.dumps(r) + "\n").encode())


def crow(key, D, contained, m4=None, final=7, lin=3):
    m1 = {"contained": contained, "type": None if contained else "L", "deficit": 0, "d_GB": 1}
    return {"key": key, "D": D, "status": "ok", "M1": m1, "M2": {"linear_forms": lin, "one_in_W": False},
            "M4": m4 or [{"rank": 3, "dims_by_deg": [0, 1, 3]}], "M5": {"z": 1},
            "M7": {"rank": 3, "one": False, "dims_by_deg": [0, 1, 3], "gb_in_M": False},
            "engine": {"final_dim": final, "dims_by_deg": [0, 1], "iterations_to_fixpoint": 1}}


def summary(key, arm, m1, m3, cell="m3n06"):
    return {"kind": "summary", "key": key, "arm": arm, "cell": cell, "r": 0, "N": 12, "M3": m3, "D_reached": 4,
            "censored": False, "M1_at_4": m1, "z": 1}


def build(tmp_path, arm="EQS4", key="m3n06/EQS4/r0", rows=None, summ=None, instances=None, extra_rows=None,
          status="completed", results=None, loaded=None, fixtures=True, tid=None):
    rdir, shared = make_dirs(tmp_path, fixtures=fixtures)
    (shared / "trials").mkdir(exist_ok=True)
    tid = tid or key.replace("/", "__")
    rec = {"trial": tid, "key": key, "arm": arm, "status": status, "results": results or {},
           "provenance": {"code_sha256_loaded": loaded or {}}}
    tp = shared / "trials" / f"{tid}.json"
    tp.write_text(json.dumps(rec))
    raw = {"trial_id": tid, "kind": "trial", "exit_code": 0, "shared_artifact_violations": [],
           "trial_record": rec, "trial_record_sha256": hashlib.sha256(tp.read_bytes()).hexdigest()}
    (rdir / "raw-result.json").write_text(json.dumps(raw))
    (rdir / "manifest.yaml").write_text(yaml.safe_dump({"run": {"trial_id": tid, "inputs": {"trial_id": tid}}}))
    gzput(shared / "instances.jsonl.gz", instances or [{"key": key, "valid": True, "N": 12, "cell": "m3n06", "arm": arm}])
    gzput(shared / "closures.jsonl.gz", (rows or []) + ([summ] if summ else []) + (extra_rows or []))
    return rdir, shared


def run_check(rdir, shared, capsys):
    capsys.readouterr()
    code = CT.main([str(rdir), "--shared-run-dir", str(shared)])
    return code, json.loads(capsys.readouterr().out.strip().splitlines()[-1])


def test_check_valid_and_censored_is_still_valid(tmp_path, capsys):
    key = "m3n06/EQS4/r0"
    cens = {"key": key, "D": 4, "status": "censored_wall", "M1": {"contained": "censored"}}
    rdir, shared = build(tmp_path, rows=[crow(key, 2, False), crow(key, 3, True), cens],
                         summ=summary(key, "EQS4", {"contained": "censored"}, 3))
    code, out = run_check(rdir, shared, capsys)
    assert code == 0 and out["valid"] and any("censored_wall" in w for w in out["warnings"])


@pytest.mark.parametrize("bad_instance", [{"valid": False, "checks": {"descent_check": {"ok": False}}}])
def test_check_ir1_ir2_ir3_invalid_instance(tmp_path, capsys, bad_instance):
    key = "m3n06/EQS4/r0"
    inst = [{"key": key, "N": 12, "cell": "m3n06", "arm": "EQS4", **bad_instance}]
    rdir, shared = build(tmp_path, rows=[crow(key, 4, True)], summ=summary(key, "EQS4", {"contained": True}, 4),
                         instances=inst)
    code, out = run_check(rdir, shared, capsys)
    assert code == 1 and any("IR-1/IR-2/IR-3" in r for r in out["reasons"])


def test_check_trial_error_and_results_invalid_flag(tmp_path, capsys):
    key = "m3n06/EQS4/r0"
    rdir, shared = build(tmp_path, status="error")
    assert run_check(rdir, shared, capsys)[0] == 1
    rdir2 = tmp_path / "x"
    rdir2.mkdir()
    rdir2, shared2 = build(rdir2, results={"invalid": "IR-1/IR-2/IR-3 failure: closures not run"})
    code, out = run_check(rdir2, shared2, capsys)
    assert code == 1 and any("invalid instance" in r for r in out["reasons"])


def test_check_ir5_stale_code_hash_and_loaded_mismatch(tmp_path, capsys, monkeypatch):
    key = "m3n06/EQS4/r0"
    rdir, shared = build(tmp_path, rows=[crow(key, 4, True)], summ=summary(key, "EQS4", {"contained": True}, 4))
    assert run_check(rdir, shared, capsys)[0] == 0
    cur = provenance.compute()
    monkeypatch.setattr(provenance, "compute", lambda: {"files": {**cur["files"], "x.py": "1"}})
    code, out = run_check(rdir, shared, capsys)
    assert code == 1 and any("not current" in r for r in out["reasons"])
    monkeypatch.setattr(provenance, "compute", lambda: cur)
    rel = next(k for k in cur["files"] if k.endswith("code/run.py"))
    sub = tmp_path / "y"
    sub.mkdir()
    rdir2, shared2 = build(sub, rows=[crow(key, 4, True)], summ=summary(key, "EQS4", {"contained": True}, 4),
                           loaded={rel: "0" * 64})
    code, out = run_check(rdir2, shared2, capsys)
    assert code == 1 and any("loaded" in r for r in out["reasons"])


def test_check_pc_tri_sr4(tmp_path, capsys):
    key = "m3n06/PC-TRI/r0"
    for i, (m1, m3, want) in enumerate(((True, 3, 0), (False, "> 4", 1), (True, 4, 1))):
        sub = tmp_path / f"p{i}"
        sub.mkdir()
        rdir, shared = build(sub, arm="PC-TRI", key=key, rows=[crow(key, 4, m1)],
                             summ=summary(key, "PC-TRI", {"contained": m1}, m3))
        code, out = run_check(rdir, shared, capsys)
        assert code == want, out
        if want:
            assert any("SR-4" in r for r in out["reasons"])


def test_check_aa_sr5_exact_equality(tmp_path, capsys):
    src, aa = "m3n06/EQS4/r0", "m3n06/EQS4-AA/r0"
    base = [crow(src, 2, False), crow(src, 3, True), crow(src, 4, True)]
    same = [crow(aa, 2, False), crow(aa, 3, True), crow(aa, 4, True)]
    rdir, shared = build(tmp_path, arm="EQS4-AA", key=aa, rows=base + same,
                         summ=summary(src, "EQS4", {"contained": True}, 3), extra_rows=[summary(aa, "EQS4-AA", {"contained": True}, 3)])
    code, out = run_check(rdir, shared, capsys)
    assert code == 0, out
    diff = [crow(aa, 2, False), crow(aa, 3, True, final=8), crow(aa, 4, True)]
    sub = tmp_path / "d"
    sub.mkdir()
    rdir2, shared2 = build(sub, arm="EQS4-AA", key=aa, rows=base + diff,
                           summ=summary(src, "EQS4", {"contained": True}, 3), extra_rows=[summary(aa, "EQS4-AA", {"contained": True}, 3)])
    code, out = run_check(rdir2, shared2, capsys)
    assert code == 1 and any("SR-5" in r for r in out["reasons"])
    sub3 = tmp_path / "m"
    sub3.mkdir()
    rdir3, shared3 = build(sub3, arm="EQS4-AA", key=aa, rows=same, summ=None,
                           extra_rows=[summary(aa, "EQS4-AA", {"contained": True}, 3)])
    code, out = run_check(rdir3, shared3, capsys)
    assert code == 1 and any("source record" in r for r in out["reasons"])
    sub4 = tmp_path / "m3"
    sub4.mkdir()
    s4 = summary(aa, "EQS4-AA", {"contained": True}, 4)           # D_solve differs from source (3)
    rdir4, shared4 = build(sub4, arm="EQS4-AA", key=aa, rows=base + same,
                           summ=summary(src, "EQS4", {"contained": True}, 3), extra_rows=[s4])
    assert run_check(rdir4, shared4, capsys)[0] == 1


def test_check_fixtures_gate_and_artifacts_and_usage(tmp_path, capsys):
    key = "m3n06/EQS4/r0"
    rdir, shared = build(tmp_path, rows=[crow(key, 4, True)], summ=summary(key, "EQS4", {"contained": True}, 4),
                         fixtures=False)
    code, out = run_check(rdir, shared, capsys)
    assert code == 1 and any("fixtures.json missing" in r for r in out["reasons"])
    (shared / "fixtures.json").write_text(json.dumps({"fixtures": [{"id": "F-1", "verdict": "pass"}] * 8,
                                                      "sr1_all_pass": False}))
    assert run_check(rdir, shared, capsys)[0] == 1
    (shared / "fixtures.json").write_text(json.dumps({"fixtures": [{"id": "F-1", "verdict": "pass"}] * 8,
                                                      "sr1_all_pass": True}))
    assert run_check(rdir, shared, capsys)[0] == 0
    # trial record tampered after the adapter wrote raw-result.json
    tp = shared / "trials" / "m3n06__EQS4__r0.json"
    d = json.load(open(tp))
    d["status"] = "completed "
    tp.write_text(json.dumps(d))
    code, out = run_check(rdir, shared, capsys)
    assert code == 1 and any("sha256" in r for r in out["reasons"])
    (rdir / "manifest.yaml").unlink()
    assert run_check(rdir, shared, capsys)[0] == 1
    assert CT.main([str(tmp_path / "nope"), "--shared-run-dir", str(shared)]) == 2
    assert CT.main([]) == 2


def test_check_fullfe_disagreement_and_der3_mismatch(tmp_path, capsys):
    key = "m3n06/EQS4-FULLFE/r0"
    row = {"key": key, "D": 3, "status": "ok", "C_FE_EQ_agree": False}
    rdir, shared = build(tmp_path, arm="EQS4-FULLFE", key=key, rows=[row])
    code, out = run_check(rdir, shared, capsys)
    assert code == 1 and any("C-FE-EQ" in r for r in out["reasons"])
    k2 = "m3n06/EQS4/r0"
    sub = tmp_path / "z"
    sub.mkdir()
    bad = crow(k2, 4, True)
    bad["der3_mismatch"] = True
    rdir2, shared2 = build(sub, rows=[bad], summ=summary(k2, "EQS4", {"contained": True}, 4))
    assert run_check(rdir2, shared2, capsys)[0] == 1
