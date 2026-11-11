#!/usr/bin/env python3
"""Admission and parser controls for the one-attempt n51 direct-rank runner."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_n51_poly00_sliced_w4 import budget_readback, parse_stdout, preflight


class N51W4RunnerTests(unittest.TestCase):
    def test_pending_authorization_refuses_before_side_effects(self):
        with self.assertRaisesRegex(RuntimeError, 'authorization'):
            preflight({'output_root': '/unused'}, {
                'authorization_status': 'pending', 'authorization_note': None,
                'external_jobs_reconciliation': None}, 'published')

    def test_stdout_requires_single_complete_rank_line(self):
        line = 'W4_dims 0 1 2 3 226437 W4_one 0 iters 3 ncols 272052'
        self.assertEqual(parse_stdout(line, 272052)['rank'], 226437)
        for invalid in (line + '\n' + line, line.replace('272052', '272053'),
                        line.replace('226437', '1'), 'W4_dims 0 1'):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                parse_stdout(invalid, 272052)

    def test_budget_headroom_and_exact_live_limits(self):
        budgets = []
        for name, period, limit, actual in (
                ('isolab-monthly-account-cost', 'MONTHLY', '1300', '1360.114'),
                ('isolab-daily-cost-100', 'DAILY', '200', '10'),
                ('spot-experiments-daily-25', 'DAILY', '200', '10')):
            budgets.append({'BudgetName': name, 'BudgetType': 'COST',
                            'TimeUnit': period, 'BudgetLimit': {'Amount': limit, 'Unit': 'USD'},
                            'CalculatedSpend': {'ActualSpend': {'Amount': actual, 'Unit': 'USD'}}})

        def fake_check_output(argv, **kwargs):
            if argv[1] == 'sts':
                return json.dumps({'Account': '123'})
            return json.dumps({'Budgets': budgets})

        with patch('run_n51_poly00_sliced_w4.subprocess.check_output',
                   side_effect=fake_check_output):
            with self.assertRaisesRegex(RuntimeError, 'monthly'):
                budget_readback(Decimal('15'), Decimal('0'), Decimal('1300'))
            budgets[0]['CalculatedSpend']['ActualSpend']['Amount'] = '1270'
            result = budget_readback(Decimal('15'), Decimal('0'), Decimal('1300'))
            self.assertEqual(set(result), {b['BudgetName'] for b in budgets})
            with self.assertRaisesRegex(RuntimeError, 'monthly'):
                budget_readback(Decimal('15'), Decimal('20'), Decimal('1300'))


if __name__ == '__main__':
    unittest.main()
