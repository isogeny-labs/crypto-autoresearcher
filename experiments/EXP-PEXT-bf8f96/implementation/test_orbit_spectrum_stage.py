"""Focused algebra and custody checks for the planned orbit stage."""

import json
from pathlib import Path
import tempfile
import unittest

from orbit_spectrum_stage import (compare_donor, compare_exact, enumerate_spectrum, placements,
                                  polynomial_rank, shift_rank, write_once)


class OrbitSpectrumStageTests(unittest.TestCase):
    def test_rank_methods_agree_with_known_cyclic_subspaces(self):
        self.assertEqual(polynomial_rank(3, [0b111]), 1)
        self.assertEqual(shift_rank(3, [0b111]), 1)
        self.assertEqual(polynomial_rank(3, [0b011]), 2)
        self.assertEqual(shift_rank(3, [0b011]), 2)
        self.assertEqual(polynomial_rank(5, [0b11111, 0b00011]), 5)
        self.assertEqual(shift_rank(5, [0b11111, 0b00011]), 5)

    def test_n3_abstract_spectrum_and_hash_are_deterministic(self):
        first = enumerate_spectrum((3,))
        second = enumerate_spectrum((3,))
        self.assertEqual(first, second)
        self.assertEqual([row["type"] for row in first["cases"]],
                         ["split", "Z2", "odd"])
        for row in first["cases"]:
            self.assertGreater(row["placement_count"], 0)
            self.assertEqual(sum(pair["count"] for pair in row["m_r"]),
                             row["placement_count"])
            self.assertEqual(len(row["placement_stream_sha256"]), 64)
        self.assertEqual(first["status"],
                         "abstract_placements_checked; realization_unasserted")

    def test_short_orbits_restricted_by_degree(self):
        self.assertTrue(all(-1 not in labels for labels, _, _, _
                            in placements(3, (3,))))

    def test_write_once_preserves_first_attempt(self):
        with tempfile.TemporaryDirectory() as scratch:
            path = Path(scratch) / "orbits.json"
            digest = write_once(path, {"sample": 1})
            original = path.read_bytes()
            self.assertEqual(len(digest), 64)
            self.assertEqual(json.loads(original), {"sample": 1})
            with self.assertRaises(FileExistsError):
                write_once(path, {"sample": 2})
            self.assertEqual(path.read_bytes(), original)

    def test_exact_readback_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as scratch:
            path = Path(scratch) / "orbits.json"
            value = enumerate_spectrum((3,))
            digest = write_once(path, value)
            self.assertEqual(compare_exact(path, (3,)), digest)
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "exact recomputation"):
                compare_exact(path, (3,))

    def test_all_n3_n5_n7_sets_match_prior_derivation(self):
        spectrum = enumerate_spectrum()
        self.assertEqual(sum(row["placement_count"] for row in spectrum["cases"]),
                         43872)
        self.assertEqual(compare_donor(spectrum)["cases_matched"], 9)
        spectrum["cases"][0]["m_r"][0]["m"] += 1
        with self.assertRaisesRegex(ValueError, "pinned derivation aid"):
            compare_donor(spectrum)


if __name__ == "__main__":
    unittest.main(verbosity=2)
