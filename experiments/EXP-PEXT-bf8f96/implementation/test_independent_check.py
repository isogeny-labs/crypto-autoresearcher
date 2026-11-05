"""Artifact custody replay and tamper rejection on fixed F27 software units."""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from candidate_unit_artifact import software_fixture_runner
from independent_candidate_unit import IndependentCandidateChecker
from independent_check import verify_artifact, verify_bound_artifact


class IndependentArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-artifact-check-")
        cls.parent = Path(cls.scratch.name)
        base = Path(__file__).parent
        for name in ("candidate_unit", "join_certificate"):
            subprocess.run(["rustc", "--edition=2021", str(base / f"{name}.rs"),
                            "-o", str(cls.parent / name)], check=True, capture_output=True)
        joined = json.loads(subprocess.check_output([cls.parent / "join_certificate", "f27-char3"]))
        cls.checker = IndependentCandidateChecker(joined["field"])
        cls.form = [1, 0, 1, 1, 0]
        cls.runner = software_fixture_runner(cls.parent / "candidate_unit", cls.parent)
        cls.caps = {"field_elements": 27, "structures": 819, "image_entries": 3276,
                    "rational_candidates": 1000, "nonrational_maps": 1000,
                    "total_candidates": 819}
        cls.runner.run("success", cls.form, joined["field"], 819,
                       cls.caps, 1024**3, 60, 60)
        cls.runner.run("failed", cls.form, joined["field"], 819,
                       dict(cls.caps, total_candidates=1), 1024**3, 60, 60)

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def verify(self, directory, **kwargs):
        return verify_artifact(directory, self.checker, self.form,
                               self.runner.binary_sha256,
                               scope="software-fixture", **kwargs)

    def test_complete_success_and_failed_attempt(self):
        reviewed = self.verify(self.parent / "success", full_geometry=True)
        self.assertEqual(reviewed["independent"]["exceptional"], 279)
        self.assertEqual(reviewed["independent"]["geometry_checked"], 279)
        with self.assertRaisesRegex(ValueError, "failure or partial"):
            self.verify(self.parent / "failed")

    def test_mutated_input_receipt_and_payload(self):
        for name in ("input", "receipt", "payload"):
            with self.subTest(name=name):
                directory = self.parent / name
                shutil.copytree(self.parent / "success", directory)
                if name == "input":
                    path = directory / "input.json"
                    value = json.loads(path.read_bytes())
                    value["form"][0] ^= 1
                    path.write_text(json.dumps(value) + "\n")
                    pattern = "input does not match external binding"
                elif name == "receipt":
                    path = directory / "receipt.json"
                    value = json.loads(path.read_bytes())
                    value["raw_sha256"] = "0"*64
                    path.write_text(json.dumps(value) + "\n")
                    pattern = "raw digest mismatch"
                else:
                    path = directory / "unit.json.gz"
                    data = bytearray(path.read_bytes())
                    data[15] ^= 1
                    path.write_bytes(data)
                    pattern = "receipt or digest mismatch"
                with self.assertRaisesRegex(ValueError, pattern):
                    self.verify(directory)

    def test_external_identity_and_scope(self):
        with self.assertRaisesRegex(ValueError, "external binary SHA-256"):
            verify_artifact(self.parent / "success", self.checker, self.form,
                            "not-a-digest", scope="software-fixture")
        with self.assertRaisesRegex(ValueError, "external production binding"):
            verify_artifact(self.parent / "success", self.checker, self.form,
                            self.runner.binary_sha256, scope="approved-cohort")
        with self.assertRaisesRegex(ValueError, "checked published join plan"):
            verify_bound_artifact(self.parent / "success", object(), 0, 0,
                                  self.checker, self.runner.binary_sha256)


if __name__ == "__main__":
    unittest.main(verbosity=2)
