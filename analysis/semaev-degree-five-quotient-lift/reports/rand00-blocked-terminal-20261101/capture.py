#!/usr/bin/env python3
"""Capture small terminal receipts from one fixed Semaev n47 D5 S3 Job."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

PREFIX = ('s3://isolab-results-104186811093-us-east-2/runs/'
          'semaev-n47-rand00-d5-blocked-retry01-20261031/'
          '6a2b5d27-5547-4508-9a28-b46bdc4d543c/lift/')
BUCKET = 'isolab-results-104186811093-us-east-2'
KEY_PREFIX = PREFIX.split(BUCKET + '/', 1)[1]
NAMES = ('result.json', 'environment.json', 'seed-transfer.json',
         'check4.started.json', 'check4.finished.json', 'check4.stdout.txt',
         'count.started.json', 'count.finished.json', 'count.stdout.txt',
         'prelaunch-disk.json', 'produce5.started.json', 'produce5.finished.json',
         'produce5.stdout.txt', 'produce5.stderr.txt')
ROOT = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def get(name):
    uri = PREFIX + name
    data = subprocess.check_output(['aws', 's3', 'cp', uri, '-', '--only-show-errors'])
    path = ROOT / name.replace('/', '__')
    if path.exists() and path.read_bytes() != data:
        raise ValueError('immutable receipt changed: ' + name)
    if not path.exists():
        path.write_bytes(data)
    return {'uri': uri, 'sha256': sha(data), 'bytes': len(data)}


def main():
    listing = json.loads(subprocess.check_output([
        'aws', 's3api', 'list-objects-v2', '--bucket', BUCKET,
        '--prefix', KEY_PREFIX + 'checkpoints/manifests/', '--output', 'json']))
    names = list(NAMES)
    for item in listing.get('Contents', []):
        names.append(item['Key'][len(KEY_PREFIX):])
    names = sorted(names)
    files = {name: get(name) for name in names}
    result = json.loads((ROOT / 'result.json').read_text())
    check = (ROOT / 'check4.stdout.txt').read_text()
    count = (ROOT / 'count.stdout.txt').read_text().strip()
    native = json.loads((ROOT / 'produce5.stdout.txt').read_text())
    if result['status'] != native['status'] or result['status'] != 'projection_kills_one':
        raise ValueError('terminal status mismatch')
    if result['exact_solutions'] != 0 or count != '0':
        raise ValueError('exact count mismatch')
    if 'VALID: 1 is not in W_4(F), and codim W_4(F) >= 61196' not in check:
        raise ValueError('independent D4 acceptance missing')
    if result['seed_codimension'] != 61196 or native['relation_rank'] != native['working_coordinates']:
        raise ValueError('native summary mismatch')
    manifests = [json.loads((ROOT / name.replace('/', '__')).read_text()) for name in names
                 if name.startswith('checkpoints/manifests/')]
    sequences = sorted(m['snapshot']['sequence'] for m in manifests)
    if sequences != list(range(1, 9)):
        raise ValueError('checkpoint manifest sequence mismatch')
    report = {'schema': 'semaev.terminal-readback/v1',
              'job_name': 'semaev-n47-rand00-d5-blocked-retry01-20261031',
              'job_uid': '11b344d6-ff88-4f5e-b5b1-755777790cd2',
              'pod_uid': '6a2b5d27-5547-4508-9a28-b46bdc4d543c',
              'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'files': files, 'checkpoint_sequence': sequences,
              'checks': ['S3 complete GET size and SHA256 for each listed small object',
                         'independent D4 checker transcript matches result codimension',
                         'exact count transcript matches result',
                         'native terminal status and full quotient rank match result',
                         'eight checkpoint manifests have consecutive sequence numbers'],
              'scope': 'D4 lower-bound acceptance and D5 quotient terminal observation; no D5 certificate or upper bound'}
    target = ROOT / 'readback.json'
    if target.exists():
        old = json.loads(target.read_text())
        for key in ('files', 'checkpoint_sequence', 'job_name', 'job_uid', 'pod_uid'):
            if old[key] != report[key]:
                raise ValueError('readback collision: ' + key)
    else:
        target.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': result['status'], 'small_files': len(files),
                      'checkpoints': len(sequences), 'readback': str(target)}))


if __name__ == '__main__':
    main()
