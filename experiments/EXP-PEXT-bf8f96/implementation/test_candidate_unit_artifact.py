"""Fixed F27 artifact success, started failure, and no-overwrite controls."""

import gzip
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from candidate_unit_artifact import (CandidateUnitArtifacts, _ADMISSION_TOKEN,
                                     software_fixture_runner)
from check_candidate_unit import verify
from independent_candidate_unit import IndependentCandidateChecker
from independent_check import verify_artifact


class CandidateArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-artifact-")
        cls.base = Path(cls.scratch.name)
        implementation = Path(__file__).parent
        for name in ("candidate_unit", "join_certificate"):
            subprocess.run(["rustc", "--edition=2021", str(implementation / f"{name}.rs"),
                            "-o", str(cls.base / name)], check=True, capture_output=True)
        cls.joined = json.loads(subprocess.check_output([cls.base / "join_certificate", "f27-char3"]))
        cls.runner = software_fixture_runner(cls.base / "candidate_unit", cls.base)
        cls.caps = {"field_elements": 27, "structures": 819, "image_entries": 3276,
                    "rational_candidates": 1000, "nonrational_maps": 1000,
                    "total_candidates": 819}
        cls.form = [1, 0, 1, 1, 0]

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_success_is_bound_and_replayed(self):
        receipt = self.runner.run("success", self.form, self.joined["field"], 819,
                                  self.caps, 1024**3, 60, 60)
        self.assertEqual(receipt["status"], "candidate_emitted")
        self.assertEqual(receipt["scope"], "software-fixture")
        directory = self.base / "success"
        self.assertFalse((directory / "unit.json.partial").exists())
        unit = json.loads(gzip.decompress((directory / "unit.json.gz").read_bytes()))
        self.assertEqual(verify(unit, self.joined, self.form)["exceptional"], 279)
        with self.assertRaises(FileExistsError):
            self.runner.run("success", self.form, self.joined["field"], 819,
                            self.caps, 1024**3, 60, 60)

    def test_started_failure_retains_raw_and_stderr(self):
        caps = dict(self.caps, total_candidates=1)
        receipt = self.runner.run("failed", self.form, self.joined["field"], 819,
                                  caps, 1024**3, 60, 60)
        self.assertEqual(receipt["status"], "child_failed")
        self.assertNotEqual(receipt["returncode"], 0)
        directory = self.base / "failed"
        self.assertTrue((directory / "unit.json.partial").is_file())
        self.assertTrue((directory / "stderr.log").is_file())
        self.assertTrue((directory / "failure.json").is_file())
        self.assertFalse((directory / "unit.json.gz").exists())

    def test_limits_and_binary_identity(self):
        with self.assertRaisesRegex(ValueError, "caps"):
            self.runner.run("bad-cap", self.form, self.joined["field"], 819,
                            dict(self.caps, structures=0), 1024**3, 60, 60)
        self.assertFalse((self.base / "bad-cap").exists())
        with self.assertRaisesRegex(ValueError, "memory"):
            self.runner.run("bad-memory", self.form, self.joined["field"], 819,
                            self.caps, 5 * 1024**3, 60, 60)
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            type(self.runner)(self.base / "candidate_unit", "0" * 64, None,
                              "software-fixture", self.base)
        with self.assertRaisesRegex(ValueError, "live supervisor admission"):
            type(self.runner)(self.base / "candidate_unit", self.runner.binary_sha256,
                              None, "approved-cohort", self.base)

    def test_persistent_worker_custody_and_mutation(self):
        class Binder:
            plan_sha256 = "a" * 64
            plan = {"field": self.joined["field"], "structures_per_T": 819}
            def bind(self, class_index, t_index):
                return {"cohort": "q3-n3", "join_plan_sha256": self.plan_sha256,
                        "class_index": class_index, "T_index": t_index,
                        "quotient_form": ([1, 0, 1, 1, 0] if t_index == 0
                                          else [1, 1, 1, 0, 1]),
                        "field": self.plan["field"], "structures_per_T": 819}
        binder = Binder()
        runner = CandidateUnitArtifacts(self.base / "candidate_unit",
                                        self.runner.binary_sha256, binder,
                                        "approved-cohort", self.base, _ADMISSION_TOKEN)
        runner.start_worker(self.caps, 1024**3, 60, 60)
        try:
            for index in range(2):
                binding = binder.bind(0, index)
                name = f"worker-{index}"
                receipt = runner.run_worker(name, binding["quotient_form"],
                                            binding["field"], 819, self.caps,
                                            1024**3, 60, 60, binding)
                self.assertEqual(receipt["status"], "candidate_emitted")
                review = verify_artifact(self.base / name,
                    IndependentCandidateChecker(self.joined["field"]),
                    binding["quotient_form"], runner.binary_sha256,
                    scope="approved-cohort", expected_binding=binding)
                self.assertTrue(review["valid"])
            source = self.base / "worker-0/input.json"
            record = json.loads(source.read_bytes())
            record["worker"]["request"] = "1,1,1,0,1\n"
            source.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, "worker custody|receipt"):
                verify_artifact(self.base / "worker-0",
                    IndependentCandidateChecker(self.joined["field"]),
                    binder.bind(0, 0)["quotient_form"], runner.binary_sha256,
                    scope="approved-cohort", expected_binding=binder.bind(0, 0))
        finally:
            runner.stop_worker()
        death_dir = self.base / "worker-death"
        death_dir.mkdir()
        dead = CandidateUnitArtifacts(self.base / "candidate_unit",
                                      self.runner.binary_sha256, binder,
                                      "approved-cohort", death_dir, _ADMISSION_TOKEN)
        dead.start_worker(self.caps, 1024**3, 60, 60)
        binding = binder.bind(0, 0)
        with mock.patch.object(dead, "_worker_cpu_seconds",
                               side_effect=FileNotFoundError("process disappeared")):
            failure = dead.run_worker("u000000", binding["quotient_form"],
                                      binding["field"], 819, self.caps,
                                      1024**3, 60, 60, binding)
        self.assertEqual(failure["status"], "child_failed")
        self.assertTrue((death_dir / "u000000/failure.json").is_file())
        self.assertFalse((death_dir / "u000000/unit.json.gz").exists())

        startup_dir = self.base / "worker-start-failed"
        startup_dir.mkdir()
        startup = CandidateUnitArtifacts(self.base / "candidate_unit",
                                         self.runner.binary_sha256, binder,
                                         "approved-cohort", startup_dir, _ADMISSION_TOKEN)
        with self.assertRaisesRegex(ValueError, "worker exited"):
            startup.start_worker(dict(self.caps, structures=1), 1024**3, 60, 60)
        self.assertTrue((startup_dir / "worker-start-failure.json").is_file())
        self.assertIn(b"cocycle index entry limit",
                      (startup_dir / "worker.stderr.log").read_bytes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
