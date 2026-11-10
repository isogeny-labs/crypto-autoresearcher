"""Published-source C6/C7 schedule checks; no candidate or control trial."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from c67_control_schedule import (COHORTS, check, cohort_schedule, schedule,
                                  write_once)


class C67ScheduleTests(unittest.TestCase):
    def test_q5_published_source_strata_and_first_units(self):
        row = cohort_schedule("q5-n3")
        self.assertEqual(row["cohort"], "q5-n3")
        self.assertEqual(row["source_T_blocks"], 504)
        self.assertEqual([s["source_T_blocks"] for s in row["strata"]],
                         [42, 126, 84, 126, 126])
        self.assertEqual([(s["C6"]["class_index"], s["C6"]["T_index"])
                          for s in row["strata"]],
                         [(2, 0), (0, 0), (4, 0), (2, 1), (0, 1)])
        self.assertTrue(all(s["C6"]["structure_ordinal"] == 0
                            and s["C6"]["slots"] == 16
                            and [c["scalar_class"] for c in s["C7"]] == [0, 1]
                            for s in row["strata"]))

    def test_write_once_exact_readback_and_tamper(self):
        fixture = {"cohort": "fixed-source-fixture", "strata": []}
        with patch("c67_control_schedule.cohort_schedule", return_value=fixture):
            with tempfile.TemporaryDirectory(prefix="pext-c67-schedule-") as root:
                path = Path(root) / "schedule.json"
                digest = write_once(path)
                self.assertEqual(check(path), digest)
                saved = json.loads(path.read_bytes())
                self.assertEqual(saved["C6_selected_units"], 0)
                self.assertEqual(len(saved["cohorts"]), len(COHORTS))
                with self.assertRaises(FileExistsError):
                    write_once(path)
                saved["seed"] += 1
                path.write_text(json.dumps(saved))
                with self.assertRaisesRegex(ValueError, "differs from published"):
                    check(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
