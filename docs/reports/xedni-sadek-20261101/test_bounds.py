"""Software controls only: no curve search, timing claim, or theorem certification."""
import ast
from pathlib import Path
import unittest


def degree_expression(base, rank, exponent):
    if any(type(x) is not int for x in (base, rank, exponent)):
        raise TypeError("integer parameters required")
    if base < 2 or rank < 1 or exponent < 1:
        raise ValueError("require base>=2, rank>=1, exponent>=1")
    return (base**2 - 1) * (base**2 - base) * base**(2*(exponent+1)*rank + 4*exponent)


def majorant(ell, rank, exponent, bound, max_exponent):
    left = degree_expression(ell, rank, exponent)
    right = degree_expression(bound, rank, max_exponent)
    if ell > bound or exponent > max_exponent:
        raise ValueError("conditional domination hypotheses not met")
    return left, right


class BoundsTests(unittest.TestCase):
    def test_prime_coefficient_counterexample(self):
        n, ell, bound = 3, 3, 3
        self.assertEqual(n % ell, 0)
        self.assertLessEqual(abs(n), bound)
        self.assertGreater(ell*ell, bound)

    def test_tight_boundary(self):
        left, right = majorant(3, 1, 2, 3, 2)
        self.assertEqual(left, right)
        self.assertEqual(left, 48 * 3**14)

    def test_strict_domination(self):
        left, right = majorant(3, 2, 1, 7, 3)
        self.assertEqual(left, 48 * 3**12)
        self.assertEqual(right, 2016 * 7**28)
        self.assertLess(left, right)

    def test_invalid_domain(self):
        for args in [(1,1,1), (2,0,1), (2,1,0), (-2,1,1)]:
            with self.assertRaises(ValueError):
                degree_expression(*args)
        with self.assertRaises(TypeError):
            degree_expression(2, 1, 1.5)
        for args in [(7,1,1,3,2), (3,1,3,7,2)]:
            with self.assertRaises(ValueError):
                majorant(*args)

    def test_imported_fixture(self):
        data = ast.literal_eval(Path(__file__).with_name('prior-output.txt').read_text())
        self.assertEqual(data['prime_divisor_pairs'], 20)
        self.assertEqual(data['failed_linear_bound'], [])
        self.assertEqual(data['failed_sqrt_bound'],
                         [(2,2),(3,3),(5,5),(6,3),(7,7),(10,5),(11,11),(13,13),(14,7),(15,5)])


if __name__ == '__main__':
    unittest.main(verbosity=2)
