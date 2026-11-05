"""Fixed F27 artifact success, started failure, and no-overwrite controls."""

import gzip
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from candidate_unit_artifact import software_fixture_runner
from check_candidate_unit import verify


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
