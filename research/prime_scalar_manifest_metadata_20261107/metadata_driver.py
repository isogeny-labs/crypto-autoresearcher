"""Single-thread worker. Loaded only by the reviewed native supervisor.

The worker never invokes subprocesses. The materializer/auditor is imported
only after the nonce gate binds actual unit identity and effective sources.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import time
import traceback


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode()


def checked_path(value, existing=True):
    path = Path(value)
    if not path.is_absolute() or str(path) != value or ".." in path.parts:
        raise RuntimeError("noncanonical absolute path")
    for ancestor in reversed((path, *path.parents)):
        try:
            info = ancestor.lstat()
        except FileNotFoundError:
            if ancestor != path or existing:
                raise
            continue
        if stat.S_ISLNK(info.st_mode):
            raise RuntimeError("symlink path refused: " + str(ancestor))
    return path


def read_bytes(path, limit):
    checked_path(str(path))
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        with os.fdopen(fd, "rb") as stream:
            value = stream.read(limit + 1)
    except BaseException:
        raise
    if len(value) > limit:
        raise RuntimeError("byte bound exceeded")
    return value


def parse(payload):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise RuntimeError("duplicate JSON key")
            result[key] = value
        return result

    def reject(value):
        raise RuntimeError("nonfinite JSON number " + value)
    return json.loads(payload.decode("utf-8"), object_pairs_hook=unique, parse_constant=reject)


def exclusive(path, value, maximum_bytes=1024 * 1024):
    path = checked_path(str(path), existing=False)
    payload = canonical(value)
    if len(payload) > maximum_bytes:
        raise RuntimeError("serialized output exceeds reserved per-file byte allowance")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def cgroup_path():
    lines = Path("/proc/self/cgroup").read_text().splitlines()
    unified = [line[3:] for line in lines if line.startswith("0::")]
    if len(unified) != 1:
        raise RuntimeError("unified cgroup missing")
    return unified[0]


def load_pinned(name, path, digest):
    # Execute exactly the already-hashed bytes. importlib's pathname loader can
    # otherwise race replacement or select a stale pyc after the hash check.
    payload = read_bytes(path, 4 * 1024 * 1024)
    if hashlib.sha256(payload).hexdigest() != digest:
        raise RuntimeError("source digest changed")
    spec = importlib.util.spec_from_loader(name, loader=None, origin=str(path))
    module = importlib.util.module_from_spec(spec)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(payload, str(path), "exec"), module.__dict__)
    return module


def main():
    if len(sys.argv) != 3:
        raise RuntimeError("expected exact binding path and SHA256")
    payload = read_bytes(sys.argv[1], 1024 * 1024)
    digest = hashlib.sha256(payload).hexdigest()
    if digest != sys.argv[2]:
        raise RuntimeError("worker binding digest mismatch")
    binding = parse(payload)
    terminal = binding["terminal"]
    record = {"schema": "prime-scalar.metadata-worker-terminal/v1", "status": "incomplete",
              "phase": binding["phase"], "binding_sha256": digest, "pid": os.getpid(),
              "invocation_id": os.environ.get("INVOCATION_ID"), "cgroup": cgroup_path(),
              "candidate_calls": 0, "oracle_calls": 0}
    try:
        if binding["schema"] != "prime-scalar.metadata-worker-binding/v1":
            raise RuntimeError("worker binding schema")
        if os.getuid() != binding["uid"] or os.geteuid() != binding["uid"]:
            raise RuntimeError("worker UID mismatch")
        if binding["phase"] not in ("builder", "audit"):
            raise RuntimeError("worker phase mismatch")
        if Path.cwd() != Path(binding["repository"]):
            raise RuntimeError("worker cwd mismatch")
        if cgroup_path() != binding["worker_cgroup"]:
            raise RuntimeError("worker membership mismatch")
        for path, expected in binding["effective_source_sha256"].items():
            actual = hashlib.sha256(read_bytes(path, 4 * 1024 * 1024)).hexdigest()
            if actual != expected:
                raise RuntimeError("effective source mismatch: " + path)
        deadline = time.monotonic() + 5.0
        gate = Path(binding["gate"])
        while not gate.exists():
            if time.monotonic() >= deadline:
                raise RuntimeError("worker release gate absent within startup bound")
            time.sleep(0.01)
        release = parse(read_bytes(gate, 1024 * 1024))
        expected_release = {
            "schema": "prime-scalar.metadata-release-gate/v1", "nonce": binding["nonce"],
            "binding_sha256": digest, "task_id": binding["task_id"], "epoch": binding["epoch"],
            "owner": binding["owner"], "phase": binding["phase"], "pid": os.getpid(),
            "worker_invocation_id": os.environ.get("INVOCATION_ID"),
            "worker_unit": binding["worker_unit"], "worker_cgroup": cgroup_path(),
            "source_sha256": binding["effective_source_sha256"],
            "spec_sha256": binding["spec_sha256"], "claim_sha256": binding["claim_sha256"],
            "approval_sha256": binding["approval_sha256"],
            "parent_invocation_id": binding["parent_invocation_id"],
            "parent_pid": binding["parent_pid"], "parent_start_ticks": binding["parent_start_ticks"],
            "parent_deadline_monotonic": binding["parent_deadline_monotonic"],
            "worker_deadline_monotonic": release.get("worker_deadline_monotonic")}
        if canonical(release) != canonical(expected_release):
            raise RuntimeError("nonce/identity/source release mismatch")
        if (type(release["worker_deadline_monotonic"]) not in (int, float)
                or not time.monotonic() < release["worker_deadline_monotonic"] <= binding["latest_worker_deadline_monotonic"]
                or time.monotonic() >= binding["parent_deadline_monotonic"]):
            raise RuntimeError("absolute external deadline binding invalid")
        parent_stat = Path("/proc/" + str(binding["parent_pid"]) + "/stat").read_text()
        if int(parent_stat.rsplit(")", 1)[1].split()[19]) != binding["parent_start_ticks"]:
            raise RuntimeError("parent PID reused")
        parent_groups = Path("/proc/" + str(binding["parent_pid"]) + "/cgroup").read_text().splitlines()
        if "0::" + binding["parent_cgroup"] not in parent_groups:
            raise RuntimeError("parent PID membership changed")
        for group in (binding["shared_cgroup"], binding["parent_cgroup"], binding["worker_cgroup"]):
            root = Path("/sys/fs/cgroup" + group)
            quota, period = (root / "cpu.max").read_text().split()
            if quota == "max" or int(quota) != int(period):
                raise RuntimeError("CPU cap ineffective")
            if (root / "memory.max").read_text().strip() != "536870912":
                raise RuntimeError("memory cap ineffective")
            if (root / "memory.swap.max").read_text().strip() != "0":
                raise RuntimeError("swap cap ineffective")
        if (Path("/sys/fs/cgroup" + binding["worker_cgroup"]) / "pids.max").read_text().strip() != "1":
            raise RuntimeError("worker TasksMax ineffective")
        if (Path("/sys/fs/cgroup" + binding["shared_cgroup"]) / "pids.max").read_text().strip() != "17":
            raise RuntimeError("aggregate TasksMax ineffective")
        if time.time() >= binding["not_after_epoch"]:
            raise RuntimeError("claim/phase deadline expired before worker operation")
        if binding["phase"] == "builder":
            module = load_pinned("_approved_metadata_builder", binding["builder_path"],
                                 binding["effective_source_sha256"][binding["builder_path"]])
            returned = module.materialize(binding["spec_path"], binding["manifest_path"],
                                          binding["admission_reference"])
            manifest_bytes = read_bytes(binding["manifest_path"], 64 * 1024 * 1024)
            if set(returned) != {"metadata_admission", "sha256", "bytes", "counts"}:
                raise RuntimeError("builder return receipt keys")
            if (returned["sha256"] != hashlib.sha256(manifest_bytes).hexdigest()
                    or type(returned["bytes"]) is not int or returned["bytes"] != len(manifest_bytes)
                    or returned["metadata_admission"] != binding["admission_reference"]):
                raise RuntimeError("builder return receipt disagrees with actual bytes")
            result = {"schema": "prime-scalar.metadata-builder-receipt/v1", "status": "complete",
                      "materialize_return": returned, "authority": release,
                      "resource_binding": binding, "candidate_calls": 0, "oracle_calls": 0}
        else:
            manifest_bytes = read_bytes(binding["manifest_path"], 64 * 1024 * 1024)
            if hashlib.sha256(manifest_bytes).hexdigest() != binding["manifest_sha256"]:
                raise RuntimeError("audit manifest bytes not frozen by launch")
            module = load_pinned("_approved_metadata_auditor", binding["auditor_path"],
                                 binding["effective_source_sha256"][binding["auditor_path"]])
            try:
                result = module.audit(binding["manifest_path"], binding["spec_path"], binding["layout_path"],
                                      binding["manifest_sha256"], binding["effective_source_sha256"][binding["layout_path"]])
                if result["auditor_sha256"] != binding["effective_source_sha256"][binding["auditor_path"]]:
                    raise RuntimeError("auditor self-source changed")
            except module.AuditFailure as error:
                result = {"schema": "prime-scalar.metadata-audit/v1", "status": "fail",
                          "first_failure": error.record, "authority": release,
                          "candidate_calls": 0, "oracle_calls": 0}
                exclusive(binding["receipt_path"], result, binding["receipt_byte_limit"])
                raise RuntimeError("independent audit mismatch; receipt retained") from error
            result["authority"] = release
        exclusive(binding["receipt_path"], result, binding["receipt_byte_limit"])
        record["status"] = "complete"
        record["receipt_sha256"] = hashlib.sha256(read_bytes(binding["receipt_path"], 4 * 1024 * 1024)).hexdigest()
    except BaseException as error:
        record["error"] = type(error).__name__ + ": " + str(error)[:2048]
        record["traceback"] = traceback.format_exc()[-8192:]
        raise
    finally:
        record["finished_epoch"] = time.time()
        exclusive(terminal, record)


if __name__ == "__main__":
    main()
