"""Source-bound write-once Rust build and tamper refusal software controls."""

import json
from pathlib import Path
import tempfile
import unittest

from candidate_build import ROOT, SOURCES, build, sha256, verify_build


class CandidateBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {name: sha256(ROOT / name) for name in SOURCES}

    def test_build_verifies_and_refuses_overwrite_and_tamper(self):
        with tempfile.TemporaryDirectory(prefix="pext-candidate-build-") as temporary:
            directory = Path(temporary)
            binary, receipt = build(directory, self.sources)
            self.assertEqual(binary.name, "candidate-unit")
            self.assertEqual(receipt["binary_sha256"], sha256(binary))
            self.assertEqual(verify_build(directory, self.sources)[1], receipt)
            with self.assertRaises(FileExistsError):
                build(directory, self.sources)
            receipt_path = directory / "candidate-build.json"
            original = receipt_path.read_bytes()
            changed = json.loads(original)
            changed["binary_sha256"] = "0"*64
            receipt_path.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, "receipt or binary mismatch"):
                verify_build(directory, self.sources)
            receipt_path.write_bytes(original)
            with binary.open("ab") as stream:
                stream.write(b"changed")
            with self.assertRaisesRegex(ValueError, "receipt or binary mismatch"):
                verify_build(directory, self.sources)

    def test_bad_source_hash_refuses_before_artifacts(self):
        with tempfile.TemporaryDirectory(prefix="pext-build-bad-source-") as temporary:
            directory = Path(temporary)
            wrong = dict(self.sources, **{SOURCES[0]: "0"*64})
            with self.assertRaisesRegex(ValueError, "source hash mismatch"):
                build(directory, wrong)
            self.assertEqual(list(directory.iterdir()), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
