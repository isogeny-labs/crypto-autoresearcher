"""Full historical n3 source identity and mutation checks."""

import json
from pathlib import Path
import tempfile
import unittest

from legacy_n3_alignment import (FIXTURES, INPUTS, OLD, check_alignment,
                                 compare_certificate, historical_field)


class LegacyN3AlignmentTests(unittest.TestCase):
    def test_both_full_ordered_cohorts(self):
        for q, (_, _, count) in FIXTURES.items():
            row = check_alignment(q)
            self.assertEqual(row["classes"], count)
            self.assertEqual(row["status"],
                             "complete_field_and_ordered_class_identity")
            record = json.loads((INPUTS / f"q{q}-n3.json").read_bytes())
            self.assertEqual(historical_field(q), record["field"])

    def test_fixture_and_model_mutations_are_refused(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            fixture = root / "fixture.jsonl"
            fixture.write_bytes((OLD / "fixtures/R1-n3-q5.jsonl").read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "fixture hash"):
                check_alignment(5, fixture=fixture)
            source = json.loads((INPUTS / "q5-n3.json").read_bytes())
            source["representatives"][0], source["representatives"][1] = (
                source["representatives"][1], source["representatives"][0])
            changed = root / "classes.json"
            changed.write_text(json.dumps(source))
            with self.assertRaisesRegex(ValueError, "ordered class"):
                check_alignment(5, inputs=changed)

    def test_committed_certificate_exact_readback(self):
        path = INPUTS / "legacy-n3-alignment.json"
        digest = compare_certificate(path)
        self.assertEqual(len(digest), 64)
        with tempfile.TemporaryDirectory() as scratch:
            changed = Path(scratch) / "changed.json"
            changed.write_bytes(path.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "full recomputation"):
                compare_certificate(changed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
