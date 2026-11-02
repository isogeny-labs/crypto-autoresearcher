#!/usr/bin/env python3
"""Check byte-identical bounded certificate output and pipe-based checking."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('binary', 'bundle', 'checker', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    fixtures = json.loads((args.bundle / 'manifest.json').read_text())['lift_fixtures']
    rows = []
    for index, fixture in enumerate(fixtures):
        seed = args.bundle / fixture['seed']
        file_output = args.out / f'fixture-{index}-file.bin'
        stream_output = args.out / f'fixture-{index}-stream.bin'
        argv = [str(args.binary), str(seed)]
        with stream_output.open('xb') as output:
            streamed = subprocess.run(argv + ['-', '4096', str(2 << 30)],
                                      stdout=output, stderr=subprocess.PIPE, check=True)
        ordinary = subprocess.run(argv + [str(file_output), '4096', str(2 << 30)],
                                  capture_output=True, check=True)
        status = json.loads(ordinary.stdout)
        stream_status = json.loads(streamed.stderr.splitlines()[-1])
        assert status == stream_status
        assert status['status'] == 'candidate_certificate'
        assert digest(file_output) == digest(stream_output) == fixture['expected_sha256']
        record = fixture['record']
        check = [sys.executable, str(args.checker), '/dev/stdin', str(record['n']),
                 record['modulus_hex'], str(record['a2']), record['a6_hex'],
                 record['z_hex'], *record['V_basis_hex']]
        producer = subprocess.Popen(argv + ['-', '4096', str(2 << 30)],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            checked = subprocess.run(check, stdin=producer.stdout,
                                     capture_output=True, text=True, check=True)
        finally:
            producer.stdout.close()
        producer_stderr = producer.communicate()[1]
        assert producer.returncode == 0
        assert json.loads(producer_stderr.splitlines()[-1]) == status
        assert 'VALID: 1 is not in W_' in checked.stdout
        rows.append(dict(fixture=index, status=status, certificate_sha256=digest(stream_output),
                         certificate_bytes=stream_output.stat().st_size,
                         checker_exit=checked.returncode,
                         checker_valid_line=next(line for line in checked.stdout.splitlines()
                                                 if line.startswith('VALID:'))))
    receipt = dict(schema='semaev.streamed-bounded-export-test/v1',
                   binary_sha256=digest(args.binary), checker_sha256=digest(args.checker),
                   bundle_manifest_sha256=digest(args.bundle / 'manifest.json'), rows=rows)
    (args.out / 'result.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'fixtures': len(rows), 'all_checker_accepted': True}))


if __name__ == '__main__':
    main()
