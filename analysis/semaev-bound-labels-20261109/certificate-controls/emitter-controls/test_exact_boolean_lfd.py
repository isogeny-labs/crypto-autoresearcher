import unittest
from unittest.mock import patch
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


    def test_certificate_provenance_and_determinism(self):
        equations = [[3, 1], [3]]
        result = analyze(3, equations, 1_000_000, include_certificate=True)
        self.assertEqual(result['status'], 'complete')
        cert = result['certificate']
        self.assertEqual(cert['schema'], 'strict-boolean-lfd-certificate/v1')
        self.assertEqual(cert['equations'], equations)
        self.assertEqual(len(cert['caps']), 5)
        saw_product = False
        for cap in cert['caps']:
            previous = []
            pivots = set()
            for index, item in enumerate(cap['basis']):
                source = item['source']
                if 'input' in source:
                    row = set(equations[source['input']])
                else:
                    saw_product = True
                    self.assertLess(source['parent'], index)
                    parent = previous[source['parent']]
                    self.assertTrue(all(bin(m).count('1') < cap['cap']
                                        for m in parent))
                    row = set()
                    for m in parent:
                        term = m | (1 << source['variable'])
                        row.symmetric_difference_update({term})
                for prior in item['reductions']:
                    self.assertLess(prior, index)
                    row.symmetric_difference_update(previous[prior])
                self.assertEqual(item['row'], sorted(row))
                self.assertTrue(row)
                pivot = min(row, key=lambda m: (-bin(m).count('1'), m))
                self.assertNotIn(pivot, pivots)
                pivots.add(pivot)
                previous.append(row)
        self.assertTrue(saw_product)
        second = analyze(3, equations, 1_000_000, include_certificate=True)
        self.assertEqual(cert, second['certificate'])
        plain = analyze(3, equations, 1_000_000)
        self.assertNotIn('certificate', plain)
        self.assertEqual(result['exact_lfd'], plain['exact_lfd'])
        self.assertGreater(result['operations_used'], plain['operations_used'])
        self.assertFalse(result['independently_checked_certificate'])

    def test_certificate_exhaustion_emits_no_partial_trace(self):
        result = analyze(2, [[3]], 1, include_certificate=True)
        self.assertIsNone(result['certificate'])
        self.assertIsNone(result['exact_lfd'])
        self.assertEqual(result['status'], 'budget_exhausted')
        with patch('exact_boolean_lfd.MAX_TRACE_ENTRIES', 8):
            result = analyze(3, [[3, 1], [3]], 1_000_000,
                             include_certificate=True)
        self.assertEqual(result['exhaustion_reason'], 'trace_entry_limit')
        self.assertEqual(result['status'], 'budget_exhausted')
        self.assertIsNone(result['certificate'])
        self.assertIsNone(result['exact_lfd'])
        self.assertLessEqual(result['trace_entries_charged'], 8)
        with self.assertRaises(ValueError):
            analyze(1, [], 100, include_certificate=1)


if __name__ == '__main__':
    unittest.main()
