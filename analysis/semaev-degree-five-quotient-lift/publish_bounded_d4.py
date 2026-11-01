#!/usr/bin/env python3
"""Publish independently checked retained D4 certificates with full readback.

This is separate from the frozen producer. It never replaces release assets or
restarts a computation. The release must exist before publication begins.
"""
import argparse
import datetime
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def save_new(path, value):
    with Path(path).open('x') as target:
        json.dump(value, target, indent=2, sort_keys=True)
        target.write('\n')


def checked_row(path, plan_hash, known_ids):
    result = json.loads(path.read_text())
    if result['status'] != 'certificate_verified':
        return None
    if result['id'] not in known_ids or result['plan_sha256'] != plan_hash:
        raise ValueError('result outside pinned plan: ' + str(path))
    stages = result['stages']
    if [stage['degree'] for stage in stages] != [3, 4]:
        raise ValueError('accepted D4 result needs checked D3 and D4 stages')
    count = result['exact_solutions']
    codim = stages[1]['certified_codimension']
    if result['last_fall_degree_lower_bound'] != (5 if codim > count else 4):
        raise ValueError('result lower-bound inference disagrees with strict count test')
    for name, entry in result['artifacts'].items():
        source = path.parent / name
        if not source.is_file() or source.stat().st_size != entry['bytes'] or digest(source) != entry['sha256']:
            raise ValueError('retained artifact changed: ' + str(source))
    cert = path.parent / 'degree4.bin'
    if digest(cert) != stages[1]['certificate_sha256']:
        raise ValueError('D4 stage digest differs from retained certificate')
    check = (path.parent / 'check4.stdout.txt').read_text()
    match = re.search(r'VALID: 1 is not in W_4\(F\), and codim W_4\(F\) >= (\d+)', check)
    if not match or int(match[1]) != codim:
        raise ValueError('original D4 checker transcript mismatch')
    if (path.parent / 'count.stdout.txt').read_text().strip() != str(count):
        raise ValueError('fresh exact-count transcript mismatch')
    return result


def pack_certificate(source, target):
    if not target.exists():
        temporary = target.with_suffix(target.suffix + '.partial')
        with temporary.open('wb') as raw, gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=0) as zipped:
            with source.open('rb') as original:
                shutil.copyfileobj(original, zipped, length=1 << 20)
        os.replace(temporary, target)
    h = hashlib.sha256()
    with gzip.open(target, 'rb') as zipped:
        for block in iter(lambda: zipped.read(1 << 20), b''):
            h.update(block)
    if h.hexdigest() != digest(source):
        raise ValueError('compressed certificate differs from retained original')


def pack_evidence(attempt, target):
    files = {p.name: p for p in attempt.iterdir() if p.is_file() and p.name != 'degree4.bin'}
    temporary = target.with_suffix(target.suffix + '.partial')
    with temporary.open('wb') as raw, gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=0) as zipped:
        with tarfile.open(fileobj=zipped, mode='w|') as archive:
            for name, path in sorted(files.items()):
                info = tarfile.TarInfo('attempt/' + name)
                info.size = path.stat().st_size
                info.mode = 0o644
                with path.open('rb') as source:
                    archive.addfile(info, source)
    if target.exists():
        if digest(temporary) != digest(target):
            temporary.unlink()
            raise ValueError('existing evidence bundle differs from retained files')
        temporary.unlink()
    else:
        os.replace(temporary, target)


def run(argv, **kwargs):
    return subprocess.run([str(value) for value in argv], check=True, **kwargs)


def readback(url, expected, destination):
    run(['curl', '-L', '--fail', '--silent', '--show-error', '--retry', '2',
         '--max-time', '1800', '-o', destination, url])
    if digest(destination) != expected:
        raise ValueError('anonymous release asset hash mismatch: ' + url)


def publish(args):
    args.archive.mkdir(parents=True, exist_ok=True)
    plan = json.loads(args.plan.read_text())
    plan_hash = digest(args.plan)
    known_ids = {item['id'] for item in plan['items']}
    if len(known_ids) != len(plan['items']) or len(known_ids) != 16:
        raise ValueError('expected full 16-input retained panel')
    with (args.archive / 'publication.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        info = json.loads(run(['gh', 'release', 'view', args.tag, '--repo', args.repo,
                               '--json', 'assets,url'], capture_output=True, text=True).stdout)
        assets = {asset['name'] for asset in info['assets']}
        eligible = []
        for path in sorted(args.run_root.glob('*/attempt-001/result.json')):
            row = checked_row(path, plan_hash, known_ids)
            if row is None:
                continue
            name = row['id']
            acknowledgement = args.archive / (name + '.publication.json')
            if acknowledgement.exists():
                old = json.loads(acknowledgement.read_text())
                if old['certificate_sha256'] != row['stages'][1]['certificate_sha256']:
                    raise ValueError('identity collision with previous publication: ' + name)
                continue
            certificate = args.archive / (name + '.D4.cert.gz')
            pack_certificate(path.parent / 'degree4.bin', certificate)
            receipt = args.archive / (name + '.receipt.json')
            expected_receipt = dict(schema='semaev.published-bounded-d4/v1', result=row,
                plan_sha256=plan_hash,
                check3_stdout=(path.parent / 'check3.stdout.txt').read_text(),
                check4_stdout=(path.parent / 'check4.stdout.txt').read_text(),
                count_stdout=(path.parent / 'count.stdout.txt').read_text(),
                compressed_sha256=digest(certificate), compressed_bytes=certificate.stat().st_size)
            if not receipt.exists():
                save_new(receipt, expected_receipt)
            elif json.loads(receipt.read_text()) != expected_receipt:
                raise ValueError('publication receipt differs from retained computation')
            evidence = args.archive / (name + '.evidence.tar.gz')
            pack_evidence(path.parent, evidence)
            eligible.append((name, row, [certificate, receipt, evidence], acknowledgement))
        if not eligible:
            print('No unpublished completed D4 certificates.', flush=True)
            return
        stored = [file for _, _, files, _ in eligible for file in files if file.suffix == '.gz']
        run([args.python, args.repo_root / 'tools/artifacts/artifacts.py', 'push', *stored, '--jobs', '2'],
            cwd=args.repo_root, env={**os.environ, 'AWS_DEFAULT_REGION': args.region})
        with tempfile.TemporaryDirectory(prefix='semaev-bounded-d4-readback-') as temporary:
            downloaded = Path(temporary) / 'asset'
            for name, row, files, acknowledgement in eligible:
                verified = []
                for file in files:
                    sha = digest(file)
                    if file.name not in assets:
                        run(['gh', 'release', 'upload', args.tag, file, '--repo', args.repo])
                        assets.add(file.name)
                    url = f'https://github.com/{args.repo}/releases/download/{args.tag}/{file.name}'
                    readback(url, sha, downloaded)
                    if file.name.endswith('.cert.gz'):
                        h = hashlib.sha256()
                        with gzip.open(downloaded, 'rb') as zipped:
                            for block in iter(lambda: zipped.read(1 << 20), b''):
                                h.update(block)
                        if h.hexdigest() != row['stages'][1]['certificate_sha256']:
                            raise ValueError('public decompressed certificate hash mismatch')
                    store_uri = None
                    if file.suffix == '.gz':
                        store_uri = f'{args.store.rstrip("/")}/sha256/{sha[:2]}/{sha}'
                        run(['aws', 's3', 'cp', store_uri, downloaded, '--region', args.region,
                             '--only-show-errors'])
                        if digest(downloaded) != sha:
                            raise ValueError('canonical store readback mismatch')
                    verified.append(dict(name=file.name, sha256=sha, bytes=file.stat().st_size,
                                         anonymous_url=url, store_uri=store_uri))
                save_new(acknowledgement, dict(schema='semaev.bounded-d4-publication-readback/v1',
                    id=name, checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    certificate_sha256=row['stages'][1]['certificate_sha256'], files=verified,
                    checks=['anonymous HTTPS GET and SHA256 for every asset',
                            'gzip decompression and original certificate SHA256',
                            'S3 GET and SHA256 for each store-backed asset']))
                run(['gh', 'release', 'upload', args.tag, acknowledgement, '--repo', args.repo])
                print(json.dumps({'id': name, 'publication': 'anonymous_and_store_readback_verified'}), flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-root', type=Path, required=True)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--repo-root', type=Path, required=True)
    p.add_argument('--repo', required=True)
    p.add_argument('--tag', required=True)
    p.add_argument('--store', default='s3://setec-astronomy-artifacts/store')
    p.add_argument('--region', default='us-east-2')
    p.add_argument('--python', default=sys.executable)
    publish(p.parse_args())


if __name__ == '__main__':
    main()
