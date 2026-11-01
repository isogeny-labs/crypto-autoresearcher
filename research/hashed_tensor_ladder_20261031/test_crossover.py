import math
import unittest

import crossover as c


class CrossoverTests(unittest.TestCase):
    def test_minimum_at_m4(self):
        self.assertEqual(c.best_m(), 4)
        self.assertAlmostEqual(c.sqrt_threshold(4), 16.0)
        self.assertAlmostEqual(c.min_log2_ell(4), 254.0)

    def test_values(self):
        self.assertAlmostEqual(c.sqrt_threshold(3), 18.0)
        self.assertAlmostEqual(c.sqrt_threshold(6), 18.0)
        self.assertAlmostEqual(c.sqrt_threshold(8), 128 / 6)

    def test_m2_rejected(self):
        with self.assertRaises(ValueError):
            c.sqrt_threshold(2)

    def test_boundary(self):
        m = 4
        self.assertFalse(c.beats_rho_unit_constants(253.9, m))
        self.assertTrue(c.beats_rho_unit_constants(254.1, m))
        for log2_ell in (6.3, 17, 64, 200):
            self.assertFalse(c.beats_rho_unit_constants(log2_ell, m))

    def test_matches_direct_inequality(self):
        # direct form m*ell/sqrt(log2(m*ell)) < (1/2 - 1/m)*ell, valid for ell small enough to represent
        for m in (3, 4, 5, 8):
            for log2_ell in (10, 100, 300, 600):
                ell = 2.0 ** log2_ell
                direct = m * ell / math.sqrt(math.log2(m * ell)) < (0.5 - 1.0 / m) * ell
                self.assertEqual(direct, c.beats_rho_unit_constants(log2_ell, m), (m, log2_ell))


if __name__ == "__main__":
    unittest.main()
