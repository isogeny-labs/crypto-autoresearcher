#!/usr/bin/env python3
"""Frozen driver of EXP-PEXT-0b2c75 (norm-character / Kummer law for |E(K)[4]|; H-PEXT-ad0073).

  python3 run.py trial --run-dir DIR --run-id RUN-... --trial-id ID --plan experiments/EXP-PEXT-0b2c75/trial-plan.json

Stages (trial-plan.json "stage"):
  regression  positive controls and instrument controls: n = 5, q = 3 family reproduces the 20 published genus-5 records
              of the sibling census (j, order, E2, E4) and the tool's verbatim sibling E4 method reproduces every published
              field of those records; fixture recounts (negative: off-family E4 = 4 at q = 3; nearby n = 3, descriptive);
              the (m, r, genus) of every S word; bitalgebra.py selfcheck; A/A rebuild (other rustc flags, 1 thread) with
              byte-identical outputs on four arms. Any failure voids the experiment (instrument defect).
  n5core      n = 5, S = (0,1,2,3), q = 5, 7, 9, 11, 13, 17, 19 (decisive, out of sample).
  n5ext       n = 5, S = (0,1,2,3), q = 23, 25, 27, 29, 31 (decisive, out of sample, long).
  n7          n = 7: S = (0,2,3,4) at q = 3, 5, 7, 9 (pre-registered, out of sample); other S classes at q = 3, 5, 7.
  negative    random 4-subsets of K (outside the family) at n = 5, q = 5, 7, 9, 11, 13, both twists.
  analyze     analysis.json and tables from the recorded run directories (recorded values only).

Standard library plus PyYAML (manifest). rustc (edition 2021) builds the tool into a temporary directory.
Large outputs are stored as deterministic gzip (mtime 0); sha256 of the uncompressed stream is recorded.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import platform
import resource
import shlex
import shutil
import subprocess
import sys
import tempfile
import time

import yaml

EXP = "EXP-PEXT-0b2c75"
HYPOTHESIS_ID = "H-PEXT-ad0073"
HERE = os.path.dirname(os.path.abspath(__file__))
EXP_DIR = os.path.dirname(HERE)
RUNS_DIR = os.path.join(EXP_DIR, "runs")
THREADS = 4
RUSTC_FLAGS = ["--edition", "2021", "-O"]
RUSTC_FLAGS_ALT = ["--edition", "2021", "-C", "opt-level=2", "-C", "codegen-units=1"]
TOOL = "pext4_census.rs"
NEG_SEED = 20261101
NEG_COUNT = 1000
# q -> (p, f)
PF = {3: (3, 1), 5: (5, 1), 7: (7, 1), 9: (3, 2), 11: (11, 1), 13: (13, 1), 17: (17, 1), 19: (19, 1), 23: (23, 1),
      25: (5, 2), 27: (3, 3), 29: (29, 1), 31: (31, 1)}
S5 = "0,1,2,3"
N5CORE = (5, 7, 9, 11, 13, 17, 19)
N5EXT = (23, 25, 27, 29, 31)
N7_PRIMARY = ("0,2,3,4", (3, 5, 7, 9))
N7_SECONDARY = (("0,1,2,5", "0,1,2,4", "0,1,2,3", "0,1,3,4", "0,1,3,5"), (3, 5, 7))
NEG_Q = (5, 7, 9, 11, 13)
AA_ARMS = ((3, 5, S5), (5, 5, S5), (9, 5, S5), (3, 7, "0,2,3,4"))
FIXTURES = {"D-n5-q3-cosets.jsonl": "8f03e3d1a28a989108a038cfffab51e0362d2397dd03e06fc0ccfe442d9123fa",
            "pilot-n3-q3-cosets.jsonl": "5003d258d9146d6650ac70d77ea373b4e4979713abbbebd82e1007c6394573ff"}
# pre-registered constants of the controls (written at design from the vendored fixtures, recomputed by the trial)
EXPECT_OFF_FAMILY = {"5": {"8": 20, "4": 0}, "17": {"8": 30, "4": 20}, "25": {"8": 10, "4": 1}}  # D-n5-q3, E2 = 4 records by min_genus then E4
EXPECT_MR = {5: {"0,1,2,3": [4, 5, 5]}, 7: {"0,1,2,3": [6, 7, 49], "0,1,2,4": [3, 7, 7], "0,1,2,5": [3, 7, 7], "0,1,3,4": [6, 7, 49], "0,1,3,5": [6, 7, 49]}}


def _sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def code_hashes() -> dict:
    out = {}
    for root, dirs, files in os.walk(HERE):
        dirs[:] = [d for d in dirs if d not in ("__pycache__",)]
        for name in sorted(files):
            if name.endswith((".py", ".rs")):
                p = os.path.join(root, name)
                out[os.path.relpath(p, HERE)] = _sha256(p)
    return dict(sorted(out.items()))


def _git_commit() -> tuple:
    try:
        c = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=HERE, text=True).strip()
        d = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", HERE], cwd=HERE).returncode != 0
        return c, d
    except (OSError, subprocess.CalledProcessError):
        return None, None


def _version(cmd: list) -> str | None:
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT).strip().splitlines()[0]
    except (OSError, subprocess.CalledProcessError, IndexError):
        return None


def build_tool(build: str, flags: list, name: str) -> str:
    out = os.path.join(build, name)
    subprocess.run(["rustc", *flags, os.path.join(HERE, TOOL), "-o", out], check=True)
    return out


def tool(binary: str, args: list) -> bytes:
    return subprocess.run([binary, *map(str, args)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True).stdout


def lines(b: bytes) -> list:
    return [json.loads(x) for x in b.decode().splitlines() if x.strip()]


def write_gz(path: str, data: bytes) -> str:
    with open(path, "wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as g:
            g.write(data)
    return sha_bytes(data)


def family_args(q: int, n: int, s: str, threads: int = THREADS) -> list:
    p, f = PF[q]
    return ["family", p, f, n, s, threads]


VALIDITY_KEYS = ("m1_m2_mismatch", "quartic_cubic_order_mismatch", "hasse_fail", "chi_norm_identity_mismatch", "e2_not_4")


def arm_summary(recs: list) -> dict:
    fld = recs[0]
    tot = recs[-1]
    ok = (fld["rec"] == "field" and tot["rec"] == "totals" and fld["orbits"] == fld["orbits_expected"]
          and tot["units"] == 2 * fld["orbits"] and all(tot[k] == 0 for k in VALIDITY_KEYS))
    return {"q": fld["q"], "n": fld["n"], "S": fld["S"], "m": fld["m"], "r": fld["r"], "genus": fld["genus"], "units": tot["units"],
            "valid": ok, "validity": {k: tot[k] for k in VALIDITY_KEYS}, "law_mismatch": tot["law"]}


def stage_family(rd: str, binary: str, arms: list, outname: str) -> tuple:
    """arms: [(q, n, S)]; one concatenated gzip stream, each arm = field record, unit records, totals."""
    buf = io.BytesIO()
    summ = []
    for q, n, s in arms:
        raw = tool(binary, family_args(q, n, s))
        buf.write(raw)
        summ.append(arm_summary(lines(raw)))
    sha = write_gz(os.path.join(rd, outname), buf.getvalue())
    ok = all(a["valid"] for a in summ)
    return ok, {"stream_sha256": sha, "arms": summ, "all_valid": ok}


def stage_negative(rd: str, binary: str) -> tuple:
    buf = io.BytesIO()
    summ = []
    for q in NEG_Q:
        p, f = PF[q]
        raw = tool(binary, ["random", p, f, 5, NEG_COUNT, NEG_SEED, THREADS])
        buf.write(raw)
        recs = lines(raw)
        tot = recs[-1]
        valid = tot["units"] == 2 * NEG_COUNT and all(tot[k] == 0 for k in ("m1_m2_mismatch", "quartic_cubic_order_mismatch", "hasse_fail", "e2_not_4"))
        summ.append({"q": q, "units": tot["units"], "valid": valid})
    sha = write_gz(os.path.join(rd, "negative.jsonl.gz"), buf.getvalue())
    ok = all(a["valid"] for a in summ)
    return ok, {"stream_sha256": sha, "arms": summ, "all_valid": ok, "seed": NEG_SEED, "configs_per_q": NEG_COUNT}


def fixture_records(name: str) -> list:
    path = os.path.join(HERE, "fixtures", name)
    assert _sha256(path) == FIXTURES[name], f"fixture {name} hash"
    with open(path) as f:
        return [json.loads(x) for x in f if x.strip()]


def stage_regression(rd: str, binary: str, build: str) -> tuple:
    checks = []

    def add(name, ok, **kw):
        checks.append({"name": name, "identical": bool(ok), **kw})

    # C1: positive control, family at n = 5, q = 3 against the 20 published genus-5 records
    raw = tool(binary, family_args(3, 5, S5))
    with open(os.path.join(rd, "R-n5-q3.jsonl"), "wb") as f:
        f.write(raw)
    fam = lines(raw)
    units = [r for r in fam if r["rec"] == "unit"]
    d5 = fixture_records("D-n5-q3-cosets.jsonl")
    g5 = [r for r in d5 if r["rec"] == "curve" and r["min_genus"] == 5]
    fix = lines(tool(binary, ["fix", 3, 1, 5, *[f"{r['a2_idx']}:{r['A_idx']}:{r['B_idx']}" for r in g5]]))
    with open(os.path.join(rd, "R-fix-n5-q3.jsonl"), "w") as f:
        for r in fix:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    add("sibling_genus5_record_count", len(g5) == 20 and len(units) == 20, fixture=len(g5), family_units=len(units))
    add("verbatim_sibling_E2_E4_order", all(a["order"] == b["order"] and a["E2"] == b["E2"] and a["E4"] == b["E4"] and a["j_fq"] == b["j_in_Fq"]
                                            for a, b in zip(fix, g5)), records=len(fix))
    a = sorted((x["j"], x["order"], x["E2"], x["E4"]) for x in fix)
    b = sorted((u["j"], u["order"], u["E2"], u["E4"]) for u in units)
    add("family_equals_published_genus5_records", a == b, multiset_size=len(a), first_difference=None if a == b else [a[:3], b[:3]])
    tot = fam[-1]
    add("family_q3_validity", all(tot[k] == 0 for k in VALIDITY_KEYS), validity={k: tot[k] for k in VALIDITY_KEYS})
    # C2: fixture recounts. Negative control: off-family split records (E2 = 4) at q = 3 by min genus and E4.
    off = {}
    for r in d5:
        if r["rec"] == "curve" and r["E2"] == 4:
            off.setdefault(str(r["min_genus"]), {}).setdefault(str(r["E4"]), 0)
            off[str(r["min_genus"])][str(r["E4"])] += 1
    exp_off = {g: {k: v for k, v in e.items() if v} for g, e in EXPECT_OFF_FAMILY.items()}
    add("negative_fixture_recount_off_family_E4", off == exp_off, observed=off, expected=exp_off)
    p3 = fixture_records("pilot-n3-q3-cosets.jsonl")
    nb = {}
    for r in p3:
        if r["rec"] == "curve" and r["min_genus"] == 3:
            k = f"E2={r['E2']},E4={r['E4']}"
            nb[k] = nb.get(k, 0) + 1
    add("nearby_n3_q3_genus3_recount_descriptive", True, observed=nb, note="descriptive; no prediction, the n = 3 genus-3 family is not four conjugates of one orbit")
    # C3: (m, r, genus) of every S word
    mr_ok = True
    mr_obs = {}
    for n in (5, 7):
        for r in lines(tool(binary, ["mr", 3, 1, n])):
            if r["rec"] == "mr":
                key = ",".join(map(str, r["S"]))
                mr_obs.setdefault(str(n), {})[key] = [r["m"], r["r"], r["genus"]]
    for n, e in EXPECT_MR.items():
        mr_ok &= mr_obs.get(str(n)) == e
    add("mr_genus_of_S_words", mr_ok, observed=mr_obs, expected={str(k): v for k, v in EXPECT_MR.items()})
    # C4: algebra selfcheck
    sys.path.insert(0, HERE)
    import bitalgebra
    sc = bitalgebra.selfcheck_dict()
    add("bitalgebra_selfcheck", sc["pass"], **{k: v for k, v in sc.items() if k != "pass"})
    # C5: A/A rebuild: other rustc flags and one thread; byte-identical streams
    alt = build_tool(build, RUSTC_FLAGS_ALT, "pext4_alt")
    aa = []
    for q, n, s in AA_ARMS:
        x = tool(binary, family_args(q, n, s, THREADS))
        y = tool(alt, family_args(q, n, s, 1))
        aa.append({"q": q, "n": n, "S": s, "bytes": len(x), "sha256_base": sha_bytes(x), "sha256_alt": sha_bytes(y), "identical": x == y})
    add("aa_rebuild_byte_identical", all(r["identical"] for r in aa), arms=aa)
    ok = all(c["identical"] for c in checks)
    with open(os.path.join(rd, "regression.json"), "w") as f:
        json.dump({"experiment": EXP, "pass": ok, "checks": checks}, f, indent=1, sort_keys=True)
    return ok, {"regression_pass": ok, "checks": len(checks), "failed": [c["name"] for c in checks if not c["identical"]]}


def stage_analyze(rd: str, up: dict) -> tuple:
    import analyze  # same bound directory
    an = analyze.analyze(up)
    with open(os.path.join(rd, "analysis.json"), "w") as f:
        json.dump(an, f, indent=1, sort_keys=True)
    with open(os.path.join(rd, "law-table.md"), "w") as f:
        f.write(analyze.table_md(an))
    return True, {"headline": an["headline"], "predictions": {k: v["outcome"] for k, v in an["predictions"].items()},
                  "valid": an["valid"], "invalid_reasons": an["invalid_reasons"]}


def cmd_trial(a: argparse.Namespace) -> int:
    t0 = time.time()
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(a.plan) as f:
        plan = json.load(f)
    trial = next(t for t in plan["trials"] if t["id"] == a.trial_id)
    assert trial["run_id"] == a.run_id, "run id does not match the plan"
    rd = a.run_dir
    os.makedirs(rd, exist_ok=True)
    up = {k: (v if os.path.isabs(v) else os.path.join(RUNS_DIR, v)) for k, v in trial.get("inputs_from", {}).items()}
    build = tempfile.mkdtemp(prefix="pext4-build-")
    status, reason, summary, code = "completed_valid", None, {}, 0
    try:
        stage = trial["stage"]
        binary = build_tool(build, RUSTC_FLAGS, "pext4") if stage != "analyze" else None
        if stage == "regression":
            ok, summary = stage_regression(rd, binary, build)
        elif stage == "n5core":
            ok, summary = stage_family(rd, binary, [(q, 5, S5) for q in N5CORE], "n5-core.jsonl.gz")
        elif stage == "n5ext":
            ok, summary = stage_family(rd, binary, [(q, 5, S5) for q in N5EXT], "n5-ext.jsonl.gz")
        elif stage == "n7":
            arms = [(q, 7, N7_PRIMARY[0]) for q in N7_PRIMARY[1]] + [(q, 7, s) for s in N7_SECONDARY[0] for q in N7_SECONDARY[1]]
            ok, summary = stage_family(rd, binary, arms, "n7.jsonl.gz")
        elif stage == "negative":
            ok, summary = stage_negative(rd, binary)
        elif stage == "analyze":
            sys.path.insert(0, HERE)
            ok, summary = stage_analyze(rd, up)
        else:
            raise ValueError(f"unknown stage {stage}")
        if not ok:
            status, code = "invalid_measurement", 1
            reason = f"{stage}: instrument check failed (see raw-result.json summary); no later trial is read as evidence"
        with open(os.path.join(rd, "raw-result.json"), "w") as f:
            json.dump({"experiment": EXP, "trial_id": a.trial_id, "run_id": a.run_id, "attack_claimed": False,
                       "summary": summary, "invalid_reason": reason}, f, indent=1, sort_keys=True)
    except Exception as e:  # recorded as failed_infrastructure, never a metric
        status, reason, code = "failed", f"failed_infrastructure: {type(e).__name__}: {e}", 1
        with open(os.path.join(rd, "raw-result.json"), "w") as f:
            json.dump({"experiment": EXP, "trial_id": a.trial_id, "run_id": a.run_id, "attack_claimed": False,
                       "summary": {}, "invalid_reason": reason}, f, indent=1)
    finally:
        shutil.rmtree(build, ignore_errors=True)
    commit, dirty = _git_commit()
    ru_c, ru_s = resource.getrusage(resource.RUSAGE_CHILDREN), resource.getrusage(resource.RUSAGE_SELF)
    manifest = {"run": {
        "id": a.run_id, "experiment_id": EXP, "hypothesis_id": HYPOTHESIS_ID,
        "task_id": plan.get("task_id"), "trial_id": a.trial_id, "role": "executor",
        "recorded_at": started[:10], "status": status, "attack_claimed": False,
        "validity": {"status": status, "reason": reason or "run.py recorded no invalidation; check.py "
                     "and independent review decide validity", "failure_class": None},
        "code": {"commit": commit, "dirty": dirty, "branch": None,
                 "command": shlex.join(getattr(sys, "orig_argv", None) or [sys.executable, *sys.argv]), "code_sha256": code_hashes(),
                 "trial_plan_sha256": _sha256(a.plan), "working_directory": os.getcwd()},
        "environment": {"host": platform.node(), "operating_system": platform.platform(),
                        "python_version": sys.version.split()[0], "rustc_version": _version(["rustc", "--version"]),
                        "processor_count": os.cpu_count(), "source": "manifest.yaml /run/environment"},
        "inputs": {"curve_id": None, "seed": NEG_SEED,
                   "parameters": {"trial_id": a.trial_id, "stage": trial["stage"], "inputs_from": trial.get("inputs_from", {}),
                                  "plan": a.plan, "rustc_flags": RUSTC_FLAGS, "threads": THREADS, "negative_count": NEG_COUNT}},
        "timing": {"started_at": started, "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "wall_seconds": round(time.time() - t0, 3)},
        "resources": {"peak_rss_bytes": int(max(ru_c.ru_maxrss, ru_s.ru_maxrss) * 1024),
                      "cpu_seconds": round(ru_c.ru_utime + ru_c.ru_stime + ru_s.ru_utime + ru_s.ru_stime, 3)},
        "result": {"metrics": {"raw_result": "raw-result.json"} if code == 0 else {},
                   "valid": status == "completed_valid", "invalid_reason": reason, "raw_result": "raw-result.json",
                   "certificate": {"kind": "none", "verified": True, "verifier": "no-claim",
                                   "note": "exact group-order and 4-torsion counts on toy fields (K up to F_{3^15}, F_{31^5}); "
                                           "no transfer, discrete logarithm, cost or speedup is claimed"}},
        "artifacts": [n for n in trial["artifacts"] if n != "manifest.yaml"],
    }}
    with open(os.path.join(rd, "manifest.yaml"), "w") as f:
        yaml.safe_dump(manifest, f, sort_keys=False)
    return code


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("trial")
    s.add_argument("--run-dir", required=True)
    s.add_argument("--run-id", required=True)
    s.add_argument("--trial-id", required=True)
    s.add_argument("--plan", required=True)
    s.set_defaults(f=cmd_trial)
    a = ap.parse_args()
    sys.exit(a.f(a))


if __name__ == "__main__":
    main()
