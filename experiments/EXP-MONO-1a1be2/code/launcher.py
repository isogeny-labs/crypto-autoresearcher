#!/usr/bin/env python3
"""Per-cell runner for EXP-MONO-1a1be2 (TASK-20261029-a97206, IM-8).

Two entry points:

  launcher.py selftest
      After approval: check_approval, then the start-up known-answer suite (isolated from repository
      configuration, "pass in full" checked against EXPECTED_KAT_ITEMS and DESIGNED_SKIPS). Writes
      experiments/EXP-MONO-1a1be2/selftest-receipts/<receipt_id>/{receipt.json,junit.xml}.

  launcher.py cell --cell-id ID --plan PLAN.json --run-id RUN-ID [--workers K] [--selftest-receipt PATH]
      A contract cell. REFUSED unless the specification is approved (approved_by set, execution_authorized and
      frozen true) and approval.lock binds the specification, code (seven files), tests/test_kat.py and the plan
      (JSON: approved_by, specification_sha256, code_sha256, trial_plan_sha256, test_file_sha256). The start-up
      suite then runs (or a launcher-written receipt for this host is accepted; any receipt failure refuses).
      Arm-A cells are refused while runs/STOP-F2.json exists. Writes experiments/EXP-MONO-1a1be2/runs/<RUN-ID>/
      (manifest.yaml with gate, startup_selftest and validity blocks, command.txt, environment.json, stdout.log,
      stderr.log, raw-result.json, summary.json, selftest/, and results/<cell_id>.cdf.json for arm C).

  launcher.py --kat kat --arm {A,B,C} --q Q --n N [--m M] --curve-seed STR [...]
      A known-answer cell, explicit flag, written under a temporary directory and never under runs/. Refused
      for any (q, n) that is an arm-A/arm-B or arm-C contract cell (KAT cells are disjoint from the contract).
      Derived statistics (ratios, coverage, frequencies) are withheld in KAT mode; only raw counts are written.

Nothing here is a run until a cell is executed through `cell`. Library functions (run_cell) are used by the
tests on KAT cells only.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime
import hashlib
import itertools
import json
import math
import os
import platform
import re
import resource
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import xml.etree.ElementTree as ET
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
EXIT_REFUSED = 3
EXIT_SELFTEST = 4

# FX-11 (5): code/ may hold only these .py files (relative paths, '/' separated). A stray numpy.py or yaml.py in
# code/ would shadow a library on `sys.path.insert(0, HERE)` while being hashed by nothing, so the check runs
# BEFORE any import that sys.path could redirect. No conftest.py and no tests/__init__.py existed at 72f51766a6.
EXPECTED_PY_FILES = ("fqn.py", "curves.py", "semaev.py", "counters.py", "launcher.py", "make_trial_plan.py",
                     "throughput_calibration.py", "tests/test_kat.py", "tests/test_kat_extended.py")


def stray_python_files(code_dir: str) -> list:
    """Relative paths of every .py file under code_dir that is not in EXPECTED_PY_FILES (sorted)."""
    found = []
    for root, dirs, files in os.walk(code_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if f.endswith(".py"):
                rel = os.path.relpath(os.path.join(root, f), code_dir).replace(os.sep, "/")
                if rel not in EXPECTED_PY_FILES:
                    found.append(rel)
    return sorted(found)


_STRAY = stray_python_files(HERE)
if _STRAY:
    print("REFUSED: code/ holds .py files outside the expected set: " + ", ".join(_STRAY), file=sys.stderr)
    sys.exit(EXIT_REFUSED)

sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import counters  # noqa: E402
import curves  # noqa: E402
import fqn  # noqa: E402
import make_trial_plan as mtp  # noqa: E402
import semaev  # noqa: E402

EXP_DIR = os.path.abspath(os.path.join(HERE, ".."))
EXP_ID = "EXP-MONO-1a1be2"
SPEC_PATH = os.path.join(EXP_DIR, "specification.yaml")
LOCK_PATH = os.path.join(EXP_DIR, "approval.lock")
RUNS_DIR = os.path.join(EXP_DIR, "runs")
CODE_FILES = ["fqn.py", "curves.py", "semaev.py", "counters.py", "kernel.c", "launcher.py", "make_trial_plan.py"]
TEST_FILE = os.path.join(HERE, "tests", "test_kat.py")
RECEIPTS_DIR = os.path.join(EXP_DIR, "selftest-receipts")
STOP_F2_NAME = "STOP-F2.json"
RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")

# FX-4: the start-up suite's expected size and designed skips. EXPECTED_KAT_ITEMS is the collected count of
# tests/test_kat.py (a test checks it against a fresh collection). DESIGNED_SKIPS maps the specification status
# to the node ids that are skipped by design: none before approval; after approval, the one refusal test that
# needs a not-yet-approved specification.
EXPECTED_KAT_ITEMS = 379
SKIP_NODE_REFUSAL = "tests/test_kat.py::test_launcher_refuses_contract_cell_while_specification_not_approved"
DESIGNED_SKIPS = {"approved": (SKIP_NODE_REFUSAL,)}


def designed_skips(status) -> list:
    return sorted(DESIGNED_SKIPS.get(status, ()))


# ----------------------------------------------------------------------------- contract pairs (KX-6)
def arm_c_pairs() -> set:
    """The arm-C (q_n, n) pairs by the trial-plan rule (least prime p > 3 with p^n >= 2^30)."""
    return {(mtp.q_rule(n), n) for n in mtp.ARM_C_NS}


def contract_pairs() -> set:
    """Every contract (q, n) pair: arm A (hence arm B) and arm C. A KAT cell must be disjoint from all."""
    return mtp.contract_cells_qn() | arm_c_pairs()


# ----------------------------------------------------------------------------- hashes and gate
def sha256_file(path: str) -> str:
    return counters.file_sha256(path)


def code_sha256() -> str:
    """One digest over the code files (name and sha256 of each, in the fixed order of CODE_FILES)."""
    h = hashlib.sha256()
    for name in CODE_FILES:
        h.update(f"{name}:{sha256_file(os.path.join(HERE, name))}\n".encode())
    return h.hexdigest()


def _sha_or_none(path: str):
    try:
        return sha256_file(path)
    except OSError:
        return None


def code_file_hashes() -> dict:
    return {name: sha256_file(os.path.join(HERE, name)) for name in CODE_FILES}


def check_approval(spec_path: str | None = None, lock_path: str | None = None, plan_path: str | None = None,
                   test_file: str | None = None):
    """(ok, reasons). The specification must be approved (status approved, approved_by set,
    execution_authorized true, frozen true) and the lock must exist and bind the current specification, code,
    test file and trial plan (FX-2, FX-11 (1)). The lock's approved_by must equal the specification's."""
    import yaml
    spec_path = spec_path or SPEC_PATH
    lock_path = lock_path or LOCK_PATH
    test_file = test_file or TEST_FILE
    reasons = []
    try:
        with open(spec_path) as fh:
            spec = yaml.safe_load(fh)
        exp = spec.get("experiment", {})
    except Exception as e:  # noqa: BLE001
        return False, [f"cannot read specification: {e}"]
    if exp.get("status") != "approved":
        reasons.append(f"specification status is {exp.get('status')!r}, not 'approved'")
    if not exp.get("approved_by"):
        reasons.append("specification approved_by is null")
    if exp.get("execution_authorized") is not True:
        reasons.append(f"specification execution_authorized is {exp.get('execution_authorized')!r}, not true")
    if exp.get("frozen") is not True:
        reasons.append(f"specification frozen is {exp.get('frozen')!r}, not true")
    if not os.path.exists(lock_path):
        reasons.append("approval lock missing: " + os.path.relpath(lock_path, os.path.dirname(spec_path)))
    else:
        try:
            with open(lock_path) as fh:
                lock = json.load(fh)
        except Exception as e:  # noqa: BLE001
            lock = {}
            reasons.append(f"approval lock unreadable: {e}")
        # Every field is checked unconditionally: an empty or non-object lock binds nothing and must refuse.
        if not isinstance(lock, dict) or not lock:
            reasons.append("approval lock is empty or not a JSON object")
            lock = {}
        if not lock.get("approved_by"):
            reasons.append("approval lock has no approved_by")
        elif lock.get("approved_by") != exp.get("approved_by"):
            reasons.append("approval lock approved_by differs from the specification's approved_by")
        if lock.get("specification_sha256") != sha256_file(spec_path):
            reasons.append("approval lock specification_sha256 differs from the specification on disk")
        if lock.get("code_sha256") != code_sha256():
            reasons.append("approval lock code_sha256 differs from the code on disk (invalid build)")
        if not lock.get("test_file_sha256"):
            reasons.append("approval lock has no test_file_sha256")
        elif lock.get("test_file_sha256") != _sha_or_none(test_file):
            reasons.append("approval lock test_file_sha256 differs from tests/test_kat.py on disk")
        if plan_path is not None and lock.get("trial_plan_sha256") != _sha_or_none(plan_path):
            reasons.append("approval lock trial_plan_sha256 differs from the trial plan passed")
    return (not reasons), reasons


def spec_status(spec_path: str | None = None):
    import yaml
    with open(spec_path or SPEC_PATH) as fh:
        return (yaml.safe_load(fh) or {}).get("experiment", {}).get("status")


# ----------------------------------------------------------------------------- start-up self-test (F-1)
def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cpu_model() -> str:
    try:
        with open("/proc/cpuinfo") as fh:
            for line in fh:
                if line.lower().startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "unknown"


def env_key() -> dict:
    """The environment key a receipt is bound to (FX-5): interpreter, numpy, pytest, compiler (path, version
    hash, flags) and the host. A receipt from another host or toolchain does not match."""
    import numpy
    import pytest
    rec = counters.compiler_record()
    ver = subprocess.run([rec["compiler"], "--version"], capture_output=True, text=True).stdout
    return {"python_version": sys.version, "numpy": numpy.__version__, "pytest": pytest.__version__,
            "compiler_path": rec["compiler"], "compiler_version_sha256": hashlib.sha256(ver.encode()).hexdigest(),
            "compile_flags": list(rec["flags"]), "machine": platform.machine(), "node": platform.node(),
            "kernel_release": platform.release(), "cpu_model": cpu_model()}


def selftest_environment(code_dir: str) -> dict:
    """FX-3: the self-test subprocess environment. Plugin autoload off, no bytecode, PYTEST_ADDOPTS and
    PYTEST_PLUGINS removed, and PYTHONPATH reduced to the entries inside the code directory."""
    env = dict(os.environ)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.pop("PYTEST_ADDOPTS", None)
    env.pop("PYTEST_PLUGINS", None)
    root = os.path.realpath(code_dir)
    keep = [p for p in env.get("PYTHONPATH", "").split(os.pathsep)
            if p and (os.path.realpath(p) == root or os.path.realpath(p).startswith(root + os.sep))]
    if keep:
        env["PYTHONPATH"] = os.pathsep.join(keep)
    else:
        env.pop("PYTHONPATH", None)
    return env


def _suite_argv(code_dir: str, extra: list) -> list:
    return [sys.executable, "-m", "pytest"] + extra + ["-p", "no:cacheprovider", "--noconftest", "-c", os.devnull,
                                                         "--rootdir", code_dir]


def parse_junit(path: str, code_dir: str | None = None) -> dict:
    """tests, failures, errors, skipped node ids, xfail count and testcase count of a junit XML file."""
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    out = {"tests": 0, "failures": 0, "errors": 0, "skipped_ids": [], "xfail": 0, "testcases": 0}
    for s in suites:
        out["tests"] += int(s.get("tests", 0))
        out["failures"] += int(s.get("failures", 0))
        out["errors"] += int(s.get("errors", 0))
        for tc in s.iter("testcase"):
            out["testcases"] += 1
            for sk in tc.findall("skipped"):
                if sk.get("type") == "pytest.xfail":
                    out["xfail"] += 1
                else:
                    out["skipped_ids"].append(tc.get("classname", "").replace(".", "/") + ".py::" + tc.get("name", ""))
    out["skipped_ids"].sort()
    out["passed"] = out["tests"] - out["failures"] - out["errors"] - len(out["skipped_ids"]) - out["xfail"]
    return out


def evaluate_suite(junit_path: str, expected_items: int, designed: list, rc: int | None = None,
                   stdout: str | None = None) -> tuple:
    """FX-4: (ok, reasons, parsed). The suite passed in full only if the exit code is 0 (when given), the junit
    test count equals expected_items, failures and errors are 0, there is no xfail or xpass, and the skipped node
    ids equal the designed skips."""
    reasons = []
    try:
        j = parse_junit(junit_path)
    except Exception as e:  # noqa: BLE001
        return False, [f"junit unreadable: {e}"], {}
    if rc is not None and rc != 0:
        reasons.append(f"pytest exit code {rc}")
    if j["tests"] != expected_items or j["testcases"] != expected_items:
        reasons.append(f"collected/ran {j['tests']} items (testcases {j['testcases']}), expected {expected_items}")
    if j["failures"] or j["errors"]:
        reasons.append(f"failures {j['failures']}, errors {j['errors']}")
    if j["xfail"]:
        reasons.append(f"{j['xfail']} xfail")
    if stdout is not None:
        m = re.search(r"\d+ (xfailed|xpassed|deselected)", stdout)
        if m:
            reasons.append("pytest summary reports " + m.group(0))
    if sorted(j["skipped_ids"]) != sorted(designed):
        reasons.append(f"skipped node ids {j['skipped_ids']} differ from the designed skips {sorted(designed)}")
    return (not reasons), reasons, j


def run_selftest_suite(out_dir: str, test_file: str | None = None, code_dir: str | None = None,
                       expected_items: int | None = None, designed: list | None = None,
                       spec_path: str | None = None) -> dict:
    """FX-3 and FX-4: run the suite isolated from repository configuration; write junit.xml into out_dir.
    Returns {passed, reasons, parsed, junit_path, rc, stdout_tail, rootdir, inifile, collected, pytest_version,
    started_utc, finished_utc}."""
    test_file = test_file or TEST_FILE
    code_dir = code_dir or HERE
    expected_items = EXPECTED_KAT_ITEMS if expected_items is None else expected_items
    if designed is None:
        designed = designed_skips(spec_status(spec_path))
    os.makedirs(out_dir, exist_ok=True)
    junit = os.path.join(out_dir, "junit.xml")
    env = selftest_environment(code_dir)
    started = _utc_now()
    r = subprocess.run(_suite_argv(code_dir, ["-q"]) + ["--junitxml", junit, test_file],
                       capture_output=True, text=True, env=env, cwd=code_dir)
    finished = _utc_now()
    c = subprocess.run(_suite_argv(code_dir, ["--collect-only"]) + [test_file],
                       capture_output=True, text=True, env=env, cwd=code_dir)
    hdr = c.stdout
    rootdir = (re.search(r"^rootdir: (.*)$", hdr, re.M) or [None, None])[1]
    inifile = (re.search(r"^configfile: (.*)$", hdr, re.M) or [None, None])[1]
    collected = re.search(r"collected (\d+) items?", hdr)
    collected = int(collected.group(1)) if collected else None
    pv = (re.search(r"pytest-([0-9][^,\s]*)", hdr) or [None, None])[1]
    if not os.path.exists(junit):
        ok, reasons, parsed = False, ["no junit.xml written (pytest exit %s)" % r.returncode], {}
    else:
        ok, reasons, parsed = evaluate_suite(junit, expected_items, designed, r.returncode, r.stdout)
    if collected != expected_items:
        ok = False
        reasons.append(f"collection reports {collected} items, expected {expected_items}")
    return {"passed": ok, "reasons": reasons, "parsed": parsed, "junit_path": junit, "rc": r.returncode,
            "stdout_tail": (r.stdout + r.stderr)[-3000:], "rootdir": rootdir, "inifile": inifile,
            "collected": collected, "pytest_version": pv, "started_utc": started, "finished_utc": finished}


RECEIPT_FIELDS = ("receipt_version", "code_sha256", "test_file_sha256", "lock_sha256", "junit_sha256", "counts",
                  "skipped_node_ids", "pytest_version", "rootdir", "inifile", "started_utc", "finished_utc", "env_key",
                  "expected_items", "designed_skips")


def write_selftest_receipt(receipts_root: str | None = None, spec_path: str | None = None,
                           lock_path: str | None = None, test_file: str | None = None,
                           expected_items: int | None = None, designed: list | None = None,
                           code_dir: str | None = None) -> tuple:
    """The selftest subcommand: check_approval, then the suite; on a full pass write receipt.json and junit.xml
    into <receipts_root>/<receipt_id>/. Returns (exit_code, receipt_path or None, messages)."""
    receipts_root = receipts_root or RECEIPTS_DIR
    spec_path = spec_path or SPEC_PATH
    lock_path = lock_path or LOCK_PATH
    test_file = test_file or TEST_FILE
    code_dir = code_dir or HERE
    ok, reasons = check_approval(spec_path, lock_path, None, test_file)
    if not ok:
        return EXIT_REFUSED, None, ["REFUSED: selftest not startable:"] + ["  - " + r for r in reasons]
    expected_items = EXPECTED_KAT_ITEMS if expected_items is None else expected_items
    designed = designed_skips(spec_status(spec_path)) if designed is None else designed
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rid = f"{stamp}-{code_sha256()[:8]}"
    rdir = os.path.join(receipts_root, rid)
    os.makedirs(rdir)                                   # never overwrites an existing receipt directory
    res = run_selftest_suite(rdir, test_file, code_dir, expected_items, designed, spec_path)
    if not res["passed"]:
        return EXIT_SELFTEST, None, ["REFUSED: start-up known-answer suite did not pass in full:"] + \
            ["  - " + r for r in res["reasons"]] + [res["stdout_tail"]]
    p = res["parsed"]
    rec = {"receipt_version": 1, "code_sha256": code_sha256(), "test_file_sha256": sha256_file(test_file),
           "lock_sha256": sha256_file(lock_path), "junit_sha256": sha256_file(res["junit_path"]),
           "counts": {"tests": p["tests"], "passed": p["passed"], "failures": p["failures"],
                      "errors": p["errors"], "skipped": len(p["skipped_ids"]), "xfail": p["xfail"]},
           "skipped_node_ids": p["skipped_ids"], "pytest_version": res["pytest_version"],
           "rootdir": res["rootdir"], "inifile": res["inifile"], "started_utc": res["started_utc"],
           "finished_utc": res["finished_utc"], "env_key": env_key(), "expected_items": expected_items,
           "designed_skips": sorted(designed)}
    path = os.path.join(rdir, "receipt.json")
    with open(path, "w") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
        fh.write("\n")
    return 0, path, [json.dumps({"receipt": path})]


def verify_receipt(path: str, receipts_root: str | None = None, spec_path: str | None = None,
                   lock_path: str | None = None, test_file: str | None = None, expected_items: int | None = None,
                   designed: list | None = None, code_dir: str | None = None) -> tuple:
    """FX-5: (ok, reasons, receipt, junit_path). Accepts only a receipt.json that resolves inside receipts_root
    and whose every recomputable field equals a recomputation on this host."""
    receipts_root = receipts_root or RECEIPTS_DIR
    spec_path = spec_path or SPEC_PATH
    lock_path = lock_path or LOCK_PATH
    test_file = test_file or TEST_FILE
    code_dir = code_dir or HERE
    expected_items = EXPECTED_KAT_ITEMS if expected_items is None else expected_items
    designed = designed_skips(spec_status(spec_path)) if designed is None else designed
    bad = []
    real = os.path.realpath(path)
    root = os.path.realpath(receipts_root)
    if not real.startswith(root + os.sep):
        return False, [f"receipt {path} does not resolve inside {receipts_root}"], None, None
    if os.path.basename(real) != "receipt.json" or not os.path.isfile(real):
        return False, [f"receipt {path} is not a receipt.json file"], None, None
    try:
        with open(real) as fh:
            rec = json.load(fh)
    except Exception as e:  # noqa: BLE001
        return False, [f"receipt unreadable: {e}"], None, None
    if not isinstance(rec, dict):
        return False, ["receipt is not a JSON object"], None, None
    if set(rec) != set(RECEIPT_FIELDS):
        bad.append(f"receipt fields differ: missing {sorted(set(RECEIPT_FIELDS) - set(rec))}, "
                   f"extra {sorted(set(rec) - set(RECEIPT_FIELDS))}")
        return False, bad, rec, None
    junit = os.path.join(os.path.dirname(real), "junit.xml")
    if not os.path.isfile(junit):
        return False, ["junit.xml beside the receipt is missing"], rec, None
    if rec["receipt_version"] != 1:
        bad.append("receipt_version is not 1")
    for k, want in (("code_sha256", code_sha256()), ("test_file_sha256", sha256_file(test_file)),
                    ("lock_sha256", sha256_file(lock_path)), ("junit_sha256", sha256_file(junit)),
                    ("expected_items", expected_items), ("designed_skips", sorted(designed)),
                    ("env_key", env_key())):
        if rec[k] != want:
            bad.append(f"receipt {k} differs from a recomputation on this host")
    ok, reasons, j = evaluate_suite(junit, expected_items, designed)
    bad += [f"junit: {r}" for r in reasons]
    if j and (rec["counts"] != {"tests": j["tests"], "passed": j["passed"], "failures": j["failures"],
                                "errors": j["errors"], "skipped": len(j["skipped_ids"]), "xfail": j["xfail"]}
              or rec["skipped_node_ids"] != j["skipped_ids"]):
        bad.append("receipt counts or skipped node ids differ from the junit.xml beside it")
    try:
        import pytest
        if rec["pytest_version"] != pytest.__version__:
            bad.append("receipt pytest_version differs from this host")
    except Exception:  # noqa: BLE001
        bad.append("pytest not importable")
    if not isinstance(rec["rootdir"], str) or os.path.realpath(rec["rootdir"]) != os.path.realpath(code_dir):
        bad.append("receipt rootdir is not the code directory")
    if not isinstance(rec["inifile"], str) or os.path.realpath(os.path.join(rec["rootdir"] or "", rec["inifile"])) \
            != os.path.realpath(os.devnull):
        bad.append("receipt inifile is not the null configuration")
    for k in ("started_utc", "finished_utc"):
        try:
            datetime.datetime.strptime(rec[k], "%Y-%m-%dT%H:%M:%SZ")
        except Exception:  # noqa: BLE001
            bad.append(f"receipt {k} is not a UTC timestamp")
    return (not bad), bad, rec, junit


# ----------------------------------------------------------------------------- the gate (FX-5, FX-6)
class GateRefused(Exception):
    def __init__(self, reasons, exit_code=EXIT_REFUSED):
        super().__init__("; ".join(reasons))
        self.reasons = list(reasons)
        self.exit_code = exit_code


_GATE_TOKEN = object()


@dataclasses.dataclass(frozen=True)
class GateResult:
    """What gate() returns. run_cell(kat=False) refuses unless given one."""
    specification_sha256: str
    lock_sha256: str
    trial_plan_sha256: str
    code_sha256: str
    test_file_sha256: str
    check_approval_passed: bool
    startup_selftest: dict
    selftest_files: dict
    _token: object = dataclasses.field(default=None, repr=False, compare=False)


def gate(plan_path: str, receipt_path: str | None = None, *, spec_path: str | None = None,
         lock_path: str | None = None, test_file: str | None = None, expected_items: int | None = None,
         designed: list | None = None, receipts_root: str | None = None, code_dir: str | None = None,
         scratch_dir: str | None = None) -> GateResult:
    """check_approval, then the start-up self-test (run here, or an accepted receipt). Raises GateRefused with
    the exit code on any failure; a receipt that fails a check refuses (it never falls through to a run)."""
    spec_path = spec_path or SPEC_PATH
    lock_path = lock_path or LOCK_PATH
    test_file = test_file or TEST_FILE
    code_dir = code_dir or HERE
    expected_items = EXPECTED_KAT_ITEMS if expected_items is None else expected_items
    ok, reasons = check_approval(spec_path, lock_path, plan_path, test_file)
    if not ok:
        raise GateRefused(reasons, EXIT_REFUSED)
    designed = designed_skips(spec_status(spec_path)) if designed is None else designed
    if receipt_path:
        rok, rr, rec, junit = verify_receipt(receipt_path, receipts_root, spec_path, lock_path, test_file,
                                             expected_items, designed, code_dir)
        if not rok:
            raise GateRefused(["selftest receipt refused:"] + rr, EXIT_REFUSED)
        p = parse_junit(junit)
        st = {"mode": "receipt", "receipt_sha256": sha256_file(os.path.realpath(receipt_path)),
              "junit_sha256": sha256_file(junit), "tests": p["tests"], "passed": p["passed"],
              "skipped_node_ids": p["skipped_ids"], "failures": p["failures"], "errors": p["errors"],
              "pytest_version": rec["pytest_version"], "rootdir": rec["rootdir"], "inifile": rec["inifile"],
              "env_key": rec["env_key"]}
        files = {"junit.xml": junit, "receipt.json": os.path.realpath(receipt_path)}
    else:
        sdir = tempfile.mkdtemp(prefix="mono1a1be2-selftest-", dir=scratch_dir)
        res = run_selftest_suite(sdir, test_file, code_dir, expected_items, designed, spec_path)
        if not res["passed"]:
            raise GateRefused(["start-up known-answer suite did not pass in full:"] + res["reasons"]
                              + [res["stdout_tail"]], EXIT_SELFTEST)
        p = res["parsed"]
        st = {"mode": "ran", "receipt_sha256": None, "junit_sha256": sha256_file(res["junit_path"]),
              "tests": p["tests"], "passed": p["passed"], "skipped_node_ids": p["skipped_ids"],
              "failures": p["failures"], "errors": p["errors"], "pytest_version": res["pytest_version"],
              "rootdir": res["rootdir"], "inifile": res["inifile"], "env_key": env_key()}
        files = {"junit.xml": res["junit_path"]}
    return GateResult(specification_sha256=sha256_file(spec_path), lock_sha256=sha256_file(lock_path),
                      trial_plan_sha256=sha256_file(plan_path), code_sha256=code_sha256(),
                      test_file_sha256=sha256_file(test_file), check_approval_passed=True,
                      startup_selftest=st, selftest_files=files, _token=_GATE_TOKEN)


def _require_gate(g) -> None:
    if not isinstance(g, GateResult) or g._token is not _GATE_TOKEN or not g.check_approval_passed:
        raise PermissionError("run_cell(kat=False) requires the GateResult returned by launcher.gate()")



# ----------------------------------------------------------------------------- environment record
def git_state() -> dict:
    root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    def g(*args):
        r = subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True)
        return r.returncode, r.stdout.strip()
    rc, head = g("rev-parse", "HEAD")
    if rc != 0:
        return {"commit": None, "dirty": None, "note": "git state unavailable at " + root}
    rc2, st = g("status", "--porcelain")
    return {"commit": head, "dirty": bool(st) if rc2 == 0 else None,
            "dirty_paths_count": len(st.splitlines()) if rc2 == 0 else None}


def environment_record() -> dict:
    import numpy
    try:
        import yaml
        yv = yaml.__version__
    except Exception:  # noqa: BLE001
        yv = None
    try:
        import pytest
        pv = pytest.__version__
    except Exception:  # noqa: BLE001
        pv = None
    u = platform.uname()
    return {
        "interpreter": {"executable": sys.executable, "version": sys.version, "implementation": platform.python_implementation()},
        "libraries": {"numpy": numpy.__version__, "pyyaml": yv, "pytest": pv},
        "compiler": counters.compiler_record(),
        "host": {"system": u.system, "release": u.release, "machine": u.machine, "node": u.node,
                 "cpu_count": os.cpu_count()},
        "git": git_state(),
        "code_sha256": code_sha256(), "code_file_sha256": code_file_hashes(),
        "random_sources": ["numpy PCG64 seeded per the specification seed rules (curves, bases, tuples, targets)",
                           "random.Random(20261029) choosing points in baby-step giant-step (does not affect N)",
                           "random.Random(20261029) in Cantor-Zassenhaus root splitting (does not affect the root set)"],
    }


# ----------------------------------------------------------------------------- cell execution
def _hist_str(h):
    return {str(k): v for k, v in sorted(h.items())}


def build_instance(q: int, n: int, curve_seed_string: str, expect: dict | None = None):
    F = fqn.FQ(q, n)
    E, info = curves.generate_curve(F, curve_seed_string)
    if expect is not None:
        for key, val in (("g", list(F.g)), ("a", list(E.a)), ("b", list(E.b))):
            if expect.get(key) != val:
                raise RuntimeError(f"identity mismatch for {key}: plan {expect.get(key)} vs regenerated {val}")
    return F, E, info


def _cell_summary_arm_a(res: dict, derived: bool):
    out = {}
    for role, r in res.items():
        d = {"B": r["B"], "t2": r["t2"], "N": r["N"], "size_X": r["size_X"], "S_size": r["S_size"],
             "generic_targets": r["generic_targets"], "special_targets": r["special_targets_O_and_E2"],
             "recount": r["recount"]}
        if "identities" in r:
            d["identities"] = r["identities"]
            if derived:                      # KX-5: the composition residuals P2(vii) to (ix), named in the summary
                d["composition_residuals"] = {k: v for k, v in r["identities"].items()
                                              if k.startswith(("vii_", "viii_", "ix_"))}
        if derived:
            conv = {}
            for c in ("A", "M", "S", "X"):
                st = r["conventions"][c]["stats"]
                conv[c] = {"mean_all": str(Fraction(st["all"]["sum"], st["all"]["targets"])),
                           "mean_generic": (str(Fraction(st["generic"]["sum"], st["generic"]["targets"]))
                                            if st["generic"]["targets"] else None),
                           "coverage_generic": ([st["generic"]["targets"] - st["generic"]["zeros"], st["generic"]["targets"]])}
            d["derived"] = conv
        out[role] = d
    return out


def run_arm_a(spec: dict, kernel, derived: bool, log):
    q, n, m = spec["q"], spec["n"], spec["m"]
    F, E, info = build_instance(q, n, spec["curve_seed"], spec.get("identity"))
    N, mask = kernel.valid_mask(E)
    if spec.get("identity") and spec["identity"].get("N") not in (None, N):
        raise RuntimeError(f"N mismatch: plan {spec['identity']['N']} vs counted {N}")
    D, X, t2 = E.factor_base()
    B = len(D)
    log(f"arm A cell {spec['cell_id']}: q={q} n={n} m={m} N={N} B={B} t2={t2} |X|={len(X)}")
    bases = {"line": D}
    seeds = spec.get("base_seeds", {})
    if "matched_random" in seeds:
        bases["matched_random"] = counters.matched_random_base(E, B, t2, curves.make_rng(seeds["matched_random"]))
    if "half_twin" in seeds:
        bases["half_twin"] = counters.twin_base(E, B, t2, curves.make_rng(seeds["half_twin"]))
    if "matched_random_reseeded_aa" in seeds:
        bases["matched_random_reseeded_aa"] = counters.matched_random_base(
            E, B, t2, curves.make_rng(seeds["matched_random_reseeded_aa"]))
    results = {}
    for role, pts in bases.items():
        Xl = counters.x_lifts(F, pts)
        t0 = time.perf_counter()
        results[role] = counters.exhaustive_cell(kernel, E, pts, Xl, m, N, mask, recount=True)
        results[role]["wall_seconds"] = time.perf_counter() - t0
        if not derived:                      # KAT mode: no cross-convention comparison is written
            results[role].pop("identities", None)
        log(f"  base {role}: B={len(pts)} done in {results[role]['wall_seconds']:.2f}s")
    raw = {"arm": "A", "cell_id": spec["cell_id"], "N": N, "curve_generation": info, "bases": results,
           "conventions_definition": "see counters.py module docstring"}
    return raw, _cell_summary_arm_a(results, derived), None


def arm_c_entry(r: dict, base_size: int, derived: bool, wall: float, target_seed: str | None = None,
                base_seed: str | None = None) -> dict:
    """Per-base record of an arm-C cell from the counter's output dict (pure function of `r`). lambda,
    lambda_exact, N_cf_formula and ncf_counted_equals_formula are derived statistics: written only when derived
    (FX-10). The seeds that define the sample are recorded as string and integer (FX-11 (3))."""
    counts = np.asarray(r["sampled_counts"])
    hist = {int(c): int(v) for c, v in zip(*np.unique(counts.astype(np.int64), return_counts=True))}
    entry = {"B": base_size, "t2": r["t2"], "S_size": r["S_size"], "draws": r["draws"],
             "multisets": r["multisets"], "cancellation_free_multisets": r["cancellation_free"], "m_S": r["m_S"],
             "hist": _hist_str(hist), "exceptional_targets": [int(c) for c in r["S_counts"]],
             "wall_seconds": wall,
             "target_seed": {"string": target_seed, "int": curves.seed_int(target_seed) if target_seed else None},
             "base_seed": {"string": base_seed, "int": curves.seed_int(base_seed) if base_seed else None}}
    if derived:
        entry["N_cf_formula"] = str(r["N_cf_formula"])
        entry["ncf_counted_equals_formula"] = bool(r.get("ncf_counted_equals_formula",
                                                         r["cancellation_free"] == r["N_cf_formula"]))
        entry["lambda_exact"] = [r["lambda"].numerator, r["lambda"].denominator]
        entry["lambda"] = float(r["lambda"])
        entry["poisson"] = counters.poisson_summary(counts, float(r["lambda"]))
    return entry


CDF_POISSON_KEYS = ("cdf_empirical", "cdf_poisson", "ks_stat", "chi2_stat", "chi2_df", "zero_fraction", "coverage",
                    "dispersion_index", "max_count", "p_max_pred")


def arm_c_flat(entry: dict, derived: bool) -> dict:
    """Flatten a per-base record into the IDEA machine_readable_output key layout (pure)."""
    flat = {k: v for k, v in entry.items() if k != "poisson"}
    if derived:
        flat.update({k: entry["poisson"][k] for k in CDF_POISSON_KEYS})
    return flat


def _summary_arm_c(cell_id, s, B, t2, N, raw_bases, derived):
    """The arm-C summary as a pure function of the raw per-base records (also used to re-derive it, FX-8)."""
    def one(v):
        d = {"multisets": v["multisets"], "cancellation_free_multisets": v["cancellation_free_multisets"],
             "m_S": v["m_S"], "max_count": max(int(c) for c in v["hist"])}
        if derived:
            d["lambda_exact"] = v["lambda_exact"]
            d["poisson"] = {k2: v["poisson"][k2] for k2 in ("coverage", "zero_fraction", "dispersion_index", "ks_stat",
                                                            "chi2_stat", "chi2_df", "max_count", "p_max_pred")}
        return d
    return {"cell_id": cell_id, "s": s, "B": B, "t2": t2, "N": N, "bases": {k: one(v) for k, v in raw_bases.items()}}


def run_arm_c(spec: dict, kernel, derived: bool, log):
    q, n, m, s = spec["q"], spec["n"], spec["m"], spec["s"]
    F, E, info = build_instance(q, n, spec["curve_seed"], spec.get("identity"))
    if F.Q < 2 ** 27:
        N, method = kernel.count_points(E), "exhaustive_kernel"
    else:
        N, _ = E.count_points_bsgs()
        method = "bsgs"
    if spec.get("identity") and spec["identity"].get("N") not in (None, N):
        raise RuntimeError(f"N mismatch: plan {spec['identity']['N']} vs counted {N}")
    D, X, t2 = E.factor_base()
    B = len(D)
    log(f"arm C cell {spec['cell_id']}: q={q} n={n} m={m} s={s} N={N} B={B} t2={t2}")
    bases = {"line": D}
    if "matched_random" in spec.get("base_seeds", {}):
        bases["matched_random"] = counters.matched_random_base(
            E, B, t2, curves.make_rng(spec["base_seeds"]["matched_random"]))
    cdf = {"cell_id": spec["cell_id"], "n": n, "q": q, "curve_id": spec["curve_index"],
           "seed": spec["curve_seed"], "B": B, "t2": t2, "N": N, "s": s}
    raw_bases = {}
    for role, pts in bases.items():
        t0 = time.perf_counter()
        tr = curves.make_rng(spec["target_seed"])
        r = counters.arm_c_cell(kernel, E, pts, m, s, tr, N)
        entry = arm_c_entry(r, len(pts), derived, time.perf_counter() - t0, spec["target_seed"],
                            spec.get("base_seeds", {}).get(role))
        raw_bases[role] = entry
        flat = arm_c_flat(entry, derived)
        if role == "line":
            cdf.update(flat)                     # IDEA machine_readable_output keys, line base at top level
        else:
            cdf[role] = flat
        log(f"  base {role}: multisets={r['multisets']} done in {entry['wall_seconds']:.2f}s")
    raw = {"arm": "C", "cell_id": spec["cell_id"], "N": N, "N_method": method, "curve_generation": info,
           "bases": raw_bases}
    summary = _summary_arm_c(spec["cell_id"], s, B, t2, N, raw_bases, derived)
    return raw, summary, cdf


TALLY_KEYS = ("tuples", "zero_poly", "degree_deficient", "not_squarefree", "any_chi_zero", "eligible",
              "eligible_split", "eligible_all_chi_equal", "disagree", "gl_checked", "gl_checked_generic",
              "gl_mismatch_generic", "gl_mismatch_nongeneric", "gl_inf_sums")


def _analyse_block(args):
    """Worker: analyse a block of x-tuples (list of lists of code tuples). Returns tallies."""
    (q, n, g, a, b, xs_block, do_group_law_mask) = args
    F = fqn.FQ(q, n, tuple(g))
    E = curves.Curve(F, tuple(a), tuple(b))
    F2 = fqn.FQ2(F)
    patterns: dict = {}
    t = dict.fromkeys(TALLY_KEYS, 0)
    for tup, do_gl in zip(xs_block, do_group_law_mask):
        xs = [tuple(x) for x in tup]
        res = semaev.analyse_fibre(F, E, xs, detail=bool(do_gl))
        t["tuples"] += 1
        generic = False
        if res["zero_poly"]:
            t["zero_poly"] += 1
        else:
            if not res["full_degree"]:
                t["degree_deficient"] += 1
            if not res["squarefree"]:
                t["not_squarefree"] += 1
            generic = res["full_degree"] and res["squarefree"]
        status = "na"
        if 0 in res["chis"]:
            t["any_chi_zero"] += 1
        elif generic:
            t["eligible"] += 1
            split = bool(res["split_completely"])
            if do_gl and split != bool(res["split_check_xq"]):
                raise RuntimeError("ddf and x^Q-x split tests disagree (implementation error)")
            alleq = len(set(res["chis"])) == 1
            t["eligible_split"] += split
            t["eligible_all_chi_equal"] += alleq
            t["disagree"] += (split != alleq)
            status = "split" if split else "nonsplit"
        pat = "".join("+" if c == 1 else "-" if c == -1 else "0" for c in res["chis"]) + "|" + status
        patterns[pat] = patterns.get(pat, 0) + 1
        if do_gl:
            roots, ninf = semaev.roots_via_group_law(F, E, xs, F2)
            t["gl_checked"] += 1
            t["gl_inf_sums"] += ninf
            if generic:
                t["gl_checked_generic"] += 1
                t["gl_mismatch_generic"] += (roots != res["roots_Fq"])
            else:
                t["gl_mismatch_nongeneric"] += (roots != res["roots_Fq"])
    t["chi_patterns"] = patterns
    return t


def _sum_tallies(ts):
    # Start from zero counters so an instance with no tuples still yields a complete tally.
    out: dict = dict.fromkeys(TALLY_KEYS, 0)
    for t in ts:
        for k, v in t.items():
            if isinstance(v, dict):
                d = out.setdefault(k, {})
                for kk, vv in v.items():
                    d[kk] = d.get(kk, 0) + int(vv)
            else:
                out[k] = out.get(k, 0) + int(v)
    out["chi_patterns"] = dict(sorted(out.get("chi_patterns", {}).items()))
    return out


def _block(tuples, i, j):
    if isinstance(tuples, np.ndarray):
        return [[list(map(int, row)) for row in t] for t in tuples[i:j]]
    return [[list(x) for x in t] for t in tuples[i:j]]


def _analyse_all(F, E, tuples, gl_mask, workers: int):
    """Analyse every x-tuple (a list of tuples of field elements, or an (T, n, n) integer array) in blocks of
    2000, in order; tallies are sums, so the result does not depend on the number of workers."""
    block = 2000
    total = len(tuples)
    jobs = ((F.q, F.n, list(F.g), list(E.a), list(E.b), _block(tuples, i, min(i + block, total)),
             gl_mask[i:i + block]) for i in range(0, total, block))
    if workers > 1:
        import multiprocessing as mp
        with mp.Pool(workers) as pool:
            return _sum_tallies(pool.imap(_analyse_block, jobs))
    return _sum_tallies(_analyse_block(j) for j in jobs)


def run_arm_b(spec: dict, kernel, derived: bool, log, workers: int = 1):
    out_inst = []
    # B1 cells that carry tuple_seed_aa also run the independent A/A sample (CTL-aa, C-aa-tupleseed).
    samples = [("primary", spec["tuple_seed"])]
    if spec["arm"] == "B1" and spec.get("tuple_seed_aa"):
        samples.append(("aa", spec["tuple_seed_aa"]))
    for inst in spec["instances"]:
        q, n = inst["q"], spec["n"]
        F, E, info = build_instance(q, n, inst["curve_seed"], inst.get("identity"))
        D, X, t2 = E.factor_base()
        for sample, seed in samples:
            rng = curves.make_rng(seed)
            if spec["arm"] == "B1":
                T = spec["tuples"]
                xs = rng.integers(0, q, size=(T, n, n))
                step = max(int(round(1 / spec["group_law_subsample_fraction"])), 1)
                gl = [(i % step == 0) for i in range(T)]          # subsample rule: every step-th tuple
                tuples = xs
            else:
                maxT = spec["max_tuples_per_instance"]
                nx = len(X)
                if nx < n:
                    tuples = []
                elif math.comb(nx, n) <= maxT:
                    tuples = [[X[i] for i in c] for c in itertools.combinations(range(nx), n)]
                else:
                    tuples = []
                    for _ in range(maxT):
                        idx = sorted(int(i) for i in rng.choice(nx, size=n, replace=False))
                        tuples.append([X[i] for i in idx])
                gl = [True] * len(tuples)
            t0 = time.perf_counter()
            tally = _analyse_all(F, E, tuples, gl, workers)
            el = time.perf_counter() - t0
            log(f"  {spec['cell_id']} q={q} [{sample}]: {tally['tuples']} tuples in {el:.1f}s")
            entry = {"q": q, "n": n, "sample": sample, "tuple_seed": seed, "B": len(D), "t2": t2,
                     "size_X": len(X), "tally": tally, "wall_seconds": el, "curve_generation": info}
            if derived:
                el_n = tally["eligible"]
                entry["derived"] = {"split_fraction_of_eligible": (tally["eligible_split"], el_n),
                                    "disagreements": tally["disagree"]}
            out_inst.append(entry)
    raw = {"arm": spec["arm"], "cell_id": spec["cell_id"], "instances": out_inst}
    return raw, {"cell_id": spec["cell_id"],
                 "instances": [{"q": i["q"], "sample": i["sample"], "tally": i["tally"]} for i in out_inst]}, None


def _install_limits(timeout_seconds, memory_gb):
    import signal
    if memory_gb:
        lim = int(memory_gb * 2 ** 30)
        resource.setrlimit(resource.RLIMIT_AS, (lim, lim))
    if timeout_seconds:
        def _alarm(signum, frame):
            raise TimeoutError(f"watchdog: cell exceeded {timeout_seconds} s")
        signal.signal(signal.SIGALRM, _alarm)
        signal.setitimer(signal.ITIMER_REAL, float(timeout_seconds))


def _write_file(path: str, text: str) -> None:
    with open(path, "w") as fh:
        fh.write(text)


def _norm(x):
    """JSON round trip with sorted keys: the form in which raw and summary are compared."""
    return json.loads(json.dumps(x, sort_keys=True, default=str))


IDENTITY_KEYS = ("q", "n", "g", "a", "b", "N", "t2", "B", "size_X")
P6_WITHHELD_REASON = "P2(vi) mismatch; P6 reading withheld (F7 first)"
CTL_NULL_ROLES = ("matched_random", "matched_random_reseeded_aa")
F2_IDENTITY = "i_sum_M"          # CTL-null: all-target multiset mean equals C(B+n-1,n)/N, i.e. the sum identity


def _identities_of(spec: dict) -> list:
    """(q, n, identity dict or None) for every curve instance of the cell spec."""
    if spec["arm"] in ("A", "C"):
        return [(spec.get("q"), spec.get("n"), spec.get("identity"))]
    return [(i.get("q"), spec.get("n"), i.get("identity")) for i in spec.get("instances", [])]


def identity_and_curve_problems(spec: dict) -> tuple:
    """(invalid_reasons, void_reasons): identity-field completeness (invalid) and the curve selection rule
    (singular or j in F_q, void), the latter re-derived from the recorded g, a, b."""
    invalid, void = [], []
    for q, n, ident in _identities_of(spec):
        missing = [k for k in IDENTITY_KEYS if not isinstance(ident, dict) or ident.get(k) is None]
        seed = ident.get("curve_seed") if isinstance(ident, dict) else None
        if not (isinstance(seed, dict) and seed.get("seed_string")):
            missing.append("seed")
        if missing:
            invalid.append(f"identity field(s) missing for q={q}, n={n}: {sorted(set(missing))}")
            continue
        F = fqn.FQ(ident["q"], ident["n"], tuple(ident["g"]))
        E = curves.Curve(F, tuple(ident["a"]), tuple(ident["b"]))
        if E.is_singular():
            void.append(f"curve selection rule: singular curve at q={ident['q']}, n={ident['n']}")
        elif ident["n"] > 1 and E.j_in_Fq():
            void.append(f"curve selection rule: j in F_q at q={ident['q']}, n={ident['n']}")
    return invalid, void


def f2_failures(raw: dict) -> list:
    """CTL-null all-target identity failures of an arm-A raw result: (role, identity name, detail). A missing
    identity on a CTL-null base is reported as a failure to evaluate (kind 'absent')."""
    out = []
    for role, r in (raw or {}).get("bases", {}).items():
        if role not in CTL_NULL_ROLES:
            continue
        ident = (r.get("identities") or {}).get(F2_IDENTITY)
        if ident is None:
            out.append((role, F2_IDENTITY, "absent"))
        elif ident["observed"] != ident["expected"]:
            out.append((role, F2_IDENTITY, "differs"))
    return out


def summary_from_raw(spec: dict, raw: dict, derived: bool) -> dict:
    arm = spec["arm"]
    if arm == "A":
        return _cell_summary_arm_a(raw["bases"], derived)
    if arm == "C":
        line = raw["bases"]["line"]
        return _summary_arm_c(raw["cell_id"], spec["s"], line["B"], line["t2"], raw["N"], raw["bases"], derived)
    return {"cell_id": raw["cell_id"],
            "instances": [{"q": i["q"], "sample": i["sample"], "tally": i["tally"]} for i in raw["instances"]]}


def raw_summary_agreement(outdir: str, spec: dict, derived: bool) -> list:
    """Re-read what the launcher wrote and re-derive the summary (and, for arm C, the cdf.json) from raw-result.json.
    Returns the list of disagreements (empty when they agree)."""
    probs = []
    try:
        with open(os.path.join(outdir, "raw-result.json")) as fh:
            raw = json.load(fh)
        with open(os.path.join(outdir, "summary.json")) as fh:
            summ = json.load(fh)
    except Exception as e:  # noqa: BLE001
        return [f"raw-result.json or summary.json unreadable: {e}"]
    try:
        want = _norm(summary_from_raw(spec, raw, derived))
    except Exception as e:  # noqa: BLE001
        return [f"summary cannot be re-derived from raw-result.json: {e}"]
    if summ != want:
        probs.append("summary.json differs from the summary re-derived from raw-result.json")
    if spec["arm"] == "C":
        try:
            with open(os.path.join(outdir, "results", spec["cell_id"] + ".cdf.json")) as fh:
                cdf = json.load(fh)
            for role, entry in raw["bases"].items():
                flat = _norm(arm_c_flat(entry, derived))
                got = cdf if role == "line" else cdf.get(role, {})
                for k, v in flat.items():
                    if got.get(k) != v:
                        probs.append(f"cdf.json key {k!r} ({role}) differs from raw-result.json")
        except Exception as e:  # noqa: BLE001
            probs.append(f"cdf.json unreadable: {e}")
    return probs


def compute_validity(spec: dict, outdir: str, status: str, failure_class, derived: bool, raw) -> dict:
    """FX-8: validity {status valid|void|invalid, reasons, readings_withheld} from the R1 recount, the group-law
    mismatch counts, identity-field completeness, raw/summary agreement (re-read from disk), the curve
    selection rule and, for arm C, the P2(vi) equality flag. invalid outranks void outranks valid."""
    invalid, void, withheld, notes = [], [], [], []
    if status != "completed":
        void.append(f"execution {status} ({failure_class}); a failed cell is void, never evidence")
    i2, v2 = identity_and_curve_problems(spec)
    invalid += i2
    void += v2
    if status == "completed" and raw is not None:
        arm = spec["arm"]
        if arm == "A":
            for role, r in raw["bases"].items():
                rec = r.get("recount") or {}
                if not rec:
                    void.append(f"R1 recount absent for base {role}")
                for name, v in rec.items():
                    if v.get("differ", 0) or v.get("differ_second", 0):
                        void.append(f"R1 recount differs for base {role}, convention {name}")
        elif arm in ("B1", "B2"):
            for inst in raw["instances"]:
                t = inst["tally"]
                for k in ("gl_mismatch_generic", "gl_mismatch_nongeneric"):
                    if t.get(k, 0) > 0:
                        void.append(f"{k} = {t[k]} at q={inst['q']} [{inst['sample']}]")
        elif arm == "C":
            for role, e in raw["bases"].items():
                if derived and e.get("ncf_counted_equals_formula") is False:
                    withheld = ["P6"]
                    if P6_WITHHELD_REASON not in notes:
                        notes.append(P6_WITHHELD_REASON)
                    notes.append(f"N_cf counted != P2(vi) closed form at base {role}")
        for p in raw_summary_agreement(outdir, spec, derived):
            void.append(p)
    reasons = invalid + void + notes
    st = "invalid" if invalid else ("void" if void else "valid")
    return {"status": st, "reasons": reasons, "readings_withheld": withheld}


def write_stop_f2(runs_dir: str, cell_id: str, identity: str, role: str) -> str:
    """Write runs/STOP-F2.json (exclusive create: an existing sentinel is never overwritten)."""
    os.makedirs(runs_dir, exist_ok=True)
    path = os.path.join(runs_dir, STOP_F2_NAME)
    try:
        with open(path, "x") as fh:
            json.dump({"cell_id": cell_id, "identity": identity, "role": role, "utc": _utc_now()}, fh, sort_keys=True)
            fh.write("\n")
    except FileExistsError:
        pass
    return path


def run_cell(spec: dict, outdir: str, kat: bool, workers: int = 1, kernel=None, command: str = "",
             run_id: str | None = None, timeout_seconds: float | None = None, memory_gb: float | None = None,
             gate: GateResult | None = None) -> dict:
    """Execute one cell spec and write the run package into outdir. Returns the manifest dict. A contract-mode
    call (kat=False) must be given the GateResult that gate() returns (FX-6); it carries the gate and
    startup_selftest blocks, a validity block (FX-8) and, on an arm-A F2 failure, writes runs/STOP-F2.json."""
    if not kat:
        _require_gate(gate)
    os.makedirs(outdir, exist_ok=True)
    msgs, errs = [], []
    log = lambda s: msgs.append(s)  # noqa: E731
    tmp = None
    t_start = time.time()
    status, reason = "completed", None
    raw = summary = cdf = None
    try:
        _install_limits(timeout_seconds, memory_gb)
        if kernel is None:
            tmp = tempfile.mkdtemp(prefix="mono1a1be2-kernel-")
            kernel = counters.Kernel(counters.build_kernel(tmp))
        derived = not kat
        arm = spec["arm"]
        if arm == "A":
            raw, summary, cdf = run_arm_a(spec, kernel, derived, log)
        elif arm == "C":
            raw, summary, cdf = run_arm_c(spec, kernel, derived, log)
        elif arm in ("B1", "B2"):
            raw, summary, cdf = run_arm_b(spec, kernel, derived, log, workers)
        else:
            raise ValueError(f"unknown arm {arm}")
    except (TimeoutError, MemoryError):
        status, reason = "failed", "resource_exhaustion"
        errs.append(traceback.format_exc())
    except Exception:  # noqa: BLE001
        status, reason = "failed", "infrastructure_or_implementation_error"
        errs.append(traceback.format_exc())
    finally:
        try:
            import signal
            signal.setitimer(signal.ITIMER_REAL, 0)
        except Exception:  # noqa: BLE001
            pass
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
    env = environment_record()
    rs, rc_ = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    manifest = {
        "experiment_id": EXP_ID, "run_id": run_id, "cell_id": spec["cell_id"], "arm": spec["arm"],
        "kat": kat, "status": status, "failure_class": reason,
        "identity_fields": {k: spec.get(k) for k in ("q", "n", "m", "curve_seed", "identity", "instances",
                                                     "base_seeds", "tuple_seed", "target_seed", "s")},
        "seeds": {k: spec.get(k) for k in ("curve_seed", "base_seeds", "tuple_seed", "target_seed")},
        "code_sha256": env["code_sha256"], "code_file_sha256": env["code_file_sha256"],
        "git": env["git"], "environment_file": "environment.json", "command_file": "command.txt",
        "started_unix": t_start, "wall_seconds": time.time() - t_start,
        "peak_rss_kb_measured": rs,
        "peak_rss_kb_self": rs, "peak_rss_kb_children": rc_, "peak_rss_kb_total_upper": rs + rc_,
        "certificate": {"kind": "none", "note": "measurement run; no discrete-log or relation claim"},
        "derived_statistics_withheld": kat,
    }
    w = lambda name, text: _write_file(os.path.join(outdir, name), text)  # noqa: E731
    w("command.txt", command + "\n")
    w("environment.json", json.dumps(env, indent=1, sort_keys=True) + "\n")
    w("stdout.log", "\n".join(msgs) + ("\n" if msgs else ""))
    w("stderr.log", "".join(errs))
    if raw is not None:
        w("raw-result.json", json.dumps(raw, indent=1, sort_keys=True, default=str) + "\n")
        w("summary.json", json.dumps(summary, indent=1, sort_keys=True, default=str) + "\n")
    if cdf is not None:
        os.makedirs(os.path.join(outdir, "results"), exist_ok=True)
        w(os.path.join("results", spec["cell_id"] + ".cdf.json"), json.dumps(cdf, indent=1, sort_keys=True, default=str) + "\n")
    if not kat:
        manifest["gate"] = {k: getattr(gate, k) for k in ("specification_sha256", "lock_sha256", "trial_plan_sha256",
                                                          "code_sha256", "test_file_sha256", "check_approval_passed")}
        manifest["startup_selftest"] = dict(gate.startup_selftest)
        sdir = os.path.join(outdir, "selftest")
        os.makedirs(sdir, exist_ok=True)
        for name, src in gate.selftest_files.items():
            shutil.copyfile(src, os.path.join(sdir, name))
        validity = compute_validity(spec, outdir, status, reason, True, raw)
        if spec["arm"] == "A" and status == "completed" and raw is not None:
            f2 = f2_failures(raw)
            if f2:
                role, ident, kind = f2[0]
                if kind == "differs":
                    path = write_stop_f2(os.path.dirname(os.path.abspath(outdir)), spec["cell_id"], ident, role)
                    manifest["f2_family_stop"] = {"sentinel": path, "identity": ident, "role": role}
                validity["reasons"].append(f"F2: CTL-null all-target identity {ident} {kind} on base {role}"
                                           + ("; arm-A family stopped (runs/STOP-F2.json)" if kind == "differs" else ""))
                if validity["status"] == "valid":
                    validity["status"] = "void"
        manifest["validity"] = validity
    import yaml
    w("manifest.yaml", yaml.safe_dump(json.loads(json.dumps(manifest, default=str)), sort_keys=True))
    return manifest


# ----------------------------------------------------------------------------- spec from a plan cell
def spec_from_plan_cell(cell: dict) -> list[dict]:
    """One launcher spec per plan cell (B2 carries both instances in one spec)."""
    arm = cell["arm"]
    if arm == "A":
        seeds = {k: v["seed_string"] for k, v in cell["base_roles"].items() if v}
        return [{"arm": "A", "cell_id": cell["cell_id"], "q": cell["q"], "n": cell["n"], "m": cell["tuple_size_m"],
                 "curve_index": cell["curve_index"], "curve_seed": cell["identity"]["curve_seed"]["seed_string"],
                 "identity": cell["identity"], "base_seeds": seeds}]
    if arm == "C":
        seeds = {k: v["seed_string"] for k, v in cell["base_roles"].items() if v}
        return [{"arm": "C", "cell_id": cell["cell_id"], "q": cell["q"], "n": cell["n"], "m": cell["tuple_size_m"],
                 "curve_index": cell["curve_index"], "curve_seed": cell["identity"]["curve_seed"]["seed_string"],
                 "identity": cell["identity"], "base_seeds": seeds, "s": cell["sample_size_s"],
                 "target_seed": cell["target_seed"]["seed_string"]}]
    if arm == "B1":
        aa = cell.get("tuple_seed_aa")
        return [{"arm": "B1", "cell_id": cell["cell_id"], "n": cell["n"], "m": cell["tuple_size_m"],
                 "tuples": cell["tuples"], "group_law_subsample_fraction": cell["group_law_subsample_fraction"],
                 "tuple_seed": cell["tuple_seed"]["seed_string"],
                 "tuple_seed_aa": aa["seed_string"] if aa else None,
                 "instances": [{"q": cell["q"], "curve_seed": cell["identity"]["curve_seed"]["seed_string"],
                                "identity": cell["identity"]}]}]
    if arm == "B2":
        return [{"arm": "B2", "cell_id": cell["cell_id"], "n": cell["n"], "m": cell["tuple_size_m"],
                 "max_tuples_per_instance": cell["max_tuples_per_instance"],
                 "tuple_seed": cell["tuple_seed"]["seed_string"],
                 "instances": [{"q": i["q"], "curve_seed": i["identity"]["curve_seed"]["seed_string"],
                                "identity": i["identity"]} for i in cell["instances"]]}]
    raise ValueError(arm)


# ----------------------------------------------------------------------------- CLI
def resolve_run_dir(run_id: str, runs_dir: str | None = None) -> str:
    """FX-11 (2): the run directory for run_id, which must match RUN_ID_RE and resolve inside runs/."""
    runs_dir = runs_dir or RUNS_DIR
    if not isinstance(run_id, str) or not RUN_ID_RE.fullmatch(run_id):
        raise ValueError(f"run id {run_id!r} does not match {RUN_ID_RE.pattern}")
    out = os.path.join(runs_dir, run_id)
    root = os.path.realpath(runs_dir)
    if not os.path.realpath(out).startswith(root + os.sep):
        raise ValueError(f"run directory for {run_id!r} does not resolve inside runs/")
    return out


def _refuse(reasons, code=EXIT_REFUSED) -> int:
    print("REFUSED: contract cell not startable:", file=sys.stderr)
    for r in reasons:
        print("  - " + r, file=sys.stderr)
    return code


def cmd_selftest(args) -> int:
    rc, path, messages = write_selftest_receipt()
    for m in messages:
        print(m, file=sys.stderr if rc else sys.stdout)
    return rc


def cmd_cell(args) -> int:
    ok, reasons = check_approval(plan_path=args.plan)
    if not ok:
        return _refuse(reasons)
    with open(args.plan) as fh:
        plan = json.load(fh)
    cell = next((c for c in plan["cells"] if c["cell_id"] == args.cell_id), None)
    if cell is None:
        print(f"REFUSED: cell {args.cell_id} not in the plan", file=sys.stderr)
        return EXIT_REFUSED
    try:
        outdir = resolve_run_dir(args.run_id)
    except ValueError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return EXIT_REFUSED
    if cell["arm"] == "A" and os.path.exists(os.path.join(RUNS_DIR, STOP_F2_NAME)):
        print(f"REFUSED: F2 family stop: {os.path.join(RUNS_DIR, STOP_F2_NAME)} exists; every arm-A cell is void "
              "until the counter is repaired under a new implementation commit", file=sys.stderr)
        return EXIT_REFUSED
    if os.path.exists(outdir):
        print(f"REFUSED: run directory {outdir} exists (run records are immutable; use a new run id)", file=sys.stderr)
        return EXIT_REFUSED
    try:
        g = gate(args.plan, args.selftest_receipt)
    except GateRefused as e:
        print("REFUSED: " + "; ".join(e.reasons[:1]), file=sys.stderr)
        for r in e.reasons[1:]:
            print("  - " + str(r), file=sys.stderr)
        return e.exit_code
    spec = spec_from_plan_cell(cell)[0]
    command = " ".join([sys.executable] + sys.argv)
    try:
        man = run_cell(spec, outdir, kat=False, workers=args.workers, command=command, run_id=args.run_id,
                       timeout_seconds=args.timeout_seconds, memory_gb=args.memory_gb, gate=g)
    finally:
        if g.startup_selftest["mode"] == "ran":
            shutil.rmtree(os.path.dirname(g.selftest_files["junit.xml"]), ignore_errors=True)
    print(json.dumps({"run_dir": outdir, "status": man["status"], "validity": man["validity"]["status"]}))
    return 0 if man["status"] == "completed" else 1


def cmd_kat(args) -> int:
    if (args.q, args.n) in contract_pairs():
        print(f"REFUSED: (q={args.q}, n={args.n}) is a contract cell (arm A/B or arm C); KAT cells must be disjoint",
              file=sys.stderr)
        return EXIT_REFUSED
    cid = f"KAT-{args.arm}-n{args.n}-q{args.q}"
    m = args.m or args.n
    spec = {"arm": args.arm, "cell_id": cid, "q": args.q, "n": args.n, "m": m, "curve_index": 0,
            "curve_seed": args.curve_seed}
    if args.arm == "A":
        spec["base_seeds"] = {"matched_random": f"kat|base|{cid}|random|0", "half_twin": f"kat|base|{cid}|twin|0"}
    elif args.arm == "C":
        spec.update(s=args.s, target_seed=f"kat|targets|{cid}", base_seeds={"matched_random": f"kat|base|{cid}|random|0"})
    else:
        spec.update(arm=args.arm, instances=[{"q": args.q, "curve_seed": args.curve_seed}], tuples=args.tuples,
                    group_law_subsample_fraction=0.1, max_tuples_per_instance=args.tuples,
                    tuple_seed=f"kat|tuples|{cid}|0")
    outdir = tempfile.mkdtemp(prefix="mono1a1be2-kat-")
    command = " ".join([sys.executable] + sys.argv)
    man = run_cell(spec, outdir, kat=True, workers=1, command=command, run_id=None)
    print(json.dumps({"kat_dir": outdir, "status": man["status"]}))
    return 0 if man["status"] == "completed" else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kat", action="store_true", help="known-answer cell: temporary directory, never runs/")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("cell")
    c.add_argument("--cell-id", required=True)
    c.add_argument("--plan", required=True)
    c.add_argument("--run-id", required=True)
    c.add_argument("--workers", type=int, default=1)
    c.add_argument("--selftest-receipt", default=None,
                   help="receipt.json written by `selftest` into selftest-receipts/; any failed check refuses the cell")
    c.add_argument("--timeout-seconds", type=float, default=None, help="watchdog; a cell over it is failed (resource_exhaustion), void")
    c.add_argument("--memory-gb", type=float, default=16.0, help="address-space cap (specification budget.maximum_memory_gb: 16)")
    sub.add_parser("selftest", help="check_approval, then the start-up suite; writes selftest-receipts/<id>/ (FX-5)")
    e = sub.add_parser("environment", help="write the environment record (interpreter, libraries, compiler and flags, host)")
    e.add_argument("--out", required=True)
    k = sub.add_parser("kat")
    k.add_argument("--arm", choices=["A", "B1", "B2", "C"], required=True)
    k.add_argument("--q", type=int, required=True)
    k.add_argument("--n", type=int, required=True)
    k.add_argument("--m", type=int)
    k.add_argument("--curve-seed", required=True)
    k.add_argument("--s", type=int, default=40)
    k.add_argument("--tuples", type=int, default=50)
    args = ap.parse_args(argv)
    if args.cmd == "environment":
        with open(args.out, "w") as fh:
            fh.write(json.dumps(environment_record(), indent=1, sort_keys=True) + "\n")
        print("wrote " + args.out)
        return 0
    if args.cmd == "selftest":
        return cmd_selftest(args)
    if args.cmd == "cell":
        if args.kat:
            print("REFUSED: --kat applies to the kat subcommand only", file=sys.stderr)
            return EXIT_REFUSED
        return cmd_cell(args)
    if not args.kat:
        print("REFUSED: the kat subcommand requires the explicit --kat flag", file=sys.stderr)
        return EXIT_REFUSED
    return cmd_kat(args)


if __name__ == "__main__":
    sys.exit(main())
