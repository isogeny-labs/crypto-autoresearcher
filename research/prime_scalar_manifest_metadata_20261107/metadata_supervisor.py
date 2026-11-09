"""Native cooperative-ownership gate and bounded user-systemd supervisor.

SOURCE ONLY. No invocation is admitted by this file's existence. The trusted
operator supplies a published Coordinator approval and a fresh launch binding.
Operational custody persists outside the canonical artifact directory.
"""
import os
import signal
import time

# Arm the process-birth startup bound before importing the remaining helpers or
# touching the trusted launch path. A malformed FIFO/device launch path must
# never consume the outer seventy-second parent envelope.
with open("/proc/self/stat", "r", encoding="ascii") as _process_stat_stream:
    _process_start_ticks = int(_process_stat_stream.read().rsplit(")", 1)[1].split()[19])
_clock_ticks = os.sysconf("SC_CLK_TCK")
_boot_offset = time.clock_gettime(time.CLOCK_BOOTTIME) - time.monotonic()
STARTUP_DEADLINE = _process_start_ticks / _clock_ticks - _boot_offset + 5 - 1 / _clock_ticks
signal.signal(signal.SIGALRM, signal.SIG_DFL)
signal.setitimer(signal.ITIMER_REAL, max(0.000001, STARTUP_DEADLINE - time.monotonic()))

import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import secrets
import stat
import subprocess
import sys

REPOSITORY = "/home/ec2-user/crypto-prime-sat-ideas-20261029"
BASE = "research/prime_scalar_manifest_metadata_20261107/"
SOURCE_TASK = "TASK-20261107-57cb8a"
TASK = "TASK-20261107-e7cdd2"
QUEUE = "coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-a99822/dispatch_queue.json"
CLAIMS = "coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-a99822/claims/"
APPROVAL = "coordination/prime_scalar_manifest_metadata_20261107/metadata-phase-approval.json"
SPEC = "coordination/prime_scalar_validation_harness_source_20261107/case-generation-spec.json"
SPEC_SHA = "7f68929cedcf12965554d96eefe7b1aeddef82f0f1bb182e6e37113e16d5e9dc"
BUILDER = "research/prime_scalar_validation_harness_source_20261107/manifest_builder.py"
BUILDER_SHA = "26b91af10fb3170ccc3b15df92aea0ca215d6ecaf4bdbd8dad546ae8a3969bdc"
SOURCE_PATHS = tuple(BASE + name for name in (
    "metadata_driver.py", "metadata_supervisor.py", "audit_manifest.py", "audit-contract.json"))
OUTPUT_PATHS = tuple(BASE + name for name in (
    "public-output-layout.json", "manifest.json", "builder-receipt.json", "audit-receipt.json",
    "supervisor-receipts.json", "report.md", "diagram.svg", "report.typ", "report.pdf", "report-inputs.json"))
RESOURCE_POLICY = {"cpu_quota_percent": 100, "memory_bytes": 536870912, "swap_bytes": 0,
                   "parent_seconds": 70, "worker_seconds": 60, "startup_seconds": 5,
                   "cleanup_seconds": 5, "parent_tasks": 16, "worker_tasks": 1,
                   "shared_tasks": 17,
                   "concurrency": 1, "builder_invocations": 1, "audit_invocations": 1,
                   "retries": 0, "candidate_calls": 0, "oracle_calls": 0,
                   "manifest_bytes": 67108864, "total_output_bytes": 134217728}
CUSTODY_NAMES = ("reservation.json", "worker-binding.json", "release-gate.pending", "release-gate.json",
                 "worker-terminal.json", "supervisor-terminal.json")


def fail(message):
    raise RuntimeError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode()


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def keys(value, expected, label):
    if type(value) is not dict or set(value) != set(expected):
        fail(label + ": exact keyset required")


def strict_equal(actual, expected, label):
    if canonical(actual) != canonical(expected):
        fail(label + ": value/type mismatch")


def parse(payload):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                fail("duplicate object key")
            result[key] = value
        return result

    def bad(value):
        fail("nonfinite number: " + value)
    return json.loads(payload.decode("utf-8"), object_pairs_hook=unique, parse_constant=bad)


def timestamp(value):
    if type(value) is not str or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value):
        fail("exact UTC timestamp required")
    return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp()


def relpath(value):
    if type(value) is not str or not value or value.startswith("/"):
        fail("repository-relative path required")
    if str(Path(value)) != value or ".." in Path(value).parts or ":" in value:
        fail("noncanonical repository path")
    return value


def safe_path(value, exists=True):
    if type(value) is not str or not value.startswith("/") or str(Path(value)) != value:
        fail("canonical absolute path required")
    path = Path(value)
    if ".." in path.parts:
        fail("parent traversal refused")
    for part in reversed((path, *path.parents)):
        try:
            info = part.lstat()
        except FileNotFoundError:
            if part == path and not exists:
                continue
            raise
        if stat.S_ISLNK(info.st_mode):
            fail("symlink refused: " + str(part))
        if info.st_uid not in (0, os.getuid()) or info.st_mode & 0o022:
            fail("untrusted writable path: " + str(part))
    return path


def read(path, limit=4 * 1024 * 1024):
    safe_path(str(path))
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    if not stat.S_ISREG(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        fail("regular input file required: " + str(path))
    with os.fdopen(descriptor, "rb") as stream:
        payload = stream.read(limit + 1)
    if len(payload) > limit:
        fail("input byte cap exceeded: " + str(path))
    return payload


def exclusive(path, value):
    safe_path(str(path), exists=False)
    payload = canonical(value)
    if len(payload) > 1024 * 1024:
        fail("custody receipt exceeds 1 MiB")
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    fd = os.open(Path(path).parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


class Supervisor:
    def __init__(self, launch):
        self.launch = launch
        self.deadline = STARTUP_DEADLINE
        self.command_env = {"PATH": "/usr/bin:/bin", "HOME": os.path.expanduser("~"),
                            "XDG_RUNTIME_DIR": "/run/user/" + str(os.getuid()),
                            "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/" + str(os.getuid()) + "/bus",
                            "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"}
        self.stage = "startup"
        self.approval = None
        self.claim = None
        self.phase = launch["phase"]
        self.worker_identity = None
        self.terminal_path = None
        self.record = {"schema": "prime-scalar.metadata-supervisor-terminal/v1",
                       "status": "incomplete", "phase": self.phase, "observations": [],
                       "candidate_calls": 0, "oracle_calls": 0}

    def command(self, argv):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            fail(self.stage + " deadline exhausted")
        try:
            result = subprocess.run(argv, cwd=REPOSITORY, stdin=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    timeout=remaining, check=False, env=self.command_env)
        except subprocess.TimeoutExpired as error:
            self.record["observations"].append({"command": argv, "timed_out": True,
                "timeout_seconds": remaining, "stdout": (error.stdout or b"").decode(errors="replace")[:16384],
                "stderr": (error.stderr or b"").decode(errors="replace")[:16384]})
            raise
        if len(result.stdout) + len(result.stderr) > 4 * 1024 * 1024:
            fail("command output limit exceeded")
        if result.returncode != 0:
            self.record["observations"].append({"command": argv, "returncode": result.returncode,
                "stdout_bytes": len(result.stdout), "stderr_bytes": len(result.stderr),
                "stdout_sha256": sha(result.stdout), "stderr_sha256": sha(result.stderr),
                "stdout": result.stdout.decode(errors="replace")[:16384],
                "stderr": result.stderr.decode(errors="replace")[:16384]})
            fail("command failed: " + repr(argv) + ": " + result.stderr.decode(errors="replace")[:2048])
        return result.stdout

    def git(self, *args):
        return self.command(["/usr/bin/git", *args])

    def published(self, binding, local=False):
        keys(binding, ("path", "commit", "sha256"), "Git binding")
        path = relpath(binding["path"])
        commit = binding["commit"]
        if not re.fullmatch(r"[0-9a-f]{40}", commit) or not re.fullmatch(r"[0-9a-f]{64}", binding["sha256"]):
            fail("invalid publication digest")
        self.git("merge-base", "--is-ancestor", commit, self.launch["fetched_commit"])
        self.git("merge-base", "--is-ancestor", commit, self.launch["worktree_commit"])
        if commit not in self.launch["github_readbacks"]:
            fail("missing exact GitHub commit readback")
        readback = self.launch["github_readbacks"][commit]
        keys(readback, ("repository", "commit", "verified_at", "response"), "GitHub readback")
        if (readback["repository"] != self.launch["github_repository"]
                or readback["commit"] != commit or readback["response"].get("sha") != commit):
            fail("GitHub readback does not bind commit")
        if not self.launch["reconciled_epoch"] <= timestamp(readback["verified_at"]) <= time.time():
            fail("GitHub readback freshness")
        payload = self.git("show", commit + ":" + path)
        if sha(payload) != binding["sha256"]:
            fail("published blob digest mismatch: " + path)
        if local and read(REPOSITORY + "/" + path) != payload:
            fail("effective local source differs from publication: " + path)
        return payload

    def show(self, unit):
        properties = ("Id", "InvocationID", "MainPID", "ControlGroup", "Slice", "ActiveState", "SubState",
                      "RuntimeMaxUSec", "TasksMax", "MemoryMax", "MemorySwapMax", "CPUQuotaPerSecUSec",
                      "KillMode", "KillSignal", "SendSIGKILL", "TimeoutStopUSec", "BindsTo", "After", "Result",
                      "ExecMainCode", "ExecMainStatus", "ExecMainStartTimestampMonotonic",
                      "ActiveEnterTimestampMonotonic", "CPUUsageNSec", "MemoryPeak", "LimitFSIZE")
        payload = self.command(["/usr/bin/systemctl", "--user", "show", unit,
                                "--property=" + ",".join(properties)])
        return dict(line.split("=", 1) for line in payload.decode().splitlines() if "=" in line)

    def seconds(self, value):
        if value == "0":
            return 0.0
        total = 0.0
        units = {"us": 0.000001, "ms": 0.001, "s": 1, "min": 60, "h": 3600}
        pieces = re.findall(r"([0-9]+(?:\.[0-9]+)?)(us|ms|min|s|h)", value)
        if not pieces or "".join(number + unit for number, unit in pieces) != value.replace(" ", ""):
            fail("unsupported systemd time value: " + value)
        for number, unit in pieces:
            total += float(number) * units[unit]
        return total

    def group(self, path):
        if not path.startswith("/") or ".." in Path(path).parts:
            fail("noncanonical cgroup")
        root = Path("/sys/fs/cgroup" + path)
        if root.is_symlink():
            fail("symlink cgroup")
        result = {"path": path}
        for name in ("cpu.max", "memory.max", "memory.swap.max", "pids.max", "cpu.stat",
                     "memory.events", "memory.peak", "cgroup.events", "cgroup.procs"):
            item = root / name
            result[name] = item.read_text().strip() if item.exists() else None
        return result

    def controls(self, facts, tasks=None):
        quota, period = facts["cpu.max"].split()
        if quota == "max" or int(quota) != int(period) or int(quota) <= 0:
            fail("effective CPU cap absent")
        if facts["memory.max"] != "536870912" or facts["memory.swap.max"] != "0":
            fail("effective memory/swap cap absent")
        if tasks is not None and facts["pids.max"] != str(tasks):
            fail("effective task cap absent")

    def unit_controls(self, facts, seconds, tasks):
        if (self.seconds(facts["RuntimeMaxUSec"]) != seconds or facts["TasksMax"] != str(tasks)
                or facts["MemoryMax"] != "536870912" or facts["MemorySwapMax"] != "0"
                or self.seconds(facts["CPUQuotaPerSecUSec"]) != 1
                or facts["KillMode"] != "control-group" or facts["SendSIGKILL"] != "yes"
                or facts["KillSignal"] not in ("9", "SIGKILL")
                or self.seconds(facts["TimeoutStopUSec"]) != 0):
            fail("actual unit controls mismatch")

    def fence(self, task):
        pattern = re.compile(re.escape(task) + r"\.([1-9][0-9]*)\.(claim|release)\.json$")
        records = {}
        names = set()
        directory = safe_path(REPOSITORY + "/" + CLAIMS.rstrip("/"))
        for path in directory.iterdir():
            if pattern.fullmatch(path.name):
                names.add(path.name)
                records[path.name] = read(str(path))
        for reference in self.launch["known_refs"]:
            tree = self.git("ls-tree", "-r", "--name-only", reference, "--", CLAIMS).decode().splitlines()
            for path in tree:
                name = Path(path).name
                if not pattern.fullmatch(name):
                    continue
                payload = self.git("show", reference + ":" + path)
                if name in records and records[name] != payload:
                    fail("ambiguous mutated native record")
                records[name] = payload
                names.add(name)
        if not names:
            fail("native claim absent")
        epoch = max(int(pattern.fullmatch(name).group(1)) for name in names)
        claim_name = task + "." + str(epoch) + ".claim.json"
        release_name = task + "." + str(epoch) + ".release.json"
        if claim_name not in records:
            fail("orphan highest-epoch release")
        claim = parse(records[claim_name])
        keys(claim, ("schema", "task_id", "epoch", "owner", "session", "branch", "worktree",
                     "acquired_at", "expires_at", "write_scope", "supersedes", "forced",
                     "supersedes_lost_completion"), "native claim")
        if (claim["schema"] != "crypto.autoresearch.task_claim.v1" or claim["task_id"] != task
                or type(claim["epoch"]) is not int or claim["epoch"] != epoch
                or type(claim["owner"]) is not str or not claim["owner"]
                or type(claim["forced"]) is not bool or type(claim["write_scope"]) is not list):
            fail("malformed native claim")
        for path in claim["write_scope"]:
            relpath(path)
        acquired, expires = timestamp(claim["acquired_at"]), timestamp(claim["expires_at"])
        if acquired >= expires or acquired > time.time():
            fail("invalid native claim times")
        release = None
        if release_name in records:
            release = parse(records[release_name])
            keys(release, ("schema", "task_id", "epoch", "owner", "outcome", "released_at", "was_expired",
                           "note", "artifact_sha256"), "native release")
            if (release["schema"] != "crypto.autoresearch.task_release.v1" or release["task_id"] != task
                    or type(release["epoch"]) is not int or release["epoch"] != epoch
                    or release["owner"] != claim["owner"] or type(release["was_expired"]) is not bool
                    or release["outcome"] not in ("completed", "failed", "abandoned")):
                fail("foreign or malformed release; no completion inferred")
            timestamp(release["released_at"])
        return claim, release, sha(records[claim_name]), sha(records[release_name]) if release else None

    def live_claim(self, reserve_seconds):
        claim, release, digest, _ = self.fence(TASK)
        if release is not None:
            fail("metadata claim already released")
        if (claim["owner"] != self.approval["owner"] or claim["epoch"] != self.launch["epoch"]
                or digest != self.launch["metadata_claim"]["sha256"]
                or claim["worktree"] != REPOSITORY):
            fail("metadata native fencing mismatch")
        strict_equal(sorted(claim["write_scope"]), sorted(OUTPUT_PATHS), "metadata write scope")
        deadline = min(timestamp(claim["expires_at"]), timestamp(self.approval["expires_at"]))
        if time.time() + reserve_seconds >= deadline:
            fail("insufficient unexpired native/phase deadline")
        if "queue" in self.approval and sha(read(REPOSITORY + "/" + QUEUE)) != self.approval["queue"]["sha256"]:
            fail("managed queue changed before reservation/release")
        if "source_release" in self.approval:
            _, source_release, source_digest, release_digest = self.fence(SOURCE_TASK)
            if (source_release is None or source_digest != self.approval["source_claim"]["sha256"]
                    or release_digest != self.approval["source_release"]["sha256"]):
                fail("source disposition changed before reservation/release")
        self.claim = claim
        return deadline

    def validate_authority(self):
        expected_launch = ("schema", "phase", "approval", "decision", "metadata_claim", "epoch",
                           "fetched_commit", "worktree_commit", "known_refs", "github_repository",
                           "github_readbacks", "reconciled_at", "readiness_at", "readiness",
                           "queue_verification", "manifest_sha256")
        keys(self.launch, expected_launch, "trusted launch")
        if self.launch["schema"] != "prime-scalar.metadata-launch/v1" or self.phase not in ("builder", "audit"):
            fail("launch schema/phase")
        if type(self.launch["epoch"]) is not int or self.launch["epoch"] <= 0:
            fail("metadata epoch must be positive integer")
        now = time.time()
        reconciled = timestamp(self.launch["reconciled_at"])
        readiness_time = timestamp(self.launch["readiness_at"])
        if not now - 300 <= reconciled <= readiness_time <= now:
            fail("root reconciliation/readiness older than 300 seconds or future-dated")
        self.launch["reconciled_epoch"] = reconciled
        if Path.cwd() != Path(REPOSITORY) or os.getuid() != os.geteuid():
            fail("wrong caller repository or setuid process")
        for key in ("fetched_commit", "worktree_commit"):
            if not re.fullmatch(r"[0-9a-f]{40}", self.launch[key]):
                fail("exact commit required")
        if self.git("rev-parse", "HEAD").decode().strip() != self.launch["worktree_commit"]:
            fail("worktree HEAD differs from trusted launch")
        if type(self.launch["known_refs"]) is not list or not self.launch["known_refs"]:
            fail("known native refs must be supplied after fresh fetch")
        for reference in self.launch["known_refs"]:
            if not re.fullmatch(r"[0-9a-f]{40}", reference):
                fail("native fencing refs must be resolved immutable commits")
        if self.launch["fetched_commit"] not in self.launch["known_refs"] or self.launch["worktree_commit"] not in self.launch["known_refs"]:
            fail("fencing omitted fetched/worktree ancestry")
        if self.launch["approval"]["path"] != APPROVAL:
            fail("unrecognized approval path")
        approval = parse(self.published(self.launch["approval"]))
        self.approval = approval
        required = ("schema", "phase_id", "execution_scope", "task_id", "owner", "source_task_id", "approved_by",
                    "decision", "issued_at", "expires_at", "caller_uid", "repository", "worktree", "sources",
                    "inputs", "source_claim", "source_release", "static_review", "queue", "layout", "resources",
                    "phases", "interpreter", "environment", "output_byte_limits", "dependency", "prohibitions")
        keys(approval, required, "phase approval")
        for key, expected in (("schema", "prime-scalar.metadata-phase-approval/v1"), ("execution_scope", "metadata_only"),
                              ("task_id", TASK), ("source_task_id", SOURCE_TASK), ("approved_by", "coordinator"),
                              ("repository", REPOSITORY), ("worktree", REPOSITORY),
                              ("dependency", "published_timely_source_completion_before_metadata")):
            strict_equal(approval[key], expected, key)
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", approval["phase_id"]):
            fail("phase identity invalid")
        if type(approval["caller_uid"]) is not int or approval["caller_uid"] != os.getuid():
            fail("caller UID not approved")
        if not timestamp(approval["issued_at"]) <= now < timestamp(approval["expires_at"]):
            fail("phase approval time invalid")
        strict_equal(approval["decision"], self.launch["decision"], "selected Coordinator decision")
        decision_payload = self.published(self.launch["decision"])
        # The Coordinator decision is a published YAML record. The trusted root
        # selects its exact digest; do not pretend a substring proves approval.
        self.record["decision_sha256"] = sha(decision_payload)
        strict_equal(approval["resources"], RESOURCE_POLICY, "fixed finite resource policy")
        strict_equal(approval["prohibitions"], ["candidate_import", "oracle_import", "scientific_execution", "retry", "cloud", "privilege_escalation"], "prohibitions")
        keys(approval["sources"], SOURCE_PATHS, "four-source publication map")
        effective = {}
        for path, binding in approval["sources"].items():
            if binding["path"] != path:
                fail("source binding path mismatch")
            self.published(binding, local=True)
            effective[REPOSITORY + "/" + path] = binding["sha256"]
        keys(approval["inputs"], ("spec", "builder", "interface", "bindings", "source_contract"), "public input bindings")
        for binding in approval["inputs"].values():
            self.published(binding, local=True)
            effective[REPOSITORY + "/" + binding["path"]] = binding["sha256"]
        if (approval["inputs"]["spec"]["path"] != SPEC or approval["inputs"]["spec"]["sha256"] != SPEC_SHA
                or approval["inputs"]["builder"]["path"] != BUILDER or approval["inputs"]["builder"]["sha256"] != BUILDER_SHA):
            fail("locked specification/materializer identity mismatch")
        expected_inputs = {
            "interface": "research/prime_scalar_validation_harness_source_20261107/interface.json",
            "bindings": "coordination/prime_scalar_manifest_metadata_20261107/input-bindings.json",
            "source_contract": "coordination/prime_scalar_manifest_metadata_20261107/source-contract.json"}
        for name, path in expected_inputs.items():
            if approval["inputs"][name]["path"] != path:
                fail("public input path mismatch")
        self.effective = effective
        self.published(approval["source_claim"])
        self.published(approval["source_release"])
        source, release, source_sha, release_sha = self.fence(SOURCE_TASK)
        source_map = {path: binding["sha256"] for path, binding in approval["sources"].items()}
        if (source_sha != approval["source_claim"]["sha256"] or release is None
                or release_sha != approval["source_release"]["sha256"] or release["outcome"] != "completed"
                or release["was_expired"] is not False
                or not timestamp(source["acquired_at"]) <= timestamp(release["released_at"]) <= timestamp(source["expires_at"])):
            fail("timely current source completion missing")
        strict_equal(release["artifact_sha256"], source_map, "source release artifact bindings")
        strict_equal(sorted(source["write_scope"]), sorted(SOURCE_PATHS), "source write scope")
        review = approval["static_review"]
        keys(review, ("text", "sha256", "reviewed_sources", "disposition"), "embedded independent review")
        if sha(review["text"].encode()) != review["sha256"] or review["disposition"] != "accepted_for_metadata_admission":
            fail("independent static review not disposed")
        strict_equal(review["reviewed_sources"], source_map, "reviewed four-source bytes")
        if type(release["note"]) is not str or review["sha256"] not in release["note"]:
            fail("source release note does not retain review digest")
        self.published(self.launch["metadata_claim"])
        expected_claim_path = CLAIMS + TASK + "." + str(self.launch["epoch"]) + ".claim.json"
        if self.launch["metadata_claim"]["path"] != expected_claim_path:
            fail("metadata claim path mismatch")
        self.live_claim(70)
        queue = approval["queue"]
        keys(queue, ("path", "sha256", "descriptor", "gitignore", "remote_verification"), "managed queue")
        if queue["path"] != QUEUE:
            fail("wrong managed queue")
        for name, suffix in (("descriptor", ".artifacts.json"), ("gitignore", ".gitignore")):
            if queue[name]["path"] != str(Path(QUEUE).parent / suffix):
                fail("managed publication descriptor path")
            self.published(queue[name], local=True)
        strict_equal(self.launch["queue_verification"], queue["remote_verification"], "remote verification receipt")
        verification = queue["remote_verification"]
        keys(verification, ("command", "returncode", "stdout", "stderr"), "managed verification receipt")
        if type(verification["returncode"]) is not int or verification["returncode"] != 0 or not verification["stdout"]:
            fail("managed remote verification absent")
        if not any(str(arg).endswith("tools/artifacts/artifacts.py") for arg in verification["command"]) or "verify" not in verification["command"]:
            fail("managed verification command not native artifact verifier")
        raw_queue = read(REPOSITORY + "/" + QUEUE)
        if sha(raw_queue) != queue["sha256"]:
            fail("hydrated queue mismatch")
        parsed_queue = parse(raw_queue)
        if parsed_queue["schema"] != "crypto.autoresearch.dispatch_queue.v1" or parsed_queue["goal_id"] != "GOAL-PFDR-fd09e0" or type(parsed_queue["max_concurrent"]) is not int or parsed_queue["max_concurrent"] != 1:
            fail("queue identity/concurrency")
        tasks = parsed_queue["tasks"]
        if type(tasks) is not list:
            fail("queue tasks must be array")
        matches = [task for task in tasks if task.get("id") == TASK]
        if len(matches) != 1:
            fail("metadata task not unique in queue")
        task = matches[0]
        if task["state"] != "queued" or task["role"] != "executor":
            fail("metadata guarded transition not published as queued")
        strict_equal(task["depends_on"], [SOURCE_TASK], "source dependency")
        strict_equal(sorted(task["write_scope"]), sorted(OUTPUT_PATHS), "queue output scope")
        strict_equal(sorted(task["artifact_paths"]), sorted(OUTPUT_PATHS), "queue artifact scope")
        readiness = self.launch["readiness"]
        keys(readiness, ("command", "returncode", "stdout", "stderr"), "native readiness observation")
        strict_equal(readiness["command"], [approval["interpreter"]["path"], "tools/research_dispatch.py", QUEUE,
                     "--ready-only", "--claims", "local"], "readiness command")
        if type(readiness["returncode"]) is not int or readiness["returncode"] != 0 or type(readiness["stdout"]) is not str:
            fail("native readiness observation failed")
        self.record["readiness"] = readiness
        self.record["queue_verification"] = verification
        layout = approval["layout"]
        if layout["path"] != BASE + "public-output-layout.json":
            fail("layout path mismatch")
        self.published(layout, local=True)
        self.effective[REPOSITORY + "/" + layout["path"]] = layout["sha256"]
        keys(approval["interpreter"], ("path", "sha256"), "interpreter")
        interpreter = safe_path(approval["interpreter"]["path"])
        # Pin a resolved executable path, never a symlink such as python3.
        if sha(read(str(interpreter), 64 * 1024 * 1024)) != approval["interpreter"]["sha256"]:
            fail("interpreter digest mismatch")
        strict_equal(approval["environment"], self.command_env, "exact approved environment")
        keys(approval["output_byte_limits"], OUTPUT_PATHS, "canonical output bounds")
        for path, limit in approval["output_byte_limits"].items():
            if type(limit) is not int or limit <= 0:
                fail("positive integer output limit required")
        if approval["output_byte_limits"][BASE + "manifest.json"] != 67108864:
            fail("manifest byte cap mismatch")
        for name in ("builder-receipt.json", "audit-receipt.json"):
            if approval["output_byte_limits"][BASE + name] != 1024 * 1024:
                fail("worker receipts require exact reserved 1 MiB prewrite cap")
        if sum(approval["output_byte_limits"].values()) + 12 * 1024 * 1024 > 134217728:
            fail("aggregate output allocations exceed 128 MiB including both custody directories")
        keys(approval["phases"], ("builder", "audit"), "two single-use phases")
        for phase, config in approval["phases"].items():
            keys(config, ("slice", "parent_unit", "worker_unit", "custody_directory", "custody_files", "command", "fresh_outputs"), "phase configuration")
            for key, suffix in (("slice", ".slice"), ("parent_unit", ".service"), ("worker_unit", ".service")):
                if not re.fullmatch(r"[a-zA-Z0-9_-]+" + re.escape(suffix), config[key]):
                    fail("canonical systemd unit name required")
            expected_dir = "/home/ec2-user/.local/state/prime-scalar-metadata/" + TASK + "-" + str(self.launch["epoch"]) + "-" + phase
            if config["custody_directory"] != expected_dir:
                fail("exact task/epoch/phase custody directory required")
            strict_equal(config["custody_files"], [expected_dir + "/" + name for name in CUSTODY_NAMES], "custody paths")
            strict_equal(config["command"], [str(interpreter), "-I", "-B", REPOSITORY + "/" + BASE + "metadata_driver.py",
                         expected_dir + "/worker-binding.json", "{binding_sha256}"], "exact worker command template")
            expected_outputs = [BASE + "manifest.json", BASE + "builder-receipt.json"] if phase == "builder" else [BASE + "audit-receipt.json"]
            strict_equal(config["fresh_outputs"], expected_outputs, "phase fresh output scope")
        first, second = approval["phases"]["builder"], approval["phases"]["audit"]
        if any(first[key] == second[key] for key in ("slice", "parent_unit", "worker_unit", "custody_directory")):
            fail("phase identities must be distinct")
        self.config = approval["phases"][self.phase]
        for path in self.config["fresh_outputs"]:
            if safe_path(REPOSITORY + "/" + path, exists=False).exists():
                fail("phase output already exists; reconcile, never relaunch")
        if self.phase == "builder":
            if self.launch["manifest_sha256"] is not None:
                fail("builder cannot bind nonexistent manifest")
        else:
            manifest = read(REPOSITORY + "/" + BASE + "manifest.json", 67108864)
            if sha(manifest) != self.launch["manifest_sha256"]:
                fail("audit frozen manifest binding mismatch")
            builder_terminal = Path(first["custody_directory"]) / "supervisor-terminal.json"
            builder_record = parse(read(str(builder_terminal)))
            if builder_record["status"] != "complete" or builder_record["phase"] != "builder" or builder_record["approval_sha256"] != self.launch["approval"]["sha256"]:
                fail("audit requires complete builder custody for same approval")
            builder_receipt_bytes = read(REPOSITORY + "/" + BASE + "builder-receipt.json")
            builder_receipt = parse(builder_receipt_bytes)
            if (sha(builder_receipt_bytes) != builder_record["worker_terminal"]["receipt_sha256"]
                    or builder_receipt["status"] != "complete"
                    or builder_receipt["materialize_return"]["sha256"] != self.launch["manifest_sha256"]
                    or builder_receipt["materialize_return"]["bytes"] != len(manifest)):
                fail("audit manifest not bound to retained builder receipt and terminal")
        self.record["approval_sha256"] = self.launch["approval"]["sha256"]
        self.record["claim_sha256"] = self.launch["metadata_claim"]["sha256"]
        self.record["effective_source_sha256"] = effective

    def bootstrap_parent_clock(self):
        # Establish the actual service clock before Git/native/approval work.
        # Even this first readback is bounded by conservative process birth.
        groups = [line[3:] for line in Path("/proc/self/cgroup").read_text().splitlines() if line.startswith("0::")]
        if len(groups) != 1:
            fail("unified parent membership absent")
        unit = Path(groups[0]).name
        if not re.fullmatch(r"[a-zA-Z0-9_-]+\.service", unit):
            fail("parent must already be a named service")
        facts = self.show(unit)
        if int(facts["MainPID"]) != os.getpid() or facts["InvocationID"] != os.environ.get("INVOCATION_ID"):
            fail("bootstrap parent identity mismatch")
        start = int(facts["ExecMainStartTimestampMonotonic"]) / 1000000
        if start <= 0:
            fail("actual external parent clock missing")
        self.parent_start = start
        self.deadline = min(self.deadline, start + 5)
        signal.setitimer(signal.ITIMER_REAL, max(0.000001, self.deadline - time.monotonic()))
        if time.monotonic() >= self.deadline:
            fail("actual five-second startup envelope exhausted before authority work")

    def check_parent(self):
        parent = self.show(self.config["parent_unit"])
        if (parent["Id"] != self.config["parent_unit"] or int(parent["MainPID"]) != os.getpid()
                or parent["InvocationID"] != os.environ.get("INVOCATION_ID")
                or parent["Slice"] != self.config["slice"] or parent["ActiveState"] != "active"):
            fail("actual parent unit/PID/invocation mismatch")
        self.unit_controls(parent, 70, 16)
        own_cgroup = [line[3:] for line in Path("/proc/self/cgroup").read_text().splitlines() if line.startswith("0::")]
        if own_cgroup != [parent["ControlGroup"]]:
            fail("parent actual cgroup mismatch")
        shared = self.show(self.config["slice"])
        if shared["Id"] != self.config["slice"] or shared["ActiveState"] != "active":
            fail("shared aggregate slice absent")
        prefix = shared["ControlGroup"] + "/"
        if not parent["ControlGroup"].startswith(prefix):
            fail("parent not under shared cap")
        self.parent = parent
        self.shared = shared
        parent_start = int(parent["ExecMainStartTimestampMonotonic"]) / 1000000
        if parent_start <= 0 or time.monotonic() - parent_start >= 5:
            fail("parent startup exceeded five seconds")
        self.parent_start = parent_start
        self.deadline = min(self.deadline, parent_start + 5)
        parent_facts, shared_facts = self.group(parent["ControlGroup"]), self.group(shared["ControlGroup"])
        self.controls(parent_facts, 16)
        self.controls(shared_facts, 17)
        self.check_membership(None)
        self.record["parent_initial"] = parent
        self.record["parent_cgroup_initial"] = parent_facts
        self.record["shared_cgroup_initial"] = shared_facts

    def check_membership(self, worker_pid):
        root = Path("/sys/fs/cgroup" + self.shared["ControlGroup"])
        expected_directories = {root / self.config["parent_unit"]}
        if worker_pid is not None:
            expected_directories.add(root / self.config["worker_unit"])
        actual_directories = {path for path in root.rglob("*") if path.is_dir()}
        if actual_directories != expected_directories:
            fail("unowned/missing child cgroup even if currently empty")
        pids = set()
        for path in root.rglob("cgroup.procs"):
            pids.update(int(pid) for pid in path.read_text().split())
        expected = {os.getpid()}
        if worker_pid is not None:
            expected.add(worker_pid)
        if pids != expected:
            fail("shared slice contains unowned or missing processes: " + repr(sorted(pids)))
        for pid in pids:
            if Path("/proc/" + str(pid)).stat().st_uid != os.getuid():
                fail("foreign UID in shared slice")

    def byte_inventory(self):
        result = {}
        for path, bound in self.approval["output_byte_limits"].items():
            absolute = REPOSITORY + "/" + path
            checked = safe_path(absolute, exists=False)
            if checked.exists():
                size = checked.stat().st_size
                if not checked.is_file() or size > bound:
                    fail("canonical output byte/type limit: " + path)
                result[absolute] = size
        for config in self.approval["phases"].values():
            directory = Path(config["custody_directory"])
            if not directory.exists():
                continue
            safe_path(str(directory))
            allowed = set(config["custody_files"])
            for path in directory.iterdir():
                safe_path(str(path))
                if str(path) not in allowed or not path.is_file() or path.stat().st_size > 1024 * 1024:
                    fail("unregistered or over-budget custody file")
                result[str(path)] = path.stat().st_size
        if sum(result.values()) > 134217728:
            fail("aggregate canonical/custody bytes exceed 128 MiB")
        return result

    def reserve_and_launch(self):
        self.live_claim(65)
        directory = safe_path(self.config["custody_directory"], exists=False)
        # Existing directory is itself a consumed-or-uncertain attempt. Never
        # delete/reuse it, even if the reservation write was interrupted.
        directory.mkdir(mode=0o700, exist_ok=False)
        fd = os.open(directory.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        self.terminal_path = directory / "supervisor-terminal.json"
        nonce = secrets.token_hex(32)
        reservation = {"schema": "prime-scalar.metadata-reservation/v1", "phase": self.phase,
                       "task_id": TASK, "epoch": self.claim["epoch"], "owner": self.claim["owner"],
                       "approval_sha256": self.launch["approval"]["sha256"],
                       "claim_sha256": self.launch["metadata_claim"]["sha256"], "spec_sha256": SPEC_SHA,
                       "source_sha256": self.effective, "nonce": nonce,
                       "parent_unit": self.config["parent_unit"], "parent_invocation_id": self.parent["InvocationID"],
                       "worker_unit": self.config["worker_unit"], "reserved_epoch": time.time()}
        exclusive(directory / "reservation.json", reservation)
        expected_group = self.shared["ControlGroup"] + "/" + self.config["worker_unit"]
        binding = {"schema": "prime-scalar.metadata-worker-binding/v1", "phase": self.phase,
                   "uid": os.getuid(), "repository": REPOSITORY, "task_id": TASK,
                   "epoch": self.claim["epoch"], "owner": self.claim["owner"], "nonce": nonce,
                   "effective_source_sha256": self.effective, "spec_sha256": SPEC_SHA,
                   "claim_sha256": self.launch["metadata_claim"]["sha256"],
                   "approval_sha256": self.launch["approval"]["sha256"],
                   "parent_invocation_id": self.parent["InvocationID"],
                   "parent_pid": os.getpid(),
                   "parent_start_ticks": int(Path("/proc/self/stat").read_text().rsplit(")", 1)[1].split()[19]),
                   "parent_deadline_monotonic": self.parent_start + 70,
                   "latest_worker_deadline_monotonic": self.parent_start + 65,
                   "parent_cgroup": self.parent["ControlGroup"], "shared_cgroup": self.shared["ControlGroup"],
                   "worker_cgroup": expected_group, "worker_unit": self.config["worker_unit"],
                   "gate": str(directory / "release-gate.json"), "terminal": str(directory / "worker-terminal.json"),
                   "builder_path": REPOSITORY + "/" + BUILDER,
                   "auditor_path": REPOSITORY + "/" + BASE + "audit_manifest.py",
                   "spec_path": REPOSITORY + "/" + SPEC,
                   "layout_path": REPOSITORY + "/" + BASE + "public-output-layout.json",
                   "manifest_path": REPOSITORY + "/" + BASE + "manifest.json",
                   "manifest_sha256": self.launch["manifest_sha256"],
                   "receipt_path": REPOSITORY + "/" + BASE + self.phase + "-receipt.json",
                   "receipt_byte_limit": self.approval["output_byte_limits"][BASE + self.phase + "-receipt.json"],
                   "admission_reference": self.launch["approval"]["commit"] + ":" + APPROVAL,
                   "not_after_epoch": min(timestamp(self.claim["expires_at"]), timestamp(self.approval["expires_at"]))}
        exclusive(directory / "worker-binding.json", binding)
        binding_digest = sha(canonical(binding))
        command = list(self.config["command"])
        command[-1] = binding_digest
        properties = {"CPUQuota": "100%", "MemoryMax": "536870912", "MemorySwapMax": "0", "TasksMax": "1",
                      "RuntimeMaxSec": "60", "TimeoutStopSec": "0", "KillMode": "control-group", "KillSignal": "SIGKILL", "SendSIGKILL": "yes",
                      "BindsTo": self.config["parent_unit"], "After": self.config["parent_unit"],
                      "WorkingDirectory": REPOSITORY, "StandardInput": "null", "StandardOutput": "null",
                      "StandardError": "journal", "LimitFSIZE": "67108864", "UMask": "0077", "NoNewPrivileges": "yes"}
        argv = ["/usr/bin/systemd-run", "--user", "--quiet", "--no-block", "--unit=" + self.config["worker_unit"],
                "--slice=" + self.config["slice"]]
        for name, value in properties.items():
            argv.append("--property=" + name + "=" + value)
        for name, value in self.approval["environment"].items():
            argv.append("--setenv=" + name + "=" + value)
        argv.extend(["--", *command])
        self.command(argv)
        # StartTransientUnit success does not imply the worker is running yet.
        while True:
            worker = self.show(self.config["worker_unit"])
            if worker.get("ActiveState") == "active" and int(worker.get("MainPID", "0")) > 0:
                break
            if worker.get("ActiveState") == "failed" or time.monotonic() >= self.deadline:
                fail("worker failed to start inside startup bound")
            time.sleep(0.01)
        if worker["Id"] != self.config["worker_unit"] or not re.fullmatch(r"[0-9a-f]{32}", worker["InvocationID"]):
            fail("worker unit identity missing")
        self.worker_identity = (worker["Id"], worker["InvocationID"])
        self.unit_controls(worker, 60, 1)
        if (worker["ControlGroup"] != expected_group or worker["Slice"] != self.config["slice"]
                or self.config["parent_unit"] not in worker["BindsTo"].split()
                or self.config["parent_unit"] not in worker["After"].split()
                or worker["LimitFSIZE"] != "67108864"):
            fail("worker placement/prearmed stop/byte cap mismatch")
        worker_pid = int(worker["MainPID"])
        self.controls(self.group(expected_group), 1)
        self.controls(self.group(self.shared["ControlGroup"]), 17)
        self.controls(self.group(self.parent["ControlGroup"]), 16)
        self.check_membership(worker_pid)
        self.live_claim(60)
        if time.monotonic() >= self.deadline:
            fail("startup five-second budget exceeded before release")
        release = {"schema": "prime-scalar.metadata-release-gate/v1", "nonce": nonce,
                   "binding_sha256": binding_digest, "task_id": TASK, "epoch": self.claim["epoch"],
                   "owner": self.claim["owner"], "phase": self.phase, "pid": worker_pid,
                   "worker_invocation_id": worker["InvocationID"], "worker_unit": worker["Id"],
                   "worker_cgroup": worker["ControlGroup"], "source_sha256": self.effective,
                   "spec_sha256": SPEC_SHA, "claim_sha256": self.launch["metadata_claim"]["sha256"],
                   "approval_sha256": self.launch["approval"]["sha256"],
                   "parent_invocation_id": self.parent["InvocationID"],
                   "parent_pid": binding["parent_pid"], "parent_start_ticks": binding["parent_start_ticks"],
                   "parent_deadline_monotonic": binding["parent_deadline_monotonic"],
                   "worker_deadline_monotonic": int(worker["ExecMainStartTimestampMonotonic"]) / 1000000 + 60}
        if release["worker_deadline_monotonic"] > binding["latest_worker_deadline_monotonic"]:
            fail("worker started too late for parent envelope")
        exclusive(directory / "release-gate.pending", release)
        # link() publishes complete, fsynced bytes atomically and refuses an
        # existing destination. The pending hardlink remains immutable custody.
        if time.monotonic() >= self.deadline:
            fail("startup exhausted while preparing durable release")
        os.link(directory / "release-gate.pending", directory / "release-gate.json", follow_symlinks=False)
        directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        self.record["worker_initial"] = worker
        self.record["release"] = release
        self.stage = "worker"
        self.deadline = min(self.parent_start + 65, int(worker["ExecMainStartTimestampMonotonic"]) / 1000000 + 60)
        # The external worker unit is independently bounded. The parent alarm
        # also ends a hung monitor at its own absolute processing boundary.
        signal.setitimer(signal.ITIMER_REAL, max(0.000001, self.deadline - time.monotonic()))
        while time.monotonic() < self.deadline:
            status = self.show(worker["Id"])
            if status["InvocationID"] != worker["InvocationID"]:
                fail("worker invocation changed; ownership uncertain")
            self.byte_inventory()
            if status["ActiveState"] in ("inactive", "failed") and status["MainPID"] == "0":
                self.record["worker_exit"] = status
                break
            time.sleep(min(0.05, max(0, self.deadline - time.monotonic())))
        else:
            fail("worker deadline reached; cleanup required")
        terminal = parse(read(str(directory / "worker-terminal.json")))
        if (terminal["status"] != "complete" or terminal["binding_sha256"] != binding_digest
                or terminal["invocation_id"] != worker["InvocationID"] or status["Result"] != "success"
                or status["ExecMainStatus"] != "0"):
            fail("worker did not complete successfully")
        self.record["worker_terminal"] = terminal
        self.record["status"] = "complete"

    def cleanup(self):
        cleanup_start = time.monotonic()
        self.stage = "cleanup"
        self.deadline = min(cleanup_start + 5, self.parent_start + 70) if hasattr(self, "parent_start") else cleanup_start + 5
        # Default-fatal kernel alarm covers ALL cleanup, including the final
        # terminal serialization/write/fsync in run(). No Python I/O handler.
        signal.setitimer(signal.ITIMER_REAL, max(0.000001, self.deadline - time.monotonic()))
        self.record["cleanup_started_monotonic"] = cleanup_start
        self.record["cleanup_absolute_deadline_monotonic"] = self.deadline
        self.record["terminal_write_within_kernel_alarm"] = True
        if self.worker_identity is not None:
            unit, invocation = self.worker_identity
            actual = self.show(unit)
            if actual["InvocationID"] != invocation:
                fail("cleanup refuses unrelated worker invocation")
            if actual["MainPID"] != "0" or actual["ActiveState"] not in ("inactive", "failed"):
                self.command(["/usr/bin/systemctl", "--user", "stop", unit])
            after = self.show(unit)
            if after["InvocationID"] != invocation or after["MainPID"] != "0" or after["ActiveState"] not in ("inactive", "failed"):
                fail("worker termination not confirmed")
            group = Path("/sys/fs/cgroup" + self.shared["ControlGroup"] + "/" + unit)
            if group.exists() and any(path.read_text().strip() for path in group.rglob("cgroup.procs")):
                fail("worker cgroup still populated")
            self.record["termination"] = {"confirmed": True, "unit": after,
                                           "worker_cgroup_retained": group.exists()}
            journal = self.command(["/usr/bin/journalctl", "--user", "_SYSTEMD_INVOCATION_ID=" + invocation,
                                    "--output=json", "--no-pager", "--lines=50"])
            self.record["worker_journal"] = {"bytes": len(journal), "sha256": sha(journal),
                                            "text": journal.decode(errors="replace")[:131072],
                                            "excerpt_truncated": len(journal) > 131072}
        elif self.approval is not None and hasattr(self, "config"):
            self.record["termination"] = {"confirmed": False,
                "reason": "No authenticated worker InvocationID; no unrelated unit stopped. Root must reconcile named unit; external RuntimeMax/BindsTo remain the bound."}
            self.record["status"] = "incomplete"
        if hasattr(self, "parent"):
            self.record["parent_final"] = self.show(self.config["parent_unit"])
            self.record["parent_cgroup_final"] = self.group(self.parent["ControlGroup"])
            self.record["shared_cgroup_final"] = self.group(self.shared["ControlGroup"])
        if self.approval is not None:
            self.record["byte_inventory"] = self.byte_inventory()
        self.record["cleanup_preterminal_seconds"] = time.monotonic() - cleanup_start

    def run(self):
        try:
            self.bootstrap_parent_clock()
            self.validate_authority()
            self.check_parent()
            self.byte_inventory()
            self.reserve_and_launch()
        except BaseException as error:
            self.record["status"] = "incomplete"
            self.record["error"] = type(error).__name__ + ": " + str(error)[:4096]
        finally:
            try:
                self.cleanup()
            except BaseException as error:
                self.record["status"] = "incomplete"
                self.record["cleanup_error"] = type(error).__name__ + ": " + str(error)[:4096]
            self.record["finished_epoch"] = time.time()
            if self.terminal_path is not None:
                exclusive(self.terminal_path, self.record)
            else:
                # No unauthorized custody path is created before authority has
                # been established. Root captures this stdout and unit status.
                sys.stdout.buffer.write(canonical(self.record))
                sys.stdout.buffer.flush()
            signal.setitimer(signal.ITIMER_REAL, 0)
        return 0 if self.record["status"] == "complete" else 1


def main():
    if len(sys.argv) != 3 or not re.fullmatch(r"[0-9a-f]{64}", sys.argv[2]):
        fail("trusted launch requires exact binding path and SHA256")
    payload = read(sys.argv[1], 1024 * 1024)
    if sha(payload) != sys.argv[2]:
        fail("trusted launch digest mismatch")
    return Supervisor(parse(payload)).run()


if __name__ == "__main__":
    raise SystemExit(main())
