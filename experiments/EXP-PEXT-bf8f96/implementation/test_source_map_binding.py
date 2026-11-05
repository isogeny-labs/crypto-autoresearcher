"""Formal source-curve map and published class/T/structure binding."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from candidate_binding import CandidateBinder
from candidate_stage import join_path
from source_map_binding import certify, certify_bound


class SourceMapBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-source-map-")
        binary = Path(cls.scratch.name) / "join"
        subprocess.run(["rustc", "--edition=2021", str(Path(__file__).with_name(
            "join_certificate.rs")), "-o", str(binary)], check=True, capture_output=True)
        cls.groups = [json.loads(subprocess.check_output(
            [binary, "f27-char3", str(start), str(start+2)]))
            for start in (0, 819)]

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_fixed_F27_zero_and_nonzero_T_maps(self):
        for group in self.groups:
            for row in group["rows"]:
                cert = certify(group["field"], row["model"],
                               row["target"], row["matrix"])
                self.assertEqual(cert["source_form"], row["original_form"])
                self.assertEqual(cert["moved_form"], row["transformed_form"])
                self.assertEqual(cert["status"],
                                 "source_to_moved_quartic_checked; descended_model_pending")
                self.assertNotEqual(cert["determinant"], 0)

    def test_published_class_T_and_ordinal_binding(self):
        binder = CandidateBinder("q5-n3", plan_path=join_path("q5-n3"))
        for t_index in (0, 1):
            cert = certify_bound(binder, 0, t_index, 0, [1, 0, 0, 1])
            self.assertEqual(cert["source_form"], binder.bind(0, t_index)["quotient_form"])
            self.assertEqual(cert["join_plan_sha256"], binder.plan_sha256)
            self.assertEqual((cert["class_index"], cert["T_index"],
                              cert["structure_ordinal"]), (0, t_index, 0))
        with self.assertRaisesRegex(ValueError, "matrix differs"):
            certify_bound(binder, 0, 1, 0, [0, 1, 1, 0])
        with self.assertRaisesRegex(ValueError, "ordinal outside"):
            certify_bound(binder, 0, 1, -1, [1, 0, 0, 1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
