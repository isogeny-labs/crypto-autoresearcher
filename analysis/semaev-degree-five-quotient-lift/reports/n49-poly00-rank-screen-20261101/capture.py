#!/usr/bin/env python3
"""Read the fixed n49 polynomial00 local result and S3 checkpoint manifests."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

SOURCE = Path('/home/ec2-user/fall-degree-data-20261029/n49-poly00-d5-local-002/attempt-001')
PREFIX = 's3://setec-astronomy-artifacts/checkpoints/semaev-n49-poly00-d5-local-002/manifests/'
ROOT = Path(__file__).resolve().parent
LOCAL = ('result.json', 'check4.stdout.txt', 'count.stdout.txt',
         'produce5.finished.json', 'produce5.stderr.txt')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    files = {}
    for name in LOCAL:
        data = (SOURCE/name).read_bytes()
        target = ROOT/name
        if target.exists() and target.read_bytes() != data:
            raise ValueError('local receipt changed: '+name)
        if not target.exists():
            target.write_bytes(data)
        files[name] = {'source': str(SOURCE/name), 'sha256': sha(data), 'bytes': len(data)}
    listing = json.loads(subprocess.check_output(['aws', 's3api', 'list-objects-v2',
        '--bucket', 'setec-astronomy-artifacts', '--prefix',
        'checkpoints/semaev-n49-poly00-d5-local-002/manifests/', '--output', 'json']))
    manifests = []
    for item in listing.get('Contents', []):
        name = item['Key'].rsplit('/', 1)[-1]
        data = subprocess.check_output(['aws', 's3', 'cp', PREFIX+name, '-', '--only-show-errors'])
        target = ROOT/name
        if target.exists() and target.read_bytes() != data:
            raise ValueError('manifest changed: '+name)
        if not target.exists():
            target.write_bytes(data)
        files[name] = {'source': PREFIX+name, 'sha256': sha(data), 'bytes': len(data)}
        manifest = json.loads(data)
        if manifest['snapshot']['binary_sha256'] != 'fc0911db6560fe10b49d88d6206f89f8de6494616020a864c82d8be552749613':
            raise ValueError('binary mismatch')
        manifests.append(manifest)
    snapshots = sorted((m['snapshot'] for m in manifests), key=lambda s:s['sequence'])
    if [s['sequence'] for s in snapshots] != list(range(1, 10)):
        raise ValueError('missing or duplicate checkpoint')
    if len({s['working_coordinates'] for s in snapshots}) != 1:
        raise ValueError('changing quotient width')
    ranks = [s['relation_rank'] for s in snapshots]
    if ranks != sorted(ranks):
        raise ValueError('rank decreased')
    result = json.loads((ROOT/'result.json').read_text())
    if result['status'] != 'failed' or result['steps']['produce5']['timeout'] is not True:
        raise ValueError('terminal status mismatch')
    if result['exact_solutions'] != 2 or (ROOT/'count.stdout.txt').read_text().strip() != '2':
        raise ValueError('exact count mismatch')
    if result['seed_codimension'] != 32291 or 'VALID: 1 is not in W_4(F), and codim W_4(F) >= 32291' not in (ROOT/'check4.stdout.txt').read_text():
        raise ValueError('D4 checker mismatch')
    if snapshots[-1]['working_coordinates'] - snapshots[-1]['relation_rank'] != 2:
        raise ValueError('unexpected terminal quotient dimension')
    report = {'schema':'semaev.checkpoint-rank-screen/v1',
              'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'id':'n49-poly00-D5-local-002','files':files,
              'rank_by_sequence': [{'sequence':s['sequence'],'rank':s['relation_rank'],
                                    'working_coordinates':s['working_coordinates']} for s in snapshots],
              'exact_solutions':2,'current_quotient_dimension':2,
              'inference':'Assuming the recorded checkpoint state, append-only rank cannot decrease; this worker cannot export codimension above 2 on restore. This is a search-admission screen, not a mathematical upper bound.',
              'checks':['full local read and SHA256 of retained result/transcripts',
                        'full S3 GET and SHA256 of nine manifests',
                        'consecutive sequences, fixed quotient width, monotone ranks',
                        'D4 checker and exact count agree with result']}
    target=ROOT/'readback.json'
    if target.exists():
        old=json.loads(target.read_text())
        for key in ('id','files','rank_by_sequence','exact_solutions','current_quotient_dimension'):
            if old[key]!=report[key]:raise ValueError('readback collision: '+key)
    else:target.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'manifests':len(snapshots),'rank':ranks[-1],
                      'width':snapshots[-1]['working_coordinates'],'exact_count':2}))


if __name__=='__main__':main()
