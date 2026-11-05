"""Write-once fixed F27 C2 instrument control for the future analyze trial.

The fixture is synthetic. It checks nonzero branch actions and rejection of
malformed collision and cross-ratio certificates; it is not a cohort result.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess

from candidate_build import compiler_identity, sha256, sync_directory
from check_all_degree_collision_certificate import verify
from input_manifest import ROOT


PREFIX = "experiments/EXP-PEXT-bf8f96/implementation/"
SOURCES = {PREFIX + name for name in (
    "c2_control_stage.py", "all_degree_collision_certificate.rs",
    "join_certificate.rs", "quotient_core.rs", "symbolic_extension.rs",
    "branch_factorization.rs", "branch_roots.rs", "root_collision.rs",
    "candidate_build.py", "check_all_degree_collision_certificate.py",
    "check_join_certificate.py", "check_compact_class_inputs.py",
    "check_curve_class_certificate.py", "check_quotient_certificate.py",
    "check_structure_certificate.py", "check_rational_collision_certificate.py",
    "generic_disjoint.py", "input_manifest.py",
)} | {"experiments/EXP-PEXT-212d5c/implementation/cover_census_n7.rs"}
SUMMARY = "c2-control.json"
BUILDS = {
    "all-degree": "all_degree_collision_certificate.rs",
    "join": "join_certificate.rs",
}
ARTIFACTS = (SUMMARY,) + tuple(
    f"c2-{tag}{suffix}" for tag in BUILDS for suffix in (
        "", ".build.stdout.log", ".build.stderr.log", ".json",
        ".run.stderr.log"))
FLAGS = ("--edition=2021",)


def checked_sources(source_hashes):
    if not isinstance(source_hashes, dict) or not SOURCES <= set(source_hashes):
        raise ValueError("C2 source closure absent from approved plan")
    observed = {}
    for relative in sorted(SOURCES):
        path = ROOT / relative
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"C2 source missing or symlinked: {relative}")
        digest = sha256(path)
        if source_hashes[relative] != digest:
            raise ValueError(f"C2 source differs from approved plan: {relative}")
        observed[relative] = digest
    return observed


def _files(directory):
    directory = Path(directory)
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("C2 run directory missing or symlinked")
    return {name: directory / name for name in ARTIFACTS}


def _json(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 64 * 1024**2:
        raise ValueError(f"C2 raw certificate missing, symlinked or oversized: {path.name}")
    try:
        return json.loads(path.read_bytes())
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"C2 raw certificate invalid: {path.name}") from error


def _control_result(certificate, joined):
    result = verify(certificate, joined)
    by_label = {row["label"]: row for row in result["targets"]}
    if (result.get("valid") is not True
            or by_label.get("split-22", {}).get("pattern") != [2, 2]
            or by_label["split-22"].get("exceptional") != 20
            or by_label["split-22"].get("nonrational") != 20
            or by_label.get("irreducible-4", {}).get("pattern") != [4]
            or by_label["irreducible-4"].get("exceptional") != 1
            or by_label["irreducible-4"].get("nonrational") != 1
            or [len(certificate["rows"][i]["cross_ratio_orbit"]) for i in (3, 4)] != [6, 1]):
        raise ValueError("C2 positive branch controls differ from fixed prediction")
    return result


def _summary(directory, source_hashes, plan_sha256, run_id, compiler):
    files = _files(directory)
    sources = checked_sources(source_hashes)
    if not isinstance(plan_sha256, str) or len(plan_sha256) != 64 or not isinstance(run_id, str):
        raise ValueError("C2 plan or RUN identity invalid")
    compiler = Path(compiler)
    selected = shutil.which("rustc")
    if selected is None or compiler != Path(selected).absolute():
        raise ValueError("C2 compiler differs from selected rustc")
    if compiler.is_symlink() and not compiler.resolve().is_file():
        raise ValueError("C2 compiler missing")
    shim, real = compiler_identity(compiler)
    version = subprocess.run([str(compiler), "--version", "--verbose"],
                             capture_output=True, text=True, check=True,
                             timeout=30).stdout.strip()
    if not version.startswith("rustc "):
        raise ValueError("C2 compiler version invalid")
    hashes = {}
    commands = {}
    for tag, source in BUILDS.items():
        binary = files[f"c2-{tag}"]
        build = [str(compiler), *FLAGS, str(ROOT / PREFIX / source),
                 "-o", str(binary) + ".partial"]
        run = [str(binary)] + (["f27-char3"] if tag == "join" else [])
        commands[tag] = {"build": build, "run": run}
    for name, path in files.items():
        if name == SUMMARY:
            continue
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"C2 retained artifact missing or symlinked: {name}")
        hashes[name] = sha256(path)
    result = _control_result(_json(files["c2-all-degree.json"]),
                             _json(files["c2-join.json"]))
    return {"schema": "pext.control-c2-synthetic/v1",
            "status": "fixed_software_fixture_checked",
            "scope": "F27 synthetic branch actions; no curve/T cohort result",
            "plan_sha256": plan_sha256, "run_id": run_id,
            "source_sha256": sources,
            "compiler": str(compiler), "compiler_shim": shim,
            "compiler_shim_sha256": sha256(shim),
            "compiler_real": real, "compiler_sha256": sha256(real),
            "compiler_version": version, "commands": commands,
            "artifact_sha256": hashes, "result": result}


def run_control(directory, source_hashes, plan_sha256, run_id):
    """Build and run the pinned fixture once, retaining every attempted output."""
    files = _files(directory)
    if (not isinstance(plan_sha256, str) or len(plan_sha256) != 64
            or not isinstance(run_id, str) or not run_id):
        raise ValueError("C2 plan or RUN identity invalid")
    partials = [Path(str(files[f"c2-{tag}"]) + ".partial") for tag in BUILDS]
    if any(path.exists() or path.is_symlink() for path in
           (*files.values(), *partials)):
        raise FileExistsError("C2 fixture attempt already exists")
    checked_sources(source_hashes)
    compiler = shutil.which("rustc")
    if compiler is None:
        raise ValueError("C2 rustc unavailable")
    compiler = str(Path(compiler).absolute())
    for tag, source in BUILDS.items():
        binary = files[f"c2-{tag}"]
        partial = Path(str(binary) + ".partial")
        command = [compiler, *FLAGS, str(ROOT / PREFIX / source), "-o", str(partial)]
        with files[f"c2-{tag}.build.stdout.log"].open("xb") as stdout, \
                files[f"c2-{tag}.build.stderr.log"].open("xb") as stderr:
            result = subprocess.run(command, cwd=ROOT, stdin=subprocess.DEVNULL,
                                    stdout=stdout, stderr=stderr, timeout=180,
                                    check=False)
            stdout.flush(); os.fsync(stdout.fileno())
            stderr.flush(); os.fsync(stderr.fileno())
        if result.returncode != 0 or partial.is_symlink() or not partial.is_file():
            raise ValueError(f"C2 {tag} build failed; logs retained")
        os.replace(partial, binary)
        command = [str(binary)] + (["f27-char3"] if tag == "join" else [])
        with files[f"c2-{tag}.json"].open("xb") as stdout, \
                files[f"c2-{tag}.run.stderr.log"].open("xb") as stderr:
            result = subprocess.run(command, cwd=ROOT, stdin=subprocess.DEVNULL,
                                    stdout=stdout, stderr=stderr, timeout=180,
                                    check=False)
            stdout.flush(); os.fsync(stdout.fileno())
            stderr.flush(); os.fsync(stderr.fileno())
        if result.returncode != 0:
            raise ValueError(f"C2 {tag} fixture failed; raw output retained")
    record = _summary(directory, source_hashes, plan_sha256, run_id, compiler)
    with files[SUMMARY].open("xb") as stream:
        stream.write((json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode())
        stream.flush(); os.fsync(stream.fileno())
    sync_directory(directory)
    return record


def check_control(directory, source_hashes, plan_sha256, run_id):
    """Independently replay retained raw certificates and exact summary bytes."""
    files = _files(directory)
    if any((path.exists() or path.is_symlink()) for path in
           (Path(str(files[f"c2-{tag}"]) + ".partial") for tag in BUILDS)):
        raise ValueError("C2 incomplete build artifact remains")
    summary = files[SUMMARY]
    if summary.is_symlink() or not summary.is_file():
        raise ValueError("C2 summary missing or symlinked")
    try:
        saved = json.loads(summary.read_bytes())
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("C2 summary invalid") from error
    if not isinstance(saved, dict) or not isinstance(saved.get("compiler"), str):
        raise ValueError("C2 compiler receipt invalid")
    expected = _summary(directory, source_hashes, plan_sha256, run_id,
                        saved["compiler"])
    if summary.read_bytes() != (json.dumps(expected, sort_keys=True,
                                          separators=(",", ":")) + "\n").encode():
        raise ValueError("C2 summary differs from independent raw replay")
    return {"schema": "pext.control-c2-check/v1", "valid": True,
            "summary_sha256": sha256(summary),
            "raw_certificate_sha256": expected["artifact_sha256"]["c2-all-degree.json"],
            "raw_join_sha256": expected["artifact_sha256"]["c2-join.json"]}
