import unittest
from exact_boolean_lfd import analyze


class ExactBooleanLfdTests(unittest.TestCase):
    def check(self, n, rows, degree, zeros):
        result = analyze(n, rows, 1_000_000)
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(result['exact_lfd'], degree)
        self.assertEqual(result['zero_count'], zeros)
        self.assertEqual(len(result['caps']), n + 2)
        self.assertEqual(result['operations_used'],
                         sum(result['operation_counters'].values()))
        self.assertFalse(result['dataset_admission'])
        return result

    def test_linear_no_fall(self):
        self.check(1, [[1]], 0, 1)

    def test_affine_unsat_fall_one(self):
        self.check(1, [[1], [0, 1]], 1, 0)

    def test_quadratic_unsat_fall_two(self):
        self.check(2, [[3, 1], [3, 1, 0], [3]], 2, 0)

    def test_genuine_feedback(self):
        # xy+x and xy imply x; multiplying new x by z supplies xz.
        result = self.check(3, [[3, 1], [3]], 2, 4)
        cap2 = result['caps'][2]
        self.assertEqual(cap2['closure_rank'], 3)  # x, xy, xz
        self.assertFalse(cap2['missing_ideal_consequence'])

    def test_zero_and_constant_systems(self):
        self.check(0, [], 0, 1)
        self.check(0, [[0]], 0, 0)
        self.check(2, [[]], 0, 4)
        self.check(2, [[3]], 0, 3)

    def test_mixed_degree_input_cap(self):
        result = self.check(2, [[1], [0, 3]], 2, 0)
        self.assertEqual(result['caps'][1]['closure_rank'], 1)

    def test_budget_exhaustion_is_unlabeled(self):
        result = analyze(3, [[3, 1], [3]], 1)
        self.assertEqual(result['status'], 'budget_exhausted')
        self.assertIsNone(result['exact_lfd'])
        self.assertLessEqual(result['operations_used'], 1)
        complete = self.check(2, [[3, 1], [3]], 2, 2)
        partial = analyze(2, [[3, 1], [3]], complete['operations_used'] - 1)
        self.assertEqual(partial['status'], 'budget_exhausted')
        self.assertIsNone(partial['exact_lfd'])
        self.assertTrue(partial['caps'])

    def test_budgets_cover_evaluation_and_columns(self):
        result = self.check(2, [[3]], 0, 3)
        counters = result['operation_counters']
        for name in ('polynomial_eval_term', 'evaluation_column_test',
                     'cap_column_generation', 'monomial_generation',
                     'closure_row_xor_bits'):
            self.assertGreater(counters[name], 0)

    def test_invalid_inputs(self):
        bad = [(13, []), (-1, []), (True, []), (2, [[4]]),
               (2, [[1, 1]]), (2, [[True]]), (2, [(1,)])]
        for n, rows in bad:
            with self.assertRaises(ValueError):
                analyze(n, rows, 1000)
        for limit in (0, True, 100_000_001):
            with self.assertRaises(ValueError):
                analyze(1, [], limit)


if __name__ == '__main__':
    unittest.main()
