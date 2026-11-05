"""Build and verify a write-once candidate binary from frozen Rust sources."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

from input_manifest import ROOT


SOURCES = (
    "experiments/EXP-PEXT-bf8f96/implementation/candidate_unit.rs",
    "experiments/EXP-PEXT-bf8f96/implementation/quotient_core.rs",
    "experiments/EXP-PEXT-bf8f96/implementation/symbolic_extension.rs",
    "experiments/EXP-PEXT-bf8f96/implementation/branch_factorization.rs",
    "experiments/EXP-PEXT-bf8f96/implementation/branch_roots.rs",
    "experiments/EXP-PEXT-bf8f96/implementation/root_collision.rs",
    "experiments/EXP-PEXT-212d5c/implementation/cover_census_n7.rs",
)
FLAGS = ("--edition=2021", "-O")


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sync_directory(directory):
    fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def checked_sources(expected_hashes):
    if not isinstance(expected_hashes, dict) or not set(SOURCES) <= set(expected_hashes):
        raise ValueError("frozen Rust source closure missing")
    result = {}
    for relative in SOURCES:
        path = ROOT / relative
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"missing or symlinked Rust source: {relative}")
        actual = sha256(path)
        if expected_hashes[relative] != actual:
            raise ValueError(f"frozen Rust source hash mismatch: {relative}")
        result[relative] = actual
    return result


def compiler_identity(compiler):
    """Record both the invoked shim and the selected real rustc executable."""
    compiler = Path(compiler)
    if not compiler.is_file():
        raise ValueError("rustc command missing")
    shim = compiler.resolve()
    if shim.name == "rustup":
        selected = subprocess.run([str(compiler), "--print", "sysroot"],
                                  capture_output=True, text=True, check=True).stdout.strip()
        real = Path(selected) / "bin" / "rustc"
    else:
        real = shim
    if not real.is_file():
        raise ValueError("selected rustc executable missing")
    return str(shim), str(real.resolve())


def build(run_dir, expected_hashes):
    """Compile once; retain failed attempts and never adopt an old binary."""
    directory = Path(run_dir)
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("build run directory missing or symlinked")
    sources = checked_sources(expected_hashes)
    binary = directory / "candidate-unit"
    partial = directory / "candidate-unit.partial"
    receipt_path = directory / "candidate-build.json"
    stdout_path = directory / "build.stdout.log"
    stderr_path = directory / "build.stderr.log"
    if any(path.exists() or path.is_symlink() for path in
           (binary, partial, receipt_path, stdout_path, stderr_path)):
        raise FileExistsError("candidate build attempt already exists")
    compiler = shutil.which("rustc")
    if compiler is None:
        raise ValueError("rustc unavailable")
    compiler = str(Path(compiler).absolute())
    shim, real = compiler_identity(compiler)
    version = subprocess.run([compiler, "--version", "--verbose"],
                             capture_output=True, text=True, check=True).stdout.strip()
    if not version.startswith("rustc "):
        raise ValueError("unexpected rustc version output")
    command = [compiler, *FLAGS, str(ROOT / SOURCES[0]), "-o", str(partial)]
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        result = subprocess.run(command, cwd=ROOT, stdin=subprocess.DEVNULL,
                                stdout=stdout, stderr=stderr, check=False)
        stdout.flush(); os.fsync(stdout.fileno())
        stderr.flush(); os.fsync(stderr.fileno())
    if result.returncode != 0:
        raise ValueError(f"candidate build failed with rustc exit {result.returncode}; logs retained")
    if not partial.is_file() or partial.is_symlink():
        raise ValueError("rustc returned without candidate binary")
    with partial.open("rb") as stream:
        os.fsync(stream.fileno())
    os.replace(partial, binary)
    receipt = {"schema": "pext.candidate-build/v1", "status": "built",
               "source_sha256": sources, "compiler": compiler,
               "compiler_shim": shim, "compiler_shim_sha256": sha256(shim),
               "compiler_real": real, "compiler_sha256": sha256(real),
               "compiler_version": version,
               "flags": list(FLAGS), "command": command,
               "binary": binary.name, "binary_sha256": sha256(binary),
               "stdout_sha256": sha256(stdout_path),
               "stderr_sha256": sha256(stderr_path)}
    with receipt_path.open("x") as stream:
        json.dump(receipt, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
        stream.flush(); os.fsync(stream.fileno())
    sync_directory(directory)
    return binary, receipt


def verify_build(run_dir, expected_hashes):
    """Read-only external check of sources, compiler, command and binary."""
    directory = Path(run_dir)
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("build run directory missing or symlinked")
    path = directory / "candidate-build.json"
    if path.is_symlink() or not path.is_file():
        raise ValueError("candidate build receipt missing or symlinked")
    try:
        receipt = json.loads(path.read_bytes())
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("candidate build receipt invalid") from error
    sources = checked_sources(expected_hashes)
    binary = directory / "candidate-unit"
    stdout = directory / "build.stdout.log"
    stderr = directory / "build.stderr.log"
    compiler = receipt.get("compiler") if isinstance(receipt, dict) else None
    if not isinstance(compiler, str) or not Path(compiler).is_file():
        raise ValueError("candidate compiler identity missing")
    shim = receipt.get("compiler_shim")
    real = receipt.get("compiler_real")
    if (not isinstance(shim, str) or not Path(shim).is_file()
            or not isinstance(real, str) or not Path(real).is_file()):
        raise ValueError("candidate compiler executable missing")
    command = [compiler, *FLAGS, str(ROOT / SOURCES[0]), "-o",
               str(directory / "candidate-unit.partial")]
    real_version = subprocess.run([real, "--version", "--verbose"],
                                  capture_output=True, text=True, check=True).stdout.strip()
    if (binary.is_symlink() or not binary.is_file()
            or stdout.is_symlink() or not stdout.is_file()
            or stderr.is_symlink() or not stderr.is_file()
            or receipt.get("schema") != "pext.candidate-build/v1"
            or receipt.get("status") != "built"
            or receipt.get("source_sha256") != sources
            or receipt.get("flags") != list(FLAGS)
            or receipt.get("command") != command
            or receipt.get("binary") != binary.name
            or shim != str(Path(compiler).resolve())
            or receipt.get("compiler_shim_sha256") != sha256(shim)
            or receipt.get("compiler_sha256") != sha256(real)
            or receipt.get("binary_sha256") != sha256(binary)
            or receipt.get("stdout_sha256") != sha256(stdout)
            or receipt.get("stderr_sha256") != sha256(stderr)
            or receipt.get("compiler_version") != real_version
            or not real_version.startswith("rustc ")):
        raise ValueError("candidate build receipt or binary mismatch")
    return binary, receipt
