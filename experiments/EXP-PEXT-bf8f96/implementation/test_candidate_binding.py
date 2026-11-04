"""Read-only custody and selected-T binding checks."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from candidate_binding import DEFAULT_MANIFEST, bind
from join_plan import canonical, expected_plan


class CandidateBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = expected_plan("q5-n3", DEFAULT_MANIFEST)
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-bind-")
        cls.path = Path(cls.scratch.name) / "join-plan.json"
        cls.path.write_bytes(canonical(cls.plan) + b"\n")

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_published_class_and_t(self):
        first = bind("q5-n3", 0, 0, plan_path=self.path)
        self.assertEqual(first["model"], self.plan["classes"][0]["model"])
        self.assertEqual(first["target"], self.plan["classes"][0]["targets"][0])
        self.assertEqual(first["structure_offset"], 0)
        self.assertEqual(first["structure_end_exclusive"], first["structures_per_T"])
        self.assertEqual(first["candidate_unit_args"][0:2], ["5", "3"])
        self.assertEqual(first["status"], "preview_only")

    def test_rejects_wrong_plan_and_indices(self):
        broken = copy.deepcopy(self.plan)
        broken["classes"][0]["targets"].reverse()
        self.path.write_bytes(canonical(broken) + b"\n")
        with self.assertRaisesRegex(ValueError, "join plan"):
            bind("q5-n3", 0, 0, plan_path=self.path)
        self.path.write_bytes(canonical(self.plan) + b"\n")
        for class_index, t_index in ((-1, 0), (len(self.plan["classes"]), 0), (0, -1),
                                     (0, len(self.plan["classes"][0]["targets"]))):
            with self.assertRaises(ValueError):
                bind("q5-n3", class_index, t_index, plan_path=self.path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
