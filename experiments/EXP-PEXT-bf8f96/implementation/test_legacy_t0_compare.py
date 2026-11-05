"""C0 projection and full-cohort identity refusal on fixture-shaped inputs."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from legacy_n3_alignment import FIXTURES, INPUTS, OLD
from legacy_t0_compare import (ARTIFACT, Q3_FIXTURE, Q3_MAPPING, class_rows,
                               compare_artifact, compare_cohort,
                               historical_projection, write_artifact)


def fixture_shaped_curves(cohort):
    """Software input only: populate new-shaped rows from old fixture data."""
    q, n, count = {"q5-n3": (5, 3, 252), "q7-n3": (7, 3, 690),
                   "q3-n5": (3, 5, 488)}[cohort]
    path = Q3_FIXTURE if q == 3 else OLD / "fixtures" / FIXTURES[q][0]
    old = class_rows(path, q, n, count)
    representatives = json.loads((INPUTS / f"{cohort}.json").read_bytes())["representatives"]
    curves = [{"cohort": cohort, "class_index": i, "model": model, "units": []}
              for i, model in enumerate(representatives)]
    indices = ([row["class_index"] for row in json.loads(Q3_MAPPING.read_bytes())["rows"]]
               if q == 3 else list(range(count)))
    for fixture, index in zip(old, indices):
        histogram = fixture["structures_by_m_r"]
        curves[index]["units"] = [{"T_index": 0, "m_r_histogram": histogram,
                                   "structures": sum(histogram.values())}]
    return curves


class LegacyT0CompareTests(unittest.TestCase):
    def test_historical_rank_one_convention(self):
        fixture = class_rows(OLD / "fixtures/R1-n3-q5.jsonl", 5, 3, 252)[0]
        histogram = fixture["structures_by_m_r"]
        self.assertEqual(historical_projection(histogram, sum(histogram.values())),
                         {key: fixture[key] for key in (
                             "structures_by_m_r", "structures_by_genus",
                             "m1_structures", "min_genus")})

    def test_full_q5_identity_and_cover_mismatch_refusal(self):
        curves = fixture_shaped_curves("q5-n3")
        self.assertEqual(compare_cohort("q5-n3", curves)["historical_class_rows"], 252)
        bad = copy.deepcopy(curves)
        bad[0]["units"][0]["m_r_histogram"]["3,8"] += 1
        with self.assertRaisesRegex(ValueError, "structure coverage"):
            compare_cohort("q5-n3", bad)
        bad = copy.deepcopy(curves)
        bad[1]["model"] = bad[0]["model"]
        with self.assertRaisesRegex(ValueError, "published identity"):
            compare_cohort("q5-n3", bad)

    def test_q3_bijection_joins_historical_order_to_new_order(self):
        curves = fixture_shaped_curves("q3-n5")
        self.assertEqual(compare_cohort("q3-n5", curves)["historical_class_rows"], 488)

    def test_full_q7_identity(self):
        curves = fixture_shaped_curves("q7-n3")
        self.assertEqual(compare_cohort("q7-n3", curves)["historical_class_rows"], 690)

    def test_write_once_and_exact_three_cohort_readback(self):
        curves = (fixture_shaped_curves("q5-n3")
                  + fixture_shaped_curves("q7-n3")
                  + fixture_shaped_curves("q3-n5"))
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            summary = write_artifact(root, curves, "a"*64,
                                     {"n3core": "RUN-fixture"})
            self.assertEqual(len(summary["checks"]), 3)
            self.assertTrue(compare_artifact(root, curves, "a"*64,
                                             {"n3core": "RUN-fixture"})["valid"])
            with self.assertRaises(FileExistsError):
                write_artifact(root, curves, "a"*64, {})
            (root / ARTIFACT).write_bytes((root / ARTIFACT).read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "exact readback"):
                compare_artifact(root, curves, "a"*64,
                                 {"n3core": "RUN-fixture"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
