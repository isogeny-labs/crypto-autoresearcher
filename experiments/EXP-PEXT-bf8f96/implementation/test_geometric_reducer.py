"""Geometric reducer arithmetic on two fixed F27 software units."""

import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from geometric_reducer import (curve_summary, expected_pattern,
                               genus_from_rank_and_support, unit_summary)


class GeometricReducerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-geometric-reducer-")
        source = Path(__file__).parent / "candidate_unit.rs"
        binary = Path(cls.scratch.name) / "candidate_unit"
        subprocess.run(["rustc", "--edition=2021", str(source), "-o", str(binary)],
                       check=True, capture_output=True)
        cls.units = []
        for form in ([1, 0, 1, 1, 0], [1, 1, 1, 0, 1]):
            args = [str(binary), "3", "3", ",".join(map(str, form)),
                    "27", "819", "3276", "1000", "1000", "819"]
            cls.units.append(json.loads(subprocess.check_output(args)))

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def summarize(self, index, unit=None):
        return unit_summary(self.units[index] if unit is None else unit, n=3,
                            target_count=2, t_index=index, expected_structures=819)

    def test_pattern_contract_and_rh(self):
        self.assertEqual([expected_pattern(count, index) for count, index in
                          ((1, 0), (2, 0), (2, 1), (4, 0), (4, 1))],
                         [[1, 3], [1, 1, 2], [4], [1, 1, 1, 1], [2, 2]])
        self.assertEqual(genus_from_rank_and_support(3, 12), 17)
        with self.assertRaisesRegex(ValueError, "nonintegral"):
            genus_from_rank_and_support(1, 5)

    def test_f27_spectrum_and_curve_matched_minima(self):
        first, second = self.summarize(0), self.summarize(1)
        self.assertEqual(first["factor_pattern"], [1, 1, 2])
        self.assertEqual(second["factor_pattern"], [4])
        self.assertEqual(first["spectrum"], [1, 9, 11, 13, 17])
        self.assertEqual(second["spectrum"], [1, 17])
        self.assertIsNone(first["geometric_spectrum_violation_count"])
        self.assertEqual(second["geometric_spectrum_violation_count"], 0)
        self.assertEqual((first["exceptional"], second["exceptional"]), (279, 1))
        first["T_index"], second["T_index"] = 0, 1
        curve = curve_summary("f27-software-fixture", 0, [0, 0], [first, second])
        self.assertEqual((curve["xline_geometric_minimum"],
                          curve["all_maps_geometric_minimum"]), (1, 1))
        self.assertFalse(curve["strict_geometric_minimum_drop"])

    def test_mutations_and_missing_t_refused(self):
        bad = copy.deepcopy(self.units[1])
        bad["rows"][0][4] += 1
        with self.assertRaisesRegex(ValueError, "Riemann-Hurwitz"):
            self.summarize(1, bad)
        bad = copy.deepcopy(self.units[0])
        bad["generic_intervals"][0][1] += 1
        with self.assertRaisesRegex(ValueError, "generic complement"):
            self.summarize(0, bad)
        bad = copy.deepcopy(self.units[1])
        bad["factor_pattern"] = [2, 2]
        self.assertEqual(self.summarize(1, bad)["branch_type_mismatch_count"], 1)
        first = self.summarize(0)
        first["T_index"] = 0
        with self.assertRaisesRegex(ValueError, "incomplete canonical T"):
            curve_summary("f27-software-fixture", 0, [0, 0], [first, first])


if __name__ == "__main__":
    unittest.main(verbosity=2)
