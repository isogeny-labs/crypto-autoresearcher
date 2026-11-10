#!/usr/bin/env python3
"""Mechanical task cards: the instructions the director tier hands the
mechanical tier, checked and executed by a tool rather than trusted.

`docs/model-tiers.md` is the design. The topology is three hops:

  1. the `experiment-director` (director tier, Sonnet) compiles a decided
     experiment into a task card that names every value the mechanical
     executor needs: an approved runbook (`kind: runbook`), or a list of
     frozen commands (`kind: frozen_command`);
  2. the main session relays the card to `executor-mechanical` (Haiku) as the
     exact text `prompt` prints -- it adds nothing, so the relay cannot
     introduce a choice the director did not make;
  3. the director assesses the result, starting from `check-relay`, which
     establishes without judgment whether the executor's report is the
     tool's output or something the executor wrote itself.

A card is accepted only when it leaves the executor nothing to decide. `lint`
enforces that: every field present, every path and digest real, no
operator-facing word that hands a choice back, no unfilled placeholder, and --
for an `EXP-*` card -- a committed approval. The card adds no authority: an
approval it cites is the Coordinator's.

A frozen-command card is executed by `run`, never by the model: the tool
checks the pinned commit and every bound digest, runs each argv without a
shell under its timeout, writes stdout and stderr where the card says, and
writes a write-once receipt with every exit code and digest. The executor
runs one command and relays what it prints, exactly as a runbook executor
relays `tools/runbook.py`. So `check-relay` works for both kinds.

ONE FILE, EVERY REPOSITORY. This file is canonical in
aburan28/crypto-autoresearcher and copied byte-identical into the sibling
repositories (crypto, cryptanalysis), so whichever repository's
`executor-mechanical` answers a dispatch, the same card works. It depends only
on PyYAML; `kind: runbook` additionally needs `tools/runbook.py`, which only
crypto-autoresearcher has, and is refused elsewhere. Change it here and copy
it; never edit a copy.

    python3 tools/task_card.py lint <card.yaml>
    python3 tools/task_card.py prompt <card.yaml>
    python3 tools/task_card.py run <card.yaml>            # frozen_command only
    python3 tools/task_card.py wait <card.yaml> [--interval 30] [--max-seconds 540]
    python3 tools/task_card.py status <card.yaml>
    python3 tools/task_card.py check-relay <card.yaml> --report <executor-report.txt>
    python3 tools/task_card.py request compile --design <spec> [--bind <path>]... --out <card.yaml>
    python3 tools/task_card.py request assess <card.yaml> [--report <executor-report.txt>]
    python3 tools/task_card.py ingest <reply.md> --expect card --out <card.yaml>
    python3 tools/task_card.py ingest <reply.md> --expect assessment --card <card.yaml> --out <assessment.yaml>
    python3 tools/task_card.py lane --design <spec> [--bind <path>]... --card <card.yaml> \
        --assessment <assessment.yaml> [--via auto|conductor|delphi] [--task T-42] [--route]
        [--free local|public]

BATCH LANE. `request` prints a single-turn prompt with every fact computed
(HEAD, sha256s, the receipt, what changed on disk), for a batch API: Delphi
(`conductor delphi ask --profile director --wait --file <prompt>`) or
`python3 -m orchestration.adapter batch submit --role experiment-director`
in crypto-autoresearcher. `ingest` writes the reply only when it is
mechanically right. Between them, `run` executes the card with no model.
`lane` does all of it end to end through one backend: Conductor-hosted
Delphi (the key is in the project vault) or standalone `delphi` (the key is
ANTHROPIC_API_KEY); `--via auto` picks whichever is connected. `--route` asks
`delphi route` which model each step's task family goes to (Delphi's capability
registry) and escalates a step the tool refuses to the next model in the chain.
`--free local|public` runs standalone delphi in free mode (DELPHI_FREE): only
models that cost nothing are called (self-hosted, local, and with `public` the
free remote tiers, which may log prompts: public or synthetic designs only);
a paid model is substituted from Delphi's free map or refused.

DETACHED STEPS. The executor's shell is killed at 600 s, and a container
restart kills whatever that shell started. So a command whose
`timeout_seconds` exceeds the card's `detach_above_seconds` (default 540) is
not run in the foreground: `run` starts a detached supervisor (`setsid`, SIGHUP
ignored, stdin closed) that runs the argv under its timeout and retry, with
stdout and stderr written straight to the command's log paths (lint requires
both), and records `<run dir>/<step>.pid.json` (pid, process start ticks, boot
id, start time). The run directory is the receipt path without `.json` and
`.receipt`, plus `.run` (`cards/CARD-x.receipt.json` -> `cards/CARD-x.run/`).
`run` then writes the receipt with `status: detached` and exits 4. `wait`
polls the pid file every `--interval` seconds for at most `--max-seconds`
(exit 4 again when the window ends with the step still running: run `wait`
again); when the supervisor's exit record appears it finishes that command's
entry and runs the remaining commands, detaching again where they are long,
and writes the final receipt. `status` reports each detached step as
running, exited or lost. Lost (pid gone or reused, no exit record) is final:
`wait` writes `status: lost at command N` and both print the suggested
`tools/loss_ledger.py add` line for the infrastructure-loss ledger.

Exit status: 0 clean / completed, 1 findings, 2 the card could not be read or
`run` refused to start, 3 `run` stopped at a failing command (a result to
report, not a problem to fix), 4 a detached step is still running (run
`wait`), 5 a detached step was lost.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[1]

SCHEMA = "crypto.autoresearch.mechanical-task-card.v1"
RECEIPT_SCHEMA = "crypto.autoresearch.task-card-receipt.v1"
KINDS = ("runbook", "frozen_command")
CARD_ID = re.compile(r"^CARD-[A-Za-z0-9][A-Za-z0-9-]{2,120}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
OWNER = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
PLACEHOLDER = re.compile(r"\{([a-z_]+)\}")
SHELL_TOKENS = {"|", "||", "&&", ";", ">", ">>", "<", "&", "2>&1", "2>", "$("}
DENIED_ENV = re.compile(r"^(LD_PRELOAD|LD_LIBRARY_PATH|DYLD_.*|RISC0_DEV_MODE|"
                        r".*(TOKEN|SECRET|PASSWORD|API_KEY|CREDENTIAL).*)$")
# The same list as tools/runbook.py: words that hand a choice back to the
# operator. Kept in step by tests/test_task_card.py where both files exist.
VAGUE = re.compile(
    r"\b(appropriate(ly)?|as needed|if needed|if necessary|when necessary|"
    r"reasonabl[ey]|sensibl[ey]|judge?ment|judge|decide|choose|pick|ideally|"
    r"roughly|approximately|maybe|perhaps|might|consider|try to|feel free|"
    r"as you see fit|use your|whatever|somehow|or similar|something like|"
    r"a few|several|etc|e\.g|tbd|todo|fixme|xxx)\b|\?", re.IGNORECASE)
# Text a mechanical executor would have to fill in itself.
UNFILLED = re.compile(r"<[^<>\n]{1,60}>")
TAIL_LINES = 20
# Above this many seconds a command runs detached: below the executor
# runtime's 600 s shell cap, with a minute to spare for the tool itself.
DETACH_ABOVE_SECONDS = 540
WAIT_INTERVAL_SECONDS = 30
WAIT_MAX_SECONDS = 540
PID_SCHEMA = "crypto.autoresearch.task-card-detached-step.v1"
EXIT_RUNNING, EXIT_LOST = 4, 5
# Supervisors this process started: held so a long-lived caller (a test, `lane`) reaps
# them with poll() instead of leaving zombies; the `run` CLI exits and init reaps them.
_STARTED: list[subprocess.Popen] = []
REQUIRED = ("schema", "card_id", "experiment_id", "author_role", "executor_role",
            "kind", "bus_address", "background", "write_scope", "stop_when")


class CardError(Exception):
    """A card that cannot be read at all, or a run that cannot start."""


# ---------------------------------------------------------------------------
# Small utilities (no dependency on tools/runbook.py)
# ---------------------------------------------------------------------------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def rel(repo: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        raise CardError(f"{path} is outside the repository {repo}; cards, binds and "
                        f"outputs live inside it") from None


def safe_relative(relative: str) -> str:
    pure = PurePosixPath(relative)
    if not relative or pure.is_absolute() or ".." in pure.parts:
        raise CardError(f"{relative!r} must be a repository-relative path without '..'")
    return pure.as_posix()


def git(repo: Path, *args: str) -> tuple[int, str]:
    result = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    return result.returncode, result.stdout.strip()


def committed_bytes_match(repo: Path, relative: str) -> bool:
    code, blob = git(repo, "rev-parse", f"HEAD:{relative}")
    return code == 0 and git(repo, "hash-object", relative) == (0, blob)


def _runbook_module(repo: Path):
    """`tools/runbook.py`, needed only by `kind: runbook` cards."""
    if not (repo / "tools" / "runbook.py").is_file():
        return None
    sys.path.insert(0, str(repo / "tools"))
    import runbook  # noqa: PLC0415
    return runbook


def load_card(path: str | Path, repo: Path = REPO) -> tuple[str, str, dict[str, Any]]:
    full = Path(path)
    full = (full if full.is_absolute() else repo / full).resolve()
    try:
        raw = full.read_bytes()
    except OSError as exc:
        raise CardError(f"{path}: {exc.strerror}") from None
    try:
        doc = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise CardError(f"{path}: YAML does not parse: {exc}") from None
    if not isinstance(doc, dict):
        raise CardError(f"{path}: a task card is a mapping")
    return rel(repo, full), sha256_bytes(raw), doc


def _text(where: str, value: Any) -> list[str]:
    if not isinstance(value, str) or not value.strip():
        return [f"{where}: must be non-empty text"]
    findings = []
    hits = sorted({m.group(0) for m in VAGUE.finditer(value)})
    if hits:
        findings.append(f"{where}: leaves a choice to the operator "
                        f"({', '.join(repr(h) for h in hits)}); state exactly what happens")
    if UNFILLED.search(value):
        findings.append(f"{where}: unfilled placeholder {UNFILLED.search(value).group(0)!r}")
    return findings


def _scope_covers(scope: list[str], path: str) -> bool:
    target = PurePosixPath(path)
    for entry in scope:
        base = PurePosixPath(entry.rstrip("/"))
        if target == base or base in target.parents:
            return True
    return False


def _in_scope(at: str, scope: list[str], path: Any) -> list[str]:
    if not isinstance(path, str) or not path:
        return [f"{at}: must be a repository-relative path"]
    try:
        safe_relative(path)
    except CardError as exc:
        return [f"{at}: {exc}"]
    return [] if _scope_covers(scope, path) else [f"{at}: {path} is outside write_scope"]


# ---------------------------------------------------------------------------
# Lint
# ---------------------------------------------------------------------------

def _approval_findings(repo: Path, card: dict[str, Any]) -> list[str]:
    """A frozen-command card for an EXP-* names the decision that approved it."""
    decision = card.get("approval_decision")
    if not isinstance(decision, str):
        return ["approval_decision: an EXP-* frozen-command card names its committed approval decision"]
    path = repo / decision
    if not path.is_file() or not committed_bytes_match(repo, decision):
        return [f"approval_decision: {decision} is not a committed file"]
    record = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("coordinator_decision") or {}
    if record.get("decision") != "approve" or card["experiment_id"] not in (record.get("target_ids") or []):
        return [f"approval_decision: {decision} does not approve {card['experiment_id']}"]
    return []


def _runbook_findings(repo: Path, card: dict[str, Any], scope: list[str]) -> list[str]:
    rb = _runbook_module(repo)
    if rb is None:
        return ["kind: runbook cards need tools/runbook.py, which only "
                "crypto-autoresearcher has; use kind: frozen_command here"]
    findings: list[str] = []
    path = card.get("runbook")
    if not isinstance(path, str):
        return ["runbook: a runbook card names the runbook path"]
    if not SHA256.match(str(card.get("runbook_sha256", ""))):
        findings.append("runbook_sha256: must be the runbook's 64-hex sha256")
    try:
        runbook = rb.load_runbook(repo, path)
    except (OSError, rb.RunbookError) as exc:
        return findings + [f"runbook: {exc}"]
    if card.get("runbook_sha256") != runbook.sha256:
        findings.append(f"runbook_sha256: card names {card.get('runbook_sha256')}, "
                        f"the runbook on disk is {runbook.sha256}")
    lint = rb.lint(runbook)
    findings += [f"runbook: does not lint clean: {item}" for item in lint]
    if runbook.experiment_id != card.get("experiment_id"):
        findings.append(f"experiment_id: card names {card.get('experiment_id')}, "
                        f"the runbook is {runbook.experiment_id}")
    if runbook.doc.get("executor_tier") != "mechanical":
        findings.append("runbook: executor_tier must be `mechanical` for a mechanical card")
    for needed in (f"{runbook.base_dir}/runbook-sessions/", f"{runbook.base_dir}/reports/"):
        if not _scope_covers(scope, needed):
            findings.append(f"write_scope: must include {needed}")
    if str(card.get("experiment_id", "")).startswith("EXP-") and not lint:
        if not rb.find_approval(repo, runbook.experiment_id, runbook.sha256):
            findings.append("runbook: no committed approval decision names this experiment "
                            f"and runbook_sha256 {runbook.sha256}")
    return findings


def _command_findings(repo: Path, card: dict[str, Any], scope: list[str]) -> list[str]:
    findings: list[str] = []
    commit = card.get("commit")
    if commit is not None:
        if not COMMIT.match(str(commit)):
            findings.append("commit: must be a full 40-hex commit id")
        elif git(repo, "cat-file", "-e", f"{commit}^{{commit}}")[0] != 0:
            findings.append(f"commit: {commit} is not a commit in this repository")
    findings += _in_scope("receipt", scope, card.get("receipt"))
    fresh = card.get("must_not_exist") or []
    if not isinstance(fresh, list):
        findings.append("must_not_exist: must list repository paths")
        fresh = []
    for index, path in enumerate(fresh):
        findings += _in_scope(f"must_not_exist[{index}]", scope, path)
    binds = card.get("binds") or []
    bound: set[str] = set()
    if not isinstance(binds, list):
        findings.append("binds: must be a list of {path, sha256}")
        binds = []
    for index, item in enumerate(binds):
        at = f"binds[{index}]"
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            findings.append(f"{at}: needs path and sha256")
            continue
        file = repo / item["path"]
        if not file.is_file():
            findings.append(f"{at}: {item['path']} does not exist")
        elif sha256_file(file) != item.get("sha256"):
            findings.append(f"{at}: {item['path']} does not match its sha256")
        bound.add(item["path"])
    commands = card.get("commands")
    if not isinstance(commands, list) or not commands:
        return findings + ["commands: a frozen-command card lists at least one command"]
    threshold = card.get("detach_above_seconds", DETACH_ABOVE_SECONDS)
    if not isinstance(threshold, int) or isinstance(threshold, bool) or threshold <= 0:
        findings.append("detach_above_seconds: must be a positive integer (default "
                        f"{DETACH_ABOVE_SECONDS}, below the executor's 600 s shell cap)")
        threshold = DETACH_ABOVE_SECONDS
    detached_scope_checked = False
    for index, command in enumerate(commands):
        at = f"commands[{index}]"
        if not isinstance(command, dict):
            findings.append(f"{at}: must be a mapping")
            continue
        argv = command.get("argv")
        if not (isinstance(argv, list) and argv and all(isinstance(a, str) and a for a in argv)):
            findings.append(f"{at}.argv: must be a non-empty list of strings (no shell string)")
            continue
        shell = sorted(set(argv) & SHELL_TOKENS)
        if shell:
            findings.append(f"{at}.argv: shell syntax {shell}; the command runs without a shell")
        for token in argv:
            if UNFILLED.search(token) or PLACEHOLDER.search(token):
                findings.append(f"{at}.argv: unfilled placeholder in {token!r}")
            if (repo / token).is_file() and token not in bound:
                findings.append(f"{at}.argv: names repository file {token} that binds does not pin")
        timeout = command.get("timeout_seconds")
        if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
            findings.append(f"{at}.timeout_seconds: must be a positive integer")
        elif timeout > threshold:
            missing = [stream for stream in ("stdout", "stderr") if not command.get(stream)]
            if missing and "detach_above_seconds" in card:
                findings.append(f"{at}: timeout_seconds {timeout} exceeds detach_above_seconds {threshold}, "
                                f"so run launches it detached; it needs the log path(s) {missing}")
            # A card frozen before detached steps existed (no explicit
            # detach_above_seconds) and without log paths keeps the legacy
            # inline run, so the 2026-11-10 rule does not fail frozen cards.
            if not detached_scope_checked and isinstance(card.get("receipt"), str):
                detached_scope_checked = True
                try:
                    findings += _in_scope(f"{at}: detached run directory", scope, run_dir(card))
                except CardError:
                    pass   # the receipt finding already names the bad path
        codes = command.get("success_exit_codes")
        if not (isinstance(codes, list) and codes and all(isinstance(c, int) for c in codes)):
            findings.append(f"{at}.success_exit_codes: must list the exit codes that mean success")
        retry = command.get("retry")
        if retry is not None:
            codes_ok = (isinstance(retry, dict) and isinstance(retry.get("exit_codes"), list)
                        and retry["exit_codes"] and all(isinstance(c, int) for c in retry["exit_codes"]))
            attempts = retry.get("max_attempts") if isinstance(retry, dict) else None
            if not codes_ok or not isinstance(attempts, int) or isinstance(attempts, bool) \
                    or not 2 <= attempts <= 3:
                findings.append(f"{at}.retry: needs exit_codes (the infrastructure failures to retry) "
                                f"and max_attempts of 2 or 3")
        if command.get("id") is not None and not OWNER.match(str(command["id"])):
            findings.append(f"{at}.id: lowercase letters, digits and hyphens")
        if command.get("cwd") is not None:
            try:
                cwd = safe_relative(str(command["cwd"]))
            except CardError as exc:
                findings.append(f"{at}.cwd: {exc}")
            else:
                if not (repo / cwd).is_dir():
                    findings.append(f"{at}.cwd: {cwd} is not a directory in the repository")
        for stream in ("stdout", "stderr"):
            if command.get(stream) is not None:
                findings += _in_scope(f"{at}.{stream}", scope, command[stream])
        for output in command.get("outputs") or []:
            findings += _in_scope(f"{at}.outputs", scope, output)
        env = command.get("env") or {}
        if not isinstance(env, dict) or not all(isinstance(k, str) and isinstance(v, str)
                                                for k, v in env.items()):
            findings.append(f"{at}.env: must map names to string values")
        else:
            denied = sorted(k for k in env if DENIED_ENV.match(k))
            if denied:
                findings.append(f"{at}.env: may not set {denied}")
    if str(card.get("experiment_id", "")).startswith("EXP-"):
        findings += _approval_findings(repo, card)
    return findings


def lint(card: dict[str, Any], repo: Path = REPO) -> list[str]:
    """Every way this card could leave the mechanical executor a choice."""
    findings = [f"{key}: required" for key in REQUIRED if key not in card]
    if findings:
        return findings
    if card["schema"] != SCHEMA:
        findings.append(f"schema: must be {SCHEMA}")
    if not CARD_ID.match(str(card["card_id"])):
        findings.append("card_id: must look like CARD-<experiment>-<n>")
    if card["author_role"] != "experiment-director":
        findings.append("author_role: cards are written by experiment-director")
    if card["executor_role"] != "executor-mechanical":
        findings.append("executor_role: cards are executed by executor-mechanical")
    if card["kind"] not in KINDS:
        findings.append(f"kind: must be one of {list(KINDS)}")
    if not OWNER.match(str(card["bus_address"])):
        findings.append("bus_address: lowercase letters, digits and hyphens")
    if not isinstance(card["background"], bool):
        findings.append("background: true when the budget exceeds ten minutes, else false")
    scope = card["write_scope"]
    if not (isinstance(scope, list) and scope and all(isinstance(s, str) and s for s in scope)):
        findings.append("write_scope: must list at least one path")
        scope = []
    for entry in scope:
        try:
            safe_relative(entry.rstrip("/"))
        except CardError as exc:
            findings.append(f"write_scope: {exc}")
    stops = card["stop_when"]
    if not (isinstance(stops, list) and stops):
        findings.append("stop_when: list each condition on which the executor stops and returns `refused`")
        stops = []
    for index, text in enumerate(stops):
        findings += _text(f"stop_when[{index}]", text)
    if card.get("notes") is not None:
        findings += _text("notes", card["notes"])
    if card["kind"] == "runbook":
        findings += _runbook_findings(repo, card, scope)
    elif card["kind"] == "frozen_command":
        findings += _command_findings(repo, card, scope)
    return findings


# ---------------------------------------------------------------------------
# Prompt: the exact dispatch text
# ---------------------------------------------------------------------------

def render_prompt(card_path: str, card_sha: str, card: dict[str, Any], repo: Path = REPO) -> str:
    """Deterministic: same card, same bytes."""
    lines = [
        f"You are executor-mechanical. This is task card {card['card_id']} "
        f"({card_path}, sha256 {card_sha}); tools/task_card.py lint accepted it.",
        "Every value you need is below. Use no other value, run nothing else, and "
        "compute nothing: every number you report is copied from tool output.",
        "",
    ]
    if card["kind"] == "runbook":
        runbook = _runbook_module(repo).load_runbook(repo, card["runbook"])
        lines += [
            'Follow ".claude/agents/executor-mechanical.md", section "Runbook '
            'execution: the procedure", steps 1 to 8, with exactly these values:',
            f"  <runbook> = {card['runbook']}",
            f"  <your bus address> = {card['bus_address']}",
            f"  <session_dir> = {runbook.session_dir}",
            f"  <session id> = {runbook.doc['session_id']}",
            f"  step 2 in the background: {'yes' if card['background'] else 'no'}",
        ]
    else:
        lines += [
            "Run exactly this one command from the repository root, and nothing else:",
            f"  python3 tools/task_card.py run {card_path}",
            f"Run it in the background: {'yes' if card['background'] else 'no'}. "
            "The tool checks the card, runs every command on it and writes the receipt; "
            "you run none of the card's commands yourself.",
            "Exit 0: completed. Exit 3: stopped at a failing command, which is a result "
            "to report. Exit 2: refused to start; return `refused` with the IMPEDIMENT line.",
        ]
        if any(isinstance(c, dict) and isinstance(c.get("timeout_seconds"), int) and _detaches(card, c)
               for c in card.get("commands") or []):
            lines += [
                "A command on this card runs detached. Exit 4: it is still running; then run exactly "
                f"`python3 tools/task_card.py wait {card_path}` and run it again each time it exits 4. "
                "Exit 5: a detached command was lost; report the output, including its "
                "`record the loss:` line, and run nothing else.",
            ]
    lines += ["", "Write only inside:"] + [f"  - {entry}" for entry in card["write_scope"]]
    lines += ["", "Stop and return `refused`, naming the condition, when:"]
    lines += [f"  - {text}" for text in card["stop_when"]]
    if card.get("notes"):
        lines += ["", f"Note from the director: {card['notes']}"]
    if card["kind"] == "runbook":
        lines += ["", "Return the output of step 7 (`status --brief`) verbatim, and nothing you "
                  "composed yourself."]
    else:
        lines += ["", "Return everything the command printed, verbatim, and nothing you "
                  "composed yourself."]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Run: a frozen-command card, executed and recorded by the tool
# ---------------------------------------------------------------------------

def _tail(data: bytes) -> list[str]:
    return data.decode("utf-8", errors="replace").splitlines()[-TAIL_LINES:]


def _write(repo: Path, relative: str, data: bytes) -> None:
    path = repo / safe_relative(relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _execute(repo: Path, command: dict[str, Any], env: dict[str, str]):
    started = time.monotonic()
    try:
        proc = subprocess.run(command["argv"], cwd=repo / safe_relative(str(command.get("cwd") or ".")),
                              env=env, capture_output=True, timeout=command["timeout_seconds"])
        result = proc.returncode, proc.stdout, proc.stderr, False
    except subprocess.TimeoutExpired as exc:
        result = None, exc.stdout or b"", exc.stderr or b"", True
    except OSError as exc:
        result = None, b"", str(exc).encode(), False
    return (*result, round(time.monotonic() - started, 3))


def _result_entry(repo: Path, index: int, command: dict[str, Any], code, out: bytes, err: bytes,
                  timed_out: bool, elapsed: float, attempts: list[dict[str, Any]]) -> dict[str, Any]:
    outputs = {path: (sha256_file(repo / path) if (repo / path).is_file() else None)
               for path in command.get("outputs") or []}
    # A declared output the command did not write is a failure: the card
    # said the command writes it.
    ok = (not timed_out) and code in command["success_exit_codes"] and None not in outputs.values()
    return {"index": index, "id": command.get("id"), "cwd": command.get("cwd") or ".",
            "argv": command["argv"], "exit_code": code, "attempts": len(attempts),
            "attempt_log": attempts,
            "timed_out": timed_out, "seconds": elapsed, "succeeded": ok,
            "stdout_sha256": sha256_bytes(out), "stderr_sha256": sha256_bytes(err),
            "stdout_tail": _tail(out), "stderr_tail": _tail(err), "outputs": outputs}


def _run_inline(repo: Path, index: int, command: dict[str, Any]) -> dict[str, Any]:
    env = dict(os.environ, **(command.get("env") or {}))
    retry = command.get("retry") or {}
    attempts = []
    for _attempt in range(retry.get("max_attempts", 1)):
        code, out, err, timed_out, elapsed = _execute(repo, command, env)
        attempts.append({"exit_code": code, "timed_out": timed_out, "seconds": elapsed})
        if timed_out or code not in (retry.get("exit_codes") or []):
            break
    for stream, data in (("stdout", out), ("stderr", err)):
        if command.get(stream):
            _write(repo, command[stream], data)
    return _result_entry(repo, index, command, code, out, err, timed_out, elapsed, attempts)


# -- detached steps ---------------------------------------------------------

def detach_threshold(card: dict[str, Any]) -> int:
    value = card.get("detach_above_seconds", DETACH_ABOVE_SECONDS)
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else DETACH_ABOVE_SECONDS


def _detaches(card: dict[str, Any], command: dict[str, Any]) -> bool:
    """Long steps detach; a legacy card without log paths stays inline."""
    if command["timeout_seconds"] <= detach_threshold(card):
        return False
    has_logs = all(command.get(stream) for stream in ("stdout", "stderr"))
    return has_logs or "detach_above_seconds" in card


def run_dir(card: dict[str, Any]) -> str:
    """`<receipt without .json and .receipt>.run`: cards/CARD-x.receipt.json -> cards/CARD-x.run."""
    stem = safe_relative(str(card["receipt"]))
    for suffix in (".json", ".receipt"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
    return stem + ".run"


def _step(index: int, command: dict[str, Any]) -> str:
    return f"{index:02d}-{command.get('id') or 'command'}"


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _boot_id() -> str | None:
    try:
        return Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    except OSError:
        return None


def _proc_start_ticks(pid: int) -> int | None:
    """Field 22 of /proc/<pid>/stat: the process start time, which tells a reused pid apart."""
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return None
    fields = stat[stat.rindex(")") + 2:].split()
    return None if fields[0] == "Z" else int(fields[19])


def _alive(pid: int, ticks: int | None, boot: str | None) -> bool:
    if boot and _boot_id() and boot != _boot_id():
        return False
    if Path("/proc").is_dir() and Path(f"/proc/{os.getpid()}/stat").is_file():
        now = _proc_start_ticks(pid)
        return now is not None and (ticks is None or now == ticks)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _atomic_json(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _launch_detached(repo: Path, card: dict[str, Any], index: int, command: dict[str, Any]) -> dict[str, Any]:
    """Start the supervisor in its own session and return the receipt's `detached` entry."""
    directory = run_dir(card)
    step = _step(index, command)
    spec_rel, pid_rel, exit_rel = (f"{directory}/{step}.{kind}.json" for kind in ("spec", "pid", "exit"))
    for relative in (pid_rel, exit_rel):
        if (repo / relative).exists():
            raise CardError(f"{relative} already exists; a detached step starts once")
    spec = {"argv": command["argv"], "cwd": command.get("cwd") or ".",
            "timeout_seconds": command["timeout_seconds"], "retry": command.get("retry") or {},
            "stdout": command["stdout"], "stderr": command["stderr"], "exit_file": exit_rel}
    _atomic_json(repo / spec_rel, spec)
    env = dict(os.environ, **(command.get("env") or {}))
    log = open(repo / f"{directory}/{step}.supervisor.log", "ab")  # noqa: SIM115
    try:
        proc = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "_supervise",
                                 "--repo", str(repo), spec_rel],
                                cwd=repo, env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                start_new_session=True, close_fds=True)
    finally:
        log.close()
    _STARTED.append(proc)
    record = {"schema": PID_SCHEMA, "card_id": card["card_id"], "index": index, "id": command.get("id"),
              "step": step, "argv": command["argv"], "pid": proc.pid,
              "pid_start_ticks": _proc_start_ticks(proc.pid), "boot_id": _boot_id(),
              "started_at": _now(), "started_epoch": round(time.time(), 3),
              "timeout_seconds": command["timeout_seconds"], "stdout": command["stdout"],
              "stderr": command["stderr"], "exit_file": exit_rel, "spec_file": spec_rel}
    _atomic_json(repo / pid_rel, record)
    return {"index": index, "id": command.get("id"), "cwd": command.get("cwd") or ".",
            "argv": command["argv"], "status": "detached", "pid_file": pid_rel, "pid": proc.pid,
            "started_at": record["started_at"], "stdout": command["stdout"], "stderr": command["stderr"]}


def _supervise(repo: Path, spec_rel: str) -> int:
    """The detached supervisor: run the argv under its timeout and retry, logs to files, then
    write the exit record (atomically, last). Its absence after the pid is gone is a loss."""
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    spec = json.loads((repo / spec_rel).read_text(encoding="utf-8"))
    retry, attempts = spec["retry"], []
    started = time.monotonic()
    for attempt in range(retry.get("max_attempts", 1)):
        t0 = time.monotonic()
        code, timed_out = None, False
        paths = [repo / safe_relative(spec[s]) for s in ("stdout", "stderr")]
        for path in paths:
            path.parent.mkdir(parents=True, exist_ok=True)
        with open(paths[0], "wb") as out, open(paths[1], "wb") as err:
            try:
                child = subprocess.Popen(spec["argv"], cwd=repo / safe_relative(spec["cwd"]),
                                         stdin=subprocess.DEVNULL, stdout=out, stderr=err)
            except OSError as exc:
                err.write(str(exc).encode())
            else:
                _atomic_json(repo / spec_rel.replace(".spec.json", ".child.json"),
                             {"child_pid": child.pid, "attempt": attempt + 1, "started_at": _now()})
                try:
                    code = child.wait(timeout=spec["timeout_seconds"])
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
                    timed_out = True
        attempts.append({"exit_code": code, "timed_out": timed_out, "seconds": round(time.monotonic() - t0, 3)})
        if timed_out or code not in (retry.get("exit_codes") or []):
            break
    _atomic_json(repo / spec["exit_file"], {"exit_code": code, "timed_out": timed_out,
                                            "seconds": round(time.monotonic() - started, 3),
                                            "attempt_log": attempts, "finished_at": _now()})
    return 0


def step_state(repo: Path, pid_rel: str) -> dict[str, Any]:
    """running | exited | lost, for one detached step, from its pid file and exit record."""
    for proc in _STARTED:
        proc.poll()
    record = json.loads((repo / pid_rel).read_text(encoding="utf-8"))
    exit_path = repo / record["exit_file"]
    state: dict[str, Any] = {"step": record["step"], "index": record["index"], "pid": record["pid"],
                             "pid_file": pid_rel, "started_at": record["started_at"],
                             "elapsed_seconds": round(time.time() - record["started_epoch"], 1)}
    if not exit_path.is_file() and _alive(record["pid"], record.get("pid_start_ticks"), record.get("boot_id")):
        return {**state, "state": "running"}
    if exit_path.is_file():   # read again: the supervisor writes the record before it exits
        return {**state, "state": "exited", "exit": json.loads(exit_path.read_text(encoding="utf-8"))}
    child = repo / record["spec_file"].replace(".spec.json", ".child.json")
    if child.is_file():
        state["child_pid"] = json.loads(child.read_text(encoding="utf-8"))["child_pid"]
        state["child_alive"] = _alive(state["child_pid"], None, record.get("boot_id"))
    return {**state, "state": "lost"}


def loss_ledger_line(card: dict[str, Any], receipt_rel: str, state: dict[str, Any]) -> str:
    """The suggested ledger row for a lost step; printed, never run (the ledger tool is separate)."""
    slug = re.sub(r"[^a-z0-9-]+", "-", f"{card['card_id']}-{state['step']}".lower()).strip("-")
    what = (f"task card {card['card_id']} step {state['step']} lost: pid {state['pid']} gone "
            f"without an exit record, started {state['started_at']}")
    return ("python3 tools/loss_ledger.py add " + " ".join(shlex.quote(a) for a in (
        "--slug", slug, "--route", "local", "--cause", "container_restart", "--what", what,
        "--source", receipt_rel)))


def _write_receipt(repo: Path, card: dict[str, Any], receipt: dict[str, Any]) -> None:
    _atomic_json(repo / safe_relative(card["receipt"]), receipt)


def _advance(repo: Path, card: dict[str, Any], receipt: dict[str, Any], start: int) -> dict[str, Any]:
    """Run commands from `start` (1-based) until one detaches, one fails, or all are done."""
    status = "completed"
    for index in range(start, len(card["commands"]) + 1):
        command = card["commands"][index - 1]
        if _detaches(card, command):
            entry = _launch_detached(repo, card, index, command)
            receipt["commands"].append(entry)
            receipt.update(status="detached", detached=entry["pid_file"])
            _write_receipt(repo, card, receipt)
            return receipt
        entry = _run_inline(repo, index, command)
        receipt["commands"].append(entry)
        if not entry["succeeded"]:
            status = f"stopped at command {index}"
            break
    receipt.pop("detached", None)
    receipt.update(status=status, dirty_after=_dirty_paths(repo))
    _write_receipt(repo, card, receipt)
    return receipt


def run_card(card_path: str, card_sha: str, card: dict[str, Any], repo: Path = REPO) -> dict[str, Any]:
    """Execute a linted frozen-command card and write its write-once receipt.

    Raises CardError (an impediment: nothing ran, nothing was written) when
    the card is not a frozen-command card, does not lint, names a commit that
    is not HEAD, already has a receipt, or names a `must_not_exist` path that
    exists. A command succeeds only with a success exit code and every
    declared output written; `retry` reruns it, up to its `max_attempts`,
    only on the exit codes it names. A command longer than
    `detach_above_seconds` is started detached and the receipt says
    `status: detached` until `wait` finishes it (the only rewrite a receipt gets).
    """
    if card.get("kind") != "frozen_command":
        raise CardError("run executes frozen_command cards; a runbook card runs through tools/runbook.py")
    findings = lint(card, repo)
    if findings:
        raise CardError("card does not lint: " + "; ".join(findings))
    receipt_path = repo / safe_relative(card["receipt"])
    if receipt_path.exists():
        raise CardError(f"receipt {card['receipt']} already exists; receipts are write-once")
    present = [path for path in card.get("must_not_exist") or [] if (repo / path).exists()]
    if present:
        raise CardError(f"must_not_exist paths already exist: {present}")
    head = git(repo, "rev-parse", "HEAD")[1]
    if card.get("commit") and card["commit"] != head:
        raise CardError(f"card pins commit {card['commit']}, HEAD is {head}")
    if any(_detaches(card, c) for c in card["commands"]) and (repo / run_dir(card)).exists():
        raise CardError(f"{run_dir(card)} already exists; a card's detached steps start once")
    receipt = {"schema": RECEIPT_SCHEMA, "card_id": card["card_id"], "card_path": card_path,
               "card_sha256": card_sha, "commit": head, "status": "running",
               "dirty_before": _dirty_paths(repo), "commands_total": len(card["commands"]), "commands": []}
    return _advance(repo, card, receipt, 1)


def _finish_detached(repo: Path, card: dict[str, Any], entry: dict[str, Any], exit_record: dict[str, Any]):
    index = entry["index"]
    command = card["commands"][index - 1]
    out, err = ((repo / command[s]).read_bytes() if (repo / command[s]).is_file() else b""
                for s in ("stdout", "stderr"))
    done = _result_entry(repo, index, command, exit_record["exit_code"], out, err, exit_record["timed_out"],
                         exit_record["seconds"], exit_record["attempt_log"])
    done.update(detached=True, pid_file=entry["pid_file"])
    return done


def wait_card(card: dict[str, Any], repo: Path = REPO, interval: float = WAIT_INTERVAL_SECONDS,
              max_seconds: float = WAIT_MAX_SECONDS, say=print) -> dict[str, Any]:
    """Poll a detached receipt's pid file until the step exits (finish it and run the rest),
    is lost (final receipt `lost at command N`), or the window closes (receipt unchanged).
    `max_seconds` 0 waits without a window."""
    receipt_path = repo / safe_relative(str(card.get("receipt") or ""))
    if not receipt_path.is_file():
        raise CardError(f"no receipt {card.get('receipt')}: run the card first")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("card_id") != card["card_id"]:
        raise CardError("receipt belongs to another card")
    began = time.monotonic()
    say(f"WAIT polling every {interval:g} s"
        + (f" for at most {max_seconds:g} s" if max_seconds else " without a window"))
    while receipt["status"] == "detached":
        entry = receipt["commands"][-1]
        state = step_state(repo, entry["pid_file"])
        if state["state"] == "running":
            if max_seconds and time.monotonic() - began + interval > max_seconds:
                say(f"WAIT window closed: step {state['step']} still running (pid {state['pid']}, "
                    f"{state['elapsed_seconds']} s since start)")
                return receipt
            time.sleep(interval)
            continue
        if state["state"] == "lost":
            entry.update(status="lost", lost_detected_at=_now(),
                         child_pid=state.get("child_pid"), child_alive=state.get("child_alive"))
            receipt.pop("detached", None)
            receipt.update(status=f"lost at command {entry['index']}", dirty_after=_dirty_paths(repo),
                           loss_ledger_suggestion=loss_ledger_line(card, card["receipt"], state))
            _write_receipt(repo, card, receipt)
            return receipt
        receipt["commands"][-1] = _finish_detached(repo, card, entry, state["exit"])
        if receipt["commands"][-1]["succeeded"]:
            receipt = _advance(repo, card, receipt, entry["index"] + 1)
        else:
            receipt.pop("detached", None)
            receipt.update(status=f"stopped at command {entry['index']}", dirty_after=_dirty_paths(repo))
            _write_receipt(repo, card, receipt)
    return receipt


def status_card(card: dict[str, Any], repo: Path = REPO) -> tuple[int, list[str]]:
    """Every detached step of the card, running / exited / lost; never writes."""
    directory = repo / run_dir(card)
    pid_files = sorted(directory.glob("*.pid.json")) if directory.is_dir() else []
    if not pid_files:
        return 0, [f"status: no detached step under {run_dir(card)}"]
    lines, code = [], 0
    for path in pid_files:
        state = step_state(repo, rel(repo, path))
        head = f"step {state['step']}: {state['state']} (pid {state['pid']}, started {state['started_at']}"
        if state["state"] == "running":
            lines.append(head + f", {state['elapsed_seconds']} s ago)")
            code = max(code, EXIT_RUNNING)
        elif state["state"] == "exited":
            ex = state["exit"]
            lines.append(head + f"; {'timed out' if ex['timed_out'] else 'exit ' + str(ex['exit_code'])} "
                         f"after {ex['seconds']} s at {ex['finished_at']})")
        else:
            child = (f"; child pid {state['child_pid']} {'still alive' if state['child_alive'] else 'gone'}"
                     if "child_pid" in state else "")
            lines.append(head + f"; pid gone, no exit record{child})")
            lines.append("  record the loss: " + loss_ledger_line(card, card["receipt"], state))
            code = EXIT_LOST
    return code, lines


def brief(receipt: dict[str, Any], receipt_rel: str, receipt_sha: str) -> str:
    """What `run` prints, derived from the receipt alone, so it can be re-derived."""
    lines = [f"card: {receipt['card_id']} (sha256 {receipt['card_sha256']})",
             f"commit: {receipt['commit']}",
             f"receipt: {receipt_rel} sha256 {receipt_sha}",
             f"status: {receipt['status']}"]
    for item in receipt["commands"]:
        label = f"{item['index']}" + (f" ({item['id']})" if item.get("id") else "")
        where = f" in {item['cwd']}" if item.get("cwd", ".") != "." else ""
        if item.get("status") in ("detached", "lost"):
            lines.append(f"command {label}: {json.dumps(item['argv'])}{where} "
                         f"{'DETACHED' if item['status'] == 'detached' else 'LOST'} "
                         f"(pid {item['pid']}, started {item['started_at']}, pid file {item['pid_file']})")
            lines.append(f"  logs: {item['stdout']} {item['stderr']}")
            continue
        exit_text = "timed out" if item["timed_out"] else f"exit {item['exit_code']}"
        if item.get("detached"):
            exit_text = "detached, " + exit_text
        if item.get("attempts", 1) > 1:
            exit_text += f" after {item['attempts']} attempts"
        lines.append(f"command {label}: {json.dumps(item['argv'])}{where} {exit_text} "
                     f"({item['seconds']} s) {'succeeded' if item['succeeded'] else 'FAILED'}")
        lines.append(f"  stdout sha256 {item['stdout_sha256']}; last {len(item['stdout_tail'])} lines:")
        lines += [f"    {line}" for line in item["stdout_tail"]]
        if item["stderr_tail"]:
            lines.append(f"  stderr last {len(item['stderr_tail'])} lines:")
            lines += [f"    {line}" for line in item["stderr_tail"]]
        for path, digest in item["outputs"].items():
            lines.append(f"  output {path}: {digest or 'MISSING'}")
    not_run = receipt["commands_total"] - len(receipt["commands"])
    if receipt["status"] == "detached":
        lines.append(f"pending: {not_run} command(s) after the detached one")
        lines.append(f"next: python3 tools/task_card.py wait {receipt['card_path']}")
    elif not_run:
        lines.append(f"not run: {not_run} command(s) after the stop")
    if receipt.get("loss_ledger_suggestion"):
        lines.append(f"record the loss: {receipt['loss_ledger_suggestion']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Check-relay
# ---------------------------------------------------------------------------

def _normalized(text: str) -> list[str]:
    return [" ".join(line.split()) for line in text.splitlines() if line.strip()]


def _missing(expected: list[str], reported: list[str]) -> list[str]:
    position, missing = 0, []
    for line in expected:
        try:
            position = reported.index(line, position) + 1
        except ValueError:
            missing.append(line)
    return missing


def check_relay(card: dict[str, Any], report_text: str, repo: Path = REPO) -> dict[str, Any]:
    """Whether the executor's report carries the tool's own output, unedited.

    The reference is recomputed from the record, never taken from the
    executor: `tools/runbook.py status --brief` of the session for a runbook
    card, `brief` of the receipt for a frozen-command card. Every reference
    line must appear, in order, in the report; a paraphrased, rounded or
    reordered report is not a relay, whatever it says.
    """
    reported = _normalized(report_text)
    if card["kind"] == "frozen_command":
        receipt_rel = card["receipt"]
        path = repo / safe_relative(receipt_rel)
        result: dict[str, Any] = {"applicable": True, "receipt": receipt_rel}
        if not path.is_file():
            result.update(relay_verbatim=False, missing_lines=[], verify_findings=["no receipt: the card never ran"])
            return result
        receipt = json.loads(path.read_text(encoding="utf-8"))
        missing = _missing(_normalized(brief(receipt, receipt_rel, sha256_file(path))), reported)
        findings = [] if receipt.get("card_id") == card["card_id"] else ["receipt belongs to another card"]
        result.update(relay_verbatim=not missing, missing_lines=missing, verify_findings=findings,
                      status=receipt.get("status"))
        return result
    rb = _runbook_module(repo)
    runbook = rb.load_runbook(repo, card["runbook"])
    session = runbook.session_dir
    result = {"applicable": True, "session_dir": session}
    try:
        expected = _normalized(rb.brief(repo, session))
    except (OSError, rb.RunbookError, IndexError, KeyError, ValueError) as exc:
        result.update(relay_verbatim=False, verify_findings=[f"session unreadable: {exc}"], missing_lines=[])
        return result
    missing = _missing(expected, reported)
    result["relay_verbatim"] = not missing
    result["missing_lines"] = missing
    result["verify_findings"] = rb.verify(repo, session)
    return result


# ---------------------------------------------------------------------------
# Batch lane: self-contained director requests, mechanically ingested replies
# ---------------------------------------------------------------------------
#
# A batch request (Delphi through Conductor, or `orchestration.adapter batch`
# in crypto-autoresearcher) is one turn: the model reads no file and runs no
# command. So `request` puts every fact in the prompt, computed by this tool
# (HEAD, every sha256, the receipt, what changed on disk), and `ingest` accepts
# a reply only when it is mechanically right: the card lints, the assessment's
# outcome is the one the facts determine. The mechanical tier needs no model
# here at all: `run` executes the card.

YAML_BLOCK = re.compile(r"```ya?ml[ \t]*\n(.*?)\n```", re.DOTALL)
OUTCOMES = ("executed_as_specified", "stopped", "impeded", "executor_deviated")
RECOMMENDATIONS = ("proceed_to_analysis", "rerun_after_infrastructure_fix", "respecify", "escalate")
ALLOWED = {"executed_as_specified": ("proceed_to_analysis",),
           "executor_deviated": ("escalate",),
           "stopped": ("rerun_after_infrastructure_fix", "respecify", "escalate"),
           "impeded": ("rerun_after_infrastructure_fix", "respecify", "escalate")}


def _dirty_paths(repo: Path) -> list[str]:
    code, out = git(repo, "status", "--porcelain", "--untracked-files=all")
    if code != 0:
        return []
    return sorted(line[3:].split(" -> ")[-1].strip('"') for line in out.splitlines() if line)


def _contract(repo: Path) -> str:
    """The director's full contract: `agents/` in crypto-autoresearcher, where the
    `.claude/agents/` file is a generated pointer to it; `.claude/agents/` elsewhere."""
    for path in (repo / "agents" / "experiment-director.md",
                 repo / ".claude" / "agents" / "experiment-director.md"):
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            break
    else:
        raise CardError("no experiment-director contract in this repository")
    if text.startswith("---"):
        text = text.split("---", 2)[2]
    return text.strip()


def _fenced(label: str, text: str, lang: str = "") -> list[str]:
    return [f"### {label}", "", f"````{lang}", text.rstrip("\n"), "````", ""]


def compile_request(designs: list[str], binds: list[str], card_out: str, repo: Path = REPO) -> str:
    """The prompt for a director compile in one turn, deterministic in the repository state."""
    card_out = safe_relative(card_out)
    head = git(repo, "rev-parse", "HEAD")[1]
    facts = [f"repository HEAD: {head}", f"card path: {card_out}"]
    for relative in binds:
        relative = safe_relative(relative)
        file = repo / relative
        facts.append(f"bind {relative}: " + (f"sha256 {sha256_file(file)}" if file.is_file() else "DOES NOT EXIST"))
    lines = [
        "You are experiment-director in compile mode, answering in a single turn through a batch API.",
        "You cannot read files or run commands. Every fact you may use is in this message; the facts "
        "under 'Computed facts' were computed by tools/task_card.py and are copied, never recomputed. "
        "A value the design does not give is a specification error, never a default.",
        "",
        "Write a `kind: frozen_command` card. Reply with exactly two fenced yaml blocks and nothing "
        "else: first the card, then `specification_errors: [...]` (an empty list only when every value "
        "came from the design or the facts). `tools/task_card.py ingest` writes the card only when it "
        "lints clean and the error list is empty.",
        "",
    ]
    lines += _fenced("Your role contract (this repository's experiment-director)", _contract(repo), "markdown")
    template = repo / "templates" / "mechanical-task-card.yaml"
    if template.is_file():
        lines += _fenced("Card template", template.read_text(encoding="utf-8"), "yaml")
    lines += _fenced("Computed facts", "\n".join(facts))
    for relative in designs:
        relative = safe_relative(relative)
        file = repo / relative
        try:
            data = file.read_bytes()
        except OSError:
            raise CardError(f"design {relative} cannot be read") from None
        lines += _fenced(f"Decided design: {relative} (sha256 {sha256_bytes(data)})",
                         data.decode("utf-8", errors="replace"))
    return "\n".join(lines)


def assessment_facts(card: dict[str, Any], report_text: str | None = None, repo: Path = REPO) -> dict[str, Any]:
    """Everything an assessment rests on, and the outcome those facts determine."""
    facts: dict[str, Any] = {"card_id": card["card_id"], "receipt": card.get("receipt")}
    path = repo / safe_relative(str(card.get("receipt") or ""))
    if card.get("kind") != "frozen_command" or not path.is_file():
        facts.update(receipt_present=False, outcome="impeded")
        return facts
    receipt = json.loads(path.read_text(encoding="utf-8"))
    mismatched = []
    for item in receipt.get("commands", []):
        for output, digest in (item.get("outputs") or {}).items():
            now = sha256_file(repo / output) if (repo / output).is_file() else None
            if digest is not None and now != digest:
                mismatched.append(output)
    scope = card["write_scope"]
    # What the run changed is read from the receipt (dirty right after the run, not before
    # it), so the director's own later files -- prompts, replies, this assessment -- are
    # never mistaken for executor writes.
    before = set(receipt.get("dirty_before") or [])
    after = receipt.get("dirty_after")
    outside = [p for p in (after if after is not None else _dirty_paths(repo))
               if p not in before and not _scope_covers(scope, p)]
    facts.update(receipt_present=True, receipt_sha256=sha256_file(path), status=receipt["status"],
                 summary=brief(receipt, card["receipt"], sha256_file(path)),
                 outputs_changed_since_run=mismatched, writes_outside_scope=outside)
    deviated = bool(mismatched or outside)
    if report_text is not None:
        relay = check_relay(card, report_text, repo)
        facts["relay_verbatim"] = relay["relay_verbatim"]
        deviated = deviated or not relay["relay_verbatim"]
    else:
        facts["relay"] = "none: tools/task_card.py run was invoked directly, no executor relayed"
    if deviated:
        facts["outcome"] = "executor_deviated"
    else:
        facts["outcome"] = "executed_as_specified" if receipt["status"] == "completed" else "stopped"
    return facts


def assess_request(card_path: str, card_sha: str, card: dict[str, Any], report_text: str | None = None,
                   repo: Path = REPO) -> str:
    facts = assessment_facts(card, report_text, repo)
    allowed = ALLOWED[facts["outcome"]]
    summary = facts.pop("summary", None)
    lines = [
        "You are experiment-director in assess mode, answering in a single turn through a batch API.",
        "You cannot read files or run commands. The facts below were computed by tools/task_card.py "
        f"from the receipt and the checkout. They determine the outcome: `{facts['outcome']}`. Your "
        f"part is the recommendation, one of {list(allowed)}, and one reason per line citing the fact "
        "or summary line it rests on. Never interpret the result.",
        "",
        "Reply with exactly one fenced yaml block and nothing else:",
        "",
        "```yaml",
        "execution_assessment:",
        f"  card_id: {card['card_id']}",
        f"  card_sha256: {card_sha}",
        f"  outcome: {facts['outcome']}",
        f"  recommendation: <one of {' | '.join(allowed)}>",
        "  reasons: [<one line each>]",
        "  interpretation: not_assessed",
        "```",
        "",
    ]
    lines += _fenced("Your role contract (this repository's experiment-director)", _contract(repo), "markdown")
    lines += _fenced(f"Card {card_path} (sha256 {card_sha})", yaml.safe_dump(card, sort_keys=False), "yaml")
    lines += _fenced("Computed facts", yaml.safe_dump(facts, sort_keys=True), "yaml")
    if summary:
        lines += _fenced("Run summary (tools/task_card.py, derived from the receipt)", summary)
    return "\n".join(lines)


def _blocks(text: str) -> list[Any]:
    out = []
    for body in YAML_BLOCK.findall(text):
        try:
            out.append(yaml.safe_load(body))
        except yaml.YAMLError:
            out.append(None)
    return out


def ingest(reply: str, out: str, expect: str, card: dict[str, Any] | None = None,
           repo: Path = REPO) -> list[str]:
    """Validate a model's reply and write it write-once; findings mean nothing was written."""
    out = safe_relative(out)
    target = repo / out
    if target.exists():
        return [f"{out} already exists; cards and assessments are write-once"]
    blocks = [b for b in _blocks(reply) if isinstance(b, dict)]
    if expect == "card":
        cards = [b for b in blocks if "schema" in b]
        errors = [b for b in blocks if "specification_errors" in b]
        if len(cards) != 1:
            return [f"reply must hold exactly one card block, found {len(cards)}"]
        if not errors:
            return ["reply has no specification_errors block"]
        listed = errors[0]["specification_errors"] or []
        if listed:
            return [f"specification_error: {item}" for item in listed]
        findings = lint(cards[0], repo)
        if findings:
            return findings
        document = cards[0]
    else:
        assessments = [b["execution_assessment"] for b in blocks
                       if isinstance(b.get("execution_assessment"), dict)]
        if len(assessments) != 1:
            return [f"reply must hold exactly one execution_assessment block, found {len(assessments)}"]
        record = assessments[0]
        facts = assessment_facts(card, None, repo)
        findings = []
        if record.get("card_id") != card["card_id"]:
            findings.append(f"card_id: {record.get('card_id')} is not {card['card_id']}")
        if record.get("outcome") != facts["outcome"]:
            findings.append(f"outcome: {record.get('outcome')}; the facts determine {facts['outcome']}")
        if record.get("recommendation") not in ALLOWED[facts["outcome"]]:
            findings.append(f"recommendation: {record.get('recommendation')} is not one of "
                            f"{list(ALLOWED[facts['outcome']])} for {facts['outcome']}")
        if record.get("interpretation") != "not_assessed":
            findings.append("interpretation: must be not_assessed")
        reasons = record.get("reasons")
        if not (isinstance(reasons, list) and reasons and all(isinstance(r, str) and r for r in reasons)):
            findings.append("reasons: list at least one reason")
        if findings:
            return findings
        record["facts"] = {k: v for k, v in facts.items() if k != "summary"}
        document = {"execution_assessment": record}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return []


# ---------------------------------------------------------------------------
# Lane: compile -> run -> assess end to end through one batch backend
# ---------------------------------------------------------------------------
#
# The two director calls go to a batch API; everything else is this tool.
# `conductor` is Conductor-hosted Delphi (`conductor delphi ask --profile
# director`, the key in the project vault, the delegation linked to a task);
# `delphi` is the standalone binary (`delphi run`, the key in the environment).
# Neither ever sees a file: each call is the prompt `request` printed.

DIRECTOR_MODEL = "claude-sonnet-5-5"   # director-runbook's anthropic binding
DIRECTOR_PROFILE = "director"          # Conductor's delphi director profile


def _conductor_connected(binary: str) -> bool:
    if not shutil.which(binary):
        return False
    try:
        probe = subprocess.run([binary, "delphi", "profiles"], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return probe.returncode == 0 and DIRECTOR_PROFILE in probe.stdout


def pick_backend(via: str, conductor: str, delphi: str) -> str:
    if via != "auto":
        return via
    if _conductor_connected(conductor):
        return "conductor"
    if shutil.which(delphi) and os.environ.get("ANTHROPIC_API_KEY"):
        return "delphi"
    raise CardError("no batch backend: `conductor delphi profiles` does not list a director profile "
                    "(connect Conductor to a control plane whose vault holds the key), and standalone "
                    "delphi needs ANTHROPIC_API_KEY")


# The task family of each director step, as Delphi's calibration suites name it.
FAMILY = {"compile": "card-compile", "assess": "assess"}


class _Refused(CardError):
    """The model declined to answer (delphi status refused): worth escalating, unlike an
    infrastructure error, which a stronger model would not fix."""


def _target(spec: str) -> dict[str, str]:
    provider, _, rest = spec.partition(":")
    model, effort = rest, ""
    if "@" in rest[1:]:
        model, effort = rest[:rest.rindex("@")], rest[rest.rindex("@") + 1:]
    return {"provider": provider, "model": model, "effort": effort}


FREE_MODES = ("local", "public")


def _delphi_env(opts: dict[str, Any]) -> dict[str, str] | None:
    """The environment for standalone delphi: free mode is DELPHI_FREE, set from opts so the
    lane's record says what actually ran (lane takes an inherited DELPHI_FREE as its default)."""
    env = dict(os.environ)
    env.pop("DELPHI_FREE", None)
    if opts.get("free"):
        env["DELPHI_FREE"] = opts["free"]
    return env


def route_for(family: str, opts: dict[str, Any]) -> dict[str, Any]:
    """`delphi route -family F -json`: the chosen model, its escalation chain and the basis."""
    proc = subprocess.run([opts["delphi"], "route", "-family", family, "-json"], capture_output=True, text=True,
                          env=_delphi_env(opts))
    try:
        data = json.loads(proc.stdout)
    except ValueError:
        raise CardError(f"delphi route -family {family} failed ({proc.returncode}): "
                        f"{proc.stderr.strip()[-400:]}") from None
    if data.get("error"):
        raise CardError(f"no routed model for {family}: {data['error']}")
    r = data["route"]
    return {"family": family, "choice": r["choice"], "escalation": r.get("escalation") or [], "basis": r["basis"]}


def _ask(backend: str, prompt: Path, workdir: Path, name: str, opts: dict[str, Any]) -> tuple[str, dict]:
    """One batch call; returns the answer text and what the backend reported."""
    if backend == "conductor":
        argv = [opts["conductor"], "delphi", "ask", "--profile", DIRECTOR_PROFILE, "--wait",
                "--file", str(prompt)] + (["--task", opts["task"]] if opts.get("task") else [])
        proc = subprocess.run(argv, capture_output=True, text=True)
        if proc.returncode != 0:
            raise CardError(f"conductor delphi ask failed ({proc.returncode}): {proc.stderr.strip()[-400:]}")
        return proc.stdout, {"profile": DIRECTOR_PROFILE, "stderr_tail": _tail(proc.stderr.encode())}
    out = workdir / name
    target = opts.get("target") or {"provider": "anthropic", "model": opts["model"], "effort": "high"}
    argv = [opts["delphi"], "run", "-provider", target["provider"], "-model", target["model"]]
    if target.get("effort"):
        argv += ["-effort", target["effort"]]
    argv += ["-every", "30s", "-out", str(out), "-prompt", prompt.read_text(encoding="utf-8")]
    proc = subprocess.run(argv, capture_output=True, text=True, env=_delphi_env(opts))
    results = out / "results.jsonl"
    if proc.returncode != 0 or not results.is_file():
        raise CardError(f"delphi run failed ({proc.returncode}): {proc.stderr.strip()[-400:]}")
    rows = [json.loads(line) for line in results.read_text(encoding="utf-8").splitlines() if line.strip()]
    result = rows[-1]
    meta = {k: result.get(k) for k in ("status", "model", "batch_id", "usage", "stop_reason", "truncated")}
    if result.get("status") == "refused":
        raise _Refused(f"the model declined: {json.dumps(result.get('refusal'))}")
    if result.get("status") != "succeeded":
        raise CardError(f"delphi returned status {result.get('status')}: "
                        f"{json.dumps(result.get('refusal') or result.get('error'))}")
    return result["text"], meta


def lane(designs: list[str], binds: list[str], card_out: str, assessment_out: str, via: str = "auto",
         opts: dict[str, Any] | None = None, repo: Path = REPO, say=print) -> int:
    """Exit status: 0 ran and assessed; 1 a reply was refused (nothing written for it);
    2 impediment (no backend, a call failed, a path already exists); 3 the run stopped at a
    failing command and was assessed."""
    opts = {"conductor": os.environ.get("CONDUCTOR", "conductor"),
            "delphi": os.environ.get("DELPHI", "delphi"), "model": DIRECTOR_MODEL, **(opts or {})}
    opts["free"] = opts.get("free") or os.environ.get("DELPHI_FREE") or None
    card_out, assessment_out = safe_relative(card_out), safe_relative(assessment_out)
    workdir = repo / (card_out.rsplit(".", 1)[0] + ".lane")
    record: dict[str, Any] = {"card": card_out, "assessment": assessment_out, "calls": {}}
    try:
        for path in (card_out, assessment_out):
            if (repo / path).exists():
                raise CardError(f"{path} already exists; cards and assessments are write-once")
        if workdir.exists():
            raise CardError(f"{rel(repo, workdir)} already exists; every lane gets a fresh record")
        if opts.get("free") and opts["free"] not in FREE_MODES:
            raise CardError(f"--free must be one of {', '.join(FREE_MODES)}, not {opts['free']!r}")
        # Routing is Delphi's capability registry and free mode is DELPHI_FREE; both are
        # standalone delphi's, and Conductor-hosted Delphi uses its fixed, paid director profile.
        needs = [flag for flag, on in (("--route", opts.get("route")), ("--free (DELPHI_FREE)", opts.get("free")))
                 if on]
        if needs:
            if via == "conductor":
                raise CardError(f"{' and '.join(needs)} needs standalone delphi; Conductor-hosted Delphi "
                                "uses its fixed director profile")
            if not shutil.which(opts["delphi"]):
                raise CardError(f"{' and '.join(needs)} needs the delphi binary ({opts['delphi']} not found)")
            backend = "delphi"
        else:
            backend = pick_backend(via, opts["conductor"], opts["delphi"])
        record["backend"] = backend
        if opts.get("free"):
            record["free"] = opts["free"]
        say(f"LANE backend {backend}" + (f", free mode ({opts['free']})" if opts.get("free") else ""))
        workdir.mkdir(parents=True)

        def call(stage: str, text: str, accept) -> list[str]:
            """Ask, and let accept (ingest) judge the reply; with --route a refused reply goes to
            the next model in the escalation chain, except a compile reply whose findings are all
            specification errors: that is the design's gap, not the model's."""
            prompt = workdir / f"{stage}.prompt.md"
            prompt.write_text(text, encoding="utf-8")
            targets: list[dict[str, str] | None] = [None]
            if opts.get("route"):
                plan = route_for(FAMILY[stage], opts)
                record.setdefault("routes", {})[stage] = plan
                say(f"LANE {stage}: routed to {plan['choice']} ({plan['basis']})")
                targets = [_target(t) for t in [plan["choice"], *plan["escalation"]]]
            findings: list[str] = []
            for attempt, target in enumerate(targets):
                name = stage if attempt == 0 else f"{stage}-escalation-{attempt}"
                say(f"LANE {name}: submitted" + (f" to {target['provider']}:{target['model']}" if target else "")
                    + ", waiting for the batch")
                try:
                    answer, meta = _ask(backend, prompt, workdir, name, dict(opts, target=target))
                except _Refused as exc:
                    record["calls"][name] = {"prompt_sha256": sha256_bytes(text.encode()), "target": target,
                                             "refused": str(exc)}
                    findings = [str(exc)]
                    say(f"LANE {name}: {exc}")
                    continue
                (workdir / f"{name}.reply.md").write_text(answer, encoding="utf-8")
                findings = accept(answer)
                record["calls"][name] = {"prompt_sha256": sha256_bytes(text.encode()),
                                         "reply_sha256": sha256_bytes(answer.encode()), "target": target,
                                         "accepted": not findings, **meta}
                say(f"LANE {name}: answered" + (f" (batch {meta['batch_id']}, usage {json.dumps(meta['usage'])})"
                                                if meta.get("batch_id") else ""))
                if not findings or all(f.startswith("specification_error:") for f in findings):
                    return findings
                if attempt + 1 < len(targets):
                    say(f"LANE {name}: refused by the tool ({findings[0]}); escalating")
            return findings

        findings = call("compile", compile_request(designs, binds, card_out, repo),
                        lambda reply: ingest(reply, card_out, "card", None, repo))
        if findings:
            record["outcome"] = "card_refused"
            for item in findings:
                say(f"INGEST: {item}")
            say(f"LANE FAIL card refused; replies kept in {rel(repo, workdir)}")
            return 1
        card_path, card_sha, card = load_card(card_out, repo)
        say(f"CARD OK {card_path} sha256 {card_sha}")
        receipt = run_card(card_path, card_sha, card, repo)
        say(brief(receipt, card["receipt"], sha256_file(repo / card["receipt"])))
        findings = call("assess", assess_request(card_path, card_sha, card, None, repo),
                        lambda reply: ingest(reply, assessment_out, "assessment", card, repo))
        if findings:
            record["outcome"] = "assessment_refused"
            for item in findings:
                say(f"INGEST: {item}")
            say(f"LANE FAIL assessment refused; replies kept in {rel(repo, workdir)}")
            return 1
        verdict = yaml.safe_load((repo / assessment_out).read_text(encoding="utf-8"))["execution_assessment"]
        record.update(outcome=verdict["outcome"], recommendation=verdict["recommendation"],
                      card_sha256=card_sha, receipt=card["receipt"])
        say(f"LANE OK {verdict['outcome']} -> {verdict['recommendation']}; assessment {assessment_out}")
        return 0 if receipt["status"] == "completed" else 3
    except CardError as exc:
        record["outcome"] = "impeded"
        record["impediment"] = str(exc)
        say(f"IMPEDIMENT {exc}")
        return 2
    finally:
        if workdir.is_dir():
            (workdir / "lane.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n",
                                               encoding="utf-8")


def _main_batch(args) -> int:
    try:
        if args.command == "request" and args.mode == "compile":
            sys.stdout.write(compile_request(args.design, args.bind or [], args.out) + "\n")
            return 0
        card = None
        if args.card:
            card_path, card_sha, card = load_card(args.card)
        if args.command == "request":
            report = Path(args.report).read_text(encoding="utf-8") if args.report else None
            sys.stdout.write(assess_request(card_path, card_sha, card, report) + "\n")
            return 0
        if args.expect == "assessment" and card is None:
            raise CardError("ingest --expect assessment needs --card")
        reply = Path(args.reply).read_text(encoding="utf-8")
        findings = ingest(reply, args.out, args.expect, card)
    except CardError as exc:
        print(f"CARD ERROR {exc}")
        return 2
    for item in findings:
        print(f"INGEST: {item}")
    print(f"INGEST {'FAIL' if findings else 'OK'} {args.out}")
    return 1 if findings else 0


def _print_final(card: dict[str, Any], receipt: dict[str, Any], repo: Path = REPO) -> int:
    print(brief(receipt, card["receipt"], sha256_file(repo / card["receipt"])))
    if receipt["status"] == "completed":
        return 0
    if receipt["status"] == "detached":
        return EXIT_RUNNING
    if receipt["status"].startswith("lost"):
        return EXIT_LOST
    return 3


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("lint", "prompt", "run", "status"):
        sub.add_parser(name).add_argument("card")
    waiting = sub.add_parser("wait", help="poll a detached step, then finish the card and its receipt")
    waiting.add_argument("card")
    waiting.add_argument("--interval", type=float, default=WAIT_INTERVAL_SECONDS,
                         help=f"seconds between polls (default {WAIT_INTERVAL_SECONDS})")
    waiting.add_argument("--max-seconds", type=float, default=WAIT_MAX_SECONDS,
                         help=f"stop waiting after this long, exit 4 (default {WAIT_MAX_SECONDS}; 0: no window)")
    supervise = sub.add_parser("_supervise", help=argparse.SUPPRESS)
    supervise.add_argument("--repo", required=True)
    supervise.add_argument("spec")
    relay = sub.add_parser("check-relay")
    relay.add_argument("card")
    relay.add_argument("--report", required=True, help="the executor's returned text, saved to a file")
    request = sub.add_parser("request", help="a self-contained director prompt for a batch API")
    request.add_argument("mode", choices=("compile", "assess"))
    request.add_argument("card", nargs="?", help="assess: the card")
    request.add_argument("--design", action="append", help="compile: a decided design file (repeatable)")
    request.add_argument("--bind", action="append", help="compile: a file whose sha256 the card binds")
    request.add_argument("--out", help="compile: where the card will be written")
    request.add_argument("--report", help="assess: an executor's relayed text, when one relayed")
    take = sub.add_parser("ingest", help="validate a batch reply and write it write-once")
    take.add_argument("reply")
    take.add_argument("--expect", choices=("card", "assessment"), required=True)
    take.add_argument("--out", required=True)
    take.add_argument("--card", help="assessment: the card it assesses")
    run_lane = sub.add_parser("lane", help="compile, run and assess end to end through a batch backend")
    run_lane.add_argument("--design", action="append", required=True, help="a decided design file (repeatable)")
    run_lane.add_argument("--bind", action="append", help="a file whose sha256 the card binds")
    run_lane.add_argument("--card", required=True, help="where the card is written")
    run_lane.add_argument("--assessment", required=True, help="where the assessment is written")
    run_lane.add_argument("--via", choices=("auto", "conductor", "delphi"), default="auto")
    run_lane.add_argument("--task", help="conductor: link each delegation to this Conductor task")
    run_lane.add_argument("--model", default=DIRECTOR_MODEL, help="delphi: the director model")
    run_lane.add_argument("--route", action="store_true",
                          help="let `delphi route` choose each step's model and escalate refused replies")
    run_lane.add_argument("--free", choices=FREE_MODES,
                          help="delphi free mode: only models that cost nothing (public: free remote tiers too, "
                               "for public or synthetic designs only)")
    args = parser.parse_args(argv)
    if args.command == "_supervise":
        return _supervise(Path(args.repo), args.spec)
    if args.command == "lane":
        return lane(args.design, args.bind or [], args.card, args.assessment, args.via,
                    {"task": args.task, "model": args.model, "route": args.route, "free": args.free})
    if args.command in ("request", "ingest"):
        if args.command == "request" and args.mode == "compile" and not (args.design and args.out):
            parser.error("request compile needs --design and --out")
        if args.command == "request" and args.mode == "assess" and not args.card:
            parser.error("request assess needs the card")
        return _main_batch(args)

    try:
        card_path, card_sha, card = load_card(args.card)
    except CardError as exc:
        print(f"CARD ERROR {exc}")
        return 2
    if args.command == "run":
        try:
            receipt = run_card(card_path, card_sha, card)
        except CardError as exc:
            print(f"IMPEDIMENT {exc}")
            return 2
        return _print_final(card, receipt)
    if args.command == "wait":
        try:
            receipt = wait_card(card, interval=args.interval, max_seconds=args.max_seconds)
        except CardError as exc:
            print(f"IMPEDIMENT {exc}")
            return 2
        return _print_final(card, receipt)
    if args.command == "status":
        try:
            code, lines = status_card(card)
        except (CardError, OSError, ValueError, KeyError) as exc:
            print(f"IMPEDIMENT {exc}")
            return 2
        print("\n".join(lines))
        return code
    findings = lint(card)
    if args.command == "lint" or findings:
        for item in findings:
            print(f"CARD: {item}")
        print(f"CARD {'FAIL' if findings else 'OK'} {card_path} sha256 {card_sha}")
        return 1 if findings else 0
    if args.command == "prompt":
        sys.stdout.write(render_prompt(card_path, card_sha, card))
        return 0
    report = Path(args.report).read_text(encoding="utf-8")
    result = check_relay(card, report)
    print(json.dumps(result, indent=2, sort_keys=True))
    clean = result["relay_verbatim"] and not result["verify_findings"]
    return 0 if clean else 1


if __name__ == "__main__":
    sys.exit(main())
