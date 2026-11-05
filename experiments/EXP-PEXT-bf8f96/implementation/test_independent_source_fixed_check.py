"""Whole source-fixed certificate gate and geometry tamper refusal."""

import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from fixed_model_geometry import build_from_source
from independent_source_fixed_check import verify


class IndependentSourceFixedCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-source-fixed-check-")
        binary = Path(cls.scratch.name) / "join"
        subprocess.run(["rustc", "--edition=2021", str(Path(__file__).with_name(
            "join_certificate.rs")), "-o", str(binary)], check=True,
                       capture_output=True)
        cls.joined = json.loads(subprocess.check_output(
            [binary, "f27-char3", "0", "4"]))
        row = cls.joined["rows"][0]
        cls.record = build_from_source(cls.joined["field"], row["model"],
                                       row["target"], row["matrix"], row["conjugates"])

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_source_algebra_and_character_genus_agree(self):
        checked = verify(self.record, self.joined["field"],
                         self.joined["rows"][0]["conjugates"])
        self.assertTrue(checked["valid"])
        self.assertEqual((checked["algebra"]["products_checked"],
                          checked["geometry"]["geometric_component_genus"]), (4, 1))

    def test_false_connected_genus_is_rejected(self):
        tampered = copy.deepcopy(self.record)
        tampered["connected_curve_genus"] += 1
        with self.assertRaisesRegex(ValueError, "independent source geometry"):
            verify(tampered, self.joined["field"],
                   self.joined["rows"][0]["conjugates"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
