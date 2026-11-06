"""Source-only checks of the prospective full-fixture C0 replay rule."""

import json
from pathlib import Path
import tempfile
import unittest

from historical_regression_stage import (ARMS, OLD, compare_rows,
                                         expected_artifacts, fixture_path, sha256)


class HistoricalRegressionStageTests(unittest.TestCase):
    def test_all_four_pinned_fixtures_are_complete_self_matches(self):
        expected_counts = (146, 345, 786, 586)
        for arm, count in zip(ARMS, expected_counts):
            path = fixture_path(arm)
            self.assertEqual(sha256(path), arm[4])
            result = compare_rows(path, path)
            self.assertTrue(result["identical"])
            self.assertEqual(result["rows_fixture"], count)
        names = expected_artifacts()
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(len(names), 14)

    def test_timing_only_change_allowed_but_every_other_field_checked(self):
        fixture = OLD / "fixtures/R1-n3-q5.jsonl"
        rows = fixture.read_bytes().splitlines()
        with tempfile.TemporaryDirectory() as scratch:
            output = Path(scratch) / "output.jsonl"
            altered = list(rows)
            field = json.loads(altered[0]); field["setup_s"] = 123.4
            altered[0] = json.dumps(field, separators=(",", ":")).encode()
            totals_index = next(i for i, raw in enumerate(altered)
                                if json.loads(raw).get("rec") == "totals")
            totals = json.loads(altered[totals_index]); totals["wall_s"] = 567.8
            altered[totals_index] = json.dumps(totals, separators=(",", ":")).encode()
            output.write_bytes(b"\n".join(altered) + b"\n")
            self.assertTrue(compare_rows(output, fixture)["identical"])
            field["structures"] += 1
            altered[0] = json.dumps(field, separators=(",", ":")).encode()
            output.write_bytes(b"\n".join(altered) + b"\n")
            self.assertEqual(compare_rows(output, fixture)["first_difference_line"], 0)
            altered[0] = rows[0]
            record = json.loads(altered[1]); record["min_genus"] += 1
            altered[1] = json.dumps(record, separators=(",", ":")).encode()
            output.write_bytes(b"\n".join(altered) + b"\n")
            self.assertEqual(compare_rows(output, fixture)["first_difference_line"], 1)

    def test_missing_row_and_timing_field_are_rejected(self):
        fixture = OLD / "fixtures/pilot-n3-q3-cosets.jsonl"
        rows = fixture.read_bytes().splitlines()
        with tempfile.TemporaryDirectory() as scratch:
            output = Path(scratch) / "output.jsonl"
            output.write_bytes(b"\n".join(rows[:-1]) + b"\n")
            self.assertFalse(compare_rows(output, fixture)["identical"])
            field = json.loads(rows[0]); del field["setup_s"]
            output.write_bytes(json.dumps(field).encode() + b"\n" +
                               b"\n".join(rows[1:]) + b"\n")
            self.assertEqual(compare_rows(output, fixture)["first_difference_line"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
