"""Deterministically seal completed candidate units into bounded tar chunks.

Each unit keeps its write-once input and receipt bytes inside the chunk. The
source directories are removed only after the tar and its receipt are fsynced
and every member has been read back and matched to the source digest. A
failure leaves the source directories for reconciliation; it never retries.
"""

import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tarfile

from input_manifest import ROOT

sys.path.insert(0, str(ROOT / "tools"))
import artifact_store


FILES = ("input.json", "receipt.json", "unit.json.gz", "stderr.log")
MAX_UNITS = 16
MAX_UNIT_GZIP_BYTES = 3 * 1024 * 1024
MAX_CHUNK_BYTES = 49 * 1024 * 1024
UNIT_NAME = re.compile(r"u[0-9]{6}\Z")
CHUNK_NAME = re.compile(r"chunk-[0-9]{6}\.tar\Z")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def sync_directory(path):
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def checked_unit_files(directory):
    directory = Path(directory)
    if (directory.is_symlink() or not directory.is_dir()
            or not UNIT_NAME.fullmatch(directory.name)
            or set(path.name for path in directory.iterdir()) != set(FILES)):
        raise ValueError("unit directory shape or name")
    files = {}
    for name in FILES:
        path = directory / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("unit member missing or symlinked")
        if name == "unit.json.gz" and path.stat().st_size > MAX_UNIT_GZIP_BYTES:
            raise ValueError("compressed unit exceeds frozen chunk allowance")
        files[name] = path.read_bytes()
    if len(files["unit.json.gz"]) > MAX_UNIT_GZIP_BYTES:
        raise ValueError("compressed unit exceeds frozen chunk allowance")
    try:
        receipt = json.loads(files["receipt.json"])
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("unit receipt invalid") from error
    if (not isinstance(receipt, dict)
            or receipt.get("schema") != "pext.candidate-unit-artifact/v1"
            or receipt.get("status") != "candidate_emitted"
            or receipt.get("input_sha256") != digest(files["input.json"])
            or receipt.get("compressed_sha256") != digest(files["unit.json.gz"])
            or receipt.get("stderr_sha256") != digest(files["stderr.log"])):
        raise ValueError("unit custody check failed before sealing")
    return files


def add_member(archive, name, data):
    member = tarfile.TarInfo(name)
    member.size = len(data)
    member.mtime = 0
    member.uid = member.gid = 0
    member.uname = member.gname = ""
    member.mode = 0o644
    archive.addfile(member, io.BytesIO(data))


def receipt_path(chunk_path):
    return chunk_path.with_suffix(".receipt.json")


def read_chunk(chunk_path):
    """Read and check the sealed tar; return its ordered exact unit bytes."""
    chunk_path = Path(chunk_path)
    receipt_file = receipt_path(chunk_path)
    stored = artifact_store.resolve(chunk_path)
    if (not CHUNK_NAME.fullmatch(chunk_path.name) or stored is None
            or stored.is_symlink() or receipt_file.is_symlink()
            or not receipt_file.is_file()):
        raise ValueError("chunk or receipt missing, symlinked or misnamed")
    with artifact_store.open_artifact(chunk_path) as stream:
        tar_bytes = stream.read(MAX_CHUNK_BYTES + 1)
    if len(tar_bytes) > MAX_CHUNK_BYTES:
        raise ValueError("chunk exceeds repository file ceiling")
    try:
        receipt = json.loads(receipt_file.read_bytes())
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("chunk receipt invalid") from error
    if (not isinstance(receipt, dict)
            or receipt.get("schema") != "pext.candidate-chunk-receipt/v1"
            or receipt.get("status") != "sealed"
            or receipt.get("chunk") != chunk_path.name
            or receipt.get("tar_sha256") != digest(tar_bytes)):
        raise ValueError("chunk receipt identity or digest mismatch")
    members = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:") as archive:
            for member in archive:
                if (not member.isfile() or member.name in members or member.mtime != 0
                        or member.uid != 0 or member.gid != 0 or member.mode != 0o644):
                    raise ValueError("chunk member metadata or duplicate")
                if member.name != "manifest.json":
                    parts = member.name.split("/")
                    if (len(parts) != 2 or not UNIT_NAME.fullmatch(parts[0])
                            or parts[1] not in FILES):
                        raise ValueError("unexpected chunk member path")
                source = archive.extractfile(member)
                if source is None:
                    raise ValueError("unreadable chunk member")
                members[member.name] = source.read()
    except (tarfile.TarError, EOFError) as error:
        raise ValueError("invalid chunk tar") from error
    if "manifest.json" not in members:
        raise ValueError("chunk manifest absent")
    manifest_bytes = members.pop("manifest.json")
    if receipt.get("manifest_sha256") != digest(manifest_bytes):
        raise ValueError("chunk manifest digest mismatch")
    try:
        manifest = json.loads(manifest_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("chunk manifest invalid") from error
    if not isinstance(manifest, dict):
        raise ValueError("chunk manifest shape")
    rows = manifest.get("units")
    if (manifest.get("schema") != "pext.candidate-chunk/v1"
            or manifest.get("chunk") != chunk_path.name
            or not isinstance(rows, list) or not 1 <= len(rows) <= MAX_UNITS
            or receipt.get("unit_count") != len(rows)):
        raise ValueError("chunk manifest identity or count")
    expected_members, units, names = set(), [], []
    for row in rows:
        name = row.get("name") if isinstance(row, dict) else None
        if not isinstance(name, str) or not UNIT_NAME.fullmatch(name) or name in names:
            raise ValueError("chunk unit identity")
        names.append(name)
        hashes = row.get("sha256")
        if not isinstance(hashes, dict) or set(hashes) != set(FILES):
            raise ValueError("chunk unit hash map")
        files = {}
        for filename in FILES:
            member = f"{name}/{filename}"
            expected_members.add(member)
            if member not in members or digest(members[member]) != hashes[filename]:
                raise ValueError("chunk member digest mismatch")
            files[filename] = members[member]
        units.append((name, files))
    if set(members) != expected_members or receipt.get("unit_names") != names:
        raise ValueError("chunk member coverage or order mismatch")
    return units, receipt


def seal_chunk(directories, chunk_path, *, remove_sources=True):
    """Seal 1-16 completed units; never overwrite a prior chunk or attempt."""
    directories = [Path(path) for path in directories]
    chunk_path = Path(chunk_path)
    if (not 1 <= len(directories) <= MAX_UNITS
            or len({path.name for path in directories}) != len(directories)
            or not CHUNK_NAME.fullmatch(chunk_path.name)
            or not chunk_path.parent.is_dir()):
        raise ValueError("chunk shape, count or destination")
    partial = chunk_path.with_suffix(".partial")
    receipt_file = receipt_path(chunk_path)
    if chunk_path.exists() or partial.exists() or receipt_file.exists():
        raise FileExistsError("refusing to overwrite chunk or partial attempt")
    checked = [(directory.name, checked_unit_files(directory)) for directory in directories]
    rows = [{"name": name, "sha256": {filename: digest(files[filename]) for filename in FILES}}
            for name, files in checked]
    manifest_bytes = canonical({"schema": "pext.candidate-chunk/v1",
                                "chunk": chunk_path.name, "units": rows})
    with partial.open("xb") as stream:
        with tarfile.open(fileobj=stream, mode="w") as archive:
            for name, files in checked:
                for filename in FILES:
                    add_member(archive, f"{name}/{filename}", files[filename])
            add_member(archive, "manifest.json", manifest_bytes)
        stream.flush()
        os.fsync(stream.fileno())
    tar_bytes = partial.read_bytes()
    if len(tar_bytes) > MAX_CHUNK_BYTES:
        raise ValueError("chunk exceeds repository file ceiling; sources retained")
    receipt = {"schema": "pext.candidate-chunk-receipt/v1", "status": "sealed",
               "chunk": chunk_path.name, "tar_sha256": digest(tar_bytes),
               "manifest_sha256": digest(manifest_bytes), "unit_count": len(checked),
               "unit_names": [name for name, _ in checked]}
    os.replace(partial, chunk_path)
    with receipt_file.open("x") as stream:
        json.dump(receipt, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    sync_directory(chunk_path.parent)
    restored, verified = read_chunk(chunk_path)
    if (verified != receipt or restored != checked):
        raise ValueError("sealed chunk readback differs from source units")
    if remove_sources:
        for directory in directories:
            shutil.rmtree(directory)
    return receipt


def expected_units(plan):
    """Frozen class-major, T-minor unit names and fixed 16-unit chunk slots."""
    classes = plan.get("classes") if isinstance(plan, dict) else None
    if not isinstance(classes, list) or not classes:
        raise ValueError("join plan classes missing")
    rows = []
    for class_index, class_row in enumerate(classes):
        targets = class_row.get("targets") if isinstance(class_row, dict) else None
        if not isinstance(targets, list) or not targets:
            raise ValueError("join plan T list missing")
        for t_index in range(len(targets)):
            ordinal = len(rows)
            if ordinal >= 1_000_000:
                raise ValueError("unit ordinal exceeds frozen name space")
            rows.append({"name": f"u{ordinal:06d}", "class_index": class_index,
                         "T_index": t_index, "chunk": f"chunk-{ordinal//MAX_UNITS:06d}.tar"})
    return rows


def check_chunk_directory(run_dir, chunk_names):
    """Reject undeclared chunks, partial attempts and leftover unit folders."""
    chunks_dir = Path(run_dir) / "chunks"
    if chunks_dir.is_symlink() or not chunks_dir.is_dir():
        raise ValueError("chunk directory missing or symlinked")
    expected_files = set()
    for name in chunk_names:
        archive = chunks_dir / name
        stored = artifact_store.resolve(archive)
        if stored is None or stored.is_symlink():
            raise ValueError("declared chunk missing or symlinked")
        expected_files.add(stored.name)
        expected_files.add(receipt_path(archive).name)
    if {path.name for path in chunks_dir.iterdir()} != expected_files:
        raise ValueError("unexpected or incomplete chunk file")
    if any(UNIT_NAME.fullmatch(path.name) for path in Path(run_dir).iterdir()):
        raise ValueError("unsealed unit directory remains")


def seal_complete_index(run_dir, cohort, plan, plan_sha256, binary_sha256):
    """Write a complete index only after every fixed chunk is sealed."""
    run_dir = Path(run_dir)
    chunks_dir = run_dir / "chunks"
    if (run_dir.is_symlink() or chunks_dir.is_symlink() or not chunks_dir.is_dir()
            or (run_dir / "units-index.json").exists()):
        raise ValueError("run/chunk directory missing, symlinked or already indexed")
    if (not isinstance(cohort, str) or not re.fullmatch(r"q[0-9]+-n[0-9]+", cohort)
            or not isinstance(plan_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", plan_sha256)
            or not isinstance(binary_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", binary_sha256)):
        raise ValueError("index external identities invalid")
    units = expected_units(plan)
    chunk_names = list(dict.fromkeys(row["chunk"] for row in units))
    check_chunk_directory(run_dir, chunk_names)
    chunks = []
    for name in chunk_names:
        archive = chunks_dir / name
        restored, receipt = read_chunk(archive)
        wanted = [row["name"] for row in units if row["chunk"] == name]
        if [unit_name for unit_name, _ in restored] != wanted:
            raise ValueError("chunk class/T unit coverage mismatch")
        chunks.append({"name": name, "tar_sha256": receipt["tar_sha256"],
                       "receipt_sha256": digest(receipt_path(archive).read_bytes()),
                       "unit_names": wanted})
    record = {"schema": "pext.candidate-units-index/v1", "status": "complete",
              "cohort": cohort, "join_plan_sha256": plan_sha256,
              "input_sha256": plan["input_sha256"],
              "manifest_sha256": plan["manifest_sha256"],
              "binary_sha256": binary_sha256,
              "structure_order": plan["order"],
              "unit_count": len(units), "units": units, "chunks": chunks}
    with (run_dir / "units-index.json").open("x") as stream:
        json.dump(record, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    sync_directory(run_dir)
    return record


def verify_complete_index(run_dir, cohort, plan, plan_sha256, binary_sha256):
    """Read back finite full-cohort chunk coverage, including stored forms."""
    run_dir = Path(run_dir)
    path = run_dir / "units-index.json"
    if run_dir.is_symlink() or path.is_symlink() or not path.is_file():
        raise ValueError("complete index missing or symlinked")
    try:
        record = json.loads(path.read_bytes())
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("complete index invalid") from error
    units = expected_units(plan)
    if (not isinstance(record, dict) or record.get("schema") != "pext.candidate-units-index/v1"
            or record.get("status") != "complete" or record.get("cohort") != cohort
            or record.get("join_plan_sha256") != plan_sha256
            or record.get("input_sha256") != plan["input_sha256"]
            or record.get("manifest_sha256") != plan["manifest_sha256"]
            or record.get("binary_sha256") != binary_sha256
            or record.get("structure_order") != plan["order"]
            or record.get("unit_count") != len(units) or record.get("units") != units):
        raise ValueError("complete index differs from published plan")
    expected_chunks = list(dict.fromkeys(row["chunk"] for row in units))
    check_chunk_directory(run_dir, expected_chunks)
    chunks = record.get("chunks")
    if not isinstance(chunks, list) or len(chunks) != len(expected_chunks):
        raise ValueError("complete index chunk cardinality")
    for name, row in zip(expected_chunks, chunks):
        archive = run_dir / "chunks" / name
        restored, receipt = read_chunk(archive)
        wanted = [unit["name"] for unit in units if unit["chunk"] == name]
        if (not isinstance(row, dict) or row.get("name") != name
                or row.get("tar_sha256") != receipt["tar_sha256"]
                or row.get("receipt_sha256") != digest(receipt_path(archive).read_bytes())
                or row.get("unit_names") != wanted
                or [unit_name for unit_name, _ in restored] != wanted):
            raise ValueError("complete index chunk receipt or coverage mismatch")
    return {"valid": True, "cohort": cohort, "unit_count": len(units),
            "chunk_count": len(chunks), "index_sha256": digest(path.read_bytes())}
