#!/usr/bin/env python3
"""Source checks and read-only budget diagnostics. This command never submits work."""
from pathlib import Path
from decimal import Decimal
import argparse
import ast
import datetime
import hashlib
import json
import math
import subprocess

import study

HERE = Path(__file__).resolve().parent
ACCOUNT = '104186811093'
BUDGETS = ('isolab-daily-cost-100', 'spot-experiments-daily-25',
           'isolab-monthly-account-cost')


def source_check():
    study.validate_profile(json.loads((HERE/'cohort-profile.json').read_text()))
    manifest = json.loads((HERE/'source-manifest.json').read_text())
    expected = {p.relative_to(HERE).as_posix() for p in HERE.rglob('*')
                if p.is_file() and (p.suffix == '.py' or p.suffix == '.json' and 'verification' not in p.relative_to(HERE).parts)
                and p.name != 'source-manifest.json' and '__pycache__' not in p.parts}
    if set(manifest['sources']) != expected:
        raise ValueError('source manifest membership differs')
    for name, entry in manifest['sources'].items():
        p = HERE/name
        if not p.resolve().is_relative_to(HERE) or p.is_symlink():
            raise ValueError('unsafe source-manifest path')
        raw = p.read_bytes()
        if len(raw) != entry['bytes'] or hashlib.sha256(raw).hexdigest() != entry['sha256']:
            raise ValueError('source digest differs: '+name)
        if p.suffix == '.py':
            ast.parse(raw, filename=name)
    return {'source_checks_pass': True, 'source_files': len(manifest['sources']),
            'geometry': study.GEOMETRY, 'workload': study.FULL,
            'scientific_draws': 0, 'execution_ready': False,
            'remaining_admission': ['protected main synchronization',
              'independent source review', 'frozen protocol and native trial plan',
              'fresh exclusions and post-freeze nonce',
              'live budget/lane reservations and isolated placement',
              'native preapproval, ownership, publication and checkpoint']}


def budget_check(aws, attempt_usd, run=subprocess.run):
    if not math.isfinite(attempt_usd) or not 0 < attempt_usd <= 15:
        raise ValueError('proposed preparation allowance must be positive and at most USD15')
    records = []
    def call(args):
        argv = [aws, '--region', 'us-east-2', '--cli-connect-timeout', '10',
                '--cli-read-timeout', '20', *args, '--output', 'json']
        r = run(argv, capture_output=True, text=True, timeout=40)
        # Record error classes, never credential values or the inherited environment.
        records.append({'argv': argv, 'returncode': r.returncode,
                        'error_code': 'AccessDenied' if 'AccessDenied' in r.stderr else
                                      'remote_error' if r.returncode else None})
        return json.loads(r.stdout) if r.returncode == 0 else None
    identity = call(['sts', 'get-caller-identity'])
    result = {'observed_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'expected_account': ACCOUNT, 'read_only': True, 'jobs_submitted': 0,
              'execution_ready': False, 'commands': records, 'budgets': []}
    if identity is None or identity.get('Account') != ACCOUNT:
        result['blocker'] = 'authorized account identity unavailable or different'
        return result
    for name in BUDGETS:
        value = call(['budgets', 'describe-budget', '--account-id', ACCOUNT,
                      '--budget-name', name])
        if value is None:
            result['budgets'].append({'name': name, 'readable': False})
            continue
        b = value['Budget']
        def money(item):
            amount = Decimal(item['Amount'])
            if item['Unit'] != 'USD' or not amount.is_finite() or amount < 0:
                raise ValueError('finite nonnegative USD budget required')
            return amount
        limit = money(b['BudgetLimit'])
        spending = b['CalculatedSpend']
        used = money(spending['ActualSpend'])
        forecast = money(spending.get('ForecastedSpend', spending['ActualSpend']))
        policy_ceiling = Decimal(1000 if name == BUDGETS[-1] else 200)
        remainder = min(limit, policy_ceiling) - max(used, forecast)
        result['budgets'].append({'name': name, 'readable': True,
           'reported_limit_usd': str(limit), 'actual_usd': str(used),
           'forecast_usd': str(forecast), 'conservative_remainder_usd': str(remainder),
           'covers_proposed_allowance_before_lane_reservations': remainder >= Decimal(str(attempt_usd))})
    result['blocker'] = ('live budget unreadable' if not all(b['readable'] for b in result['budgets'])
                         else 'lane reservations, placement and native admission still required')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['check', 'budget'])
    parser.add_argument('--aws', default='aws')
    parser.add_argument('--attempt-usd', type=float, default=15)
    args = parser.parse_args()
    try:
        result = source_check() if args.action == 'check' else budget_check(args.aws, args.attempt_usd)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(json.dumps({'execution_ready': False, 'error': str(exc), 'jobs_submitted': 0}))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if args.action == 'check' else 2


if __name__ == '__main__':
    raise SystemExit(main())
