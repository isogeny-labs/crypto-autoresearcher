#!/usr/bin/env python3
"""Two fresh public-only certificate searches; native checker runs afterward."""
import argparse
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import traceback


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def decode(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate key: ' + key)
            result[key] = value
        return result
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique)


def digest_file(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_once(path, document):
    raw = (json.dumps(document, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()
    with path.open('xb') as stream:
        stream.write(raw)
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


def child_limits(cpu_seconds):
    resource.setrlimit(resource.RLIMIT_AS, (3 << 30, 3 << 30))
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
    if hasattr(os, 'sched_getaffinity'):
        available = sorted(os.sched_getaffinity(0))
        os.sched_setaffinity(0, set(available[:2]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--input-manifest', required=True, type=Path)
    parser.add_argument('--time-limit', type=int, default=1200)
    args = parser.parse_args()
    if not 1 <= args.time_limit <= 1200:
        raise ValueError('watchdog must respect frozen maximum1200s')
    root, out = args.repo_root.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    # Reserve address space for the parent/control plane in addition to the
    # one sequential3GiB child. No worker is detached from the native group.
    resource.setrlimit(resource.RLIMIT_AS, (512 << 20, 4 << 30))
    resource.setrlimit(resource.RLIMIT_CPU, (1800, 1800))
    if hasattr(os, 'sched_getaffinity'):
        os.sched_setaffinity(0, set(sorted(os.sched_getaffinity(0))[:2]))
    if os.getpgrp() != os.getpid():
        raise ValueError('native supervisor must provide a fresh process group')
    native_launch_raw = (out / 'launch.json').read_bytes()
    native_environment_raw = (out / 'environment.json').read_bytes()
    native_launch = decode(native_launch_raw)
    beginning = time.monotonic()
    stop = beginning + args.time_limit
    manifest_path = args.input_manifest if args.input_manifest.is_absolute() else root / args.input_manifest
    manifest_raw = manifest_path.read_bytes()
    manifest = decode(manifest_raw)
    binding = manifest['inputs'][0]
    public = Path(binding['local_readonly_absolute_path'])
    if public.stat().st_size != binding['payload_bytes'] or digest_file(public) != binding['payload_sha256']:
        raise ValueError('public input immutable identity mismatch')
    # Merely locate the other bindings: no candidate data is opened by this process.
    if len(manifest['inputs']) != 3:
        raise ValueError('input manifest must have exactly public/traces/cells')
    write_once(out / 'runtime-guard.json', {
        'schema': 'classical.ecdlp.reference-original-watchdog/v1',
        'started_at': now(), 'monotonic_start': beginning, 'monotonic_stop': stop,
        'maximum_wall_seconds': args.time_limit, 'maximum_cpu_seconds': 1800,
        'driver_pid': os.getpid(), 'native_process_group': os.getpgrp(),
        'native_run_id': native_launch['run_id'],
        'native_launch_sha256': hashlib.sha256(native_launch_raw).hexdigest(),
        'memory_bytes': 4 << 30, 'cpus_maximum': 2,
        'resource_telemetry_is_performance_measurement': False,
        'wall_valid': False, 'original_stop_must_not_reset': True})
    source_dir = Path(__file__).resolve().parent
    source_hashes = {name: digest_file(source_dir / name)
                     for name in ('solver.py', 'driver.py', 'verify.py')}
    processes, active = [], []
    complete = False
    failure = None

    def cpu_snapshot(child=None):
        own = resource.getrusage(resource.RUSAGE_SELF)
        reaped = resource.getrusage(resource.RUSAGE_CHILDREN)
        live = 0.0
        if child is not None:
            try:
                stat = Path('/proc') / str(child.pid) / 'stat'
                text = stat.read_text()
                fields = text[text.rfind(')') + 2:].split()
                if int(fields[2]) != os.getpgrp():
                    raise RuntimeError('worker detached from native process group')
                live = (int(fields[11]) + int(fields[12])) / os.sysconf('SC_CLK_TCK')
            except FileNotFoundError:
                if child.poll() is None:
                    raise RuntimeError('live worker CPU bookkeeping unavailable')
                # poll reaped it; refresh the aggregate child charge.
                reaped = resource.getrusage(resource.RUSAGE_CHILDREN)
        return {'driver_self_cpu_seconds': own.ru_utime + own.ru_stime,
                'reaped_children_cpu_seconds': reaped.ru_utime + reaped.ru_stime,
                'live_child_cpu_seconds': live}

    def guard(child=None):
        if time.monotonic() >= stop:
            raise TimeoutError('original shared watchdog reached')
        snapshot = cpu_snapshot(child)
        if sum(snapshot.values()) >= 1790:
            raise TimeoutError('shared cumulative1800 CPU allowance guard;10second cleanup reserve')
        return snapshot

    def guarded_write(path, document):
        guard()
        result = write_once(path, document)
        guard()
        return result

    def interruption(signum, frame):
        raise InterruptedError('native parent signal ' + str(signum))

    signal.signal(signal.SIGTERM, interruption)
    signal.signal(signal.SIGINT, interruption)
    try:
        for label in ('A', 'B'):
            prior_cpu = sum(guard().values())
            child_cpu_limit = math.floor(1800 - prior_cpu - 10)
            if child_cpu_limit < 1:
                raise TimeoutError('shared CPU allowance exhausted before child')
            remaining = stop - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('original watchdog expired before fresh pass')
            target = out / ('certificates-' + label + '.json')
            argv = [sys.executable, '-B', str(source_dir / 'solver.py'),
                    '--public-input', str(public), '--expected-sha256', binding['payload_sha256'],
                    '--output', str(target)]
            environment = os.environ.copy()
            environment.update(PYTHONDONTWRITEBYTECODE='1', PYTHONHASHSEED='0',
                               REFERENCE_TIME_LIMIT=str(remaining))
            record = {'label': label, 'argv': argv, 'started_at': now(),
                      'candidate_files_opened': False, 'wait_returned': False,
                      'returncode': None, 'stdout': '', 'stderr': ''}
            processes.append(record)
            child = subprocess.Popen(argv, cwd=root, env=environment,
                                     stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, preexec_fn=lambda: child_limits(child_cpu_limit),
                                     text=True)
            record['pid'] = child.pid
            active.append(child)
            try:
                while True:
                    guard(child)
                    try:
                        stdout, stderr = child.communicate(timeout=min(0.2, max(0.001, stop - time.monotonic())))
                        break
                    except subprocess.TimeoutExpired:
                        continue
                record.update(stdout=stdout, stderr=stderr, returncode=child.returncode,
                              wait_returned=True, finished_at=now())
            except BaseException:
                if child.poll() is None:
                    child.terminate()
                try:
                    stdout, stderr = child.communicate(timeout=2)
                except subprocess.TimeoutExpired:
                    child.kill()
                    stdout, stderr = child.communicate(timeout=2)
                record.update(stdout=stdout, stderr=stderr, returncode=child.returncode,
                              wait_returned=True, finished_at=now(), termination_requested=True)
                raise
            finally:
                active.remove(child)
            if child.returncode != 0:
                raise RuntimeError('reference child failed: ' + label)
            if len(stdout.encode()) > 1 << 20 or len(stderr.encode()) > 1 << 20:
                raise ValueError('child log cap exceeded')
            record['cumulative_cpu_after_wait'] = guard()
        first = (out / 'certificates-A.json').read_bytes()
        second = (out / 'certificates-B.json').read_bytes()
        if first != second:
            raise ValueError('fresh-process A/A canonical certificate bytes disagree')
        files = {name: {'sha256': digest_file(out / name), 'bytes': (out / name).stat().st_size}
                 for name in ('certificates-A.json', 'certificates-B.json')}
        guarded_write(out / 'certificate-seal.json', {
            'schema': 'classical.ecdlp.reference-before-candidate-seal/v1',
            'source_sha256': source_hashes, 'input_manifest_sha256': hashlib.sha256(manifest_raw).hexdigest(),
            'public_input_sha256': binding['payload_sha256'], 'files': files,
            'native_environment_sha256': hashlib.sha256(native_environment_raw).hexdigest(),
            'native_launch_sha256': hashlib.sha256(native_launch_raw).hexdigest(),
            'runtime_guard_sha256': digest_file(out / 'runtime-guard.json'),
            'AA_identical_bytes': True, 'candidate_files_opened_before_seal': False,
            'producer_direct_equations_verified': True,
            'independent_checker_still_required': True, 'sealed_at': now()})
        complete = True
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error),
                   'traceback': traceback.format_exc()}
    finally:
        for child in active:
            if child.poll() is None:
                child.kill()
            child.wait(timeout=2)
        final_cpu = cpu_snapshot()
        observed_cpu = sum(final_cpu.values())
        ledger = {'schema': 'classical.ecdlp.shared-cpu-ledger/v1',
                  **final_cpu, 'observed_cpu_seconds': observed_cpu,
                  'finalization_reserve_seconds': 2.0,
                  'charged_cpu_seconds': observed_cpu + 2.0,
                  'driver_pid': os.getpid(), 'native_run_id': native_launch['run_id'],
                  'native_launch_sha256': hashlib.sha256(native_launch_raw).hexdigest(),
                  'original_monotonic_stop': stop, 'source_sha256': source_hashes,
                  'performance_metric': False,
                  'enforcement': '0.2s cooperative sampling+self/reaped/live CPU; decreasing OS child limits; cleanup reserve; native group/watchdog/claim guards. Not a performance measurement.'}
        if complete:
            guard()
        write_once(out / 'worker-processes.json', {
            'schema': 'classical.ecdlp.actual-reference-child-processes/v1',
            'processes': processes, 'failure': failure, 'complete': complete,
            'host': {'kernel': os.uname().release, 'machine': os.uname().machine,
                     'logical_cpus': os.cpu_count(), 'isolation': 'shared provided workspace; performance unqualified'},
            'ended_at': now(), 'wall_valid': False, 'cpu_ledger': ledger})
        result = {'schema': 'classical.ecdlp.public-reference-raw-result/v1',
                  'attack_claimed': complete, 'reference_search_complete': complete,
                  'source_sha256': source_hashes, 'public_input_sha256': binding['payload_sha256'],
                  'failure': failure,
                  'scientific_scope': 'Finite classical reference scalar certificates only; no new algorithm/performance claim.'}
        if complete:
            guard()
        write_once(out / 'raw-result.json', result)
        # Real producer equation checks precede verified:true. The independently
        # implemented native checker must still validate the same bytes.
        certificate = {'kind': 'discrete_log', 'verified': True,
                       'path': 'certificate-seal.json',
                       'verification_method': 'Producer direct [x]G=Q plus known/negative controls; independent native checker pending'} if complete else {
                           'kind': 'none', 'verified': None, 'note': 'Reference search incomplete; no complete solve claim.'}
        if complete:
            guard()
        write_once(out / 'manifest.yaml', {'run': {'attack_claimed': complete,
                                                  'result': {'certificate': certificate}}})
        if complete:
            guard()
    if not complete:
        print(json.dumps(failure), file=sys.stderr)
        raise SystemExit(1)
    print(json.dumps({'reference_passes_complete': 2, 'AA_equal': True,
                      'candidate_files_opened': False, 'independent_checker_pending': True}))


if __name__ == '__main__':
    main()
