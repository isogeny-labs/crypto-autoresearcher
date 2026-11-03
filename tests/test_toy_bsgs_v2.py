"""Boundary and count-field controls for the versioned toy BSGS driver."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples/runbooks/toy-ecdlp-bsgs"


def call(mode: str, value: str, directory: Path) -> tuple[subprocess.CompletedProcess[str], subprocess.CompletedProcess[str] | None]:
    directory.mkdir()
    command = [sys.executable, str(EXAMPLE / "solve_v2.py"), "--trial-id", "boundary",
               "--mode", mode, "--curve", str(EXAMPLE / "curve.json"), "--run-dir", str(directory)]
    if mode == "known-k":
        command += ["--k", value]
    elif mode == "search":
        command += ["--seed", value]
    produced = subprocess.run(command, capture_output=True, text=True)
    if produced.returncode:
        return produced, None
    checked = subprocess.run([sys.executable, str(EXAMPLE / "check_v2.py"),
                              str(directory), str(EXAMPLE / "curve.json"), mode, value],
                             capture_output=True, text=True)
    return produced, checked


class VersionedBsgsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="bsgs-v2-", dir="/var/tmp")
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_zero_identity_and_canonical_boundaries(self) -> None:
        for value in ("0", "1", "1024", "1047688"):
            with self.subTest(value=value):
                produced, checked = call("known-k", value, self.root / value)
                self.assertEqual(produced.returncode, 0, produced.stderr)
                self.assertIsNotNone(checked)
                self.assertEqual(checked.returncode, 0, checked.stderr)
                record = json.loads((self.root / value / "raw-result.json").read_text())
                self.assertEqual(record["k_found"], int(value))
                self.assertEqual(record["Q"] is None, value == "0")

    def test_negative_and_out_of_range_scalar_rejected(self) -> None:
        for value in ("-1", "1047689"):
            with self.subTest(value=value):
                produced, checked = call("known-k", value, self.root / value)
                self.assertNotEqual(produced.returncode, 0)
                self.assertIn("canonical scalar", produced.stderr)
                self.assertIsNone(checked)

    def test_boolean_logarithm_is_not_a_scalar(self) -> None:
        produced, checked = call("known-k", "1", self.root / "boolean")
        self.assertEqual(produced.returncode, 0, produced.stderr)
        self.assertIsNotNone(checked)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        result_file = self.root / "boolean" / "raw-result.json"
        record = json.loads(result_file.read_text())
        record["k_found"] = True
        result_file.write_text(json.dumps(record))
        check = subprocess.run([sys.executable, str(EXAMPLE / "check_v2.py"), str(self.root / "boolean"),
                                str(EXAMPLE / "curve.json"), "known-k", "1"], capture_output=True, text=True)
        self.assertEqual(check.returncode, 1)
        self.assertIn("no logarithm", check.stdout)

    def test_setup_count_mutation_fails_checker(self) -> None:
        produced, checked = call("known-k", "123456", self.root / "control")
        self.assertEqual(produced.returncode, 0, produced.stderr)
        self.assertIsNotNone(checked)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        result_file = self.root / "control" / "raw-result.json"
        record = json.loads(result_file.read_text())
        record["setup_ops"] += 1
        result_file.write_text(json.dumps(record))
        check = subprocess.run([sys.executable, str(EXAMPLE / "check_v2.py"), str(self.root / "control"),
                                str(EXAMPLE / "curve.json"), "known-k", "123456"], capture_output=True, text=True)
        self.assertEqual(check.returncode, 1)
        self.assertIn("setup_ops differs", check.stdout)


if __name__ == "__main__":
    unittest.main()
