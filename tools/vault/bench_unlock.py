"""Run the frozen, local software unlock comparison; never launch research."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import signal
import statistics
import subprocess
import sys
import time


PUBLIC_FIXTURE_KEY = "public-vault-unlock-software-fixture-20261114"


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def git(root, *args, env=None, data=None, timeout=120):
    return subprocess.run(
        ["git", "-C", str(root), *args], env=env, input=data,
        capture_output=True, check=True, timeout=timeout,
    ).stdout


def source_inputs(root, candidate, protocol_path):
    if re.fullmatch(r"[0-9a-f]{40}", candidate) is None:
        raise ValueError("candidate must be a full published commit ID")
    raw_protocol = protocol_path.read_bytes()
    protocol = json.loads(raw_protocol)
    if raw_protocol != git(root, "show", candidate + ":" + protocol["protocol_path"]):
        raise ValueError("protocol differs from its candidate commit")
    if Path(__file__).read_bytes() != git(root, "show", candidate + ":" + protocol["harness_path"]):
        raise ValueError("benchmark harness differs from its candidate commit")
    sources = {}
    revisions = {"baseline": protocol["baseline_commit"], "candidate": candidate}
    for arm, revision in revisions.items():
        body = git(root, "show", revision + ":" + protocol["controller_path"])
        if hashlib.sha256(body).hexdigest() != protocol[arm + "_controller_sha256"]:
            raise ValueError(arm + " controller source digest differs")
        compile(body, arm + "-vaultctl.py", "exec")
        sources[arm] = body
    return protocol, sources


def fixture_environment():
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("GIT_", "CAVAULT_"))
           and key not in ("KEY", "PYTHONPATH", "PYTHONSTARTUP")}
    env.update(
        KEY=PUBLIC_FIXTURE_KEY,
        GIT_CONFIG_GLOBAL=os.devnull,
        GIT_CONFIG_NOSYSTEM="1",
        PYTHONDONTWRITEBYTECODE="1",
        OMP_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1",
    )
    return env


def payload(protocol, number):
    prefix = b"public unlock software fixture/v1\0"
    seed = (protocol["seed"] + ":" + str(number)).encode()
    return prefix + hashlib.shake_256(seed).digest(protocol["bytes_per_file"] - len(prefix))


def prepare(output, protocol, sources, env):
    expected = {}
    for number in range(protocol["files"]):
        data = payload(protocol, number)
        expected[f"data/{number:04d}.bin"] = hashlib.sha256(data).hexdigest()
    expected["data/empty.bin"] = hashlib.sha256(b"").hexdigest()
    roots, scripts, trees = {}, {}, {}
    source_dir = output / "sources"
    source_dir.mkdir()
    for arm, body in sources.items():
        script = source_dir / (arm + "-vaultctl.py")
        script.write_bytes(body)
        root = output / ("fixture-" + arm)
        (root / "data").mkdir(parents=True)
        (root / ".gitattributes").write_text(
            "* filter=vault -text\n/.gitattributes -filter -text\n"
        )
        for number in range(protocol["files"]):
            (root / f"data/{number:04d}.bin").write_bytes(payload(protocol, number))
        (root / "data/empty.bin").write_bytes(b"")
        git(root, "init", "-q", env=env)
        git(root, "config", "user.name", "Software Fixture", env=env)
        git(root, "config", "user.email", "fixture@example.invalid", env=env)
        git(root, "config", "core.hooksPath", os.devnull, env=env)
        subprocess.run(
            [sys.executable, str(script), "setup", "--quiet", "--script", str(script)],
            cwd=root, env=env, check=True, capture_output=True, timeout=60,
        )
        git(root, "add", ".", env=env)
        git(root, "commit", "-qm", "deterministic software fixture", env=env)
        trees[arm] = git(root, "write-tree", env=env).decode().strip()
        roots[arm], scripts[arm] = root, script
    if len(set(trees.values())) != 1:
        raise ValueError("baseline and candidate fixture trees differ")
    write_json(output / "input-manifest.json", {
        "schema": "software.vault-unlock.inputs/v1",
        "files_sha256": expected, "git_trees": trees,
        "payload_bytes": protocol["files"] * protocol["bytes_per_file"],
    })
    return roots, scripts, expected, trees


def relock(root, names, env):
    requests = b"".join(("HEAD:" + name + "\n").encode() for name in names)
    data = git(root, "cat-file", "--batch", env=env, data=requests)
    cursor = 0
    for name in names:
        end = data.index(b"\n", cursor)
        header = data[cursor:end].split()
        if len(header) != 3 or header[1] != b"blob":
            raise ValueError("fixture blob is unavailable")
        length = int(header[2])
        cursor = end + 1
        body = data[cursor:cursor + length]
        if len(body) != length or data[cursor + length:cursor + length + 1] != b"\n":
            raise ValueError("fixture batch is truncated")
        if not body.startswith(b"VLT1"):
            raise ValueError("fixture is not stored as ciphertext")
        (root / name).write_bytes(body)
        cursor += length + 1
    if cursor != len(data):
        raise ValueError("unexpected fixture batch suffix")


def run_trial(root, script, arm, role, number, output, protocol, env, expected, tree, deadline):
    import psutil

    if time.monotonic() >= deadline:
        raise TimeoutError("campaign deadline before relocking")
    relock(root, expected, env)
    if git(root, "write-tree", env=env).decode().strip() != tree:
        raise ValueError("relocking changed the fixture index")
    if time.monotonic() >= deadline:
        raise TimeoutError("campaign deadline before unlock launch")
    prefix = output / f"{number:02d}-{role}-{arm}"
    started = time.monotonic()
    status, samples, peak, code = "running", 0, 0, None
    with prefix.with_suffix(".stdout.log").open("wb") as stdout, \
            prefix.with_suffix(".stderr.log").open("wb") as stderr, \
            prefix.with_suffix(".rss.jsonl").open("w") as trace:
        proc = subprocess.Popen(
            [sys.executable, str(script), "unlock", "--quiet", "--script", str(script)],
            cwd=root, env=env, stdout=stdout, stderr=stderr, start_new_session=True,
        )
        process = psutil.Process(proc.pid)
        try:
            while proc.poll() is None:
                now = time.monotonic()
                if now > deadline or now - started > protocol["trial_timeout_seconds"]:
                    status = "censored_timeout"
                    os.killpg(proc.pid, signal.SIGKILL)
                    break
                rss, identities = 0, []
                try:
                    children = [process, *process.children(recursive=True)]
                except psutil.NoSuchProcess:
                    children = []
                for child in children:
                    try:
                        resident = child.memory_info().rss
                    except psutil.NoSuchProcess:
                        continue
                    rss += resident
                    identities.append({"pid": child.pid, "rss_bytes": resident})
                trace.write(json.dumps({"seconds": now - started, "sum_rss_bytes": rss,
                                        "processes": identities}) + "\n")
                peak, samples = max(peak, rss), samples + 1
                time.sleep(protocol["rss_sample_period_seconds"])
        finally:
            if proc.poll() is None:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            code = proc.wait()
    elapsed = time.monotonic() - started
    if status == "running":
        status = "completed" if code == 0 else "failed"
    controls = {}
    if status == "completed":
        controls["plaintext_digests"] = all(
            hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
            for name, digest in expected.items()
        )
        controls["index_tree"] = git(root, "write-tree", env=env).decode().strip() == tree
        controls["clean_status"] = not git(root, "status", "--porcelain", env=env).strip()
        controls["required_filter"] = git(root, "config", "--get", "filter.vault.required",
                                         env=env).strip() == b"true"
        if not all(controls.values()) or not samples:
            status = "failed_software_control"
    return {"trial": number, "arm": arm, "role": role, "status": status,
            "exit": code, "wall_seconds": elapsed, "sampled_peak_sum_rss_bytes": peak,
            "rss_samples": samples, "controls": controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    protocol, sources = source_inputs(root, args.candidate, args.protocol.resolve())
    if args.validate_only:
        print("published benchmark inputs match their frozen digests")
        return 0
    if args.output is None:
        parser.error("--output is required for a measured run")
    import cryptography
    import psutil
    from cryptography.hazmat.backends.openssl.backend import backend

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "source-and-host.json", {
        "candidate_commit": args.candidate, "protocol": protocol,
        "python": sys.version, "platform": platform.platform(),
        "cryptography": cryptography.__version__, "openssl": backend.openssl_version_text(),
        "psutil": psutil.__version__, "isolation": protocol["isolation"],
        "controllers_sha256": {arm: hashlib.sha256(body).hexdigest()
                               for arm, body in sources.items()},
    })
    deadline = time.monotonic() + protocol["campaign_timeout_seconds"]
    rows = []
    try:
        env = fixture_environment()
        roots, scripts, expected, trees = prepare(output, protocol, sources, env)
        for role, order in (("warmup", protocol["warmup_order"]),
                            ("measured", protocol["measured_order"])):
            for arm in order:
                row = run_trial(roots[arm], scripts[arm], arm, role, len(rows), output,
                                protocol, env, expected, trees[arm], deadline)
                rows.append(row)
                with (output / "trials.jsonl").open("a") as raw:
                    raw.write(json.dumps(row) + "\n")
                print(f"trial {row['trial']:02d} {role} {arm}: {row['status']}", flush=True)
                if row["status"] != "completed":
                    raise RuntimeError("trial did not meet the frozen software controls")
        measured = {arm: [row for row in rows if row["role"] == "measured" and row["arm"] == arm]
                    for arm in ("baseline", "candidate")}
        summary = {"schema": "software.vault-unlock.summary/v1", "status": "measured",
                   "scope": protocol["workload_scope"], "isolation": protocol["isolation"]}
        for arm, values in measured.items():
            walls = [row["wall_seconds"] for row in values]
            memory = [row["sampled_peak_sum_rss_bytes"] for row in values]
            summary[arm] = {
                "n": len(values), "wall_median_seconds": statistics.median(walls),
                "wall_range_seconds": [min(walls), max(walls)],
                "sampled_rss_median_bytes": statistics.median(memory),
                "sampled_rss_range_bytes": [min(memory), max(memory)],
            }
        pairs = list(zip(measured["baseline"], measured["candidate"]))
        summary["derived_paired_wall_ratios"] = [
            before["wall_seconds"] / after["wall_seconds"] for before, after in pairs
        ]
        summary["derived_median_paired_wall_ratio"] = statistics.median(
            summary["derived_paired_wall_ratios"])
        write_json(output / "summary.json", summary)
        return 0
    except Exception as error:
        write_json(output / "failure.json", {"status": "incomplete", "error_type": type(error).__name__,
                                             "detail": str(error), "completed_rows": len(rows)})
        raise


if __name__ == "__main__":
    raise SystemExit(main())
