"""Fixed F27 software control for complete driver and failed-unit retention."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from candidate_census_driver import run_batch
from candidate_census_check import check_batch
from candidate_unit_artifact import CandidateUnitArtifacts, file_sha256


class FixtureBinder:
    cohort = "q3-n3"
    plan_sha256 = "3" * 64
    plan_path = None
    plan = {"classes": [{"targets": [None, [1, 2]]}],
            "input_sha256": "1"*64, "manifest_sha256": "2"*64,
            "order": "log-point-coset-transversal/v1"}

    def __init__(self, field):
        self.field = field

    def bind(self, class_index, t_index):
        if class_index != 0 or t_index not in (0, 1):
            raise ValueError("fixture class/T index")
        return {"cohort": self.cohort, "join_plan_sha256": self.plan_sha256,
                "class_index": class_index, "T_index": t_index,
                "quotient_form": ([1, 0, 1, 1, 0] if t_index == 0
                                  else [1, 1, 1, 0, 1]),
                "field": self.field, "structures_per_T": 819}


class BatchDriverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-batch-driver-")
        cls.base = Path(cls.scratch.name)
        source = Path(__file__).with_name("candidate_unit.rs")
        subprocess.run(["rustc", "--edition=2021", str(source),
                        "-o", str(cls.base / "candidate_unit")],
                       capture_output=True, check=True)
        join_source = source.with_name("join_certificate.rs")
        subprocess.run(["rustc", "--edition=2021", str(join_source),
                        "-o", str(cls.base / "join_certificate")],
                       capture_output=True, check=True)
        cls.field = json.loads(subprocess.check_output(
            [cls.base / "join_certificate", "f27-char3"]))["field"]
        cls.binder = FixtureBinder(cls.field)
        cls.binder.plan["field"] = cls.field
        cls.caps = {"field_elements": 27, "structures": 819,
                    "image_entries": 3276, "rational_candidates": 1000,
                    "nonrational_maps": 1000, "total_candidates": 819}

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def runner(self, directory):
        binary = self.base / "candidate_unit"
        return CandidateUnitArtifacts(binary, file_sha256(binary),
                                      self.binder, "software-fixture", directory)

    def test_complete_two_unit_fixture(self):
        directory = self.base / "complete" / "cohorts" / "q3-n3"
        directory.mkdir(parents=True)
        runner = self.runner(directory)
        result = run_batch(runner, directory, "q3-n3", "3"*64,
                           self.caps, 1024**3, 60, 60, 120)
        self.assertEqual((result["unit_count"], result["chunk_count"]), (2, 1))
        self.assertTrue((directory / "units-index.json").is_file())
        self.assertFalse((directory / "u000000").exists())
        self.assertFalse((directory / "u000001").exists())
        review = check_batch(directory, "q3-n3", self.binder,
                             runner.binary_sha256, scope="software-fixture",
                             full_geometry=True)
        self.assertEqual(review["unit_count"], 2)
        self.assertEqual(review["exceptional"], 280)
        self.assertEqual(review["generic"], 2*819-280)
        self.assertEqual(len((directory / "candidate-reviews.jsonl").read_text().splitlines()), 2)
        with self.assertRaises(FileExistsError):
            check_batch(directory, "q3-n3", self.binder,
                        runner.binary_sha256, scope="software-fixture")
        with self.assertRaises(FileExistsError):
            run_batch(runner, directory, "q3-n3", "3"*64,
                      self.caps, 1024**3, 60, 60, 120)

    def test_failed_first_unit_retained_without_index(self):
        directory = self.base / "failed"
        directory.mkdir()
        runner = self.runner(directory)
        caps = dict(self.caps, total_candidates=1)
        with self.assertRaisesRegex(ValueError, "candidate unit failed: u000000"):
            run_batch(runner, directory, "q3-n3", "3"*64,
                      caps, 1024**3, 60, 60, 120)
        self.assertTrue((directory / "u000000/failure.json").is_file())
        self.assertFalse((directory / "units-index.json").exists())
        self.assertEqual(list((directory / "chunks").iterdir()), [])
        with self.assertRaises(FileExistsError):
            run_batch(runner, directory, "q3-n3", "3"*64,
                      self.caps, 1024**3, 60, 60, 120)

    def test_preflight_refuses_wrong_plan_without_unit(self):
        directory = self.base / "wrong-plan"
        directory.mkdir()
        with self.assertRaisesRegex(ValueError, "join plan hash mismatch"):
            run_batch(self.runner(directory), directory, "q3-n3", "4"*64,
                      self.caps, 1024**3, 60, 60, 120)
        self.assertEqual(list(directory.iterdir()), [])

    def test_checker_deadline_retains_partial(self):
        directory = self.base / "deadline"
        directory.mkdir()
        runner = self.runner(directory)
        run_batch(runner, directory, "q3-n3", "3"*64,
                  self.caps, 1024**3, 60, 60, 120)
        wrong_limits_dir = self.base / "wrong-limits"
        shutil.copytree(directory, wrong_limits_dir)
        wrong_limits = {"caps": dict(self.caps, structures=818),
                        "memory_bytes": 1024**3, "cpu_seconds": 60,
                        "unit_wall_seconds": 60}
        with self.assertRaisesRegex(ValueError, "limits differ from frozen stage"):
            check_batch(wrong_limits_dir, "q3-n3", self.binder,
                        runner.binary_sha256, scope="software-fixture",
                        expected_limits=wrong_limits)
        self.assertFalse((wrong_limits_dir / "candidate-check.json").exists())
        past = datetime.now(timezone.utc) - timedelta(seconds=1)
        with self.assertRaisesRegex(TimeoutError, "checker stage deadline"):
            check_batch(directory, "q3-n3", self.binder,
                        runner.binary_sha256, scope="software-fixture",
                        deadline_utc=past)
        self.assertTrue((directory / "candidate-reviews.partial").is_file())
        self.assertFalse((directory / "candidate-check.json").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
