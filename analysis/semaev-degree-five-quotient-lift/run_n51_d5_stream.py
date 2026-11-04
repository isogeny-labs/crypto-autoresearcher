#!/usr/bin/env python3
"""One frozen n51 D5 trial with retained D4 seed, exact count, and S3 custody.

The result is a named-instance lower bound only when the original checker
accepts the D5 certificate and its codimension exceeds the exact count.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import shutil
import subprocess
import sys
import time
import traceback
import urllib.request

import stream_certificate_custody as custody


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    temporary = path.with_suffix(path.suffix + '.partial')
    with temporary.open('x') as output:
        json.dump(value, output, sort_keys=True, indent=2)
        output.write('\n')
        output.flush()
        os.fsync(output.fileno())
    os.replace(temporary, path)


def upload(path, out, target):
    if target:
        suffix = str(path.relative_to(out))
        subprocess.run(['aws', 's3', 'cp', str(path), target + '/d5-run/' + suffix,
                        '--only-show-errors', '--no-overwrite'], check=True, timeout=1200)


def stage(label, argv, out, target, timeout, memory_bytes):
    stdout = out / (label + '.stdout.txt')
    stderr = out / (label + '.stderr.txt')
    def cap():
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
    began = time.monotonic()
    timed_out = False
    returncode = None
    with stdout.open('xb') as a, stderr.open('xb') as b:
        try:
            child = subprocess.run(list(map(str, argv)), stdout=a, stderr=b,
                                   timeout=timeout, preexec_fn=cap)
            returncode = child.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
    record = dict(label=label, argv=list(map(str, argv)), returncode=returncode,
                  timed_out=timed_out,
                  elapsed_seconds=time.monotonic() - began, wall_valid=False,
                  stdout_sha256=sha(stdout), stderr_sha256=sha(stderr))
    path = out / (label + '.json')
    save(path, record)
    for file in (stdout, stderr, path):
        upload(file, out, target)
    if timed_out or returncode:
        raise RuntimeError(label + ' timed out' if timed_out else
                           label + ' returned ' + str(returncode))
    return stdout.read_text()


def validate_request(request, bundle, source):
    if request.get('schema') != 'semaev.streamed-d5-trial-request/v1' or request.get('status') != 'frozen':
        raise ValueError('frozen D5 trial request required')
    record = request['record']
    if record['n'] != 51 or len(record['V_basis_hex']) != 26 or request['expected_exact_solutions'] != 0:
        raise ValueError('request differs from frozen n51 polynomial-01 presentation')
    instruments = request['instruments']
    for name, digest in [('quotient_lift_bounded_stream', instruments['producer_binary_sha256']),
                         ('cert_check.py', instruments['checker_sha256']),
                         ('count_by_sum', instruments['counter_sha256']),
                         ('stream_certificate_custody.py', instruments['transport_sha256'])]:
        if sha(bundle / name) != digest:
            raise ValueError('instrument identity mismatch: ' + name)
    if sha(source) != instruments['runner_sha256']:
        raise ValueError('runner identity mismatch')
    expected = 32 + 8 * request['profile']['next_degree_columns'] * (1 +
               (request['profile']['working_coordinates'] + 63) // 64)
    if expected != request['limits']['certificate_max_bytes'] or expected > 50_000_000_000:
        raise ValueError('D5 certificate ceiling mismatch')
    if request['limits']['producer_memory_bytes'] >= request['limits']['pod_memory_bytes']:
        raise ValueError('producer cap must leave pod headroom')
    seed = request['seed']
    if (sha(bundle / 'prior-result.json') != seed['prior_result_sha256'] or
            sha(bundle / 'publication-ack.json') != seed['publication_ack_sha256'] or
            sha(bundle / 'panel-plan.json') != seed['source_panel_plan_sha256'] or
            sha(bundle / 'profile.json') != request['profile']['sha256']):
        raise ValueError('published predecessor or D5 profile identity mismatch')
    prior = json.loads((bundle / 'prior-result.json').read_text())
    ack = json.loads((bundle / 'publication-ack.json').read_text())
    panel = json.loads((bundle / 'panel-plan.json').read_text())
    profile = json.loads((bundle / 'profile.json').read_text())
    selected = [item for item in panel['items'] if item['id'] == prior['id']]
    certs = [item for item in ack['files'] if item['name'].endswith('.D4.cert.gz')]
    if (len(selected) != 1 or selected[0]['record'] != record or
            sha(bundle / 'panel-plan.json') != prior['plan_sha256'] or
            prior['status'] != 'certificate_verified' or
            prior['exact_solutions'] != request['expected_exact_solutions'] or
            [item['degree'] for item in prior['stages']] != [3, 4] or
            prior['stages'][1]['certificate_sha256'] != seed['raw_sha256'] or
            prior['stages'][1]['certified_codimension'] != request['seed_codimension'] or
            ack['id'] != prior['id'] or ack['certificate_sha256'] != seed['raw_sha256'] or
            len(certs) != 1 or certs[0]['sha256'] != seed['compressed_sha256'] or
            certs[0]['bytes'] != seed['compressed_bytes'] or
            certs[0]['store_uri'] != seed['compressed_uri'] or
            certs[0]['anonymous_url'] != seed['compressed_url'] or
            profile['working_coordinates'] != request['profile']['working_coordinates'] or
            profile['next_degree_columns'] != request['profile']['next_degree_columns'] or
            profile['native_envelopes']['60000']['envelope_bytes'] !=
                request['profile']['bounded_native_envelope_bytes']):
        raise ValueError('published predecessor, selected input, or profile differs from trial request')


def receive_seed(request, out, target):
    spec = request['seed']
    compressed = out / 'seed-D4.bin.gz'
    raw = out / 'seed-D4.bin'
    compressed_hash = hashlib.sha256()
    compressed_total = 0
    began = time.monotonic()
    with urllib.request.urlopen(spec['compressed_url'], timeout=120) as source, compressed.open('xb') as output:
        for block in iter(lambda: source.read(1 << 20), b''):
            compressed_total += len(block)
            if (compressed_total > spec['compressed_bytes'] or
                    time.monotonic() - began > request['limits']['seed_transfer_timeout_seconds']):
                raise ValueError('compressed D4 seed transfer exceeded frozen limit')
            compressed_hash.update(block)
            output.write(block)
        output.flush()
        os.fsync(output.fileno())
    if (compressed_total != spec['compressed_bytes'] or
            compressed_hash.hexdigest() != spec['compressed_sha256']):
        raise ValueError('compressed D4 seed identity mismatch')
    digest = hashlib.sha256()
    total = 0
    with gzip.open(compressed, 'rb') as source, raw.open('xb') as output:
        for block in iter(lambda: source.read(1 << 20), b''):
            total += len(block)
            if total > spec['raw_bytes']:
                raise ValueError('D4 seed decompressed beyond frozen size')
            digest.update(block)
            output.write(block)
        output.flush()
        os.fsync(output.fileno())
    if total != spec['raw_bytes'] or digest.hexdigest() != spec['raw_sha256']:
        raise ValueError('raw D4 seed identity mismatch')
    compressed.unlink()
    receipt = dict(compressed_url=spec['compressed_url'], compressed_uri=spec['compressed_uri'],
                   compressed_bytes=spec['compressed_bytes'],
                   compressed_sha256=spec['compressed_sha256'], raw_bytes=total,
                   raw_sha256=digest.hexdigest())
    save(out / 'seed.json', receipt)
    upload(out / 'seed.json', out, target)
    return raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--request', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--upload', action='store_true')
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    bundle = args.bundle.resolve()
    request = json.loads(args.request.read_text())
    target = os.environ['ISOLAB_RESULTS_URI'].rstrip('/') if args.upload else None
    started = time.monotonic()
    result = dict(schema='semaev.streamed-d5-trial-result/v1', id=request.get('id'),
                  request_sha256=sha(args.request), status='started', wall_valid=False)
    try:
        validate_request(request, bundle, Path(__file__))
        if target is None:
            raise ValueError('durable assigned S3 result prefix required for frontier trial')
        limit = Path('/sys/fs/cgroup/memory.max').read_text().strip()
        if not limit.isdigit() or int(limit) < request['limits']['pod_memory_bytes']:
            raise ValueError('pod cgroup memory admission refused')
        disk = shutil.disk_usage(out)
        seed = request['seed']
        needed = seed['compressed_bytes'] + seed['raw_bytes'] + request['limits']['ephemeral_reserve_bytes']
        if disk.free < needed:
            raise ValueError('pod disk admission refused')
        environment = dict(cgroup_memory_bytes=int(limit), disk_free_bytes=disk.free,
                           required_seed_and_reserve_bytes=needed, results_uri=target)
        save(out / 'environment.json', environment)
        upload(out / 'environment.json', out, target)
        raw = receive_seed(request, out, target)
        record = request['record']
        basis = record['V_basis_hex']
        checker = bundle / 'cert_check.py'
        common = [str(record['n']), record['modulus_hex'], str(record['a2']),
                  record['a6_hex'], record['z_hex'], *basis]
        check4 = stage('check4', [sys.executable, checker, raw, *common], out, target,
                       request['limits']['seed_check_timeout_seconds'], 32 << 30)
        match = re.search(r'VALID: 1 is not in W_4\(F\), and codim W_4\(F\) >= (\d+)', check4)
        if not match or int(match[1]) != request['seed_codimension']:
            raise ValueError('retained D4 seed did not independently recheck')
        count_argv = [bundle / 'count_by_sum', record['n'], record['modulus_hex'],
                      record['z_hex'], record['a6_hex'], len(basis), *basis]
        count_text = stage('count', count_argv, out, target,
                           request['limits']['count_timeout_seconds'], 1 << 30)
        count = int(count_text.strip())
        if count != request['expected_exact_solutions']:
            raise ValueError('fresh exact count differs from frozen request')
        limits = request['limits']
        binary = bundle / 'quotient_lift_bounded_stream'
        transport_plan = dict(schema='semaev.streamed-certificate-custody/v1',
            id=request['id'],
            producer_identity=dict(path=str(binary), sha256=sha(binary)),
            checker_identity=dict(path=str(checker), sha256=sha(checker)),
            producer_argv=[str(binary), str(raw), '-', str(limits['chunk_rows']),
                           str(limits['producer_memory_bytes'])],
            checker_argv=[sys.executable, str(checker), '/dev/stdin', *common],
            inputs=[dict(path=str(raw), producer_argv_index=1,
                         bytes=seed['raw_bytes'], sha256=seed['raw_sha256'])],
            max_certificate_bytes=limits['certificate_max_bytes'],
            timeout_seconds=limits['producer_and_upload_timeout_seconds'],
            upload_timeout_seconds=limits['upload_timeout_seconds'],
            checker_timeout_seconds=limits['checker_timeout_seconds'])
        save(out / 'transport-plan.json', transport_plan)
        upload(out / 'transport-plan.json', out, target)
        checked = custody.transfer(transport_plan, out / 'transport', sha(out / 'transport-plan.json'))
        for file in sorted((out / 'transport').iterdir()):
            if file.is_file():
                upload(file, out, target)
        codim = checked['steps']['checker']['codimension']
        result.update(status='certificate_verified', exact_solutions=count,
                      checked_codimension=codim,
                      last_fall_degree_lower_bound=6 if codim > count else None,
                      certificate_sha256=checked['steps']['readback']['sha256'],
                      certificate_bytes=checked['steps']['readback']['bytes'],
                      certificate_uri=checked['target'])
    except Exception as error:
        result.update(status='failed', error=repr(error), traceback=traceback.format_exc())
    result['elapsed_seconds'] = time.monotonic() - started
    save(out / 'result.json', result)
    upload(out / 'result.json', out, target)
    print(json.dumps(result), flush=True)
    return 0 if result['status'] == 'certificate_verified' else 1


if __name__ == '__main__':
    raise SystemExit(main())
