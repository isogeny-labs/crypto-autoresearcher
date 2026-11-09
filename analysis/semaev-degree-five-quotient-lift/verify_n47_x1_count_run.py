#!/usr/bin/env python3
"""Verify custody and exact outputs of the frozen independent n47 x1 count."""
import argparse
import hashlib
import json
from pathlib import Path


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def require_equal(actual, expected, label):
    if actual != expected:
        raise ValueError('%s mismatch' % label)


def polynomial_rem(a, modulus):
    while a and a.bit_length() >= modulus.bit_length():
        a ^= modulus << (a.bit_length() - modulus.bit_length())
    return a


def frobenius_x(n, modulus):
    value = 2
    for _ in range(n):
        square = sum(1 << (2 * j) for j in range(value.bit_length())
                     if value >> j & 1)
        value = polynomial_rem(square, modulus)
    return value


def basis_rank(values):
    pivots = {}
    for value in values:
        while value:
            high = value.bit_length() - 1
            if high in pivots:
                value ^= pivots[high]
            else:
                pivots[high] = value
                break
    return len(pivots)


def check_named_target(plan):
    record = plan['record']
    n = record['n']
    modulus = int(record['modulus_hex'], 16)
    basis = [int(value, 16) for value in record['V_basis_hex']]
    if (record['name'] != 'fresh-n47-rand-00' or n != 47 or
            record['a2'] != 0 or record['k'] != len(basis) or
            record['k'] != 24):
        raise ValueError('named target dimensions mismatch')
    if (modulus != ((1 << 47) | (1 << 5) | 1) or
            frobenius_x(n, modulus) != 2 or
            not modulus & 1 or bin(modulus).count('1') % 2 != 1):
        raise ValueError('named modulus irreducibility check failed')
    if (int(record['z_hex'], 16) == 0 or
            any(value >= (1 << n) or value == 0 for value in basis) or
            basis_rank(basis) != len(basis) or
            any(int(record[key], 16) >= (1 << n)
                for key in ('z_hex', 'a6_hex'))):
        raise ValueError('named field element or factor basis invalid')
    expected = [plan['build_argv'][-1], str(n), record['modulus_hex'],
                record['z_hex'], record['a6_hex'], str(len(basis))]
    expected.extend(record['V_basis_hex'])
    require_equal(plan['target_argv'], expected, 'named target argv')
    wrapper = ['/usr/bin/timeout', str(plan['limits']['target_timeout_seconds']),
               '/usr/bin/prlimit', '--as=%d' % plan['limits']['address_space_bytes'],
               '--']
    require_equal(plan['target_launch_argv'], wrapper + expected,
                  'named target launch argv')


def verified_stream(stage, stream, root):
    rel = Path(stage[stream + '_path'])
    if rel.is_absolute() or '..' in rel.parts:
        raise ValueError('stage output escapes result root')
    path = root / rel
    require_equal(sha256(path), stage[stream + '_sha256'], stream + ' SHA-256')
    return path.read_bytes()


def verify_stage(stage, argv, expected_stdout, root):
    require_equal(stage['argv'], argv, 'stage argv')
    require_equal(stage['exit_code'], 0, 'stage exit code')
    require_equal(verified_stream(stage, 'stdout', root), expected_stdout, 'stage stdout')
    require_equal(verified_stream(stage, 'stderr', root), b'', 'stage stderr')
    return stage['stdout_sha256']


def verify(plan_path, receipt_path, repository, result_root, published_copy=False):
    plan = json.loads(plan_path.read_text())
    receipt = json.loads(receipt_path.read_text())
    require_equal(plan['schema'], 'semaev.n47-rand00-independent-x1-count-plan/v1', 'plan schema')
    require_equal(receipt['schema'], 'semaev.n47-rand00-x1-count-run/v1', 'receipt schema')
    require_equal(receipt['plan_sha256'], sha256(plan_path), 'plan SHA-256')
    require_equal(receipt['attempts'], 1, 'attempt count')
    require_equal(receipt['retries'], 0, 'retry count')
    if not published_copy:
        require_equal(str(result_root), plan['output_root'], 'result root')
    require_equal(sha256(repository / plan['source_path']), plan['source_sha256'], 'source SHA-256')
    require_equal(receipt['source_sha256'], plan['source_sha256'], 'receipt source SHA-256')
    require_equal(sha256(repository / plan['named_plan_path']), plan['named_plan_sha256'], 'named plan SHA-256')
    require_equal(sha256(Path(plan['original_input_system_path'])), plan['input_sys_sha256'],
                  'original input system SHA-256')
    require_equal(json.loads((repository / plan['named_plan_path']).read_text())['record'],
                  plan['record'], 'named instance record')
    check_named_target(plan)
    binary = result_root / 'count_x1' if published_copy else Path(plan['build_argv'][-1])
    require_equal(sha256(binary), receipt['binary_sha256'], 'binary SHA-256')
    build = receipt['build']
    require_equal(build['argv'], plan['build_launch_argv'], 'build argv')
    require_equal(build['exit_code'], 0, 'build exit code')
    verified_stream(build, 'stdout', result_root)
    verified_stream(build, 'stderr', result_root)
    if len(receipt['controls']) != len(plan['controls']):
        raise ValueError('control count mismatch')
    controls = []
    for expected, stage in zip(plan['controls'], receipt['controls']):
        require_equal(stage['id'], expected['id'], 'control id')
        controls.append(verify_stage(stage, expected['launch_argv'],
                                     ('%d\n' % expected['expected_exact_count']).encode(), result_root))
    target_hash = verify_stage(receipt['target'], plan['target_launch_argv'], b'0\n', result_root)
    return {'status': 'accepted_zero_count', 'plan_sha256': receipt['plan_sha256'],
            'binary_sha256': receipt['binary_sha256'], 'control_stdout_sha256': controls,
            'target_stdout_sha256': target_hash, 'named_instance': plan['record']['name']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('receipt', type=Path)
    parser.add_argument('repository', type=Path)
    parser.add_argument('result_root', type=Path)
    parser.add_argument('--published-copy', action='store_true',
                        help='check a byte-for-byte published copy of the run directory')
    args = parser.parse_args()
    print(json.dumps(verify(args.plan, args.receipt, args.repository, args.result_root,
                            published_copy=args.published_copy),
                     sort_keys=True))


if __name__ == '__main__':
    main()
