#!/usr/bin/env python3
"""Benchmark records: every benchmark run leaves a record in Git and its raw data in S3.

Shared, byte-identical in crypto, crypto-autoresearcher and cryptanalysis
(lab contract, section 7; owner: crypto-autoresearcher). Standard library only.
It never computes a measurement: it records the values a harness produced,
hashes the raw files, derives the content-addressed S3 location, and renders
the progress report from the committed records. Every derived number in the
report is labelled derived.

One record per run, schema `bench.record/v1`, at
`<records_dir>/<YYYYMMDD>T<HHMM>Z-<slug>.json` (default `benchmarks/records/`;
`.benchrec.json` at the repository root overrides the layout).

    benchrec.py init --slug SLUG --problem PROBLEM [--curve UID] [--entry DIR]
    benchrec.py run RECORD -- COMMAND...          run a launcher under the record
    benchrec.py add-raw RECORD PATH... [--s3-uri URI]
    benchrec.py metric RECORD --name N --value V --unit U [--better lower|higher]
                [--baseline V] [--reference V --reference-kind matched_rho]
                [--n N] [--spread-low L --spread-high H] [--note TEXT]
    benchrec.py upload RECORD [--all]             copy raw files to the store (needs AWS)
    benchrec.py close RECORD --status measured|invalid|censored
                [--report PDF] [--svg SVG...] [--validation PATH] [--summary TEXT]
    benchrec.py report [--check]                  regenerate the progress report
    benchrec.py check [--base REF] [--local] [--verify-s3]
    benchrec.py gate                              what the push hook runs
    benchrec.py open                              list records still open here

Exit codes: 0 pass, 1 a check failed, 2 usage.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import time
import zlib
from pathlib import Path

SCHEMA = "bench.record/v1"
PROGRESS_SCHEMA = "bench.progress/v1"
BUCKET = "setec-astronomy-artifacts"
STORE_PREFIX = "store/sha256"
DEFAULT_CONFIG = {
    "records_dir": "benchmarks/records",
    "progress_dir": "benchmarks/progress",
    "entry_dirs": ["benchmarks"],
    "entry_re": r"^\d{8}-[A-Za-z0-9_.-]+$",
    "bucket": BUCKET,
    "store_prefix": STORE_PREFIX,
}
OPEN_LIST = ".benchrec/open.jsonl"

# One unit vocabulary for every repository. A metric outside it is rejected;
# extend the table (owner first) instead of inventing a spelling.
UNITS = {
    "S": ("group operations / sqrt(n); the ECDLP cost unit, every phase priced", "lower"),
    "gae": ("counted group-addition equivalents", "lower"),
    "log2_gae": ("log2 of counted group-addition equivalents", "lower"),
    "ns_per_gae": ("wall nanoseconds per group-addition equivalent", "lower"),
    "ir": ("Callgrind instructions retired (whole run)", "lower"),
    "ir_per_op": ("Callgrind instructions per group operation or step", "lower"),
    "cycles_per_op": ("CPU cycles per group operation or step (perf stat)", "lower"),
    "ipc": ("instructions per cycle (perf stat)", "higher"),
    "wall_s": ("wall-clock seconds", "lower"),
    "cpu_s": ("CPU seconds on the pinned core", "lower"),
    "ops_per_s": ("operations per second", "higher"),
    "fmul": ("field multiplications", "lower"),
    "ratio": ("dimensionless ratio, reference / candidate unless the note says otherwise", "higher"),
    "percent": ("percent of the reference", "lower"),
    "count": ("a count (relations, rows, solves)", "neutral"),
    "bytes": ("bytes", "lower"),
}
# The unit every progress headline is drawn in. A metric in another unit is
# plotted in its own panel and never mixed into the headline.
HEADLINE_UNIT = "S"
STATUSES = ("open", "measured", "invalid", "censored")
REFERENCE_KINDS = ("matched_rho", "unmatched_rho", "baseline", "external_tool", "none")


# --------------------------------------------------------------------------- repo

def git(root: Path, *args: str, check: bool = True) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if check and p.returncode != 0:
        raise SystemExit(f"benchrec: git {' '.join(args)}: {p.stderr.strip()[:300]}")
    return p.stdout


def repo_root(start: Path | None = None) -> Path:
    start = (start or Path.cwd()).resolve()
    out = subprocess.run(["git", "-C", str(start), "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit("benchrec: not inside a git repository")
    return Path(out.stdout.strip())


def repo_name(root: Path) -> str:
    url = git(root, "remote", "get-url", "origin", check=False).strip()
    name = url.rstrip("/").split("/")[-1] if url else root.name
    return name[:-4] if name.endswith(".git") else name


def load_config(root: Path) -> dict:
    cfg = dict(DEFAULT_CONFIG)
    p = root / ".benchrec.json"
    if p.is_file():
        user = json.loads(p.read_text())
        if not isinstance(user, dict):
            raise SystemExit("benchrec: .benchrec.json must hold an object")
        cfg.update(user)
    return cfg


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def store_uri(cfg: dict, digest: str) -> str:
    return f"s3://{cfg['bucket']}/{cfg['store_prefix']}/{digest[:2]}/{digest}"


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def stamp(t: dt.datetime) -> str:
    return t.strftime("%Y%m%dT%H%MZ")


def host_info() -> dict:
    cpu = ""
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.lower().startswith("model name"):
                cpu = line.split(":", 1)[1].strip()
                break
    except OSError:
        cpu = platform.processor()
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "cpu": cpu,
        "cpus_online": os.cpu_count(),
        "isolation": os.environ.get("BENCHREC_ISOLATION", "unstated"),
    }


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)


def load_record(root: Path, ref: str) -> tuple[Path, dict]:
    p = Path(ref)
    if not p.is_absolute():
        p = (Path.cwd() / p).resolve() if p.exists() else (root / p).resolve()
    if not p.is_file():
        raise SystemExit(f"benchrec: no record at {ref}")
    rec = json.loads(p.read_text())
    if rec.get("schema") != SCHEMA:
        raise SystemExit(f"benchrec: {ref} is not a {SCHEMA} record")
    return p, rec


def rel(root: Path, p: Path) -> str:
    return p.resolve().relative_to(root).as_posix()


# ---------------------------------------------------------------------- open list

def open_list(root: Path) -> list[dict]:
    p = root / OPEN_LIST
    if not p.is_file():
        return []
    out = []
    for line in p.read_text().splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def set_open_list(root: Path, items: list[dict]) -> None:
    p = root / OPEN_LIST
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(json.dumps(i) + "\n" for i in items))


# --------------------------------------------------------------------- commands

def cmd_init(a, root: Path, cfg: dict) -> int:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,60}", a.slug):
        raise SystemExit("benchrec: --slug is lowercase letters, digits and dashes")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_:./-]{1,120}", a.problem):
        raise SystemExit("benchrec: --problem is a stable key such as ecdlp:EC1P40Cgh1a2b3c4d5e6 or kernel:rho_zp_step")
    now = utcnow()
    head = git(root, "rev-parse", "HEAD").strip()
    dirty = bool(git(root, "status", "--porcelain", "--untracked-files=no").strip())
    branch = git(root, "rev-parse", "--abbrev-ref", "HEAD").strip()
    rec = {
        "schema": SCHEMA,
        "id": f"{stamp(now)}-{a.slug}",
        "slug": a.slug,
        "problem": a.problem,
        "curve_uid": a.curve,
        "repo": repo_name(root),
        "created_utc": now.isoformat(),
        "closed_utc": None,
        "status": "open",
        "commit": head,
        "commit_dirty": dirty,
        "branch": branch,
        "host": host_info(),
        "entries": list(a.entry or []),
        "commands": [],
        "raw": [],
        "metrics": [],
        "reports": {"pdf": None, "svg": [], "png": []},
        "validation": None,
        "summary": "",
        "session": os.environ.get("CLAUDE_SESSION_ID") or os.environ.get("CHECKPOINT_SESSION") or None,
    }
    path = root / cfg["records_dir"] / f"{rec['id']}.json"
    if path.exists():
        raise SystemExit(f"benchrec: {rel(root, path)} exists; records are never overwritten")
    write_json(path, rec)
    items = open_list(root)
    items.append({"record": rel(root, path), "opened": now.isoformat()})
    set_open_list(root, items)
    print(rel(root, path))
    print(f"export BENCHREC={rel(root, path)}", file=sys.stderr)
    return 0


def cmd_run(a, root: Path, cfg: dict) -> int:
    path, rec = load_record(root, a.record)
    if rec["status"] != "open":
        raise SystemExit(f"benchrec: {a.record} is {rec['status']}; open a new record for a new run")
    if not a.command:
        raise SystemExit("benchrec: run RECORD -- COMMAND...")
    env = dict(os.environ, BENCHREC=rel(root, path))
    t0 = utcnow()
    start = time.monotonic()
    proc = subprocess.run(a.command, env=env, cwd=a.cwd or None)
    wall = time.monotonic() - start
    rec["commands"].append({
        "argv": list(a.command),
        "cwd": os.path.relpath(a.cwd or os.getcwd(), root),
        "started_utc": t0.isoformat(),
        "wall_s": round(wall, 3),
        "exit": proc.returncode,
    })
    write_json(path, rec)
    return proc.returncode


def cmd_add_raw(a, root: Path, cfg: dict) -> int:
    path, rec = load_record(root, a.record)
    if rec["status"] != "open":
        raise SystemExit(f"benchrec: {a.record} is closed")
    known = {r["path"] for r in rec["raw"]}
    for p in a.paths:
        fp = Path(p)
        if not fp.is_file():
            raise SystemExit(f"benchrec: {p} is not a file")
        digest = sha256_file(fp)
        try:
            rp = rel(root, fp)
        except ValueError:
            rp = fp.resolve().as_posix()
        if rp in known:
            continue
        rec["raw"].append({
            "path": rp,
            "sha256": digest,
            "bytes": fp.stat().st_size,
            "s3_uri": a.s3_uri or store_uri(cfg, digest),
            "uploaded": False,
        })
        known.add(rp)
    write_json(path, rec)
    print(f"{len(rec['raw'])} raw file(s) recorded")
    return 0


def cmd_metric(a, root: Path, cfg: dict) -> int:
    path, rec = load_record(root, a.record)
    if rec["status"] != "open":
        raise SystemExit(f"benchrec: {a.record} is closed")
    if a.unit not in UNITS:
        raise SystemExit(f"benchrec: unknown unit {a.unit!r}; one of {', '.join(sorted(UNITS))}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_./-]{0,80}", a.name):
        raise SystemExit("benchrec: --name is a stable lowercase key")
    better = a.better or UNITS[a.unit][1]
    m = {
        "name": a.name,
        "value": a.value,
        "unit": a.unit,
        "better": better,
        "n": a.n,
        "spread": [a.spread_low, a.spread_high] if a.spread_low is not None else None,
        "baseline": a.baseline,
        "reference": a.reference,
        "reference_kind": a.reference_kind if a.reference is not None else None,
        "note": a.note or "",
    }
    if any(x["name"] == a.name for x in rec["metrics"]):
        raise SystemExit(f"benchrec: metric {a.name} already recorded; a rerun is a new record")
    rec["metrics"].append(m)
    write_json(path, rec)
    return 0


def aws_available() -> bool:
    if not shutil.which("aws"):
        return False
    env = dict(os.environ)
    for k in ("ARTIFACTS_AWS_ACCESS_KEY_ID", "ARTIFACTS_AWS_SECRET_ACCESS_KEY"):
        if k in env:
            env[k.replace("ARTIFACTS_", "")] = env[k]
    p = subprocess.run(["aws", "sts", "get-caller-identity"], capture_output=True, env=env)
    return p.returncode == 0


def aws_env() -> dict:
    env = dict(os.environ)
    for k in ("ARTIFACTS_AWS_ACCESS_KEY_ID", "ARTIFACTS_AWS_SECRET_ACCESS_KEY"):
        if k in env:
            env[k.replace("ARTIFACTS_", "")] = env[k]
    env.setdefault("AWS_REGION", os.environ.get("ARTIFACTS_AWS_REGION", "us-east-2"))
    env.setdefault("AWS_DEFAULT_REGION", env["AWS_REGION"])
    return env


def s3_exists(uri: str) -> bool:
    bucket, key = uri[5:].split("/", 1)
    p = subprocess.run(["aws", "s3api", "head-object", "--bucket", bucket, "--key", key],
                       capture_output=True, env=aws_env())
    return p.returncode == 0


def cmd_upload(a, root: Path, cfg: dict) -> int:
    path, rec = load_record(root, a.record)
    if not aws_available():
        print("benchrec: no AWS credentials here; CI uploads files that are in Git, "
              "push larger ones with tools/artifacts/artifacts.py push where credentials exist",
              file=sys.stderr)
        return 1
    rc = 0
    for r in rec["raw"]:
        if r.get("uploaded") and not a.all:
            continue
        src = root / r["path"]
        if not src.is_file():
            print(f"benchrec: {r['path']} missing locally; cannot upload", file=sys.stderr)
            rc = 1
            continue
        if sha256_file(src) != r["sha256"]:
            print(f"benchrec: {r['path']} changed since it was recorded", file=sys.stderr)
            rc = 1
            continue
        if s3_exists(r["s3_uri"]):
            r["uploaded"] = True
            continue
        p = subprocess.run(["aws", "s3", "cp", "--only-show-errors", str(src), r["s3_uri"]], env=aws_env())
        if p.returncode == 0:
            r["uploaded"] = True
        else:
            rc = 1
    write_json(path, rec)
    return rc


def cmd_close(a, root: Path, cfg: dict) -> int:
    path, rec = load_record(root, a.record)
    if rec["status"] != "open":
        raise SystemExit(f"benchrec: {a.record} is already {rec['status']}")
    if a.status not in STATUSES or a.status == "open":
        raise SystemExit("benchrec: --status measured|invalid|censored")
    if a.report:
        rec["reports"]["pdf"] = rel(root, Path(a.report))
    for s in a.svg or []:
        rec["reports"]["svg"].append(rel(root, Path(s)))
    for s in a.png or []:
        rec["reports"]["png"].append(rel(root, Path(s)))
    if a.validation:
        rec["validation"] = rel(root, Path(a.validation))
    for e in a.entry or []:
        if e not in rec["entries"]:
            rec["entries"].append(e)
    if a.summary:
        rec["summary"] = a.summary
    rec["status"] = a.status
    rec["closed_utc"] = utcnow().isoformat()
    errors = record_errors(root, cfg, rec, rel(root, path), require_closed=True)
    if errors:
        rec["status"] = "open"
        rec["closed_utc"] = None
        for e in errors:
            print(f"benchrec: {e}", file=sys.stderr)
        return 1
    write_json(path, rec)
    items = [i for i in open_list(root) if i["record"] != rel(root, path)]
    set_open_list(root, items)
    write_progress(root, cfg)
    print(f"closed {rel(root, path)} ({a.status}); progress report regenerated in {cfg['progress_dir']}/")
    return 0


# ---------------------------------------------------------------------- checks

def record_errors(root: Path, cfg: dict, rec: dict, name: str, *, require_closed: bool,
                  verify_s3: bool = False, manifests: dict | None = None) -> list[str]:
    e: list[str] = []
    for k in ("schema", "id", "slug", "problem", "repo", "created_utc", "status", "commit",
              "branch", "host", "entries", "commands", "raw", "metrics", "reports"):
        if k not in rec:
            e.append(f"{name}: missing field {k}")
    if e:
        return e
    if rec["schema"] != SCHEMA:
        e.append(f"{name}: schema {rec['schema']!r} is not {SCHEMA}")
    if rec["status"] not in STATUSES:
        e.append(f"{name}: status {rec['status']!r}")
    if not re.fullmatch(r"[0-9a-f]{40}", rec["commit"]):
        e.append(f"{name}: commit is not a 40-hex sha")
    stem = Path(name).stem
    if rec["id"] != stem:
        e.append(f"{name}: id {rec['id']!r} does not match the file name")
    if require_closed:
        if rec["status"] == "open":
            e.append(f"{name}: still open; close it with benchrec.py close")
            return e
        if not rec["commands"]:
            e.append(f"{name}: no command recorded (run the launcher with benchrec.py run, "
                     "or BENCHREC=<record> in its environment and record the command)")
        if rec["status"] == "measured":
            if not rec["metrics"]:
                e.append(f"{name}: a measured record needs at least one metric")
            if not rec["raw"]:
                e.append(f"{name}: a measured record names its raw data files")
            if not rec["reports"].get("pdf"):
                e.append(f"{name}: a measured record names its report PDF")
            if not rec.get("summary"):
                e.append(f"{name}: a measured record carries a one-line summary")
        if rec["status"] in ("invalid", "censored") and not rec.get("summary"):
            e.append(f"{name}: say why the run is {rec['status']} in --summary")
    seen = set()
    for m in rec["metrics"]:
        if m.get("unit") not in UNITS:
            e.append(f"{name}: metric {m.get('name')} has unknown unit {m.get('unit')!r}")
        if not isinstance(m.get("value"), (int, float)) or isinstance(m.get("value"), bool):
            e.append(f"{name}: metric {m.get('name')} value is not a number")
        if m.get("better") not in ("lower", "higher", "neutral"):
            e.append(f"{name}: metric {m.get('name')} better must be lower|higher|neutral")
        if m.get("reference") is not None and m.get("reference_kind") not in REFERENCE_KINDS:
            e.append(f"{name}: metric {m.get('name')} reference_kind must be one of {REFERENCE_KINDS}")
        if m.get("name") in seen:
            e.append(f"{name}: metric {m.get('name')} listed twice")
        seen.add(m.get("name"))
    for r in rec["raw"]:
        for k in ("path", "sha256", "bytes", "s3_uri"):
            if k not in r:
                e.append(f"{name}: raw entry missing {k}")
        if not re.fullmatch(r"[0-9a-f]{64}", str(r.get("sha256", ""))):
            e.append(f"{name}: raw {r.get('path')} sha256 malformed")
        if not str(r.get("s3_uri", "")).startswith("s3://"):
            e.append(f"{name}: raw {r.get('path')} has no s3:// location")
        local = root / r.get("path", "")
        if local.is_file():
            if sha256_file(local) != r.get("sha256"):
                e.append(f"{name}: raw {r['path']} differs from its recorded sha256")
        else:
            covered = manifests is not None and manifests.get(r.get("path")) == r.get("sha256")
            if not covered and not r.get("uploaded"):
                e.append(f"{name}: raw {r.get('path')} is neither in Git, nor in a .artifacts.json "
                         "manifest, nor marked uploaded; run benchrec.py upload or artifacts.py push")
        if verify_s3 and not s3_exists(r["s3_uri"]):
            e.append(f"{name}: raw {r['path']} is not at {r['s3_uri']}")
    def stored_ok(p: str, what: str) -> bool:
        """True if p is in the checkout, or is store-backed through a .artifacts.json manifest
        (docs/artifacts.md). With verify_s3, a store-backed file must also exist in the store."""
        if (root / p).is_file():
            return True
        digest = manifests.get(p) if manifests is not None else None
        if not digest:
            return False
        if verify_s3 and not s3_exists(store_uri(cfg, digest)):
            e.append(f"{name}: {what} {p} is in a .artifacts.json manifest but not at {store_uri(cfg, digest)}")
        return True
    for k in ("pdf",):
        p = rec["reports"].get(k)
        if p and not stored_ok(p, "report"):
            e.append(f"{name}: report {p} is not in the checkout or a .artifacts.json manifest")
    for p in rec["reports"].get("svg", []) + rec["reports"].get("png", []):
        if not stored_ok(p, "graph"):
            e.append(f"{name}: graph {p} is not in the checkout or a .artifacts.json manifest")
    if rec.get("validation") and not stored_ok(rec["validation"], "validation file"):
        e.append(f"{name}: validation file {rec['validation']} is not in the checkout or a .artifacts.json manifest")
    for d in rec["entries"]:
        if not (root / d).is_dir():
            e.append(f"{name}: entry directory {d} is not in the checkout")
    return e


def artifact_manifests(root: Path) -> dict[str, str]:
    """path -> sha256 for every file listed in a .artifacts.json manifest."""
    out: dict[str, str] = {}
    for mf in root.rglob(".artifacts.json"):
        if any(part in (".git", "target", "node_modules") for part in mf.parts):
            continue
        try:
            data = json.loads(mf.read_text())
        except (OSError, ValueError):
            continue
        files = data.get("files", data) if isinstance(data, dict) else {}
        if isinstance(files, dict):
            for fname, meta in files.items():
                digest = meta.get("sha256") if isinstance(meta, dict) else None
                if digest:
                    out[(mf.parent / fname).resolve().relative_to(root).as_posix()] = digest
        elif isinstance(files, list):
            for meta in files:
                if isinstance(meta, dict) and meta.get("sha256") and meta.get("name"):
                    out[(mf.parent / meta["name"]).resolve().relative_to(root).as_posix()] = meta["sha256"]
    return out


def all_records(root: Path, cfg: dict) -> list[tuple[str, dict]]:
    d = root / cfg["records_dir"]
    out = []
    if d.is_dir():
        for p in sorted(d.glob("*.json")):
            try:
                out.append((rel(root, p), json.loads(p.read_text())))
            except ValueError:
                out.append((rel(root, p), {"schema": "unreadable"}))
    return out


def changed_paths(root: Path, base: str) -> list[str]:
    merge_base = git(root, "merge-base", base, "HEAD", check=False).strip() or base
    out = git(root, "diff", "--name-only", "--diff-filter=ACMR", f"{merge_base}...HEAD", check=False)
    return [l for l in out.splitlines() if l]


def new_entries(root: Path, cfg: dict, paths: list[str]) -> set[str]:
    entries: set[str] = set()
    pat = re.compile(cfg["entry_re"])
    reserved = {Path(cfg["records_dir"]).name, Path(cfg["progress_dir"]).name}
    for p in paths:
        for ed in cfg["entry_dirs"]:
            ed = ed.rstrip("/")
            if p.startswith(ed + "/"):
                first = p[len(ed) + 1:].split("/", 1)[0]
                if first in reserved or "/" not in p[len(ed) + 1:]:
                    continue
                if pat.match(first):
                    entries.add(f"{ed}/{first}")
    return entries


def cmd_check(a, root: Path, cfg: dict) -> int:
    problems: list[str] = []
    if a.verify_s3 and not aws_available():
        print("FAIL: --verify-s3 asked for but no AWS credentials or aws CLI here; "
              "the S3 side of the records cannot be verified")
        return 1
    recs = all_records(root, cfg)
    manifests = artifact_manifests(root)
    referenced: set[str] = set()
    for name, rec in recs:
        if rec.get("schema") != SCHEMA:
            problems.append(f"{name}: not a {SCHEMA} record")
            continue
        problems += record_errors(root, cfg, rec, name, require_closed=True,
                                  verify_s3=a.verify_s3, manifests=manifests)
        referenced.update(rec.get("entries", []))
    if a.base:
        changed = changed_paths(root, a.base)
        for d in sorted(new_entries(root, cfg, changed)):
            if d not in referenced:
                problems.append(f"{d}: benchmark entry added without a {SCHEMA} record naming it "
                                f"(benchrec.py init --entry {d} ...)")
        touched_records = [p for p in changed if p.startswith(cfg["records_dir"].rstrip("/") + "/")]
        base_ref = git(root, "merge-base", a.base, "HEAD", check=False).strip() or a.base
        for p in touched_records:
            old = git(root, "show", f"{base_ref}:{p}", check=False)
            if old.strip():
                try:
                    o = json.loads(old)
                except ValueError:
                    o = {}
                if o.get("status") in ("measured", "invalid", "censored"):
                    problems.append(f"{p}: a closed record is immutable; a rerun is a new record")
    if a.local:
        for item in open_list(root):
            problems.append(f"{item['record']}: opened {item['opened']} and not closed")
    stale = progress_stale(root, cfg)
    if stale:
        problems.append("progress report is stale: " + ", ".join(stale) +
                        " (run python3 tools/benchrec.py report)")
    for p in problems:
        print(f"FAIL: {p}")
    n = len([r for _, r in recs if r.get("schema") == SCHEMA])
    if problems:
        print(f"benchrec: {len(problems)} problem(s) across {n} record(s)")
        return 1
    print(f"benchrec: OK, {n} record(s), progress report current")
    return 0


def cmd_gate(a, root: Path, cfg: dict) -> int:
    ns = argparse.Namespace(base=None, local=True, verify_s3=False)
    return cmd_check(ns, root, cfg)


def cmd_open(a, root: Path, cfg: dict) -> int:
    items = open_list(root)
    for i in items:
        print(f"{i['record']}  (opened {i['opened']})")
    return 0 if not items else 1


# ------------------------------------------------------------------- progress

def series_key(rec: dict, m: dict) -> str:
    return f"{rec['problem']}|{m['name']}|{m['unit']}"


def build_progress(root: Path, cfg: dict) -> dict:
    recs = [r for _, r in all_records(root, cfg) if r.get("schema") == SCHEMA]
    closed = [r for r in recs if r.get("status") == "measured"]
    closed.sort(key=lambda r: (r.get("closed_utc") or r["created_utc"], r["id"]))
    series: dict[str, dict] = {}
    for r in closed:
        for m in r["metrics"]:
            k = series_key(r, m)
            s = series.setdefault(k, {
                "problem": r["problem"], "metric": m["name"], "unit": m["unit"],
                "better": m["better"], "points": [],
            })
            s["points"].append({
                "record": r["id"], "date": (r.get("closed_utc") or r["created_utc"])[:10],
                "value": m["value"], "n": m.get("n"), "spread": m.get("spread"),
                "reference": m.get("reference"), "reference_kind": m.get("reference_kind"),
                "commit": r["commit"][:12], "summary": r.get("summary", ""),
            })
    out_series = []
    for k in sorted(series):
        s = series[k]
        pts = s["points"]
        first = pts[0]["value"]
        prev = None
        for p in pts:
            v = p["value"]
            p["derived"] = {}
            if s["better"] in ("lower", "higher") and first not in (0, None):
                sign = 1.0 if s["better"] == "lower" else -1.0
                p["derived"]["improvement_vs_first_percent"] = round(sign * (first - v) / abs(first) * 100.0, 4)
                if prev not in (0, None):
                    p["derived"]["improvement_vs_previous_percent"] = round(sign * (prev - v) / abs(prev) * 100.0, 4)
            if p.get("reference") not in (0, None):
                p["derived"]["value_over_reference"] = round(v / p["reference"], 6)
            prev = v
        s["first"] = first
        s["latest"] = pts[-1]["value"]
        s["latest_derived"] = pts[-1]["derived"]
        out_series.append(s)
    counts = {st: len([r for r in recs if r.get("status") == st]) for st in STATUSES}
    return {
        "schema": PROGRESS_SCHEMA,
        "repo": repo_name(root),
        "headline_unit": HEADLINE_UNIT,
        "units": {u: {"meaning": d, "better": b} for u, (d, b) in UNITS.items()},
        "records": counts,
        "latest_record": closed[-1]["id"] if closed else None,
        "series": out_series,
        "note": ("Every value is quoted from the record it names, in that record's unit. "
                 "Percentages and ratios under 'derived' are computed here from those values "
                 "and are not measurements. Series in different units are never compared."),
    }


def progress_paths(root: Path, cfg: dict) -> dict[str, Path]:
    d = root / cfg["progress_dir"]
    return {"json": d / "progress.json", "md": d / "PROGRESS.md",
            "svg": d / "progress.svg", "pdf": d / "progress.pdf"}


def render_all(prog: dict) -> dict[str, bytes]:
    return {
        "json": (json.dumps(prog, indent=2, sort_keys=True) + "\n").encode(),
        "md": render_md(prog).encode(),
        "svg": render_svg(prog).encode(),
        "pdf": render_pdf(prog),
    }


def write_progress(root: Path, cfg: dict) -> None:
    prog = build_progress(root, cfg)
    paths = progress_paths(root, cfg)
    for k, data in render_all(prog).items():
        paths[k].parent.mkdir(parents=True, exist_ok=True)
        paths[k].write_bytes(data)


def progress_stale(root: Path, cfg: dict) -> list[str]:
    prog = build_progress(root, cfg)
    paths = progress_paths(root, cfg)
    stale = []
    for k, data in render_all(prog).items():
        p = paths[k]
        if not p.is_file() or p.read_bytes() != data:
            stale.append(rel(root, p) if p.is_relative_to(root) else str(p))
    return stale


def cmd_report(a, root: Path, cfg: dict) -> int:
    if a.check:
        stale = progress_stale(root, cfg)
        if stale:
            print("stale: " + ", ".join(stale))
            return 1
        print("progress report current")
        return 0
    write_progress(root, cfg)
    for p in progress_paths(root, cfg).values():
        print(rel(root, p))
    return 0


def fmt(v) -> str:
    if v is None:
        return "–"
    if isinstance(v, float):
        if v != 0 and (abs(v) >= 1e6 or abs(v) < 1e-3):
            return f"{v:.4g}"
        return f"{v:,.4f}".rstrip("0").rstrip(".")
    return str(v)


def render_md(prog: dict) -> str:
    L = [f"# Benchmark progress: {prog['repo']}", "",
         "Generated by `tools/benchrec.py report` from `bench.record/v1` records. "
         "Do not edit; rerun the tool.", "",
         f"Records: " + ", ".join(f"{k} {v}" for k, v in prog["records"].items()) +
         f". Latest measured record: `{prog['latest_record']}`.", "",
         f"Headline unit: `{prog['headline_unit']}` ({prog['units'][prog['headline_unit']]['meaning']}). "
         "Improvement percentages are derived from recorded values within one series "
         "(same problem, metric and unit); a positive number is a gain in the direction "
         "the unit calls better. `value/ref` is the recorded value over its recorded "
         "reference (matched rho where the record says so): the distance remaining.", ""]
    head = [s for s in prog["series"] if s["unit"] == prog["headline_unit"]]
    other = [s for s in prog["series"] if s["unit"] != prog["headline_unit"]]
    for title, group in (("Headline series (same unit everywhere)", head), ("Other series, each in its own unit", other)):
        L += [f"## {title}", ""]
        if not group:
            L += ["(none yet)", ""]
            continue
        L += ["| problem | metric | unit | first | latest | gain vs first | gain vs previous | value/ref (kind) | points |",
              "|:--|:--|:--|--:|--:|--:|--:|--:|--:|"]
        for s in group:
            d = s["latest_derived"]
            last = s["points"][-1]
            ref = (f"{fmt(d.get('value_over_reference'))} ({last.get('reference_kind')})"
                   if d.get("value_over_reference") is not None else "–")
            L.append(f"| {s['problem']} | {s['metric']} | {s['unit']} | {fmt(s['first'])} | {fmt(s['latest'])} | "
                     f"{fmt(d.get('improvement_vs_first_percent'))}% | {fmt(d.get('improvement_vs_previous_percent'))}% | "
                     f"{ref} | {len(s['points'])} |")
        L.append("")
    L += ["## Every point", ""]
    for s in prog["series"]:
        L += [f"### {s['problem']} · {s['metric']} [{s['unit']}]", "",
              "| date | record | commit | value | n | spread | gain vs first | value/ref | summary |",
              "|:--|:--|:--|--:|--:|:--|--:|--:|:--|"]
        for p in s["points"]:
            sp = f"{fmt(p['spread'][0])}–{fmt(p['spread'][1])}" if p.get("spread") else "–"
            L.append(f"| {p['date']} | `{p['record']}` | `{p['commit']}` | {fmt(p['value'])} | {fmt(p.get('n'))} | {sp} | "
                     f"{fmt(p['derived'].get('improvement_vs_first_percent'))}% | "
                     f"{fmt(p['derived'].get('value_over_reference'))} | {p['summary'][:120]} |")
        L.append("")
    L += ["", prog["note"], ""]
    return "\n".join(L)


# ------------------------------------------------------------------ SVG chart

PALETTE = ["#167f73", "#637bad", "#aa8b5b", "#93a1a4", "#69879e", "#b05c5c", "#5c8a3a", "#8a5ca8"]


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def chart_panels(prog: dict) -> list[dict]:
    """Panels: headline 'gain vs first' for every headline series, 'distance to
    reference' where references exist, then one panel per other unit."""
    panels = []
    head = [s for s in prog["series"] if s["unit"] == prog["headline_unit"]]
    if head:
        panels.append({"title": f"Cumulative gain vs first record, unit {prog['headline_unit']} (derived, %)",
                       "ylabel": "% better than first", "series": head,
                       "y": lambda p: p["derived"].get("improvement_vs_first_percent"), "log": False})
    refd = [s for s in prog["series"] if any(p["derived"].get("value_over_reference") for p in s["points"])]
    if refd:
        panels.append({"title": "Distance remaining: value / reference (1.0 = parity; derived)",
                       "ylabel": "value / reference", "series": refd,
                       "y": lambda p: p["derived"].get("value_over_reference"), "log": True})
    by_unit: dict[str, list] = {}
    for s in prog["series"]:
        if s["unit"] != prog["headline_unit"]:
            by_unit.setdefault(s["unit"], []).append(s)
    for u in sorted(by_unit):
        panels.append({"title": f"Series in unit {u}: gain vs first record (derived, %)",
                       "ylabel": "% better than first", "series": by_unit[u],
                       "y": lambda p: p["derived"].get("improvement_vs_first_percent"), "log": False})
    return panels


def _date_num(d: str) -> int:
    return dt.date.fromisoformat(d).toordinal()


def panel_geometry(panel: dict):
    xs, ys = [], []
    for s in panel["series"]:
        for p in s["points"]:
            y = panel["y"](p)
            if y is None:
                continue
            xs.append(_date_num(p["date"]))
            ys.append(y)
    if not xs:
        return None
    import math
    if panel["log"]:
        ys = [math.log10(y) for y in ys if y > 0]
        if not ys:
            return None
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    if x0 == x1:
        x0, x1 = x0 - 1, x1 + 1
    if y0 == y1:
        y0, y1 = y0 - 1, y1 + 1
    pad = (y1 - y0) * 0.1
    return x0, x1, y0 - pad, y1 + pad


def render_svg(prog: dict) -> str:
    import math
    W, PH, M = 900, 260, 60
    panels = chart_panels(prog)
    H = 70 + max(1, len(panels)) * (PH + 50)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif" font-size="12">',
         f'<rect width="{W}" height="{H}" fill="white"/>',
         f'<text x="{M}" y="30" font-size="18" font-weight="bold">Benchmark progress: {_esc(prog["repo"])}</text>',
         f'<text x="{M}" y="50" fill="#555">Values from bench.record/v1 records; percentages and ratios derived, same unit within a series. '
         f'Records: {", ".join(f"{k} {v}" for k, v in prog["records"].items())}.</text>']
    if not panels:
        o.append(f'<text x="{M}" y="100">No measured records yet.</text>')
    for i, panel in enumerate(panels):
        top = 70 + i * (PH + 50)
        geom = panel_geometry(panel)
        o.append(f'<text x="{M}" y="{top + 14}" font-weight="bold">{_esc(panel["title"])}</text>')
        gx0, gy0, gw, gh = M, top + 24, W - 2 * M - 220, PH - 40
        o.append(f'<rect x="{gx0}" y="{gy0}" width="{gw}" height="{gh}" fill="none" stroke="#999"/>')
        if geom is None:
            o.append(f'<text x="{gx0 + 10}" y="{gy0 + 20}" fill="#555">no points</text>')
            continue
        x0, x1, y0, y1 = geom

        def X(d):
            return gx0 + (d - x0) / (x1 - x0) * gw

        def Y(v):
            v = math.log10(v) if panel["log"] else v
            return gy0 + gh - (v - y0) / (y1 - y0) * gh
        for k in range(5):
            yv = y0 + (y1 - y0) * k / 4
            yy = gy0 + gh - gh * k / 4
            lab = f"{10 ** yv:.3g}" if panel["log"] else f"{yv:.3g}"
            o.append(f'<line x1="{gx0}" y1="{yy:.1f}" x2="{gx0 + gw}" y2="{yy:.1f}" stroke="#eee"/>')
            o.append(f'<text x="{gx0 - 6}" y="{yy + 4:.1f}" text-anchor="end" fill="#555">{lab}</text>')
        for k in range(4):
            xv = x0 + (x1 - x0) * k / 3
            xx = gx0 + gw * k / 3
            o.append(f'<text x="{xx:.1f}" y="{gy0 + gh + 16}" text-anchor="middle" fill="#555">'
                     f'{dt.date.fromordinal(int(round(xv))).isoformat()}</text>')
        if not panel["log"]:
            zy = Y(0.0)
            if gy0 <= zy <= gy0 + gh:
                o.append(f'<line x1="{gx0}" y1="{zy:.1f}" x2="{gx0 + gw}" y2="{zy:.1f}" stroke="#bbb" stroke-dasharray="4 3"/>')
        else:
            zy = Y(1.0)
            if gy0 <= zy <= gy0 + gh:
                o.append(f'<line x1="{gx0}" y1="{zy:.1f}" x2="{gx0 + gw}" y2="{zy:.1f}" stroke="#bbb" stroke-dasharray="4 3"/>')
                o.append(f'<text x="{gx0 + gw - 4}" y="{zy - 4:.1f}" text-anchor="end" fill="#777">parity</text>')
        o.append(f'<text transform="translate({gx0 - 44},{gy0 + gh / 2:.1f}) rotate(-90)" text-anchor="middle" fill="#555">{_esc(panel["ylabel"])}</text>')
        for j, s in enumerate(panel["series"]):
            col = PALETTE[j % len(PALETTE)]
            pts = [(X(_date_num(p["date"])), Y(panel["y"](p)), p) for p in s["points"]
                   if panel["y"](p) is not None and (not panel["log"] or panel["y"](p) > 0)]
            if len(pts) > 1:
                o.append('<polyline fill="none" stroke="%s" stroke-width="2" points="%s"/>' %
                         (col, " ".join(f"{x:.1f},{y:.1f}" for x, y, _ in pts)))
            for x, y, p in pts:
                o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{col}"><title>{_esc(p["record"])}: {fmt(p["value"])} {s["unit"]} (n={p.get("n")})</title></circle>')
            lx, ly = gx0 + gw + 16, gy0 + 14 + j * 16
            o.append(f'<rect x="{lx}" y="{ly - 9}" width="10" height="10" fill="{col}"/>')
            o.append(f'<text x="{lx + 14}" y="{ly}">{_esc((s["problem"] + " · " + s["metric"])[:34])}</text>')
    o.append("</svg>")
    return "\n".join(o) + "\n"


# ------------------------------------------------------------------ PDF (stdlib)

class Pdf:
    """A deterministic single-font PDF writer: text, lines, rectangles, circles."""

    def __init__(self, w=612, h=792):
        self.w, self.h = w, h
        self.pages: list[list[str]] = []
        self.new_page()

    def new_page(self):
        self.pages.append([])

    def _c(self, s):
        self.pages[-1].append(s)

    @staticmethod
    def _rgb(hexcol):
        h = hexcol.lstrip("#")
        return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

    def text(self, x, y, s, size=10, color="#000000", bold=False):
        r, g, b = self._rgb(color)
        s = s.encode("latin-1", "replace").decode("latin-1").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        font = "/F2" if bold else "/F1"
        self._c(f"BT {font} {size} Tf {r:.3f} {g:.3f} {b:.3f} rg {x:.1f} {self.h - y:.1f} Td ({s}) Tj ET")

    def line(self, x1, y1, x2, y2, color="#000000", width=1, dash=None):
        r, g, b = self._rgb(color)
        d = f"[{dash}] 0 d" if dash else "[] 0 d"
        self._c(f"{r:.3f} {g:.3f} {b:.3f} RG {width} w {d} {x1:.1f} {self.h - y1:.1f} m {x2:.1f} {self.h - y2:.1f} l S")

    def rect(self, x, y, w, h, stroke="#000000", fill=None):
        if fill:
            r, g, b = self._rgb(fill)
            self._c(f"{r:.3f} {g:.3f} {b:.3f} rg {x:.1f} {self.h - y - h:.1f} {w:.1f} {h:.1f} re f")
        if stroke:
            r, g, b = self._rgb(stroke)
            self._c(f"{r:.3f} {g:.3f} {b:.3f} RG 1 w [] 0 d {x:.1f} {self.h - y - h:.1f} {w:.1f} {h:.1f} re S")

    def dot(self, x, y, r=3, color="#000000"):
        self.rect(x - r, y - r, 2 * r, 2 * r, stroke=None, fill=color)

    def polyline(self, pts, color="#000000", width=1.5):
        if len(pts) < 2:
            return
        r, g, b = self._rgb(color)
        parts = [f"{r:.3f} {g:.3f} {b:.3f} RG {width} w [] 0 d {pts[0][0]:.1f} {self.h - pts[0][1]:.1f} m"]
        parts += [f"{x:.1f} {self.h - y:.1f} l" for x, y in pts[1:]]
        self._c(" ".join(parts) + " S")

    def render(self) -> bytes:
        objs: list[bytes] = []

        def add(b: bytes) -> int:
            objs.append(b)
            return len(objs)
        font1 = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        font2 = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
        page_ids = []
        content_ids = []
        for page in self.pages:
            stream = zlib.compress("\n".join(page).encode("latin-1"))
            content_ids.append(add(b"<< /Length %d /Filter /FlateDecode >>\nstream\n" % len(stream) + stream + b"\nendstream"))
        pages_id = len(objs) + len(self.pages) + 1
        for cid in content_ids:
            page_ids.append(add(
                f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {self.w} {self.h}] "
                f"/Resources << /Font << /F1 {font1} 0 R /F2 {font2} 0 R >> >> /Contents {cid} 0 R >>".encode()))
        kids = " ".join(f"{p} 0 R" for p in page_ids)
        real_pages_id = add(f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode())
        assert real_pages_id == pages_id
        catalog = add(f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode())
        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = []
        for i, body in enumerate(objs, 1):
            offsets.append(len(out))
            out += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"
        xref = len(out)
        out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
        for off in offsets:
            out += f"{off:010d} 00000 n \n".encode()
        out += f"trailer\n<< /Size {len(objs) + 1} /Root {catalog} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
        return bytes(out)


def render_pdf(prog: dict) -> bytes:
    import math
    pdf = Pdf()
    W, H, M = pdf.w, pdf.h, 48
    y = 60
    pdf.text(M, y, f"Benchmark progress: {prog['repo']}", 18, bold=True)
    y += 20
    pdf.text(M, y, "From bench.record/v1 records in Git; raw data in S3 by SHA-256. Derived numbers are labelled derived.", 9, "#555555")
    y += 14
    pdf.text(M, y, "Records: " + ", ".join(f"{k} {v}" for k, v in prog["records"].items()) +
             f". Headline unit {prog['headline_unit']}: {prog['units'][prog['headline_unit']]['meaning']}.", 9, "#555555")
    y += 24
    panels = chart_panels(prog)
    if not panels:
        pdf.text(M, y, "No measured records yet.", 11)
    PH = 200
    for panel in panels:
        if y + PH + 40 > H - M:
            pdf.new_page()
            y = 60
        pdf.text(M, y, panel["title"], 11, bold=True)
        y += 10
        gx0, gy0, gw, gh = M + 40, y, W - 2 * M - 200, PH - 40
        pdf.rect(gx0, gy0, gw, gh, stroke="#999999")
        geom = panel_geometry(panel)
        if geom is None:
            pdf.text(gx0 + 8, gy0 + 16, "no points", 9, "#555555")
            y += PH
            continue
        x0, x1, y0, y1 = geom

        def X(d):
            return gx0 + (d - x0) / (x1 - x0) * gw

        def Y(v):
            v = math.log10(v) if panel["log"] else v
            return gy0 + gh - (v - y0) / (y1 - y0) * gh
        for k in range(5):
            yv = y0 + (y1 - y0) * k / 4
            yy = gy0 + gh - gh * k / 4
            lab = f"{10 ** yv:.3g}" if panel["log"] else f"{yv:.3g}"
            pdf.line(gx0, yy, gx0 + gw, yy, "#eeeeee")
            pdf.text(gx0 - 34, yy + 3, lab, 7, "#555555")
        for k in range(4):
            xv = x0 + (x1 - x0) * k / 3
            xx = gx0 + gw * k / 3
            pdf.text(xx - 22, gy0 + gh + 12, dt.date.fromordinal(int(round(xv))).isoformat(), 7, "#555555")
        zy = Y(1.0 if panel["log"] else 0.0)
        if gy0 <= zy <= gy0 + gh:
            pdf.line(gx0, zy, gx0 + gw, zy, "#bbbbbb", 1, "4 3")
        pdf.text(M - 4, gy0 - 2, panel["ylabel"], 7, "#555555")
        for j, s in enumerate(panel["series"]):
            col = PALETTE[j % len(PALETTE)]
            pts = [(X(_date_num(p["date"])), Y(panel["y"](p))) for p in s["points"]
                   if panel["y"](p) is not None and (not panel["log"] or panel["y"](p) > 0)]
            pdf.polyline(pts, col)
            for px, py in pts:
                pdf.dot(px, py, 2.5, col)
            lx, ly = gx0 + gw + 12, gy0 + 12 + j * 12
            pdf.rect(lx, ly - 7, 8, 8, stroke=None, fill=col)
            pdf.text(lx + 12, ly, (s["problem"] + " · " + s["metric"])[:30], 7)
        y += PH
    # Table page(s)
    pdf.new_page()
    y = 60
    pdf.text(M, y, "Series summary", 14, bold=True)
    y += 18
    cols = [(M, "problem · metric"), (M + 230, "unit"), (M + 270, "first"), (M + 330, "latest"),
            (M + 390, "gain vs first"), (M + 460, "value/ref"), (M + 510, "pts")]
    for x, t in cols:
        pdf.text(x, y, t, 8, bold=True)
    y += 6
    pdf.line(M, y, W - M, y, "#999999")
    y += 12
    for s in prog["series"]:
        if y > H - M:
            pdf.new_page()
            y = 60
        d = s["latest_derived"]
        vals = [(s["problem"] + " · " + s["metric"])[:48], s["unit"], fmt(s["first"]), fmt(s["latest"]),
                (fmt(d.get("improvement_vs_first_percent")) + "%") if d.get("improvement_vs_first_percent") is not None else "–",
                fmt(d.get("value_over_reference")), str(len(s["points"]))]
        for (x, _), v in zip(cols, vals):
            pdf.text(x, y, v, 8)
        y += 12
    y += 16
    for line in _wrap(prog["note"], 110):
        if y > H - M:
            pdf.new_page()
            y = 60
        pdf.text(M, y, line, 8, "#555555")
        y += 11
    return pdf.render()


def _wrap(s: str, n: int) -> list[str]:
    words, lines, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------------ main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=None, help="repository root (default: from cwd)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init")
    p.add_argument("--slug", required=True)
    p.add_argument("--problem", required=True)
    p.add_argument("--curve", default=None, help="curve UID (urn:ec-record:1:sha256:...) or EC1 alias")
    p.add_argument("--entry", action="append", help="benchmarks/<date>-<slug> directory this run fills")
    p.set_defaults(fn=cmd_init)

    p = sub.add_parser("run")
    p.add_argument("record")
    p.add_argument("--cwd", default=None)
    p.add_argument("command", nargs=argparse.REMAINDER)
    p.set_defaults(fn=cmd_run)

    p = sub.add_parser("add-raw")
    p.add_argument("record")
    p.add_argument("paths", nargs="+")
    p.add_argument("--s3-uri", default=None, help="where the file already is (isolab results bucket); default the content-addressed store")
    p.set_defaults(fn=cmd_add_raw)

    p = sub.add_parser("metric")
    p.add_argument("record")
    p.add_argument("--name", required=True)
    p.add_argument("--value", required=True, type=float)
    p.add_argument("--unit", required=True)
    p.add_argument("--better", choices=("lower", "higher", "neutral"), default=None)
    p.add_argument("--n", type=int, default=None)
    p.add_argument("--spread-low", type=float, default=None)
    p.add_argument("--spread-high", type=float, default=None)
    p.add_argument("--baseline", type=float, default=None, help="the frozen baseline value this run was compared with, same unit")
    p.add_argument("--reference", type=float, default=None, help="the reference value (matched rho), same unit")
    p.add_argument("--reference-kind", choices=REFERENCE_KINDS, default="matched_rho")
    p.add_argument("--note", default=None)
    p.set_defaults(fn=cmd_metric)

    p = sub.add_parser("upload")
    p.add_argument("record")
    p.add_argument("--all", action="store_true")
    p.set_defaults(fn=cmd_upload)

    p = sub.add_parser("close")
    p.add_argument("record")
    p.add_argument("--status", required=True, choices=("measured", "invalid", "censored"))
    p.add_argument("--report", default=None)
    p.add_argument("--svg", action="append")
    p.add_argument("--png", action="append")
    p.add_argument("--validation", default=None)
    p.add_argument("--entry", action="append")
    p.add_argument("--summary", default=None)
    p.set_defaults(fn=cmd_close)

    p = sub.add_parser("report")
    p.add_argument("--check", action="store_true")
    p.set_defaults(fn=cmd_report)

    p = sub.add_parser("check")
    p.add_argument("--base", default=None, help="compare against this ref (CI: origin/<base>)")
    p.add_argument("--local", action="store_true", help="also fail on records opened here and not closed")
    p.add_argument("--verify-s3", action="store_true", help="HEAD every raw object (needs AWS credentials)")
    p.set_defaults(fn=cmd_check)

    p = sub.add_parser("gate")
    p.set_defaults(fn=cmd_gate)

    p = sub.add_parser("open")
    p.set_defaults(fn=cmd_open)

    a = ap.parse_args(argv)
    root = (a.root or repo_root()).resolve()
    cfg = load_config(root)
    if a.cmd == "run" and a.command and a.command[0] == "--":
        a.command = a.command[1:]
    return a.fn(a, root, cfg)


if __name__ == "__main__":
    sys.exit(main())
