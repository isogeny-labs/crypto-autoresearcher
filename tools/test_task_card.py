#!/usr/bin/env python3
"""Tests for tools/task_card.py frozen-command cards, including detached steps.

The executor's shell is killed at 600 s (docs/session-logs/2026-11-08.md), so a
long command is started detached, `wait` finishes it, and `status` tells a
running step from an exited one and from a lost one.

Run: python3 -m unittest tools.test_task_card
"""
from __future__ import annotations

import io
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import task_card as tc  # noqa: E402

EMIT = "import sys\nprint('line one')\nprint('value=42')\nsys.exit(int(sys.argv[1]))\n"
SLEEP = "import sys, time\ntime.sleep(float(sys.argv[1]))\nprint('slept', sys.argv[1])\n"


def _git_repo(root: Path):
    repo = root / "repo"
    (repo / "tools").mkdir(parents=True)
    (repo / "tools" / "emit.py").write_text(EMIT)
    (repo / "tools" / "nap.py").write_text(SLEEP)
    for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"],
                 ["add", "-A"], ["commit", "-q", "-m", "init"]):
        subprocess.run(["git", *args], cwd=repo, check=True)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True,
                          text=True, check=True).stdout.strip()
    return repo, head


def _card(repo: Path, head: str, commands: list[dict], **extra) -> dict:
    card = {
        "schema": tc.SCHEMA, "card_id": "CARD-EXAMPLE-detach-01", "experiment_id": "EXAMPLE-detach",
        "author_role": "experiment-director", "executor_role": "executor-mechanical",
        "kind": "frozen_command", "commit": head, "receipt": "out/CARD-EXAMPLE-detach-01.receipt.json",
        "binds": [{"path": f"tools/{name}", "sha256": tc.sha256_file(repo / "tools" / name)}
                  for name in ("emit.py", "nap.py")],
        "commands": commands,
        "bus_address": "executor-mechanical-test", "background": False,
        "write_scope": ["out/"], "stop_when": ["The run command exits with status 2."],
    }
    card.update(extra)
    return card


def _nap(seconds: str, timeout: int, ident: str = "nap") -> dict:
    return {"id": ident, "argv": ["python3", "tools/nap.py", seconds], "timeout_seconds": timeout,
            "success_exit_codes": [0], "stdout": f"out/{ident}.stdout", "stderr": f"out/{ident}.stderr"}


def _emit(code: str = "0", timeout: int = 30) -> dict:
    """timeout 1 keeps it inline (not above) on the detach tests' 1 s threshold."""
    return {"id": "emit", "argv": ["python3", "tools/emit.py", code], "timeout_seconds": timeout,
            "success_exit_codes": [0]}


class InlineCards(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo, self.head = _git_repo(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_short_commands_run_inline_and_relay_verbatim(self):
        card = _card(self.repo, self.head, [_emit(), _emit()])
        self.assertEqual(tc.lint(card, self.repo), [])
        receipt = tc.run_card("card.yaml", "0" * 64, card, self.repo)
        self.assertEqual(receipt["status"], "completed")
        self.assertEqual([c["exit_code"] for c in receipt["commands"]], [0, 0])
        self.assertFalse((self.repo / tc.run_dir(card)).exists())
        printed = tc.brief(receipt, card["receipt"], tc.sha256_file(self.repo / card["receipt"]))
        self.assertIn("value=42", printed)
        self.assertTrue(tc.check_relay(card, printed, self.repo)["relay_verbatim"])

    def test_a_failing_command_stops_the_card(self):
        card = _card(self.repo, self.head, [_emit("3"), _emit()])
        receipt = tc.run_card("card.yaml", "0" * 64, card, self.repo)
        self.assertEqual(receipt["status"], "stopped at command 1")

    def test_receipts_are_write_once(self):
        card = _card(self.repo, self.head, [_emit()])
        tc.run_card("card.yaml", "0" * 64, card, self.repo)
        with self.assertRaises(tc.CardError):
            tc.run_card("card.yaml", "0" * 64, card, self.repo)


class DetachLint(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo, self.head = _git_repo(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_long_command_without_log_paths_is_refused(self):
        long = _emit()
        long["timeout_seconds"] = 3600            # above the default 540
        # A legacy card (no explicit detach_above_seconds) keeps the inline run.
        legacy = _card(self.repo, self.head, [long])
        self.assertEqual([f for f in tc.lint(legacy, self.repo) if "log path" in f], [])
        self.assertFalse(tc._detaches(legacy, long))
        # A card that opts into detaching must name the log paths.
        findings = tc.lint(_card(self.repo, self.head, [long], detach_above_seconds=540), self.repo)
        self.assertTrue(any("exceeds detach_above_seconds 540" in f and "stdout" in f for f in findings),
                        findings)

    def test_the_threshold_is_per_card_and_validated(self):
        short = _emit()                           # 30 s: inline at 540, detached at 10
        self.assertEqual(tc.lint(_card(self.repo, self.head, [short]), self.repo), [])
        findings = tc.lint(_card(self.repo, self.head, [short], detach_above_seconds=10), self.repo)
        self.assertTrue(any("needs the log path" in f for f in findings), findings)
        findings = tc.lint(_card(self.repo, self.head, [short], detach_above_seconds=0), self.repo)
        self.assertTrue(any(f.startswith("detach_above_seconds") for f in findings), findings)

    def test_the_run_directory_must_be_in_write_scope(self):
        card = _card(self.repo, self.head, [_nap("0", 30)], detach_above_seconds=1,
                     write_scope=["out/nap.stdout", "out/nap.stderr", "out/CARD-EXAMPLE-detach-01.receipt.json"])
        findings = tc.lint(card, self.repo)
        self.assertTrue(any("detached run directory" in f for f in findings), findings)
        self.assertEqual(tc.run_dir(card), "out/CARD-EXAMPLE-detach-01.run")

    def test_the_prompt_says_run_then_wait_only_when_a_command_detaches(self):
        inline = _card(self.repo, self.head, [_emit()])
        detached = _card(self.repo, self.head, [_nap("0", 30)], detach_above_seconds=1)
        self.assertNotIn("task_card.py wait", tc.render_prompt("c.yaml", "0" * 64, inline, self.repo))
        self.assertIn("python3 tools/task_card.py wait c.yaml",
                      tc.render_prompt("c.yaml", "0" * 64, detached, self.repo))


class DetachedRuns(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo, self.head = _git_repo(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def _receipt(self, card):
        return json.loads((self.repo / card["receipt"]).read_text())

    def test_run_detaches_then_wait_finishes_and_runs_the_rest(self):
        card = _card(self.repo, self.head, [_emit(timeout=1), _nap("0.6", 30), _emit(timeout=1)], detach_above_seconds=1)
        self.assertEqual(tc.lint(card, self.repo), [])
        receipt = tc.run_card("card.yaml", "0" * 64, card, self.repo)
        self.assertEqual(receipt["status"], "detached")
        self.assertEqual(len(receipt["commands"]), 2)
        entry = receipt["commands"][1]
        self.assertEqual(entry["status"], "detached")
        pid_file = self.repo / entry["pid_file"]
        self.assertEqual(entry["pid_file"], "out/CARD-EXAMPLE-detach-01.run/02-nap.pid.json")
        record = json.loads(pid_file.read_text())
        self.assertEqual(record["pid"], entry["pid"])
        self.assertIn("started_at", record)
        self.assertEqual(self._receipt(card)["status"], "detached")
        printed = tc.brief(receipt, card["receipt"], tc.sha256_file(self.repo / card["receipt"]))
        self.assertIn("next: python3 tools/task_card.py wait card.yaml", printed)

        code, lines = tc.status_card(card, self.repo)
        self.assertEqual(code, tc.EXIT_RUNNING, lines)
        self.assertIn(": running", lines[0])

        said: list[str] = []
        final = tc.wait_card(card, self.repo, interval=0.1, max_seconds=30, say=said.append)
        self.assertIn("polling every 0.1 s", said[0])
        self.assertEqual(final["status"], "completed")
        self.assertEqual([c["exit_code"] for c in final["commands"]], [0, 0, 0])
        self.assertTrue(final["commands"][1]["detached"])
        self.assertEqual(final["commands"][1]["stdout_tail"], ["slept 0.6"])
        self.assertEqual((self.repo / "out/nap.stdout").read_text(), "slept 0.6\n")
        self.assertEqual(self._receipt(card), final)
        code, lines = tc.status_card(card, self.repo)
        self.assertEqual(code, 0)
        self.assertIn(": exited", lines[0])
        self.assertIn("exit 0", lines[0])
        # A second wait on a final receipt changes nothing.
        self.assertEqual(tc.wait_card(card, self.repo, interval=0.1, max_seconds=5, say=said.append), final)

    def test_the_wait_window_closes_with_the_step_still_running(self):
        card = _card(self.repo, self.head, [_nap("3", 30)], detach_above_seconds=1)
        tc.run_card("card.yaml", "0" * 64, card, self.repo)
        said: list[str] = []
        receipt = tc.wait_card(card, self.repo, interval=0.2, max_seconds=0.5, say=said.append)
        self.assertEqual(receipt["status"], "detached")
        self.assertTrue(any("still running" in line for line in said), said)
        final = tc.wait_card(card, self.repo, interval=0.2, max_seconds=30, say=said.append)
        self.assertEqual(final["status"], "completed")

    def test_a_detached_timeout_and_failure_stop_the_card(self):
        card = _card(self.repo, self.head, [_nap("5", 2), _emit(timeout=1)], detach_above_seconds=1)
        tc.run_card("card.yaml", "0" * 64, card, self.repo)
        final = tc.wait_card(card, self.repo, interval=0.2, max_seconds=30, say=lambda _l: None)
        self.assertEqual(final["status"], "stopped at command 1")
        self.assertTrue(final["commands"][0]["timed_out"])
        self.assertEqual(len(final["commands"]), 1)

    def test_a_killed_supervisor_is_lost_and_suggests_a_ledger_row(self):
        card = _card(self.repo, self.head, [_nap("60", 120)], detach_above_seconds=1)
        receipt = tc.run_card("card.yaml", "0" * 64, card, self.repo)
        pid = receipt["commands"][0]["pid"]
        # A container restart: the whole detached session dies, nothing writes an exit record.
        time.sleep(0.3)
        os.killpg(pid, signal.SIGKILL)
        deadline = time.time() + 10
        while tc.step_state(self.repo, receipt["commands"][0]["pid_file"])["state"] == "running":
            self.assertLess(time.time(), deadline)
            time.sleep(0.05)
        code, lines = tc.status_card(card, self.repo)
        self.assertEqual(code, tc.EXIT_LOST, lines)
        self.assertIn(": lost", lines[0])
        self.assertTrue(lines[1].strip().startswith("record the loss: python3 tools/loss_ledger.py add "))
        self.assertIn("--cause container_restart", lines[1])
        final = tc.wait_card(card, self.repo, interval=0.1, max_seconds=5, say=lambda _l: None)
        self.assertEqual(final["status"], "lost at command 1")
        self.assertIn("tools/loss_ledger.py add", final["loss_ledger_suggestion"])
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(tc._print_final(card, final, self.repo), tc.EXIT_LOST)
        self.assertIn("LOST", out.getvalue())
        self.assertIn("record the loss:", out.getvalue())

    def test_a_reused_pid_is_not_mistaken_for_the_step(self):
        card = _card(self.repo, self.head, [_nap("0", 30)], detach_above_seconds=1)
        receipt = tc.run_card("card.yaml", "0" * 64, card, self.repo)
        pid_rel = receipt["commands"][0]["pid_file"]
        tc.wait_card(card, self.repo, interval=0.1, max_seconds=30, say=lambda _l: None)
        # Point the record at this live test process with the wrong start time and drop the exit record.
        record = json.loads((self.repo / pid_rel).read_text())
        exit_file = self.repo / record["exit_file"]
        exit_file.unlink()
        record.update(pid=os.getpid(), pid_start_ticks=(tc._proc_start_ticks(os.getpid()) or 0) + 1)
        (self.repo / pid_rel).write_text(json.dumps(record))
        if Path(f"/proc/{os.getpid()}/stat").is_file():
            self.assertEqual(tc.step_state(self.repo, pid_rel)["state"], "lost")


if __name__ == "__main__":
    unittest.main()
