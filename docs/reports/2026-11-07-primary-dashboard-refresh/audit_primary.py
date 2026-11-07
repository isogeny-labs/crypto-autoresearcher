"""Independent small-curve replay and accounting check for the pinned IC rows.

This reads committed cryptanalysis receipts; it does not run the benchmark.
It intentionally implements GF(2^n) and binary-curve group arithmetic here,
instead of importing the producer's arithmetic implementation.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def multiply(a, b, modulus, degree):
    result = 0
    while b:
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & (1 << degree):
            a ^= modulus
    return result


def inverse(a, modulus, degree):
    if not a:
        raise ZeroDivisionError
    result = 1
    exponent = (1 << degree) - 2
    while exponent:
        if exponent & 1:
            result = multiply(result, a, modulus, degree)
        a = multiply(a, a, modulus, degree)
        exponent >>= 1
    return result


def add(p, q, modulus, degree, a2):
    if p is None:
        return q
    if q is None:
        return p
    x1, y1 = p
    x2, y2 = q
    if x1 == x2 and y1 ^ y2 == x1:
        return None
    if x1 == x2:
        if x1 == 0:
            return None
        slope = x1 ^ multiply(y1, inverse(x1, modulus, degree), modulus, degree)
        x3 = multiply(slope, slope, modulus, degree) ^ slope ^ a2
        y3 = multiply(x1, x1, modulus, degree) ^ multiply(slope ^ 1, x3, modulus, degree)
    else:
        slope = multiply(y1 ^ y2, inverse(x1 ^ x2, modulus, degree), modulus, degree)
        x3 = multiply(slope, slope, modulus, degree) ^ slope ^ x1 ^ x2 ^ a2
        y3 = multiply(slope, x1 ^ x3, modulus, degree) ^ x3 ^ y1
    return x3, y3


def scalar_multiply(k, p, modulus, degree, a2):
    result = None
    while k:
        if k & 1:
            result = add(result, p, modulus, degree, a2)
        p = add(p, p, modulus, degree, a2)
        k >>= 1
    return result


def on_curve(p, modulus, degree, a2, a6):
    x, y = p
    m = lambda a, b: multiply(a, b, modulus, degree)
    return m(y, y) ^ m(x, y) == m(m(x, x), x) ^ m(a2, m(x, x)) ^ a6


def audit(source_repo, snapshot_path, export_path, ui_repo):
    archive = source_repo / 'experiments/ic-bench/baseline/primary.jsonl'
    rows = [json.loads(line) for line in archive.read_text().splitlines() if line]
    seen = set()
    results = []
    for i, row in enumerate(rows, 1):
        candidate_id, workload_id = row['candidate_id'], row['workload_id']
        candidate = json.loads((source_repo / 'experiments/ic-bench/candidates' / (candidate_id + '.json')).read_text())
        workload = json.loads((source_repo / 'experiments/ic-bench/workloads' / (workload_id + '.json')).read_text())
        field, curve = candidate['field'], candidate['curve']
        degree = field['degree']
        modulus = sum(1 << e for e in field['modulus_exponents'])
        generator = tuple(curve['generator'])
        order = curve['subgroup_order']
        assert on_curve(generator, modulus, degree, curve['a2'], curve['a6'])
        assert scalar_multiply(order, generator, modulus, degree, curve['a2']) is None
        assert len(workload['targets']) == row['counts']['targets'] == 1
        assert row['counts']['targets_verified'] == 1 and row['verified_scalar'] is True
        assert row['status'] == 'complete' and row['kind'] == 'full_dlp'
        assert row['scalar_certificate_ref'] == row['run_id'] + '#descents'
        assert row['run_id'] == candidate_id + 'W' + workload_id + 'R1'
        assert row['source_curve_ref'] == workload['curve_id'] == curve['curve_id']
        scalar, x, y = workload['targets'][0]
        target = (x, y)
        assert on_curve(target, modulus, degree, curve['a2'], curve['a6'])
        assert scalar_multiply(scalar, generator, modulus, degree, curve['a2']) == target
        assert len(row['descents']) == 1
        descent = row['descents'][0]
        assert descent['verified'] is True and descent['recovered'] is True
        assert descent['scalar'] == scalar
        rho = row['rho_measured']
        assert rho['verified'] is True and rho['scalar'] == scalar
        assert row['total_operations'] == sum(row['phase_operations'].values())
        assert row['online']['ic_online_ns'] == sum(row['online']['phase_wall_ns'].values())
        assert row['online']['overhead_charged_to_target_descent_ns'] <= row['online']['phase_wall_ns']['target_descent']
        assert row['online']['rho_online_ns'] == rho['online_wall_ns']
        assert row['bench_cell'] not in seen
        seen.add(row['bench_cell'])
        results.append({'line': i, 'bench_cell': row['bench_cell'], 'run_id': row['run_id'],
                        'target_scalar': scalar, 'total_operations': row['total_operations'],
                        'ic_online_ns': row['online']['ic_online_ns'],
                        'rho_online_ns': row['online']['rho_online_ns'],
                        'status': row['status']})
    assert len(rows) == 9 and len(seen) == 9
    snapshot = json.loads(snapshot_path.read_text())
    exported = json.loads(export_path.read_text())
    assert len(snapshot['rows']) == len(exported['rows']) == 9
    assert snapshot['source_repository'] == exported['source_repository'] == 'aburan28/cryptanalysis'
    assert snapshot['coverage'] == exported['coverage']
    assert snapshot['identities'] == exported['identities']
    assert set(snapshot['sources']) == set(exported['sources'])
    for path, pin in snapshot['sources'].items():
        assert pin['sha256'] == exported['sources'][path]['sha256']
        committed = subprocess.check_output(['git', '-C', str(source_repo), 'show',
            f"{snapshot['source_commit']}:{path}"])
        assert hashlib.sha256(committed).hexdigest() == pin['sha256']
    for pinned, current in zip(snapshot['rows'], exported['rows']):
        assert pinned['id'] == (snapshot['source_commit'] + ':' + ':'.join(current['id'].split(':')[1:]))
        assert {k: v for k, v in pinned.items() if k != 'id'} == {k: v for k, v in current.items() if k != 'id'}
    digest = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
    catalog = json.loads((ui_repo / 'ui/benchmarks/catalog.json').read_text())
    assert catalog['sha256'] == digest
    receipts = json.loads((ui_repo / 'ui/receipts.json').read_text())
    selected = [r for r in receipts['receipts'] if r.get('adapter') == 'benchmark-snapshot/1']
    assert len(selected) == 9
    for i, selection in enumerate(selected):
        assert selection['snapshot']['sha256'] == digest
        assert selection['row_id'] == snapshot['rows'][i]['id']
    return {'schema': 'primary-ic-audit/1', 'source_archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
            'pinned_source_commit': snapshot['source_commit'], 'current_source_commit': exported['source_commit'],
            'snapshot_sha256': digest, 'source_hashes_equal': True, 'normalized_rows_equal': True,
            'checks': 'nine source rows; independent GF(2^13) point replay; generator order; target, descent and rho scalar; phase sums; receipt identities; pinned/current source hashes; normalized UI rows; catalog and selector pins',
            'rows': results}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-repo', type=Path, required=True)
    parser.add_argument('--ui-repo', type=Path, required=True)
    parser.add_argument('--current-export', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(audit(args.source_repo, args.ui_repo / 'ui/benchmarks/cryptanalysis-primary.json',
                          args.current_export, args.ui_repo), indent=2, sort_keys=True))
