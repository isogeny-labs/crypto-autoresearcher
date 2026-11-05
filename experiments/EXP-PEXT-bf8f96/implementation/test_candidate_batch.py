"""Deterministic bounded chunk sealing, custody replay and failure retention."""

import gzip
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from candidate_batch import (expected_units, read_chunk, seal_chunk,
                             seal_complete_index, verify_complete_index)
from candidate_unit_artifact import software_fixture_runner
from independent_candidate_unit import IndependentCandidateChecker
from independent_check import verify_artifact


class CandidateChunkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-chunks-")
        cls.parent = Path(cls.scratch.name)
        base = Path(__file__).parent
        for name in ("candidate_unit", "join_certificate"):
            subprocess.run(["rustc", "--edition=2021", str(base / f"{name}.rs"),
                            "-o", str(cls.parent / name)], check=True, capture_output=True)
        cls.joined = json.loads(subprocess.check_output([cls.parent / "join_certificate", "f27-char3"]))
        cls.checker = IndependentCandidateChecker(cls.joined["field"])
        cls.forms = [[1, 0, 1, 1, 0], [1, 1, 1, 0, 1]]
        cls.runner = software_fixture_runner(cls.parent / "candidate_unit", cls.parent)
        cls.caps = {"field_elements": 27, "structures": 819, "image_entries": 3276,
                    "rational_candidates": 1000, "nonrational_maps": 1000,
                    "total_candidates": 819}

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def make_unit(self, name, form):
        self.runner.run(name, form, self.joined["field"], 819,
                        self.caps, 1024**3, 60, 60)
        return self.parent / name

    def test_sealed_chunk_restores_exact_verified_units(self):
        directories = [self.make_unit(f"u{i:06d}", form)
                       for i, form in enumerate(self.forms)]
        chunks = self.parent / "chunks"
        chunks.mkdir()
        archive = chunks / "chunk-000000.tar"
        receipt = seal_chunk(directories, archive)
        self.assertEqual(receipt["unit_count"], 2)
        self.assertTrue(all(not path.exists() for path in directories))
        restored, checked = read_chunk(archive)
        self.assertEqual(checked, receipt)
        self.assertEqual([name for name, _ in restored], ["u000000", "u000001"])
        plan = {"classes": [{"targets": [None, [1, 2]]}],
                "input_sha256": "1"*64, "manifest_sha256": "2"*64,
                "order": "log-point-coset-transversal/v1"}
        self.assertEqual([row["name"] for row in expected_units(plan)],
                         ["u000000", "u000001"])
        index = seal_complete_index(self.parent, "q3-n3", plan, "3"*64,
                                    self.runner.binary_sha256)
        self.assertEqual(index["unit_count"], 2)
        self.assertEqual(verify_complete_index(self.parent, "q3-n3", plan,
                         "3"*64, self.runner.binary_sha256)["chunk_count"], 1)
        index_path = self.parent / "units-index.json"
        index_bytes = index_path.read_bytes()
        changed_index = json.loads(index_bytes)
        changed_index["units"][0]["class_index"] = 7
        index_path.write_text(json.dumps(changed_index))
        with self.assertRaisesRegex(ValueError, "complete index differs"):
            verify_complete_index(self.parent, "q3-n3", plan, "3"*64,
                                  self.runner.binary_sha256)
        index_path.write_bytes(index_bytes)
        stray = chunks / "chunk-999999.partial"
        stray.write_bytes(b"incomplete")
        with self.assertRaisesRegex(ValueError, "unexpected or incomplete"):
            verify_complete_index(self.parent, "q3-n3", plan, "3"*64,
                                  self.runner.binary_sha256)
        stray.unlink()
        for (name, files), form in zip(restored, self.forms):
            directory = self.parent / "restored" / name
            directory.mkdir(parents=True)
            for filename, data in files.items():
                (directory / filename).write_bytes(data)
            report = verify_artifact(directory, self.checker, form,
                                     self.runner.binary_sha256,
                                     scope="software-fixture", full_geometry=True)
            self.assertTrue(report["valid"])
        with self.assertRaises(FileExistsError):
            seal_chunk([self.parent / "restored/u000000"], archive)
        data = bytearray(archive.read_bytes())
        data[2048] ^= 1
        archive.write_bytes(data)
        with self.assertRaisesRegex(ValueError, "receipt identity or digest mismatch"):
            read_chunk(archive)
        with self.assertRaisesRegex(ValueError, "receipt identity or digest mismatch"):
            verify_complete_index(self.parent, "q3-n3", plan, "3"*64,
                                  self.runner.binary_sha256)

    def test_oversized_member_retains_source(self):
        directory = self.make_unit("u999999", self.forms[0])
        (directory / "unit.json.gz").write_bytes(b"x" * (3*1024*1024+1))
        chunks = self.parent / "failure-chunks"
        chunks.mkdir()
        archive = chunks / "chunk-000001.tar"
        with self.assertRaisesRegex(ValueError, "compressed unit exceeds"):
            seal_chunk([directory], archive)
        self.assertTrue(directory.exists())
        self.assertFalse(archive.exists())
        shutil.rmtree(directory)

    def test_compacted_stored_form_reads_back(self):
        directory = self.make_unit("u000010", self.forms[1])
        chunks = self.parent / "compressed-chunks"
        chunks.mkdir()
        archive = chunks / "chunk-000010.tar"
        receipt = seal_chunk([directory], archive)
        compressed = archive.with_name(archive.name + ".gz")
        compressed.write_bytes(gzip.compress(archive.read_bytes(), mtime=0))
        archive.unlink()
        restored, checked = read_chunk(archive)
        self.assertEqual(checked, receipt)
        self.assertEqual(restored[0][0], "u000010")


if __name__ == "__main__":
    unittest.main(verbosity=2)
