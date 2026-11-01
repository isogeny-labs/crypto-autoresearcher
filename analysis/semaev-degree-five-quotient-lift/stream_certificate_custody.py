#!/usr/bin/env python3
"""Upload a bounded producer stream, read it back, and run the independent checker.

This transport does not infer a fall-degree bound. A frozen trial request must
bind its commands, input identities, limits, and exact solution count separately.
The assigned ISOLAB_RESULTS_URI supplies a unique, durable destination.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import threading
import time


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def persist(path, value):
    temporary = path.with_suffix(path.suffix + '.partial')
    with temporary.open('x') as output:
        json.dump(value, output, indent=2, sort_keys=True)
        output.write('\n')
        output.flush()
        os.fsync(output.fileno())
    os.replace(temporary, path)


def run(argv, **kwargs):
    return subprocess.run(list(map(str, argv)), check=True, **kwargs)


def transfer(plan, out, plan_sha256, aws='aws'):
    out.mkdir(parents=True, exist_ok=False)
    prefix = os.environ['ISOLAB_RESULTS_URI'].rstrip('/')
    if not prefix.startswith('s3://') or '/' not in prefix[5:]:
        raise ValueError('assigned S3 run prefix required')
    if plan.get('schema') != 'semaev.streamed-certificate-custody/v1':
        raise ValueError('unsupported request schema')
    name = plan['id']
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}', name):
        raise ValueError('unsafe certificate ID')
    if plan['max_certificate_bytes'] <= 0 or plan['max_certificate_bytes'] > 50_000_000_000:
        raise ValueError('certificate limit outside admitted transport range')
    for role in ('producer', 'checker'):
        identity = plan[role + '_identity']
        path = Path(identity['path'])
        if not path.is_file() or sha(path) != identity['sha256']:
            raise ValueError(role + ' identity mismatch')
        argv = plan[role + '_argv']
        accepted = (argv[0] == str(path) or
                    (role == 'checker' and len(argv) > 1 and
                     argv[0] == sys.executable and argv[1] == str(path)))
        if not accepted:
            raise ValueError(role + ' command differs from identity')
    for binding in plan['inputs']:
        path = Path(binding['path'])
        index = binding['producer_argv_index']
        if (index < 1 or index >= len(plan['producer_argv']) or
                plan['producer_argv'][index] != str(path) or
                not path.is_file() or path.stat().st_size != binding['bytes'] or
                sha(path) != binding['sha256']):
            raise ValueError('producer input identity mismatch: ' + str(path))
    if '/dev/stdin' not in plan['checker_argv']:
        raise ValueError('checker must read the S3 stream from /dev/stdin')
    target = prefix + '/d5/' + name + '.candidate.bin'
    start = time.monotonic()
    receipt = dict(schema='semaev.streamed-certificate-custody-result/v1',
                   id=name, target=target, status='started',
                   plan_sha256=plan_sha256, steps={})
    persist(out / 'started.json', receipt)
    bucket, _, key = target[5:].partition('/')
    prior = subprocess.run([aws, 's3api', 'head-object', '--bucket', bucket,
                            '--key', key, '--output', 'json'],
                           capture_output=True, text=True)
    if prior.returncode == 0:
        raise ValueError('target already exists; refuse overwrite: ' + target)
    if '404' not in prior.stderr and 'Not Found' not in prior.stderr and 'NoSuchKey' not in prior.stderr:
        raise RuntimeError('target existence could not be established: ' + prior.stderr[-1000:])
    producer = None
    uploader = None
    expired = threading.Event()
    def timeout():
        expired.set()
        for child in (producer, uploader):
            if child is not None and child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
    timer = threading.Timer(plan['timeout_seconds'], timeout)
    timer.start()
    try:
        with (out / 'producer.stderr.txt').open('xb') as producer_log, \
             (out / 'upload.stderr.txt').open('xb') as upload_log:
            producer = subprocess.Popen(plan['producer_argv'], stdout=subprocess.PIPE,
                                        stderr=producer_log, start_new_session=True)
            uploader = subprocess.Popen([aws, 's3', 'cp', '-', target, '--expected-size',
                                         str(plan['max_certificate_bytes']), '--no-overwrite',
                                         '--only-show-errors'],
                                        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                        stderr=upload_log, start_new_session=True)
            h = hashlib.sha256()
            size = 0
            while True:
                block = producer.stdout.read(1 << 20)
                if not block:
                    break
                size += len(block)
                if size > plan['max_certificate_bytes']:
                    raise ValueError('producer exceeded frozen certificate limit')
                h.update(block)
                uploader.stdin.write(block)
            producer.stdout.close()
            uploader.stdin.close()
            producer_code = producer.wait(timeout=30)
            upload_code = uploader.wait(timeout=plan['upload_timeout_seconds'])
        if expired.is_set() or producer_code or upload_code or size == 0:
            raise RuntimeError(f'producer/upload incomplete: timeout={expired.is_set()} '
                               f'producer={producer_code} upload={upload_code} bytes={size}')
        lines = (out / 'producer.stderr.txt').read_text().splitlines()
        status = json.loads(lines[-1])
        if status.get('status') != 'candidate_certificate' or status.get('codimension', 0) <= 0:
            raise ValueError('producer did not report a candidate certificate')
        receipt['steps']['upload'] = dict(bytes=size, sha256=h.hexdigest(),
                                          producer_status=status)
        persist(out / 'uploaded.json', receipt)
    finally:
        timer.cancel()
        for child in (producer, uploader):
            if child is not None and child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
                child.wait()
    remote = run([aws, 's3api', 'head-object', '--bucket', bucket, '--key', key,
                  '--output', 'json'], capture_output=True, text=True)
    if json.loads(remote.stdout)['ContentLength'] != size:
        raise ValueError('stored object length differs from producer stream')
    reader = subprocess.Popen([aws, 's3', 'cp', target, '-', '--only-show-errors'],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              start_new_session=True)
    checker = subprocess.Popen(plan['checker_argv'], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                               start_new_session=True)
    readback_expired = threading.Event()
    def readback_timeout():
        readback_expired.set()
        for child in (reader, checker):
            if child.poll() is None:
                try:
                    os.killpg(child.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
    readback_timer = threading.Timer(plan['checker_timeout_seconds'], readback_timeout)
    readback_timer.start()
    h = hashlib.sha256()
    read_size = 0
    try:
        for block in iter(lambda: reader.stdout.read(1 << 20), b''):
            read_size += len(block)
            if read_size > plan['max_certificate_bytes']:
                raise ValueError('S3 readback exceeded frozen certificate limit')
            h.update(block)
            checker.stdin.buffer.write(block)
        checker.stdin.close()
        checker.stdin = None
    except BaseException:
        readback_timer.cancel()
        reader.kill()
        checker.kill()
        reader.wait()
        checker.wait()
        raise
    reader.stdout.close()
    checked_out, checked_error = checker.communicate(timeout=plan['checker_timeout_seconds'])
    _, read_error = reader.communicate(timeout=1200)
    readback_timer.cancel()
    if readback_expired.is_set():
        raise RuntimeError('S3 readback or checker exceeded frozen timeout')
    (out / 'checker.stdout.txt').write_text(checked_out)
    (out / 'checker.stderr.txt').write_text(checked_error)
    if read_size != size or h.hexdigest() != receipt['steps']['upload']['sha256']:
        raise ValueError('full S3 readback differs from producer: ' + read_error.decode()[-1000:])
    receipt['steps']['readback'] = dict(bytes=read_size, sha256=h.hexdigest())
    persist(out / 'readback.json', receipt)
    if checker.returncode or reader.returncode:
        raise RuntimeError('independent checker or S3 reader failed')
    match = re.search(r'VALID: 1 is not in W_5\(F\), and codim W_5\(F\) >= (\d+)', checked_out)
    if not match or int(match[1]) != status['codimension']:
        raise ValueError('independent checker did not reproduce D5 codimension')
    receipt['steps']['checker'] = dict(codimension=int(match[1]), stdout_sha256=sha(out / 'checker.stdout.txt'))
    receipt['status'] = 'certificate_verified'
    receipt['elapsed_seconds'] = time.monotonic() - start
    persist(out / 'result.json', receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    try:
        print(json.dumps(transfer(plan, args.out, sha(args.plan))), flush=True)
    except Exception as error:
        if args.out.is_dir():
            persist(args.out / 'failure.json', dict(schema='semaev.streamed-certificate-custody-failure/v1',
                         plan_sha256=sha(args.plan), error=repr(error)))
        raise


if __name__ == '__main__':
    main()
